"""
Script para crear EventType usando Django ORM
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from django.db import connection
from apps.events.models import EventType


def crear_eventtype():
    print("=" * 60)
    print("CREANDO TABLA events_eventtype CON DJANGO")
    print("=" * 60)

    # Crear la tabla usando SQL directo
    cursor = connection.cursor()

    try:
        # Verificar si existe
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='events_eventtype'"
        )
        if cursor.fetchone():
            print("✓ Tabla ya existe")
        else:
            print("✗ Tabla NO existe. Creándola...")
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
            print("✓ Tabla creada")

        # Verificar datos
        count = EventType.objects.count()
        print(f"\nRegistros actuales: {count}")

        if count == 0:
            print("Insertando tipos de eventos...")
            EventType.objects.get_or_create(
                name="LIGA",
                defaults={
                    "description": "Evento de liga regular",
                    "color": "#0d2c54",
                    "icon": "fas fa-trophy",
                    "is_active": True,
                },
            )
            print("  ✓ LIGA")

            EventType.objects.get_or_create(
                name="SHOWCASES",
                defaults={
                    "description": "Evento showcase para mostrar talento",
                    "color": "#0d2c54",
                    "icon": "fas fa-star",
                    "is_active": True,
                },
            )
            print("  ✓ SHOWCASES")

            EventType.objects.get_or_create(
                name="TORNEO",
                defaults={
                    "description": "Torneo competitivo",
                    "color": "#0d2c54",
                    "icon": "fas fa-medal",
                    "is_active": True,
                },
            )
            print("  ✓ TORNEO")

            EventType.objects.get_or_create(
                name="WORLD SERIES",
                defaults={
                    "description": "Serie mundial de béisbol",
                    "color": "#0d2c54",
                    "icon": "fas fa-globe",
                    "is_active": True,
                },
            )
            print("  ✓ WORLD SERIES")
            print("✓ Datos insertados")

        # Mostrar todos
        print("\nTipos de eventos:")
        for et in EventType.objects.all():
            print(f"  - {et.name}")

        print("\n" + "=" * 60)
        print("✓ PROCESO COMPLETADO")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    crear_eventtype()
