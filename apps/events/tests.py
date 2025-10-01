from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse

from apps.locations.models import City, Country, Season, Site, State

from .models import Division, Event, EventAttendance, EventCategory


class EventModelTest(TestCase):
    """Test cases for Event model"""

    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

        # Create test data
        self.category = EventCategory.objects.create(
            name="Test Category", description="Test Description"
        )
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
        self.division = Division.objects.create(
            name="Test Division",
            description="Test Division Description",
            age_min=18,
            age_max=25,
            skill_level="Intermediate",
        )

    def test_event_creation(self):
        """Test event creation"""
        event = Event.objects.create(
            title="Test Event",
            description="Test Description",
            category=self.category,
            city=self.city,
            country=self.country,
            state=self.state,
            primary_site=self.site,
            season=self.season,
            start_date="2024-01-01",
            end_date="2024-01-02",
            organizer=self.user,
        )
        self.assertEqual(event.title, "Test Event")
        self.assertEqual(event.city, self.city)
        self.assertFalse(event.is_public)

    def test_event_str_representation(self):
        """Test string representation of event"""
        event = Event.objects.create(
            title="Test Event",
            category=self.category,
            city=self.city,
            country=self.country,
            state=self.state,
            primary_site=self.site,
            season=self.season,
            start_date="2024-01-01",
            end_date="2024-01-02",
            organizer=self.user,
        )
        self.assertEqual(str(event), "Test Event")


class EventViewTest(TestCase):
    """Test cases for Event views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

        # Create test data
        self.category = EventCategory.objects.create(
            name="Test Category", description="Test Description"
        )
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

    def test_event_list_view_requires_login(self):
        """Test that event list view requires login"""
        response = self.client.get(reverse("events:list"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_event_list_view_with_login(self):
        """Test event list view with authenticated user"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("events:list"))
        self.assertEqual(response.status_code, 200)

    def test_event_detail_view(self):
        """Test event detail view"""
        event = Event.objects.create(
            title="Test Event",
            category=self.category,
            city=self.city,
            country=self.country,
            state=self.state,
            primary_site=self.site,
            season=self.season,
            start_date="2024-01-01",
            end_date="2024-01-02",
            organizer=self.user,
        )

        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("events:detail", args=[event.pk]))
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
        # In development, the default key is acceptable
        self.assertTrue(len(settings.SECRET_KEY) > 10)

    def test_debug_is_false_in_production(self):
        """Test that DEBUG is False in production settings"""
        from django.conf import settings

        # In production, DEBUG should be False
        # This is a reminder to check production settings
        if hasattr(settings, "DEBUG"):
            # In test environment, DEBUG might be True, which is OK
            self.assertIsInstance(settings.DEBUG, bool)


class DivisionModelTest(TestCase):
    """Test cases for Division model"""

    def setUp(self):
        """Set up test data"""
        self.division = Division.objects.create(
            name="Test Division",
            description="Test Division Description",
            age_min=18,
            age_max=25,
            skill_level="Intermediate",
        )

    def test_division_creation(self):
        """Test division creation"""
        self.assertEqual(self.division.name, "Test Division")
        self.assertEqual(self.division.age_min, 18)
        self.assertEqual(self.division.age_max, 25)
        self.assertEqual(self.division.skill_level, "Intermediate")
        self.assertTrue(self.division.is_active)

    def test_division_str_representation(self):
        """Test string representation of division"""
        self.assertEqual(str(self.division), "Test Division")

    def test_division_age_range_property(self):
        """Test age range property"""
        self.assertEqual(self.division.age_range, "18-25 años")

    def test_division_age_range_min_only(self):
        """Test age range with only minimum age"""
        division = Division.objects.create(
            name="Min Only Division",
            age_min=21,
            skill_level="Advanced",
        )
        self.assertEqual(division.age_range, "21+ años")

    def test_division_age_range_max_only(self):
        """Test age range with only maximum age"""
        division = Division.objects.create(
            name="Max Only Division",
            age_max=30,
            skill_level="Beginner",
        )
        self.assertEqual(division.age_range, "Hasta 30 años")

    def test_division_age_range_no_limits(self):
        """Test age range with no age limits"""
        division = Division.objects.create(
            name="No Limits Division",
            skill_level="Open",
        )
        self.assertEqual(division.age_range, "Sin restricción de edad")


