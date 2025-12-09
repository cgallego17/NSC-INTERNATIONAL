import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from apps.locations.models import Country, State, City, Site, Hotel

# Buscar duplicados
mexico1 = Country.objects.filter(name="Mexico", is_active=True).first()
mexico2 = Country.objects.filter(name="México", is_active=True).first()

if mexico1 and mexico2:
    # Mantener el más antiguo (México con acento, ID 2)
    keep = mexico2 if mexico2.created_at <= mexico1.created_at else mexico1
    remove = mexico1 if keep == mexico2 else mexico2

    print(f"Mantener: {keep.id} - {keep.name}")
    print(f"Eliminar: {remove.id} - {remove.name}")

    # Mover estados
    for state in State.objects.filter(country=remove):
        existing = State.objects.filter(country=keep, name=state.name).first()
        if existing:
            City.objects.filter(state=state).update(state=existing)
            Site.objects.filter(state=state).update(state=existing)
            Hotel.objects.filter(state=state).update(state=existing)
            state.delete()
        else:
            state.country = keep
            state.save()

    # Mover sitios y hoteles
    Site.objects.filter(country=remove).update(country=keep)
    Hotel.objects.filter(country=remove).update(country=keep)

    # Actualizar nombre si es necesario
    if keep.name == "Mexico":
        keep.name = "México"
        keep.save()

    # Eliminar duplicado
    remove.delete()
    print("✅ Duplicado eliminado")
elif mexico1:
    mexico1.name = "México"
    mexico1.save()
    print("✅ Nombre actualizado")
elif mexico2:
    print("✅ Todo correcto")
else:
    print("No se encontraron duplicados")
