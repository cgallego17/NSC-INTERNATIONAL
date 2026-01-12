from apps.accounts.models import Order, StripeEventCheckout
from apps.locations.models import HotelReservation

c = StripeEventCheckout.objects.get(pk=60)
print("Checkout Status:", c.status)
print("Paid at:", c.paid_at)

orders = Order.objects.filter(stripe_checkout=c)
print("Orders count:", orders.count())
if orders.exists():
    o = orders.first()
    print("Order ID:", o.pk)
    print("Order status:", o.status)
    print("Order paid_at:", o.paid_at)

reservations = HotelReservation.objects.filter(user=c.user, hotel__event=c.event)
print("Reservations count:", reservations.count())

cart = c.hotel_cart_snapshot or {}
room_count = 0
for v in cart.values():
    if isinstance(v, dict) and v.get("type") == "room":
        room_count += 1
print("Rooms in cart:", room_count)

print("\nDIAGNOSIS:")
if c.status == "paid" and not orders.exists():
    print("PROBLEM: Checkout PAID but NO ORDER")
elif (
    c.status == "paid"
    and orders.exists()
    and not reservations.exists()
    and room_count > 0
):
    print("PROBLEM: Checkout PAID, Order exists, but NO RESERVATIONS")
elif c.status == "created":
    print("Checkout still in CREATED status")
elif c.status == "paid" and orders.exists() and reservations.exists():
    print("OK: Everything created correctly")
