import importlib.util
import os
import sys

# Cambiar al directorio raíz del proyecto si es necesario
script_dir = os.path.dirname(os.path.abspath(__file__))


def _discover_project_root(start_dir: str) -> str:
    """Walk up from start_dir until a Django project root is found (manage.py)."""
    current = os.path.abspath(start_dir)
    for _ in range(8):
        if os.path.exists(os.path.join(current, "manage.py")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    # Fallback: two levels up from scripts/import
    return os.path.abspath(os.path.join(start_dir, os.pardir, os.pardir))


project_root = _discover_project_root(script_dir)

# Agregar el directorio raíz al path de Python
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Cambiar al directorio raíz del proyecto
os.chdir(project_root)


def _discover_settings_module() -> str:
    """Try to find a valid <package>.settings module in the project root."""
    # Allow override via CLI: python importar_netherlands.py nsc_admin.settings
    if len(sys.argv) >= 2 and sys.argv[1] and not sys.argv[1].startswith("-"):
        return sys.argv[1]

    # Allow override via env var
    env = os.environ.get("DJANGO_SETTINGS_MODULE")
    if env:
        return env

    # Common defaults
    candidates = [
        "nsc_admin.settings",
        "config.settings",
        "core.settings",
        "project.settings",
        "settings",
    ]

    # Also scan top-level packages for a settings.py
    try:
        for entry in os.listdir(project_root):
            full = os.path.join(project_root, entry)
            if not os.path.isdir(full):
                continue
            if entry.startswith(".") or entry in {
                "venv",
                "env",
                "__pycache__",
                "node_modules",
            }:
                continue
            if os.path.exists(os.path.join(full, "settings.py")):
                candidates.insert(0, f"{entry}.settings")
    except Exception:
        pass

    for mod in candidates:
        try:
            if importlib.util.find_spec(mod) is not None:
                return mod
        except (ModuleNotFoundError, ValueError):
            continue

    raise RuntimeError(
        "No se pudo detectar DJANGO_SETTINGS_MODULE. "
        "Configúralo con DJANGO_SETTINGS_MODULE=<tu_modulo>.settings "
        "o ejecuta: python importar_netherlands.py <tu_modulo>.settings"
    )


import django

settings_module = _discover_settings_module()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
django.setup()

import json

from django.db import transaction

from apps.locations.models import City, Country, State

# Forzar salida UTF-8
if sys.stdout.encoding != "utf-8":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")

print("=" * 60)
print("IMPORTACIÓN DE NETHERLANDS")
print("=" * 60)
sys.stdout.flush()

# Cargar JSON
# Buscar el archivo en data/ desde el directorio raíz del proyecto
json_file = None
json_paths = [
    os.path.join(project_root, "data", "countries+states+cities.json"),
    os.path.join(project_root, "countries+states+cities.json"),
    "data/countries+states+cities.json",
    "countries+states+cities.json",
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
    raise SystemExit(1)

print(f"\n📂 Cargando {json_file}...")
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)
print(f"✓ Archivo cargado: {len(data)} países")

# Buscar Netherlands
nl_country = None
for country in data:
    name = (country.get("name", "") or "").lower()
    iso2 = (country.get("iso2", "") or "").upper()
    iso3 = (country.get("iso3", "") or "").upper()
    if ("netherlands" in name) or iso2 == "NL" or iso3 == "NLD":
        nl_country = country
        break

if not nl_country:
    print("❌ No se encontró Netherlands")
    raise SystemExit(1)

print(
    f"\n✓ País encontrado: {nl_country['name']} (ISO2: {nl_country.get('iso2', 'N/A')})"
)

states_data = nl_country.get("states", [])
total_cities = sum(len(state.get("cities", [])) for state in states_data)

print(f"  - Provincias/Estados: {len(states_data)}")
print(f"  - Ciudades totales: {total_cities}")

print("\n🔄 Importando datos...")

try:
    with transaction.atomic():
        # Crear o obtener el país
        country, created = Country.objects.get_or_create(
            code=(nl_country.get("iso2") or "NL").upper(),
            defaults={
                "name": "Netherlands",
                "is_active": True,
            },
        )

        if created:
            print(f"✓ País creado: {country.name}")
        else:
            # Si ya existe, asegurar que esté activo y con nombre actualizado
            updated_fields = []
            if not country.is_active:
                country.is_active = True
                updated_fields.append("is_active")
            if country.name != "Netherlands":
                country.name = "Netherlands"
                updated_fields.append("name")
            if updated_fields:
                country.save(update_fields=updated_fields)
            print(f"⚠ País ya existe: {country.name}")

        # Importar estados y ciudades
        states_created = 0
        cities_created = 0

        for idx, state_data in enumerate(states_data, 1):
            state_name = state_data.get("name")
            if not state_name:
                continue

            state_code = state_data.get("iso2") or ""
            state, state_created = State.objects.get_or_create(
                country=country,
                name=state_name,
                defaults={
                    "code": state_code[:10] if state_code else "",
                    "is_active": True,
                },
            )

            if state_created:
                states_created += 1
            else:
                # Asegurar activo
                if not state.is_active:
                    state.is_active = True
                    state.save(update_fields=["is_active"])

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
                else:
                    if not city.is_active:
                        city.is_active = True
                        city.save(update_fields=["is_active"])

            if idx % 10 == 0:
                print(f"  Procesados {idx}/{len(states_data)} estados...")
                sys.stdout.flush()

        print("\n✅ Importación completada!")
        print(f"   - País: {'Creado' if created else 'Ya existía'}")
        print(f"   - Estados creados: {states_created}")
        print(f"   - Ciudades creadas: {cities_created}")
        sys.stdout.flush()

        final_states = State.objects.filter(country=country).count()
        final_cities = City.objects.filter(state__country=country).count()
        print("\n📊 Verificación:")
        print(f"   - Estados en BD: {final_states}")
        print(f"   - Ciudades en BD: {final_cities}")
        sys.stdout.flush()

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback

    traceback.print_exc()
    raise
