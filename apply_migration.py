#!/usr/bin/env python
"""Script para aplicar la migración 0010 de locations"""
import os
import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from django.core.management import execute_from_command_line
import sys

# Ejecutar migración
print("Aplicando migración 0010_create_hotel_room_service_reservation...")
sys.argv = ["manage.py", "migrate", "locations", "0010", "--verbosity", "2"]
execute_from_command_line(sys.argv)

print("\nMigración completada. Verificando tablas...")

from django.db import connection

cursor = connection.cursor()
cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%hotel%'"
)
tables = [row[0] for row in cursor.fetchall()]
print(f"Tablas de hotel: {tables}")

if "locations_hotelreservation" in tables:
    print("✓ Tabla locations_hotelreservation creada correctamente")
else:
    print("✗ Tabla locations_hotelreservation NO encontrada")
