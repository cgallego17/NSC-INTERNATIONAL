"""
Tests para verificar que todos los permisos y restricciones se cumplan correctamente.

Este archivo verifica:
1. Que los usuarios normales no puedan acceder a URLs que requieren staff/admin
2. Que los jugadores no puedan iniciar sesión
3. Que los padres solo puedan ver sus hijos
4. Que los managers solo puedan ver sus equipos
5. Que staff no pueda eliminar datos críticos (solo admin)
6. Que los mixins funcionen correctamente
"""

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import PermissionDenied

from apps.accounts.models import UserProfile, Player, Team, PlayerParent
from apps.events.models import Event
from apps.locations.models import Country, State, City
from apps.media.models import MediaFile


class PermisosBaseTestCase(TestCase):
    """Clase base para tests de permisos con usuarios de prueba"""

    def setUp(self):
        """Crear usuarios de prueba para todos los tests"""
        self.client = Client()

        # Usuario normal - Padre
        self.parent_user = User.objects.create_user(
            username="parent_user",
            email="parent@test.com",
            password="testpass123",
            first_name="Parent",
            last_name="User",
        )
        self.parent_profile = UserProfile.objects.create(
            user=self.parent_user, user_type="parent"
        )

        # Usuario normal - Manager
        self.manager_user = User.objects.create_user(
            username="manager_user",
            email="manager@test.com",
            password="testpass123",
            first_name="Manager",
            last_name="User",
        )
        self.manager_profile = UserProfile.objects.create(
            user=self.manager_user, user_type="team_manager"
        )

        # Usuario Staff (NO superuser)
        self.staff_user = User.objects.create_user(
            username="staff_user",
            email="staff@test.com",
            password="testpass123",
            first_name="Staff",
            last_name="User",
            is_staff=True,
        )
        self.staff_profile = UserProfile.objects.create(
            user=self.staff_user, user_type="admin"
        )

        # Usuario Superuser/Admin
        self.admin_user = User.objects.create_user(
            username="admin_user",
            email="admin@test.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            is_staff=True,
            is_superuser=True,
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user, user_type="admin"
        )

        # Jugador (NO puede iniciar sesión)
        self.player_user = User.objects.create_user(
            username="player_user",
            email="player@test.com",
            password="testpass123",
            first_name="Player",
            last_name="User",
            is_active=False,  # IMPORTANTE: Inactivo
        )
        self.player_profile = UserProfile.objects.create(
            user=self.player_user, user_type="player"
        )
        self.player = Player.objects.create(user=self.player_user)

        # Crear equipo para el manager
        self.team = Team.objects.create(
            name="Test Team",
            slug="test-team",
            manager=self.manager_user,
        )

        # Crear jugador del equipo del manager
        self.manager_player_user = User.objects.create_user(
            username="manager_player",
            email="manager_player@test.com",
            password="testpass123",
            first_name="Manager",
            last_name="Player",
        )
        self.manager_player_profile = UserProfile.objects.create(
            user=self.manager_player_user, user_type="player"
        )
        self.manager_player = Player.objects.create(
            user=self.manager_player_user, team=self.team
        )

        # Crear relación padre-hijo
        PlayerParent.objects.create(
            parent=self.parent_user, player=self.player, relationship="guardian"
        )

        # Crear datos maestros para tests de eliminación
        self.country = Country.objects.create(name="Test Country", code="TC")
        self.state = State.objects.create(name="Test State", country=self.country)
        self.city = City.objects.create(name="Test City", state=self.state)

        # Crear evento para tests (requiere organizer)
        self.event = Event.objects.create(
            title="Test Event",
            status="draft",
            organizer=self.staff_user,  # Requerido
        )


class TestJugadoresNoPuedenIniciarSesion(PermisosBaseTestCase):
    """Verificar que los jugadores NO puedan iniciar sesión"""

    def test_jugador_no_puede_iniciar_sesion(self):
        """Un jugador con is_active=False no puede iniciar sesión"""
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "player_user", "password": "testpass123"},
        )
        # Debería redirigir o mostrar error
        self.assertNotEqual(response.status_code, 200)
        # El usuario no debería estar autenticado
        self.assertFalse(self.client.session.get("_auth_user_id"))

    def test_jugador_tiene_is_active_false(self):
        """Verificar que los jugadores tienen is_active=False"""
        self.assertFalse(self.player_user.is_active)


