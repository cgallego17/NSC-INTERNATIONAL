from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import translation
from django.conf import settings

from apps.accounts.models import UserProfile
from apps.accounts.forms import UserProfileForm
from apps.core.middleware import DefaultLanguageMiddleware


class PreferredLanguageModelTest(TestCase):
    """Tests para el campo preferred_language en el modelo UserProfile"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Crear el perfil si no existe
        self.profile, created = UserProfile.objects.get_or_create(user=self.user)

    def test_preferred_language_field_exists(self):
        """Verificar que el campo preferred_language existe en el modelo"""
        self.assertTrue(hasattr(self.profile, 'preferred_language'))
        self.assertEqual(self.profile.preferred_language, 'en')  # Valor por defecto

    def test_preferred_language_default_value(self):
        """Verificar que el valor por defecto es 'en'"""
        new_user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='testpass123'
        )
        # Crear el perfil si no existe
        profile, created = UserProfile.objects.get_or_create(user=new_user)
        self.assertEqual(profile.preferred_language, 'en')

    def test_preferred_language_can_be_set(self):
        """Verificar que se puede establecer el idioma preferido"""
        self.profile.preferred_language = 'es'
        self.profile.save()
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.preferred_language, 'es')

    def test_preferred_language_choices(self):
        """Verificar que solo acepta valores válidos"""
        # Django no valida las opciones en el nivel del modelo directamente
        # pero podemos verificar que el campo tiene las opciones correctas
        field = UserProfile._meta.get_field('preferred_language')
        choices = [choice[0] for choice in field.choices]
        self.assertIn('en', choices)
        self.assertIn('es', choices)
        self.assertNotIn('fr', choices)


class PreferredLanguageFormTest(TestCase):
    """Tests para el campo preferred_language en el formulario"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Crear el perfil si no existe
        self.profile, created = UserProfile.objects.get_or_create(user=self.user)

    def test_form_includes_preferred_language_field(self):
        """Verificar que el formulario incluye el campo preferred_language"""
        form = UserProfileForm(instance=self.profile)
        self.assertIn('preferred_language', form.fields)

    def test_form_preferred_language_choices(self):
        """Verificar que el formulario tiene las opciones correctas"""
        form = UserProfileForm(instance=self.profile)
        field = form.fields['preferred_language']
        choices = [choice[0] for choice in field.choices]
        self.assertIn('en', choices)
        self.assertIn('es', choices)

    def test_form_saves_preferred_language(self):
        """Verificar que el formulario guarda el idioma preferido correctamente"""
        form_data = {
            'phone': '',
            'address': '',
            'country': '',
            'state': '',
            'city': '',
            'postal_code': '',
            'birth_date': '',
            'bio': '',
            'preferred_language': 'es',
        }
        form = UserProfileForm(data=form_data, instance=self.profile)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        form.save()
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.preferred_language, 'es')


