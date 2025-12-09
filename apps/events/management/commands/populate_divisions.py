from django.core.management.base import BaseCommand

from apps.events.models import Division


class Command(BaseCommand):
    help = "Poblar la base de datos con divisiones de baseball del PDF"

    def handle(self, *args, **options):
        self.stdout.write("Iniciando población de divisiones de baseball...")
        self.stdout.write("=" * 70)

        # Crear divisiones de baseball según el PDF proporcionado
        divisions_data = [
            # 5U Divisiones
            {
                "name": "Baseball 5U Tball",
                "description": "División T-Ball para 5 años o menos",
                "age_max": 5,
                "skill_level": "Principiante",
            },
            {
                "name": "Baseball 5U Coach Pitch",
                "description": "División Coach Pitch para 5 años o menos",
                "age_max": 5,
                "skill_level": "Principiante",
            },
            # 6U Divisiones
            {
                "name": "Baseball 6U Tball",
                "description": "División T-Ball para 6 años o menos",
                "age_max": 6,
                "skill_level": "Principiante",
            },
            {
                "name": "Baseball 6U Coach Pitch",
                "description": "División Coach Pitch para 6 años o menos",
                "age_max": 6,
                "skill_level": "Principiante",
            },
            # 7U Divisiones
            {
                "name": "Baseball 7 & Under REC + CP",
                "description": "División Recreativa + Coach Pitch para 7 años o menos",
                "age_max": 7,
                "skill_level": "Recreativo",
            },
            {
                "name": "Baseball 7U D3 CP",
                "description": "División D3 Coach Pitch para 7 años o menos",
                "age_max": 7,
                "skill_level": "Intermedio",
            },
            {
                "name": "Baseball 7U D2 CP",
                "description": "División D2 Coach Pitch para 7 años o menos",
                "age_max": 7,
                "skill_level": "Intermedio",
            },
            {
                "name": "Baseball 7U OPEN CP",
                "description": "División OPEN Coach Pitch para 7 años o menos",
                "age_max": 7,
                "skill_level": "Avanzado",
            },
            {
                "name": "Baseball 7U D3 KP",
                "description": "División D3 Kid Pitch para 7 años o menos",
                "age_max": 7,
                "skill_level": "Intermedio",
            },
            {
                "name": "Baseball 7U D2 KP",
                "description": "División D2 Kid Pitch para 7 años o menos",
                "age_max": 7,
                "skill_level": "Intermedio",
            },
            {
                "name": "Baseball 7U OPEN KP",
                "description": "División OPEN Kid Pitch para 7 años o menos",
                "age_max": 7,
                "skill_level": "Avanzado",
            },
            # 8U Divisiones
            {
                "name": "Baseball 8U REC + CP",
                "description": "División Recreativa + Coach Pitch para 8 años o menos",
                "age_max": 8,
                "skill_level": "Recreativo",
            },
            {
                "name": "Baseball 8U D3 CP",
                "description": "División D3 Coach Pitch para 8 años o menos",
                "age_max": 8,
                "skill_level": "Intermedio",
            },
            {
                "name": "Baseball 8U D2 CP",
                "description": "División D2 Coach Pitch para 8 años o menos",
                "age_max": 8,
                "skill_level": "Intermedio",
            },
            {
                "name": "Baseball 8U D1 CP",
                "description": "División D1 Coach Pitch para 8 años o menos",
                "age_max": 8,
                "skill_level": "Avanzado",
            },
            {
                "name": "Baseball 8U OPEN CP",
                "description": "División OPEN Coach Pitch para 8 años o menos",
                "age_max": 8,
                "skill_level": "Avanzado",
            },
            {
                "name": "Baseball 8U D3 KP",
                "description": "División D3 Kid Pitch para 8 años o menos",
                "age_max": 8,
                "skill_level": "Intermedio",
            },
            {
                "name": "Baseball 8U D2 KP",
                "description": "División D2 Kid Pitch para 8 años o menos",
                "age_max": 8,
                "skill_level": "Intermedio",
            },
            {
                "name": "Baseball 8U D1 KP",
                "description": "División D1 Kid Pitch para 8 años o menos",
                "age_max": 8,
                "skill_level": "Avanzado",
            },
            {
                "name": "Baseball 8U OPEN KP",
                "description": "División OPEN Kid Pitch para 8 años o menos",
                "age_max": 8,
                "skill_level": "Avanzado",
            },
            # 9U Divisiones
            {
                "name": "Baseball 9U REC",
                "description": "División Recreativa para 9 años o menos",
                "age_max": 9,
                "skill_level": "Recreativo",
            },
            {
                "name": "Baseball 9U D3",
                "description": "División D3 para 9 años o menos",
                "age_max": 9,
                "skill_level": "Intermedio",
            },
            {
                "name": "Baseball 9U D2",
                "description": "División D2 para 9 años o menos",
                "age_max": 9,
                "skill_level": "Intermedio",
            },
            {
                "name": "Baseball 9U D1",
                "description": "División D1 para 9 años o menos",
                "age_max": 9,
                "skill_level": "Avanzado",
            },
            {
                "name": "Baseball 9U OPEN",
                "description": "División OPEN para 9 años o menos",
                "age_max": 9,
                "skill_level": "Avanzado",
            },
            # 10U Divisiones
            {
                "name": "Baseball 10U REC",
                "description": "División Recreativa para 10 años o menos",
                "age_max": 10,
                "skill_level": "Recreativo",
            },
            {
                "name": "Baseball 10U D3",
                "description": "División D3 para 10 años o menos",
                "age_max": 10,
                "skill_level": "Intermedio",
            },
            {
                "name": "Baseball 10U D2",
                "description": "División D2 para 10 años o menos",
                "age_max": 10,
                "skill_level": "Intermedio",
            },
            {
                "name": "Baseball 10U D1",
                "description": "División D1 para 10 años o menos",
                "age_max": 10,
                "skill_level": "Avanzado",
            },
            {
                "name": "Baseball 10U OPEN",
                "description": "División OPEN para 10 años o menos",
                "age_max": 10,
                "skill_level": "Avanzado",
            },
            # 11U Divisiones
            {
                "name": "Baseball 11U REC",
                "description": "División Recreativa para 11 años o menos",
                "age_max": 11,
                "skill_level": "Recreativo",
            },
            {
                "name": "Baseball 11U D3",
                "description": "División D3 para 11 años o menos",
                "age_max": 11,
                "skill_level": "Intermedio",
            },
            {
                "name": "Baseball 11U D2",
                "description": "División D2 para 11 años o menos",
                "age_max": 11,
                "skill_level": "Intermedio",
            },
            {
                "name": "Baseball 11U D1",
                "description": "División D1 para 11 años o menos",
                "age_max": 11,
                "skill_level": "Avanzado",
            },
            {
                "name": "Baseball 11U OPEN",
                "description": "División OPEN para 11 años o menos",
                "age_max": 11,
                "skill_level": "Avanzado",
            },
            # 12U Divisiones
            {
                "name": "Baseball 12U REC",
                "description": "División Recreativa para 12 años o menos",
                "age_max": 12,
                "skill_level": "Recreativo",
            },
            {
                "name": "Baseball 12U D3",
                "description": "División D3 para 12 años o menos",
                "age_max": 12,
                "skill_level": "Intermedio",
            },
            {
                "name": "Baseball 12U D2",
                "description": "División D2 para 12 años o menos",
                "age_max": 12,
                "skill_level": "Intermedio",
            },
            {
                "name": "Baseball 12U D1",
                "description": "División D1 para 12 años o menos",
                "age_max": 12,
                "skill_level": "Avanzado",
            },
            {
                "name": "Baseball 12U OPEN",
                "description": "División OPEN para 12 años o menos",
                "age_max": 12,
                "skill_level": "Avanzado",
            },
            # 13U Divisiones
            {
                "name": "Baseball 13U REC",
                "description": "División Recreativa para 13 años o menos",
                "age_max": 13,
                "skill_level": "Recreativo",
            },
            {
                "name": "Baseball 13U D3",
                "description": "División D3 para 13 años o menos",
                "age_max": 13,
                "skill_level": "Intermedio",
            },
            {
                "name": "Baseball 13U D2",
                "description": "División D2 para 13 años o menos",
                "age_max": 13,
                "skill_level": "Intermedio",
            },
            {
                "name": "Baseball 13U D1",
                "description": "División D1 para 13 años o menos",
                "age_max": 13,
                "skill_level": "Avanzado",
            },
            {
                "name": "Baseball 13U OPEN (60/90)",
                "description": "División OPEN 60/90 para 13 años o menos",
                "age_max": 13,
                "skill_level": "Avanzado",
            },
            {
                "name": "Baseball 13U OPEN",
                "description": "División OPEN para 13 años o menos",
                "age_max": 13,
                "skill_level": "Avanzado",
            },
            # 14U Divisiones
            {
                "name": "Baseball 14U REC",
                "description": "División Recreativa para 14 años o menos",
                "age_max": 14,
                "skill_level": "Recreativo",
            },
            {
                "name": "Baseball 14U D3",
                "description": "División D3 para 14 años o menos",
                "age_max": 14,
                "skill_level": "Intermedio",
            },
            {
                "name": "Baseball 14U D2",
                "description": "División D2 para 14 años o menos",
                "age_max": 14,
                "skill_level": "Intermedio",
            },
            {
                "name": "Baseball 14U D1",
                "description": "División D1 para 14 años o menos",
                "age_max": 14,
                "skill_level": "Avanzado",
            },
            {
                "name": "Baseball 14U 54X80",
                "description": "División 54X80 para 14 años o menos",
                "age_max": 14,
                "skill_level": "Avanzado",
            },
            {
                "name": "Baseball 14U OPEN",
                "description": "División OPEN para 14 años o menos",
                "age_max": 14,
                "skill_level": "Avanzado",
            },
            # 15U Divisiones
            {
                "name": "Baseball 15U D3",
                "description": "División D3 para 15 años o menos",
                "age_max": 15,
                "skill_level": "Intermedio",
            },
            {
                "name": "Baseball 15U D2",
                "description": "División D2 para 15 años o menos",
                "age_max": 15,
                "skill_level": "Intermedio",
            },
            {
                "name": "Baseball 15U D1",
                "description": "División D1 para 15 años o menos",
                "age_max": 15,
                "skill_level": "Avanzado",
            },
            {
                "name": "Baseball 15U OPEN",
                "description": "División OPEN para 15 años o menos",
                "age_max": 15,
                "skill_level": "Avanzado",
            },
            # 16U Divisiones
            {
                "name": "Baseball 16U D2",
                "description": "División D2 para 16 años o menos",
                "age_max": 16,
                "skill_level": "Intermedio",
            },
            {
                "name": "Baseball 16U D1",
                "description": "División D1 para 16 años o menos",
                "age_max": 16,
                "skill_level": "Avanzado",
            },
            {
                "name": "Baseball UNDERCLASS",
                "description": "División UNDERCLASS",
                "skill_level": "Avanzado",
            },
            {
                "name": "Baseball 16U OPEN",
                "description": "División OPEN para 16 años o menos",
                "age_max": 16,
                "skill_level": "Avanzado",
            },
            # 17U Divisiones
            {
                "name": "Baseball 17U D2",
                "description": "División D2 para 17 años o menos",
                "age_max": 17,
                "skill_level": "Intermedio",
            },
            {
                "name": "Baseball 17U D1",
                "description": "División D1 para 17 años o menos",
                "age_max": 17,
                "skill_level": "Avanzado",
            },
            {
                "name": "Baseball 17U OPEN",
                "description": "División OPEN para 17 años o menos",
                "age_max": 17,
                "skill_level": "Avanzado",
            },
            # 18U Divisiones
            {
                "name": "Baseball 18U D2",
                "description": "División D2 para 18 años o menos",
                "age_max": 18,
                "skill_level": "Intermedio",
            },
            {
                "name": "Baseball 18U D1",
                "description": "División D1 para 18 años o menos",
                "age_max": 18,
                "skill_level": "Avanzado",
            },
            {
                "name": "Baseball UPPERCLASS",
                "description": "División UPPERCLASS",
                "skill_level": "Avanzado",
            },
            {
                "name": "Baseball HS DIVISION",
                "description": "División High School",
                "skill_level": "Avanzado",
            },
            {
                "name": "Baseball 18U OPEN",
                "description": "División OPEN para 18 años o menos",
                "age_max": 18,
                "skill_level": "Avanzado",
            },
            # 19U Divisiones
            {
                "name": "Baseball 19U",
                "description": "División para 19 años o menos",
                "age_max": 19,
                "skill_level": "Avanzado",
            },
            {
                "name": "Baseball 19U OPEN",
                "description": "División OPEN para 19 años o menos",
                "age_max": 19,
                "skill_level": "Avanzado",
            },
        ]

        created_count = 0
        updated_count = 0
        existing_count = 0

        for division_data in divisions_data:
            division, created = Division.objects.get_or_create(
                name=division_data["name"], defaults=division_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ División creada: {division.name} ({division.age_range})"
                    )
                )
            else:
                # Actualizar si hay cambios
                updated = False
                for key, value in division_data.items():
                    if key != "name" and getattr(division, key) != value:
                        setattr(division, key, value)
                        updated = True

                if updated:
                    division.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"↻ División actualizada: {division.name} ({division.age_range})"
                        )
                    )
                else:
                    existing_count += 1
                    self.stdout.write(
                        f"  División ya existe: {division.name} ({division.age_range})"
                    )

        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Divisiones creadas: {created_count} | "
                f"↻ Actualizadas: {updated_count} | "
                f"  Existentes: {existing_count}"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(f"Total divisiones en BD: {Division.objects.count()}")
        )
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("✓ Proceso completado exitosamente!"))

