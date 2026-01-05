#!/usr/bin/env python
"""
Script para verificar y corregir el estado de las migraciones de slug
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from django.db import connection

# Verificar si el campo slug existe
with connection.cursor() as cursor:
    # Para PostgreSQL
    if 'postgresql' in connection.vendor:
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='accounts_player' AND column_name='slug'
        """)
        slug_exists = cursor.fetchone() is not None
    # Para SQLite
    elif 'sqlite' in connection.vendor:
        cursor.execute("PRAGMA table_info(accounts_player)")
        columns = [col[1] for col in cursor.fetchall()]
        slug_exists = 'slug' in columns
    else:
        # MySQL
        cursor.execute("""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME='accounts_player' AND COLUMN_NAME='slug'
        """)
        slug_exists = cursor.fetchone() is not None

print(f"Campo 'slug' existe en accounts_player: {slug_exists}")

if slug_exists:
    print("\n✓ El campo slug ya existe. Puedes marcar la migración 0036 como aplicada (fake):")
    print("  python manage.py migrate accounts 0036 --fake")
else:
    print("\n✗ El campo slug NO existe. Necesitas aplicar la migración 0036 normalmente.")
    print("  Pero primero necesitas resolver el conflicto de dependencias.")
    print("\n  Opción 1: Marcar 0036 como fake y luego agregar el campo manualmente")
    print("  Opción 2: Revertir 0037, aplicar 0036, y luego re-aplicar 0037")

