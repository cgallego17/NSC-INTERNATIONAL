"""
Script final para verificar y crear tipos de eventos
"""

import os
import django
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from apps.events.models import EventType
from apps.events.forms import EventForm

print("=" * 70)
print("VERIFICACIÓN FINAL DE EVENTTYPE")
print("=" * 70)

# Verificar datos
print("\n1. Verificando datos en la base de datos:")
count = EventType.objects.count()
print(f"   Total tipos: {count}")

if count == 0:
    print("   ✗ No hay tipos de eventos. Creándolos...")
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

    for tipo_data in tipos:
        tipo, created = EventType.objects.get_or_create(
            name=tipo_data["name"], defaults={**tipo_data, "is_active": True}
        )
        if created:
            print(f"   ✓ Creado: {tipo.name}")
        else:
            print(f"   - Ya existe: {tipo.name}")

    count = EventType.objects.count()
    print(f"   ✓ Total después de crear: {count}")

print("\n2. Listando tipos de eventos:")
for tipo in EventType.objects.all():
    print(f"   - ID: {tipo.id}, Name: {tipo.name}, Active: {tipo.is_active}")

# Verificar formulario
print("\n3. Verificando formulario:")
try:
    form = EventForm()
    print(f"   Campos en formulario: {list(form.fields.keys())}")

    if "event_type" in form.fields:
        et_field = form.fields["event_type"]
        queryset = et_field.queryset
        qs_count = queryset.count()
        print(f"   ✓ Campo 'event_type' existe")
        print(f"   Queryset count: {qs_count}")

        if qs_count > 0:
            print(f"   Opciones disponibles:")
            for et in queryset:
                print(f"     - {et.id}: {et.name}")
        else:
            print(f"   ✗ Queryset está vacío!")
            print(
                f"   Esto significa que no hay tipos activos o hay un problema con el filtro"
            )
    else:
        print(f"   ✗ Campo 'event_type' NO está en el formulario!")

except Exception as e:
    print(f"   ✗ Error al crear formulario: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 70)
print("FIN DE VERIFICACIÓN")
print("=" * 70)
