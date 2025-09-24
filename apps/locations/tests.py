from django.test import TestCase

from .models import City, Country, Rule, Season, Site, State


class LocationModelTest(TestCase):
    """Test cases for Location models"""

    def setUp(self):
        """Set up test data"""
        self.country = Country.objects.create(name="México", code="MX")
        self.state = State.objects.create(name="Jalisco", country=self.country)
        self.city = City.objects.create(name="Guadalajara", state=self.state)

    def test_country_creation(self):
        """Test country creation"""
        country = Country.objects.create(name="Estados Unidos", code="US")
        self.assertEqual(country.name, "Estados Unidos")
        self.assertEqual(country.code, "US")

    def test_state_creation(self):
        """Test state creation"""
        state = State.objects.create(name="California", country=self.country)
        self.assertEqual(state.name, "California")
        self.assertEqual(state.country, self.country)

    def test_city_creation(self):
        """Test city creation"""
        city = City.objects.create(name="Tijuana", state=self.state)
        self.assertEqual(city.name, "Tijuana")
        self.assertEqual(city.state, self.state)

    def test_site_creation(self):
        """Test site creation"""
        site = Site.objects.create(site_name="Estadio Azteca", city=self.city, state=self.state, country=self.country, address_1="Calz. de Tlalpan 3465", postal_code="04650")
        self.assertEqual(site.site_name, "Estadio Azteca")
        self.assertEqual(site.city, self.city)

    def test_str_representations(self):
        """Test string representations of models"""
        self.assertEqual(str(self.country), "México")
        self.assertEqual(str(self.state), "Jalisco, México")
        self.assertEqual(str(self.city), "Guadalajara, Jalisco, México")


class SeasonModelTest(TestCase):
    """Test cases for Season models"""

    def setUp(self):
        """Set up test data"""
        self.season = Season.objects.create(name="Apertura 2024", league="Liga MX", season_type="regular", year=2024, start_date="2024-01-01", end_date="2024-12-31")

    def test_season_league_field(self):
        """Test season league field"""
        season = Season.objects.create(name="Premier League 2024", league="Premier League", season_type="regular", year=2024, start_date="2024-01-01", end_date="2024-12-31")
        self.assertEqual(season.league, "Premier League")

    def test_season_creation(self):
        """Test season creation"""
        season = Season.objects.create(name="Clausura 2024", league="Liga MX", season_type="regular", year=2024, start_date="2024-01-01", end_date="2024-12-31")
        self.assertEqual(season.name, "Clausura 2024")
        self.assertEqual(season.league, "Liga MX")
        self.assertEqual(season.year, 2024)

    def test_str_representations(self):
        """Test string representations of models"""
        self.assertEqual(str(self.season), "Apertura 2024 2024")


class RuleModelTest(TestCase):
    """Test cases for Rule model"""

    def test_rule_creation(self):
        """Test rule creation"""
        rule = Rule.objects.create(name="Test Rule", description="Test Description", rule_type="general")
        self.assertEqual(rule.name, "Test Rule")
        self.assertEqual(rule.description, "Test Description")
        self.assertEqual(rule.rule_type, "general")

    def test_rule_str_representation(self):
        """Test string representation of rule"""
        rule = Rule.objects.create(name="Test Rule", description="Test Description", rule_type="general")
        self.assertEqual(str(rule), "Test Rule")


class ModelRelationshipsTest(TestCase):
    """Test model relationships"""

    def setUp(self):
        """Set up test data"""
        self.country = Country.objects.create(name="México", code="MX")
        self.state = State.objects.create(name="Jalisco", country=self.country)
        self.city = City.objects.create(name="Guadalajara", state=self.state)
        self.site = Site.objects.create(site_name="Estadio Jalisco", city=self.city, state=self.state, country=self.country, address_1="Av. Patria 1200", postal_code="44100")
        self.season = Season.objects.create(name="Apertura 2024", league="Liga MX", season_type="regular", year=2024, start_date="2024-01-01", end_date="2024-12-31")

    def test_country_state_relationship(self):
        """Test country-state relationship"""
        self.assertEqual(self.state.country, self.country)
        self.assertIn(self.state, self.country.states.all())

    def test_state_city_relationship(self):
        """Test state-city relationship"""
        self.assertEqual(self.city.state, self.state)
        self.assertIn(self.city, self.state.cities.all())

    def test_city_site_relationship(self):
        """Test city-site relationship"""
        self.assertEqual(self.site.city, self.city)
        self.assertIn(self.site, self.city.sites.all())

    def test_season_league_field(self):
        """Test season league field"""
        self.assertEqual(self.season.league, "Liga MX")
