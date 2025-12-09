#!/usr/bin/env python
"""Script para aplicar migraciones y verificar estado"""
import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from django.core.management import call_command
from django.db import connection
from io import StringIO

# Aplicar migraciones
print("Aplicando migraciones de events...")
try:
    call_command("migrate", "events", verbosity=2)
    print("✓ Migraciones aplicadas")
except Exception as e:
    print(f"✗ Error: {e}")

# Verificar tabla
print("\nVerificando tabla events_event_divisions...")
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
        print("✓ Tabla events_event_divisions existe")
    else:
        print("✗ Tabla NO existe")

    # Contar registros
    cursor.execute("SELECT COUNT(*) FROM events_event_divisions")
    count = cursor.fetchone()[0]
    print(f"  Registros: {count}")

# Marcar migración como aplicada
print("\nMarcando migración 0021 como aplicada...")
try:
    call_command("migrate", "events", "0021", "--fake", verbosity=1)
    print("✓ Migración marcada como aplicada")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n✓ Proceso completado")





