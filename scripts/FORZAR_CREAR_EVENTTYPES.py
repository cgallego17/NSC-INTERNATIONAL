"""
Forzar creación de tipos de eventos usando SQL directo
"""

import sqlite3
from datetime import datetime

conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

# Verificar tabla
cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='events_eventtype'"
)
if not cursor.fetchone():
    print("ERROR: Tabla no existe. Ejecuta migraciones primero.")
    exit(1)

# Eliminar todos los tipos existentes
cursor.execute("DELETE FROM events_eventtype")
print("Tipos anteriores eliminados")

# Insertar nuevos tipos
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
tipos = [
    ("LIGA", "Evento de liga regular", "#0d2c54", "fas fa-trophy", now, now),
    (
        "SHOWCASES",
        "Evento showcase para mostrar talento",
        "#0d2c54",
        "fas fa-star",
        now,
        now,
    ),
    ("TORNEO", "Torneo competitivo", "#0d2c54", "fas fa-medal", now, now),
    ("WORLD SERIES", "Serie mundial de béisbol", "#0d2c54", "fas fa-globe", now, now),
]

print("\nInsertando tipos de eventos:")
for name, desc, color, icon, created, updated in tipos:
    cursor.execute(
        """
        INSERT INTO events_eventtype 
        (name, description, color, icon, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, 1, ?, ?)
    """,
        (name, desc, color, icon, created, updated),
    )
    print(f"  ✓ {name}")

conn.commit()

# Verificar
cursor.execute("SELECT id, name, is_active FROM events_eventtype ORDER BY name")
rows = cursor.fetchall()
print(f"\n✓ Tipos en la base de datos ({len(rows)}):")
for row in rows:
    print(f"  ID: {row[0]}, Name: '{row[1]}', Active: {row[2]}")

conn.close()
print("\n✓ Proceso completado")
