from django.test import TestCase
from django.contrib.auth.models import User
from .models import Country, State, City, Site, Season, League, Rule


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
        site = Site.objects.create(
            name="Estadio Azteca",
            city=self.city,
            address="Calz. de Tlalpan 3465"
        )
        self.assertEqual(site.name, "Estadio Azteca")
        self.assertEqual(site.city, self.city)
        
    def test_str_representations(self):
        """Test string representations of models"""
        self.assertEqual(str(self.country), "México")
        self.assertEqual(str(self.state), "Jalisco")
        self.assertEqual(str(self.city), "Guadalajara")


class SeasonModelTest(TestCase):
    """Test cases for Season models"""
    
    def setUp(self):
        """Set up test data"""
        self.league = League.objects.create(name="Liga MX")
        self.season = Season.objects.create(
            name="Apertura 2024",
            league=self.league,
            season_type="Apertura",
            year=2024
        )
        
    def test_league_creation(self):
        """Test league creation"""
        league = League.objects.create(name="Premier League")
        self.assertEqual(league.name, "Premier League")
        
    def test_season_creation(self):
        """Test season creation"""
        season = Season.objects.create(
            name="Clausura 2024",
            league=self.league,
            season_type="Clausura",
            year=2024
        )
        self.assertEqual(season.name, "Clausura 2024")
        self.assertEqual(season.league, self.league)
        self.assertEqual(season.year, 2024)
        
    def test_str_representations(self):
        """Test string representations of models"""
        self.assertEqual(str(self.league), "Liga MX")
        self.assertEqual(str(self.season), "Apertura 2024")


class RuleModelTest(TestCase):
    """Test cases for Rule model"""
    
    def test_rule_creation(self):
        """Test rule creation"""
        rule = Rule.objects.create(
            name="Test Rule",
            description="Test Description",
            rule_type="general"
        )
        self.assertEqual(rule.name, "Test Rule")
        self.assertEqual(rule.description, "Test Description")
        self.assertEqual(rule.rule_type, "general")
        
    def test_rule_str_representation(self):
        """Test string representation of rule"""
        rule = Rule.objects.create(
            name="Test Rule",
            description="Test Description",
            rule_type="general"
        )
        self.assertEqual(str(rule), "Test Rule")


class ModelRelationshipsTest(TestCase):
    """Test model relationships"""
    
    def setUp(self):
        """Set up test data"""
        self.country = Country.objects.create(name="México", code="MX")
        self.state = State.objects.create(name="Jalisco", country=self.country)
        self.city = City.objects.create(name="Guadalajara", state=self.state)
        self.site = Site.objects.create(
            name="Estadio Jalisco",
            city=self.city,
            address="Av. Patria 1200"
        )
        self.league = League.objects.create(name="Liga MX")
        self.season = Season.objects.create(
            name="Apertura 2024",
            league=self.league,
            season_type="Apertura",
            year=2024
        )
        
    def test_country_state_relationship(self):
        """Test country-state relationship"""
        self.assertEqual(self.state.country, self.country)
        self.assertIn(self.state, self.country.state_set.all())
        
    def test_state_city_relationship(self):
        """Test state-city relationship"""
        self.assertEqual(self.city.state, self.state)
        self.assertIn(self.city, self.state.city_set.all())
        
    def test_city_site_relationship(self):
        """Test city-site relationship"""
        self.assertEqual(self.site.city, self.city)
        self.assertIn(self.site, self.city.site_set.all())
        
    def test_league_season_relationship(self):
        """Test league-season relationship"""
        self.assertEqual(self.season.league, self.league)
        self.assertIn(self.season, self.league.season_set.all())
