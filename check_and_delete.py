import sqlite3

db_path = "db.sqlite3"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Verificar antes
cursor.execute("SELECT COUNT(*) FROM events_event")
before = cursor.fetchone()[0]
print(f"Eventos ANTES: {before}")

# Eliminar
cursor.execute("DELETE FROM events_event")
conn.commit()

# Verificar después
cursor.execute("SELECT COUNT(*) FROM events_event")
after = cursor.fetchone()[0]
print(f"Eventos DESPUÉS: {after}")

conn.close()









