import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from apps.locations.models import Country, State, City

# Contar antes
print(
    f"Antes - Países: {Country.objects.count()}, Estados: {State.objects.count()}, Ciudades: {City.objects.count()}"
)

# Eliminar
City.objects.all().delete()
State.objects.all().delete()
Country.objects.all().delete()

# Contar después
print(
    f"Después - Países: {Country.objects.count()}, Estados: {State.objects.count()}, Ciudades: {City.objects.count()}"
)
print("✅ Eliminación completada")
