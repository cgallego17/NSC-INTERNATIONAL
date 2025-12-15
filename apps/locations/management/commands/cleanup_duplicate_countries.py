"""
Comando para limpiar países duplicados
"""

from django.core.management.base import BaseCommand
from apps.locations.models import Country, State, City, Site, Hotel
from django.db.models import Count, Q


class Command(BaseCommand):
    help = "Identifica y consolida países duplicados"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Solo muestra los duplicados sin hacer cambios",
        )
        parser.add_argument(
            "--consolidate",
            action="store_true",
            help="Consolida los duplicados (mantiene el más antiguo)",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        consolidate = options["consolidate"]

        self.stdout.write(self.style.SUCCESS("=== BÚSQUEDA DE PAÍSES DUPLICADOS ===\n"))

        # Buscar países con nombres similares (case-insensitive)
        all_countries = Country.objects.all().order_by("name")

        # Agrupar por nombre normalizado (sin espacios extras, lowercase, sin acentos)
        import unicodedata

        def normalize_name(name):
            """Normaliza el nombre removiendo acentos y convirtiendo a lowercase"""
            # Remover acentos
            nfd = unicodedata.normalize("NFD", name.strip().lower())
            # Filtrar caracteres combinables (acentos)
            normalized = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
            return normalized

        country_groups = {}
        for country in all_countries:
            normalized_name = normalize_name(country.name)
            if normalized_name not in country_groups:
                country_groups[normalized_name] = []
            country_groups[normalized_name].append(country)

        # Encontrar grupos con más de un país
        duplicates = {k: v for k, v in country_groups.items() if len(v) > 1}

        if not duplicates:
            self.stdout.write(
                self.style.SUCCESS("✓ No se encontraron países duplicados.")
            )
            return

        self.stdout.write(
            self.style.WARNING(
                f"Se encontraron {len(duplicates)} grupos de países duplicados:\n"
            )
        )

        total_to_merge = 0
        for normalized_name, countries in duplicates.items():
            self.stdout.write(
                f'\n📌 Grupo: "{normalized_name}" ({len(countries)} países)'
            )

            # Ordenar por fecha de creación (más antiguo primero)
            countries_sorted = sorted(countries, key=lambda c: c.created_at)
            keep_country = countries_sorted[0]
            merge_countries = countries_sorted[1:]

            self.stdout.write(
                f'  ✓ MANTENER: ID {keep_country.id} - "{keep_country.name}" (Código: {keep_country.code}, Activo: {keep_country.is_active}, Creado: {keep_country.created_at})'
            )

            for country in merge_countries:
                # Contar relaciones
                states_count = State.objects.filter(country=country).count()
                # Las ciudades están relacionadas con estados, no directamente con países
                cities_count = City.objects.filter(state__country=country).count()
                # Los sitios pueden estar relacionados con country, state o city
                sites_count = Site.objects.filter(
                    Q(country=country)
                    | Q(state__country=country)
                    | Q(city__state__country=country)
                ).count()
                # Los hoteles pueden estar relacionados con country, state o city
                hotels_count = Hotel.objects.filter(
                    Q(country=country)
                    | Q(state__country=country)
                    | Q(city__state__country=country)
                ).count()
                total_relations = (
                    states_count + cities_count + sites_count + hotels_count
                )

                self.stdout.write(
                    f'  ✗ ELIMINAR: ID {country.id} - "{country.name}" (Código: {country.code}, Activo: {country.is_active}, Creado: {country.created_at})'
                )
                self.stdout.write(
                    f"    └─ Relaciones: {states_count} estados, {cities_count} ciudades, {sites_count} sitios, {hotels_count} hoteles"
                )

                if total_relations > 0:
                    self.stdout.write(
                        self.style.WARNING(
                            f"    ⚠️  ADVERTENCIA: Este país tiene {total_relations} relaciones. Se moverán al país principal."
                        )
                    )
                    total_to_merge += total_relations

        if not consolidate and not dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\n⚠️  Para consolidar los duplicados, ejecuta: python manage.py cleanup_duplicate_countries --consolidate"
                )
            )
            return

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✓ DRY RUN: Se consolidarían {len(duplicates)} grupos, moviendo {total_to_merge} relaciones."
                )
            )
            return

        if consolidate:
            self.stdout.write(
                self.style.WARNING(
                    f"\n🔄 Consolidando {len(duplicates)} grupos de países duplicados...\n"
                )
            )

            merged_count = 0
            for normalized_name, countries in duplicates.items():
                countries_sorted = sorted(countries, key=lambda c: c.created_at)
                keep_country = countries_sorted[0]
                merge_countries = countries_sorted[1:]

                for country_to_merge in merge_countries:
                    # Mover estados (las ciudades se moverán automáticamente ya que dependen de estados)
                    states = State.objects.filter(country=country_to_merge)
                    states_count = states.count()

                    # Mover estados uno por uno para manejar duplicados
                    states_moved = 0
                    states_merged = 0
                    for state in states:
                        # Verificar si ya existe un estado con el mismo nombre en el país principal
                        existing_state = State.objects.filter(
                            country=keep_country, name=state.name
                        ).first()

                        if existing_state:
                            # Si existe, mover las ciudades al estado existente
                            cities_to_move = City.objects.filter(state=state)
                            cities_count_moved = cities_to_move.count()
                            cities_to_move.update(state=existing_state)

                            # Actualizar sitios y hoteles que referencian este estado
                            Site.objects.filter(state=state).update(
                                state=existing_state
                            )
                            Hotel.objects.filter(state=state).update(
                                state=existing_state
                            )

                            # Eliminar el estado duplicado
                            state.delete()
                            states_merged += 1
                            self.stdout.write(
                                f"    → Estado '{state.name}' fusionado con estado existente ({cities_count_moved} ciudades movidas)"
                            )
                        else:
                            # Si no existe, mover el estado normalmente
                            state.country = keep_country
                            state.save()
                            states_moved += 1

                    # Las ciudades ya fueron movidas en el proceso de mover estados
                    cities_count = City.objects.filter(
                        state__country=country_to_merge
                    ).count()

                    # Mover sitios (pueden tener country, state o city)
                    sites = Site.objects.filter(
                        Q(country=country_to_merge)
                        | Q(state__country=country_to_merge)
                        | Q(city__state__country=country_to_merge)
                    )
                    sites_count = sites.count()
                    # Actualizar sitios que tienen country directo
                    Site.objects.filter(country=country_to_merge).update(
                        country=keep_country
                    )
                    # Los sitios con state o city se actualizarán automáticamente cuando se muevan los estados

                    # Mover hoteles (pueden tener country, state o city)
                    hotels = Hotel.objects.filter(
                        Q(country=country_to_merge)
                        | Q(state__country=country_to_merge)
                        | Q(city__state__country=country_to_merge)
                    )
                    hotels_count = hotels.count()
                    # Actualizar hoteles que tienen country directo
                    Hotel.objects.filter(country=country_to_merge).update(
                        country=keep_country
                    )
                    # Los hoteles con state o city se actualizarán automáticamente cuando se muevan los estados

                    # Si el país a eliminar está activo pero el principal no, activar el principal
                    if country_to_merge.is_active and not keep_country.is_active:
                        keep_country.is_active = True
                        keep_country.save()

                    # Eliminar el país duplicado
                    country_to_merge.delete()
                    merged_count += 1

                    self.stdout.write(
                        f'✓ Consolidado: "{country_to_merge.name}" → "{keep_country.name}" ({states_count} estados procesados, {cities_count} ciudades, {sites_count} sitios, {hotels_count} hoteles)'
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✅ Consolidación completada: {merged_count} países eliminados."
                )
            )





