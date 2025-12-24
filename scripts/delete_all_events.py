#!/usr/bin/env python
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from apps.events.models import Event

# Contar eventos antes de eliminar
count_before = Event.objects.count()
print(f"Eventos encontrados: {count_before}")

if count_before > 0:
    # Eliminar todos los eventos
    deleted = Event.objects.all().delete()
    print(f"✓ Eventos eliminados: {deleted[0]}")

    # Verificar que se eliminaron
    count_after = Event.objects.count()
    print(f"Eventos restantes: {count_after}")

    if count_after == 0:
        print("✓ Todos los eventos fueron eliminados exitosamente")
    else:
        print(f"⚠ Aún quedan {count_after} eventos")
else:
    print("✓ No hay eventos para eliminar")
