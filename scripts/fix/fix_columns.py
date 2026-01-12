import sqlite3

conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

# Verificar campos existentes
cursor.execute("PRAGMA table_info(events_event)")
existing_cols = [col[1] for col in cursor.fetchall()]

print("Verificando campos...")
print(f"Campos existentes: {len(existing_cols)}")

# Campos que deben existir
fields_to_add = [
    ("stripe_payment_profile", "VARCHAR(255)"),
    ("display_player_list", "BOOLEAN DEFAULT 0"),
    ("email_welcome_body", "TEXT"),
    ("video_url", "VARCHAR(200)"),
    ("hotel_id", "INTEGER"),
    ("event_contact_id", "INTEGER"),
]

added = []
for field_name, field_type in fields_to_add:
    if field_name not in existing_cols:
        try:
            cursor.execute(
                f"ALTER TABLE events_event ADD COLUMN {field_name} {field_type}"
            )
            conn.commit()
            added.append(field_name)
            print(f"✓ Agregado: {field_name}")
        except Exception as e:
            print(f"✗ Error con {field_name}: {e}")
    else:
        print(f"✓ Ya existe: {field_name}")

if added:
    print(f"\n✓ Se agregaron {len(added)} campos: {', '.join(added)}")
else:
    print("\n✓ Todos los campos ya existen")

conn.close()
