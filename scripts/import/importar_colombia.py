import os
import sys

# Cambiar al directorio raíz del proyecto si es necesario
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if os.path.basename(project_root) != 'NSC-INTERNATIONAL':
    # Si el script está en scripts/, subir un nivel
    project_root = os.path.dirname(script_dir)

# Agregar el directorio raíz al path de Python
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Cambiar al directorio raíz del proyecto
os.chdir(project_root)

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
print("IMPORTACIÓN DE COLOMBIA")
print("=" * 60)
sys.stdout.flush()

# Cargar JSON
# Buscar el archivo en data/ desde el directorio raíz del proyecto
json_file = None
json_paths = [
    os.path.join(project_root, "data", "countries+states+cities.json"),
    os.path.join(project_root, "countries+states+cities.json"),
    "data/countries+states+cities.json",
    "countries+states+cities.json"
]

for path in json_paths:
    if os.path.exists(path):
        json_file = path
        break

if not json_file:
    print("❌ No se encontró el archivo countries+states+cities.json")
    print(f"   Directorio actual: {os.getcwd()}")
    print(f"   Directorio raíz del proyecto: {project_root}")
    print("   Buscado en:")
    for path in json_paths:
        print(f"     - {path}")
    exit(1)
print(f"\n📂 Cargando {json_file}...")
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)
print(f"✓ Archivo cargado: {len(data)} países")

# Buscar Colombia
colombia_country = None
for country in data:
    name = country.get("name", "").lower()
    iso2 = country.get("iso2", "").upper()
    iso3 = country.get("iso3", "").upper()
    if (
        "colombia" in name
        or iso2 == "CO"
        or iso3 == "COL"
    ):
        colombia_country = country
        break

if not colombia_country:
    print("❌ No se encontró Colombia")
    exit(1)

print(
    f"\n✓ País encontrado: {colombia_country['name']} (ISO2: {colombia_country.get('iso2', 'N/A')})"
)

states_data = colombia_country.get("states", [])
total_cities = sum(len(state.get("cities", [])) for state in states_data)

print(f"  - Departamentos: {len(states_data)}")
print(f"  - Ciudades totales: {total_cities}")

print("\n🔄 Importando datos...")

try:
    with transaction.atomic():
        # Crear o obtener el país
        country, created = Country.objects.get_or_create(
            code=colombia_country.get("iso2", "CO").upper(),
            defaults={
                "name": "Colombia",
                "is_active": True,
            },
        )

        if created:
            print(f"✓ País creado: {country.name}")
        else:
            print(f"⚠ País ya existe: {country.name}")

        # Importar departamentos y ciudades
        states_created = 0
        cities_created = 0

        for idx, state_data in enumerate(states_data, 1):
            state_name = state_data.get("name")
            if not state_name:
                continue

            # Crear o obtener el departamento
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

            # Importar ciudades del departamento
            cities_data = state_data.get("cities", [])
            for city_data in cities_data:
                city_name = city_data.get("name")
                if not city_name:
                    continue

                city, city_created = City.objects.get_or_create(
                    state=state,
                    name=city_name,
                    defaults={"is_active": True},
                )
                if city_created:
                    cities_created += 1

            # Mostrar progreso cada 10 departamentos
            if idx % 10 == 0:
                print(f"  Procesados {idx}/{len(states_data)} departamentos...")
                sys.stdout.flush()

        print("\n✅ Importación completada!")
        print(f"   - País: {'Creado' if created else 'Ya existía'}")
        print(f"   - Departamentos creados: {states_created}")
        print(f"   - Ciudades creadas: {cities_created}")
        sys.stdout.flush()

        # Verificar resultados
        final_states = State.objects.filter(country=country).count()
        final_cities = City.objects.filter(state__country=country).count()
        print(f"\n📊 Verificación:")
        print(f"   - Departamentos en BD: {final_states}")
        print(f"   - Ciudades en BD: {final_cities}")
        sys.stdout.flush()

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback

    traceback.print_exc()

