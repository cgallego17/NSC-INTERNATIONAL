#!/usr/bin/env python
"""
Script de configuración rápida para NSC Admin Dashboard
Usa configuración simplificada sin variables de entorno
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Ejecuta un comando y muestra el resultado"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def create_directories():
    """Crea directorios necesarios"""
    directories = [
        "logs",
        "media",
        "media/products",
        "media/categories",
        "media/customers/avatars",
        "media/users/avatars",
        "staticfiles"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directorios creados")

def setup_simple_config():
    """Configura el proyecto con settings simplificados"""
    # Copiar settings simplificado
    settings_file = Path("nsc_admin/settings.py")
    settings_simple = Path("nsc_admin/settings_simple.py")
    
    if settings_simple.exists():
        shutil.copy(settings_simple, settings_file)
        print("✅ Configuración simplificada aplicada")
        return True
    else:
        print("❌ No se encontró settings_simple.py")
        return False

def main():
    """Función principal de configuración rápida"""
    print("🚀 Configuración rápida de NSC Admin Dashboard...")
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print("❌ Se requiere Python 3.8 o superior")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    
    # Configurar con settings simplificados
    if not setup_simple_config():
        print("❌ No se pudo configurar el proyecto")
        sys.exit(1)
    
    # Crear directorios
    create_directories()
    
    # Instalar dependencias básicas
    basic_requirements = [
        "Django==4.2.7",
        "Pillow==10.1.0",
        "whitenoise==6.6.0",
        "django-crispy-forms==2.1",
        "crispy-bootstrap5==0.7"
    ]
    
    print("\n🔄 Instalando dependencias básicas...")
    for req in basic_requirements:
        if not run_command(f"pip install {req}", f"Instalando {req.split('==')[0]}"):
            print(f"⚠️  Advertencia: No se pudo instalar {req}")
    
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
    
    print("\n🎉 ¡Configuración rápida completada!")
    print("\n📋 Próximos pasos:")
    print("1. Ejecuta: python manage.py runserver")
    print("2. Visita: http://127.0.0.1:8000")
    print("3. Inicia sesión con el superusuario creado")
    
    print("\n🔧 Comandos útiles:")
    print("- python manage.py runserver          # Iniciar servidor de desarrollo")
    print("- python manage.py createsuperuser   # Crear otro superusuario")
    print("- python manage.py shell             # Abrir shell de Django")
    print("- python manage.py test              # Ejecutar tests")

if __name__ == "__main__":
    main()

