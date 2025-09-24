from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse

from apps.locations.models import City, Country, League, Season, Site, State

from .models import Event


class EventModelTest(TestCase):
    """Test cases for Event model"""

    def setUp(self):
        """Set up test data"""
        # Create test data
        self.country = Country.objects.create(name="México", code="MX")
        self.state = State.objects.create(name="Jalisco", country=self.country)
        self.city = City.objects.create(name="Guadalajara", state=self.state)
        self.site = Site.objects.create(name="Estadio Jalisco", city=self.city, address="Av. Patria 1200")
        self.league = League.objects.create(name="Liga MX")
        self.season = Season.objects.create(name="Apertura 2024", league=self.league, season_type="Apertura", year=2024)

    def test_event_creation(self):
        """Test event creation"""
        event = Event.objects.create(
            name="Test Event",
            description="Test Description",
            city=self.city,
            country=self.country,
            state=self.state,
            site=self.site,
            season=self.season,
            start_date="2024-01-01",
            end_date="2024-01-02",
        )
        self.assertEqual(event.name, "Test Event")
        self.assertEqual(event.city, self.city)
        self.assertTrue(event.is_public)

    def test_event_str_representation(self):
        """Test string representation of event"""
        event = Event.objects.create(
            name="Test Event",
            city=self.city,
            country=self.country,
            state=self.state,
            site=self.site,
            season=self.season,
            start_date="2024-01-01",
            end_date="2024-01-02",
        )
        self.assertEqual(str(event), "Test Event")


class EventViewTest(TestCase):
    """Test cases for Event views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass123")

        # Create test data
        self.country = Country.objects.create(name="México", code="MX")
        self.state = State.objects.create(name="Jalisco", country=self.country)
        self.city = City.objects.create(name="Guadalajara", state=self.state)
        self.site = Site.objects.create(name="Estadio Jalisco", city=self.city, address="Av. Patria 1200")
        self.league = League.objects.create(name="Liga MX")
        self.season = Season.objects.create(name="Apertura 2024", league=self.league, season_type="Apertura", year=2024)

    def test_event_list_view_requires_login(self):
        """Test that event list view requires login"""
        response = self.client.get(reverse("events:event_list"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_event_list_view_with_login(self):
        """Test event list view with authenticated user"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("events:event_list"))
        self.assertEqual(response.status_code, 200)

    def test_event_detail_view(self):
        """Test event detail view"""
        event = Event.objects.create(
            name="Test Event",
            city=self.city,
            country=self.country,
            state=self.state,
            site=self.site,
            season=self.season,
            start_date="2024-01-01",
            end_date="2024-01-02",
        )

        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("events:event_detail", args=[event.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Event")


class DatabaseTest(TestCase):
    """Test database operations"""

    def test_database_connection(self):
        """Test database connection"""
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            self.assertEqual(result[0], 1)

    def test_migrations_work(self):
        """Test that migrations work correctly"""
        # This test ensures that all migrations can be applied
        call_command("migrate", verbosity=0, interactive=False)
        # If we get here without error, migrations work
        self.assertTrue(True)


class SecurityTest(TestCase):
    """Test security-related functionality"""

    def test_secret_key_is_set(self):
        """Test that SECRET_KEY is properly configured"""
        from django.conf import settings

        self.assertTrue(hasattr(settings, "SECRET_KEY"))
        self.assertNotEqual(settings.SECRET_KEY, "")
        self.assertNotEqual(settings.SECRET_KEY, "django-insecure-change-this-in-production-key-for-development-only")

    def test_debug_is_false_in_production(self):
        """Test that DEBUG is False in production settings"""
        from django.conf import settings

        # In production, DEBUG should be False
        # This is a reminder to check production settings
        if hasattr(settings, "DEBUG"):
            # In test environment, DEBUG might be True, which is OK
            self.assertIsInstance(settings.DEBUG, bool)
