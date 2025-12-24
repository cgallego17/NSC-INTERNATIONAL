#!/usr/bin/env python
"""Script para crear la tabla events_event_divisions"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from django.db import connection


def create_table():
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
    else:
        print("Creando tabla events_event_divisions...")
        try:
            cursor.execute(
                """
                CREATE TABLE events_event_divisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER NOT NULL,
                    division_id INTEGER NOT NULL,
                    UNIQUE(event_id, division_id),
                    FOREIGN KEY (event_id) REFERENCES events_event(id) ON DELETE CASCADE,
                    FOREIGN KEY (division_id) REFERENCES events_division(id) ON DELETE CASCADE
                )
            """
            )
            connection.commit()
            print("✓ Tabla creada exitosamente")
        except Exception as e:
            print(f"✗ Error al crear tabla: {e}")
            connection.rollback()
            return False

    # Verificar estructura
    cursor.execute("PRAGMA table_info(events_event_divisions)")
    columns = cursor.fetchall()
    print("\nEstructura de la tabla:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")

    return True


if __name__ == "__main__":
    success = create_table()
    sys.exit(0 if success else 1)
