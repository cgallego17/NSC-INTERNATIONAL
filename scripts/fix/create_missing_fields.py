import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Verificar y crear campos faltantes
    cursor.execute("PRAGMA table_info(events_event)")
    existing_cols = [col[1] for col in cursor.fetchall()]

    fields_to_add = [
        ("stripe_payment_profile", "VARCHAR(255)"),
        ("display_player_list", "BOOLEAN DEFAULT 0"),
        ("email_welcome_body", "TEXT"),
        ("video_url", "VARCHAR(200)"),
    ]

    for field_name, field_type in fields_to_add:
        if field_name not in existing_cols:
            print(f"Agregando campo {field_name}...")
            cursor.execute(
                f"ALTER TABLE events_event ADD COLUMN {field_name} {field_type}"
            )
            connection.commit()
            print(f"✓ Campo {field_name} agregado")
        else:
            print(f"✓ Campo {field_name} ya existe")

    # Verificar ForeignKeys
    fk_fields = [
        ("hotel_id", "INTEGER REFERENCES locations_hotel(id)"),
        ("event_contact_id", "INTEGER REFERENCES events_eventcontact(id)"),
    ]

    for field_name, field_type in fk_fields:
        if field_name not in existing_cols:
            print(f"Agregando campo {field_name}...")
            cursor.execute(
                f"ALTER TABLE events_event ADD COLUMN {field_name} {field_type}"
            )
            connection.commit()
            print(f"✓ Campo {field_name} agregado")
        else:
            print(f"✓ Campo {field_name} ya existe")

    # Verificar tabla EventContact
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='events_eventcontact'"
    )
    if not cursor.fetchone():
        print("Creando tabla events_eventcontact...")
        cursor.execute(
            """
            CREATE TABLE events_eventcontact (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                photo VARCHAR(100),
                phone VARCHAR(20),
                email VARCHAR(254),
                information TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                city_id INTEGER REFERENCES locations_city(id),
                state_id INTEGER REFERENCES locations_state(id),
                country_id INTEGER REFERENCES locations_country(id)
            )
        """
        )
        connection.commit()
        print("✓ Tabla events_eventcontact creada")
    else:
        print("✓ Tabla events_eventcontact ya existe")

    # Verificar tabla many-to-many additional_hotels
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='events_event_additional_hotels'"
    )
    if not cursor.fetchone():
        print("Creando tabla events_event_additional_hotels...")
        cursor.execute(
            """
            CREATE TABLE events_event_additional_hotels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL REFERENCES events_event(id) ON DELETE CASCADE,
                hotel_id INTEGER NOT NULL REFERENCES locations_hotel(id) ON DELETE CASCADE,
                UNIQUE(event_id, hotel_id)
            )
        """
        )
        connection.commit()
        print("✓ Tabla events_event_additional_hotels creada")
    else:
        print("✓ Tabla events_event_additional_hotels ya existe")

print("\n✓ Todos los campos y tablas verificados/creados")
