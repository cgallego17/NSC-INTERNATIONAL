"""
Script para revisar checkouts cancelados y verificar si tienen wallet_deduction
y si fueron reembolsados correctamente.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from decimal import Decimal
from django.contrib.auth.models import User
from apps.accounts.models import StripeEventCheckout, UserWallet, WalletTransaction
from django.utils import timezone
from datetime import timedelta


def check_cancelled_checkouts():
    """Revisa checkouts cancelados y verifica wallet refunds"""
    print("\n" + "=" * 80)
    print("REVISION DE CHECKOUTS CANCELADOS")
    print("=" * 80 + "\n")

    # Buscar todos los checkouts cancelados
    cancelled_checkouts = StripeEventCheckout.objects.filter(
        status="cancelled"
    ).order_by("-created_at")

    print(f"[INFO] Total de checkouts cancelados: {cancelled_checkouts.count()}\n")

    if cancelled_checkouts.count() == 0:
        print("[INFO] No hay checkouts cancelados en la base de datos.")
        return

    # Revisar checkouts recientes (últimos 30 días)
    recent_date = timezone.now() - timedelta(days=30)
    recent_cancelled = cancelled_checkouts.filter(created_at__gte=recent_date)
    print(f"[INFO] Checkouts cancelados en los últimos 30 días: {recent_cancelled.count()}\n")

    # Revisar cada checkout cancelado
    checkouts_with_wallet = []
    checkouts_without_refund = []

    for checkout in recent_cancelled:
        breakdown = checkout.breakdown or {}
        wallet_deduction_str = breakdown.get("wallet_deduction", "0")

        try:
            wallet_deduction = Decimal(str(wallet_deduction_str))
        except (ValueError, TypeError):
            wallet_deduction = Decimal("0.00")

        if wallet_deduction > 0:
            checkouts_with_wallet.append((checkout, wallet_deduction))

            # Verificar si hay un refund para este checkout
            wallet, _ = UserWallet.objects.get_or_create(user=checkout.user)
            refund_transactions = WalletTransaction.objects.filter(
                wallet=wallet,
                transaction_type="refund",
                reference_id__contains=f"checkout_cancel:{checkout.pk}",
            )

            if not refund_transactions.exists():
                # También buscar por referencia sin el prefijo exacto
                refund_transactions = WalletTransaction.objects.filter(
                    wallet=wallet,
                    transaction_type="refund",
                    description__contains=checkout.event.title,
                    created_at__gte=checkout.created_at,
                )

            if not refund_transactions.exists():
                checkouts_without_refund.append((checkout, wallet_deduction))

    print(f"[INFO] Checkouts cancelados con wallet_deduction: {len(checkouts_with_wallet)}")
    print(
        f"[INFO] Checkouts cancelados SIN reembolso de wallet: {len(checkouts_without_refund)}\n"
    )

    if checkouts_without_refund:
        print("=" * 80)
        print("CHECKOUTS CANCELADOS QUE NECESITAN REEMBOLSO:")
        print("=" * 80 + "\n")

        for checkout, wallet_deduction in checkouts_without_refund:
            print(f"Checkout ID: {checkout.pk}")
            print(f"  Usuario: {checkout.user.username} (ID: {checkout.user.pk})")
            print(f"  Evento: {checkout.event.title} (ID: {checkout.event.pk})")
            print(f"  Fecha de creación: {checkout.created_at}")
            print(f"  Fecha de cancelación: {checkout.updated_at}")
            print(f"  Wallet deduction: ${wallet_deduction}")
            print(f"  Session ID: {checkout.stripe_session_id}")
            print(f"  Balance actual del wallet: ${wallet.balance}")

            # Verificar balance del wallet
            wallet, _ = UserWallet.objects.get_or_create(user=checkout.user)
            print(f"  Balance actual del wallet: ${wallet.balance}")

            print("-" * 80)

    # También revisar checkouts expirados
    expired_checkouts = StripeEventCheckout.objects.filter(
        status="expired"
    ).order_by("-created_at")

    print(f"\n[INFO] Total de checkouts expirados: {expired_checkouts.count()}")
    recent_expired = expired_checkouts.filter(created_at__gte=recent_date)
    print(f"[INFO] Checkouts expirados en los últimos 30 días: {recent_expired.count()}\n")

    expired_without_refund = []
    for checkout in recent_expired:
        breakdown = checkout.breakdown or {}
        wallet_deduction_str = breakdown.get("wallet_deduction", "0")

        try:
            wallet_deduction = Decimal(str(wallet_deduction_str))
        except (ValueError, TypeError):
            wallet_deduction = Decimal("0.00")

        if wallet_deduction > 0:
            wallet, _ = UserWallet.objects.get_or_create(user=checkout.user)
            refund_transactions = WalletTransaction.objects.filter(
                wallet=wallet,
                transaction_type="refund",
                reference_id__contains=f"checkout_expired:{checkout.pk}",
            )

            if not refund_transactions.exists():
                refund_transactions = WalletTransaction.objects.filter(
                    wallet=wallet,
                    transaction_type="refund",
                    description__contains=checkout.event.title,
                    created_at__gte=checkout.created_at,
                )

            if not refund_transactions.exists():
                expired_without_refund.append((checkout, wallet_deduction))

    if expired_without_refund:
        print("=" * 80)
        print("CHECKOUTS EXPIRADOS QUE NECESITAN REEMBOLSO:")
        print("=" * 80 + "\n")

        for checkout, wallet_deduction in expired_without_refund:
            print(f"Checkout ID: {checkout.pk}")
            print(f"  Usuario: {checkout.user.username} (ID: {checkout.user.pk})")
            print(f"  Evento: {checkout.event.title} (ID: {checkout.event.pk})")
            print(f"  Fecha de creación: {checkout.created_at}")
            print(f"  Wallet deduction: ${wallet_deduction}")
            print(f"  Session ID: {checkout.stripe_session_id}")

            wallet, _ = UserWallet.objects.get_or_create(user=checkout.user)
            print(f"  Balance actual del wallet: ${wallet.balance}")
            print("-" * 80)

    # Resumen
    print("\n" + "=" * 80)
    print("RESUMEN:")
    print("=" * 80)
    print(f"Checkouts cancelados con wallet: {len(checkouts_with_wallet)}")
    print(f"Checkouts cancelados sin reembolso: {len(checkouts_without_refund)}")
    print(f"Checkouts expirados sin reembolso: {len(expired_without_refund)}")
    print("=" * 80 + "\n")

    # Si hay checkouts que necesitan reembolso, ofrecer opción de reembolsarlos
    total_to_refund = checkouts_without_refund + expired_without_refund
    if total_to_refund:
        print(f"[ADVERTENCIA] Se encontraron {len(total_to_refund)} checkouts que necesitan reembolso.")
        print("[INFO] Ejecuta el script de reembolso manual si deseas procesarlos.\n")


if __name__ == "__main__":
    check_cancelled_checkouts()