class PreferredLanguageViewTest(TestCase):
    """Tests para la vista de actualización de perfil con idioma preferido"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Crear el perfil si no existe
        self.profile, created = UserProfile.objects.get_or_create(user=self.user)
        self.client.login(username='testuser', password='testpass123')

    def test_profile_update_view_saves_language(self):
        """Verificar que la vista guarda el idioma preferido"""
        url = reverse('accounts:profile_edit')
        response = self.client.post(url, {
            'phone': '',
            'address': '',
            'country': '',
            'state': '',
            'city': '',
            'postal_code': '',
            'birth_date': '',
            'bio': '',
            'preferred_language': 'es',
        })
        # La vista debería redirigir después de guardar
        self.assertEqual(response.status_code, 302)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.preferred_language, 'es')

    def test_profile_update_sets_session_language(self):
        """Verificar que al actualizar el idioma, se establece en la sesión"""
        url = reverse('accounts:profile_edit')
        response = self.client.post(url, {
            'phone': '',
            'address': '',
            'country': '',
            'state': '',
            'city': '',
            'postal_code': '',
            'birth_date': '',
            'bio': '',
            'preferred_language': 'es',
        })
        # Verificar que el idioma se estableció en la sesión
        language_key = getattr(translation, "LANGUAGE_SESSION_KEY", "_language")
        session_language = self.client.session.get(language_key)
        self.assertEqual(session_language, 'es')
        self.assertTrue(self.client.session.get('user_selected_language', False))


class PreferredLanguageMiddlewareTest(TestCase):
    """Tests para el middleware que usa el idioma preferido del usuario"""

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = DefaultLanguageMiddleware(lambda request: None)

    def get_response(self, request):
        """Función de respuesta simulada"""
        from django.http import HttpResponse
        return HttpResponse()

    def test_middleware_uses_user_preferred_language(self):
        """Verificar que el middleware usa el idioma preferido del usuario"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.preferred_language = 'es'
        profile.save()

        request = self.factory.get('/')
        request.user = user
        request.session = {}

        middleware = DefaultLanguageMiddleware(self.get_response)
        middleware(request)

        # Verificar que el idioma se estableció en la sesión
        language_key = getattr(translation, "LANGUAGE_SESSION_KEY", "_language")
        self.assertEqual(request.session.get(language_key), 'es')
        self.assertEqual(translation.get_language(), 'es')

    def test_middleware_uses_default_language_when_no_preference(self):
        """Verificar que el middleware usa inglés cuando no hay preferencia"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Crear el perfil (debería tener 'en' por defecto)
        profile, created = UserProfile.objects.get_or_create(user=user)

        request = self.factory.get('/')
        request.user = user
        request.session = {}

        middleware = DefaultLanguageMiddleware(self.get_response)
        middleware(request)

        # Verificar que se usa inglés por defecto
        language_key = getattr(translation, "LANGUAGE_SESSION_KEY", "_language")
        self.assertEqual(request.session.get(language_key), settings.LANGUAGE_CODE)
        self.assertEqual(translation.get_language(), settings.LANGUAGE_CODE)

    def test_middleware_respects_explicit_user_selection(self):
        """Verificar que el middleware respeta la selección explícita del usuario"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.preferred_language = 'es'
        profile.save()

        request = self.factory.get('/')
        request.user = user
        request.session = {
            '_language': 'en',  # Usuario seleccionó explícitamente inglés
            'user_selected_language': True
        }

        middleware = DefaultLanguageMiddleware(self.get_response)
        middleware(request)

        # Debería usar el idioma de la sesión (inglés) en lugar del preferido (español)
        self.assertEqual(translation.get_language(), 'en')

    def test_middleware_handles_unauthenticated_user(self):
        """Verificar que el middleware maneja usuarios no autenticados"""
        from django.contrib.auth.models import AnonymousUser

        request = self.factory.get('/')
        request.user = AnonymousUser()
        request.session = {}

        middleware = DefaultLanguageMiddleware(self.get_response)
        middleware(request)

        # Debería usar inglés por defecto
        language_key = getattr(translation, "LANGUAGE_SESSION_KEY", "_language")
        self.assertEqual(request.session.get(language_key), settings.LANGUAGE_CODE)
        self.assertEqual(translation.get_language(), settings.LANGUAGE_CODE)

    def test_middleware_handles_user_without_profile(self):
        """Verificar que el middleware maneja usuarios sin perfil"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Eliminar el perfil
        UserProfile.objects.filter(user=user).delete()

        request = self.factory.get('/')
        request.user = user
        request.session = {}

        middleware = DefaultLanguageMiddleware(self.get_response)
        middleware(request)

        # Debería usar inglés por defecto sin errores
        language_key = getattr(translation, "LANGUAGE_SESSION_KEY", "_language")
        self.assertEqual(request.session.get(language_key), settings.LANGUAGE_CODE)
        self.assertEqual(translation.get_language(), settings.LANGUAGE_CODE)


class PreferredLanguageIntegrationTest(TestCase):
    """Tests de integración para el flujo completo del idioma preferido"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_complete_flow_set_and_use_preferred_language(self):
        """Test del flujo completo: establecer idioma y verificar que se usa"""
        # 1. Establecer el idioma preferido en el perfil
        url = reverse('accounts:profile_edit')
        response = self.client.post(url, {
            'phone': '',
            'address': '',
            'country': '',
            'state': '',
            'city': '',
            'postal_code': '',
            'birth_date': '',
            'bio': '',
            'preferred_language': 'es',
        })
        self.assertEqual(response.status_code, 302)

        # 2. Verificar que se guardó en el perfil
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        profile.refresh_from_db()
        self.assertEqual(profile.preferred_language, 'es')

        # 3. Simular una nueva solicitud (como si el usuario cerrara sesión y volviera)
        # El middleware debería usar el idioma preferido del perfil
        factory = RequestFactory()
        request = factory.get('/')
        request.user = self.user
        request.session = {}

        middleware = DefaultLanguageMiddleware(lambda req: None)
        middleware(request)

        # 4. Verificar que el middleware estableció el idioma correcto
        language_key = getattr(translation, "LANGUAGE_SESSION_KEY", "_language")
        self.assertEqual(request.session.get(language_key), 'es')
        self.assertEqual(translation.get_language(), 'es')
