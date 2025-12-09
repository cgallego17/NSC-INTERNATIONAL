"""
Script para insertar los tipos de eventos: LIGA, SHOWCASES, TORNEO, WORLD SERIES
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from apps.events.models import EventType
from datetime import datetime

print("=" * 70)
print("INSERTANDO TIPOS DE EVENTOS")
print("=" * 70)

tipos_eventos = [
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

for tipo_data in tipos_eventos:
    tipo, created = EventType.objects.get_or_create(
        name=tipo_data["name"],
        defaults={
            "description": tipo_data["description"],
            "color": tipo_data["color"],
            "icon": tipo_data["icon"],
            "is_active": True,
        },
    )

    if created:
        creados += 1
        print(f"✓ Creado: {tipo.name}")
    else:
        # Actualizar si es necesario
        actualizado = False
        if tipo.description != tipo_data["description"]:
            tipo.description = tipo_data["description"]
            actualizado = True
        if tipo.color != tipo_data["color"]:
            tipo.color = tipo_data["color"]
            actualizado = True
        if tipo.icon != tipo_data["icon"]:
            tipo.icon = tipo_data["icon"]
            actualizado = True
        if not tipo.is_active:
            tipo.is_active = True
            actualizado = True

        if actualizado:
            tipo.save()
            actualizados += 1
            print(f"↻ Actualizado: {tipo.name}")
        else:
            print(f"- Ya existe: {tipo.name}")

print("\n" + "=" * 70)
print(f"✓ Proceso completado: {creados} creados, {actualizados} actualizados")
print("=" * 70)

# Mostrar todos los tipos
print("\nTipos de eventos en la base de datos:")
for tipo in EventType.objects.all().order_by("name"):
    print(f"  - {tipo.name}")
