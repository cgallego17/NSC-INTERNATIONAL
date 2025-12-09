import sqlite3
import os
import django

# Método 1: SQL directo
print("Eliminando eventos con SQL...")
conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()
cursor.execute("DELETE FROM events_event")
conn.commit()
cursor.execute("SELECT COUNT(*) FROM events_event")
count_sql = cursor.fetchone()[0]
conn.close()
print(f"Eventos restantes (SQL): {count_sql}")

# Método 2: Django ORM
print("\nEliminando eventos con Django ORM...")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()
from apps.events.models import Event

Event.objects.all().delete()
count_django = Event.objects.count()
print(f"Eventos restantes (Django): {count_django}")

print("\n✓ Proceso completado")





