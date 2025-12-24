"""
Script para crear events_eventtype - Escribe resultado en archivo
"""

import sqlite3
import sys
from datetime import datetime

output_lines = []


def log(msg):
    print(msg)
    output_lines.append(msg)


try:
    log("=" * 70)
    log("CREANDO TABLA events_eventtype")
    log("=" * 70)

    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()

    # Verificar
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='events_eventtype'"
    )
    exists = cursor.fetchone()

    if exists:
        log("✓ Tabla existe")
    else:
        log("✗ Creando tabla...")
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
        log("✓ Tabla CREADA")

    # Columnas
    cursor.execute("PRAGMA table_info(events_eventtype)")
    cols = [c[1] for c in cursor.fetchall()]
    log(f"Columnas: {', '.join(cols)}")

    # Agregar faltantes
    if "color" not in cols:
        cursor.execute(
            "ALTER TABLE events_eventtype ADD COLUMN color VARCHAR(7) DEFAULT '#0d2c54'"
        )
        conn.commit()
        log("✓ color agregada")
    if "icon" not in cols:
        cursor.execute(
            "ALTER TABLE events_eventtype ADD COLUMN icon VARCHAR(50) DEFAULT 'fas fa-calendar'"
        )
        conn.commit()
        log("✓ icon agregada")

    # Datos
    cursor.execute("SELECT COUNT(*) FROM events_eventtype")
    count = cursor.fetchone()[0]
    log(f"Registros: {count}")

    if count == 0:
        log("Insertando datos...")
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
            log(f"  ✓ {n}")
        conn.commit()
        log("✓ Datos insertados")

    # Verificar
    cursor.execute("SELECT name FROM events_eventtype")
    tipos_db = [r[0] for r in cursor.fetchall()]
    log(f"Tipos en BD: {tipos_db}")

    conn.close()
    log("=" * 70)
    log("✓ COMPLETADO")
    log("=" * 70)

    # Escribir a archivo
    with open("eventtype_result.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    log("\nResultado guardado en eventtype_result.txt")

except Exception as e:
    log(f"\n✗ ERROR: {e}")
    import traceback

    log(traceback.format_exc())
    with open("eventtype_error.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    sys.exit(1)
