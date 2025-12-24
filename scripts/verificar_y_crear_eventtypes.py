"""
Script para verificar y crear tipos de eventos
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from apps.events.models import EventType
from django.db import connection

print("=" * 70)
print("VERIFICANDO Y CREANDO TIPOS DE EVENTOS")
print("=" * 70)

# Verificar tabla
cursor = connection.cursor()
cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='events_eventtype'"
)
table_exists = cursor.fetchone()
print(f"Tabla existe: {table_exists is not None}")

if not table_exists:
    print("ERROR: La tabla events_eventtype no existe!")
    print("Ejecuta las migraciones primero: python manage.py migrate")
    exit(1)

# Verificar datos con ORM
try:
    count = EventType.objects.count()
    print(f"\nRegistros en BD (ORM): {count}")

    if count == 0:
        print("\nNo hay tipos de eventos. Creándolos...")
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
                name=tipo_data["name"], defaults=tipo_data
            )
            if created:
                print(f"  ✓ Creado: {tipo.name}")
            else:
                print(f"  - Ya existe: {tipo.name}")

        print("\n✓ Tipos de eventos creados")
    else:
        print("\nTipos de eventos existentes:")
        for tipo in EventType.objects.all():
            print(f"  - {tipo.name} (ID: {tipo.id}, Active: {tipo.is_active})")

    # Verificar queryset del formulario
    print("\n" + "=" * 70)
    print("VERIFICANDO FORMULARIO")
    print("=" * 70)

    from apps.events.forms import EventForm

    form = EventForm()

    print(f"Campos en formulario: {list(form.fields.keys())}")
    print(f"event_type en formulario: {'event_type' in form.fields}")

    if "event_type" in form.fields:
        et_field = form.fields["event_type"]
        queryset = et_field.queryset
        print(f"Queryset count: {queryset.count()}")
        print(f"Tipos disponibles:")
        for et in queryset:
            print(f"  - {et.name} (ID: {et.id})")

except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 70)
print("COMPLETADO")
print("=" * 70)
