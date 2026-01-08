#!/usr/bin/env python
"""
Script alternativo para ejecutar la migración 0041 manualmente
Si la migración falla en el servidor, ejecuta este script primero
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nsc_admin.settings')
django.setup()

from django.db import connection, transaction
from apps.events.models import Division
from apps.accounts.models import Player

def manual_migration():
    """Ejecuta la migración manualmente"""

    print("\n=== MIGRACIÓN MANUAL 0041 ===\n")

    # 1. Verificar estado actual
    print("1. Verificando estado actual...")
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(accounts_player)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"   Columnas actuales: {', '.join(columns)}")

        has_division = 'division' in columns
        has_division_id = 'division_id' in columns
        has_division_id_temp = 'division_id_temp' in columns

        print(f"   - Tiene 'division': {has_division}")
        print(f"   - Tiene 'division_id': {has_division_id}")
        print(f"   - Tiene 'division_id_temp': {has_division_id_temp}")

    # 2. Crear columna temporal si no existe
    if not has_division_id_temp and not has_division_id:
        print("\n2. Creando columna temporal division_id_temp...")
        with connection.cursor() as cursor:
            cursor.execute(
                "ALTER TABLE accounts_player ADD COLUMN division_id_temp INTEGER REFERENCES events_division(id);"
            )
        print("   ✓ Columna creada")
    else:
        print("\n2. Columna temporal ya existe o división ya migrada")

    # 3. Leer datos de divisiones actuales (si existe columna division)
    if has_division and not has_division_id:
        print("\n3. Leyendo datos de divisiones...")
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, division
                FROM accounts_player
                WHERE division IS NOT NULL AND division != ''
                """
            )
            division_data = dict(cursor.fetchall())
        print(f"   ✓ Encontrados {len(division_data)} jugadores con división")

        # 4. Migrar datos
        if division_data:
            print("\n4. Migrando datos...")
            updates_to_apply = []

            for player_id, old_division_value in division_data.items():
                if not old_division_value:
                    continue

                division_name = str(old_division_value).strip()

                # Buscar o crear división
                division = None
                try:
                    division = Division.objects.get(name=division_name)
                except Division.DoesNotExist:
                    base_name = division_name.split()[0] if " " in division_name else division_name
                    division = Division.objects.filter(name__startswith=base_name).first()
                    if not division:
                        division = Division.objects.create(name=base_name, is_active=True)

                if division:
                    updates_to_apply.append((division.id, player_id))

            # Aplicar actualizaciones
            if updates_to_apply:
                with connection.cursor() as cursor:
                    # Deshabilitar temporalmente foreign key checks
                    cursor.execute("PRAGMA foreign_keys = OFF")
                    cursor.executemany(
                        "UPDATE accounts_player SET division_id_temp = ? WHERE id = ?",
                        updates_to_apply
                    )
                    cursor.execute("PRAGMA foreign_keys = ON")
                print(f"   ✓ Actualizados {len(updates_to_apply)} jugadores")

        # 5. Eliminar columna antigua y renombrar nueva
        print("\n5. Reemplazando columna...")
        with connection.cursor() as cursor:
            # Deshabilitar temporalmente foreign key checks
            cursor.execute("PRAGMA foreign_keys = OFF")

            # Eliminar columna antigua
            if has_division:
                cursor.execute("ALTER TABLE accounts_player DROP COLUMN division")
                print("   ✓ Columna 'division' eliminada")

            # Renombrar temporal a definitiva
            if has_division_id_temp and not has_division_id:
                cursor.execute("ALTER TABLE accounts_player RENAME COLUMN division_id_temp TO division_id")
                print("   ✓ Columna renombrada a 'division_id'")

            cursor.execute("PRAGMA foreign_keys = ON")

        print("\n=== MIGRACIÓN COMPLETADA ===\n")
    else:
        print("\n⚠ La migración ya fue aplicada o no hay datos que migrar")

    # 6. Verificar resultado final
    print("\n6. Verificando resultado...")
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(accounts_player)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"   Columnas finales: {', '.join(columns)}")

        if 'division_id' in columns:
            cursor.execute("SELECT COUNT(*) FROM accounts_player WHERE division_id IS NOT NULL")
            count = cursor.fetchone()[0]
            print(f"   ✓ Jugadores con división: {count}")
        else:
            print("   ⚠ Columna 'division_id' no encontrada")

if __name__ == '__main__':
    try:
        with transaction.atomic():
            manual_migration()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
