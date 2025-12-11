# Generated migration to change division from ForeignKey to ManyToManyField

from django.db import migrations, models


def migrate_division_data(apps, schema_editor):
    """Migrar datos de division (ForeignKey) a divisions (ManyToMany)"""
    Event = apps.get_model("events", "Event")
    Division = apps.get_model("events", "Division")

    for event in Event.objects.all():
        if hasattr(event, "division") and event.division_id:
            # Si el evento tiene una división en el campo antiguo, agregarla al nuevo campo
            try:
                division = Division.objects.get(pk=event.division_id)
                event.divisions.add(division)
            except Division.DoesNotExist:
                pass


def reverse_migrate_division_data(apps, schema_editor):
    """Función reversa: no hacemos nada ya que perdemos información al revertir"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0020_add_gate_fee_type_if_missing"),
    ]

    operations = [
        # Agregar el nuevo campo ManyToManyField
        migrations.AddField(
            model_name="event",
            name="divisions",
            field=models.ManyToManyField(
                blank=True,
                help_text="Puedes seleccionar una o más divisiones para este evento",
                related_name="events",
                to="events.division",
                verbose_name="Divisiones",
            ),
        ),
        # Migrar datos del campo antiguo al nuevo (si hay datos)
        migrations.RunPython(
            code=migrate_division_data,
            reverse_code=reverse_migrate_division_data,
        ),
        # Eliminar el campo ForeignKey antiguo
        migrations.RemoveField(
            model_name="event",
            name="division",
        ),
    ]









