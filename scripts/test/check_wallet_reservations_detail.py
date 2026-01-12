"""
Script para revisar en detalle las reservas de wallet.
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


def check_wallet_reservations_detail():
    """Revisa en detalle las reservas de wallet"""
    print("\n" + "=" * 80)
    print("REVISION DETALLADA DE RESERVAS DE WALLET")
    print("=" * 80 + "\n")

    # Buscar todas las transacciones de pago con referencia "event_checkout_pending"
    reservations = WalletTransaction.objects.filter(
        transaction_type="payment",
        reference_id__contains="event_checkout_pending"
    ).order_by("-created_at")

    print(f"[INFO] Total de reservas encontradas: {reservations.count()}\n")

    for reservation in reservations:
        wallet = reservation.wallet
        reference_id = reservation.reference_id

        print("=" * 80)
        print(f"Reserva ID: {reservation.pk}")
        print(f"  Usuario: {wallet.user.username} (ID: {wallet.user.pk})")
        print(f"  Monto: ${reservation.amount}")
        print(f"  Fecha: {reservation.created_at}")
        print(f"  Reference: {reference_id}")
        print(f"  Balance actual: ${wallet.balance}")
        print(f"  Pending actual: ${wallet.pending_balance}")

        # Extraer event_id
        try:
            event_id = int(reference_id.split(":")[-1])
            print(f"  Event ID: {event_id}")
        except (ValueError, IndexError):
            print(f"  [ERROR] No se pudo extraer event_id")
            print("-" * 80)
            continue

        # Buscar checkouts
        checkouts = StripeEventCheckout.objects.filter(
            user=wallet.user,
            event_id=event_id
        ).order_by("-created_at")

        print(f"  Checkouts encontrados: {checkouts.count()}")

        for checkout in checkouts[:3]:  # Mostrar los primeros 3
            print(f"    - Checkout {checkout.pk}:")
            print(f"      Status: {checkout.status}")
            print(f"      Creado: {checkout.created_at}")
            print(f"      Session ID: {checkout.stripe_session_id}")

            breakdown = checkout.breakdown or {}
            wallet_deduction_str = breakdown.get("wallet_deduction", "0")
            try:
                wallet_deduction = Decimal(str(wallet_deduction_str))
                print(f"      Wallet deduction: ${wallet_deduction}")
            except:
                print(f"      Wallet deduction: N/A")

        # Buscar transacciones relacionadas
        print(f"\n  Transacciones relacionadas:")

        # Buscar confirmaciones
        confirmations = WalletTransaction.objects.filter(
            wallet=wallet,
            transaction_type="payment",
            reference_id__contains="checkout_confirmed",
            created_at__gte=reservation.created_at
        ).order_by("-created_at")

        print(f"    Confirmaciones: {confirmations.count()}")
        for conf in confirmations[:2]:
            print(f"      - ${conf.amount} el {conf.created_at}: {conf.reference_id}")

        # Buscar liberaciones
        releases = WalletTransaction.objects.filter(
            wallet=wallet,
            transaction_type="refund",
            reference_id__contains="checkout_",
            created_at__gte=reservation.created_at
        ).order_by("-created_at")

        print(f"    Liberaciones: {releases.count()}")
        for rel in releases[:2]:
            print(f"      - ${rel.amount} el {rel.created_at}: {rel.reference_id}")

        # Verificar si la reserva debería estar liberada
        if checkouts.exists():
            latest_checkout = checkouts.first()
            if latest_checkout.status in ["cancelled", "expired"]:
                # Debería haberse liberado
                released = releases.filter(
                    reference_id__contains=f"checkout_{latest_checkout.status}:{latest_checkout.pk}"
                ).exists()

                if not released:
                    print(f"\n  [ADVERTENCIA] Checkout {latest_checkout.pk} está {latest_checkout.status} pero NO se liberó la reserva")
                    print(f"  [ACCION] Esta reserva necesita ser liberada manualmente")
                else:
                    print(f"\n  [OK] La reserva fue liberada correctamente")
            elif latest_checkout.status == "paid":
                # Debería haberse confirmado
                confirmed = confirmations.filter(
                    reference_id__contains=f"checkout_confirmed:{latest_checkout.pk}"
                ).exists()

                if not confirmed:
                    print(f"\n  [ADVERTENCIA] Checkout {latest_checkout.pk} está pagado pero NO se confirmó el wallet")
                    print(f"  [ACCION] Esta reserva necesita ser confirmada manualmente")
                else:
                    print(f"\n  [OK] La reserva fue confirmada correctamente")
            elif latest_checkout.status in ["created", "registered"]:
                # Aún está pendiente, esto es normal
                print(f"\n  [INFO] Checkout {latest_checkout.pk} aún está pendiente (status: {latest_checkout.status})")
        else:
            print(f"\n  [ADVERTENCIA] No se encontró checkout asociado")
            print(f"  [ACCION] Esta reserva probablemente necesita ser liberada")

        print("-" * 80)

    print("\n" + "=" * 80)
    print("REVISION COMPLETADA")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    check_wallet_reservations_detail()
