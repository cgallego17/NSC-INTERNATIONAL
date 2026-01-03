"""
Tests para verificar que PlayerUpdateForm guarda correctamente secondary_position e is_pitcher
"""
from django.contrib.auth.models import User
from django.test import TestCase

from .forms import PlayerUpdateForm
from .models import Player, Team, UserProfile


class PlayerUpdateFormTest(TestCase):
    """Tests para PlayerUpdateForm, especialmente secondary_position e is_pitcher"""

    def setUp(self):
        """Configurar datos de prueba"""
        # Crear usuario manager
        self.manager_user = User.objects.create_user(
            username="manager",
            email="manager@test.com",
            password="testpass123",
        )
        self.manager_profile = UserProfile.objects.create(
            user=self.manager_user,
            user_type="manager",
        )

        # Crear equipo
        self.team = Team.objects.create(
            name="Test Team",
            manager=self.manager_user,
        )

        # Crear usuario jugador
        self.player_user = User.objects.create_user(
            username="player1",
            email="player1@test.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )
        self.player_profile = UserProfile.objects.create(
            user=self.player_user,
            user_type="player",
            birth_date="2010-01-01",
        )

        # Crear jugador
        self.player = Player.objects.create(
            user=self.player_user,
            team=self.team,
            jersey_number=10,
            position="pitcher",
            secondary_position="",  # Inicialmente vacío
            is_pitcher=False,  # Inicialmente False
            height="5'10\"",
            weight=150,
        )

    def test_update_secondary_position_and_is_pitcher(self):
        """Test que secondary_position e is_pitcher se guardan correctamente"""
        form_data = {
            "team": self.team.pk,
            "jersey_number": 10,
            "position": "pitcher",
            "secondary_position": "catcher",  # Cambiar a catcher
            "is_pitcher": True,  # Cambiar a True
            "height": "5'10\"",
            "weight": 150,
            "age_verification_status": "pending",
            "age_verification_notes": "",
            "first_name": "John",
            "last_name": "Doe",
            "email": "player1@test.com",
        }

        form = PlayerUpdateForm(
            data=form_data,
            instance=self.player,
            user=self.manager_user,
        )

        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

        # Guardar el formulario
        saved_player = form.save()

        # Refrescar desde la base de datos
        saved_player.refresh_from_db()

        # Verificar que secondary_position se guardó correctamente
        self.assertEqual(
            saved_player.secondary_position,
            "catcher",
            "secondary_position no se guardó correctamente",
        )

        # Verificar que is_pitcher se guardó correctamente
        self.assertTrue(
            saved_player.is_pitcher,
            "is_pitcher no se guardó correctamente",
        )

    def test_update_secondary_position_empty(self):
        """Test que secondary_position puede ser vacío"""
        form_data = {
            "team": self.team.pk,
            "jersey_number": 10,
            "position": "pitcher",
            "secondary_position": "",  # Vacío
            "is_pitcher": False,
            "height": "5'10\"",
            "weight": 150,
            "age_verification_status": "pending",
            "age_verification_notes": "",
            "first_name": "John",
            "last_name": "Doe",
            "email": "player1@test.com",
        }

        form = PlayerUpdateForm(
            data=form_data,
            instance=self.player,
            user=self.manager_user,
        )

        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

        saved_player = form.save()
        saved_player.refresh_from_db()

        self.assertEqual(
            saved_player.secondary_position,
            "",
            "secondary_position vacío no se guardó correctamente",
        )

    def test_update_is_pitcher_false(self):
        """Test que is_pitcher puede ser False"""
        # Primero establecer is_pitcher a True
        self.player.is_pitcher = True
        self.player.save()

        form_data = {
            "team": self.team.pk,
            "jersey_number": 10,
            "position": "pitcher",
            "secondary_position": "catcher",
            "is_pitcher": False,  # Cambiar a False
            "height": "5'10\"",
            "weight": 150,
            "age_verification_status": "pending",
            "age_verification_notes": "",
            "first_name": "John",
            "last_name": "Doe",
            "email": "player1@test.com",
        }

        form = PlayerUpdateForm(
            data=form_data,
            instance=self.player,
            user=self.manager_user,
        )

        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

        saved_player = form.save()
        saved_player.refresh_from_db()

        self.assertFalse(
            saved_player.is_pitcher,
            "is_pitcher False no se guardó correctamente",
        )

    def test_update_both_fields_together(self):
        """Test que ambos campos se pueden actualizar juntos"""
        form_data = {
            "team": self.team.pk,
            "jersey_number": 10,
            "position": "first_base",
            "secondary_position": "third_base",
            "is_pitcher": True,
            "height": "5'10\"",
            "weight": 150,
            "age_verification_status": "pending",
            "age_verification_notes": "",
            "first_name": "John",
            "last_name": "Doe",
            "email": "player1@test.com",
        }

        form = PlayerUpdateForm(
            data=form_data,
            instance=self.player,
            user=self.manager_user,
        )

        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

        saved_player = form.save()
        saved_player.refresh_from_db()

        # Verificar ambos campos
        self.assertEqual(saved_player.secondary_position, "third_base")
        self.assertTrue(saved_player.is_pitcher)
        self.assertEqual(saved_player.position, "first_base")

    def test_checkbox_not_checked_saves_false(self):
        """Test que cuando el checkbox no está marcado, is_pitcher se guarda como False"""
        # Primero establecer is_pitcher a True
        self.player.is_pitcher = True
        self.player.save()

        # Simular que el checkbox no se envía en el POST (no está en form_data)
        form_data = {
            "team": self.team.pk,
            "jersey_number": 10,
            "position": "pitcher",
            "secondary_position": "catcher",
            # is_pitcher NO está en form_data (checkbox no marcado)
            "height": "5'10\"",
            "weight": 150,
            "age_verification_status": "pending",
            "age_verification_notes": "",
            "first_name": "John",
            "last_name": "Doe",
            "email": "player1@test.com",
        }

        form = PlayerUpdateForm(
            data=form_data,
            instance=self.player,
            user=self.manager_user,
        )

        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

        # Verificar que cleaned_data tiene is_pitcher = False
        self.assertIn("is_pitcher", form.cleaned_data)
        self.assertFalse(form.cleaned_data["is_pitcher"])

        saved_player = form.save()
        saved_player.refresh_from_db()

        self.assertFalse(
            saved_player.is_pitcher,
            "is_pitcher debería ser False cuando el checkbox no está marcado",
        )

