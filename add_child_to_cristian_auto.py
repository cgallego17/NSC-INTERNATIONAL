"""
Script para agregar un hijo al usuario Cristian Gallego (versión automática)
Uso: python add_child_to_cristian_auto.py "Nombre" "Apellido" ["Segundo Apellido"]
"""

import os
import django
import secrets
import string
import sys

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from django.contrib.auth.models import User
from apps.accounts.models import UserProfile, Player, PlayerParent


def create_child_for_cristian(
    first_name, last_name, last_name2=None, relationship="guardian", is_primary=False
):
    """Crear un nuevo hijo para Cristian Gallego"""

    # Buscar el usuario Cristian Gallego
    try:
        parent_user = User.objects.filter(
            first_name__icontains="Cristian", last_name__icontains="Gallego"
        ).first()

        if not parent_user:
            parent_user = User.objects.filter(last_name__icontains="Gallego").first()

        if not parent_user:
            print("[ERROR] No se encontro el usuario 'Cristian Gallego'")
            return False

        print(
            f"[OK] Usuario encontrado: {parent_user.get_full_name()} ({parent_user.username})"
        )

        # Verificar que sea padre
        try:
            profile = parent_user.profile
            if not profile.is_parent:
                print(f"[INFO] Cambiando tipo de usuario a 'parent'...")
                profile.user_type = "parent"
                profile.save()
        except UserProfile.DoesNotExist:
            print("[INFO] Creando perfil como 'parent'...")
            profile = UserProfile.objects.create(user=parent_user, user_type="parent")

        # Contar hijos actuales
        current_children = PlayerParent.objects.filter(parent=parent_user).count()
        print(f"[INFO] Hijos actuales: {current_children}")

        # Generar username único
        base_username = f"{first_name.lower()}.{last_name.lower()}"
        if last_name2:
            base_username = (
                f"{first_name.lower()}.{last_name.lower()}.{last_name2.lower()}"
            )

        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        # Generar contraseña aleatoria
        alphabet = string.ascii_letters + string.digits
        password = "".join(secrets.choice(alphabet) for i in range(20))

        # Combinar apellidos
        if last_name2:
            full_last_name = f"{last_name} {last_name2}"
        else:
            full_last_name = last_name

        # Email temporal
        email = f"{username}@nsc-temp.local"

        print(f"[INFO] Creando usuario: {username}")

        # Crear usuario INACTIVO
        child_user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=full_last_name,
            is_active=False,
        )

        print("[OK] Usuario creado")

        # Crear perfil de usuario
        child_profile = UserProfile.objects.create(
            user=child_user,
            user_type="player",
        )

        print("[OK] Perfil de usuario creado")

        # Crear perfil de jugador
        player = Player.objects.create(
            user=child_user,
            team=None,
            jersey_number=None,
        )

        print("[OK] Perfil de jugador creado")

        # Crear relación padre-jugador
        player_parent = PlayerParent.objects.create(
            parent=parent_user,
            player=player,
            relationship=relationship,
            is_primary=is_primary,
        )

        print("[OK] Relacion padre-jugador creada")

        print("\n" + "=" * 50)
        print("[OK] JUGADOR REGISTRADO EXITOSAMENTE")
        print("=" * 50)
        print(f"Nombre: {child_user.get_full_name()}")
        print(f"Username: {child_user.username}")
        print(f"Padre: {parent_user.get_full_name()}")
        print(f"Relacion: {player_parent.get_relationship_display()}")
        print(f"Contacto principal: {'Si' if is_primary else 'No'}")
        print(
            f"\nTotal de hijos de {parent_user.get_full_name()}: {PlayerParent.objects.filter(parent=parent_user).count()}"
        )

        return True

    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            'Uso: python add_child_to_cristian_auto.py "Nombre" "Apellido" ["Segundo Apellido"] [relationship] [is_primary]'
        )
        print(
            'Ejemplo: python add_child_to_cristian_auto.py "Juan" "Gallego" "Perez" "father" "true"'
        )
        sys.exit(1)

    first_name = sys.argv[1]
    last_name = sys.argv[2]
    last_name2 = sys.argv[3] if len(sys.argv) > 3 else None
    relationship = sys.argv[4] if len(sys.argv) > 4 else "guardian"
    is_primary = sys.argv[5].lower() == "true" if len(sys.argv) > 5 else False

    create_child_for_cristian(
        first_name, last_name, last_name2, relationship, is_primary
    )







