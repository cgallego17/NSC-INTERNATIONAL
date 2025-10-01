from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

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
        site = Site.objects.create(
            site_name="Estadio Azteca",
            city=self.city,
            state=self.state,
            country=self.country,
            address_1="Calz. de Tlalpan 3465",
            postal_code="04650",
        )
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
        self.season = Season.objects.create(
            name="Apertura 2024",
            league="Liga MX",
            season_type="regular",
            year=2024,
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

    def test_season_league_field(self):
        """Test season league field"""
        season = Season.objects.create(
            name="Premier League 2024",
            league="Premier League",
            season_type="regular",
            year=2024,
            start_date="2024-01-01",
            end_date="2024-12-31",
        )
        self.assertEqual(season.league, "Premier League")

    def test_season_creation(self):
        """Test season creation"""
        season = Season.objects.create(
            name="Clausura 2024",
            league="Liga MX",
            season_type="regular",
            year=2024,
            start_date="2024-01-01",
            end_date="2024-12-31",
        )
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
        self.site = Site.objects.create(
            site_name="Estadio Jalisco",
            city=self.city,
            state=self.state,
            country=self.country,
            address_1="Av. Patria 1200",
            postal_code="44100",
        )
        self.season = Season.objects.create(
            name="Apertura 2024",
            league="Liga MX",
            season_type="regular",
            year=2024,
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

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


class LocationViewTest(TestCase):
    """Test cases for Location views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.country = Country.objects.create(name="México", code="MX")
        self.state = State.objects.create(name="Jalisco", country=self.country)
        self.city = City.objects.create(name="Guadalajara", state=self.state)
        self.site = Site.objects.create(
            site_name="Estadio Jalisco",
            city=self.city,
            state=self.state,
            country=self.country,
            address_1="Av. Patria 1200",
            postal_code="44100",
        )
        self.season = Season.objects.create(
            name="Apertura 2024",
            league="Liga MX",
            season_type="regular",
            year=2024,
            start_date="2024-01-01",
            end_date="2024-12-31",
        )
        self.rule = Rule.objects.create(
            name="Test Rule",
            description="Test Description",
            rule_type="general",
        )

    def test_country_list_view_requires_login(self):
        """Test that country list view requires login"""
        response = self.client.get(reverse("locations:country_list"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_country_list_view_with_login(self):
        """Test country list view with authenticated user"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("locations:country_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "México")

    def test_country_detail_view(self):
        """Test country detail view"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("locations:country_detail", args=[self.country.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "México")

    def test_state_list_view_requires_login(self):
        """Test that state list view requires login"""
        response = self.client.get(reverse("locations:state_list"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_state_list_view_with_login(self):
        """Test state list view with authenticated user"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("locations:state_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jalisco")

    def test_state_detail_view(self):
        """Test state detail view"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("locations:state_detail", args=[self.state.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jalisco")

    def test_city_list_view_requires_login(self):
        """Test that city list view requires login"""
        response = self.client.get(reverse("locations:city_list"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_city_list_view_with_login(self):
        """Test city list view with authenticated user"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("locations:city_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Guadalajara")

    def test_city_detail_view(self):
        """Test city detail view"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("locations:city_detail", args=[self.city.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Guadalajara")

    def test_site_list_view_requires_login(self):
        """Test that site list view requires login"""
        response = self.client.get(reverse("locations:site_list"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_site_list_view_with_login(self):
        """Test site list view with authenticated user"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("locations:site_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Estadio Jalisco")

    def test_site_detail_view(self):
        """Test site detail view"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("locations:site_detail", args=[self.site.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Estadio Jalisco")

    def test_season_list_view_requires_login(self):
        """Test that season list view requires login"""
        response = self.client.get(reverse("locations:season_list"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_season_list_view_with_login(self):
        """Test season list view with authenticated user"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("locations:season_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Apertura 2024")

    def test_season_detail_view(self):
        """Test season detail view"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("locations:season_detail", args=[self.season.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Apertura 2024")

    def test_rule_list_view_requires_login(self):
        """Test that rule list view requires login"""
        response = self.client.get(reverse("locations:rule_list"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_rule_list_view_with_login(self):
        """Test rule list view with authenticated user"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("locations:rule_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Rule")

    def test_rule_detail_view(self):
        """Test rule detail view"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("locations:rule_detail", args=[self.rule.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Rule")


class LocationAPITest(TestCase):
    """Test cases for Location API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.country = Country.objects.create(name="México", code="MX")
        self.state = State.objects.create(name="Jalisco", country=self.country)
        self.city = City.objects.create(name="Guadalajara", state=self.state)

    def test_countries_api(self):
        """Test countries API endpoint"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("locations:countries_api"))
        self.assertEqual(response.status_code, 200)
        # Check JSON response contains the country
        import json

        data = json.loads(response.content.decode())
        self.assertTrue(any(country["name"] == "México" for country in data))

    def test_states_api(self):
        """Test states API endpoint"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("locations:states_api"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jalisco")

    def test_states_api_with_country_filter(self):
        """Test states API endpoint with country filter"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("locations:states_api"), {"country": self.country.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jalisco")

    def test_cities_api(self):
        """Test cities API endpoint"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("locations:cities_api"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Guadalajara")

    def test_cities_api_with_state_filter(self):
        """Test cities API endpoint with state filter"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("locations:cities_api"), {"state": self.state.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Guadalajara")


class LocationModelPropertiesTest(TestCase):
    """Test cases for Location model properties"""

    def setUp(self):
        """Set up test data"""
        self.country = Country.objects.create(name="México", code="MX")
        self.state = State.objects.create(name="Jalisco", country=self.country)
        self.city = City.objects.create(name="Guadalajara", state=self.state)

    def test_country_states_count_property(self):
        """Test country states count property"""
        self.assertEqual(self.country.states_count, 1)

    def test_country_cities_count_property(self):
        """Test country cities count property"""
        self.assertEqual(self.country.cities_count, 1)

    def test_state_cities_count_property(self):
        """Test state cities count property"""
        self.assertEqual(self.state.cities_count, 1)

    def test_state_country_name_property(self):
        """Test state country name property"""
        self.assertEqual(self.state.country.name, "México")

    def test_city_state_name_property(self):
        """Test city state name property"""
        self.assertEqual(self.city.state.name, "Jalisco")

    def test_city_country_name_property(self):
        """Test city country name property"""
        self.assertEqual(self.city.country.name, "México")
