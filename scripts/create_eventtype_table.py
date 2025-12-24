"""
Script para crear la tabla events_eventtype si no existe
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from django.db import connection


def create_eventtype_table():
    cursor = connection.cursor()

    # Verificar si la tabla existe
    cursor.execute(
        """
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='events_eventtype'
    """
    )

    if cursor.fetchone():
        print("La tabla events_eventtype ya existe")
        return

    # Crear la tabla
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

    # Crear índice para name
    cursor.execute(
        """
        CREATE UNIQUE INDEX events_eventtype_name_unique ON events_eventtype(name)
    """
    )

    connection.commit()
    print("✓ Tabla events_eventtype creada exitosamente")


if __name__ == "__main__":
    create_eventtype_table()
