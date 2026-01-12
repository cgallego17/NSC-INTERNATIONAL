"""
Script para verificar órdenes recientes
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nsc_admin.settings')
django.setup()

from apps.accounts.models import Order
from django.utils import timezone
from datetime import timedelta

print("=" * 70)
print("VERIFICACION DE ORDENES RECIENTES")
print("=" * 70)

recent = timezone.now() - timedelta(days=7)
orders = Order.objects.filter(created_at__gte=recent).order_by('-created_at')

print(f"\n[INFO] Ordenes creadas en los ultimos 7 dias: {orders.count()}")

if orders.exists():
    print(f"\n[INFO] Ultimas 10 ordenes:")
    for o in orders[:10]:
        print(f"  - {o.order_number}:")
        print(f"    Status: {o.status}")
        print(f"    Usuario: {o.user.username}")
        print(f"    Evento: {o.event.title if o.event else 'N/A'}")
        print(f"    Monto: ${o.total_amount}")
        print(f"    Creado: {o.created_at}")
        print(f"    Pagado: {o.paid_at if o.paid_at else 'No'}")
        print()
else:
    print("\n[WARNING] No hay ordenes creadas en los ultimos 7 dias")

print("=" * 70)
