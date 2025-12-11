import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

import json
from django.db import transaction
from apps.locations.models import Country, State, City

# Forzar salida UTF-8
if sys.stdout.encoding != "utf-8":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")

print("=" * 60)
print("IMPORTACIÓN DE ESTADOS UNIDOS")
print("=" * 60)
sys.stdout.flush()

# Cargar JSON
json_file = "countries+states+cities.json"
print(f"\n📂 Cargando {json_file}...")
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)
print(f"✓ Archivo cargado: {len(data)} países")

# Buscar Estados Unidos
us_country = None
for country in data:
    name = country.get("name", "").lower()
    iso2 = country.get("iso2", "").upper()
    if (
        "united states" in name
        or iso2 == "US"
        or country.get("iso3", "").upper() == "USA"
    ):
        us_country = country
        break

if not us_country:
    print("❌ No se encontró Estados Unidos")
    exit(1)

print(
    f"\n✓ País encontrado: {us_country['name']} (ISO2: {us_country.get('iso2', 'N/A')})"
)

states_data = us_country.get("states", [])
total_cities = sum(len(state.get("cities", [])) for state in states_data)

print(f"  - Estados: {len(states_data)}")
print(f"  - Ciudades totales: {total_cities}")

print("\n🔄 Importando datos...")

try:
    with transaction.atomic():
        # Crear o obtener el país
        country, created = Country.objects.get_or_create(
            code=us_country.get("iso2", "US").upper(),
            defaults={
                "name": us_country["name"],
                "is_active": True,
            },
        )

        if created:
            print(f"✓ País creado: {country.name}")
        else:
            print(f"⚠ País ya existe: {country.name}")

        # Importar estados y ciudades
        states_created = 0
        cities_created = 0

        for idx, state_data in enumerate(states_data, 1):
            state_name = state_data.get("name")
            if not state_name:
                continue

            # Crear o obtener el estado
            state, state_created = State.objects.get_or_create(
                country=country,
                name=state_name,
                defaults={
                    "code": (
                        state_data.get("iso2", "")[:10]
                        if state_data.get("iso2")
                        else ""
                    ),
                    "is_active": True,
                },
            )

            if state_created:
                states_created += 1

            # Importar ciudades del estado
            cities_data = state_data.get("cities", [])
            for city_data in cities_data:
                city_name = city_data.get("name")
                if not city_name:
                    continue

                City.objects.get_or_create(
                    state=state,
                    name=city_name,
                    defaults={"is_active": True},
                )
                cities_created += 1

            # Mostrar progreso cada 10 estados
            if idx % 10 == 0:
                print(f"  Procesados {idx}/{len(states_data)} estados...")
                sys.stdout.flush()

        print("\n✅ Importación completada!")
        print(f"   - País: {'Creado' if created else 'Ya existía'}")
        print(f"   - Estados creados: {states_created}")
        print(f"   - Ciudades creadas: {cities_created}")
        sys.stdout.flush()

        # Verificar resultados
        final_states = State.objects.filter(country=country).count()
        final_cities = City.objects.filter(state__country=country).count()
        print(f"\n📊 Verificación:")
        print(f"   - Estados en BD: {final_states}")
        print(f"   - Ciudades en BD: {final_cities}")
        sys.stdout.flush()

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback

    traceback.print_exc()




