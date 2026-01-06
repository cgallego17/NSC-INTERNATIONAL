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

    def test_plan_payment_subscription_only_charges_required_months(self):
        """Test que el plan de pago solo se suscribe por los meses necesarios hasta pagar el total"""
        import sys
        from datetime import date
        from decimal import ROUND_HALF_UP
        from unittest.mock import patch

        # Configurar evento con deadline para calcular meses
        future_date = date.today() + timedelta(days=90)  # ~3 meses
        self.event.payment_deadline = future_date
        self.event.save()

        # Calcular meses esperados (inclusive desde hoy hasta deadline)
        from django.utils import timezone

        now = timezone.localdate()
        expected_months = (
            (future_date.year - now.year) * 12 + (future_date.month - now.month) + 1
        )

        # El subtotal se calcula como: players_total (sin descuento en plan) + hotel_total + no_show_fee
        # Para simplificar, usaremos el default_entry_fee del evento
        players_count = 1
        players_total = Decimal(str(self.event.default_entry_fee)) * Decimal(
            str(players_count)
        )
        # No hay hotel en este test, pero puede haber no_show_fee si el evento tiene hotel
        hotel_total = Decimal("0.00")
        no_show_fee = Decimal("1000.00") if self.event.hotel else Decimal("0.00")
        subtotal = players_total + hotel_total + no_show_fee

        # En modo plan, el monto mensual es subtotal / meses (sin descuento)
        expected_monthly_amount = (subtotal / Decimal(str(expected_months))).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        # Mock de Stripe
        mock_stripe = MagicMock()

        # Mock de sesión de checkout
        mock_checkout_session = Mock()
        mock_checkout_session.id = "cs_test_plan"
        mock_checkout_session.url = "https://checkout.stripe.com/test"
        mock_stripe.checkout.Session.create.return_value = mock_checkout_session

        # Mock de sesión de éxito (con subscription)
        mock_success_session = Mock()
        mock_success_session.payment_status = "paid"
        mock_success_session.subscription = "sub_test_plan_123"
        mock_stripe.checkout.Session.retrieve.return_value = mock_success_session

        # Mock de subscription
        mock_subscription = {
            "id": "sub_test_plan_123",
            "items": {"data": [{"price": {"id": "price_test_plan_123"}}]},
        }
        mock_stripe.Subscription.retrieve.return_value = mock_subscription

        # Mock de subscription schedule
        mock_schedule = {"id": "sub_sched_test_plan_123"}
        mock_stripe.SubscriptionSchedule.create.return_value = mock_schedule

        sys.modules["stripe"] = mock_stripe

        try:
            with self.settings(STRIPE_SECRET_KEY="sk_test_123"):
                # 1. Crear sesión de checkout en modo plan
                response = self.client.post(
                    reverse(
                        "accounts:create_stripe_event_checkout_session",
                        args=[self.event.pk],
                    ),
                    {
                        "players": [self.player.pk],
                        "payment_mode": "plan",
                    },
                )

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertTrue(data.get("success"))

                # Verificar que se creó el checkout con los datos correctos
                checkout = StripeEventCheckout.objects.get(
                    stripe_session_id="cs_test_plan"
                )
                self.assertEqual(checkout.payment_mode, "plan")
                self.assertEqual(checkout.plan_months, expected_months)
                # Verificar que el monto mensual es aproximadamente correcto
                self.assertAlmostEqual(
                    float(checkout.plan_monthly_amount),
                    float(expected_monthly_amount),
                    places=2,
                )

                # Verificar que se llamó a Session.create con modo subscription
                create_call = mock_stripe.checkout.Session.create
                self.assertTrue(create_call.called)
                call_kwargs = create_call.call_args[1]
                self.assertEqual(call_kwargs["mode"], "subscription")

                # Verificar que los line_items tienen el monto mensual correcto
                line_items = call_kwargs["line_items"]
                self.assertEqual(len(line_items), 1)  # Solo el item de suscripción
                subscription_item = line_items[0]
                self.assertEqual(
                    subscription_item["price_data"]["unit_amount"],
                    int(expected_monthly_amount * 100),  # Convertir a centavos
                )

                # 2. Simular éxito del pago
                response = self.client.get(
                    reverse(
                        "accounts:stripe_event_checkout_success", args=[self.event.pk]
                    ),
                    {"session_id": "cs_test_plan"},
                )

                # Verificar que se creó el schedule de suscripción
                checkout.refresh_from_db()
                self.assertEqual(checkout.stripe_subscription_id, "sub_test_plan_123")
                self.assertEqual(
                    checkout.stripe_subscription_schedule_id, "sub_sched_test_plan_123"
                )

                # Verificar que se llamó a SubscriptionSchedule.create con los parámetros correctos
                schedule_create_call = mock_stripe.SubscriptionSchedule.create
                self.assertTrue(schedule_create_call.called)
                schedule_kwargs = schedule_create_call.call_args[1]

                # Verificar que el schedule se crea desde la suscripción
                self.assertEqual(
                    schedule_kwargs["from_subscription"], "sub_test_plan_123"
                )

                # Verificar que se cancela después de los meses
                self.assertEqual(schedule_kwargs["end_behavior"], "cancel")

                # Verificar que las fases tienen las iteraciones correctas
                # (remaining_months = months - 1 porque el primer pago ya se hizo)
                phases = schedule_kwargs["phases"]
                self.assertEqual(len(phases), 1)
                phase = phases[0]
                expected_iterations = (
                    expected_months - 1
                )  # Menos 1 porque el primer pago ya se hizo
                self.assertEqual(phase["iterations"], expected_iterations)

                # Verificar que el precio es correcto
                self.assertEqual(phase["items"][0]["price"], "price_test_plan_123")

                # 3. Verificar que el plan aparece en Plans & Payments
                # Obtener el contexto de la vista directamente
                from django.test import RequestFactory

                from apps.accounts.views_private import UserDashboardView

                factory = RequestFactory()
                request = factory.get("/")
                request.user = self.parent_user
                # Agregar sesión al request
                from django.contrib.sessions.middleware import SessionMiddleware

                middleware = SessionMiddleware(lambda req: None)
                middleware.process_request(request)
                request.session.save()

                view = UserDashboardView()
                view.request = request
                context = view.get_context_data()

                # Verificar que el plan aparece en active_payment_plans
                active_plans = context.get("active_payment_plans", [])
                self.assertGreater(
                    len(active_plans),
                    0,
                    "El plan debería aparecer en active_payment_plans",
                )

                # Buscar nuestro checkout en los planes activos
                plan_found = False
                for plan in active_plans:
                    if plan.pk == checkout.pk:
                        plan_found = True
                        # Verificar que tiene los datos correctos
                        self.assertEqual(plan.payment_mode, "plan")
                        self.assertEqual(plan.status, "paid")
                        self.assertEqual(plan.plan_months, expected_months)
                        self.assertAlmostEqual(
                            float(plan.plan_monthly_amount),
                            float(expected_monthly_amount),
                            places=2,
                        )
                        break

                self.assertTrue(
                    plan_found, "El checkout debería estar en active_payment_plans"
                )

                # Verificar que el plan aparece en payment_history
                payment_history = context.get("payment_history", [])
                self.assertGreater(
                    len(payment_history),
                    0,
                    "El plan debería aparecer en payment_history",
                )

                # Buscar nuestro checkout en el historial
                history_found = False
                for history_item in payment_history:
                    if history_item.pk == checkout.pk:
                        history_found = True
                        # Verificar que tiene los datos correctos
                        self.assertEqual(history_item.status, "paid")
                        self.assertEqual(history_item.payment_mode, "plan")
                        self.assertIsNotNone(history_item.paid_at)
                        break

                self.assertTrue(
                    history_found, "El checkout debería estar en payment_history"
                )

                # Verificar que el plan tiene subscription_id y schedule_id guardados
                checkout.refresh_from_db()
                self.assertIsNotNone(checkout.stripe_subscription_id)
                self.assertIsNotNone(checkout.stripe_subscription_schedule_id)
                self.assertEqual(checkout.status, "paid")
                self.assertIsNotNone(checkout.paid_at)

                # 4. Verificar que los próximos pagos aparecen en upcoming_payments
                upcoming_payments = context.get("upcoming_payments", [])
                # Debería haber (expected_months - 1) próximos pagos (el primer pago ya se hizo)
                expected_upcoming_count = expected_months - 1
                self.assertGreaterEqual(
                    len(upcoming_payments),
                    expected_upcoming_count,
                    f"Debería haber al menos {expected_upcoming_count} próximos pagos",
                )

                # Verificar que los próximos pagos tienen los datos correctos
                for payment in upcoming_payments:
                    if payment["checkout"].pk == checkout.pk:
                        self.assertEqual(payment["event"], self.event)
                        self.assertIsNotNone(payment["due_date"])
                        self.assertEqual(payment["amount"], expected_monthly_amount)
                        self.assertIn("payment_number", payment)
                        self.assertIn("total_payments", payment)
                        self.assertEqual(payment["total_payments"], expected_months)
                        # Verificar que la fecha es futura
                        from django.utils import timezone

                        self.assertGreater(payment["due_date"], timezone.now())

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
