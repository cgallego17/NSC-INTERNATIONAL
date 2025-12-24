"""
Script para verificar y solucionar el problema de event_type
"""

import os
import django
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from apps.events.models import EventType
from apps.events.forms import EventForm

print("=" * 70)
print("VERIFICACIÓN DE EVENT_TYPE")
print("=" * 70)

# 1. Verificar datos
print("\n1. Verificando datos en la base de datos:")
count = EventType.objects.count()
print(f"   Total tipos: {count}")

active_count = EventType.objects.filter(is_active=True).count()
print(f"   Tipos activos: {active_count}")

if active_count == 0:
    print("   ✗ No hay tipos activos. Creándolos...")
    tipos = [
        {
            "name": "LIGA",
            "description": "Evento de liga regular",
            "color": "#0d2c54",
            "icon": "fas fa-trophy",
        },
        {
            "name": "SHOWCASES",
            "description": "Evento showcase",
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
            "description": "Serie mundial",
            "color": "#0d2c54",
            "icon": "fas fa-globe",
        },
    ]

    for tipo_data in tipos:
        tipo, created = EventType.objects.get_or_create(
            name=tipo_data["name"], defaults={**tipo_data, "is_active": True}
        )
        if created:
            print(f"   ✓ Creado: {tipo.name}")
        else:
            tipo.is_active = True
            tipo.save()
            print(f"   ↻ Reactivado: {tipo.name}")

print("\n2. Tipos en la base de datos:")
for tipo in EventType.objects.filter(is_active=True):
    print(f"   - {tipo.id}: {tipo.name}")

# 3. Verificar formulario
print("\n3. Verificando formulario:")
try:
    form = EventForm()
    print(f"   Campos: {list(form.fields.keys())}")

    if "event_type" in form.fields:
        et_field = form.fields["event_type"]
        queryset = et_field.queryset
        qs_count = queryset.count()
        print(f"   ✓ Campo 'event_type' existe")
        print(f"   Queryset count: {qs_count}")

        if qs_count > 0:
            print(f"   ✓ Opciones disponibles:")
            for et in queryset:
                print(f"     - {et.id}: {et.name}")
        else:
            print(f"   ✗ PROBLEMA: Queryset está vacío!")
            print(f"   Verificando directamente...")
            direct = EventType.objects.filter(is_active=True)
            print(f"   Direct query count: {direct.count()}")
            if direct.count() > 0:
                print(f"   Forzando queryset...")
                form.fields["event_type"].queryset = direct.order_by("name")
                print(f"   Nuevo count: {form.fields['event_type'].queryset.count()}")
    else:
        print(f"   ✗ Campo 'event_type' NO está en el formulario!")

except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 70)
print("FIN")
print("=" * 70)
