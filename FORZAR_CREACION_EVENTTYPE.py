"""
Forzar creación de events_eventtype
"""

import sqlite3
from datetime import datetime

conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

# Eliminar si existe
cursor.execute("DROP TABLE IF EXISTS events_eventtype")
print("Tabla eliminada (si existía)")

# Crear
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

# Insertar datos
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
tipos = [
    ("LIGA", "Evento de liga regular", "#0d2c54", "fas fa-trophy", now, now),
    ("SHOWCASES", "Evento showcase", "#0d2c54", "fas fa-star", now, now),
    ("TORNEO", "Torneo competitivo", "#0d2c54", "fas fa-medal", now, now),
    ("WORLD SERIES", "Serie mundial", "#0d2c54", "fas fa-globe", now, now),
]

cursor.executemany(
    """
    INSERT INTO events_eventtype 
    (name, description, color, icon, is_active, created_at, updated_at)
    VALUES (?, ?, ?, ?, 1, ?, ?)
""",
    tipos,
)

conn.commit()

# Verificar
cursor.execute("SELECT COUNT(*) FROM events_eventtype")
print(f"Registros insertados: {cursor.fetchone()[0]}")

cursor.execute("SELECT name FROM events_eventtype")
print("Tipos:", [r[0] for r in cursor.fetchall()])

conn.close()
print("✓ Tabla creada y datos insertados")