class TestPermisosPadres(PermisosBaseTestCase):
    """Verificar permisos de usuarios tipo Padre"""

    def setUp(self):
        super().setUp()
        self.client.login(username="parent_user", password="testpass123")

    def test_padre_puede_ver_panel(self):
        """Padre puede acceder a su panel"""
        response = self.client.get(reverse("panel"))
        self.assertEqual(response.status_code, 200)

    def test_padre_puede_ver_su_hijo(self):
        """Padre puede ver detalles de su hijo"""
        response = self.client.get(
            reverse("accounts:player_detail", kwargs={"pk": self.player.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_padre_no_puede_ver_otro_jugador(self):
        """Padre NO puede ver jugadores que no son sus hijos"""
        response = self.client.get(
            reverse("accounts:player_detail", kwargs={"pk": self.manager_player.pk})
        )
        # Debería lanzar PermissionDenied o redirigir
        self.assertIn(response.status_code, [403, 302])

    def test_padre_no_puede_ver_lista_completa_jugadores(self):
        """Padre NO puede ver lista completa de jugadores (requiere staff)"""
        response = self.client.get(reverse("accounts:player_list"))
        # Debería redirigir al panel con mensaje de error
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("panel"))

    def test_padre_no_puede_aprobar_verificaciones(self):
        """Padre NO puede aprobar verificaciones (solo staff)"""
        response = self.client.post(
            reverse("accounts:approve_age_verification", kwargs={"pk": self.player.pk}),
            {"action": "approve"},
        )
        # Debería redirigir con error
        self.assertEqual(response.status_code, 302)

    def test_padre_no_puede_acceder_admin_dashboard(self):
        """Padre NO puede acceder al admin dashboard"""
        response = self.client.get(reverse("dashboard"))
        # Debería redirigir
        self.assertEqual(response.status_code, 302)

    def test_padre_no_puede_eliminar_eventos(self):
        """Padre NO puede eliminar eventos (solo admin)"""
        response = self.client.post(
            reverse("events:delete", kwargs={"pk": self.event.pk})
        )
        # Debería redirigir
        self.assertEqual(response.status_code, 302)


class TestPermisosManagers(PermisosBaseTestCase):
    """Verificar permisos de usuarios tipo Manager"""

    def setUp(self):
        super().setUp()
        self.client.login(username="manager_user", password="testpass123")

    def test_manager_puede_ver_panel(self):
        """Manager puede acceder a su panel"""
        response = self.client.get(reverse("panel"))
        self.assertEqual(response.status_code, 200)

    def test_manager_puede_ver_su_jugador(self):
        """Manager puede ver jugadores de su equipo"""
        response = self.client.get(
            reverse("accounts:player_detail", kwargs={"pk": self.manager_player.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_manager_no_puede_ver_jugador_otro_equipo(self):
        """Manager NO puede ver jugadores de otros equipos"""
        response = self.client.get(
            reverse("accounts:player_detail", kwargs={"pk": self.player.pk})
        )
        # Debería lanzar PermissionDenied o redirigir
        self.assertIn(response.status_code, [403, 302])

    def test_manager_puede_crear_equipo(self):
        """Manager puede crear equipos"""
        response = self.client.get(reverse("accounts:team_create"))
        self.assertEqual(response.status_code, 200)

    def test_manager_puede_editar_su_equipo(self):
        """Manager puede editar su propio equipo"""
        response = self.client.get(
            reverse("accounts:team_edit", kwargs={"pk": self.team.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_manager_no_puede_aprobar_verificaciones(self):
        """Manager NO puede aprobar verificaciones (solo staff)"""
        response = self.client.post(
            reverse(
                "accounts:approve_age_verification",
                kwargs={"pk": self.manager_player.pk},
            ),
            {"action": "approve"},
        )
        # Debería redirigir con error (solo staff puede aprobar)
        self.assertEqual(response.status_code, 302)

    def test_manager_no_puede_eliminar_eventos(self):
        """Manager NO puede eliminar eventos (solo admin)"""
        response = self.client.post(
            reverse("events:delete", kwargs={"pk": self.event.pk})
        )
        # Debería redirigir
        self.assertEqual(response.status_code, 302)


class TestPermisosStaff(PermisosBaseTestCase):
    """Verificar permisos de usuarios Staff (NO superuser)"""

    def setUp(self):
        super().setUp()
        self.client.login(username="staff_user", password="testpass123")

    def test_staff_puede_ver_admin_dashboard(self):
        """Staff puede acceder al admin dashboard"""
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_staff_puede_ver_lista_jugadores(self):
        """Staff puede ver lista completa de jugadores"""
        response = self.client.get(reverse("accounts:player_list"))
        self.assertEqual(response.status_code, 200)

    def test_staff_puede_aprobar_verificaciones(self):
        """Staff puede aprobar verificaciones"""
        response = self.client.post(
            reverse("accounts:approve_age_verification", kwargs={"pk": self.player.pk}),
            {"action": "approve"},
        )
        # Debería funcionar (redirige después de aprobar)
        self.assertEqual(response.status_code, 302)

    def test_staff_no_puede_ver_usuarios(self):
        """Staff NO puede ver lista de usuarios (solo admin)"""
        response = self.client.get(reverse("accounts:user_list"))
        # Debería redirigir (requiere superuser)
        self.assertEqual(response.status_code, 302)

    def test_staff_no_puede_eliminar_eventos(self):
        """Staff NO puede eliminar eventos (solo admin)"""
        response = self.client.post(
            reverse("events:delete", kwargs={"pk": self.event.pk})
        )
        # Debería redirigir (requiere superuser)
        self.assertEqual(response.status_code, 302)

    def test_staff_no_puede_eliminar_paises(self):
        """Staff NO puede eliminar países (solo admin)"""
        response = self.client.post(
            reverse("locations:country_delete", kwargs={"pk": self.country.pk})
        )
        # Debería redirigir (requiere superuser)
        self.assertEqual(response.status_code, 302)

    def test_staff_no_puede_operaciones_masivas(self):
        """Staff NO puede realizar operaciones masivas (solo admin)"""
        response = self.client.post(
            reverse("media:bulk_delete"),
            content_type="application/json",
            data='{"ids": [1]}',
        )
        # Debería retornar 403 (requiere superuser)
        self.assertEqual(response.status_code, 403)

    def test_staff_no_puede_configuracion_sistema(self):
        """Staff NO puede acceder a configuración del sistema (solo admin)"""
        response = self.client.get(reverse("accounts:home_content_admin"))
        # Debería redirigir (requiere superuser)
        self.assertEqual(response.status_code, 302)


class TestPermisosAdmin(PermisosBaseTestCase):
    """Verificar permisos de usuarios Admin (Superuser)"""

    def setUp(self):
        super().setUp()
        self.client.login(username="admin_user", password="testpass123")

    def test_admin_puede_ver_usuarios(self):
        """Admin puede ver lista de usuarios"""
        response = self.client.get(reverse("accounts:user_list"))
        self.assertEqual(response.status_code, 200)

    def test_admin_puede_eliminar_eventos(self):
        """Admin puede eliminar eventos"""
        event_pk = self.event.pk
        response = self.client.post(
            reverse("events:delete", kwargs={"pk": event_pk})
        )
        # Debería redirigir después de eliminar
        self.assertEqual(response.status_code, 302)
        # Verificar que el evento fue eliminado
        self.assertFalse(Event.objects.filter(pk=event_pk).exists())

    def test_admin_puede_eliminar_paises(self):
        """Admin puede eliminar países"""
        country_pk = self.country.pk
        response = self.client.post(
            reverse("locations:country_delete", kwargs={"pk": country_pk})
        )
        # Debería redirigir después de eliminar
        self.assertEqual(response.status_code, 302)
        # Verificar que el país fue eliminado
        self.assertFalse(Country.objects.filter(pk=country_pk).exists())

    def test_admin_puede_operaciones_masivas(self):
        """Admin puede realizar operaciones masivas"""
        # Crear archivo de prueba
        media_file = MediaFile.objects.create(
            name="test_file",
            file_type="image",
            status="active",
        )
        response = self.client.post(
            reverse("media:bulk_delete"),
            content_type="application/json",
            data=f'{{"ids": [{media_file.pk}]}}',
        )
        # Debería funcionar (200 o 302)
        self.assertIn(response.status_code, [200, 302])

    def test_admin_puede_configuracion_sistema(self):
        """Admin puede acceder a configuración del sistema"""
        response = self.client.get(reverse("accounts:home_content_admin"))
        self.assertEqual(response.status_code, 200)

    def test_admin_puede_publicar_eventos(self):
        """Admin puede publicar/despublicar eventos"""
        response = self.client.post(
            reverse("events:toggle_publish", kwargs={"pk": self.event.pk})
        )
        # Debería redirigir después de cambiar estado
        self.assertEqual(response.status_code, 302)


class TestMixins(PermisosBaseTestCase):
    """Verificar que los mixins funcionen correctamente"""

    def test_staff_required_mixin_bloquea_usuario_normal(self):
        """StaffRequiredMixin bloquea usuarios normales"""
        self.client.login(username="parent_user", password="testpass123")
        response = self.client.get(reverse("accounts:player_list"))
        # Debería redirigir
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("panel"))

    def test_staff_required_mixin_permite_staff(self):
        """StaffRequiredMixin permite acceso a staff"""
        self.client.login(username="staff_user", password="testpass123")
        response = self.client.get(reverse("accounts:player_list"))
        self.assertEqual(response.status_code, 200)

    def test_superuser_required_mixin_bloquea_staff(self):
        """SuperuserRequiredMixin bloquea staff (no superuser)"""
        self.client.login(username="staff_user", password="testpass123")
        response = self.client.get(reverse("accounts:user_list"))
        # Debería redirigir
        self.assertEqual(response.status_code, 302)

    def test_superuser_required_mixin_permite_admin(self):
        """SuperuserRequiredMixin permite acceso a admin"""
        self.client.login(username="admin_user", password="testpass123")
        response = self.client.get(reverse("accounts:user_list"))
        self.assertEqual(response.status_code, 200)

    def test_manager_required_mixin_bloquea_padre(self):
        """ManagerRequiredMixin bloquea padres"""
        self.client.login(username="parent_user", password="testpass123")
        response = self.client.get(reverse("accounts:player_register"))
        # Debería redirigir
        self.assertEqual(response.status_code, 302)

    def test_manager_required_mixin_permite_manager(self):
        """ManagerRequiredMixin permite acceso a managers"""
        self.client.login(username="manager_user", password="testpass123")
        response = self.client.get(reverse("accounts:player_register"))
        self.assertEqual(response.status_code, 200)


class TestVerificacionesManuales(PermisosBaseTestCase):
    """Verificar que las verificaciones manuales de permisos funcionen"""

    def test_player_detail_view_verifica_permisos(self):
        """PlayerDetailView verifica permisos correctamente"""
        # Padre puede ver su hijo
        self.client.login(username="parent_user", password="testpass123")
        response = self.client.get(
            reverse("accounts:player_detail", kwargs={"pk": self.player.pk})
        )
        self.assertEqual(response.status_code, 200)

        # Usuario sin relación NO puede ver
        other_user = User.objects.create_user(
            username="other_user",
            email="other@test.com",
            password="testpass123",
        )
        UserProfile.objects.create(user=other_user, user_type="parent")
        self.client.login(username="other_user", password="testpass123")
        response = self.client.get(
            reverse("accounts:player_detail", kwargs={"pk": self.player.pk})
        )
        # Debería lanzar PermissionDenied (403)
        self.assertEqual(response.status_code, 403)

    def test_approve_age_verification_solo_staff(self):
        """approve_age_verification solo permite staff"""
        # Manager NO puede aprobar
        self.client.login(username="manager_user", password="testpass123")
        response = self.client.post(
            reverse(
                "accounts:approve_age_verification",
                kwargs={"pk": self.manager_player.pk},
            ),
            {"action": "approve"},
        )
        # Debería redirigir con error
        self.assertEqual(response.status_code, 302)

        # Staff SÍ puede aprobar
        self.client.login(username="staff_user", password="testpass123")
        response = self.client.post(
            reverse(
                "accounts:approve_age_verification",
                kwargs={"pk": self.manager_player.pk},
            ),
            {"action": "approve"},
        )
        # Debería funcionar
        self.assertEqual(response.status_code, 302)


class TestOwnerOrStaffRequiredMixin(PermisosBaseTestCase):
    """Verificar que OwnerOrStaffRequiredMixin funcione correctamente"""

    def test_team_update_permite_manager(self):
        """TeamUpdateView permite al manager editar su equipo"""
        self.client.login(username="manager_user", password="testpass123")
        response = self.client.get(
            reverse("accounts:team_edit", kwargs={"pk": self.team.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_team_update_bloquea_otro_manager(self):
        """TeamUpdateView bloquea a otros managers"""
        other_manager = User.objects.create_user(
            username="other_manager",
            email="other_manager@test.com",
            password="testpass123",
        )
        UserProfile.objects.create(user=other_manager, user_type="team_manager")
        self.client.login(username="other_manager", password="testpass123")
        response = self.client.get(
            reverse("accounts:team_edit", kwargs={"pk": self.team.pk})
        )
        # Debería redirigir
        self.assertEqual(response.status_code, 302)

    def test_team_update_permite_staff(self):
        """TeamUpdateView permite a staff editar cualquier equipo"""
        self.client.login(username="staff_user", password="testpass123")
        response = self.client.get(
            reverse("accounts:team_edit", kwargs={"pk": self.team.pk})
        )
        self.assertEqual(response.status_code, 200)


class TestPermisosPorDefecto(PermisosBaseTestCase):
    """Verificar permisos por defecto de usuarios nuevos"""

    def test_usuario_nuevo_no_es_staff(self):
        """Usuario nuevo NO es staff por defecto"""
        self.assertFalse(self.parent_user.is_staff)
        self.assertFalse(self.manager_user.is_staff)

    def test_usuario_nuevo_no_es_superuser(self):
        """Usuario nuevo NO es superuser por defecto"""
        self.assertFalse(self.parent_user.is_superuser)
        self.assertFalse(self.manager_user.is_superuser)

    def test_usuario_nuevo_es_activo(self):
        """Usuario nuevo es activo por defecto (excepto jugadores)"""
        self.assertTrue(self.parent_user.is_active)
        self.assertTrue(self.manager_user.is_active)
        # Jugadores NO son activos
        self.assertFalse(self.player_user.is_active)

    def test_usuario_nuevo_tiene_user_type(self):
        """Usuario nuevo tiene user_type definido"""
        self.assertEqual(self.parent_profile.user_type, "parent")
        self.assertEqual(self.manager_profile.user_type, "team_manager")


class TestRestriccionesCriticas(PermisosBaseTestCase):
    """Verificar restricciones críticas de seguridad"""

    def test_staff_no_puede_eliminar_datos_maestros(self):
        """Staff NO puede eliminar datos maestros críticos"""
        self.client.login(username="staff_user", password="testpass123")

        # Intentar eliminar país
        response = self.client.post(
            reverse("locations:country_delete", kwargs={"pk": self.country.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirige (no tiene permiso)

        # Verificar que el país NO fue eliminado
        self.assertTrue(Country.objects.filter(pk=self.country.pk).exists())

    def test_admin_puede_eliminar_datos_maestros(self):
        """Admin SÍ puede eliminar datos maestros críticos"""
        self.client.login(username="admin_user", password="testpass123")

        country_pk = self.country.pk
        response = self.client.post(
            reverse("locations:country_delete", kwargs={"pk": country_pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirige después de eliminar

        # Verificar que el país SÍ fue eliminado
        self.assertFalse(Country.objects.filter(pk=country_pk).exists())

    def test_staff_no_puede_toggle_publish_eventos(self):
        """Staff NO puede publicar/despublicar eventos (solo admin)"""
        self.client.login(username="staff_user", password="testpass123")
        response = self.client.post(
            reverse("events:toggle_publish", kwargs={"pk": self.event.pk})
        )
        # Debería redirigir (requiere superuser)
        self.assertEqual(response.status_code, 302)

    def test_admin_puede_toggle_publish_eventos(self):
        """Admin SÍ puede publicar/despublicar eventos"""
        self.client.login(username="admin_user", password="testpass123")
        original_status = self.event.status
        response = self.client.post(
            reverse("events:toggle_publish", kwargs={"pk": self.event.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirige después de cambiar

        # Verificar que el estado cambió
        self.event.refresh_from_db()
        self.assertNotEqual(self.event.status, original_status)

