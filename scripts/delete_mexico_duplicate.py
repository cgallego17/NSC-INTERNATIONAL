#!/usr/bin/env python
"""Script para eliminar el duplicado de México"""
import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from apps.locations.models import Country, State, City, Site, Hotel
from django.db.models import Q

# Forzar salida UTF-8 y flushing
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", line_buffering=True)

print("=" * 60)
print("ELIMINANDO DUPLICADO DE MÉXICO")
print("=" * 60)

# Buscar ambos países
mexico1 = Country.objects.filter(name="Mexico", is_active=True).first()
mexico2 = Country.objects.filter(name="México", is_active=True).first()

if not mexico1 and not mexico2:
    print("\n✓ No se encontraron países con nombre 'Mexico' o 'México'")
    sys.exit(0)

if mexico1 and mexico2:
    print(f"\nEncontrados dos países:")
    print(f"  1. ID {mexico1.id}: '{mexico1.name}' (Código: {mexico1.code})")
    print(f"  2. ID {mexico2.id}: '{mexico2.name}' (Código: {mexico2.code})")

    # Mantener el más antiguo (México con acento, ID 2 según el log anterior)
    keep = mexico1 if mexico1.created_at <= mexico2.created_at else mexico2
    remove = mexico2 if keep == mexico1 else mexico1

    print(f"\n✓ MANTENER: ID {keep.id} - '{keep.name}'")
    print(f"✗ ELIMINAR: ID {remove.id} - '{remove.name}'")

    # Mover estados uno por uno para manejar duplicados
    states = list(State.objects.filter(country=remove))
    print(f"\nProcesando {len(states)} estados...")

    for state in states:
        existing_state = State.objects.filter(country=keep, name=state.name).first()

        if existing_state:
            # Fusionar ciudades
            cities_moved = City.objects.filter(state=state).update(state=existing_state)
            Site.objects.filter(state=state).update(state=existing_state)
            Hotel.objects.filter(state=state).update(state=existing_state)
            state.delete()
            print(f"  → Estado '{state.name}' fusionado ({cities_moved} ciudades)")
        else:
            state.country = keep
            state.save()
            print(f"  → Estado '{state.name}' movido")

    # Mover sitios y hoteles con country directo
    Site.objects.filter(country=remove).update(country=keep)
    Hotel.objects.filter(country=remove).update(country=keep)

    # Actualizar nombre si es necesario
    if keep.name == "Mexico":
        keep.name = "México"
        keep.save()
        print(f"\n✓ Nombre actualizado a 'México'")

    # Eliminar el duplicado
    remove.delete()
    print(f"\n✅ Duplicado eliminado!")
    print(f"   País final: ID {keep.id} - '{keep.name}' (Código: {keep.code})")

elif mexico1:
    print(f"\nSolo se encontró 'Mexico'. Actualizando a 'México'...")
    mexico1.name = "México"
    mexico1.save()
    print(f"✅ Actualizado: ID {mexico1.id} - '{mexico1.name}'")
elif mexico2:
    print(f"\nSolo se encontró 'México'. Todo correcto.")
    print(f"   País: ID {mexico2.id} - '{mexico2.name}'")
