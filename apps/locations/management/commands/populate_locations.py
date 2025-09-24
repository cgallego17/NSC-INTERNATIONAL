from django.core.management.base import BaseCommand
from apps.locations.models import Country, State, City, Season
from datetime import date


class Command(BaseCommand):
    help = 'Poblar la base de datos con países, estados, ciudades y temporadas de baseball'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando población de datos...')
        
        # Crear países
        self.create_countries()
        
        # Crear estados
        self.create_states()
        
        # Crear ciudades
        self.create_cities()
        
        # Crear temporadas
        self.create_seasons()
        
        self.stdout.write(
            self.style.SUCCESS('Datos poblados exitosamente!')
        )

    def create_countries(self):
        countries_data = [
            {'name': 'Estados Unidos', 'code': 'US'},
            {'name': 'México', 'code': 'MX'},
            {'name': 'Colombia', 'code': 'CO'},
        ]
        
        for country_data in countries_data:
            country, created = Country.objects.get_or_create(
                code=country_data['code'],
                defaults=country_data
            )
            if created:
                self.stdout.write(f'País creado: {country.name}')
            else:
                self.stdout.write(f'País ya existe: {country.name}')

    def create_states(self):
        # Estados de Estados Unidos
        us_states = [
            {'name': 'California', 'code': 'CA'},
            {'name': 'Texas', 'code': 'TX'},
            {'name': 'Florida', 'code': 'FL'},
            {'name': 'New York', 'code': 'NY'},
            {'name': 'Illinois', 'code': 'IL'},
            {'name': 'Arizona', 'code': 'AZ'},
            {'name': 'Georgia', 'code': 'GA'},
            {'name': 'North Carolina', 'code': 'NC'},
            {'name': 'Michigan', 'code': 'MI'},
            {'name': 'Ohio', 'code': 'OH'},
        ]
        
        # Estados de México
        mx_states = [
            {'name': 'Baja California', 'code': 'BC'},
            {'name': 'Sonora', 'code': 'SON'},
            {'name': 'Chihuahua', 'code': 'CHIH'},
            {'name': 'Coahuila', 'code': 'COAH'},
            {'name': 'Nuevo León', 'code': 'NL'},
            {'name': 'Tamaulipas', 'code': 'TAM'},
            {'name': 'Sinaloa', 'code': 'SIN'},
            {'name': 'Jalisco', 'code': 'JAL'},
            {'name': 'Yucatán', 'code': 'YUC'},
            {'name': 'Quintana Roo', 'code': 'QR'},
        ]
        
        # Departamentos de Colombia
        co_states = [
            {'name': 'Antioquia', 'code': 'ANT'},
            {'name': 'Valle del Cauca', 'code': 'VAC'},
            {'name': 'Cundinamarca', 'code': 'CUN'},
            {'name': 'Atlántico', 'code': 'ATL'},
            {'name': 'Santander', 'code': 'SAN'},
            {'name': 'Bolívar', 'code': 'BOL'},
            {'name': 'Córdoba', 'code': 'COR'},
            {'name': 'Nariño', 'code': 'NAR'},
            {'name': 'Cauca', 'code': 'CAU'},
            {'name': 'Tolima', 'code': 'TOL'},
        ]
        
        us = Country.objects.get(code='US')
        mx = Country.objects.get(code='MX')
        co = Country.objects.get(code='CO')
        
        for state_data in us_states:
            state, created = State.objects.get_or_create(
                country=us,
                name=state_data['name'],
                defaults={'code': state_data['code']}
            )
            if created:
                self.stdout.write(f'Estado creado: {state.name}, {state.country.name}')
        
        for state_data in mx_states:
            state, created = State.objects.get_or_create(
                country=mx,
                name=state_data['name'],
                defaults={'code': state_data['code']}
            )
            if created:
                self.stdout.write(f'Estado creado: {state.name}, {state.country.name}')
        
        for state_data in co_states:
            state, created = State.objects.get_or_create(
                country=co,
                name=state_data['name'],
                defaults={'code': state_data['code']}
            )
            if created:
                self.stdout.write(f'Estado creado: {state.name}, {state.country.name}')

    def create_cities(self):
        # Ciudades de Estados Unidos
        us_cities = {
            'California': ['Los Angeles', 'San Francisco', 'San Diego', 'Sacramento', 'Oakland'],
            'Texas': ['Houston', 'Dallas', 'Austin', 'San Antonio', 'Fort Worth'],
            'Florida': ['Miami', 'Tampa', 'Orlando', 'Jacksonville', 'Tallahassee'],
            'New York': ['New York City', 'Buffalo', 'Rochester', 'Syracuse', 'Albany'],
            'Illinois': ['Chicago', 'Aurora', 'Rockford', 'Joliet', 'Naperville'],
        }
        
        # Ciudades de México
        mx_cities = {
            'Baja California': ['Tijuana', 'Mexicali', 'Ensenada', 'Rosarito', 'Tecate'],
            'Sonora': ['Hermosillo', 'Ciudad Obregón', 'Nogales', 'Guaymas', 'Navojoa'],
            'Chihuahua': ['Chihuahua', 'Ciudad Juárez', 'Delicias', 'Parral', 'Cuauhtémoc'],
            'Coahuila': ['Saltillo', 'Torreón', 'Monclova', 'Piedras Negras', 'Acuña'],
            'Nuevo León': ['Monterrey', 'Guadalupe', 'Apodaca', 'San Nicolás', 'Santa Catarina'],
        }
        
        # Ciudades de Colombia
        co_cities = {
            'Antioquia': ['Medellín', 'Bello', 'Itagüí', 'Envigado', 'Apartadó'],
            'Valle del Cauca': ['Cali', 'Palmira', 'Buenaventura', 'Tuluá', 'Cartago'],
            'Cundinamarca': ['Bogotá', 'Soacha', 'Zipaquirá', 'Chía', 'Girardot'],
            'Atlántico': ['Barranquilla', 'Soledad', 'Malambo', 'Puerto Colombia', 'Galapa'],
            'Santander': ['Bucaramanga', 'Floridablanca', 'Girón', 'Piedecuesta', 'San Gil'],
        }
        
        # Crear ciudades de Estados Unidos
        for state_name, cities in us_cities.items():
            try:
                state = State.objects.get(country__code='US', name=state_name)
                for city_name in cities:
                    city, created = City.objects.get_or_create(
                        state=state,
                        name=city_name
                    )
                    if created:
                        self.stdout.write(f'Ciudad creada: {city.name}, {state.name}')
            except State.DoesNotExist:
                self.stdout.write(f'Estado no encontrado: {state_name}')
        
        # Crear ciudades de México
        for state_name, cities in mx_cities.items():
            try:
                state = State.objects.get(country__code='MX', name=state_name)
                for city_name in cities:
                    city, created = City.objects.get_or_create(
                        state=state,
                        name=city_name
                    )
                    if created:
                        self.stdout.write(f'Ciudad creada: {city.name}, {state.name}')
            except State.DoesNotExist:
                self.stdout.write(f'Estado no encontrado: {state_name}')
        
        # Crear ciudades de Colombia
        for state_name, cities in co_cities.items():
            try:
                state = State.objects.get(country__code='CO', name=state_name)
                for city_name in cities:
                    city, created = City.objects.get_or_create(
                        state=state,
                        name=city_name
                    )
                    if created:
                        self.stdout.write(f'Ciudad creada: {city.name}, {state.name}')
            except State.DoesNotExist:
                self.stdout.write(f'Estado no encontrado: {state_name}')

    def create_seasons(self):
        seasons_data = [
            {
                'name': 'Temporada Regular 2024',
                'year': 2024,
                'start_date': date(2024, 3, 28),
                'end_date': date(2024, 9, 29),
                'status': 'completed',
                'description': 'Temporada regular de Major League Baseball 2024'
            },
            {
                'name': 'Temporada Regular 2025',
                'year': 2025,
                'start_date': date(2025, 3, 27),
                'end_date': date(2025, 9, 28),
                'status': 'upcoming',
                'description': 'Temporada regular de Major League Baseball 2025'
            },
            {
                'name': 'Liga Mexicana 2024',
                'year': 2024,
                'start_date': date(2024, 4, 4),
                'end_date': date(2024, 8, 25),
                'status': 'completed',
                'description': 'Temporada 2024 de la Liga Mexicana de Béisbol'
            },
            {
                'name': 'Liga Mexicana 2025',
                'year': 2025,
                'start_date': date(2025, 4, 3),
                'end_date': date(2025, 8, 24),
                'status': 'upcoming',
                'description': 'Temporada 2025 de la Liga Mexicana de Béisbol'
            },
            {
                'name': 'Liga Profesional 2024',
                'year': 2024,
                'start_date': date(2024, 1, 19),
                'end_date': date(2024, 10, 20),
                'status': 'completed',
                'description': 'Temporada 2024 de la Liga Profesional de Béisbol de Colombia'
            },
            {
                'name': 'Liga Profesional 2025',
                'year': 2025,
                'start_date': date(2025, 1, 17),
                'end_date': date(2025, 10, 19),
                'status': 'upcoming',
                'description': 'Temporada 2025 de la Liga Profesional de Béisbol de Colombia'
            },
        ]
        
        for season_data in seasons_data:
            season, created = Season.objects.get_or_create(
                name=season_data['name'],
                year=season_data['year'],
                defaults=season_data
            )
            if created:
                self.stdout.write(f'Temporada creada: {season.name} {season.year}')
            else:
                self.stdout.write(f'Temporada ya existe: {season.name} {season.year}')

