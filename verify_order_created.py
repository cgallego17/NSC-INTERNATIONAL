"""
Script para verificar que la última orden creada tiene todas las relaciones correctas
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nsc_admin.settings')
django.setup()

from apps.accounts.models import Order
from apps.locations.models import HotelReservation

# Obtener la última orden
order = Order.objects.order_by('-created_at').first()

if not order:
    print("No se encontró ninguna orden")
    exit(1)

print("=" * 80)
print(f"VERIFICANDO ORDEN: {order.order_number}")
print("=" * 80)

print(f"\n1. Información básica:")
print(f"   - Order Number: {order.order_number}")
print(f"   - Status: {order.status}")
print(f"   - Total: ${order.total_amount}")
print(f"   - Evento: {order.event.title if order.event else 'N/A'}")

print(f"\n2. Reservas de hotel:")
reservations = HotelReservation.objects.filter(order=order)
print(f"   - Total reservas (via order field): {reservations.count()}")

if reservations.exists():
    for i, res in enumerate(reservations, 1):
        print(f"\n   Reserva {i}:")
        print(f"     - ID: {res.id}")
        print(f"     - Hotel: {res.hotel.hotel_name}")
        print(f"     - Habitación: {res.room.room_number}")
        print(f"     - Check-in: {res.check_in}")
        print(f"     - Check-out: {res.check_out}")
        print(f"     - Huéspedes: {res.number_of_guests}")
        print(f"     - Huéspedes adicionales: {len(res.additional_guest_details_json)}")
        for guest in res.additional_guest_details_json:
            print(f"       * {guest.get('name')} ({guest.get('type')}) - {guest.get('birth_date', 'N/A')}")
else:
    print("   [WARNING] No se encontraron reservas vinculadas directamente")
    # Buscar por session_id como fallback
    if order.stripe_session_id:
        reservations_by_session = HotelReservation.objects.filter(
            notes__icontains=order.stripe_session_id
        )
        print(f"   - Reservas encontradas por session_id: {reservations_by_session.count()}")
        if reservations_by_session.exists():
            for i, res in enumerate(reservations_by_session, 1):
                print(f"\n   Reserva {i} (via session_id):")
                print(f"     - ID: {res.id}")
                print(f"     - Hotel: {res.hotel.hotel_name}")
                print(f"     - Habitación: {res.room.room_number}")

print(f"\n3. Breakdown de reservas en Order:")
if order.breakdown and "hotel_reservations" in order.breakdown:
    print(f"   - Total en breakdown: {len(order.breakdown['hotel_reservations'])}")
    for i, res_info in enumerate(order.breakdown["hotel_reservations"], 1):
        print(f"\n   Reserva {i} del breakdown:")
        print(f"     - Habitación: {res_info.get('room_number')}")
        print(f"     - Hotel: {res_info.get('hotel_name')}")
        if res_info.get("additional_guest_details"):
            print(f"     - Huéspedes adicionales: {len(res_info['additional_guest_details'])}")
            for guest in res_info["additional_guest_details"]:
                print(f"       * {guest.get('name')} ({guest.get('type')}) - {guest.get('birth_date', 'N/A')}")
else:
    print("   [WARNING] No hay reservas en el breakdown")

print(f"\n4. Jugadores registrados:")
print(f"   - Total: {len(order.registered_players)}")
for player in order.registered_players:
    print(f"     - {player.user.get_full_name()} ({player.division})")

print("\n" + "=" * 80)