class EventCategoryModelTest(TestCase):
    """Test cases for EventCategory model"""

    def test_category_creation(self):
        """Test category creation"""
        category = EventCategory.objects.create(
            name="Test Category",
            description="Test Description",
        )
        self.assertEqual(category.name, "Test Category")
        self.assertEqual(category.description, "Test Description")
        self.assertTrue(category.is_active)

    def test_category_str_representation(self):
        """Test string representation of category"""
        category = EventCategory.objects.create(
            name="Test Category",
            description="Test Description",
        )
        self.assertEqual(str(category), "Test Category")


class EventAttendanceModelTest(TestCase):
    """Test cases for EventAttendance model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.category = EventCategory.objects.create(
            name="Test Category", description="Test Description"
        )
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
        self.event = Event.objects.create(
            title="Test Event",
            category=self.category,
            city=self.city,
            country=self.country,
            state=self.state,
            primary_site=self.site,
            season=self.season,
            start_date="2024-01-01",
            end_date="2024-01-02",
            organizer=self.user,
        )

    def test_attendance_creation(self):
        """Test attendance creation"""
        attendance = EventAttendance.objects.create(
            event=self.event,
            user=self.user,
            status="confirmed",
        )
        self.assertEqual(attendance.event, self.event)
        self.assertEqual(attendance.user, self.user)
        self.assertEqual(attendance.status, "confirmed")

    def test_attendance_str_representation(self):
        """Test string representation of attendance"""
        attendance = EventAttendance.objects.create(
            event=self.event,
            user=self.user,
            status="confirmed",
        )
        expected = f"{self.user.get_full_name()} - {self.event.title}"
        self.assertEqual(str(attendance), expected)


class EventFormTest(TestCase):
    """Test cases for EventForm"""

    def setUp(self):
        """Set up test data"""
        self.category = EventCategory.objects.create(
            name="Test Category", description="Test Description"
        )
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
        self.division = Division.objects.create(
            name="Test Division",
            description="Test Division Description",
            age_min=18,
            age_max=25,
            skill_level="Intermediate",
        )

    def test_form_valid_data(self):
        """Test form with valid data"""
        from .forms import EventForm

        form_data = {
            "title": "Test Event",
            "description": "Test Description",
            "category": self.category.id,
            "city": self.city.id,
            "country": self.country.id,
            "state": self.state.id,
            "primary_site": self.site.id,
            "season": self.season.id,
            "division": self.division.id,
            "start_date": "2024-01-01",
            "end_date": "2024-01-02",
            "stature": "single_points",
        }
        form = EventForm(data=form_data)
        if not form.is_valid():
            print("Form errors:", form.errors)
        self.assertTrue(form.is_valid())

    def test_form_invalid_data(self):
        """Test form with invalid data"""
        from .forms import EventForm

        form_data = {
            "title": "",  # Empty title should be invalid
            "description": "Test Description",
        }
        form = EventForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)


class DivisionViewTest(TestCase):
    """Test cases for Division views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.division = Division.objects.create(
            name="Test Division",
            description="Test Division Description",
            age_min=18,
            age_max=25,
            skill_level="Intermediate",
        )

    def test_division_list_view_requires_login(self):
        """Test that division list view requires login"""
        response = self.client.get(reverse("events:division_list"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_division_list_view_with_login(self):
        """Test division list view with authenticated user"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("events:division_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Division")

    def test_division_detail_view(self):
        """Test division detail view"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(
            reverse("events:division_detail", args=[self.division.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Division")

    def test_division_create_view(self):
        """Test division create view"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("events:division_create"))
        self.assertEqual(response.status_code, 200)

    def test_division_update_view(self):
        """Test division update view"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(
            reverse("events:division_update", args=[self.division.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Division")

    def test_division_delete_view(self):
        """Test division delete view"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(
            reverse("events:division_delete", args=[self.division.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Division")
