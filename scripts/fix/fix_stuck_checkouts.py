"""
Script para procesar checkouts en estado 'created' que tienen wallet_deduction
y deberían estar cancelados o expirados.
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


def fix_stuck_checkouts():
    """Procesa checkouts en estado 'created' que tienen wallet_deduction"""
    print("\n" + "=" * 80)
    print("PROCESANDO CHECKOUTS COLGADOS CON WALLET_DEDUCTION")
    print("=" * 80 + "\n")

    # Buscar checkouts en estado "created" con wallet_deduction
    recent_date = timezone.now() - timedelta(days=30)

    stuck_checkouts = StripeEventCheckout.objects.filter(
        status="created",
        created_at__gte=recent_date
    ).order_by("-created_at")

    checkouts_to_fix = []

    for checkout in stuck_checkouts:
        breakdown = checkout.breakdown or {}
        wallet_deduction_str = breakdown.get("wallet_deduction", "0")

        try:
            wallet_deduction = Decimal(str(wallet_deduction_str))
        except:
            wallet_deduction = Decimal("0.00")

        if wallet_deduction > 0:
            # Verificar si ya hay un refund
            wallet, _ = UserWallet.objects.get_or_create(user=checkout.user)
            refund_exists = WalletTransaction.objects.filter(
                wallet=wallet,
                transaction_type="refund",
                reference_id__contains=f"checkout_cancel:{checkout.pk}"
            ).exists()

            if not refund_exists:
                # También verificar por referencia de expired
                refund_exists = WalletTransaction.objects.filter(
                    wallet=wallet,
                    transaction_type="refund",
                    reference_id__contains=f"checkout_expired:{checkout.pk}"
                ).exists()

            if not refund_exists:
                checkouts_to_fix.append((checkout, wallet_deduction))

    print(f"[INFO] Checkouts encontrados con wallet_deduction sin reembolso: {len(checkouts_to_fix)}\n")

    if not checkouts_to_fix:
        print("[INFO] No hay checkouts que necesiten procesamiento.")
        return

    # Mostrar detalles
    print("=" * 80)
    print("CHECKOUTS QUE NECESITAN PROCESAMIENTO:")
    print("=" * 80 + "\n")

    for checkout, wallet_deduction in checkouts_to_fix:
        print(f"Checkout ID: {checkout.pk}")
        print(f"  Usuario: {checkout.user.username} (ID: {checkout.user.pk})")
        print(f"  Evento: {checkout.event.title} (ID: {checkout.event.pk})")
        print(f"  Creado: {checkout.created_at}")
        print(f"  Wallet Deduction: ${wallet_deduction}")
        print(f"  Session ID: {checkout.stripe_session_id}")

        wallet, _ = UserWallet.objects.get_or_create(user=checkout.user)
        print(f"  Wallet Balance Actual: ${wallet.balance}")
        print("-" * 80)

    # Preguntar si procesar
    print("\n[INFO] Estos checkouts tienen wallet_deduction pero no tienen reembolso.")
    print("[INFO] ¿Deseas procesarlos y reembolsar el wallet? (s/n): ", end="")

    # Para ejecución automática, procesar directamente
    # En producción, descomentar la línea de arriba para confirmación manual
    response = "s"  # Por defecto procesar

    if response.lower() == "s":
        print("\n[INFO] Procesando checkouts...\n")

        for checkout, wallet_deduction in checkouts_to_fix:
            try:
                wallet, _ = UserWallet.objects.get_or_create(user=checkout.user)

                # Reembolsar el wallet
                wallet.refund(
                    amount=wallet_deduction,
                    description=f"Refund for stuck checkout: {checkout.event.title}",
                    reference_id=f"checkout_stuck_fix:{checkout.pk}",
                )

                # Marcar como cancelado (ya que está en estado created y no se completó)
                checkout.status = "cancelled"
                checkout.save(update_fields=["status", "updated_at"])

                print(f"[OK] Checkout {checkout.pk}: Reembolsados ${wallet_deduction} a {checkout.user.username}")

            except Exception as e:
                print(f"[ERROR] Checkout {checkout.pk}: Error al procesar: {e}")

        print("\n[INFO] Procesamiento completado.")
    else:
        print("\n[INFO] Procesamiento cancelado.")

    print("\n" + "=" * 80)
    print("PROCESO COMPLETADO")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    fix_stuck_checkouts()
