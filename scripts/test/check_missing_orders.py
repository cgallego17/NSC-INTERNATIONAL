"""
Script para verificar checkouts pagados sin órdenes creadas
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nsc_admin.settings')
django.setup()

from apps.accounts.models import Order, StripeEventCheckout

print("=" * 70)
print("VERIFICACION DE ORDENES Y CHECKOUTS")
print("=" * 70)

total_orders = Order.objects.count()
paid_orders = Order.objects.filter(status="paid").count()
pending_orders = Order.objects.filter(status__in=["pending", "pending_registration"]).count()

print(f"\n[INFO] Ordenes:")
print(f"   Total: {total_orders}")
print(f"   Pagadas: {paid_orders}")
print(f"   Pendientes: {pending_orders}")

total_checkouts = StripeEventCheckout.objects.count()
paid_checkouts = StripeEventCheckout.objects.filter(status="paid").count()
created_checkouts = StripeEventCheckout.objects.filter(status="created").count()

print(f"\n[INFO] Checkouts:")
print(f"   Total: {total_checkouts}")
print(f"   Pagados: {paid_checkouts}")
print(f"   Creados (pendientes): {created_checkouts}")

# Verificar checkouts pagados sin órdenes
paid_checkout_ids = StripeEventCheckout.objects.filter(status="paid").values_list('id', flat=True)
orders_with_checkout = Order.objects.filter(stripe_checkout_id__in=paid_checkout_ids).values_list('stripe_checkout_id', flat=True)

missing_orders = []
for checkout_id in paid_checkout_ids:
    if checkout_id not in orders_with_checkout:
        missing_orders.append(checkout_id)

print(f"\n[WARNING] Checkouts pagados SIN orden creada: {len(missing_orders)}")

if missing_orders:
    print(f"\n[INFO] IDs de checkouts sin orden:")
    for checkout_id in missing_orders[:10]:  # Mostrar solo los primeros 10
        checkout = StripeEventCheckout.objects.get(id=checkout_id)
        print(f"   - Checkout ID: {checkout_id}")
        print(f"     Usuario: {checkout.user.username}")
        print(f"     Evento: {checkout.event.title if checkout.event else 'N/A'}")
        print(f"     Monto: ${checkout.amount_total}")
        print(f"     Creado: {checkout.created_at}")
        print(f"     Pagado: {checkout.paid_at}")
        print()

if len(missing_orders) > 10:
    print(f"   ... y {len(missing_orders) - 10} más")

print("\n" + "=" * 70)
