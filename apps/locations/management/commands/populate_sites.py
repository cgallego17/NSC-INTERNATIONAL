from django.core.management.base import BaseCommand
from apps.locations.models import Site, Country, State, City


class Command(BaseCommand):
    help = 'Populates the database with initial Site data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting sites population...'))
        
        # Get USA and some states for the sites
        try:
            usa = Country.objects.get(name__icontains='Estados Unidos')
            california = State.objects.filter(country=usa, name__icontains='California').first()
            texas = State.objects.filter(country=usa, name__icontains='Texas').first()
            florida = State.objects.filter(country=usa, name__icontains='Florida').first()
            new_york = State.objects.filter(country=usa, name__icontains='New York').first()
            
            # Get some cities
            los_angeles = City.objects.filter(state=california, name__icontains='Los Angeles').first() if california else None
            houston = City.objects.filter(state=texas, name__icontains='Houston').first() if texas else None
            miami = City.objects.filter(state=florida, name__icontains='Miami').first() if florida else None
            new_york_city = City.objects.filter(state=new_york, name__icontains='New York').first() if new_york else None
            anaheim = City.objects.filter(state=california, name__icontains='Anaheim').first() if california else None
            austin = City.objects.filter(state=texas, name__icontains='Austin').first() if texas else None
            tampa = City.objects.filter(state=florida, name__icontains='Tampa').first() if florida else None
            
        except Country.DoesNotExist:
            self.stdout.write(self.style.ERROR('USA country not found. Please run populate_complete_locations first.'))
            return

        sites_to_create = [
            {
                'site_name': 'Dodger Stadium',
                'abbreviation': 'DODG',
                'address_1': '1000 Vin Scully Ave',
                'address_2': '',
                'city': los_angeles,
                'state': california,
                'postal_code': '90012',
                'country': usa,
                'website': 'https://www.mlb.com/dodgers/ballpark',
                'additional_info': 'Home of the Los Angeles Dodgers. Features state-of-the-art facilities and seating for 56,000 fans.',
                'is_active': True
            },
            {
                'site_name': 'Minute Maid Park',
                'abbreviation': 'MMP',
                'address_1': '501 Crawford St',
                'address_2': '',
                'city': houston,
                'state': texas,
                'postal_code': '77002',
                'country': usa,
                'website': 'https://www.mlb.com/astros/ballpark',
                'additional_info': 'Home of the Houston Astros. Features a retractable roof and modern amenities.',
                'is_active': True
            },
            {
                'site_name': 'Marlins Park',
                'abbreviation': 'MP',
                'address_1': '501 Marlins Way',
                'address_2': '',
                'city': miami,
                'state': florida,
                'postal_code': '33125',
                'country': usa,
                'website': 'https://www.mlb.com/marlins/ballpark',
                'additional_info': 'Home of the Miami Marlins. Features a retractable roof and modern design.',
                'is_active': True
            },
            {
                'site_name': 'Yankee Stadium',
                'abbreviation': 'YS',
                'address_1': '1 E 161st St',
                'address_2': '',
                'city': new_york_city,
                'state': new_york,
                'postal_code': '10451',
                'country': usa,
                'website': 'https://www.mlb.com/yankees/ballpark',
                'additional_info': 'Home of the New York Yankees. Historic venue with modern amenities.',
                'is_active': True
            },
            {
                'site_name': 'Angel Stadium',
                'abbreviation': 'AS',
                'address_1': '2000 E Gene Autry Way',
                'address_2': '',
                'city': anaheim,
                'state': california,
                'postal_code': '92806',
                'country': usa,
                'website': 'https://www.mlb.com/angels/ballpark',
                'additional_info': 'Home of the Los Angeles Angels. Features the Big A and modern facilities.',
                'is_active': True
            },
            {
                'site_name': 'Community Baseball Field',
                'abbreviation': 'CBF',
                'address_1': '1234 Main St',
                'address_2': '',
                'city': austin,
                'state': texas,
                'postal_code': '78701',
                'country': usa,
                'website': '',
                'additional_info': 'Local community baseball field with basic amenities. Perfect for youth leagues and amateur games.',
                'is_active': True
            },
            {
                'site_name': 'Spring Training Complex',
                'abbreviation': 'STC',
                'address_1': '4567 Training Blvd',
                'address_2': 'Suite 100',
                'city': None,  # Phoenix no está en la base de datos
                'state': None,
                'postal_code': '85001',
                'country': usa,
                'website': 'https://example.com/spring-training',
                'additional_info': 'Professional spring training facility with multiple fields and training amenities.',
                'is_active': True
            },
            {
                'site_name': 'Legacy Field',
                'abbreviation': 'LF',
                'address_1': '789 Old Stadium Rd',
                'address_2': '',
                'city': tampa,
                'state': florida,
                'postal_code': '33601',
                'country': usa,
                'website': '',
                'additional_info': 'Historic baseball field with traditional charm. Limited modern amenities but rich in history.',
                'is_active': False
            }
        ]

        created_count = 0
        updated_count = 0

        for site_data in sites_to_create:
            site, created = Site.objects.update_or_create(
                site_name=site_data['site_name'],
                defaults=site_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created site: {site.site_name}'))
                created_count += 1
            else:
                self.stdout.write(self.style.MIGRATE_HEADING(f'Updated site: {site.site_name}'))
                updated_count += 1

        self.stdout.write(self.style.SUCCESS('\nSites population completed!'))
        self.stdout.write(self.style.SUCCESS(f'Created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'Updated: {updated_count}'))
        self.stdout.write(self.style.SUCCESS(f'Total sites: {Site.objects.count()}'))
