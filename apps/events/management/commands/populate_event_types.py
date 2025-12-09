"""
Comando para poblar tipos de eventos iniciales
"""

from django.core.management.base import BaseCommand

from apps.events.models import EventType


class Command(BaseCommand):
    help = "Pobla la base de datos con tipos de eventos iniciales"

    def handle(self, *args, **options):
        event_types = [
            {
                "name": "LIGA",
                "description": "Evento de liga regular",
                "color": "#0d2c54",
                "icon": "fas fa-trophy",
            },
            {
                "name": "SHOWCASES",
                "description": "Evento showcase para mostrar talento",
                "color": "#0d2c54",
                "icon": "fas fa-star",
            },
            {
                "name": "TORNEO",
                "description": "Torneo competitivo",
                "color": "#0d2c54",
                "icon": "fas fa-medal",
            },
            {
                "name": "WORLD SERIES",
                "description": "Serie mundial de béisbol",
                "color": "#0d2c54",
                "icon": "fas fa-globe",
            },
        ]

        created_count = 0
        updated_count = 0

        for event_type_data in event_types:
            event_type, created = EventType.objects.get_or_create(
                name=event_type_data["name"],
                defaults={
                    "description": event_type_data["description"],
                    "color": event_type_data.get("color", "#0d2c54"),
                    "icon": event_type_data.get("icon", "fas fa-calendar"),
                    "is_active": True,
                },
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Tipo de evento "{event_type.name}" creado exitosamente'
                    )
                )
            else:
                # Actualizar si ya existe pero está inactivo
                if not event_type.is_active:
                    event_type.is_active = True
                    event_type.description = event_type_data["description"]
                    event_type.color = event_type_data.get("color", "#0d2c54")
                    event_type.icon = event_type_data.get("icon", "fas fa-calendar")
                    event_type.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'↻ Tipo de evento "{event_type.name}" reactivado y actualizado'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.NOTICE(
                            f'- Tipo de evento "{event_type.name}" ya existe'
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Proceso completado: {created_count} creados, {updated_count} actualizados"
            )
        )
