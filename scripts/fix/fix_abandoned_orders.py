#!/usr/bin/env python
"""
Script para corregir órdenes que deberían estar marcadas como "abandoned"
pero no lo están.
"""

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from apps.accounts.models import Order, StripeEventCheckout
from django.utils import timezone
from datetime import timedelta


def print_info(msg):
    print(f"[INFO] {msg}")


def print_success(msg):
    print(f"[OK] {msg}")


def print_error(msg):
    print(f"[ERROR] {msg}")


def fix_abandoned_orders():
    """Corregir órdenes que deberían estar marcadas como abandoned"""

    print("=" * 70)
    print("CORRECCION DE ORDENES ABANDONADAS")
    print("=" * 70)

    fixed_count = 0

    # 1. Órdenes con checkout cancelado que no están abandonadas
    print("\n[INFO] Buscando órdenes con checkout cancelado...")
    cancelled_checkouts = StripeEventCheckout.objects.filter(status="cancelled")

    for checkout in cancelled_checkouts:
        order = Order.objects.filter(stripe_checkout=checkout).first()
        if order and order.status in ["pending", "pending_registration"]:
            print_info(
                f"Corrigiendo Order #{order.order_number}: "
                f"checkout={checkout.pk} (cancelled), status actual={order.status}"
            )
            order.status = "abandoned"
            order.save(update_fields=["status", "updated_at"])
            fixed_count += 1
            print_success(f"  -> Order #{order.order_number} marcada como 'abandoned'")

    # 2. Órdenes con checkout expirado que no están abandonadas
    print("\n[INFO] Buscando órdenes con checkout expirado...")
    expired_checkouts = StripeEventCheckout.objects.filter(status="expired")

    for checkout in expired_checkouts:
        order = Order.objects.filter(stripe_checkout=checkout).first()
        if order and order.status in ["pending", "pending_registration"]:
            print_info(
                f"Corrigiendo Order #{order.order_number}: "
                f"checkout={checkout.pk} (expired), status actual={order.status}"
            )
            order.status = "abandoned"
            order.save(update_fields=["status", "updated_at"])
            fixed_count += 1
            print_success(f"  -> Order #{order.order_number} marcada como 'abandoned'")

    # 3. Órdenes pendientes antiguas (más de 25 horas) sin checkout o con checkout expirado/cancelado
    print("\n[INFO] Buscando órdenes pendientes antiguas...")
    old_time = timezone.now() - timedelta(hours=25)
    old_pending = Order.objects.filter(
        status__in=["pending", "pending_registration"],
        created_at__lt=old_time
    )

    for order in old_pending:
        checkout = order.stripe_checkout
        if not checkout or checkout.status in ["expired", "cancelled"]:
            print_info(
                f"Corrigiendo Order #{order.order_number}: "
                f"creada hace más de 25h, checkout status={checkout.status if checkout else 'N/A'}"
            )
            order.status = "abandoned"
            order.save(update_fields=["status", "updated_at"])
            fixed_count += 1
            print_success(f"  -> Order #{order.order_number} marcada como 'abandoned'")

    print("\n" + "=" * 70)
    if fixed_count > 0:
        print_success(f"Total de órdenes corregidas: {fixed_count}")
    else:
        print_info("No se encontraron órdenes que necesiten corrección")
    print("=" * 70)

    return fixed_count


if __name__ == "__main__":
    try:
        fixed = fix_abandoned_orders()
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n[INFO] Operación interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
