#!/usr/bin/env python
import sqlite3
import sys

try:
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()

    # Verificar campos existentes
    cursor.execute("PRAGMA table_info(events_event)")
    existing_cols = {col[1]: col for col in cursor.fetchall()}

    print("Campos existentes en events_event:")
    for col_name in sorted(existing_cols.keys()):
        print(f"  - {col_name}")

    # Campos que deben existir
    fields_to_add = [
        ("stripe_payment_profile", "VARCHAR(255)"),
        ("display_player_list", "BOOLEAN DEFAULT 0"),
        ("email_welcome_body", "TEXT"),
        ("video_url", "VARCHAR(200)"),
        ("hotel_id", "INTEGER"),
        ("event_contact_id", "INTEGER"),
    ]

    print("\nVerificando campos faltantes...")
    added_count = 0
    for field_name, field_type in fields_to_add:
        if field_name not in existing_cols:
            print(f"Agregando {field_name}...")
            try:
                cursor.execute(
                    f"ALTER TABLE events_event ADD COLUMN {field_name} {field_type}"
                )
                conn.commit()
                print(f"  ✓ {field_name} agregado")
                added_count += 1
            except sqlite3.OperationalError as e:
                print(f"  ✗ Error: {e}")
        else:
            print(f"  ✓ {field_name} ya existe")

    if added_count > 0:
        print(f"\n✓ Se agregaron {added_count} campos")
    else:
        print("\n✓ Todos los campos ya existen")

    # Verificar tabla many-to-many
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='events_event_additional_hotels'"
    )
    if not cursor.fetchone():
        print("\nCreando tabla events_event_additional_hotels...")
        cursor.execute(
            """
            CREATE TABLE events_event_additional_hotels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                hotel_id INTEGER NOT NULL,
                UNIQUE(event_id, hotel_id)
            )
        """
        )
        conn.commit()
        print("  ✓ Tabla creada")
    else:
        print("\n✓ Tabla events_event_additional_hotels ya existe")

    conn.close()
    print("\n✓ Proceso completado exitosamente")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
