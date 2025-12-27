"""
Tests para validación del formulario de eventos
Verifica que los campos season, rule, divisions, event_contact y additional_hotels
validen correctamente valores activos e inactivos
"""

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from apps.locations.models import Country, Season, State, City, Rule, Hotel
from apps.events.forms import EventForm
from apps.events.models import (
    Event,
    EventCategory,
    EventType,
    Division,
    EventContact,
    GateFeeType,
)


class EventFormValidationTest(TestCase):
    """Tests para validación del formulario de eventos"""

    def setUp(self):
        """Configurar datos de prueba"""
        # Crear usuario
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )

        # Crear país, estado y ciudad
        self.country = Country.objects.create(
            name="United States", code="US", is_active=True
        )
        self.state = State.objects.create(
            name="California", country=self.country, is_active=True
        )
        self.city = City.objects.create(
            name="Los Angeles", state=self.state, is_active=True
        )

        # Crear temporadas (activa e inactiva)
        self.season_active = Season.objects.create(
            name="Baseball 2026",
            league="MLB",
            season_type="regular",
            year=2026,
            start_date="2026-01-01",
            end_date="2026-12-31",
            is_active=True,
        )
        self.season_inactive = Season.objects.create(
            name="Baseball 2025",
            league="MLB",
            season_type="regular",
            year=2025,
            start_date="2025-01-01",
            end_date="2025-12-31",
            is_active=False,
        )

        # Crear reglamentos (activo e inactivo)
        self.rule_active = Rule.objects.create(
            name="Reglamento MLB 2026", description="Reglamento activo", is_active=True
        )
        self.rule_inactive = Rule.objects.create(
            name="Reglamento MLB 2025",
            description="Reglamento inactivo",
            is_active=False,
        )

        # Crear divisiones (activas e inactivas)
        self.division_active_1 = Division.objects.create(
            name="Division 10U",
            description="10 años",
            age_min=10,
            age_max=10,
            is_active=True,
        )
        self.division_active_2 = Division.objects.create(
            name="Division 12U",
            description="12 años",
            age_min=12,
            age_max=12,
            is_active=True,
        )
        self.division_inactive = Division.objects.create(
            name="Division 8U",
            description="8 años",
            age_min=8,
            age_max=8,
            is_active=False,
        )

        # Crear contactos (activos e inactivos)
        self.contact_active = EventContact.objects.create(
            name="Contacto Activo",
            email="active@example.com",
            phone="1234567890",
            is_active=True,
        )
        self.contact_inactive = EventContact.objects.create(
            name="Contacto Inactivo",
            email="inactive@example.com",
            phone="0987654321",
            is_active=False,
        )

        # Crear hoteles (activos e inactivos)
        self.hotel_active = Hotel.objects.create(
            hotel_name="Hotel Activo",
            city=self.city,
            state=self.state,
            country=self.country,
            is_active=True,
        )
        self.hotel_inactive = Hotel.objects.create(
            hotel_name="Hotel Inactivo",
            city=self.city,
            state=self.state,
            country=self.country,
            is_active=False,
        )

        # Crear categoría de evento
        self.category = EventCategory.objects.create(
            name="Test Category", description="Test", is_active=True
        )

        # Crear tipo de evento
        self.event_type = EventType.objects.create(
            name="LIGA", description="Liga", is_active=True
        )

        # Crear gate fee type
        self.gate_fee_type = GateFeeType.objects.create(
            name="General", description="Entrada general", is_active=True
        )

    def test_season_validation_active(self):
        """Test que acepta temporada activa"""
        form_data = {
            "season": self.season_active.id,
            "title": "Test Event",
            "description": "Test Description",
            "country": self.country.id,
            "state": self.state.id,
            "city": self.city.id,
            "rule": self.rule_active.id,
            "event_type": self.event_type.id,
            "start_date": "2026-06-01",
            "end_date": "2026-06-05",
        }
        form = EventForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        self.assertEqual(form.cleaned_data["season"], self.season_active)

    def test_season_validation_inactive(self):
        """Test que rechaza temporada inactiva"""
        form_data = {
            "season": self.season_inactive.id,
            "title": "Test Event",
            "description": "Test Description",
            "country": self.country.id,
            "state": self.state.id,
            "city": self.city.id,
            "rule": self.rule_active.id,
            "event_type": self.event_type.id,
            "start_date": "2026-06-01",
            "end_date": "2026-06-05",
        }
        form = EventForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("season", form.errors)

    def test_rule_validation_active(self):
        """Test que acepta reglamento activo"""
        form_data = {
            "season": self.season_active.id,
            "title": "Test Event",
            "description": "Test Description",
            "country": self.country.id,
            "state": self.state.id,
            "city": self.city.id,
            "rule": self.rule_active.id,
            "event_type": self.event_type.id,
            "start_date": "2026-06-01",
            "end_date": "2026-06-05",
        }
        form = EventForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        self.assertEqual(form.cleaned_data["rule"], self.rule_active)

    def test_rule_validation_inactive(self):
        """Test que rechaza reglamento inactivo"""
        form_data = {
            "season": self.season_active.id,
            "title": "Test Event",
            "description": "Test Description",
            "country": self.country.id,
            "state": self.state.id,
            "city": self.city.id,
            "rule": self.rule_inactive.id,
            "event_type": self.event_type.id,
            "start_date": "2026-06-01",
            "end_date": "2026-06-05",
        }
        form = EventForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("rule", form.errors)

    def test_divisions_validation_active(self):
        """Test que acepta divisiones activas"""
        form_data = {
            "season": self.season_active.id,
            "title": "Test Event",
            "description": "Test Description",
            "country": self.country.id,
            "state": self.state.id,
            "city": self.city.id,
            "rule": self.rule_active.id,
            "event_type": self.event_type.id,
            "divisions": [self.division_active_1.id, self.division_active_2.id],
            "start_date": "2026-06-01",
            "end_date": "2026-06-05",
        }
        form = EventForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        self.assertIn(self.division_active_1, form.cleaned_data["divisions"])
        self.assertIn(self.division_active_2, form.cleaned_data["divisions"])

    def test_divisions_validation_inactive(self):
        """Test que rechaza divisiones inactivas"""
        form_data = {
            "season": self.season_active.id,
            "title": "Test Event",
            "description": "Test Description",
            "country": self.country.id,
            "state": self.state.id,
            "city": self.city.id,
            "rule": self.rule_active.id,
            "event_type": self.event_type.id,
            "divisions": [self.division_inactive.id],
            "start_date": "2026-06-01",
            "end_date": "2026-06-05",
        }
        form = EventForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("divisions", form.errors)

    def test_divisions_validation_mixed(self):
        """Test que filtra divisiones inactivas y mantiene activas"""
        form_data = {
            "season": self.season_active.id,
            "title": "Test Event",
            "description": "Test Description",
            "country": self.country.id,
            "state": self.state.id,
            "city": self.city.id,
            "rule": self.rule_active.id,
            "event_type": self.event_type.id,
            "divisions": [
                self.division_active_1.id,
                self.division_inactive.id,
                self.division_active_2.id,
            ],
            "start_date": "2026-06-01",
            "end_date": "2026-06-05",
        }
        form = EventForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("divisions", form.errors)

    def test_event_contact_validation_active(self):
        """Test que acepta contactos activos"""
        form_data = {
            "season": self.season_active.id,
            "title": "Test Event",
            "description": "Test Description",
            "country": self.country.id,
            "state": self.state.id,
            "city": self.city.id,
            "rule": self.rule_active.id,
            "event_type": self.event_type.id,
            "event_contact": [self.contact_active.id],
            "start_date": "2026-06-01",
            "end_date": "2026-06-05",
        }
        form = EventForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        self.assertIn(self.contact_active, form.cleaned_data["event_contact"])

    def test_event_contact_validation_inactive(self):
        """Test que rechaza contactos inactivos"""
        form_data = {
            "season": self.season_active.id,
            "title": "Test Event",
            "description": "Test Description",
            "country": self.country.id,
            "state": self.state.id,
            "city": self.city.id,
            "rule": self.rule_active.id,
            "event_type": self.event_type.id,
            "event_contact": [self.contact_inactive.id],
            "start_date": "2026-06-01",
            "end_date": "2026-06-05",
        }
        form = EventForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("event_contact", form.errors)

    def test_additional_hotels_validation_active(self):
        """Test que acepta hoteles adicionales activos"""
        form_data = {
            "season": self.season_active.id,
            "title": "Test Event",
            "description": "Test Description",
            "country": self.country.id,
            "state": self.state.id,
            "city": self.city.id,
            "rule": self.rule_active.id,
            "event_type": self.event_type.id,
            "additional_hotels": [self.hotel_active.id],
            "start_date": "2026-06-01",
            "end_date": "2026-06-05",
        }
        form = EventForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        self.assertIn(self.hotel_active, form.cleaned_data["additional_hotels"])

    def test_additional_hotels_validation_inactive(self):
        """Test que rechaza hoteles adicionales inactivos"""
        form_data = {
            "season": self.season_active.id,
            "title": "Test Event",
            "description": "Test Description",
            "country": self.country.id,
            "state": self.state.id,
            "city": self.city.id,
            "rule": self.rule_active.id,
            "event_type": self.event_type.id,
            "additional_hotels": [self.hotel_inactive.id],
            "start_date": "2026-06-01",
            "end_date": "2026-06-05",
        }
        form = EventForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("additional_hotels", form.errors)

    def test_form_with_all_valid_data(self):
        """Test que el formulario acepta todos los datos válidos"""
        form_data = {
            "season": self.season_active.id,
            "title": "Test Event Complete",
            "description": "Test Description Complete",
            "country": self.country.id,
            "state": self.state.id,
            "city": self.city.id,
            "rule": self.rule_active.id,
            "event_type": self.event_type.id,
            "divisions": [self.division_active_1.id, self.division_active_2.id],
            "event_contact": [self.contact_active.id],
            "additional_hotels": [self.hotel_active.id],
            "start_date": "2026-06-01",
            "end_date": "2026-06-05",
            "default_entry_fee": 100.00,
        }
        form = EventForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

        # Verificar que todos los datos se guardaron correctamente
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = self.user
            event.save()
            form.save_m2m()

            self.assertEqual(event.season, self.season_active)
            self.assertEqual(event.rule, self.rule_active)
            self.assertIn(self.division_active_1, event.divisions.all())
            self.assertIn(self.division_active_2, event.divisions.all())
            self.assertIn(self.contact_active, event.event_contact.all())
            self.assertIn(self.hotel_active, event.additional_hotels.all())













