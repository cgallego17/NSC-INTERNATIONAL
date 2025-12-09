#!/usr/bin/env python
"""Script para aplicar migración 0023 y verificar campos"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from django.core.management import call_command
from django.db import connection

print("Aplicando migración 0023...")
try:
    call_command("migrate", "events", "0023", verbosity=2)
    print("✓ Migración aplicada")
except Exception as e:
    print(f"✗ Error: {e}")

print("\nVerificando campos en el modelo...")
from apps.events.models import Event

fields = [f.name for f in Event._meta.get_fields() if hasattr(f, "name")]
required_fields = [
    "stripe_payment_profile",
    "display_player_list",
    "hotel",
    "additional_hotels",
    "event_contact",
    "email_welcome_body",
    "video_url",
]
found = [f for f in required_fields if f in fields]
missing = [f for f in required_fields if f not in fields]

print(f"✓ Campos encontrados: {found}")
if missing:
    print(f"✗ Campos faltantes: {missing}")

print("\nVerificando tabla en BD...")
with connection.cursor() as cursor:
    cursor.execute("PRAGMA table_info(events_event)")
    cols = [col[1] for col in cursor.fetchall()]
    db_fields = [c for c in required_fields if c in cols or f"{c}_id" in cols]
    print(f"✓ Campos en BD: {db_fields}")

print("\n✓ Verificación completada")





