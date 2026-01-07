import json
import sys
import types
from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Player, PlayerParent, UserProfile
from apps.events.models import Event
from apps.locations.models import Hotel, HotelRoom


def _q(amount: Decimal) -> Decimal:
    return Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _to_cents(amount: Decimal) -> int:
    return int((_q(amount) * 100).to_integral_value(rounding=ROUND_HALF_UP))


class _FakeStripeSession:
    def __init__(self, id="sess_test", url="https://stripe.test/checkout"):
        self.id = id
        self.url = url


class StripeCheckoutTotalsTests(TestCase):
    def setUp(self):
        # Fake stripe module so import stripe succeeds inside the view
        self._stripe_calls = []

        fake_stripe = types.ModuleType("stripe")
        fake_stripe.api_key = None

        class _CheckoutSession:
            @staticmethod
            def create(**kwargs):
                self._stripe_calls.append(kwargs)
                return _FakeStripeSession()

        class _Checkout:
            Session = _CheckoutSession

        fake_stripe.checkout = _Checkout

        sys.modules["stripe"] = fake_stripe

        # Users
        self.parent_user = User.objects.create_user(
            username="parent1", email="parent1@test.com", password="pass"
        )
        UserProfile.objects.create(user=self.parent_user, user_type="parent")

        self.player_user = User.objects.create_user(
            username="player1", email="player1@test.com", password="pass"
        )
        UserProfile.objects.create(user=self.player_user, user_type="player")
        self.player = Player.objects.create(user=self.player_user)
        PlayerParent.objects.create(parent=self.parent_user, player=self.player)

        # Hotel + room
        self.hotel = Hotel.objects.create(
            hotel_name="HQ Hotel",
            address="123 St",
            buy_out_fee=Decimal("1000.00"),
            is_active=True,
        )
        self.room = HotelRoom.objects.create(
            hotel=self.hotel,
            room_number="101",
            name="Superior Room",
            room_type="double",
            capacity=4,
            price_per_night=Decimal("165.59"),
            price_includes_guests=2,
            additional_guest_price=Decimal("10.00"),
            breakfast_included=False,
            stock=10,
            is_available=True,
            # required by HotelRoom.clean() in our codebase
            check_in_date=timezone.localdate(),
            check_out_date=timezone.localdate() + timezone.timedelta(days=8),
            check_in_time=timezone.now().time().replace(hour=15, minute=0, second=0, microsecond=0),
            check_out_time=timezone.now().time().replace(hour=11, minute=0, second=0, microsecond=0),
        )

        # Event
        self.event = Event.objects.create(
            title="Test Event",
            description="desc",
            organizer=self.parent_user,
            default_entry_fee=Decimal("1500.00"),
            status="draft",
            hotel=self.hotel,
            payment_deadline=timezone.localdate(),  # makes plan_months = 1
        )

    @override_settings(STRIPE_SECRET_KEY="sk_test_123", STRIPE_CURRENCY="usd")
    def test_pay_now_uses_vue_payload_and_discount(self):
        """
        Pay now:
        - Uses hotel_reservation_json instead of session cart
        - Applies 5% discount only when hotel stay exists
        """
        self.client.force_login(self.parent_user)

        # Put a legacy cart in session to ensure it would be different if used
        session = self.client.session
        session["hotel_cart"] = {
            "legacy-room-1": {
                "type": "room",
                "room_id": self.room.pk,
                "check_in": "2026-01-01",
                "check_out": "2026-01-20",
                "guests": 1,
                "services": [],
            }
        }
        session.save()

        payload = {
            "hotel_pk": self.hotel.pk,
            "check_in_date": "2026-01-01",
            "check_out_date": "2026-01-09",
            "nights": 8,
            "rooms": [
                {
                    "roomId": str(self.room.pk),
                    "roomLabel": "Superior Room",
                    "price": "165.59",
                    "priceIncludesGuests": 2,
                    "additionalGuestPrice": "10.00",
                    # taxes differ per room; this is per-night fixed
                    "taxes": [
                        {"name": "ISH 5%", "amount": "8.28"},
                        {"name": "IVA 16%", "amount": "26.49"},
                    ],
                }
            ],
            "guest_assignments": {str(self.room.pk): [0, 1, 2]},  # 3 guests in room => 1 extra
            "guests": [],
        }

        resp = self.client.post(
            reverse("accounts:create_stripe_event_checkout_session", kwargs={"pk": self.event.pk}),
            data={
                "payment_mode": "now",
                "players": [str(self.player.pk)],
                "hotel_reservation_json": json.dumps(payload),
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json().get("success"))
        self.assertEqual(len(self._stripe_calls), 1)

        call = self._stripe_calls[0]
        self.assertEqual(call.get("mode"), "payment")
        items = call.get("line_items") or []
        self.assertEqual(len(items), 2)

        # Expected totals
        players_total = Decimal("1500.00")
        room_base_per_night = Decimal("165.59") + Decimal("10.00")  # 1 extra
        room_base = _q(room_base_per_night * Decimal("8"))
        taxes_per_night = Decimal("8.28") + Decimal("26.49")
        taxes_total = _q(taxes_per_night * Decimal("8"))
        hotel_total = _q(room_base + taxes_total)  # 1682.88
        self.assertEqual(hotel_total, Decimal("1682.88"))

        # Discount 5%
        discount = Decimal("0.95")
        expected_players_unit = _q(players_total * discount)
        expected_hotel_unit = _q(hotel_total * discount)

        # Find line items by name
        names = [i["price_data"]["product_data"]["name"] for i in items]
        self.assertTrue(any("Event registration" in n for n in names))
        self.assertTrue(any("Hotel stay" in n for n in names))

        for i in items:
            name = i["price_data"]["product_data"]["name"]
            unit = i["price_data"]["unit_amount"]
            qty = i.get("quantity")
            if "Event registration" in name:
                self.assertEqual(qty, 1)
                self.assertEqual(unit, _to_cents(expected_players_unit))
            elif "Hotel stay" in name:
                self.assertEqual(qty, 1)
                self.assertEqual(unit, _to_cents(expected_hotel_unit))

    @override_settings(STRIPE_SECRET_KEY="sk_test_123", STRIPE_CURRENCY="usd")
    def test_payment_plan_uses_subtotal_no_discount(self):
        """
        Payment plan:
        - Creates a subscription line item
        - No discount applied
        - Monthly amount ~ subtotal / months (months=1 in this test)
        """
        self.client.force_login(self.parent_user)

        payload = {
            "hotel_pk": self.hotel.pk,
            "check_in_date": "2026-01-01",
            "check_out_date": "2026-01-09",
            "nights": 8,
            "rooms": [
                {
                    "roomId": str(self.room.pk),
                    "roomLabel": "Superior Room",
                    "price": "165.59",
                    "priceIncludesGuests": 2,
                    "additionalGuestPrice": "10.00",
                    "taxes": [
                        {"name": "ISH 5%", "amount": "8.28"},
                        {"name": "IVA 16%", "amount": "26.49"},
                    ],
                }
            ],
            "guest_assignments": {str(self.room.pk): [0, 1, 2]},
            "guests": [],
        }

        resp = self.client.post(
            reverse("accounts:create_stripe_event_checkout_session", kwargs={"pk": self.event.pk}),
            data={
                "payment_mode": "plan",
                "players": [str(self.player.pk)],
                "hotel_reservation_json": json.dumps(payload),
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json().get("success"))
        self.assertEqual(len(self._stripe_calls), 1)

        call = self._stripe_calls[0]
        self.assertEqual(call.get("mode"), "subscription")
        items = call.get("line_items") or []
        self.assertEqual(len(items), 1)

        # Expected subtotal with no discount
        players_total = Decimal("1500.00")
        room_base_per_night = Decimal("165.59") + Decimal("10.00")
        room_base = _q(room_base_per_night * Decimal("8"))
        taxes_total = _q((Decimal("8.28") + Decimal("26.49")) * Decimal("8"))
        hotel_total = _q(room_base + taxes_total)
        subtotal = _q(players_total + hotel_total)

        li = items[0]
        self.assertEqual(li.get("quantity"), 1)
        self.assertEqual(li["price_data"]["recurring"]["interval"], "month")
        self.assertEqual(li["price_data"]["unit_amount"], _to_cents(subtotal))

    @override_settings(STRIPE_SECRET_KEY="sk_test_123", STRIPE_CURRENCY="usd")
    def test_event_without_hotel_no_buy_out_fee(self):
        """
        Events without hotel should never apply buy out fee.
        """
        event_no_hotel = Event.objects.create(
            title="No Hotel",
            description="desc",
            organizer=self.parent_user,
            default_entry_fee=Decimal("1500.00"),
            status="draft",
            hotel=None,
            payment_deadline=timezone.localdate(),
        )

        self.client.force_login(self.parent_user)
        resp = self.client.post(
            reverse("accounts:create_stripe_event_checkout_session", kwargs={"pk": event_no_hotel.pk}),
            data={
                "payment_mode": "now",
                "players": [str(self.player.pk)],
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json().get("success"))
        self.assertEqual(len(self._stripe_calls), 1)

        call = self._stripe_calls[0]
        items = call.get("line_items") or []
        # Only registration should be charged
        self.assertEqual(len(items), 1)
        name = items[0]["price_data"]["product_data"]["name"]
        self.assertIn("Event registration", name)
        self.assertEqual(items[0]["price_data"]["unit_amount"], _to_cents(Decimal("1500.00")))


