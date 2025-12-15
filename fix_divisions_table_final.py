#!/usr/bin/env python
"""Script final para crear la tabla events_event_divisions"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Crear tabla si no existe
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS events_event_divisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            division_id INTEGER NOT NULL,
            UNIQUE(event_id, division_id)
        )
    """
    )
    connection.commit()

    # Verificar
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='events_event_divisions'"
    )
    if cursor.fetchone():
        print("SUCCESS: Tabla events_event_divisions creada/verificada")
    else:
        print("ERROR: No se pudo crear la tabla")










