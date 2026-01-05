#!/usr/bin/env python
"""
Script para organizar y optimizar la base de datos antes de subirla al servidor
"""
import os
import sqlite3
import shutil
from datetime import datetime

DB_FILE = "db.sqlite3"
BACKUP_DIR = "database_backups"

def optimize_database():
    """Optimiza la base de datos SQLite"""
    print("1. Optimizando base de datos...")

    if not os.path.exists(DB_FILE):
        print(f"   [ERROR] Archivo {DB_FILE} no encontrado")
        return False

    # Crear backup antes de optimizar
    backup_file = create_backup()

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Vacuum para optimizar
        print("   - Ejecutando VACUUM...")
        cursor.execute("VACUUM")

        # Reindex
        print("   - Reindexando...")
        cursor.execute("REINDEX")

        # Analizar para optimizar queries
        print("   - Analizando tablas...")
        cursor.execute("ANALYZE")

        conn.commit()
        conn.close()

        print("   [OK] Base de datos optimizada")
        return True
    except Exception as e:
        print(f"   [ERROR] Error al optimizar: {e}")
        # Restaurar backup si hay error
        if backup_file and os.path.exists(backup_file):
            print(f"   - Restaurando backup desde {backup_file}...")
            shutil.copy(backup_file, DB_FILE)
        return False

def create_backup():
    """Crea un backup de la base de datos"""
    print("\n2. Creando backup...")

    if not os.path.exists(DB_FILE):
        return None

    # Crear directorio de backups si no existe
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    # Nombre del backup con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"db_backup_{timestamp}.sqlite3")

    try:
        shutil.copy(DB_FILE, backup_file)
        size = os.path.getsize(backup_file) / (1024 * 1024)
        print(f"   [OK] Backup creado: {backup_file} ({size:.2f} MB)")
        return backup_file
    except Exception as e:
        print(f"   [ERROR] Error al crear backup: {e}")
        return None

def get_database_info():
    """Obtiene información sobre la base de datos"""
    print("\n3. Información de la base de datos:")

    if not os.path.exists(DB_FILE):
        print("   [ERROR] Archivo no encontrado")
        return

    size = os.path.getsize(DB_FILE) / (1024 * 1024)
    print(f"   - Tamaño: {size:.2f} MB")

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Contar tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"   - Tablas: {len(tables)}")

        # Contar migraciones aplicadas
        cursor.execute("SELECT COUNT(*) FROM django_migrations")
        migrations = cursor.fetchone()[0]
        print(f"   - Migraciones aplicadas: {migrations}")

        # Contar jugadores
        try:
            cursor.execute("SELECT COUNT(*) FROM accounts_player")
            players = cursor.fetchone()[0]
            print(f"   - Jugadores: {players}")
        except:
            pass

        conn.close()
    except Exception as e:
        print(f"   [ERROR] Error al obtener informacion: {e}")

def create_upload_package():
    """Crea un paquete listo para subir"""
    print("\n4. Creando paquete para subir...")

    if not os.path.exists(DB_FILE):
        print("   [ERROR] Archivo de base de datos no encontrado")
        return None

    package_name = f"db_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite3"

    try:
        shutil.copy(DB_FILE, package_name)
        size = os.path.getsize(package_name) / (1024 * 1024)
        print(f"   [OK] Paquete creado: {package_name} ({size:.2f} MB)")
        print(f"\n   Para subir al servidor:")
        print(f"   scp {package_name} usuario@servidor:/var/www/NSC-INTERNATIONAL/")
        print(f"\n   O usando rsync:")
        print(f"   rsync -avz {package_name} usuario@servidor:/var/www/NSC-INTERNATIONAL/")
        return package_name
    except Exception as e:
        print(f"   [ERROR] Error al crear paquete: {e}")
        return None

def main():
    print("=" * 60)
    print("Organizando base de datos para subir al servidor")
    print("=" * 60)

    # Información
    get_database_info()

    # Optimizar
    if optimize_database():
        # Información después de optimizar
        get_database_info()

    # Crear paquete
    package = create_upload_package()

    print("\n" + "=" * 60)
    print("[OK] Proceso completado")
    print("=" * 60)

    if package:
        print(f"\n[PAQUETE] Archivo listo para subir: {package}")
        print("\n[IMPORTANTE] Antes de subir al servidor:")
        print("   1. Detén el servidor Django en producción")
        print("   2. Haz backup de la base de datos actual del servidor")
        print("   3. Sube el archivo y reemplázalo")
        print("   4. Asegúrate de que los permisos sean correctos")
        print("   5. Reinicia el servidor")

if __name__ == "__main__":
    main()

