"""
Script para crear directamente la tabla events_eventtype
"""

import sqlite3
import sys
from datetime import datetime

try:
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()

    # Eliminar tabla si existe (para recrearla limpia)
    cursor.execute("DROP TABLE IF EXISTS events_eventtype")
    print("✓ Tabla anterior eliminada (si existía)")

    # Crear la tabla
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

    # Crear índice único
    cursor.execute(
        "CREATE UNIQUE INDEX events_eventtype_name_unique ON events_eventtype(name)"
    )

    # Insertar los tipos de eventos
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    event_types = [
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
        (
            "WORLD SERIES",
            "Serie mundial de béisbol",
            "#0d2c54",
            "fas fa-globe",
            now,
            now,
        ),
    ]

    cursor.executemany(
        """
        INSERT INTO events_eventtype (name, description, color, icon, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, 1, ?, ?)
    """,
        event_types,
    )

    conn.commit()

    # Verificar
    cursor.execute("SELECT COUNT(*) FROM events_eventtype")
    count = cursor.fetchone()[0]
    print(f"✓ Tabla creada con {count} registros")

    cursor.execute("SELECT name FROM events_eventtype ORDER BY name")
    types = cursor.fetchall()
    print("Tipos de eventos:")
    for t in types:
        print(f"  - {t[0]}")

    conn.close()
    print("\n✓ Proceso completado exitosamente")
    sys.exit(0)

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
