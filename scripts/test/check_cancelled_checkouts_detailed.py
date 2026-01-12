"""
Script para revisar en detalle los checkouts cancelados y expirados.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from decimal import Decimal
from apps.accounts.models import StripeEventCheckout, UserWallet, WalletTransaction
from django.utils import timezone
from datetime import timedelta


def check_cancelled_checkouts_detailed():
    """Revisa en detalle los checkouts cancelados y expirados"""
    print("\n" + "=" * 80)
    print("REVISION DETALLADA DE CHECKOUTS CANCELADOS Y EXPIRADOS")
    print("=" * 80 + "\n")

    # Buscar checkouts cancelados recientes
    recent_date = timezone.now() - timedelta(days=30)

    cancelled = StripeEventCheckout.objects.filter(
        status="cancelled",
        created_at__gte=recent_date
    ).order_by("-created_at")

    expired = StripeEventCheckout.objects.filter(
        status="expired",
        created_at__gte=recent_date
    ).order_by("-created_at")

    print(f"[INFO] Checkouts cancelados (últimos 30 días): {cancelled.count()}")
    print(f"[INFO] Checkouts expirados (últimos 30 días): {expired.count()}\n")

    # Revisar cancelados
    if cancelled.exists():
        print("=" * 80)
        print("CHECKOUTS CANCELADOS:")
        print("=" * 80 + "\n")

        for checkout in cancelled:
            print(f"Checkout ID: {checkout.pk}")
            print(f"  Usuario: {checkout.user.username} (ID: {checkout.user.pk})")
            print(f"  Evento: {checkout.event.title} (ID: {checkout.event.pk})")
            print(f"  Creado: {checkout.created_at}")
            print(f"  Actualizado: {checkout.updated_at}")
            print(f"  Session ID: {checkout.stripe_session_id}")
            print(f"  Payment Mode: {checkout.payment_mode}")
            print(f"  Amount Total: ${checkout.amount_total}")

            breakdown = checkout.breakdown or {}
            print(f"  Breakdown: {breakdown}")

            wallet_deduction_str = breakdown.get("wallet_deduction", "0")
            try:
                wallet_deduction = Decimal(str(wallet_deduction_str))
            except:
                wallet_deduction = Decimal("0.00")

            print(f"  Wallet Deduction: ${wallet_deduction}")

            # Verificar wallet del usuario
            wallet, _ = UserWallet.objects.get_or_create(user=checkout.user)
            print(f"  Wallet Balance Actual: ${wallet.balance}")

            # Buscar transacciones de refund relacionadas
            refunds = WalletTransaction.objects.filter(
                wallet=wallet,
                transaction_type="refund",
                created_at__gte=checkout.created_at
            ).order_by("-created_at")

            print(f"  Refunds después del checkout: {refunds.count()}")
            for refund in refunds[:3]:  # Mostrar últimos 3
                print(f"    - ${refund.amount} el {refund.created_at}: {refund.description}")
                print(f"      Reference: {refund.reference_id}")

            print("-" * 80)

    # Revisar expirados (solo los primeros 10 para no saturar)
    if expired.exists():
        print("\n" + "=" * 80)
        print("CHECKOUTS EXPIRADOS (mostrando primeros 10):")
        print("=" * 80 + "\n")

        for checkout in expired[:10]:
            print(f"Checkout ID: {checkout.pk}")
            print(f"  Usuario: {checkout.user.username} (ID: {checkout.user.pk})")
            print(f"  Evento: {checkout.event.title} (ID: {checkout.event.pk})")
            print(f"  Creado: {checkout.created_at}")
            print(f"  Session ID: {checkout.stripe_session_id}")

            breakdown = checkout.breakdown or {}
            wallet_deduction_str = breakdown.get("wallet_deduction", "0")
            try:
                wallet_deduction = Decimal(str(wallet_deduction_str))
            except:
                wallet_deduction = Decimal("0.00")

            print(f"  Wallet Deduction: ${wallet_deduction}")

            if wallet_deduction > 0:
                wallet, _ = UserWallet.objects.get_or_create(user=checkout.user)
                print(f"  Wallet Balance Actual: ${wallet.balance}")

                # Buscar refunds
                refunds = WalletTransaction.objects.filter(
                    wallet=wallet,
                    transaction_type="refund",
                    reference_id__contains=f"checkout_expired:{checkout.pk}"
                )

                if refunds.exists():
                    print(f"  [OK] Reembolso encontrado")
                else:
                    print(f"  [ADVERTENCIA] No se encontró reembolso específico")

            print("-" * 80)

    # Buscar checkouts recientes en estado "created" que podrían estar "colgados"
    created_recent = StripeEventCheckout.objects.filter(
        status="created",
        created_at__gte=recent_date
    ).order_by("-created_at")

    print(f"\n[INFO] Checkouts en estado 'created' (últimos 30 días): {created_recent.count()}")

    if created_recent.exists():
        print("\n[ADVERTENCIA] Hay checkouts en estado 'created' que podrían necesitar cancelación:")
        for checkout in created_recent[:5]:
            print(f"  - Checkout {checkout.pk}: {checkout.user.username}, {checkout.event.title}, creado {checkout.created_at}")
            breakdown = checkout.breakdown or {}
            wallet_deduction_str = breakdown.get("wallet_deduction", "0")
            try:
                wallet_deduction = Decimal(str(wallet_deduction_str))
            except:
                wallet_deduction = Decimal("0.00")
            if wallet_deduction > 0:
                print(f"    [ADVERTENCIA] Tiene wallet_deduction de ${wallet_deduction}")

    print("\n" + "=" * 80)
    print("REVISION COMPLETADA")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    check_cancelled_checkouts_detailed()
