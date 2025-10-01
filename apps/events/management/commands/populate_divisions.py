from django.core.management.base import BaseCommand

from apps.events.models import Division


class Command(BaseCommand):
    help = "Poblar la base de datos con divisiones de baseball"

    def handle(self, *args, **options):
        self.stdout.write("Iniciando población de divisiones de baseball...")

        # Crear divisiones de baseball
        divisions_data = [
            {
                "name": "T-Ball",
                "description": "División para niños de 4-6 años que están aprendiendo los fundamentos del baseball",
                "age_min": 4,
                "age_max": 6,
                "skill_level": "Principiante",
            },
            {
                "name": "Coach Pitch",
                "description": "División para niños de 7-8 años donde los entrenadores lanzan la pelota",
                "age_min": 7,
                "age_max": 8,
                "skill_level": "Principiante",
            },
            {
                "name": "Minor League",
                "description": "División para niños de 9-10 años con lanzamiento de jugadores",
                "age_min": 9,
                "age_max": 10,
                "skill_level": "Intermedio",
            },
            {
                "name": "Major League",
                "description": "División para niños de 11-12 años con reglas completas de baseball",
                "age_min": 11,
                "age_max": 12,
                "skill_level": "Intermedio",
            },
            {
                "name": "Junior League",
                "description": "División para adolescentes de 13-14 años",
                "age_min": 13,
                "age_max": 14,
                "skill_level": "Avanzado",
            },
            {
                "name": "Senior League",
                "description": "División para jóvenes de 15-16 años",
                "age_min": 15,
                "age_max": 16,
                "skill_level": "Avanzado",
            },
            {
                "name": "Big League",
                "description": "División para jóvenes de 17-18 años",
                "age_min": 17,
                "age_max": 18,
                "skill_level": "Avanzado",
            },
            {
                "name": "Adult League",
                "description": "División para adultos de 18+ años",
                "age_min": 18,
                "skill_level": "Recreativo",
            },
            {
                "name": "Women's League",
                "description": "División exclusiva para mujeres de 16+ años",
                "age_min": 16,
                "skill_level": "Recreativo",
            },
            {
                "name": "Veterans League",
                "description": "División para jugadores veteranos de 35+ años",
                "age_min": 35,
                "skill_level": "Recreativo",
            },
        ]

        for division_data in divisions_data:
            division, created = Division.objects.get_or_create(
                name=division_data["name"], defaults=division_data
            )
            if created:
                self.stdout.write(
                    f"División creada: {division.name} ({division.age_range})"
                )
            else:
                self.stdout.write(f"División ya existe: {division.name}")

        self.stdout.write(
            self.style.SUCCESS(f"Total divisiones: {Division.objects.count()}")
        )
        self.stdout.write(self.style.SUCCESS("Divisiones pobladas exitosamente!"))
