"""
Comando para limpiar divisiones, manteniendo solo las divisiones estándar (05U-18U)
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.events.models import Division, Event
from apps.accounts.models import Player


class Command(BaseCommand):
    help = 'Elimina todas las divisiones excepto las estándar (05U-18U)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo muestra qué se haría sin hacer cambios',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        # Divisiones estándar a mantener
        standard_divisions = [
            '05U', '06U', '07U', '08U', '09U', '10U', '11U', '12U',
            '13U', '14U', '15U', '16U', '17U', '18U'
        ]

        self.stdout.write(self.style.SUCCESS('\n=== LIMPIEZA DE DIVISIONES ===\n'))
        self.stdout.write(f'Divisiones estándar a mantener: {", ".join(standard_divisions)}\n')

        # Obtener todas las divisiones
        all_divisions = Division.objects.all()
        self.stdout.write(f'Total divisiones en BD: {all_divisions.count()}\n')

        # Identificar divisiones a mantener y eliminar
        divisions_to_keep = []
        divisions_to_delete = []

        for division in all_divisions:
            if division.name in standard_divisions:
                divisions_to_keep.append(division)
            else:
                divisions_to_delete.append(division)

        self.stdout.write(f'Divisiones a mantener: {len(divisions_to_keep)}')
        for div in divisions_to_keep:
            player_count = Player.objects.filter(division=div).count()
            event_count = Event.objects.filter(divisions=div).count()
            self.stdout.write(f'  - {div.name} (ID: {div.id}): {player_count} jugadores, {event_count} eventos')

        self.stdout.write(f'\nDivisiones a eliminar: {len(divisions_to_delete)}')
        for div in divisions_to_delete[:20]:  # Mostrar solo las primeras 20
            player_count = Player.objects.filter(division=div).count()
            event_count = Event.objects.filter(divisions=div).count()
            self.stdout.write(
                self.style.WARNING(
                    f'  - {div.name} (ID: {div.id}): {player_count} jugadores, {event_count} eventos'
                )
            )
        if len(divisions_to_delete) > 20:
            self.stdout.write(
                self.style.WARNING(f'  ... y {len(divisions_to_delete) - 20} más')
            )

        # Verificar jugadores y eventos afectados
        players_with_deleted_divisions = Player.objects.filter(
            division__in=divisions_to_delete
        )
        events_with_deleted_divisions = Event.objects.filter(
            divisions__in=divisions_to_delete
        ).distinct()

        if players_with_deleted_divisions.exists():
            self.stdout.write(
                self.style.WARNING(
                    f'\n⚠ ADVERTENCIA: {players_with_deleted_divisions.count()} jugadores tienen divisiones que serán eliminadas'
                )
            )
            # Intentar mapear a divisiones estándar
            for player in players_with_deleted_divisions[:10]:
                if player.division:
                    div_name = player.division.name
                    # Extraer nombre base (ej: "10U" de "10U OPEN")
                    base_name = div_name.split()[0] if ' ' in div_name else div_name
                    if base_name in standard_divisions:
                        standard_div = Division.objects.get(name=base_name)
                        self.stdout.write(
                            f'  - {player.user.get_full_name()}: {div_name} -> {base_name}'
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f'  - {player.user.get_full_name()}: {div_name} (NO SE PUEDE MAPEAR)'
                            )
                        )

        if events_with_deleted_divisions.exists():
            self.stdout.write(
                self.style.WARNING(
                    f'\n⚠ ADVERTENCIA: {events_with_deleted_divisions.count()} eventos tienen divisiones que serán eliminadas'
                )
            )
            for event in events_with_deleted_divisions:
                deleted_divs = [d for d in event.divisions.all() if d in divisions_to_delete]
                if deleted_divs:
                    self.stdout.write(f'  - {event.title}: {[d.name for d in deleted_divs]}')

        if dry_run:
            self.stdout.write(self.style.WARNING('\n=== MODO DRY-RUN: No se realizaron cambios ===\n'))
            return

        # Confirmar antes de eliminar (comentado para ejecución no interactiva)
        # self.stdout.write(self.style.WARNING('\n⚠ Esto eliminará divisiones y puede afectar jugadores y eventos.'))
        # self.stdout.write('Presiona Enter para continuar o Ctrl+C para cancelar...')
        # try:
        #     input()
        # except KeyboardInterrupt:
        #     self.stdout.write(self.style.ERROR('\nOperación cancelada.'))
        #     return

        # Ejecutar limpieza
        self.stdout.write(self.style.SUCCESS('\n=== ELIMINANDO DIVISIONES ===\n'))

        with transaction.atomic():
            # 1. Actualizar jugadores con divisiones a eliminar
            updated_players = 0
            for player in players_with_deleted_divisions:
                if player.division:
                    div_name = player.division.name
                    base_name = div_name.split()[0] if ' ' in div_name else div_name
                    if base_name in standard_divisions:
                        try:
                            standard_div = Division.objects.get(name=base_name)
                            player.division = standard_div
                            player.save()
                            updated_players += 1
                        except Division.DoesNotExist:
                            self.stdout.write(
                                self.style.ERROR(
                                    f'  [ERROR] No se encontró división estándar: {base_name}'
                                )
                            )
                    else:
                        # Si no se puede mapear, poner a NULL
                        player.division = None
                        player.save()
                        self.stdout.write(
                            self.style.WARNING(
                                f'  [WARNING] Jugador {player.user.get_full_name()}: división {div_name} -> NULL'
                            )
                        )

            self.stdout.write(f'  [OK] Actualizados {updated_players} jugadores\n')

            # 2. Actualizar eventos - remover divisiones a eliminar
            updated_events = 0
            for event in events_with_deleted_divisions:
                current_divs = list(event.divisions.all())
                new_divs = [d for d in current_divs if d not in divisions_to_delete]

                # Intentar mapear divisiones eliminadas a estándar
                for deleted_div in current_divs:
                    if deleted_div in divisions_to_delete:
                        div_name = deleted_div.name
                        base_name = div_name.split()[0] if ' ' in div_name else div_name
                        if base_name in standard_divisions:
                            try:
                                standard_div = Division.objects.get(name=base_name)
                                if standard_div not in new_divs:
                                    new_divs.append(standard_div)
                            except Division.DoesNotExist:
                                pass

                event.divisions.set(new_divs)
                updated_events += 1

            self.stdout.write(f'  [OK] Actualizados {updated_events} eventos\n')

            # 3. Eliminar divisiones
            deleted_count = 0
            for division in divisions_to_delete:
                div_name = division.name
                division.delete()
                deleted_count += 1
                if deleted_count <= 20:
                    self.stdout.write(f'  [DELETED] {div_name}')

            self.stdout.write(f'\n  [OK] Eliminadas {deleted_count} divisiones\n')

        self.stdout.write(self.style.SUCCESS('\n=== COMPLETADO ===\n'))

        # Verificación final
        remaining_divisions = Division.objects.all()
        self.stdout.write(f'Divisiones restantes: {remaining_divisions.count()}')
        for div in remaining_divisions.order_by('name'):
            self.stdout.write(f'  - {div.name}')
