"""
Comando para sincronizar las divisiones de los eventos con las divisiones que tienen los jugadores.
Solo mantiene las divisiones que tienen jugadores asignados.
"""
from django.core.management.base import BaseCommand
from django.db.models import Count
from apps.events.models import Division, Event
from apps.accounts.models import Player


class Command(BaseCommand):
    help = 'Sincroniza las divisiones de eventos con las divisiones de jugadores. Solo mantiene divisiones usadas por jugadores.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo muestra qué se haría sin hacer cambios',
        )
        parser.add_argument(
            '--remove-unused',
            action='store_true',
            help='Elimina las divisiones que no tienen jugadores ni eventos',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        remove_unused = options['remove_unused']

        self.stdout.write(self.style.SUCCESS('\n=== ANÁLISIS DE DIVISIONES ===\n'))

        # 1. Obtener divisiones usadas por jugadores
        self.stdout.write('1. DIVISIONES USADAS POR JUGADORES:')
        player_divisions = Player.objects.filter(
            division__isnull=False
        ).values(
            'division__id', 'division__name'
        ).annotate(
            count=Count('id')
        ).order_by('division__name')

        player_division_ids = set()
        for pd in player_divisions:
            div_id = pd['division__id']
            div_name = pd['division__name']
            count = pd['count']
            player_division_ids.add(div_id)
            self.stdout.write(f'   [OK] ID {div_id}: {div_name} ({count} jugadores)')

        self.stdout.write(f'\n   Total divisiones con jugadores: {len(player_division_ids)}\n')

        # 2. Obtener divisiones usadas por eventos
        self.stdout.write('2. DIVISIONES ACTUALES EN EVENTOS:')
        all_events = Event.objects.all()
        event_division_stats = {}

        for event in all_events:
            event_divs = event.divisions.all()
            for div in event_divs:
                if div.id not in event_division_stats:
                    event_division_stats[div.id] = {
                        'name': div.name,
                        'events': []
                    }
                event_division_stats[div.id]['events'].append(event.title)

        for div_id, stats in sorted(event_division_stats.items()):
            events_count = len(stats['events'])
            self.stdout.write(f'   - ID {div_id}: {stats["name"]} ({events_count} eventos)')
            if div_id not in player_division_ids:
                self.stdout.write(self.style.WARNING(f'      [WARNING] Esta division NO tiene jugadores!'))

        self.stdout.write(f'\n   Total divisiones en eventos: {len(event_division_stats)}\n')

        # 3. Identificar divisiones que necesitan ser removidas de eventos
        self.stdout.write('3. ACCIONES A REALIZAR:')
        divisions_to_remove_from_events = set(event_division_stats.keys()) - player_division_ids

        if divisions_to_remove_from_events:
            self.stdout.write(self.style.WARNING(f'\n   Divisiones a REMOVER de eventos (no tienen jugadores):'))
            for div_id in sorted(divisions_to_remove_from_events):
                div_name = event_division_stats[div_id]['name']
                events = event_division_stats[div_id]['events']
                self.stdout.write(f'      - ID {div_id}: {div_name}')
                self.stdout.write(f'        Eventos afectados: {", ".join(events[:3])}')
                if len(events) > 3:
                    self.stdout.write(f'        ... y {len(events) - 3} más')
        else:
            self.stdout.write(self.style.SUCCESS('   [OK] Todas las divisiones en eventos tienen jugadores\n'))

        # 4. Divisiones sin usar
        all_divisions = Division.objects.all()
        unused_divisions = []
        for div in all_divisions:
            player_count = Player.objects.filter(division_id=div.id).count()
            event_count = Event.objects.filter(divisions__id=div.id).count()
            if player_count == 0 and event_count == 0:
                unused_divisions.append(div)

        if unused_divisions:
            self.stdout.write(f'\n   Divisiones sin usar (sin jugadores ni eventos): {len(unused_divisions)}')
            for div in unused_divisions:
                self.stdout.write(f'      - ID {div.id}: {div.name}')
        else:
            self.stdout.write(self.style.SUCCESS('   [OK] No hay divisiones completamente sin usar\n'))

        # 5. Ejecutar cambios si no es dry-run
        if dry_run:
            self.stdout.write(self.style.WARNING('\n=== MODO DRY-RUN: No se realizaron cambios ===\n'))
            return

        self.stdout.write(self.style.SUCCESS('\n=== APLICANDO CAMBIOS ===\n'))

        # Remover divisiones de eventos que no tienen jugadores
        if divisions_to_remove_from_events:
            for event in all_events:
                event_divs = list(event.divisions.all())
                removed_divs = [d for d in event_divs if d.id in divisions_to_remove_from_events]
                if removed_divs:
                    for div in removed_divs:
                        event.divisions.remove(div)
                    self.stdout.write(
                        self.style.WARNING(
                            f'   Evento "{event.title}": Removidas divisiones {[d.name for d in removed_divs]}'
                        )
                    )

        # Remover divisiones completamente sin usar
        if remove_unused and unused_divisions:
            for div in unused_divisions:
                div_name = div.name
                div.delete()
                self.stdout.write(
                    self.style.SUCCESS(f'   [OK] Eliminada division sin usar: {div_name}')
                )

        self.stdout.write(self.style.SUCCESS('\n=== COMPLETADO ===\n'))

        # 6. Verificación final
        self.stdout.write('VERIFICACIÓN FINAL:')
        remaining_event_divisions = set()
        for event in Event.objects.all():
            for div in event.divisions.all():
                remaining_event_divisions.add(div.id)

        only_player_divisions = remaining_event_divisions - player_division_ids
        if only_player_divisions:
            self.stdout.write(
                self.style.ERROR(
                    f'   [ERROR] Aun hay {len(only_player_divisions)} divisiones en eventos sin jugadores!'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    '   [OK] Todas las divisiones en eventos tienen jugadores asignados'
                )
            )
