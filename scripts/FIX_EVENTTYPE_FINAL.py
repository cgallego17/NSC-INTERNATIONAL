"""
Script FINAL para crear events_eventtype - Con salida forzada
"""

import sqlite3
import sys
from datetime import datetime

# Forzar salida inmediata
sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)

try:
    print("\n" + "=" * 70)
    print("CREANDO TABLA events_eventtype")
    print("=" * 70 + "\n")

    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()

    # Verificar existencia
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='events_eventtype'"
    )
    exists = cursor.fetchone()

    if exists:
        print("✓ Tabla existe")
    else:
        print("✗ Tabla NO existe - CREANDO...")
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
        print("✓ Tabla CREADA\n")

    # Verificar columnas
    cursor.execute("PRAGMA table_info(events_eventtype)")
    cols = [c[1] for c in cursor.fetchall()]
    print(f"Columnas: {', '.join(cols)}\n")

    # Agregar faltantes
    if "color" not in cols:
        cursor.execute(
            "ALTER TABLE events_eventtype ADD COLUMN color VARCHAR(7) DEFAULT '#0d2c54'"
        )
        conn.commit()
        print("✓ Columna 'color' agregada")
    if "icon" not in cols:
        cursor.execute(
            "ALTER TABLE events_eventtype ADD COLUMN icon VARCHAR(50) DEFAULT 'fas fa-calendar'"
        )
        conn.commit()
        print("✓ Columna 'icon' agregada")

    # Datos
    cursor.execute("SELECT COUNT(*) FROM events_eventtype")
    count = cursor.fetchone()[0]
    print(f"\nRegistros: {count}")

    if count == 0:
        print("Insertando datos...")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tipos = [
            ("LIGA", "Evento de liga regular", "#0d2c54", "fas fa-trophy"),
            ("SHOWCASES", "Evento showcase", "#0d2c54", "fas fa-star"),
            ("TORNEO", "Torneo competitivo", "#0d2c54", "fas fa-medal"),
            ("WORLD SERIES", "Serie mundial", "#0d2c54", "fas fa-globe"),
        ]
        for n, d, c, i in tipos:
            cursor.execute(
                """
                INSERT OR IGNORE INTO events_eventtype 
                (name, description, color, icon, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, 1, ?, ?)
            """,
                (n, d, c, i, now, now),
            )
            print(f"  ✓ {n}")
        conn.commit()

    # Verificar final
    cursor.execute("SELECT name FROM events_eventtype")
    print(f"\nTipos en BD: {[r[0] for r in cursor.fetchall()]}")

    conn.close()
    print("\n" + "=" * 70)
    print("✓ COMPLETADO")
    print("=" * 70 + "\n")

except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
