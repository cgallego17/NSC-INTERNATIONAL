#!/usr/bin/env python
"""Script para asegurar que la tabla events_event_divisions existe"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from django.db import connection


def ensure_table():
    cursor = connection.cursor()

    # Verificar si existe
    cursor.execute(
        """
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='events_event_divisions'
    """
    )
    exists = cursor.fetchone()

    if exists:
        print("✓ La tabla events_event_divisions ya existe")
        # Verificar estructura
        cursor.execute("PRAGMA table_info(events_event_divisions)")
        columns = cursor.fetchall()
        print("\nEstructura actual:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
    else:
        print("✗ La tabla NO existe. Creándola...")
        try:
            # Crear la tabla
            cursor.execute(
                """
                CREATE TABLE events_event_divisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER NOT NULL,
                    division_id INTEGER NOT NULL,
                    UNIQUE(event_id, division_id)
                )
            """
            )
            connection.commit()
            print("✓ Tabla creada exitosamente")

            # Verificar estructura
            cursor.execute("PRAGMA table_info(events_event_divisions)")
            columns = cursor.fetchall()
            print("\nEstructura creada:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        except Exception as e:
            print(f"✗ Error al crear tabla: {e}")
            connection.rollback()
            return False

    # Verificar que podemos hacer una consulta simple
    try:
        cursor.execute("SELECT COUNT(*) FROM events_event_divisions")
        count = cursor.fetchone()[0]
        print(f"\n✓ Tabla accesible. Registros actuales: {count}")
    except Exception as e:
        print(f"✗ Error al acceder a la tabla: {e}")
        return False

    return True


if __name__ == "__main__":
    success = ensure_table()
    if success:
        print("\n✓ Todo listo. La tabla está lista para usar.")
    else:
        print("\n✗ Hubo un problema. Revisa los errores arriba.")
    sys.exit(0 if success else 1)
