#!/usr/bin/env python
"""
Script para organizar y preparar las migraciones para subir al servidor
"""
import os
import shutil
from datetime import datetime
from pathlib import Path

MIGRATIONS_DIR = "apps/accounts/migrations"
BACKUP_DIR = "migrations_backups"
UPLOAD_DIR = "migrations_upload"

def get_migration_files():
    """Obtiene la lista de archivos de migración"""
    migrations = []
    if os.path.exists(MIGRATIONS_DIR):
        for file in sorted(os.listdir(MIGRATIONS_DIR)):
            if file.endswith('.py') and file != '__init__.py':
                migrations.append(file)
    return migrations

def create_migrations_backup():
    """Crea un backup de las migraciones actuales"""
    print("1. Creando backup de migraciones...")

    if not os.path.exists(MIGRATIONS_DIR):
        print(f"   [ERROR] Directorio {MIGRATIONS_DIR} no encontrado")
        return None

    # Crear directorio de backups
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"migrations_backup_{timestamp}")
    os.makedirs(backup_path, exist_ok=True)

    try:
        migrations = get_migration_files()
        for migration in migrations:
            src = os.path.join(MIGRATIONS_DIR, migration)
            dst = os.path.join(backup_path, migration)
            shutil.copy(src, dst)

        print(f"   [OK] Backup creado: {backup_path} ({len(migrations)} archivos)")
        return backup_path
    except Exception as e:
        print(f"   [ERROR] Error al crear backup: {e}")
        return None

def create_upload_package():
    """Crea un paquete con todas las migraciones para subir"""
    print("\n2. Creando paquete de migraciones para subir...")

    if not os.path.exists(MIGRATIONS_DIR):
        print(f"   [ERROR] Directorio {MIGRATIONS_DIR} no encontrado")
        return None

    # Crear directorio de upload
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"migrations_upload_{timestamp}"
    package_path = os.path.join(UPLOAD_DIR, package_name)
    os.makedirs(package_path, exist_ok=True)

    try:
        migrations = get_migration_files()

        # Copiar todas las migraciones
        for migration in migrations:
            src = os.path.join(MIGRATIONS_DIR, migration)
            dst = os.path.join(package_path, migration)
            shutil.copy(src, dst)

        # Crear archivo __init__.py si no existe
        init_file = os.path.join(package_path, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write("")

        # Crear archivo README con instrucciones
        readme_content = f"""# Migraciones para Subir al Servidor

Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Total de migraciones: {len(migrations)}

## Instrucciones para Aplicar en el Servidor

1. Detén el servidor Django:
   sudo systemctl stop gunicorn
   # O
   sudo supervisorctl stop nsc

2. Haz backup de las migraciones actuales:
   cd /var/www/NSC-INTERNATIONAL
   cp -r apps/accounts/migrations apps/accounts/migrations.backup_$(date +%Y%m%d_%H%M%S)

3. Sube este directorio al servidor:
   scp -r {package_name} root@servidor:/var/www/NSC-INTERNATIONAL/apps/accounts/

   O usando rsync:
   rsync -avz {package_name}/ root@servidor:/var/www/NSC-INTERNATIONAL/apps/accounts/migrations/

4. Verifica que los archivos estén en el lugar correcto:
   ls -la /var/www/NSC-INTERNATIONAL/apps/accounts/migrations/ | grep -E "003[678]"

5. Aplica las migraciones:
   cd /var/www/NSC-INTERNATIONAL
   python manage.py migrate accounts

6. Reinicia el servidor:
   sudo systemctl start gunicorn
   # O
   sudo supervisorctl start nsc

## Migraciones Incluidas

"""
        for migration in migrations:
            readme_content += f"- {migration}\n"

        with open(os.path.join(package_path, "README.md"), 'w', encoding='utf-8') as f:
            f.write(readme_content)

        # Crear archivo .tar.gz para facilitar la subida
        import tarfile
        tar_name = f"{package_name}.tar.gz"
        tar_path = os.path.join(UPLOAD_DIR, tar_name)

        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(package_path, arcname=package_name)

        tar_size = os.path.getsize(tar_path) / 1024  # KB

        print(f"   [OK] Paquete creado: {package_path}")
        print(f"   [OK] Archivo comprimido: {tar_path} ({tar_size:.2f} KB)")
        print(f"   [OK] Total de migraciones: {len(migrations)}")

        return package_path, tar_path
    except Exception as e:
        print(f"   [ERROR] Error al crear paquete: {e}")
        return None, None

def get_migrations_info():
    """Obtiene información sobre las migraciones"""
    print("\n3. Información de migraciones:")

    migrations = get_migration_files()
    print(f"   - Total de migraciones: {len(migrations)}")

    # Contar migraciones por número
    migration_numbers = {}
    for migration in migrations:
        # Extraer número de migración (ej: 0036_add_slug_to_player.py -> 0036)
        try:
            num = migration.split('_')[0]
            if num.isdigit():
                migration_numbers[num] = migration
        except:
            pass

    # Mostrar las últimas 10 migraciones
    print(f"   - Últimas migraciones:")
    for migration in sorted(migrations)[-10:]:
        print(f"     * {migration}")

    # Verificar migraciones problemáticas (0036-0038)
    problem_migrations = [m for m in migrations if m.startswith(('0036', '0037', '0038'))]
    if problem_migrations:
        print(f"\n   - Migraciones relacionadas con slug (0036-0038):")
        for m in sorted(problem_migrations):
            print(f"     * {m}")

def main():
    print("=" * 60)
    print("Organizando migraciones para subir al servidor")
    print("=" * 60)

    # Información
    get_migrations_info()

    # Backup
    backup = create_migrations_backup()

    # Crear paquete
    package_path, tar_path = create_upload_package()

    print("\n" + "=" * 60)
    print("[OK] Proceso completado")
    print("=" * 60)

    if package_path and tar_path:
        print(f"\n[PAQUETE] Directorio listo: {package_path}")
        print(f"[PAQUETE] Archivo comprimido: {tar_path}")
        print("\nPara subir al servidor:")
        print(f"  scp {tar_path} root@servidor:/tmp/")
        print(f"\nO descomprimir y subir el directorio:")
        print(f"  tar -xzf {tar_path}")
        print(f"  scp -r {package_path} root@servidor:/var/www/NSC-INTERNATIONAL/apps/accounts/")

        print("\n[IMPORTANTE] Antes de aplicar en el servidor:")
        print("   1. Detén el servidor Django")
        print("   2. Haz backup de las migraciones actuales")
        print("   3. Sube y reemplaza las migraciones")
        print("   4. Aplica las migraciones: python manage.py migrate accounts")
        print("   5. Reinicia el servidor")

if __name__ == "__main__":
    main()

