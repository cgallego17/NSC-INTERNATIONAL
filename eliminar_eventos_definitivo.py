#!/usr/bin/env python
"""Script definitivo para eliminar todos los eventos"""
import sqlite3
import os
import sys

# Ruta absoluta a la base de datos
db_path = os.path.join(os.getcwd(), "db.sqlite3")
print(f"Ruta de BD: {db_path}")
print(f"¿Existe?: {os.path.exists(db_path)}")

if not os.path.exists(db_path):
    print("ERROR: No se encontró la base de datos")
    sys.exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Verificar antes
cursor.execute("SELECT COUNT(*) FROM events_event")
count_before = cursor.fetchone()[0]
print(f"\nEventos ANTES de eliminar: {count_before}")

if count_before > 0:
    # Mostrar algunos eventos
    cursor.execute("SELECT id, title FROM events_event LIMIT 5")
    events = cursor.fetchall()
    print("\nPrimeros eventos a eliminar:")
    for event_id, title in events:
        print(f"  - ID {event_id}: {title}")

# Eliminar TODOS los eventos
print("\nEliminando todos los eventos...")
cursor.execute("DELETE FROM events_event")
rows_deleted = cursor.rowcount
conn.commit()
print(f"Filas eliminadas: {rows_deleted}")

# Verificar después
cursor.execute("SELECT COUNT(*) FROM events_event")
count_after = cursor.fetchone()[0]
print(f"\nEventos DESPUÉS de eliminar: {count_after}")

conn.close()

if count_after == 0:
    print("\n✓ ÉXITO: Todos los eventos fueron eliminados")
    print("\nIMPORTANTE: Reinicia el servidor Django para ver los cambios")
else:
    print(f"\n⚠ ADVERTENCIA: Aún quedan {count_after} eventos en la base de datos")










