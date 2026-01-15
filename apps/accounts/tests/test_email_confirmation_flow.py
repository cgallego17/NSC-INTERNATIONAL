from django.contrib.auth.models import User
from django.core import mail
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import UserProfile
from apps.locations.models import City, Country, State


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class EmailConfirmationFlowTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.country = Country.objects.create(name="Mexico", code="MEX", is_active=True)
        self.state = State.objects.create(
            country=self.country, name="Yucatan", code="YUC", is_active=True
        )
        self.city = City.objects.create(state=self.state, name="Merida", is_active=True)

    def test_public_registration_creates_inactive_user_and_sends_confirmation_email(
        self,
    ):
        url = reverse("accounts:register")

        payload = {
            "email": "newuser@test.com",
            "first_name": "New",
            "last_name": "User",
            "last_name2": "",
            "user_type": "parent",
            "phone_prefix": "+52",
            "phone": "9991234567",
            "phone_secondary": "",
            "birth_date": "",
            "country": str(self.country.pk),
            "state": str(self.state.pk),
            "city": str(self.city.pk),
            "address": "",
            "address_line_2": "",
            "postal_code": "",
            "bio": "",
            "website": "",
            "social_media": "",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        }

        response = self.client.post(url, data=payload, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("accounts:email_confirmation_sent"))

        user = User.objects.get(email="newuser@test.com")
        self.assertFalse(user.is_active)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Confirm", mail.outbox[0].subject)
        self.assertIn("confirm-email", mail.outbox[0].body)

    def test_player_user_login_shows_player_message_not_email_confirmation_message(
        self,
    ):
        player_user = User.objects.create_user(
            username="player_user_test",
            email="player_login@test.com",
            password="testpass123",
            is_active=False,
        )
        UserProfile.objects.create(user=player_user, user_type="player")

        login_url = reverse("accounts:login")
        response = self.client.post(
            login_url,
            data={"username": "player_login@test.com", "password": "testpass123"},
            follow=True,
        )

        messages_text = "\n".join([m.message for m in response.context.get("messages")])
        self.assertIn("Players cannot log in", messages_text)
        self.assertNotIn("confirm your email", messages_text.lower())

    def test_creating_player_user_directly_does_not_send_confirmation_email(self):
        mail.outbox = []
        user = User.objects.create_user(
            username="player_created_direct",
            email="player_created_direct@test.com",
            password="testpass123",
            is_active=False,
        )
        UserProfile.objects.create(user=user, user_type="player")
        self.assertEqual(len(mail.outbox), 0)
