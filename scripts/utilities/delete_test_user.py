"""
Script para eliminar un usuario de prueba y todos sus datos relacionados
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nsc_admin.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.accounts.models import (
    Order,
    UserWallet,
    WalletTransaction,
    StripeEventCheckout,
    UserProfile,
    Player,
    PlayerParent,
)

User = get_user_model()

# Usuario a eliminar
username = 'spectator_checkout_test_20260111053401275157'
email = 'spectator_checkout_test_20260111053401275157@example.com'

print("=" * 70)
print("ELIMINACION DE USUARIO DE PRUEBA")
print("=" * 70)

try:
    # Buscar usuario por username o email
    user = None
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            print(f"\n[ERROR] Usuario no encontrado: {username} / {email}")
            sys.exit(1)

    print(f"\n[OK] Usuario encontrado:")
    print(f"   ID: {user.id}")
    print(f"   Username: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Nombre: {user.get_full_name()}")

    # Contar datos relacionados
    print(f"\n[INFO] Datos relacionados encontrados:")

    orders_count = Order.objects.filter(user=user).count()
    print(f"   - Ordenes: {orders_count}")

    checkouts_count = StripeEventCheckout.objects.filter(user=user).count()
    print(f"   - Stripe Checkouts: {checkouts_count}")

    wallets_count = UserWallet.objects.filter(user=user).count()
    print(f"   - Wallets: {wallets_count}")

    wallet_transactions_count = 0
    if wallets_count > 0:
        wallet = UserWallet.objects.filter(user=user).first()
        wallet_transactions_count = WalletTransaction.objects.filter(wallet=wallet).count()
        print(f"   - Transacciones de Wallet: {wallet_transactions_count}")

    try:
        profile = user.profile
        print(f"   - Perfil: [OK]")
    except:
        print(f"   - Perfil: [NO]")

    try:
        player = user.player_profile
        print(f"   - Perfil de Jugador: [OK]")
        player_parents_count = PlayerParent.objects.filter(parent=user).count()
        print(f"   - Relaciones como Padre: {player_parents_count}")
    except:
        print(f"   - Perfil de Jugador: [NO]")

    # Confirmar eliminación
    print(f"\n[WARNING] ADVERTENCIA: Se eliminaran TODOS los datos relacionados con este usuario.")
    print(f"   Esta accion NO se puede deshacer.")

    response = input("\n¿Continuar con la eliminacion? (escribe 'SI' para confirmar): ")
    if response != 'SI':
        print("\n[ERROR] Eliminacion cancelada.")
        sys.exit(0)

    print(f"\n[INFO] Eliminando datos...")

    # Eliminar en orden específico para evitar problemas de integridad

    # 1. Eliminar transacciones de wallet
    if wallets_count > 0:
        wallet = UserWallet.objects.filter(user=user).first()
        deleted_transactions = WalletTransaction.objects.filter(wallet=wallet).delete()
        print(f"   [OK] Transacciones de wallet eliminadas: {deleted_transactions[0]}")

    # 2. Eliminar wallets
    deleted_wallets = UserWallet.objects.filter(user=user).delete()
    print(f"   [OK] Wallets eliminados: {deleted_wallets[0]}")

    # 3. Eliminar checkouts de Stripe
    deleted_checkouts = StripeEventCheckout.objects.filter(user=user).delete()
    print(f"   [OK] Stripe Checkouts eliminados: {deleted_checkouts[0]}")

    # 4. Eliminar relaciones como padre
    deleted_parents = PlayerParent.objects.filter(parent=user).delete()
    print(f"   [OK] Relaciones como padre eliminadas: {deleted_parents[0]}")

    # 5. Eliminar órdenes
    deleted_orders = Order.objects.filter(user=user).delete()
    print(f"   [OK] Ordenes eliminadas: {deleted_orders[0]}")

    # 6. Eliminar perfil de jugador (si existe)
    try:
        player = user.player_profile
        deleted_player = player.delete()
        print(f"   [OK] Perfil de jugador eliminado")
    except:
        pass

    # 7. Eliminar usuario (esto eliminará automáticamente el perfil por CASCADE)
    user_id = user.id
    user_username = user.username
    user.delete()
    print(f"   [OK] Usuario eliminado: {user_username} (ID: {user_id})")

    print(f"\n[OK] Eliminacion completada exitosamente!")
    print(f"   Usuario '{user_username}' y todos sus datos relacionados han sido eliminados.")

except Exception as e:
    print(f"\n[ERROR] Error durante la eliminacion: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
