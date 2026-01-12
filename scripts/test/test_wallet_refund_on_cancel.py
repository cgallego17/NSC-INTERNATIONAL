"""
Script para probar el reembolso del wallet cuando se cancela un checkout de Stripe.
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
from apps.accounts.models import UserWallet, WalletTransaction, StripeEventCheckout
from apps.events.models import Event


def test_wallet_refund_on_cancel():
    """Test que verifica el reembolso del wallet al cancelar un checkout"""
    print("\n" + "=" * 80)
    print("TEST: Wallet Refund on Checkout Cancel")
    print("=" * 80 + "\n")

    # Buscar un usuario de prueba
    user = User.objects.filter(is_superuser=False).first()
    if not user:
        print("[ERROR] No se encontró un usuario para probar")
        return

    print(f"[INFO] Usuario de prueba: {user.username} (ID: {user.pk})")

    # Obtener o crear wallet
    wallet, created = UserWallet.objects.get_or_create(user=user)
    if created:
        print(f"[INFO] Wallet creado para usuario {user.username}")
    else:
        print(f"[INFO] Wallet existente para usuario {user.username}")

    # Balance inicial
    initial_balance = wallet.balance
    print(f"[INFO] Balance inicial del wallet: ${initial_balance}")

    # Agregar fondos de prueba si el balance es 0
    if initial_balance == 0:
        test_amount = Decimal("100.00")
        wallet.balance = test_amount
        wallet.save()
        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type="deposit",
            amount=test_amount,
            description="Test deposit",
            balance_after=test_amount,
        )
        print(f"[INFO] Agregados ${test_amount} al wallet para prueba")
        initial_balance = test_amount

    # Buscar un evento de prueba
    event = Event.objects.filter(status="active").first()
    if not event:
        event = Event.objects.first()
    if not event:
        print("[ERROR] No se encontró un evento para probar")
        return

    print(f"[INFO] Evento de prueba: {event.title} (ID: {event.pk})")

    # Simular un checkout con wallet deduction
    wallet_deduction = Decimal("50.00")
    print(f"\n[INFO] Simulando checkout con deducción de wallet: ${wallet_deduction}")

    # Crear un checkout de prueba
    checkout = StripeEventCheckout.objects.create(
        user=user,
        event=event,
        stripe_session_id=f"test_session_{user.pk}_{event.pk}",
        payment_mode="now",
        discount_percent=0,
        player_ids=[],
        hotel_cart_snapshot={},
        breakdown={
            "players_total": "0.00",
            "subtotal": "100.00",
            "total_before_discount": "100.00",
            "discount_percent": 0,
            "wallet_deduction": str(wallet_deduction),
            "total": "50.00",
        },
        amount_total=Decimal("50.00"),
        status="created",
    )
    print(f"[INFO] Checkout creado: ID {checkout.pk}")

    # Descontar del wallet (simular el proceso de checkout)
    try:
        wallet.deduct_funds(
            amount=wallet_deduction,
            description=f"Test payment for event: {event.title}",
            reference_id=f"test_checkout:{checkout.pk}",
        )
        print(f"[INFO] Wallet descontado: ${wallet_deduction}")
        print(f"[INFO] Balance después de deducción: ${wallet.balance}")
    except ValueError as e:
        print(f"[ERROR] Error al descontar wallet: {e}")
        checkout.delete()
        return

    # Verificar que el checkout tiene wallet_deduction en breakdown
    checkout.refresh_from_db()
    breakdown = checkout.breakdown or {}
    stored_wallet_deduction = Decimal(str(breakdown.get("wallet_deduction", "0")))
    print(f"\n[INFO] Wallet deduction en breakdown: ${stored_wallet_deduction}")

    if stored_wallet_deduction != wallet_deduction:
        print(
            f"[ERROR] Wallet deduction no coincide! Esperado: ${wallet_deduction}, Encontrado: ${stored_wallet_deduction}"
        )
        checkout.delete()
        return

    # Simular cancelación
    print("\n[INFO] Simulando cancelación del checkout...")
    balance_before_refund = wallet.balance

    # Verificar breakdown
    breakdown = checkout.breakdown or {}
    wallet_deduction_str = breakdown.get("wallet_deduction", "0")
    wallet_deduction_to_refund = Decimal(str(wallet_deduction_str))

    if wallet_deduction_to_refund > 0:
        try:
            wallet.refund(
                amount=wallet_deduction_to_refund,
                description=f"Refund for cancelled checkout: {event.title}",
                reference_id=f"checkout_cancel:{checkout.pk}",
            )
            print(f"[OK] Wallet reembolsado: ${wallet_deduction_to_refund}")
            print(f"[INFO] Balance después de reembolso: ${wallet.balance}")

            # Verificar que el balance se restauró correctamente
            expected_balance = balance_before_refund + wallet_deduction_to_refund
            if abs(wallet.balance - expected_balance) < Decimal("0.01"):
                print(f"[OK] Balance correcto después del reembolso")
            else:
                print(
                    f"[ERROR] Balance incorrecto! Esperado: ${expected_balance}, Actual: ${wallet.balance}"
                )
        except Exception as e:
            print(f"[ERROR] Error al reembolsar wallet: {e}")
    else:
        print("[WARNING] No se encontró wallet_deduction en el breakdown")

    # Marcar checkout como cancelado
    checkout.status = "cancelled"
    checkout.save(update_fields=["status", "updated_at"])
    print(f"[INFO] Checkout marcado como cancelado")

    # Verificar transacciones
    refund_transactions = WalletTransaction.objects.filter(
        wallet=wallet, transaction_type="refund"
    ).order_by("-created_at")
    if refund_transactions.exists():
        latest_refund = refund_transactions.first()
        print(f"\n[INFO] Última transacción de reembolso:")
        print(f"  - Tipo: {latest_refund.transaction_type}")
        print(f"  - Monto: ${latest_refund.amount}")
        print(f"  - Descripción: {latest_refund.description}")
        print(f"  - Balance después: ${latest_refund.balance_after}")
    else:
        print("[WARNING] No se encontraron transacciones de reembolso")

    # Limpiar
    checkout.delete()
    print(f"\n[INFO] Checkout de prueba eliminado")

    # Restaurar balance inicial si es necesario
    if wallet.balance != initial_balance:
        difference = wallet.balance - initial_balance
        if difference > 0:
            wallet.balance = initial_balance
            wallet.save()
            print(f"[INFO] Balance restaurado a ${initial_balance}")

    print("\n" + "=" * 80)
    print("TEST COMPLETADO")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    test_wallet_refund_on_cancel()
