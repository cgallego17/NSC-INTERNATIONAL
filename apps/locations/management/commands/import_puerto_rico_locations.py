"""
Comando para importar Puerto Rico, sus estados y ciudades desde el JSON
"""

import json
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.locations.models import Country, State, City


class Command(BaseCommand):
    help = (
        "Importa Puerto Rico, sus estados y ciudades desde countries+states+cities.json"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--json-file",
            type=str,
            default="countries+states+cities.json",
            help="Ruta al archivo JSON (por defecto: countries+states+cities.json)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Solo muestra lo que se importaría sin hacer cambios",
        )

    def handle(self, *args, **options):
        json_file = options["json_file"]
        dry_run = options["dry_run"]

        if not os.path.exists(json_file):
            self.stdout.write(self.style.ERROR(f"❌ El archivo {json_file} no existe."))
            return

        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("IMPORTACIÓN DE PUERTO RICO"))
        self.stdout.write(self.style.SUCCESS("=" * 60))

        # Cargar JSON
        self.stdout.write(f"\n📂 Cargando {json_file}...")
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.stdout.write(
                self.style.SUCCESS(f"✓ Archivo cargado: {len(data)} países")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error al cargar JSON: {e}"))
            return

        # Buscar Puerto Rico (buscar por nombre o ISO2)
        pr_country = None
        for country in data:
            name = country.get("name", "").lower()
            iso2 = country.get("iso2", "").upper()
            iso3 = country.get("iso3", "").upper()
            if "puerto rico" in name or iso2 == "PR" or iso3 == "PRI":
                pr_country = country
                break

        if not pr_country:
            self.stdout.write(
                self.style.ERROR("❌ No se encontró Puerto Rico en el JSON")
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ País encontrado: {pr_country['name']} (ISO2: {pr_country.get('iso2', 'N/A')})"
            )
        )

        states_data = pr_country.get("states", [])
        total_cities = sum(len(state.get("cities", [])) for state in states_data)

        self.stdout.write(f"  - Estados/Municipios: {len(states_data)}")
        self.stdout.write(f"  - Ciudades totales: {total_cities}")

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\n🔍 DRY RUN: No se realizarán cambios en la base de datos"
                )
            )
            self.stdout.write(f"  Se crearían:")
            self.stdout.write(f"    - 1 país: {pr_country['name']}")
            self.stdout.write(f"    - {len(states_data)} estados/municipios")
            self.stdout.write(f"    - {total_cities} ciudades")
            return

        # Importar con transacción
        self.stdout.write(self.style.WARNING("\n🔄 Importando datos..."))

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
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ País creado: {country.name}")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"⚠ País ya existe: {country.name}")
                    )

                # Importar estados y ciudades
                states_created = 0
                states_updated = 0
                cities_created = 0
                cities_updated = 0

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
                    else:
                        states_updated += 1
                        # Actualizar código si está vacío
                        if not state.code and state_data.get("iso2"):
                            state.code = state_data.get("iso2", "")[:10]
                            state.save()

                    # Importar ciudades del estado
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
                            cities_updated += 1

                    # Mostrar progreso cada 10 estados
                    if idx % 10 == 0:
                        self.stdout.write(
                            f"  Procesados {idx}/{len(states_data)} estados/municipios..."
                        )

                self.stdout.write(self.style.SUCCESS("\n✅ Importación completada!"))
                self.stdout.write(f"   - País: {'Creado' if created else 'Ya existía'}")
                self.stdout.write(f"   - Estados/Municipios creados: {states_created}")
                self.stdout.write(
                    f"   - Estados/Municipios actualizados: {states_updated}"
                )
                self.stdout.write(f"   - Ciudades creadas: {cities_created}")
                self.stdout.write(f"   - Ciudades actualizadas: {cities_updated}")

                # Verificar resultados
                final_states = State.objects.filter(country=country).count()
                final_cities = City.objects.filter(state__country=country).count()
                self.stdout.write(f"\n📊 Verificación:")
                self.stdout.write(f"   - Estados/Municipios en BD: {final_states}")
                self.stdout.write(f"   - Ciudades en BD: {final_cities}")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\n❌ Error durante la importación: {e}")
            )
            import traceback

            self.stdout.write(self.style.ERROR(traceback.format_exc()))
            raise





