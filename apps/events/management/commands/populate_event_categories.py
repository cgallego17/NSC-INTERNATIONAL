"""
Comando para poblar categorías de eventos iniciales
"""

from django.core.management.base import BaseCommand

from apps.events.models import EventCategory


class Command(BaseCommand):
    help = "Pobla la base de datos con categorías de eventos iniciales"

    def handle(self, *args, **options):
        event_categories = [
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

        for category_data in event_categories:
            category, created = EventCategory.objects.get_or_create(
                name=category_data["name"],
                defaults={
                    "description": category_data["description"],
                    "color": category_data["color"],
                    "icon": category_data["icon"],
                    "is_active": True,
                },
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Categoría "{category.name}" creada exitosamente'
                    )
                )
            else:
                # Actualizar si ya existe pero está inactiva
                if not category.is_active:
                    category.is_active = True
                    category.description = category_data["description"]
                    category.color = category_data["color"]
                    category.icon = category_data["icon"]
                    category.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'↻ Categoría "{category.name}" reactivada y actualizada'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.NOTICE(f'- Categoría "{category.name}" ya existe')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Proceso completado: {created_count} creadas, {updated_count} actualizadas"
            )
        )






