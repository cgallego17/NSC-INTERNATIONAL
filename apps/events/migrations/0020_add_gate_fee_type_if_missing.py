# Generated manually to fix missing gate_fee_type column

from django.db import migrations, models
import django.db.models.deletion


def add_gate_fee_type_if_missing(apps, schema_editor):
    """Add gate_fee_type column if it doesn't exist"""
    db_alias = schema_editor.connection.alias
    with schema_editor.connection.cursor() as cursor:
        # First, ensure GateFeeType table exists
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS events_gatefeetype (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL
            )
        """
        )

        # Check if column exists
        cursor.execute("PRAGMA table_info(events_event)")
        columns = [row[1] for row in cursor.fetchall()]

        if "gate_fee_type_id" not in columns and "gate_fee_type" not in columns:
            # Column doesn't exist, add it
            cursor.execute(
                """
                ALTER TABLE events_event 
                ADD COLUMN gate_fee_type_id INTEGER REFERENCES events_gatefeetype(id) NULL
            """
            )


def remove_gate_fee_type_if_exists(apps, schema_editor):
    """Remove gate_fee_type column if it exists (reverse migration)"""
    # SQLite doesn't support DROP COLUMN easily, so we'll skip this
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0019_event_email_welcome_body"),
    ]

    operations = [
        migrations.RunPython(
            add_gate_fee_type_if_missing, remove_gate_fee_type_if_exists
        ),
    ]





