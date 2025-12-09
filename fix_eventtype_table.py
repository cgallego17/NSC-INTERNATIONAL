"""
Script para crear/verificar la tabla events_eventtype
"""

import sqlite3
import sys

try:
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()

    # Verificar si la tabla existe
    cursor.execute(
        """
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='events_eventtype'
    """
    )

    if cursor.fetchone():
        print("✓ Tabla events_eventtype existe")

        # Verificar columnas
        cursor.execute("PRAGMA table_info(events_eventtype)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Columnas encontradas: {', '.join(columns)}")

        # Agregar columnas faltantes
        if "color" not in columns:
            print("Agregando columna 'color'...")
            cursor.execute(
                "ALTER TABLE events_eventtype ADD COLUMN color VARCHAR(7) DEFAULT '#0d2c54'"
            )
            print("✓ Columna 'color' agregada")

        if "icon" not in columns:
            print("Agregando columna 'icon'...")
            cursor.execute(
                "ALTER TABLE events_eventtype ADD COLUMN icon VARCHAR(50) DEFAULT 'fas fa-calendar'"
            )
            print("✓ Columna 'icon' agregada")
    else:
        print("✗ Tabla no existe. Creándola...")
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
        print("✓ Tabla creada exitosamente")

    conn.commit()
    conn.close()
    print("\n✓ Proceso completado correctamente")
    sys.exit(0)

except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
