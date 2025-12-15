"""
Script para agregar un hijo al usuario Cristian Gallego
"""

import os
import django
import secrets
import string

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from django.contrib.auth.models import User
from apps.accounts.models import UserProfile, Player, PlayerParent


def create_child_for_cristian():
    """Crear un nuevo hijo para Cristian Gallego"""

    # Buscar el usuario Cristian Gallego
    try:
        # Intentar buscar por nombre completo
        parent_user = User.objects.filter(
            first_name__icontains="Cristian", last_name__icontains="Gallego"
        ).first()

        if not parent_user:
            # Intentar buscar solo por apellido
            parent_user = User.objects.filter(last_name__icontains="Gallego").first()

        if not parent_user:
            print("[ERROR] No se encontro el usuario 'Cristian Gallego'")
            print("\nUsuarios disponibles con 'Gallego':")
            for user in User.objects.filter(last_name__icontains="Gallego"):
                print(f"  - {user.get_full_name()} ({user.username})")
            return

        print(
            f"[OK] Usuario encontrado: {parent_user.get_full_name()} ({parent_user.username})"
        )

        # Verificar que sea padre
        try:
            profile = parent_user.profile
            if not profile.is_parent:
                print(
                    f"[ADVERTENCIA] El usuario no es padre. Tipo actual: {profile.user_type}"
                )
                print("¿Deseas cambiar el tipo a 'parent'? (s/n): ", end="")
                response = input().strip().lower()
                if response == "s":
                    profile.user_type = "parent"
                    profile.save()
                    print("[OK] Tipo de usuario cambiado a 'parent'")
                else:
                    print("[ERROR] Operacion cancelada")
                    return
        except UserProfile.DoesNotExist:
            print(
                "[ADVERTENCIA] El usuario no tiene perfil. Creando perfil como 'parent'..."
            )
            profile = UserProfile.objects.create(user=parent_user, user_type="parent")
            print("[OK] Perfil creado")

        # Contar hijos actuales
        current_children = PlayerParent.objects.filter(parent=parent_user).count()
        print(f"[INFO] Hijos actuales: {current_children}")

        # Solicitar información del nuevo hijo
        print("\n" + "=" * 50)
        print("REGISTRO DE NUEVO HIJO/JUGADOR")
        print("=" * 50)

        first_name = input("Nombre del jugador: ").strip()
        if not first_name:
            print("[ERROR] El nombre es requerido")
            return

        last_name = input("Apellido del jugador: ").strip()
        if not last_name:
            print("[ERROR] El apellido es requerido")
            return

        last_name2 = input("Segundo apellido (opcional): ").strip()

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

        print(f"\n[INFO] Creando usuario: {username}")

        # Crear usuario INACTIVO
        child_user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=full_last_name,
            is_active=False,  # Los jugadores no pueden iniciar sesión
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
        relationship = (
            input("\nRelación (father/mother/guardian/other) [guardian]: ")
            .strip()
            .lower()
        )
        if not relationship or relationship not in [
            "father",
            "mother",
            "guardian",
            "other",
        ]:
            relationship = "guardian"

        is_primary_input = input("¿Es contacto principal? (s/n) [n]: ").strip().lower()
        is_primary = is_primary_input == "s"

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

    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    create_child_for_cristian()



