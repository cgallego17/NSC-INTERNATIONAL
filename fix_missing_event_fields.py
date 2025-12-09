import sqlite3

conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

# Verificar campos en events_event
cursor.execute("PRAGMA table_info(events_event)")
existing_cols = [col[1] for col in cursor.fetchall()]

print("Campos existentes en events_event:")
for col in existing_cols:
    print(f"  - {col}")

# Campos que deberían existir según el modelo
fields_to_add = [
    ("stripe_payment_profile", "VARCHAR(255)"),
    ("display_player_list", "BOOLEAN DEFAULT 0"),
    ("email_welcome_body", "TEXT"),
    ("video_url", "VARCHAR(200)"),
    ("hotel_id", "INTEGER"),
    ("event_contact_id", "INTEGER"),
]

print("\nVerificando y agregando campos faltantes...")
for field_name, field_type in fields_to_add:
    if field_name not in existing_cols:
        print(f"Agregando campo {field_name}...")
        try:
            cursor.execute(
                f"ALTER TABLE events_event ADD COLUMN {field_name} {field_type}"
            )
            conn.commit()
            print(f"✓ Campo {field_name} agregado exitosamente")
        except Exception as e:
            print(f"✗ Error al agregar {field_name}: {e}")
    else:
        print(f"✓ Campo {field_name} ya existe")

# Verificar tabla many-to-many additional_hotels
cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='events_event_additional_hotels'"
)
if not cursor.fetchone():
    print("\nCreando tabla events_event_additional_hotels...")
    try:
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
        print("✓ Tabla events_event_additional_hotels creada")
    except Exception as e:
        print(f"✗ Error al crear tabla: {e}")
else:
    print("\n✓ Tabla events_event_additional_hotels ya existe")

conn.close()
print("\n✓ Verificación completada")
