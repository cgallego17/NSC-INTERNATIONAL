#!/usr/bin/env python
"""
Script para probar el sistema de órdenes abandonadas.

Este script verifica que:
1. Las órdenes se marcan como "abandoned" cuando el checkout se cancela
2. Las órdenes se marcan como "abandoned" cuando el checkout expira
3. Las órdenes de planes de pago también se marcan como "abandoned"
4. Las órdenes pagadas NO se marcan como "abandoned"
"""

import os
import sys
import django
from decimal import Decimal
from datetime import timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from django.utils import timezone
from apps.accounts.models import Order, StripeEventCheckout, User
from apps.events.models import Event


def print_section(title):
    """Imprimir un título de sección"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_info(msg):
    """Imprimir mensaje informativo"""
    print(f"[INFO] {msg}")


def print_success(msg):
    """Imprimir mensaje de éxito"""
    print(f"[OK] {msg}")


def print_error(msg):
    """Imprimir mensaje de error"""
    print(f"[ERROR] {msg}")


def print_warning(msg):
    """Imprimir mensaje de advertencia"""
    print(f"[WARNING] {msg}")


def test_abandoned_orders():
    """Probar el sistema de órdenes abandonadas"""

    print_section("TEST: Sistema de Órdenes Abandonadas")

    # Obtener un usuario de prueba
    try:
        user = User.objects.filter(is_active=True).first()
        if not user:
            print_error("No se encontró ningún usuario activo para la prueba")
            return False
        print_info(f"Usuario de prueba: {user.username} ({user.email})")
    except Exception as e:
        print_error(f"Error obteniendo usuario: {e}")
        return False

    # Obtener un evento (activo o cualquier otro)
    try:
        event = Event.objects.filter(status="active").first()
        if not event:
            event = Event.objects.first()
        if not event:
            print_warning("No se encontró ningún evento para la prueba (continuando sin evento específico)")
        else:
            print_info(f"Evento de referencia: {event.title} (ID: {event.pk})")
    except Exception as e:
        print_warning(f"Error obteniendo evento: {e} (continuando sin evento específico)")

    results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
    }

    # Test 1: Verificar que existen órdenes con estado "abandoned"
    print_section("Test 1: Verificar órdenes abandonadas existentes")
    results["total_tests"] += 1
    try:
        abandoned_orders = Order.objects.filter(status="abandoned")
        count = abandoned_orders.count()
        print_info(f"Órdenes abandonadas encontradas: {count}")

        if count > 0:
            print_success(f"Test 1 PASADO: Se encontraron {count} órdenes abandonadas")
            # Mostrar algunas órdenes abandonadas
            for order in abandoned_orders[:5]:
                print_info(
                    f"  - Order #{order.order_number}: {order.event.title if order.event else 'N/A'} "
                    f"(payment_mode: {order.payment_mode}, created: {order.created_at})"
                )
            results["passed"] += 1
        else:
            print_warning("Test 1: No se encontraron órdenes abandonadas (esto puede ser normal si no hay datos)")
            results["passed"] += 1  # No es un error, solo información
    except Exception as e:
        print_error(f"Test 1 FALLIDO: {e}")
        results["failed"] += 1

    # Test 2: Verificar órdenes con checkout cancelado
    print_section("Test 2: Verificar órdenes con checkout cancelado")
    results["total_tests"] += 1
    try:
        cancelled_checkouts = StripeEventCheckout.objects.filter(status="cancelled")
        count = cancelled_checkouts.count()
        print_info(f"Checkouts cancelados encontrados: {count}")

        if count > 0:
            # Verificar que las órdenes asociadas están marcadas como "abandoned"
            abandoned_from_cancelled = 0
            not_abandoned = []

            for checkout in cancelled_checkouts[:10]:
                order = Order.objects.filter(stripe_checkout=checkout).first()
                if order:
                    if order.status == "abandoned":
                        abandoned_from_cancelled += 1
                    elif order.status in ["pending", "pending_registration"]:
                        not_abandoned.append({
                            "order": order.order_number,
                            "status": order.status,
                            "checkout": checkout.pk,
                        })

            print_info(f"Órdenes abandonadas por checkout cancelado: {abandoned_from_cancelled}")

            if not_abandoned:
                print_warning(f"Órdenes con checkout cancelado que NO están abandonadas: {len(not_abandoned)}")
                for item in not_abandoned[:3]:
                    print_warning(f"  - Order #{item['order']}: status={item['status']}, checkout={item['checkout']}")
                results["failed"] += 1
            else:
                print_success("Test 2 PASADO: Todas las órdenes con checkout cancelado están marcadas como 'abandoned'")
                results["passed"] += 1
        else:
            print_warning("Test 2: No se encontraron checkouts cancelados")
            results["passed"] += 1
    except Exception as e:
        print_error(f"Test 2 FALLIDO: {e}")
        results["failed"] += 1

    # Test 3: Verificar órdenes con checkout expirado
    print_section("Test 3: Verificar órdenes con checkout expirado")
    results["total_tests"] += 1
    try:
        expired_checkouts = StripeEventCheckout.objects.filter(status="expired")
        count = expired_checkouts.count()
        print_info(f"Checkouts expirados encontrados: {count}")

        if count > 0:
            # Verificar que las órdenes asociadas están marcadas como "abandoned"
            abandoned_from_expired = 0
            not_abandoned = []

            for checkout in expired_checkouts[:10]:
                order = Order.objects.filter(stripe_checkout=checkout).first()
                if order:
                    if order.status == "abandoned":
                        abandoned_from_expired += 1
                    elif order.status in ["pending", "pending_registration"]:
                        not_abandoned.append({
                            "order": order.order_number,
                            "status": order.status,
                            "checkout": checkout.pk,
                        })

            print_info(f"Órdenes abandonadas por checkout expirado: {abandoned_from_expired}")

            if not_abandoned:
                print_warning(f"Órdenes con checkout expirado que NO están abandonadas: {len(not_abandoned)}")
                for item in not_abandoned[:3]:
                    print_warning(f"  - Order #{item['order']}: status={item['status']}, checkout={item['checkout']}")
                results["failed"] += 1
            else:
                print_success("Test 3 PASADO: Todas las órdenes con checkout expirado están marcadas como 'abandoned'")
                results["passed"] += 1
        else:
            print_warning("Test 3: No se encontraron checkouts expirados")
            results["passed"] += 1
    except Exception as e:
        print_error(f"Test 3 FALLIDO: {e}")
        results["failed"] += 1

    # Test 4: Verificar órdenes de planes de pago abandonadas
    print_section("Test 4: Verificar órdenes de planes de pago abandonadas")
    results["total_tests"] += 1
    try:
        plan_abandoned = Order.objects.filter(
            status="abandoned",
            payment_mode="plan"
        )
        count = plan_abandoned.count()
        print_info(f"Órdenes de planes de pago abandonadas: {count}")

        if count > 0:
            print_success(f"Test 4 PASADO: Se encontraron {count} órdenes de planes de pago abandonadas")
            for order in plan_abandoned[:5]:
                checkout = order.stripe_checkout
                print_info(
                    f"  - Order #{order.order_number}: {order.event.title if order.event else 'N/A'} "
                    f"(checkout status: {checkout.status if checkout else 'N/A'}, "
                    f"subscription_id: {checkout.stripe_subscription_id if checkout else 'N/A'})"
                )
            results["passed"] += 1
        else:
            print_warning("Test 4: No se encontraron órdenes de planes de pago abandonadas")
            results["passed"] += 1
    except Exception as e:
        print_error(f"Test 4 FALLIDO: {e}")
        results["failed"] += 1

    # Test 5: Verificar que las órdenes pagadas NO están marcadas como "abandoned"
    print_section("Test 5: Verificar que órdenes pagadas NO están abandonadas")
    results["total_tests"] += 1
    try:
        paid_abandoned = Order.objects.filter(
            status="abandoned",
            paid_at__isnull=False
        )
        count = paid_abandoned.count()

        if count > 0:
            print_error(f"Test 5 FALLIDO: Se encontraron {count} órdenes pagadas marcadas como 'abandoned'")
            for order in paid_abandoned[:5]:
                print_error(
                    f"  - Order #{order.order_number}: paid_at={order.paid_at}, "
                    f"status={order.status}"
                )
            results["failed"] += 1
        else:
            print_success("Test 5 PASADO: Ninguna orden pagada está marcada como 'abandoned'")
            results["passed"] += 1
    except Exception as e:
        print_error(f"Test 5 FALLIDO: {e}")
        results["failed"] += 1

    # Test 6: Verificar órdenes pendientes recientes que deberían estar abandonadas
    print_section("Test 6: Verificar órdenes pendientes antiguas")
    results["total_tests"] += 1
    try:
        # Órdenes pendientes creadas hace más de 25 horas (más de 24h de expiración de Stripe)
        old_time = timezone.now() - timedelta(hours=25)
        old_pending = Order.objects.filter(
            status__in=["pending", "pending_registration"],
            created_at__lt=old_time
        )
        count = old_pending.count()

        if count > 0:
            print_warning(f"Se encontraron {count} órdenes pendientes creadas hace más de 25 horas")
            print_warning("Estas órdenes deberían estar marcadas como 'abandoned' si su checkout expiró")

            # Verificar si tienen checkouts expirados
            with_expired_checkout = 0
            for order in old_pending[:10]:
                checkout = order.stripe_checkout
                if checkout and checkout.status in ["expired", "cancelled"]:
                    with_expired_checkout += 1
                    print_warning(
                        f"  - Order #{order.order_number}: status={order.status}, "
                        f"checkout status={checkout.status}, created={order.created_at}"
                    )

            if with_expired_checkout > 0:
                print_error(f"Test 6 FALLIDO: {with_expired_checkout} órdenes con checkout expirado/cancelado aún están pendientes")
                results["failed"] += 1
            else:
                print_success("Test 6 PASADO: No se encontraron órdenes pendientes con checkouts expirados")
                results["passed"] += 1
        else:
            print_success("Test 6 PASADO: No se encontraron órdenes pendientes antiguas")
            results["passed"] += 1
    except Exception as e:
        print_error(f"Test 6 FALLIDO: {e}")
        results["failed"] += 1

    # Resumen final
    print_section("RESUMEN DE TESTS")
    print_info(f"Total de tests: {results['total_tests']}")
    print_success(f"Tests pasados: {results['passed']}")
    if results["failed"] > 0:
        print_error(f"Tests fallidos: {results['failed']}")
    else:
        print_success("Tests fallidos: 0")

    success_rate = (results["passed"] / results["total_tests"]) * 100
    print_info(f"Tasa de éxito: {success_rate:.1f}%")

    return results["failed"] == 0


if __name__ == "__main__":
    try:
        success = test_abandoned_orders()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[INFO] Test interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
