import sqlite3
import os

conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

# Verificar antes
cursor.execute("SELECT COUNT(*) FROM events_event")
count_before = cursor.fetchone()[0]

# Eliminar
cursor.execute("DELETE FROM events_event")
conn.commit()

# Verificar después
cursor.execute("SELECT COUNT(*) FROM events_event")
count_after = cursor.fetchone()[0]

# Escribir resultado a archivo
with open("delete_result.txt", "w") as f:
    f.write(f"Eventos antes: {count_before}\n")
    f.write(f"Eventos después: {count_after}\n")
    if count_after == 0:
        f.write("✓ Todos los eventos eliminados\n")
    else:
        f.write(f"⚠ Aún quedan {count_after} eventos\n")

conn.close()
print(f"Eventos antes: {count_before}")
print(f"Eventos después: {count_after}")
