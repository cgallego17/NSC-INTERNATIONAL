"""
Script para actualizar las divisiones de los jugadores a divisiones simples
"""

from django.core.management.base import BaseCommand
from apps.events.models import Division
from apps.accounts.models import Player


class Command(BaseCommand):
    help = 'Actualiza las divisiones de los jugadores a divisiones simples (10U, 14U, etc.)'

    def handle(self, *args, **options):
        # Asegurar que existen las divisiones simples
        simple_divisions = ['05U', '06U', '07U', '08U', '09U', '10U', '11U', '12U', '13U', '14U', '15U', '16U', '17U', '18U']

        for div_name in simple_divisions:
            Division.objects.get_or_create(
                name=div_name,
                defaults={
                    'is_active': True,
                    'description': f'Division {div_name}'
                }
            )

        # Actualizar jugadores
        players_updated = 0
        players_with_division = Player.objects.exclude(division__isnull=True)

        for player in players_with_division:
            if not player.division:
                continue

            current_division = player.division
            current_name = current_division.name

            # Si ya es una división simple (formato "10U" o solo números como "141"), verificar
            # Si el nombre es solo números, necesitamos buscar la división correcta basada en edad
            if current_name in simple_divisions:
                continue

            # Si el nombre es solo números (ej: "141", "119"), buscar la división basada en la edad del jugador
            if current_name.isdigit():
                # Obtener la edad del jugador y determinar la división
                if hasattr(player, 'user') and hasattr(player.user, 'profile') and player.user.profile.birth_date:
                    from datetime import date
                    today = date.today()
                    age = today.year - player.user.profile.birth_date.year - ((today.month, today.day) < (player.user.profile.birth_date.month, player.user.profile.birth_date.day))
                    # Mapear edad a división (aproximado)
                    age_to_division = {
                        5: '05U', 6: '06U', 7: '07U', 8: '08U', 9: '09U',
                        10: '10U', 11: '11U', 12: '12U', 13: '13U', 14: '14U',
                        15: '15U', 16: '16U', 17: '17U', 18: '18U'
                    }
                    base_name = age_to_division.get(age, None)
                    if not base_name:
                        continue
                else:
                    # No podemos determinar la edad, saltar este jugador
                    continue
            else:
                # Extraer la parte de edad (ej: "10U OPEN" -> "10U")
                base_name = current_name.split()[0] if ' ' in current_name else current_name
                # Si no termina en "U", puede que sea un formato diferente
                if not base_name.endswith('U') and len(base_name) > 2:
                    # Intentar extraer número seguido de U
                    import re
                    match = re.search(r'(\d+)U', base_name)
                    if match:
                        base_name = match.group(0)
                    else:
                        continue

            # Buscar la división simple correspondiente
            if base_name in simple_divisions:
                try:
                    simple_division = Division.objects.get(name=base_name)
                    player.division = simple_division
                    player.save(update_fields=['division'])
                    players_updated += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Player {player.id} ({player.user.get_full_name()}): {current_name} -> {base_name}'
                        )
                    )
                except Division.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Player {player.id}: No se encontro division simple para {base_name}'
                        )
                    )

        self.stdout.write(self.style.SUCCESS(f'\nActualizados {players_updated} jugadores'))
        self.stdout.write(self.style.SUCCESS('Migracion completada'))
