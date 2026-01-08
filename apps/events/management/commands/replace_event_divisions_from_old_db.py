"""
Comando para reemplazar las divisiones de eventos con las divisiones de jugadores
desde una base de datos anterior (antes de los cambios).
"""
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import connections, transaction
from django.db.models import Count
from apps.events.models import Division, Event
from apps.accounts.models import Player


class Command(BaseCommand):
    help = 'Reemplaza las divisiones de eventos con las divisiones de jugadores desde una base de datos anterior'

    def add_arguments(self, parser):
        parser.add_argument(
            'old_db_path',
            type=str,
            help='Ruta a la base de datos anterior (db.sqlite3)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo muestra qué se haría sin hacer cambios',
        )

    def handle(self, *args, **options):
        old_db_path = Path(options['old_db_path'])
        dry_run = options['dry_run']

        if not old_db_path.exists():
            self.stdout.write(
                self.style.ERROR(f'Error: No se encuentra el archivo {old_db_path}')
            )
            return

        self.stdout.write(self.style.SUCCESS('\n=== IMPORTANDO DIVISIONES DESDE BASE DE DATOS ANTERIOR ===\n'))
        self.stdout.write(f'Base de datos anterior: {old_db_path}\n')

        # Configurar conexión a la base de datos anterior
        old_db_config = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(old_db_path),
        }

        # Crear una conexión temporal a la base de datos anterior
        old_db_alias = 'old_db'
        connections.databases[old_db_alias] = old_db_config

        try:
            # Leer divisiones de jugadores de la base de datos anterior
            self.stdout.write('1. Leyendo divisiones de jugadores de la BD anterior...')

            with connections[old_db_alias].cursor() as cursor:
                # Obtener divisiones únicas de jugadores
                cursor.execute("""
                    SELECT DISTINCT division
                    FROM accounts_player
                    WHERE division IS NOT NULL AND division != ''
                    ORDER BY division
                """)
                old_player_divisions = [row[0] for row in cursor.fetchall()]

            self.stdout.write(f'   Encontradas {len(old_player_divisions)} divisiones de jugadores:')
            for div in old_player_divisions:
                self.stdout.write(f'      - {div}')

            # Leer eventos y sus divisiones actuales de la BD anterior
            self.stdout.write('\n2. Leyendo eventos y sus divisiones de la BD anterior...')

            old_event_divisions_map = {}
            with connections[old_db_alias].cursor() as cursor:
                # Obtener eventos con sus divisiones
                cursor.execute("""
                    SELECT e.id, e.title, d.name
                    FROM events_event e
                    JOIN events_event_divisions ed ON e.id = ed.event_id
                    JOIN events_division d ON ed.division_id = d.id
                    ORDER BY e.id, d.name
                """)

                for event_id, event_title, division_name in cursor.fetchall():
                    if event_id not in old_event_divisions_map:
                        old_event_divisions_map[event_id] = {
                            'title': event_title,
                            'divisions': []
                        }
                    old_event_divisions_map[event_id]['divisions'].append(division_name)

            self.stdout.write(f'   Encontrados {len(old_event_divisions_map)} eventos con divisiones')
            for event_id, data in old_event_divisions_map.items():
                self.stdout.write(f'      - Evento ID {event_id}: {data["title"]}')
                self.stdout.write(f'        Divisiones: {", ".join(data["divisions"])}')

            # Mapear divisiones antiguas a divisiones actuales (por nombre)
            self.stdout.write('\n3. Mapeando divisiones antiguas a divisiones actuales...')

            current_divisions = {div.name: div for div in Division.objects.all()}
            division_mapping = {}

            for old_div_name in old_player_divisions:
                # Buscar división actual por nombre exacto
                if old_div_name in current_divisions:
                    division_mapping[old_div_name] = current_divisions[old_div_name]
                    self.stdout.write(f'   [OK] {old_div_name} -> {current_divisions[old_div_name].name} (ID: {current_divisions[old_div_name].id})')
                else:
                    # Intentar encontrar por nombre simplificado
                    simple_name = old_div_name.split()[0] if ' ' in old_div_name else old_div_name
                    found = False
                    for div_name, div_obj in current_divisions.items():
                        if div_name.startswith(simple_name) or simple_name.startswith(div_name):
                            division_mapping[old_div_name] = div_obj
                            self.stdout.write(f'   [MAP] {old_div_name} -> {div_obj.name} (ID: {div_obj.id})')
                            found = True
                            break
                    if not found:
                        self.stdout.write(
                            self.style.WARNING(f'   [WARNING] No se encontró división para: {old_div_name}')
                        )

            if dry_run:
                self.stdout.write(self.style.WARNING('\n=== MODO DRY-RUN: No se realizaron cambios ===\n'))
                return

            # Actualizar eventos en la base de datos actual
            self.stdout.write('\n4. Actualizando eventos en la base de datos actual...')

            with transaction.atomic():
                for event_id, old_data in old_event_divisions_map.items():
                    # Buscar el evento en la BD actual (por título o ID si existe)
                    try:
                        # Intentar por ID primero
                        event = Event.objects.get(pk=event_id)
                    except Event.DoesNotExist:
                        # Intentar por título
                        try:
                            event = Event.objects.get(title=old_data['title'])
                        except Event.DoesNotExist:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'   [SKIP] Evento "{old_data["title"]}" no encontrado en BD actual'
                                )
                            )
                            continue

                    # Obtener divisiones actuales que corresponden a las antiguas
                    new_divisions = []
                    for old_div_name in old_data['divisions']:
                        if old_div_name in division_mapping:
                            new_divisions.append(division_mapping[old_div_name])
                        else:
                            # Si la división antigua no tiene jugadores, intentar mapear por nombre
                            simple_name = old_div_name.split()[0] if ' ' in old_div_name else old_div_name
                            for div_name, div_obj in current_divisions.items():
                                if div_name == simple_name or div_name.startswith(simple_name):
                                    new_divisions.append(div_obj)
                                    break

                    if new_divisions:
                        # Limpiar divisiones actuales y agregar las nuevas
                        event.divisions.clear()
                        event.divisions.set(new_divisions)

                        div_names = [d.name for d in new_divisions]
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'   [OK] Evento "{event.title}": Actualizado con divisiones {div_names}'
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'   [WARNING] Evento "{event.title}": No se pudieron mapear divisiones'
                            )
                        )

            self.stdout.write(self.style.SUCCESS('\n=== COMPLETADO ===\n'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\nError: {str(e)}'))
            import traceback
            self.stdout.write(traceback.format_exc())
        finally:
            # Cerrar conexión temporal
            if old_db_alias in connections.databases:
                del connections.databases[old_db_alias]
