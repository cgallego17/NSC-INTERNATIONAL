"""
Script para liberar la reserva colgada del usuario cristian.gallego.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from apps.accounts.models import WalletTransaction, UserWallet
from django.contrib.auth.models import User

user = User.objects.get(username="cristian.gallego")
wallet, _ = UserWallet.objects.get_or_create(user=user)

print(f"Wallet de {user.username}:")
print(f"  Balance: ${wallet.balance}")
print(f"  Pending: ${wallet.pending_balance}")
print(f"  Available: ${wallet.available_balance}")

# Buscar la reserva 16
reservation_16 = WalletTransaction.objects.get(pk=16)
print(f"\nReserva 16:")
print(f"  Monto: ${reservation_16.amount}")
print(f"  Fecha: {reservation_16.created_at}")
print(f"  Reference: {reservation_16.reference_id}")

# Verificar si ya fue liberada
releases = WalletTransaction.objects.filter(
    wallet=wallet,
    transaction_type="refund",
    reference_id__contains="checkout_cancel:73",
    created_at__gte=reservation_16.created_at
)

if releases.exists():
    print(f"\n[INFO] La reserva 16 ya tiene una transacción de liberación")
    print(f"[INFO] Pero el pending_balance no se actualizó correctamente")

    # Calcular el pending correcto
    # Solo contar reservas que no tienen liberación o confirmación
    all_reservations = WalletTransaction.objects.filter(
        wallet=wallet,
        transaction_type="payment",
        reference_id__contains="event_checkout_pending"
    )

    active_count = 0
    total_active = 0

    for res in all_reservations:
        # Verificar si tiene liberación o confirmación
        has_release = WalletTransaction.objects.filter(
            wallet=wallet,
            transaction_type="refund",
            created_at__gte=res.created_at,
            amount=res.amount
        ).exists()

        has_confirm = WalletTransaction.objects.filter(
            wallet=wallet,
            transaction_type="payment",
            reference_id__contains="checkout_confirmed",
            created_at__gte=res.created_at,
            amount=res.amount
        ).exists()

        if not has_release and not has_confirm:
            active_count += 1
            total_active += res.amount
            print(f"  Reserva activa: {res.pk} - ${res.amount}")

    print(f"\n[INFO] Reservas activas: {active_count}")
    print(f"[INFO] Total activo: ${total_active}")

    # Ajustar pending_balance
    if wallet.pending_balance != total_active:
        print(f"\n[INFO] Ajustando pending_balance de ${wallet.pending_balance} a ${total_active}")
        wallet.pending_balance = total_active
        wallet.save(update_fields=["pending_balance", "updated_at"])
        print(f"[OK] Pending balance actualizado")
    else:
        print(f"\n[INFO] Pending balance ya está correcto")
else:
    print(f"\n[INFO] La reserva 16 NO fue liberada")
    print(f"[INFO] Liberando ahora...")

    wallet.release_reserved_funds(
        amount=reservation_16.amount,
        description="Liberación de reserva colgada (checkout 73 cancelado)",
        reference_id="stuck_reservation_fix:16",
    )

    print(f"[OK] Reserva liberada")

print(f"\nEstado final:")
print(f"  Balance: ${wallet.balance}")
print(f"  Pending: ${wallet.pending_balance}")
print(f"  Available: ${wallet.available_balance}")
