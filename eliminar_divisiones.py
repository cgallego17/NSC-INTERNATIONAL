import os
import django
import sqlite3

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from apps.events.models import Division, Event

# Abrir archivo para escribir resultados
with open("resultado_eliminacion_divisiones.txt", "w", encoding="utf-8") as f:
    f.write("=" * 70 + "\n")
    f.write("ELIMINACIÓN DE TODAS LAS DIVISIONES\n")
    f.write("=" * 70 + "\n\n")

    # Paso 1: Verificar
    count_before = Division.objects.count()
    f.write(f"1. Divisiones encontradas: {count_before}\n")

    if count_before > 0:
        f.write("\n   Divisiones existentes:\n")
        for division in Division.objects.all():
            f.write(f"     - ID {division.id}: {division.name}\n")

    # Paso 2: Limpiar relaciones
    f.write("\n2. Limpiando relaciones con eventos...\n")
    events_count = Event.objects.filter(divisions__isnull=False).distinct().count()
    f.write(f"   Eventos con divisiones: {events_count}\n")

    for event in Event.objects.all():
        event.divisions.clear()
    f.write("   ✓ Relaciones limpiadas\n")

    # Paso 3: Eliminar divisiones
    f.write("\n3. Eliminando divisiones...\n")
    if count_before > 0:
        deleted = Division.objects.all().delete()
        f.write(f"   ✓ Divisiones eliminadas: {deleted[0]}\n")
    else:
        f.write("   No hay divisiones para eliminar\n")

    # Paso 4: Verificación final
    count_final = Division.objects.count()
    f.write(f"\n4. Verificación final:\n")
    f.write(f"   Divisiones restantes: {count_final}\n")

    f.write("\n" + "=" * 70 + "\n")
    if count_final == 0:
        f.write("✓ TODAS LAS DIVISIONES FUERON ELIMINADAS EXITOSAMENTE\n")
    else:
        f.write(f"⚠ AÚN QUEDAN {count_final} DIVISIONES\n")
    f.write("=" * 70 + "\n")

print("Proceso completado. Ver resultado_eliminacion_divisiones.txt")





