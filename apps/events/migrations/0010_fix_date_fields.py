# Generated migration to fix corrupted date fields

from django.db import migrations, connection
from django.conf import settings
from django.utils.dateparse import parse_date, parse_datetime
from datetime import datetime, date
import sqlite3
import os


def fix_date_fields(apps, schema_editor):
    """Fix corrupted date fields in Event model using raw SQL"""
    # Get database path from Django settings
    db_path = connection.settings_dict["NAME"]
    # Convert Path object to string if needed
    if hasattr(db_path, "__fspath__"):
        db_path = str(db_path)
    elif not isinstance(db_path, str):
        db_path = str(db_path)

    # Create a new SQLite connection without date converters
    # This bypasses Django's connection entirely
    raw_db = sqlite3.connect(
        db_path, detect_types=0
    )  # detect_types=0 disables type detection
    raw_db.row_factory = sqlite3.Row  # Use Row factory for easier access

    try:
        cursor = raw_db.cursor()

        # Check if table exists first
        cursor.execute(
            """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='events_event'
        """
        )
        table_exists = cursor.fetchone()

        if not table_exists:
            # Table doesn't exist yet (e.g., during test migrations), skip
            return

        # Read values as TEXT to avoid any conversion
        cursor.execute(
            "SELECT id, CAST(start_date AS TEXT) as start_date, CAST(end_date AS TEXT) as end_date FROM events_event"
        )
        rows = cursor.fetchall()

        for row in rows:
            row_id = row["id"]
            start_date_raw = row["start_date"]
            end_date_raw = row["end_date"]
            new_start_date = None
            new_end_date = None

            # Fix start_date
            if start_date_raw:
                try:
                    # Convert bytes to string if needed
                    if isinstance(start_date_raw, bytes):
                        start_date_raw = start_date_raw.decode("utf-8", errors="ignore")

                    if isinstance(start_date_raw, str) and start_date_raw.strip():
                        # Try parsing as datetime (ISO format like '2024-01-25 07:17:08.577639')
                        # Extract just the date part if it's a datetime
                        if " " in start_date_raw:
                            # It's a datetime string, extract date part
                            date_part = start_date_raw.split(" ")[0]
                            d = parse_date(date_part)
                            if d:
                                new_start_date = d.isoformat()
                        else:
                            # Try parsing as date
                            d = parse_date(start_date_raw)
                            if d:
                                new_start_date = d.isoformat()
                except (ValueError, TypeError, AttributeError) as e:
                    # If parsing fails, set to NULL
                    new_start_date = None

            # Fix end_date
            if end_date_raw:
                try:
                    # Convert bytes to string if needed
                    if isinstance(end_date_raw, bytes):
                        end_date_raw = end_date_raw.decode("utf-8", errors="ignore")

                    if isinstance(end_date_raw, str) and end_date_raw.strip():
                        # Try parsing as datetime (ISO format)
                        # Extract just the date part if it's a datetime
                        if " " in end_date_raw:
                            # It's a datetime string, extract date part
                            date_part = end_date_raw.split(" ")[0]
                            d = parse_date(date_part)
                            if d:
                                new_end_date = d.isoformat()
                        else:
                            # Try parsing as date
                            d = parse_date(end_date_raw)
                            if d:
                                new_end_date = d.isoformat()
                except (ValueError, TypeError, AttributeError) as e:
                    # If parsing fails, set to NULL
                    new_end_date = None

            # Update the row directly
            updates = []
            params = []

            if start_date_raw:  # If we had a value
                if new_start_date is not None:
                    updates.append("start_date = ?")
                    params.append(new_start_date)
                else:
                    # If we couldn't parse it, set to NULL
                    updates.append("start_date = NULL")

            if end_date_raw:  # If we had a value
                if new_end_date is not None:
                    updates.append("end_date = ?")
                    params.append(new_end_date)
                else:
                    # If we couldn't parse it, set to NULL
                    updates.append("end_date = NULL")

            if updates:
                params.append(row_id)
                sql = f"UPDATE events_event SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(sql, params)

        raw_db.commit()
    finally:
        raw_db.close()


def reverse_fix_date_fields(apps, schema_editor):
    """Reverse migration - nothing to do"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0009_division_event_division"),
    ]

    operations = [
        migrations.RunPython(fix_date_fields, reverse_fix_date_fields),
    ]
