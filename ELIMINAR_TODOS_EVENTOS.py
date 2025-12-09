import sqlite3
import os
import django

print("=" * 70)
print("ELIMINACIÓN DEFINITIVA DE TODOS LOS EVENTOS")
print("=" * 70)

# Paso 1: SQL directo
db_path = os.path.abspath("db.sqlite3")
print(f"\n1. Base de datos: {db_path}")
print(f"   ¿Existe?: {os.path.exists(db_path)}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM events_event")
count_before = cursor.fetchone()[0]
print(f"\n2. Eventos ANTES: {count_before}")

if count_before > 0:
    cursor.execute("SELECT id, title FROM events_event LIMIT 5")
    events = cursor.fetchall()
    print("   Primeros eventos:")
    for event_id, title in events:
        print(f"     - ID {event_id}: {title[:60]}...")

    print("\n3. Eliminando con SQL...")
    cursor.execute("DELETE FROM events_event")
    conn.commit()
    print("   ✓ DELETE ejecutado")

    cursor.execute("SELECT COUNT(*) FROM events_event")
    count_after = cursor.fetchone()[0]
    print(f"   Eventos DESPUÉS: {count_after}")
else:
    print("\n3. No hay eventos para eliminar")

conn.close()

# Paso 2: Django ORM
print("\n4. Verificando con Django ORM...")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from apps.events.models import Event

count_django = Event.objects.count()
print(f"   Eventos (Django): {count_django}")

if count_django > 0:
    Event.objects.all().delete()
    count_django_after = Event.objects.count()
    print(f"   Eventos después (Django): {count_django_after}")

print("\n" + "=" * 70)
print("PROCESO COMPLETADO")
print("=" * 70)
print("\n⚠ IMPORTANTE:")
print("   1. Detén el servidor Django (Ctrl+C)")
print("   2. Reinicia el servidor: python manage.py runserver")
print("   3. Recarga la página con Ctrl+F5")





