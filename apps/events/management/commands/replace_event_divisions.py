"""
Script para reemplazar divisiones compuestas de eventos por divisiones simples
que coincidan con las divisiones de los jugadores (10U, 14U, etc.)
"""

from django.core.management.base import BaseCommand
from apps.events.models import Event, Division


class Command(BaseCommand):
    help = 'Reemplaza divisiones compuestas de eventos por divisiones simples (10U, 14U, etc.)'

    def handle(self, *args, **options):
        # Crear divisiones simples si no existen
        simple_divisions = ['05U', '06U', '07U', '08U', '09U', '10U', '11U', '12U', '13U', '14U', '15U', '16U', '17U', '18U']

        created_count = 0
        for div_name in simple_divisions:
            division, created = Division.objects.get_or_create(
                name=div_name,
                defaults={
                    'is_active': True,
                    'description': f'División {div_name}'
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Creada division: {div_name}'))

        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(f'\nCreadas {created_count} divisiones simples'))

        # Mapear divisiones compuestas a simples
        # Extraer la parte de edad de nombres como "10U OPEN" -> "10U"
        events_updated = 0
        divisions_mapping = {}

        for event in Event.objects.all():
            old_divisions = list(event.divisions.all())
            if not old_divisions:
                continue

            new_divisions = []
            for old_div in old_divisions:
                # Extraer la parte de edad (ej: "10U OPEN" -> "10U")
                div_name = old_div.name
                base_name = div_name.split()[0] if ' ' in div_name else div_name

                # Buscar o crear la división simple correspondiente
                if base_name in simple_divisions:
                    simple_div = Division.objects.get(name=base_name)
                    if simple_div not in new_divisions:
                        new_divisions.append(simple_div)

            # Reemplazar divisiones del evento
            if new_divisions:
                event.divisions.clear()
                event.divisions.set(new_divisions)
                events_updated += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Evento "{event.title}": {[d.name for d in old_divisions]} -> {[d.name for d in new_divisions]}'
                    )
                )

        self.stdout.write(self.style.SUCCESS(f'\nActualizados {events_updated} eventos'))
        self.stdout.write(self.style.SUCCESS('Migracion completada'))
