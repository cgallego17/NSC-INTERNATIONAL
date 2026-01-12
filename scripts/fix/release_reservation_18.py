"""
Script para liberar la reserva 18 del usuario cristian.gallego.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from apps.accounts.models import WalletTransaction, UserWallet, StripeEventCheckout
from django.contrib.auth.models import User

user = User.objects.get(username="cristian.gallego")
wallet, _ = UserWallet.objects.get_or_create(user=user)

print(f"Wallet de {user.username}:")
print(f"  Balance: ${wallet.balance}")
print(f"  Pending: ${wallet.pending_balance}")
print(f"  Available: ${wallet.available_balance}")

# Buscar la reserva 18
reservation_18 = WalletTransaction.objects.get(pk=18)
print(f"\nReserva 18:")
print(f"  Monto: ${reservation_18.amount}")
print(f"  Fecha: {reservation_18.created_at}")
print(f"  Reference: {reservation_18.reference_id}")

# Buscar checkout asociado (checkout 74)
checkout_74 = StripeEventCheckout.objects.get(pk=74)
print(f"\nCheckout 74:")
print(f"  Status: {checkout_74.status}")
print(f"  Creado: {checkout_74.created_at}")
print(f"  Session ID: {checkout_74.stripe_session_id}")

# Verificar si ya fue liberada o confirmada
releases = WalletTransaction.objects.filter(
    wallet=wallet,
    transaction_type="refund",
    reference_id__contains="checkout_",
    created_at__gte=reservation_18.created_at
)

confirmations = WalletTransaction.objects.filter(
    wallet=wallet,
    transaction_type="payment",
    reference_id__contains="checkout_confirmed",
    created_at__gte=reservation_18.created_at
)

if releases.exists() or confirmations.exists():
    print(f"\n[INFO] La reserva ya fue procesada")
    if releases.exists():
        print(f"  Liberaciones encontradas: {releases.count()}")
        for r in releases:
            print(f"    - ${r.amount} el {r.created_at}: {r.reference_id}")
    if confirmations.exists():
        print(f"  Confirmaciones encontradas: {confirmations.count()}")
        for c in confirmations:
            print(f"    - ${c.amount} el {c.created_at}: {c.reference_id}")
else:
    print(f"\n[INFO] Liberando la reserva...")

    # Si el checkout está en estado "created", cancelarlo primero
    if checkout_74.status == "created":
        print(f"[INFO] Cancelando checkout 74...")
        checkout_74.status = "cancelled"
        checkout_74.save(update_fields=["status", "updated_at"])
        print(f"[OK] Checkout 74 marcado como cancelado")

    # Liberar la reserva
    wallet.release_reserved_funds(
        amount=reservation_18.amount,
        description=f"Liberación de reserva: {checkout_74.event.title}",
        reference_id=f"checkout_cancel:{checkout_74.pk}",
    )

    print(f"[OK] Reserva liberada: ${reservation_18.amount}")

print(f"\nEstado final:")
print(f"  Balance: ${wallet.balance}")
print(f"  Pending: ${wallet.pending_balance}")
print(f"  Available: ${wallet.available_balance}")
