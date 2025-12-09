"""
Comando para eliminar todos los países, estados y ciudades
"""

from django.core.management.base import BaseCommand
from apps.locations.models import Country, State, City, Site, Hotel


class Command(BaseCommand):
    help = "Elimina todos los países, estados y ciudades"

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirmar",
            action="store_true",
            help="Confirma la eliminación (requerido para ejecutar)",
        )

    def handle(self, *args, **options):
        if not options["confirmar"]:
            self.stdout.write(
                self.style.WARNING(
                    "\n⚠️  ADVERTENCIA: Esta operación eliminará TODOS los países, estados y ciudades."
                )
            )
            self.stdout.write(
                "   También se eliminarán todos los sitios y hoteles relacionados."
            )
            self.stdout.write("\n¿Estás seguro? Esta acción NO se puede deshacer.")
            self.stdout.write(
                "\nPara confirmar, ejecuta: python manage.py delete_all_locations --confirmar"
            )
            return

        # Contar registros antes de eliminar
        countries_count = Country.objects.count()
        states_count = State.objects.count()
        cities_count = City.objects.count()
        sites_count = Site.objects.count()
        hotels_count = Hotel.objects.count()

        self.stdout.write(self.style.WARNING("\n" + "=" * 60))
        self.stdout.write(
            self.style.WARNING("ELIMINACIÓN DE TODOS LOS PAÍSES, ESTADOS Y CIUDADES")
        )
        self.stdout.write(self.style.WARNING("=" * 60))

        self.stdout.write(f"\nRegistros actuales:")
        self.stdout.write(f"  - Países: {countries_count}")
        self.stdout.write(f"  - Estados: {states_count}")
        self.stdout.write(f"  - Ciudades: {cities_count}")
        self.stdout.write(f"  - Sitios: {sites_count}")
        self.stdout.write(f"  - Hoteles: {hotels_count}")

        self.stdout.write(self.style.WARNING("\n🔄 Eliminando..."))

        # Eliminar en orden: ciudades -> estados -> países
        # (Las relaciones CASCADE se encargarán automáticamente)

        # 1. Eliminar todas las ciudades
        deleted_cities = City.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f"✓ Ciudades eliminadas: {deleted_cities[0]}")
        )

        # 2. Eliminar todos los estados
        deleted_states = State.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f"✓ Estados eliminados: {deleted_states[0]}")
        )

        # 3. Eliminar todos los países
        deleted_countries = Country.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f"✓ Países eliminados: {deleted_countries[0]}")
        )

        # Verificar que también se eliminaron sitios y hoteles relacionados
        remaining_sites = Site.objects.count()
        remaining_hotels = Hotel.objects.count()

        self.stdout.write(self.style.SUCCESS("\n✅ Eliminación completada!"))
        self.stdout.write(f"   - Países eliminados: {deleted_countries[0]}")
        self.stdout.write(f"   - Estados eliminados: {deleted_states[0]}")
        self.stdout.write(f"   - Ciudades eliminadas: {deleted_cities[0]}")

        if remaining_sites > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"\n⚠️  Nota: Quedan {remaining_sites} sitios (pueden tener country/state/city en NULL)"
                )
            )
        if remaining_hotels > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️  Nota: Quedan {remaining_hotels} hoteles (pueden tener country/state/city en NULL)"
                )
            )
