"""
Script para crear órdenes faltantes para checkouts pagados
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nsc_admin.settings')
django.setup()

from apps.accounts.models import Order, StripeEventCheckout
from apps.accounts.views_private import _create_order_from_stripe_checkout

print("=" * 70)
print("CREAR ORDENES FALTANTES PARA CHECKOUTS PAGADOS")
print("=" * 70)

# Buscar checkouts pagados sin órdenes
paid_checkouts = StripeEventCheckout.objects.filter(status="paid")
orders_with_checkout = Order.objects.filter(
    stripe_checkout_id__in=paid_checkouts.values_list('id', flat=True)
).values_list('stripe_checkout_id', flat=True)

missing_orders = []
for checkout in paid_checkouts:
    if checkout.id not in orders_with_checkout:
        missing_orders.append(checkout)

print(f"\n[INFO] Checkouts pagados sin orden: {len(missing_orders)}")

if missing_orders:
    print(f"\n[INFO] Creando órdenes faltantes...")
    for checkout in missing_orders:
        try:
            print(f"   - Checkout ID: {checkout.id}, Usuario: {checkout.user.username}, Evento: {checkout.event.title if checkout.event else 'N/A'}")
            order = _create_order_from_stripe_checkout(checkout)
            print(f"     [OK] Orden creada: {order.order_number}")
        except Exception as e:
            print(f"     [ERROR] Error creando orden: {e}")
            import traceback
            traceback.print_exc()
else:
    print(f"\n[OK] No hay checkouts pagados sin órdenes.")

print("\n" + "=" * 70)
