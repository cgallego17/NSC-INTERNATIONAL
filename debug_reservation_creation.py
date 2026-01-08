"""
Script para depurar por qué no se están creando las reservas
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nsc_admin.settings')
django.setup()

from apps.accounts.models import StripeEventCheckout
from apps.locations.models import HotelRoom
from datetime import datetime, date

checkout = StripeEventCheckout.objects.order_by('-created_at').first()

if not checkout:
    print("No se encontró checkout")
    exit(1)

print(f"Checkout: {checkout.stripe_session_id}")
print(f"Status: {checkout.status}")
print(f"\nHotel cart snapshot:")
print(json.dumps(checkout.hotel_cart_snapshot, indent=2, default=str))

cart = checkout.hotel_cart_snapshot or {}

for room_key, item_data in cart.items():
    if item_data.get("type") != "room":
        continue

    room_id = item_data.get("room_id")
    print(f"\n{'='*60}")
    print(f"Procesando habitación: {room_key}")
    print(f"Room ID: {room_id}")

    try:
        room = HotelRoom.objects.get(id=room_id)
        print(f"Room encontrado: {room.room_number}")
        print(f"  - stock: {room.stock}")
        print(f"  - is_available: {room.is_available}")

        check_in_str = item_data.get("check_in")
        check_out_str = item_data.get("check_out")
        print(f"  - check_in: {check_in_str}")
        print(f"  - check_out: {check_out_str}")

        if check_in_str and check_out_str:
            check_in = datetime.strptime(check_in_str, "%Y-%m-%d").date()
            check_out = datetime.strptime(check_out_str, "%Y-%m-%d").date()

            if room.stock is not None and room.stock > 0:
                active_reservations_count = room.reservations.filter(
                    check_in__lt=check_out,
                    check_out__gt=check_in,
                    status__in=["pending", "confirmed", "checked_in"],
                ).count()
                print(f"  - active_reservations_count: {active_reservations_count}")
                print(f"  - stock disponible: {room.stock - active_reservations_count}")

                if active_reservations_count >= room.stock:
                    print(f"  [PROBLEMA] No hay stock disponible!")
                else:
                    print(f"  [OK] Hay stock disponible")
            else:
                print(f"  [OK] Stock ilimitado (stock={room.stock})")

        print(f"  - additional_guest_details: {len(item_data.get('additional_guest_details', []))}")
        for guest in item_data.get("additional_guest_details", []):
            print(f"    * {guest.get('name')} ({guest.get('type')})")

    except HotelRoom.DoesNotExist:
        print(f"  [ERROR] Room con ID {room_id} no encontrado!")
    except Exception as e:
        print(f"  [ERROR] {e}")

