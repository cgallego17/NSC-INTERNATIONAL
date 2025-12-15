#!/usr/bin/env python
"""Script para eliminar todos los países, estados y ciudades"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from apps.locations.models import Country, State, City, Site, Hotel

print("=" * 60)
print("ELIMINACIÓN DE TODOS LOS PAÍSES, ESTADOS Y CIUDADES")
print("=" * 60)

# Contar registros antes de eliminar
countries_count = Country.objects.count()
states_count = State.objects.count()
cities_count = City.objects.count()
sites_count = Site.objects.count()
hotels_count = Hotel.objects.count()

print(f"\nRegistros actuales:")
print(f"  - Países: {countries_count}")
print(f"  - Estados: {states_count}")
print(f"  - Ciudades: {cities_count}")
print(f"  - Sitios: {sites_count}")
print(f"  - Hoteles: {hotels_count}")

# Confirmar
print(
    "\n⚠️  ADVERTENCIA: Esta operación eliminará TODOS los países, estados y ciudades."
)
print("   También se eliminarán todos los sitios y hoteles relacionados.")
print("\n¿Estás seguro? Esta acción NO se puede deshacer.")
print(
    "\nPara confirmar, ejecuta: python eliminar_todos_paises_estados_ciudades.py --confirmar"
)

import sys

if "--confirmar" not in sys.argv:
    print("\n❌ Operación cancelada. Agrega --confirmar para ejecutar.")
    sys.exit(0)

print("\n🔄 Eliminando...")
import sys

sys.stdout.flush()

# Eliminar en orden: ciudades -> estados -> países
# (Las relaciones CASCADE se encargarán automáticamente)

# 1. Eliminar todas las ciudades
print("Eliminando ciudades...")
deleted_cities = City.objects.all().delete()
print(f"✓ Ciudades eliminadas: {deleted_cities[0]}")
sys.stdout.flush()

# 2. Eliminar todos los estados
print("Eliminando estados...")
deleted_states = State.objects.all().delete()
print(f"✓ Estados eliminados: {deleted_states[0]}")
sys.stdout.flush()

# 3. Eliminar todos los países
print("Eliminando países...")
deleted_countries = Country.objects.all().delete()
print(f"✓ Países eliminados: {deleted_countries[0]}")
sys.stdout.flush()

# Verificar que también se eliminaron sitios y hoteles relacionados
remaining_sites = Site.objects.count()
remaining_hotels = Hotel.objects.count()

print(f"\n✅ Eliminación completada!")
print(f"   - Países eliminados: {deleted_countries[0]}")
print(f"   - Estados eliminados: {deleted_states[0]}")
print(f"   - Ciudades eliminadas: {deleted_cities[0]}")

if remaining_sites > 0:
    print(
        f"\n⚠️  Nota: Quedan {remaining_sites} sitios (pueden tener country/state/city en NULL)"
    )
if remaining_hotels > 0:
    print(
        f"⚠️  Nota: Quedan {remaining_hotels} hoteles (pueden tener country/state/city en NULL)"
    )

print("\n" + "=" * 60)





