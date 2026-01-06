"""
Tests para el flujo de checkout de Stripe para eventos
"""

from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, Mock

from django.contrib.auth.models import User
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Player, PlayerParent, StripeEventCheckout, UserProfile
from apps.events.models import Event, EventAttendance, EventCategory
from apps.locations.models import (
    City,
    Country,
    Hotel,
    HotelReservation,
    HotelRoom,
    State,
)


class StripeCheckoutTestCase(TestCase):
    """Tests para el flujo completo de checkout de Stripe"""

    def setUp(self):
        """Configurar datos de prueba"""
        # Crear usuario padre
        self.parent_user = User.objects.create_user(
            username="parentuser",
            email="parent@test.com",
            password="testpass123",
        )
        self.parent_profile = UserProfile.objects.create(
            user=self.parent_user, user_type="parent"
        )

        # Crear jugador hijo
        self.player_user = User.objects.create_user(
            username="playeruser",
            email="player@test.com",
            password="testpass123",
            first_name="Test",
            last_name="Player",
        )
        self.player_profile = UserProfile.objects.create(
            user=self.player_user, user_type="player", birth_date=date(2010, 1, 1)
        )
        self.player = Player.objects.create(user=self.player_user)

        # Relacionar padre e hijo
        PlayerParent.objects.create(parent=self.parent_user, player=self.player)

        # Crear categoría de evento
        self.category = EventCategory.objects.create(
            name="Test Category", description="Test Description"
        )

        # Crear ubicación
        self.country = Country.objects.create(name="México", code="MX")
        self.state = State.objects.create(name="Jalisco", country=self.country)
        self.city = City.objects.create(name="Guadalajara", state=self.state)

        # Crear evento
        self.event = Event.objects.create(
            title="Test Event",
            category=self.category,
            city=self.city,
            state=self.state,
            country=self.country,
            organizer=self.parent_user,
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=35),
            default_entry_fee=Decimal("100.00"),
            payment_deadline=date.today() + timedelta(days=90),
        )

        # Crear hotel y habitación
        self.hotel = Hotel.objects.create(
            hotel_name="Test Hotel",
            city=self.city,
            state=self.state,
            country=self.country,
            address="Test Address",
        )
        self.room = HotelRoom.objects.create(
            hotel=self.hotel,
            name="Test Room",
            room_type="double",
            price_per_night=Decimal("50.00"),
            capacity=2,
            price_includes_guests=2,
        )
        self.event.hotel = self.hotel
        self.event.save()

        # Cliente de prueba
        self.client = Client()
        self.client.login(username="parentuser", password="testpass123")

    def test_create_checkout_session_plan_mode(self):
        """Test crear sesión de checkout en modo plan"""
        # Mock de Stripe Session
        mock_session = Mock()
        mock_session.id = "cs_test_123"
        mock_session.url = "https://checkout.stripe.com/test"

        # Mockear stripe directamente
        import sys

        mock_stripe = MagicMock()
        mock_stripe.checkout.Session.create.return_value = mock_session
        sys.modules["stripe"] = mock_stripe

        try:
            with self.settings(STRIPE_SECRET_KEY="sk_test_123"):
                url = reverse(
                    "accounts:create_stripe_event_checkout_session",
                    args=[self.event.pk],
                )
                response = self.client.post(
                    url,
                    {
                        "players": [str(self.player.pk)],
                        "payment_mode": "plan",
                    },
                )

                # Verificar respuesta
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertTrue(data["success"])
                self.assertIn("checkout_url", data)
                self.assertEqual(
                    data["checkout_url"], "https://checkout.stripe.com/test"
                )

                # Verificar que se creó el checkout
                checkout = StripeEventCheckout.objects.get(
                    stripe_session_id="cs_test_123"
                )
                self.assertEqual(checkout.user, self.parent_user)
                self.assertEqual(checkout.event, self.event)
                self.assertEqual(checkout.payment_mode, "plan")
                self.assertEqual(checkout.status, "created")
                self.assertIn(self.player.pk, checkout.player_ids)
        finally:
            # Limpiar el mock
            if "stripe" in sys.modules:
                del sys.modules["stripe"]

    def test_create_checkout_session_pay_now_mode(self):
        """Test crear sesión de checkout en modo pay now"""
        # Mock de Stripe Session
        mock_session = Mock()
        mock_session.id = "cs_test_456"
        mock_session.url = "https://checkout.stripe.com/test"

        # Agregar hotel al carrito
        session = self.client.session
        session["hotel_cart"] = {
            "room_1": {
                "type": "room",
                "room_id": self.room.pk,
                "check_in": "2024-06-01",
                "check_out": "2024-06-05",
                "guests": 2,
                "services": [],
            }
        }
        session.save()

        # Mockear stripe directamente
        import sys

        mock_stripe = MagicMock()
        mock_stripe.checkout.Session.create.return_value = mock_session
        sys.modules["stripe"] = mock_stripe

        try:
            with self.settings(STRIPE_SECRET_KEY="sk_test_123"):
                url = reverse(
                    "accounts:create_stripe_event_checkout_session",
                    args=[self.event.pk],
                )
                response = self.client.post(
                    url,
                    {
                        "players": [str(self.player.pk)],
                        "payment_mode": "now",
                    },
                )

                # Verificar respuesta
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertTrue(data["success"])

                # Verificar checkout
                checkout = StripeEventCheckout.objects.get(
                    stripe_session_id="cs_test_456"
                )
                self.assertEqual(checkout.payment_mode, "now")
                self.assertEqual(
                    checkout.discount_percent, 5
                )  # Descuento del 5% con hotel
        finally:
            # Limpiar el mock
            if "stripe" in sys.modules:
                del sys.modules["stripe"]

    def test_stripe_checkout_success_creates_reservations(self):
        """Test que al confirmar el pago se crean las reservas"""
        # Crear checkout
        checkout = StripeEventCheckout.objects.create(
            user=self.parent_user,
            event=self.event,
            stripe_session_id="cs_test_789",
            payment_mode="now",
            status="created",
            amount_total=Decimal("150.00"),
            player_ids=[self.player.pk],
            hotel_cart_snapshot={
                "room_1": {
                    "type": "room",
                    "room_id": self.room.pk,
                    "check_in": "2024-06-01",
                    "check_out": "2024-06-05",
                    "guests": 2,
                    "services": [],
                }
            },
        )

        # Mock de sesión de Stripe
        mock_session = Mock()
        mock_session.payment_status = "paid"
        mock_session.subscription = None

        # Mockear stripe directamente
        import sys

        mock_stripe = MagicMock()
        mock_stripe.checkout.Session.retrieve.return_value = mock_session
        sys.modules["stripe"] = mock_stripe

        try:
            with self.settings(STRIPE_SECRET_KEY="sk_test_123"):
                # Usar el cliente de Django que tiene los middlewares configurados
                self.client.get(
                    reverse(
                        "accounts:stripe_event_checkout_success", args=[self.event.pk]
                    ),
                    {"session_id": "cs_test_789"},
                )

                # Verificar que se creó la reserva
                reservations = HotelReservation.objects.filter(user=self.parent_user)
                self.assertEqual(reservations.count(), 1)
                reservation = reservations.first()
                self.assertEqual(reservation.room, self.room)
                self.assertEqual(reservation.status, "confirmed")
                self.assertEqual(reservation.number_of_guests, 2)

                # Verificar que se creó la asistencia al evento
                attendance = EventAttendance.objects.get(
                    event=self.event, user=self.player_user
                )
                self.assertEqual(attendance.status, "confirmed")

                # Verificar que el checkout está marcado como pagado
                checkout.refresh_from_db()
                self.assertEqual(checkout.status, "paid")
                self.assertIsNotNone(checkout.paid_at)
        finally:
            # Limpiar el mock
            if "stripe" in sys.modules:
                del sys.modules["stripe"]

    def test_finalize_stripe_checkout_idempotent(self):
        """Test que _finalize_stripe_event_checkout es idempotente"""
        from apps.accounts.views_private import _finalize_stripe_event_checkout

        # Crear checkout en estado created (no pagado aún)
        checkout = StripeEventCheckout.objects.create(
            user=self.parent_user,
            event=self.event,
            stripe_session_id="cs_test_idempotent",
            payment_mode="now",
            status="created",  # No pagado aún
            amount_total=Decimal("100.00"),
            player_ids=[self.player.pk],
            hotel_cart_snapshot={},
        )

        # Llamar dos veces (la primera debería procesar, la segunda no porque ya está paid)
        _finalize_stripe_event_checkout(checkout)
        checkout.refresh_from_db()
        self.assertEqual(checkout.status, "paid")  # Verificar que se marcó como pagado

        # Llamar de nuevo (debería ser idempotente)
        _finalize_stripe_event_checkout(checkout)

        # Verificar que solo se creó una asistencia
        attendances = EventAttendance.objects.filter(
            event=self.event, user=self.player_user
        )
        self.assertEqual(attendances.count(), 1)

    def test_payment_plans_appear_in_context(self):
        """Test que los planes de pago aparecen en el contexto de Plans & Payments"""
        # Crear checkout pagado
        StripeEventCheckout.objects.create(
            user=self.parent_user,
            event=self.event,
            stripe_session_id="cs_test_context",
            payment_mode="plan",
            status="paid",
            amount_total=Decimal("300.00"),
            plan_months=3,
            plan_monthly_amount=Decimal("100.00"),
            player_ids=[self.player.pk],
            hotel_cart_snapshot={},
        )

        # Obtener contexto de la vista
        from apps.accounts.views_private import UserDashboardView

        factory = RequestFactory()
        request = factory.get("/")
        request.user = self.parent_user
        request.session = {}

        view = UserDashboardView()
        view.request = request
        context = view.get_context_data()

        # Verificar que los planes aparecen
        self.assertIn("active_payment_plans", context)
        self.assertIn("payment_history", context)
        self.assertEqual(len(context["active_payment_plans"]), 1)
        self.assertEqual(len(context["payment_history"]), 1)

    def test_payment_history_only_shows_paid(self):
        """Test que el historial solo muestra checkouts pagados"""
        # Crear checkout pagado
        paid_checkout = StripeEventCheckout.objects.create(
            user=self.parent_user,
            event=self.event,
            stripe_session_id="cs_paid",
            payment_mode="now",
            status="paid",
            amount_total=Decimal("100.00"),
            player_ids=[self.player.pk],
            hotel_cart_snapshot={},
        )
        paid_checkout.paid_at = timezone.now()
        paid_checkout.save()

        # Crear checkout no pagado
        StripeEventCheckout.objects.create(
            user=self.parent_user,
            event=self.event,
            stripe_session_id="cs_created",
            payment_mode="now",
            status="created",
            amount_total=Decimal("100.00"),
            player_ids=[self.player.pk],
            hotel_cart_snapshot={},
        )

        # Obtener contexto
        from apps.accounts.views_private import UserDashboardView

        factory = RequestFactory()
        request = factory.get("/")
        request.user = self.parent_user
        request.session = {}

        view = UserDashboardView()
        view.request = request
        context = view.get_context_data()

        # Verificar que solo aparece el pagado en el historial
        self.assertEqual(len(context["payment_history"]), 1)
        self.assertEqual(context["payment_history"][0].stripe_session_id, "cs_paid")

    def test_plan_mode_creates_subscription_schedule(self):
        """Test que el modo plan crea un schedule de suscripción"""
        # Mock de subscription y schedule
        mock_subscription = Mock()
        mock_subscription.id = "sub_test_123"
        mock_subscription.items = Mock()
        mock_subscription.items.data = [{"price": {"id": "price_test_123"}}]

        mock_schedule = Mock()
        mock_schedule.id = "sub_sched_test_123"
        # El código accede a schedule.get("id", "") o schedule.id
        mock_schedule.get = Mock(return_value="sub_sched_test_123")

        # Crear checkout con subscription
        checkout = StripeEventCheckout.objects.create(
            user=self.parent_user,
            event=self.event,
            stripe_session_id="cs_test_schedule",
            payment_mode="plan",
            status="created",
            amount_total=Decimal("300.00"),
            plan_months=3,
            plan_monthly_amount=Decimal("100.00"),
            player_ids=[self.player.pk],
            hotel_cart_snapshot={},
        )

        # Mock de sesión de Stripe
        mock_session = Mock()
        mock_session.payment_status = "paid"
        mock_session.subscription = "sub_test_123"

        # Mockear stripe directamente
        import sys

        mock_stripe = MagicMock()
        mock_stripe.checkout.Session.retrieve.return_value = mock_session
        # El código accede a sub.get("items", {}) y sub.get("items", {}).get("data", [])
        mock_subscription_dict = {
            "id": "sub_test_123",
            "items": {"data": [{"price": {"id": "price_test_123"}}]},
        }
        mock_stripe.Subscription.retrieve.return_value = mock_subscription_dict
        # El código accede a schedule.get("id", "")
        mock_schedule_dict = {"id": "sub_sched_test_123"}
        mock_stripe.SubscriptionSchedule.create.return_value = mock_schedule_dict
        sys.modules["stripe"] = mock_stripe

        try:
            with self.settings(STRIPE_SECRET_KEY="sk_test_123"):
                # Usar el cliente de Django que tiene los middlewares configurados
                self.client.get(
                    reverse(
                        "accounts:stripe_event_checkout_success", args=[self.event.pk]
                    ),
                    {"session_id": "cs_test_schedule"},
                )

                # Verificar que se creó el schedule
                checkout.refresh_from_db()
                self.assertEqual(
                    checkout.stripe_subscription_schedule_id, "sub_sched_test_123"
                )
        finally:
            # Limpiar el mock
            if "stripe" in sys.modules:
                del sys.modules["stripe"]

    def test_no_show_fee_applied_without_hotel(self):
        """Test que se aplica el no-show fee cuando no hay hotel"""
        from apps.accounts.views_private import create_stripe_event_checkout_session

        factory = RequestFactory()
        request = factory.post(
            reverse(
                "accounts:create_stripe_event_checkout_session", args=[self.event.pk]
            ),
            {
                "players": [str(self.player.pk)],
                "payment_mode": "now",
            },
        )
        request.user = self.parent_user
        request.session = {}  # Sin hotel en el carrito

        # Mock de Stripe
        mock_session = Mock()
        mock_session.id = "cs_test_no_show"
        mock_session.url = "https://checkout.stripe.com/test"

        # Mockear stripe directamente
        import sys

        mock_stripe = MagicMock()
        mock_stripe.checkout.Session.create.return_value = mock_session
        sys.modules["stripe"] = mock_stripe

        try:
            with self.settings(STRIPE_SECRET_KEY="sk_test_123"):
                create_stripe_event_checkout_session(request, self.event.pk)

                # Verificar que se aplicó el no-show fee
                checkout = StripeEventCheckout.objects.get(
                    stripe_session_id="cs_test_no_show"
                )
                breakdown = checkout.breakdown
                self.assertGreater(Decimal(str(breakdown.get("no_show_fee", 0))), 0)
        finally:
            # Limpiar el mock
            if "stripe" in sys.modules:
                del sys.modules["stripe"]
