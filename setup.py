#!/usr/bin/env python
"""
Script de configuración inicial para NSC Admin Dashboard
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Ejecuta un comando y muestra el resultado"""
    print(f"\n🔄 {description}...")
    try:
        # Convert string command to list for security
        if isinstance(command, str):
            command = command.split()
        
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False


def create_env_file():
    """Crea el archivo .env desde env.example"""
    env_example = Path("env.example")
    env_file = Path(".env")

    if env_file.exists():
        print("📄 El archivo .env ya existe")
        return True

    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Archivo .env creado desde env.example")
        return True
    else:
        # Crear archivo .env básico si no existe env.example
        env_content = """# Django Settings
SECRET_KEY=django-insecure-change-this-in-production-key-for-development-only
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (for production)
DB_NAME=nsc_admin
DB_USER=postgres
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432

# Email Settings (for production)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
"""
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ Archivo .env creado con configuración básica")
        return True


def create_directories():
    """Crea directorios necesarios"""
    directories = [
        "logs",
        "media",
        "media/products",
        "media/categories",
        "media/customers/avatars",
        "media/users/avatars",
        "staticfiles",
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

    print("✅ Directorios creados")


def main():
    """Función principal de configuración"""
    print("🚀 Configurando NSC Admin Dashboard...")

    # Verificar Python
    if sys.version_info < (3, 8):
        print("❌ Se requiere Python 3.8 o superior")
        sys.exit(1)

    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")

    # Crear archivo .env
    if not create_env_file():
        print("❌ No se pudo crear el archivo .env")
        sys.exit(1)

    # Crear directorios
    create_directories()

    # Instalar dependencias
    if not run_command("pip install -r requirements.txt", "Instalando dependencias"):
        print("❌ Error instalando dependencias")
        sys.exit(1)

    # Ejecutar migraciones
    if not run_command("python manage.py makemigrations", "Creando migraciones"):
        print("❌ Error creando migraciones")
        sys.exit(1)

    if not run_command("python manage.py migrate", "Ejecutando migraciones"):
        print("❌ Error ejecutando migraciones")
        sys.exit(1)

    # Crear superusuario
    print("\n👤 Creando superusuario...")
    print("Por favor, ingresa los datos del superusuario:")
    run_command("python manage.py createsuperuser", "Creando superusuario")

    # Recopilar archivos estáticos
    if not run_command("python manage.py collectstatic --noinput", "Recopilando archivos estáticos"):
        print("⚠️  Advertencia: No se pudieron recopilar archivos estáticos")

    print("\n🎉 ¡Configuración completada!")
    print("\n📋 Próximos pasos:")
    print("1. Edita el archivo .env con tus configuraciones")
    print("2. Ejecuta: python manage.py runserver")
    print("3. Visita: http://127.0.0.1:8000")
    print("4. Inicia sesión con el superusuario creado")

    print("\n🔧 Comandos útiles:")
    print("- python manage.py runserver          # Iniciar servidor de desarrollo")
    print("- python manage.py createsuperuser   # Crear otro superusuario")
    print("- python manage.py shell             # Abrir shell de Django")
    print("- python manage.py test              # Ejecutar tests")


if __name__ == "__main__":
    main()
