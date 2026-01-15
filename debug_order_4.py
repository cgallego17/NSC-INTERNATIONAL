import os
import sys

import django

# Setup Django environment
sys.path.append(r"c:\Users\cris-\Documents\ncs3\NSC-INTERNATIONAL")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from django.db.models import Q

from apps.accounts.models import Order
from apps.locations.models import HotelReservation


def inspect_order(order_id):
    try:
        order = Order.objects.get(id=order_id)
        print(f"Order #{order.id}: {order.order_number}")
        print(f"User: {order.user}")
        print(f"Stripe Session ID: {order.stripe_session_id}")
        if order.stripe_checkout:
            print(
                f"Stripe Checkout Session ID: {order.stripe_checkout.stripe_session_id}"
            )

        print("\n--- Hotel Reservations via property ---")
        reservations = order.hotel_reservations
        print(f"Count: {reservations.count()}")
        for res in reservations:
            print(
                f" - Res #{res.id}: Hotel={res.hotel}, Room={res.room}, Order={res.order_id}"
            )

        print("\n--- Hotel Reservations via direct query (order=order) ---")
        direct_reservations = HotelReservation.objects.filter(order=order)
        print(f"Count: {direct_reservations.count()}")

        print("\n--- Hotel Reservations via Stripe Session ID search in notes ---")
        session_id = order.stripe_session_id or (
            order.stripe_checkout.stripe_session_id if order.stripe_checkout else None
        )
        if session_id:
            note_reservations = HotelReservation.objects.filter(
                notes__icontains=session_id
            )
            print(f"Searching for session_id: {session_id}")
            print(f"Count: {note_reservations.count()}")
            for res in note_reservations:
                print(f" - Res #{res.id}: Hotel={res.hotel}, Notes={res.notes}")
        else:
            print("No Stripe Session ID to search for.")

        print("\n--- Hotel Reservations for this user (ALL) ---")
        user_reservations = HotelReservation.objects.filter(user=order.user).order_by(
            "-created_at"
        )
        print(f"Total count: {user_reservations.count()}")
        for res in user_reservations[:5]:
            print(
                f" - Res #{res.id}: Created={res.created_at}, Order={res.order_id}, Notes='{res.notes}'"
            )

        print("\n--- Order Breakdown ---")
        print(order.breakdown)

        if order.stripe_checkout:
            print("\n--- Stripe Checkout Hotel Cart Snapshot ---")
            print(order.stripe_checkout.hotel_cart_snapshot)

    except Order.DoesNotExist:
        print(f"Order {order_id} not found.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    inspect_order(4)
