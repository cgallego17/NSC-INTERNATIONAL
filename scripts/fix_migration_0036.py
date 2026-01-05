#!/usr/bin/env python
"""
Script para marcar la migración 0036 como aplicada directamente en la base de datos
y verificar/crear el campo slug si es necesario
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from django.db import connection
from django.core.management import call_command

# 1. Verificar si el campo slug existe
print("1. Verificando si el campo 'slug' existe en accounts_player...")
with connection.cursor() as cursor:
    if 'postgresql' in connection.vendor:
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='accounts_player' AND column_name='slug'
        """)
        slug_exists = cursor.fetchone() is not None
    elif 'sqlite' in connection.vendor:
        cursor.execute("PRAGMA table_info(accounts_player)")
        columns = [col[1] for col in cursor.fetchall()]
        slug_exists = 'slug' in columns
    else:  # MySQL
        cursor.execute("""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME='accounts_player' AND COLUMN_NAME='slug'
        """)
        slug_exists = cursor.fetchone() is not None

print(f"   Campo 'slug' existe: {slug_exists}")

# 2. Si no existe, crearlo
if not slug_exists:
    print("\n2. Creando campo 'slug'...")
    with connection.cursor() as cursor:
        try:
            if 'postgresql' in connection.vendor:
                cursor.execute("""
                    ALTER TABLE accounts_player
                    ADD COLUMN slug VARCHAR(200) UNIQUE
                """)
            elif 'sqlite' in connection.vendor:
                cursor.execute("""
                    ALTER TABLE accounts_player
                    ADD COLUMN slug VARCHAR(200)
                """)
            connection.commit()
            # SQLite no soporta UNIQUE en ALTER TABLE, hay que crear índice después
            try:
                cursor.execute("""
                    CREATE UNIQUE INDEX IF NOT EXISTS accounts_player_slug_unique
                    ON accounts_player(slug) WHERE slug IS NOT NULL AND slug != ''
                """)
                connection.commit()
            except:
                pass  # El índice puede ya existir
            else:  # MySQL
                cursor.execute("""
                    ALTER TABLE accounts_player
                    ADD COLUMN slug VARCHAR(200) UNIQUE
                """)
            connection.commit()
            print("   ✓ Campo 'slug' creado")
        except Exception as e:
            print(f"   ✗ Error al crear campo: {e}")
            print("   (Puede que ya exista o haya otro problema)")

# 3. Marcar migración 0036 como aplicada en django_migrations
print("\n3. Marcando migración 0036 como aplicada en django_migrations...")
with connection.cursor() as cursor:
    # Verificar si ya está marcada
    cursor.execute("""
        SELECT * FROM django_migrations
        WHERE app='accounts' AND name='0036_add_slug_to_player'
    """)
    if cursor.fetchone():
        print("   ✓ Migración 0036 ya está marcada como aplicada")
    else:
        # Insertar el registro
        from django.utils import timezone
        if 'postgresql' in connection.vendor:
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied)
                VALUES ('accounts', '0036_add_slug_to_player', %s)
            """, [timezone.now()])
        elif 'sqlite' in connection.vendor:
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied)
                VALUES ('accounts', '0036_add_slug_to_player', datetime('now'))
            """)
        else:  # MySQL
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied)
                VALUES ('accounts', '0036_add_slug_to_player', %s)
            """, [timezone.now()])
        connection.commit()
        print("   ✓ Migración 0036 marcada como aplicada")

# 4. Verificar estado
print("\n4. Estado final:")
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT name, applied FROM django_migrations
        WHERE app='accounts' AND name LIKE '003%'
        ORDER BY name
    """)
    for row in cursor.fetchall():
        status = "✓" if row[1] else "✗"
        print(f"   {status} {row[0]}")

print("\n✓ Proceso completado. Ahora puedes ejecutar:")
print("   python manage.py migrate accounts")

