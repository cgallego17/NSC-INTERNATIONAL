#!/usr/bin/env python
"""Script para verificar el flujo completo del checkout de Stripe"""

import json

from apps.accounts.models import Order, StripeEventCheckout
from apps.locations.models import HotelReservation

# Obtener el checkout
checkout_id = 60
c = StripeEventCheckout.objects.get(pk=checkout_id)

print("=" * 80)
print("CHECKOUT INFO")
print("=" * 80)
print(f"ID: {c.pk}")
print(f"Status: {c.status}")
print(f"Paid at: {c.paid_at}")
print(f"User: {c.user.username} ({c.user.email})")
print(f"Event: {c.event.event_name}")
print(f"Stripe Session ID: {c.stripe_session_id}")
print()

# Verificar si existe Order
orders = Order.objects.filter(stripe_checkout=c)
print("=" * 80)
print(f"ORDERS (Total: {orders.count()})")
print("=" * 80)
if orders.exists():
    for o in orders:
        print(f"Order ID: {o.pk}")
        print(f"  Status: {o.status}")
        print(f"  Paid at: {o.paid_at}")
        print(f"  Created at: {o.created_at}")
        print()
else:
    print("NO ORDERS FOUND")
    print()

# Verificar hotel_cart_snapshot
print("=" * 80)
print("HOTEL CART SNAPSHOT")
print("=" * 80)
cart = c.hotel_cart_snapshot or {}
print(f"Total keys in cart: {len(cart)}")
print(f"Keys: {list(cart.keys())}")
print()

room_count = 0
for key, value in cart.items():
    if isinstance(value, dict) and value.get("type") == "room":
        room_count += 1
        print(f"Room #{room_count} (key: {key})")
        print(f'  room_id: {value.get("room_id")}')
        print(f'  check_in: {value.get("check_in")}')
        print(f'  check_out: {value.get("check_out")}')
        print(f'  guests: {value.get("guests")}')
        print(f'  additional_guest_names: {value.get("additional_guest_names")}')

        add_details = value.get("additional_guest_details")
        if add_details:
            print(f"  additional_guest_details ({len(add_details)} guests):")
            for idx, guest in enumerate(add_details, 1):
                print(
                    f'    Guest {idx}: {guest.get("name")} ({guest.get("type")}) - {guest.get("birth_date")} - {guest.get("email")}'
                )
        else:
            print(f"  additional_guest_details: None")
        print()

if room_count == 0:
    print("NO ROOMS FOUND IN CART")
    print()

# Verificar HotelReservations
print("=" * 80)
print("HOTEL RESERVATIONS")
print("=" * 80)
reservations = HotelReservation.objects.filter(user=c.user, hotel__event=c.event)
print(f"Total reservations for user in this event: {reservations.count()}")
print()

if reservations.exists():
    for r in reservations:
        print(f"Reservation ID: {r.pk}")
        print(f"  Room: {r.room.room_name}")
        print(f"  Hotel: {r.hotel.hotel_name}")
        print(f"  Check-in: {r.check_in}")
        print(f"  Check-out: {r.check_out}")
        print(f"  Status: {r.status}")
        print(f"  Guests: {r.number_of_guests}")
        print(f"  Guest name: {r.guest_name}")
        print(f'  Order ID: {r.order_id if r.order else "None"}')
        print(
            f'  Additional guest names: {r.additional_guest_names[:100] if r.additional_guest_names else "None"}'
        )
        print(
            f"  Additional guest details: {len(r.additional_guest_details_json) if r.additional_guest_details_json else 0} guests"
        )
        print(f"  Created at: {r.created_at}")
        print()
else:
    print("NO RESERVATIONS FOUND")
    print()

# Verificar si el checkout está marcado como paid pero no tiene Order
print("=" * 80)
print("DIAGNOSIS")
print("=" * 80)
if c.status == "paid" and not orders.exists():
    print("⚠️  PROBLEM: Checkout is marked as PAID but NO ORDER exists")
    print("   This means _finalize_stripe_event_checkout was not called or failed")
elif (
    c.status == "paid"
    and orders.exists()
    and not reservations.exists()
    and room_count > 0
):
    print("⚠️  PROBLEM: Checkout is PAID, Order exists, but NO RESERVATIONS created")
    print(
        "   This means _finalize_stripe_event_checkout did not create HotelReservation objects"
    )
    print("   Possible reasons:")
    print("   - Room not available")
    print("   - Room not found")
    print("   - Invalid check-in/check-out dates")
    print("   - Exception during reservation creation")
elif c.status == "created":
    print("ℹ️  Checkout is still in CREATED status (not paid yet)")
elif c.status == "paid" and orders.exists() and reservations.exists():
    print(
        "✅ Everything looks correct: Checkout PAID, Order created, Reservations created"
    )
else:
    print(
        f"Status: {c.status}, Orders: {orders.count()}, Reservations: {reservations.count()}, Rooms in cart: {room_count}"
    )

print("=" * 80)
