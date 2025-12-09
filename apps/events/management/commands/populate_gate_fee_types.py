"""
Comando para poblar tipos de tarifas de entrada iniciales
"""
from django.core.management.base import BaseCommand

from apps.events.models import GateFeeType


class Command(BaseCommand):
    help = "Pobla la base de datos con tipos de tarifas de entrada iniciales"

    def handle(self, *args, **options):
        gate_fee_types = [
            {
                "name": "PLAYER GATE FEE",
                "description": "Tarifa de entrada para jugadores",
            },
            {
                "name": "SPECTATOR GATE FEE",
                "description": "Tarifa de entrada para espectadores",
            },
        ]

        created_count = 0
        updated_count = 0

        for gate_fee_type_data in gate_fee_types:
            gate_fee_type, created = GateFeeType.objects.get_or_create(
                name=gate_fee_type_data["name"],
                defaults={
                    "description": gate_fee_type_data["description"],
                    "is_active": True,
                },
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Tipo de tarifa de entrada "{gate_fee_type.name}" creado exitosamente'
                    )
                )
            else:
                # Actualizar si ya existe pero está inactivo
                if not gate_fee_type.is_active:
                    gate_fee_type.is_active = True
                    gate_fee_type.description = gate_fee_type_data["description"]
                    gate_fee_type.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'↻ Tipo de tarifa de entrada "{gate_fee_type.name}" reactivado y actualizado'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.NOTICE(
                            f'- Tipo de tarifa de entrada "{gate_fee_type.name}" ya existe'
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Proceso completado: {created_count} creados, {updated_count} actualizados"
            )
        )













