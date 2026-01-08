"""
Comando para reemplazar las divisiones de eventos con las divisiones simples de jugadores
desde la base de datos actual (que tiene division como CharField).
"""
import sqlite3
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.events.models import Division, Event


class Command(BaseCommand):
    help = 'Reemplaza las divisiones compuestas de eventos con divisiones simples de jugadores'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo muestra qué se haría sin hacer cambios',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        self.stdout.write(self.style.SUCCESS('\n=== REEMPLAZANDO DIVISIONES DE EVENTOS ===\n'))

        # Conectar a la base de datos actual
        from django.conf import settings
        db_path = Path(settings.DATABASES['default']['NAME'])

        if not db_path.exists():
            self.stdout.write(self.style.ERROR(f'Error: No se encuentra la base de datos {db_path}'))
            return

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        try:
            # 1. Leer divisiones de jugadores
            self.stdout.write('1. Leyendo divisiones de jugadores...')
            cursor.execute("""
                SELECT DISTINCT division, COUNT(*) as count
                FROM accounts_player
                WHERE division IS NOT NULL AND division != ''
                GROUP BY division
                ORDER BY division
            """)
            player_divisions = [row[0] for row in cursor.fetchall()]

            self.stdout.write(f'   Encontradas {len(player_divisions)} divisiones de jugadores:')
            for div in player_divisions:
                cursor.execute("SELECT COUNT(*) FROM accounts_player WHERE division = ?", (div,))
                count = cursor.fetchone()[0]
                self.stdout.write(f'      - {div} ({count} jugadores)')

            # 2. Leer eventos y sus divisiones actuales
            self.stdout.write('\n2. Leyendo eventos y sus divisiones actuales...')
            cursor.execute("""
                SELECT e.id, e.title, d.name
                FROM events_event e
                JOIN events_event_divisions ed ON e.id = ed.event_id
                JOIN events_division d ON ed.division_id = d.id
                ORDER BY e.id, d.name
            """)

            event_divisions_map = {}
            for event_id, event_title, division_name in cursor.fetchall():
                if event_id not in event_divisions_map:
                    event_divisions_map[event_id] = {
                        'title': event_title,
                        'divisions': []
                    }
                event_divisions_map[event_id]['divisions'].append(division_name)

            self.stdout.write(f'   Encontrados {len(event_divisions_map)} eventos con divisiones')
            for event_id, data in event_divisions_map.items():
                self.stdout.write(f'      - Evento ID {event_id}: {data["title"]}')
                self.stdout.write(f'        Divisiones actuales: {", ".join(data["divisions"])}')

            # 3. Mapear divisiones compuestas a simples
            self.stdout.write('\n3. Mapeando divisiones compuestas a simples...')

            # Crear o obtener divisiones simples en la BD actual
            simple_divisions = {}
            for player_div in player_divisions:
                # Buscar o crear la división simple
                division_obj, created = Division.objects.get_or_create(
                    name=player_div,
                    defaults={'is_active': True}
                )
                simple_divisions[player_div] = division_obj
                if created:
                    self.stdout.write(f'   [CREATED] División creada: {player_div} (ID: {division_obj.id})')
                else:
                    self.stdout.write(f'   [EXISTS] División existe: {player_div} (ID: {division_obj.id})')

            # 4. Mapear divisiones compuestas a simples
            def extract_simple_division(compound_name):
                """Extrae la división simple de un nombre compuesto"""
                # Ejemplos: "10U OPEN" -> "10U", "13U OPEN (54/80)" -> "13U"
                parts = compound_name.split()
                if parts:
                    simple = parts[0]
                    # Remover paréntesis si existen
                    if '(' in simple:
                        simple = simple.split('(')[0]
                    return simple
                return None

            if dry_run:
                self.stdout.write(self.style.WARNING('\n=== MODO DRY-RUN: No se realizaron cambios ===\n'))
                return

            # 5. Actualizar eventos
            self.stdout.write('\n4. Actualizando eventos...')

            with transaction.atomic():
                for event_id, old_data in event_divisions_map.items():
                    try:
                        event = Event.objects.get(pk=event_id)
                    except Event.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(f'   [SKIP] Evento ID {event_id} no encontrado')
                        )
                        continue

                    # Extraer divisiones simples de las compuestas
                    new_divisions = []
                    for compound_div in old_data['divisions']:
                        simple_name = extract_simple_division(compound_div)
                        if simple_name and simple_name in simple_divisions:
                            new_divisions.append(simple_divisions[simple_name])
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'   [WARNING] No se pudo mapear: {compound_div}'
                                )
                            )

                    if new_divisions:
                        # Limpiar y establecer nuevas divisiones
                        event.divisions.clear()
                        event.divisions.set(new_divisions)

                        div_names = [d.name for d in new_divisions]
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'   [OK] Evento "{event.title}": {", ".join(old_data["divisions"])} -> {", ".join(div_names)}'
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
            conn.close()
