#!/usr/bin/env python
"""
Script para eliminar todas las divisiones de la base de datos
"""
import os
import django
import sqlite3

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from apps.events.models import Division

print("=" * 70)
print("ELIMINACIÓN DE TODAS LAS DIVISIONES")
print("=" * 70)

# Paso 1: Verificar con Django ORM
print("\n1. Verificando divisiones con Django ORM:")
count_before = Division.objects.count()
print(f"   Divisiones encontradas: {count_before}")

if count_before > 0:
    print("\n   Divisiones existentes:")
    for division in Division.objects.all():
        print(f"     - ID {division.id}: {division.name}")
        if division.description:
            print(f"       Descripción: {division.description[:50]}...")
        if division.age_min or division.age_max:
            print(f"       Rango de edad: {division.age_range}")

# Paso 2: Eliminar relaciones ManyToMany primero (si es necesario)
print("\n2. Verificando relaciones con eventos...")
from apps.events.models import Event

events_with_divisions = Event.objects.filter(divisions__isnull=False).distinct().count()
print(f"   Eventos con divisiones asignadas: {events_with_divisions}")

if events_with_divisions > 0:
    print("   Eliminando relaciones de divisiones en eventos...")
    for event in Event.objects.all():
        event.divisions.clear()
    print("   ✓ Relaciones eliminadas")

# Paso 3: Eliminar con Django ORM
print("\n3. Eliminando divisiones con Django ORM...")
if count_before > 0:
    deleted = Division.objects.all().delete()
    print(f"   ✓ Divisiones eliminadas: {deleted[0]}")
else:
    print("   No hay divisiones para eliminar")

# Paso 4: Verificar con SQL directo
print("\n4. Verificando con SQL directo...")
db_path = os.path.abspath("db.sqlite3")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM events_division")
count_sql_after = cursor.fetchone()[0]
print(f"   Divisiones restantes (SQL): {count_sql_after}")

if count_sql_after > 0:
    print("   Eliminando divisiones restantes con SQL...")
    cursor.execute("DELETE FROM events_division")
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM events_division")
    count_sql_final = cursor.fetchone()[0]
    print(f"   Divisiones restantes después de SQL: {count_sql_final}")
else:
    count_sql_final = 0

conn.close()

# Paso 5: Verificación final
print("\n5. Verificación final:")
count_final = Division.objects.count()
print(f"   Divisiones finales (Django): {count_final}")

print("\n" + "=" * 70)
if count_final == 0 and count_sql_final == 0:
    print("✓ TODAS LAS DIVISIONES FUERON ELIMINADAS EXITOSAMENTE")
else:
    print(f"⚠ AÚN QUEDAN DIVISIONES: Django={count_final}, SQL={count_sql_final}")
print("=" * 70)

print("\n⚠ IMPORTANTE:")
print("   - Las relaciones con eventos han sido limpiadas")
print("   - Puedes agregar nuevas divisiones desde el admin o el formulario")
print("   - Si el servidor está corriendo, recarga la página con Ctrl+F5")





