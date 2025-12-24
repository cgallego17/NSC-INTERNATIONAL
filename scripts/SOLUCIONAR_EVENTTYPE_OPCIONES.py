"""
Script para verificar y crear tipos de eventos con salida visible
"""

import os
import django
import sys

# Forzar salida inmediata
sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from apps.events.models import EventType
from apps.events.forms import EventForm

print("\n" + "=" * 70)
print("SOLUCIONANDO PROBLEMA DE OPCIONES EN EVENT_TYPE")
print("=" * 70 + "\n")

# 1. Verificar datos
print("1. Verificando datos en la base de datos:")
count = EventType.objects.count()
print(f"   Total tipos: {count}")

if count == 0:
    print("   ✗ No hay tipos. Creándolos...\n")
else:
    print("   Tipos existentes:")
    for tipo in EventType.objects.all():
        print(f"     - ID: {tipo.id}, Name: '{tipo.name}', Active: {tipo.is_active}")

# 2. Crear/actualizar tipos
print("\n2. Asegurando que los tipos existan y estén activos:")
tipos = [
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

creados = 0
actualizados = 0

for tipo_data in tipos:
    tipo, created = EventType.objects.get_or_create(
        name=tipo_data["name"], defaults={**tipo_data, "is_active": True}
    )

    if created:
        creados += 1
        print(f"   ✓ Creado: {tipo.name}")
    else:
        # Asegurar que esté activo
        if not tipo.is_active:
            tipo.is_active = True
            tipo.save()
            actualizados += 1
            print(f"   ↻ Reactivado: {tipo.name}")
        else:
            print(f"   - Ya existe y está activo: {tipo.name}")

print(f"\n   Resumen: {creados} creados, {actualizados} actualizados")

# 3. Verificar queryset del formulario
print("\n3. Verificando queryset del formulario:")
try:
    form = EventForm()

    if "event_type" in form.fields:
        et_field = form.fields["event_type"]
        queryset = et_field.queryset

        print(f"   Campo 'event_type' existe en el formulario")
        print(f"   Queryset count: {queryset.count()}")

        if queryset.count() > 0:
            print(f"   ✓ Opciones disponibles:")
            for et in queryset:
                print(f"     - {et.id}: {et.name}")
        else:
            print(f"   ✗ PROBLEMA: Queryset está vacío!")
            print(f"   Verificando directamente desde el modelo...")

            # Verificar directamente
            direct_count = EventType.objects.filter(is_active=True).count()
            print(
                f"   EventType.objects.filter(is_active=True).count(): {direct_count}"
            )

            if direct_count > 0:
                print(f"   Tipos activos encontrados directamente:")
                for et in EventType.objects.filter(is_active=True):
                    print(f"     - {et.id}: {et.name}")

                print(f"\n   Intentando forzar el queryset...")
                # Forzar el queryset
                form.fields["event_type"].queryset = EventType.objects.filter(
                    is_active=True
                ).order_by("name")
                new_count = form.fields["event_type"].queryset.count()
                print(f"   Nuevo queryset count: {new_count}")
    else:
        print(f"   ✗ Campo 'event_type' NO está en el formulario!")

except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 70)
print("FIN")
print("=" * 70 + "\n")
