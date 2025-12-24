#!/usr/bin/env python
"""Script para verificar países duplicados"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from apps.locations.models import Country

print("=" * 60)
print("VERIFICACIÓN DE PAÍSES")
print("=" * 60)

# Todos los países
all_countries = Country.objects.all().order_by("name")
print(f"\nTotal de países en la base de datos: {all_countries.count()}\n")

# Países activos
active_countries = Country.objects.filter(is_active=True).order_by("name")
print(f"Países activos: {active_countries.count()}\n")

# Buscar duplicados por nombre (case-insensitive)
from collections import defaultdict

country_dict = defaultdict(list)

for country in all_countries:
    normalized = country.name.strip().lower()
    country_dict[normalized].append(country)

duplicates = {k: v for k, v in country_dict.items() if len(v) > 1}

if duplicates:
    print("⚠️  PAÍSES DUPLICADOS ENCONTRADOS:\n")
    for normalized_name, countries in duplicates.items():
        print(f"  '{normalized_name}' aparece {len(countries)} veces:")
        for c in countries:
            print(
                f"    - ID: {c.id}, Nombre: '{c.name}', Código: {c.code}, Activo: {c.is_active}"
            )
        print()
else:
    print("✓ No se encontraron países duplicados por nombre exacto\n")

# Buscar variantes de México
mexico_variants = []
for country in all_countries:
    name_lower = country.name.lower()
    if "mex" in name_lower or "méx" in name_lower:
        mexico_variants.append(country)

if mexico_variants:
    print("🔍 VARIANTES DE 'MÉXICO' ENCONTRADAS:\n")
    for c in mexico_variants:
        print(
            f"  ID: {c.id}, Nombre: '{c.name}', Código: {c.code}, Activo: {c.is_active}"
        )
    print()

# Listar todos los países activos
print("📋 PAÍSES ACTIVOS (como aparecen en el formulario):\n")
for i, country in enumerate(active_countries, 1):
    print(f"  {i}. {country.name} (ID: {country.id}, Código: {country.code})")

print("\n" + "=" * 60)
