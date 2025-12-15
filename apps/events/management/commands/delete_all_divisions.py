"""
Comando de gestión para eliminar todas las divisiones
"""

from django.core.management.base import BaseCommand
from apps.events.models import Division, Event


class Command(BaseCommand):
    help = "Elimina todas las divisiones de la base de datos"

    def handle(self, *args, **options):
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("ELIMINACIÓN DE TODAS LAS DIVISIONES"))
        self.stdout.write("=" * 70)

        # Paso 1: Verificar divisiones
        count_before = Division.objects.count()
        self.stdout.write(f"\n1. Divisiones encontradas: {count_before}")

        if count_before > 0:
            self.stdout.write("\n   Divisiones existentes:")
            for division in Division.objects.all():
                self.stdout.write(f"     - ID {division.id}: {division.name}")

        # Paso 2: Eliminar relaciones ManyToMany
        self.stdout.write("\n2. Verificando relaciones con eventos...")
        events_with_divisions = (
            Event.objects.filter(divisions__isnull=False).distinct().count()
        )
        self.stdout.write(
            f"   Eventos con divisiones asignadas: {events_with_divisions}"
        )

        if events_with_divisions > 0:
            self.stdout.write("   Eliminando relaciones de divisiones en eventos...")
            for event in Event.objects.all():
                event.divisions.clear()
            self.stdout.write(self.style.SUCCESS("   ✓ Relaciones eliminadas"))

        # Paso 3: Eliminar divisiones
        self.stdout.write("\n3. Eliminando divisiones...")
        if count_before > 0:
            deleted = Division.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f"   ✓ Divisiones eliminadas: {deleted[0]}")
            )
        else:
            self.stdout.write("   No hay divisiones para eliminar")

        # Paso 4: Verificación final
        count_final = Division.objects.count()
        self.stdout.write(f"\n4. Verificación final:")
        self.stdout.write(f"   Divisiones restantes: {count_final}")

        self.stdout.write("\n" + "=" * 70)
        if count_final == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    "✓ TODAS LAS DIVISIONES FUERON ELIMINADAS EXITOSAMENTE"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"⚠ AÚN QUEDAN {count_final} DIVISIONES")
            )
        self.stdout.write("=" * 70)






