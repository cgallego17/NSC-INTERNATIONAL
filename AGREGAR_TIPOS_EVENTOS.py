"""
Agregar tipos de eventos directamente a la base de datos
"""

import sqlite3
from datetime import datetime

conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

# Verificar si la tabla existe, si no crearla
cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='events_eventtype'"
)
if not cursor.fetchone():
    print("Creando tabla events_eventtype...")
    cursor.execute(
        """
        CREATE TABLE events_eventtype (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL UNIQUE,
            description TEXT NOT NULL,
            color VARCHAR(7) NOT NULL DEFAULT '#0d2c54',
            icon VARCHAR(50) NOT NULL DEFAULT 'fas fa-calendar',
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        )
    """
    )
    cursor.execute(
        "CREATE UNIQUE INDEX events_eventtype_name_unique ON events_eventtype(name)"
    )
    conn.commit()
    print("✓ Tabla creada")

# Insertar o actualizar tipos de eventos
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
tipos = [
    ("LIGA", "Evento de liga regular", "#0d2c54", "fas fa-trophy"),
    ("SHOWCASES", "Evento showcase para mostrar talento", "#0d2c54", "fas fa-star"),
    ("TORNEO", "Torneo competitivo", "#0d2c54", "fas fa-medal"),
    ("WORLD SERIES", "Serie mundial de béisbol", "#0d2c54", "fas fa-globe"),
]

print("\nInsertando tipos de eventos...")
for name, desc, color, icon in tipos:
    cursor.execute(
        """
        INSERT OR REPLACE INTO events_eventtype 
        (name, description, color, icon, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, 1, ?, ?)
    """,
        (name, desc, color, icon, now, now),
    )
    print(f"  ✓ {name}")

conn.commit()

# Verificar
cursor.execute("SELECT name FROM events_eventtype ORDER BY name")
tipos_db = [r[0] for r in cursor.fetchall()]
print(f"\n✓ Tipos en la base de datos: {tipos_db}")

conn.close()
print("\n✓ Proceso completado")
