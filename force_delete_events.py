#!/usr/bin/env python
import os
import django
import sqlite3

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from apps.events.models import Event

# Método 1: Usando Django ORM
print("=== Eliminando eventos con Django ORM ===")
count_before = Event.objects.count()
print(f"Eventos encontrados: {count_before}")

if count_before > 0:
    deleted = Event.objects.all().delete()
    print(f"Eliminados: {deleted[0]}")

count_after = Event.objects.count()
print(f"Eventos restantes (Django): {count_after}")

# Método 2: Eliminación directa con SQL
print("\n=== Eliminando eventos con SQL directo ===")
conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM events_event")
count_sql_before = cursor.fetchone()[0]
print(f"Eventos en BD (SQL): {count_sql_before}")

if count_sql_before > 0:
    cursor.execute("DELETE FROM events_event")
    conn.commit()
    print("✓ DELETE ejecutado")

cursor.execute("SELECT COUNT(*) FROM events_event")
count_sql_after = cursor.fetchone()[0]
print(f"Eventos restantes (SQL): {count_sql_after}")

conn.close()

# Verificación final
print("\n=== Verificación final ===")
final_count = Event.objects.count()
print(f"Eventos finales: {final_count}")

if final_count == 0:
    print("✓ Todos los eventos fueron eliminados exitosamente")
else:
    print(f"⚠ Aún quedan {final_count} eventos")
