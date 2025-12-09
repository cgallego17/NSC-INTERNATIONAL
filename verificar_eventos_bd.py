#!/usr/bin/env python
"""Script para verificar eventos en la base de datos"""
import sqlite3
import os
import django

# Verificar con SQL directo
print("=" * 60)
print("VERIFICACIÓN DE EVENTOS EN BASE DE DATOS")
print("=" * 60)

db_path = "db.sqlite3"
if not os.path.exists(db_path):
    print(f"ERROR: No se encontró {db_path}")
    exit(1)

print(f"\n1. Ruta de BD: {os.path.abspath(db_path)}")
print(f"   ¿Existe?: {os.path.exists(db_path)}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Verificar eventos
cursor.execute("SELECT COUNT(*) FROM events_event")
count = cursor.fetchone()[0]
print(f"\n2. Total de eventos en BD: {count}")

if count > 0:
    print("\n3. Primeros 10 eventos:")
    cursor.execute("SELECT id, title, status, start_date FROM events_event LIMIT 10")
    events = cursor.fetchall()
    for i, (event_id, title, status, start_date) in enumerate(events, 1):
        print(
            f"   {i}. ID {event_id}: {title[:50]}... (Estado: {status}, Fecha: {start_date})"
        )

    print(f"\n4. ¿Eliminar todos los eventos? (S/N)")
    # Eliminar directamente
    cursor.execute("DELETE FROM events_event")
    conn.commit()
    print("   ✓ Eventos eliminados")

    cursor.execute("SELECT COUNT(*) FROM events_event")
    count_after = cursor.fetchone()[0]
    print(f"   Eventos restantes: {count_after}")
else:
    print("\n3. No hay eventos en la base de datos")

conn.close()

# Verificar con Django
print("\n5. Verificación con Django ORM:")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from apps.events.models import Event

count_django = Event.objects.count()
print(f"   Eventos encontrados (Django): {count_django}")

if count_django > 0:
    events = Event.objects.all()[:5]
    print("   Primeros eventos:")
    for e in events:
        print(f"     - ID {e.id}: {e.title}")
    # Eliminar
    Event.objects.all().delete()
    print("   ✓ Eventos eliminados con Django")
    count_django_after = Event.objects.count()
    print(f"   Eventos restantes (Django): {count_django_after}")
else:
    print("   No hay eventos")

print("\n" + "=" * 60)
print("VERIFICACIÓN COMPLETADA")
print("=" * 60)
print("\n⚠ IMPORTANTE: Reinicia el servidor Django después de eliminar eventos")
