import sqlite3

conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

# Verificar eventos antes
cursor.execute("SELECT COUNT(*) FROM events_event")
count_before = cursor.fetchone()[0]
print(f"Eventos antes: {count_before}")

if count_before > 0:
    # Mostrar algunos eventos
    cursor.execute("SELECT id, title FROM events_event LIMIT 5")
    events = cursor.fetchall()
    print("\nPrimeros eventos:")
    for event_id, title in events:
        print(f"  - ID {event_id}: {title}")

# Eliminar todos los eventos
print("\nEliminando todos los eventos...")
cursor.execute("DELETE FROM events_event")
conn.commit()
print("✓ DELETE ejecutado")

# Verificar después
cursor.execute("SELECT COUNT(*) FROM events_event")
count_after = cursor.fetchone()[0]
print(f"\nEventos después: {count_after}")

# Verificar tablas relacionadas
print("\nVerificando tablas relacionadas:")
cursor.execute("SELECT COUNT(*) FROM events_eventattendance")
attendance_count = cursor.fetchone()[0]
print(f"  - EventAttendance: {attendance_count}")

cursor.execute("SELECT COUNT(*) FROM events_eventcomment")
comment_count = cursor.fetchone()[0]
print(f"  - EventComment: {comment_count}")

conn.close()

if count_after == 0:
    print("\n✓ Todos los eventos fueron eliminados exitosamente")
else:
    print(f"\n⚠ Aún quedan {count_after} eventos")
