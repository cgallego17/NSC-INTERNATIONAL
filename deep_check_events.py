#!/usr/bin/env python
import os
import django
import sqlite3

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from apps.events.models import Event

print("=== VERIFICACIÓN PROFUNDA DE EVENTOS ===\n")

# 1. Verificar con Django ORM
print("1. Verificación con Django ORM:")
count_django = Event.objects.count()
print(f"   Eventos encontrados: {count_django}")

if count_django > 0:
    events = Event.objects.all()[:10]
    print("   Primeros eventos:")
    for e in events:
        print(f"     - ID {e.id}: {e.title} (Estado: {e.status})")

# 2. Verificar directamente con SQL
print("\n2. Verificación directa con SQL:")
conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM events_event")
count_sql = cursor.fetchone()[0]
print(f"   Eventos en tabla: {count_sql}")

if count_sql > 0:
    cursor.execute("SELECT id, title, status FROM events_event LIMIT 10")
    rows = cursor.fetchall()
    print("   Primeros eventos en BD:")
    for row in rows:
        print(f"     - ID {row[0]}: {row[1]} (Estado: {row[2]})")

# 3. Verificar si hay múltiples bases de datos
print("\n3. Verificando ubicación de la BD:")
import django.conf

db_path = django.conf.settings.DATABASES["default"]["NAME"]
print(f"   Ruta de BD: {db_path}")
print(f"   ¿Existe?: {os.path.exists(db_path)}")

# 4. Eliminar TODOS los eventos
print("\n4. Eliminando TODOS los eventos...")
if count_sql > 0:
    cursor.execute("DELETE FROM events_event")
    conn.commit()
    print("   ✓ DELETE ejecutado")

    cursor.execute("SELECT COUNT(*) FROM events_event")
    count_after = cursor.fetchone()[0]
    print(f"   Eventos restantes: {count_after}")

    # También con Django
    Event.objects.all().delete()
    count_django_after = Event.objects.count()
    print(f"   Eventos restantes (Django): {count_django_after}")

conn.close()

print("\n=== VERIFICACIÓN COMPLETADA ===")
