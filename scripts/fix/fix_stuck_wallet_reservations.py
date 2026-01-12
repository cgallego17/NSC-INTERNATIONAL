"""
Script para liberar reservas de wallet que quedaron colgadas.
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


def fix_stuck_wallet_reservations():
    """Libera reservas de wallet que quedaron colgadas"""
    print("\n" + "=" * 80)
    print("LIBERANDO RESERVAS DE WALLET COLGADAS")
    print("=" * 80 + "\n")

    # Buscar transacciones de pago con referencia "event_checkout_pending"
    stuck_reservations = WalletTransaction.objects.filter(
        transaction_type="payment",
        reference_id__contains="event_checkout_pending"
    ).order_by("-created_at")

    print(f"[INFO] Transacciones de reserva encontradas: {stuck_reservations.count()}\n")

    if stuck_reservations.count() == 0:
        print("[INFO] No hay reservas colgadas.")
        return

    # Agrupar por wallet y verificar si hay checkouts asociados
    reservations_to_release = []

    for reservation in stuck_reservations:
        wallet = reservation.wallet
        reference_id = reservation.reference_id

        # Extraer event_id del reference_id (formato: event_checkout_pending:event_id)
        try:
            event_id = int(reference_id.split(":")[-1])
        except (ValueError, IndexError):
            print(f"[WARNING] No se pudo extraer event_id de: {reference_id}")
            continue

        # Buscar checkouts para este evento y usuario
        checkouts = StripeEventCheckout.objects.filter(
            user=wallet.user,
            event_id=event_id,
            created_at__gte=reservation.created_at - timedelta(hours=1),
            created_at__lte=reservation.created_at + timedelta(hours=1)
        ).order_by("-created_at")

        # Verificar si el checkout está pagado, cancelado o expirado
        should_release = False
        checkout_status = None

        if checkouts.exists():
            latest_checkout = checkouts.first()
            checkout_status = latest_checkout.status

            # Si está pagado, cancelado o expirado, debería haberse liberado o confirmado
            if latest_checkout.status in ["paid"]:
                # Si está pagado, debería haberse confirmado, no liberado
                # Verificar si hay una transacción de confirmación
                confirmed = WalletTransaction.objects.filter(
                    wallet=wallet,
                    transaction_type="payment",
                    reference_id__contains=f"checkout_confirmed:{latest_checkout.pk}",
                    created_at__gte=reservation.created_at
                ).exists()

                if not confirmed:
                    print(f"[WARNING] Checkout {latest_checkout.pk} está pagado pero no se confirmó el wallet")
            elif latest_checkout.status in ["cancelled", "expired"]:
                # Debería haberse liberado
                released = WalletTransaction.objects.filter(
                    wallet=wallet,
                    transaction_type="refund",
                    reference_id__contains=f"checkout_{latest_checkout.status}:{latest_checkout.pk}",
                    created_at__gte=reservation.created_at
                ).exists()

                if not released:
                    should_release = True
                    print(f"[INFO] Checkout {latest_checkout.pk} está {latest_checkout.status} pero no se liberó la reserva")
        else:
            # No hay checkout asociado, probablemente se canceló antes de crear el checkout
            # O el checkout fue eliminado
            should_release = True
            print(f"[INFO] No se encontró checkout para reserva {reservation.pk}")

        if should_release:
            reservations_to_release.append((reservation, wallet, reservation.amount))

    print(f"\n[INFO] Reservas que necesitan liberación: {len(reservations_to_release)}\n")

    if reservations_to_release:
        print("=" * 80)
        print("RESERVAS A LIBERAR:")
        print("=" * 80 + "\n")

        for reservation, wallet, amount in reservations_to_release:
            print(f"Reserva ID: {reservation.pk}")
            print(f"  Usuario: {wallet.user.username} (ID: {wallet.user.pk})")
            print(f"  Monto: ${amount}")
            print(f"  Fecha: {reservation.created_at}")
            print(f"  Reference: {reservation.reference_id}")
            print(f"  Balance actual: ${wallet.balance}")
            print(f"  Pending actual: ${wallet.pending_balance}")
            print("-" * 80)

        print("\n[INFO] ¿Deseas liberar estas reservas? (s/n): ", end="")
        response = "s"  # Por defecto procesar

        if response.lower() == "s":
            print("\n[INFO] Liberando reservas...\n")

            for reservation, wallet, amount in reservations_to_release:
                try:
                    # Liberar la reserva
                    wallet.release_reserved_funds(
                        amount=amount,
                        description=f"Liberación de reserva colgada: {reservation.description}",
                        reference_id=f"stuck_reservation_fix:{reservation.pk}",
                    )

                    print(f"[OK] Reserva {reservation.pk}: Liberados ${amount} para {wallet.user.username}")

                except Exception as e:
                    print(f"[ERROR] Reserva {reservation.pk}: Error al liberar: {e}")

            print("\n[INFO] Procesamiento completado.")
        else:
            print("\n[INFO] Procesamiento cancelado.")

    print("\n" + "=" * 80)
    print("PROCESO COMPLETADO")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    fix_stuck_wallet_reservations()
