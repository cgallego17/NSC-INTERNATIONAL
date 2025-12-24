"""
Script simple para insertar tipos de eventos
"""

import sqlite3
from datetime import datetime

print("=" * 70)
print("INSERTANDO TIPOS DE EVENTOS")
print("=" * 70)

conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

# Verificar tabla
cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='events_eventtype'"
)
if not cursor.fetchone():
    print("ERROR: Tabla events_eventtype no existe")
    print("Ejecuta: python manage.py migrate")
    exit(1)

# Eliminar todos
cursor.execute("DELETE FROM events_eventtype")
print("\n1. Tipos anteriores eliminados")

# Insertar nuevos
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
tipos = [
    ("LIGA", "Evento de liga regular", "#0d2c54", "fas fa-trophy"),
    ("SHOWCASES", "Evento showcase para mostrar talento", "#0d2c54", "fas fa-star"),
    ("TORNEO", "Torneo competitivo", "#0d2c54", "fas fa-medal"),
    ("WORLD SERIES", "Serie mundial de béisbol", "#0d2c54", "fas fa-globe"),
]

print("\n2. Insertando tipos:")
for name, desc, color, icon in tipos:
    cursor.execute(
        """
        INSERT INTO events_eventtype 
        (name, description, color, icon, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, 1, ?, ?)
    """,
        (name, desc, color, icon, now, now),
    )
    print(f"   ✓ {name}")

conn.commit()

# Verificar
cursor.execute("SELECT id, name, is_active FROM events_eventtype ORDER BY name")
rows = cursor.fetchall()
print(f"\n3. Verificación ({len(rows)} tipos):")
for row in rows:
    print(f"   ID: {row[0]}, Name: '{row[1]}', Active: {bool(row[2])}")

conn.close()
print("\n" + "=" * 70)
print("✓ COMPLETADO")
print("=" * 70)
