"""
Script para limpiar reservas duplicadas de wallet y verificar integridad.
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


def fix_duplicate_wallet_reservations():
    """Limpia reservas duplicadas y verifica integridad"""
    print("\n" + "=" * 80)
    print("LIMPIANDO RESERVAS DUPLICADAS DE WALLET")
    print("=" * 80 + "\n")

    # Buscar todos los wallets con pending_balance > 0
    wallets_with_pending = UserWallet.objects.filter(pending_balance__gt=0)

    print(f"[INFO] Wallets con pending balance: {wallets_with_pending.count()}\n")

    for wallet in wallets_with_pending:
        print("=" * 80)
        print(f"Wallet de {wallet.user.username} (ID: {wallet.user.pk})")
        print(f"  Balance: ${wallet.balance}")
        print(f"  Pending: ${wallet.pending_balance}")
        print(f"  Available: ${wallet.available_balance}")

        # Buscar todas las reservas activas (transacciones de pago con event_checkout_pending)
        reservations = WalletTransaction.objects.filter(
            wallet=wallet,
            transaction_type="payment",
            reference_id__contains="event_checkout_pending"
        ).order_by("-created_at")

        print(f"\n  Reservas encontradas: {reservations.count()}")
        total_reserved = Decimal("0.00")

        for reservation in reservations:
            print(f"    - Reserva {reservation.pk}: ${reservation.amount} el {reservation.created_at}")
            print(f"      Reference: {reservation.reference_id}")

            # Verificar si hay liberación o confirmación
            try:
                event_id = int(reservation.reference_id.split(":")[-1])
            except:
                event_id = None

            if event_id:
                # Buscar checkouts relacionados
                checkouts = StripeEventCheckout.objects.filter(
                    user=wallet.user,
                    event_id=event_id,
                    created_at__gte=reservation.created_at - timedelta(minutes=5),
                    created_at__lte=reservation.created_at + timedelta(minutes=5)
                ).order_by("-created_at")

                if checkouts.exists():
                    latest_checkout = checkouts.first()
                    print(f"      Checkout asociado: {latest_checkout.pk} (status: {latest_checkout.status})")

                    # Verificar si fue liberada o confirmada
                    released = WalletTransaction.objects.filter(
                        wallet=wallet,
                        transaction_type="refund",
                        reference_id__contains=f"checkout_{latest_checkout.status}:{latest_checkout.pk}",
                        created_at__gte=reservation.created_at
                    ).exists()

                    confirmed = WalletTransaction.objects.filter(
                        wallet=wallet,
                        transaction_type="payment",
                        reference_id__contains=f"checkout_confirmed:{latest_checkout.pk}",
                        created_at__gte=reservation.created_at
                    ).exists()

                    if latest_checkout.status in ["cancelled", "expired"]:
                        if not released:
                            print(f"      [ADVERTENCIA] Debería estar liberada pero no lo está")
                        else:
                            print(f"      [OK] Fue liberada correctamente")
                            total_reserved += reservation.amount  # Esta cuenta como reservada aunque fue liberada
                    elif latest_checkout.status == "paid":
                        if not confirmed:
                            print(f"      [ADVERTENCIA] Debería estar confirmada pero no lo está")
                        else:
                            print(f"      [OK] Fue confirmada correctamente")
                            total_reserved += reservation.amount  # Esta cuenta como reservada aunque fue confirmada
                    elif latest_checkout.status in ["created", "registered"]:
                        print(f"      [INFO] Checkout aún pendiente")
                        total_reserved += reservation.amount
                else:
                    print(f"      [ADVERTENCIA] No se encontró checkout asociado")
                    total_reserved += reservation.amount

        print(f"\n  Total reservado según transacciones: ${total_reserved}")
        print(f"  Pending balance en wallet: ${wallet.pending_balance}")

        difference = wallet.pending_balance - total_reserved
        if abs(difference) > Decimal("0.01"):
            print(f"  [ADVERTENCIA] Diferencia: ${difference}")
            print(f"  [ACCION] El pending_balance no coincide con las reservas")

            # Ajustar el pending_balance
            print(f"\n  ¿Ajustar pending_balance a ${total_reserved}? (s/n): ", end="")
            response = "s"

            if response.lower() == "s":
                wallet.pending_balance = total_reserved
                wallet.save(update_fields=["pending_balance", "updated_at"])
                print(f"  [OK] Pending balance ajustado a ${total_reserved}")

        print("-" * 80)

    print("\n" + "=" * 80)
    print("PROCESO COMPLETADO")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    fix_duplicate_wallet_reservations()
