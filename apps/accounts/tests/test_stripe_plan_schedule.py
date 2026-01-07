import sys
import types
from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import StripeEventCheckout, UserProfile
from apps.events.models import Event
from apps.locations.models import Hotel


class _FakeStripeSessionObj:
    def __init__(self, payment_status="paid", subscription="sub_123"):
        self.payment_status = payment_status
        self.subscription = subscription


class StripePlanScheduleTests(TestCase):
    def setUp(self):
        # Fake stripe module so import stripe succeeds inside the views
        self._schedule_calls = []
        self._subscription_retrieve_calls = []

        fake_stripe = types.ModuleType("stripe")
        fake_stripe.api_key = None

        class _CheckoutSession:
            @staticmethod
            def retrieve(session_id, stripe_account=None):
                # Return a paid session with a subscription id
                return _FakeStripeSessionObj(payment_status="paid", subscription="sub_test_123")

        class _Checkout:
            Session = _CheckoutSession

        class _Subscription:
            @staticmethod
            def retrieve(subscription_id, stripe_account=None):
                self._subscription_retrieve_calls.append((subscription_id, stripe_account))
                # Minimal structure used by _ensure_plan_subscription_schedule
                return {"items": {"data": [{"price": {"id": "price_test_123"}}]}}

        class _SubscriptionSchedule:
            @staticmethod
            def create(**kwargs):
                self._schedule_calls.append(kwargs)
                return {"id": "sched_test_123"}

        fake_stripe.checkout = _Checkout
        fake_stripe.Subscription = _Subscription
        fake_stripe.SubscriptionSchedule = _SubscriptionSchedule

        sys.modules["stripe"] = fake_stripe

        # User + profile
        self.user = User.objects.create_user(
            username="parent2", email="parent2@test.com", password="pass"
        )
        UserProfile.objects.create(user=self.user, user_type="parent")

        # Hotel + event
        hotel = Hotel.objects.create(
            hotel_name="HQ",
            address="123",
            buy_out_fee=Decimal("0.00"),
            is_active=True,
        )
        # Make a deadline 3 months out so plan_months > 1
        self.event = Event.objects.create(
            title="Plan Event",
            description="d",
            organizer=self.user,
            default_entry_fee=Decimal("100.00"),
            status="draft",
            hotel=hotel,
            payment_deadline=date(2026, 4, 15),
        )

    @override_settings(STRIPE_SECRET_KEY="sk_test_123")
    def test_success_creates_subscription_schedule_for_plan_months_gt_1(self):
        """
        When payment_mode=plan and plan_months > 1, after successful checkout
        we must create a SubscriptionSchedule with iterations = months-1, and store it.
        """
        self.client.force_login(self.user)

        # Create checkout record as if created during session creation
        checkout = StripeEventCheckout.objects.create(
            user=self.user,
            event=self.event,
            stripe_session_id="sess_test_123",
            currency="usd",
            payment_mode="plan",
            discount_percent=0,
            player_ids=[1],
            hotel_cart_snapshot={},
            breakdown={},
            amount_total=Decimal("0.00"),
            plan_months=3,
            plan_monthly_amount=Decimal("10.00"),
            status="created",
        )

        resp = self.client.get(
            reverse("accounts:stripe_event_checkout_success", kwargs={"pk": self.event.pk})
            + "?session_id=sess_test_123"
        )
        self.assertEqual(resp.status_code, 302)

        checkout.refresh_from_db()
        self.assertEqual(checkout.stripe_subscription_id, "sub_test_123")
        self.assertEqual(checkout.stripe_subscription_schedule_id, "sched_test_123")

        self.assertEqual(len(self._schedule_calls), 1)
        call = self._schedule_calls[0]
        phases = call.get("phases") or []
        self.assertEqual(phases[0].get("iterations"), 2)  # months-1


