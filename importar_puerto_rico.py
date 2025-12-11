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
print("IMPORTACIÓN DE PUERTO RICO")
print("=" * 60)
sys.stdout.flush()

# Cargar JSON
json_file = "countries+states+cities.json"
print(f"\n📂 Cargando {json_file}...")
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)
print(f"✓ Archivo cargado: {len(data)} países")

# Buscar Puerto Rico
pr_country = None
for country in data:
    name = country.get("name", "").lower()
    iso2 = country.get("iso2", "").upper()
    iso3 = country.get("iso3", "").upper()
    if "puerto rico" in name or iso2 == "PR" or iso3 == "PRI":
        pr_country = country
        break

if not pr_country:
    print("❌ No se encontró Puerto Rico")
    exit(1)

print(
    f"\n✓ País encontrado: {pr_country['name']} (ISO2: {pr_country.get('iso2', 'N/A')})"
)

states_data = pr_country.get("states", [])
total_cities = sum(len(state.get("cities", [])) for state in states_data)

print(f"  - Estados/Municipios: {len(states_data)}")
print(f"  - Ciudades totales: {total_cities}")

print("\n🔄 Importando datos...")

try:
    with transaction.atomic():
        # Crear o obtener el país
        country, created = Country.objects.get_or_create(
            code=pr_country.get("iso2", "PR").upper(),
            defaults={
                "name": "Puerto Rico",
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
                print(f"  Procesados {idx}/{len(states_data)} estados/municipios...")
                sys.stdout.flush()

        print("\n✅ Importación completada!")
        print(f"   - País: {'Creado' if created else 'Ya existía'}")
        print(f"   - Estados/Municipios creados: {states_created}")
        print(f"   - Ciudades creadas: {cities_created}")
        sys.stdout.flush()

        # Verificar resultados
        final_states = State.objects.filter(country=country).count()
        final_cities = City.objects.filter(state__country=country).count()
        print(f"\n📊 Verificación:")
        print(f"   - Estados/Municipios en BD: {final_states}")
        print(f"   - Ciudades en BD: {final_cities}")
        sys.stdout.flush()

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback

    traceback.print_exc()




