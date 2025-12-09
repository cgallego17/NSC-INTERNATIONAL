import sqlite3
import os
import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from apps.events.models import Event

print("=" * 50)
print("ELIMINACIÓN COMPLETA DE EVENTOS")
print("=" * 50)

# Paso 1: Verificar con Django
print("\n1. Verificando con Django ORM:")
count_django_before = Event.objects.count()
print(f"   Eventos encontrados: {count_django_before}")

# Paso 2: Verificar con SQL directo
print("\n2. Verificando con SQL directo:")
conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM events_event")
count_sql_before = cursor.fetchone()[0]
print(f"   Eventos en BD: {count_sql_before}")

if count_sql_before > 0:
    cursor.execute("SELECT id, title FROM events_event LIMIT 5")
    events = cursor.fetchall()
    print("   Primeros eventos:")
    for event_id, title in events:
        print(f"     - ID {event_id}: {title}")

# Paso 3: Eliminar con SQL directo
print("\n3. Eliminando con SQL directo...")
cursor.execute("DELETE FROM events_event")
conn.commit()
cursor.execute("SELECT COUNT(*) FROM events_event")
count_sql_after = cursor.fetchone()[0]
print(f"   Eventos restantes (SQL): {count_sql_after}")

# Paso 4: Eliminar con Django ORM
print("\n4. Eliminando con Django ORM...")
Event.objects.all().delete()
count_django_after = Event.objects.count()
print(f"   Eventos restantes (Django): {count_django_after}")

# Paso 5: Verificación final
print("\n5. Verificación final:")
cursor.execute("SELECT COUNT(*) FROM events_event")
final_count = cursor.fetchone()[0]
print(f"   Eventos finales en BD: {final_count}")

conn.close()

print("\n" + "=" * 50)
if final_count == 0 and count_django_after == 0:
    print("✓ TODOS LOS EVENTOS FUERON ELIMINADOS")
else:
    print(f"⚠ AÚN QUEDAN EVENTOS: BD={final_count}, Django={count_django_after}")
print("=" * 50)
