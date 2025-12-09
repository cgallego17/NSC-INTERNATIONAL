"""
Script definitivo para crear tipos de eventos usando Django ORM
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from apps.events.models import EventType

print("=" * 70)
print("CREANDO TIPOS DE EVENTOS")
print("=" * 70)

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
for tipo_data in tipos:
    tipo, created = EventType.objects.get_or_create(
        name=tipo_data["name"], defaults={**tipo_data, "is_active": True}
    )
    if created:
        creados += 1
        print(f"✓ Creado: {tipo.name}")
    else:
        # Actualizar si está inactivo
        if not tipo.is_active:
            tipo.is_active = True
            tipo.save()
            print(f"↻ Reactivado: {tipo.name}")
        else:
            print(f"- Ya existe: {tipo.name}")

print(f"\n✓ Proceso completado: {creados} creados")
print(f"Total tipos: {EventType.objects.count()}")

# Verificar
print("\nTipos disponibles:")
for tipo in EventType.objects.filter(is_active=True):
    print(f"  - {tipo.name} (ID: {tipo.id})")
