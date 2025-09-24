from django.core.management.base import BaseCommand
from apps.locations.models import Country, State, City, Season
from datetime import date, datetime

class Command(BaseCommand):
    help = 'Poblar completamente las tablas de ubicaciones y temporadas'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando población completa de datos...')
        
        # Crear países
        countries_data = [
            {'name': 'Estados Unidos', 'code': 'US'},
            {'name': 'México', 'code': 'MX'},
            {'name': 'Colombia', 'code': 'CO'},
            {'name': 'Canadá', 'code': 'CA'},
            {'name': 'Venezuela', 'code': 'VE'},
            {'name': 'República Dominicana', 'code': 'DO'},
            {'name': 'Cuba', 'code': 'CU'},
            {'name': 'Puerto Rico', 'code': 'PR'},
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
        
        # Crear estados de Estados Unidos
        us = Country.objects.get(code='US')
        us_states = [
            {'name': 'California', 'code': 'CA'},
            {'name': 'Texas', 'code': 'TX'},
            {'name': 'Florida', 'code': 'FL'},
            {'name': 'Nueva York', 'code': 'NY'},
            {'name': 'Illinois', 'code': 'IL'},
            {'name': 'Arizona', 'code': 'AZ'},
            {'name': 'Nevada', 'code': 'NV'},
            {'name': 'Colorado', 'code': 'CO'},
            {'name': 'Washington', 'code': 'WA'},
            {'name': 'Oregón', 'code': 'OR'},
            {'name': 'Nueva Jersey', 'code': 'NJ'},
            {'name': 'Massachusetts', 'code': 'MA'},
            {'name': 'Georgia', 'code': 'GA'},
            {'name': 'Carolina del Norte', 'code': 'NC'},
            {'name': 'Michigan', 'code': 'MI'},
            {'name': 'Ohio', 'code': 'OH'},
            {'name': 'Pennsylvania', 'code': 'PA'},
            {'name': 'Tennessee', 'code': 'TN'},
            {'name': 'Indiana', 'code': 'IN'},
            {'name': 'Missouri', 'code': 'MO'},
        ]
        
        for state_data in us_states:
            state, created = State.objects.get_or_create(
                country=us,
                code=state_data['code'],
                defaults=state_data
            )
            if created:
                self.stdout.write(f'Estado creado: {state.name}, {us.name}')
        
        # Crear estados de México
        mx = Country.objects.get(code='MX')
        mx_states = [
            {'name': 'Ciudad de México', 'code': 'CDMX'},
            {'name': 'Jalisco', 'code': 'JAL'},
            {'name': 'Nuevo León', 'code': 'NL'},
            {'name': 'Puebla', 'code': 'PUE'},
            {'name': 'Guanajuato', 'code': 'GTO'},
            {'name': 'Veracruz', 'code': 'VER'},
            {'name': 'Yucatán', 'code': 'YUC'},
            {'name': 'Quintana Roo', 'code': 'QR'},
            {'name': 'Baja California', 'code': 'BC'},
            {'name': 'Sonora', 'code': 'SON'},
        ]
        
        for state_data in mx_states:
            state, created = State.objects.get_or_create(
                country=mx,
                code=state_data['code'],
                defaults=state_data
            )
            if created:
                self.stdout.write(f'Estado creado: {state.name}, {mx.name}')
        
        # Crear estados de Colombia
        co = Country.objects.get(code='CO')
        co_states = [
            {'name': 'Bogotá D.C.', 'code': 'BOG'},
            {'name': 'Antioquia', 'code': 'ANT'},
            {'name': 'Valle del Cauca', 'code': 'VAC'},
            {'name': 'Atlántico', 'code': 'ATL'},
            {'name': 'Santander', 'code': 'SAN'},
            {'name': 'Bolívar', 'code': 'BOL'},
            {'name': 'Cundinamarca', 'code': 'CUN'},
            {'name': 'Nariño', 'code': 'NAR'},
            {'name': 'Córdoba', 'code': 'COR'},
            {'name': 'Tolima', 'code': 'TOL'},
        ]
        
        for state_data in co_states:
            state, created = State.objects.get_or_create(
                country=co,
                code=state_data['code'],
                defaults=state_data
            )
            if created:
                self.stdout.write(f'Estado creado: {state.name}, {co.name}')
        
        # Crear ciudades de Estados Unidos
        us_cities = [
            # California
            {'name': 'Los Ángeles', 'state_code': 'CA'},
            {'name': 'San Francisco', 'state_code': 'CA'},
            {'name': 'San Diego', 'state_code': 'CA'},
            {'name': 'Sacramento', 'state_code': 'CA'},
            {'name': 'Oakland', 'state_code': 'CA'},
            # Texas
            {'name': 'Houston', 'state_code': 'TX'},
            {'name': 'Dallas', 'state_code': 'TX'},
            {'name': 'Austin', 'state_code': 'TX'},
            {'name': 'San Antonio', 'state_code': 'TX'},
            {'name': 'Fort Worth', 'state_code': 'TX'},
            # Florida
            {'name': 'Miami', 'state_code': 'FL'},
            {'name': 'Tampa', 'state_code': 'FL'},
            {'name': 'Orlando', 'state_code': 'FL'},
            {'name': 'Jacksonville', 'state_code': 'FL'},
            {'name': 'Tallahassee', 'state_code': 'FL'},
            # Nueva York
            {'name': 'Nueva York', 'state_code': 'NY'},
            {'name': 'Buffalo', 'state_code': 'NY'},
            {'name': 'Rochester', 'state_code': 'NY'},
            {'name': 'Albany', 'state_code': 'NY'},
            # Illinois
            {'name': 'Chicago', 'state_code': 'IL'},
            {'name': 'Springfield', 'state_code': 'IL'},
            {'name': 'Peoria', 'state_code': 'IL'},
        ]
        
        for city_data in us_cities:
            try:
                state = State.objects.get(country=us, code=city_data['state_code'])
                city, created = City.objects.get_or_create(
                    state=state,
                    name=city_data['name']
                )
                if created:
                    self.stdout.write(f'Ciudad creada: {city.name}, {state.name}')
            except State.DoesNotExist:
                self.stdout.write(f'Estado no encontrado: {city_data["state_code"]}')
        
        # Crear ciudades de México
        mx_cities = [
            # Ciudad de México
            {'name': 'Ciudad de México', 'state_code': 'CDMX'},
            {'name': 'Iztapalapa', 'state_code': 'CDMX'},
            {'name': 'Gustavo A. Madero', 'state_code': 'CDMX'},
            {'name': 'Álvaro Obregón', 'state_code': 'CDMX'},
            # Jalisco
            {'name': 'Guadalajara', 'state_code': 'JAL'},
            {'name': 'Zapopan', 'state_code': 'JAL'},
            {'name': 'Tlaquepaque', 'state_code': 'JAL'},
            {'name': 'Tonalá', 'state_code': 'JAL'},
            # Nuevo León
            {'name': 'Monterrey', 'state_code': 'NL'},
            {'name': 'Guadalupe', 'state_code': 'NL'},
            {'name': 'San Nicolás', 'state_code': 'NL'},
            {'name': 'Apodaca', 'state_code': 'NL'},
            # Puebla
            {'name': 'Puebla', 'state_code': 'PUE'},
            {'name': 'Tehuacán', 'state_code': 'PUE'},
            {'name': 'San Pedro Cholula', 'state_code': 'PUE'},
        ]
        
        for city_data in mx_cities:
            try:
                state = State.objects.get(country=mx, code=city_data['state_code'])
                city, created = City.objects.get_or_create(
                    state=state,
                    name=city_data['name']
                )
                if created:
                    self.stdout.write(f'Ciudad creada: {city.name}, {state.name}')
            except State.DoesNotExist:
                self.stdout.write(f'Estado no encontrado: {city_data["state_code"]}')
        
        # Crear ciudades de Colombia
        co_cities = [
            # Bogotá D.C.
            {'name': 'Bogotá', 'state_code': 'BOG'},
            {'name': 'Usaquén', 'state_code': 'BOG'},
            {'name': 'Chapinero', 'state_code': 'BOG'},
            {'name': 'Santa Fe', 'state_code': 'BOG'},
            # Antioquia
            {'name': 'Medellín', 'state_code': 'ANT'},
            {'name': 'Bello', 'state_code': 'ANT'},
            {'name': 'Itagüí', 'state_code': 'ANT'},
            {'name': 'Envigado', 'state_code': 'ANT'},
            # Valle del Cauca
            {'name': 'Cali', 'state_code': 'VAC'},
            {'name': 'Palmira', 'state_code': 'VAC'},
            {'name': 'Buenaventura', 'state_code': 'VAC'},
            {'name': 'Tuluá', 'state_code': 'VAC'},
            # Atlántico
            {'name': 'Barranquilla', 'state_code': 'ATL'},
            {'name': 'Soledad', 'state_code': 'ATL'},
            {'name': 'Malambo', 'state_code': 'ATL'},
            {'name': 'Puerto Colombia', 'state_code': 'ATL'},
        ]
        
        for city_data in co_cities:
            try:
                state = State.objects.get(country=co, code=city_data['state_code'])
                city, created = City.objects.get_or_create(
                    state=state,
                    name=city_data['name']
                )
                if created:
                    self.stdout.write(f'Ciudad creada: {city.name}, {state.name}')
            except State.DoesNotExist:
                self.stdout.write(f'Estado no encontrado: {city_data["state_code"]}')
        
        # Crear temporadas de baseball
        seasons_data = [
            # Estados Unidos - MLB
            {'name': 'MLB Temporada Regular 2023', 'year': 2023, 'season_type': 'regular', 'start_date': date(2023, 3, 30), 'end_date': date(2023, 10, 1), 'status': 'completed', 'description': 'Temporada regular de Major League Baseball 2023', 'total_games': 162, 'teams_count': 30, 'league': 'Major League Baseball'},
            {'name': 'MLB Temporada Regular 2024', 'year': 2024, 'season_type': 'regular', 'start_date': date(2024, 3, 28), 'end_date': date(2024, 9, 29), 'status': 'completed', 'description': 'Temporada regular de Major League Baseball 2024', 'total_games': 162, 'teams_count': 30, 'league': 'Major League Baseball'},
            {'name': 'MLB Temporada Regular 2025', 'year': 2025, 'season_type': 'regular', 'start_date': date(2025, 3, 27), 'end_date': date(2025, 9, 28), 'status': 'upcoming', 'description': 'Temporada regular de Major League Baseball 2025', 'total_games': 162, 'teams_count': 30, 'league': 'Major League Baseball'},
            {'name': 'MLB Postemporada 2024', 'year': 2024, 'season_type': 'playoffs', 'start_date': date(2024, 10, 1), 'end_date': date(2024, 10, 31), 'status': 'completed', 'description': 'Postemporada de Major League Baseball 2024', 'total_games': 41, 'teams_count': 12, 'league': 'Major League Baseball'},
            {'name': 'MLB Postemporada 2025', 'year': 2025, 'season_type': 'playoffs', 'start_date': date(2025, 10, 1), 'end_date': date(2025, 10, 31), 'status': 'upcoming', 'description': 'Postemporada de Major League Baseball 2025', 'total_games': 41, 'teams_count': 12, 'league': 'Major League Baseball'},
            
            # México - Liga Mexicana
            {'name': 'Liga Mexicana 2023', 'year': 2023, 'season_type': 'regular', 'start_date': date(2023, 4, 7), 'end_date': date(2023, 8, 20), 'status': 'completed', 'description': 'Temporada 2023 de la Liga Mexicana de Béisbol', 'total_games': 114, 'teams_count': 18, 'league': 'Liga Mexicana de Béisbol'},
            {'name': 'Liga Mexicana 2024', 'year': 2024, 'season_type': 'regular', 'start_date': date(2024, 4, 5), 'end_date': date(2024, 8, 18), 'status': 'completed', 'description': 'Temporada 2024 de la Liga Mexicana de Béisbol', 'total_games': 114, 'teams_count': 18, 'league': 'Liga Mexicana de Béisbol'},
            {'name': 'Liga Mexicana 2025', 'year': 2025, 'season_type': 'regular', 'start_date': date(2025, 4, 4), 'end_date': date(2025, 8, 17), 'status': 'upcoming', 'description': 'Temporada 2025 de la Liga Mexicana de Béisbol', 'total_games': 114, 'teams_count': 18, 'league': 'Liga Mexicana de Béisbol'},
            
            # Colombia - Liga Profesional
            {'name': 'Liga Profesional 2023', 'year': 2023, 'season_type': 'regular', 'start_date': date(2023, 1, 20), 'end_date': date(2023, 6, 15), 'status': 'completed', 'description': 'Temporada 2023 de la Liga Profesional de Béisbol de Colombia', 'total_games': 60, 'teams_count': 8, 'league': 'Liga Profesional de Béisbol de Colombia'},
            {'name': 'Liga Profesional 2024', 'year': 2024, 'season_type': 'regular', 'start_date': date(2024, 1, 19), 'end_date': date(2024, 6, 14), 'status': 'completed', 'description': 'Temporada 2024 de la Liga Profesional de Béisbol de Colombia', 'total_games': 60, 'teams_count': 8, 'league': 'Liga Profesional de Béisbol de Colombia'},
            {'name': 'Liga Profesional 2025', 'year': 2025, 'season_type': 'regular', 'start_date': date(2025, 1, 18), 'end_date': date(2025, 6, 13), 'status': 'upcoming', 'description': 'Temporada 2025 de la Liga Profesional de Béisbol de Colombia', 'total_games': 60, 'teams_count': 8, 'league': 'Liga Profesional de Béisbol de Colombia'},
            
            # Temporadas especiales
            {'name': 'Serie Mundial 2024', 'year': 2024, 'season_type': 'world_series', 'start_date': date(2024, 10, 25), 'end_date': date(2024, 11, 2), 'status': 'completed', 'description': 'Serie Mundial de Major League Baseball 2024', 'total_games': 7, 'teams_count': 2, 'league': 'Major League Baseball'},
            {'name': 'Serie Mundial 2025', 'year': 2025, 'season_type': 'world_series', 'start_date': date(2025, 10, 24), 'end_date': date(2025, 11, 1), 'status': 'upcoming', 'description': 'Serie Mundial de Major League Baseball 2025', 'total_games': 7, 'teams_count': 2, 'league': 'Major League Baseball'},
            {'name': 'Juego de Estrellas 2024', 'year': 2024, 'season_type': 'all_star', 'start_date': date(2024, 7, 16), 'end_date': date(2024, 7, 16), 'status': 'completed', 'description': 'Juego de Estrellas de Major League Baseball 2024', 'total_games': 1, 'teams_count': 2, 'league': 'Major League Baseball'},
            {'name': 'Juego de Estrellas 2025', 'year': 2025, 'season_type': 'all_star', 'start_date': date(2025, 7, 15), 'end_date': date(2025, 7, 15), 'status': 'upcoming', 'description': 'Juego de Estrellas de Major League Baseball 2025', 'total_games': 1, 'teams_count': 2, 'league': 'Major League Baseball'},
            {'name': 'Clásico Mundial 2023', 'year': 2023, 'season_type': 'international', 'start_date': date(2023, 3, 8), 'end_date': date(2023, 3, 21), 'status': 'completed', 'description': 'Clásico Mundial de Béisbol 2023', 'total_games': 47, 'teams_count': 20, 'league': 'World Baseball Classic'},
            {'name': 'Clásico Mundial 2026', 'year': 2026, 'season_type': 'international', 'start_date': date(2026, 3, 6), 'end_date': date(2026, 3, 19), 'status': 'upcoming', 'description': 'Clásico Mundial de Béisbol 2026', 'total_games': 47, 'teams_count': 20, 'league': 'World Baseball Classic'},
        ]
        
        for season_data in seasons_data:
            season, created = Season.objects.get_or_create(
                name=season_data['name'],
                year=season_data['year'],
                defaults=season_data
            )
            if created:
                self.stdout.write(f'Temporada creada: {season.name}')
            else:
                self.stdout.write(f'Temporada ya existe: {season.name}')
        
        # Mostrar resumen final
        self.stdout.write('\n=== RESUMEN DE DATOS POBLADOS ===')
        self.stdout.write(f'Países: {Country.objects.count()}')
        self.stdout.write(f'Estados: {State.objects.count()}')
        self.stdout.write(f'Ciudades: {City.objects.count()}')
        self.stdout.write(f'Temporadas: {Season.objects.count()}')
        
        self.stdout.write('\n=== PAÍSES ===')
        for country in Country.objects.all():
            states_count = State.objects.filter(country=country).count()
            cities_count = City.objects.filter(state__country=country).count()
            self.stdout.write(f'{country.name} ({country.code}): {states_count} estados, {cities_count} ciudades')
        
        self.stdout.write('\n=== TEMPORADAS POR AÑO ===')
        for year in sorted(Season.objects.values_list('year', flat=True).distinct()):
            seasons = Season.objects.filter(year=year)
            self.stdout.write(f'{year}: {seasons.count()} temporadas')
            for season in seasons:
                self.stdout.write(f'  - {season.name} ({season.get_status_display()})')
        
        self.stdout.write('\n¡Datos poblados exitosamente!')
