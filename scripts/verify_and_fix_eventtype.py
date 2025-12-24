"""
Script para verificar y crear la tabla events_eventtype
"""

import os
import django
import sqlite3

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from django.db import connection


def verify_and_fix():
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()

    # Verificar si la tabla existe
    cursor.execute(
        """
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='events_eventtype'
    """
    )

    result = cursor.fetchone()

    if result:
        print("✓ La tabla events_eventtype existe")
        # Verificar columnas
        cursor.execute("PRAGMA table_info(events_eventtype)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        print(f"Columnas: {column_names}")

        # Verificar si faltan color e icon
        if "color" not in column_names:
            print("Agregando columna color...")
            cursor.execute(
                "ALTER TABLE events_eventtype ADD COLUMN color VARCHAR(7) DEFAULT '#0d2c54'"
            )
            conn.commit()
            print("✓ Columna color agregada")

        if "icon" not in column_names:
            print("Agregando columna icon...")
            cursor.execute(
                "ALTER TABLE events_eventtype ADD COLUMN icon VARCHAR(50) DEFAULT 'fas fa-calendar'"
            )
            conn.commit()
            print("✓ Columna icon agregada")
    else:
        print("✗ La tabla events_eventtype NO existe. Creándola...")
        cursor.execute(
            """
            CREATE TABLE events_eventtype (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT NOT NULL,
                color VARCHAR(7) NOT NULL DEFAULT '#0d2c54',
                icon VARCHAR(50) NOT NULL DEFAULT 'fas fa-calendar',
                is_active BOOLEAN NOT NULL DEFAULT 1,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL
            )
        """
        )

        cursor.execute(
            """
            CREATE UNIQUE INDEX events_eventtype_name_unique ON events_eventtype(name)
        """
        )

        conn.commit()
        print("✓ Tabla events_eventtype creada exitosamente")

    conn.close()
    print("\n✓ Verificación completada")


if __name__ == "__main__":
    verify_and_fix()
