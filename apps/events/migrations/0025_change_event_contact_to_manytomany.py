# Generated migration to change event_contact from ForeignKey to ManyToManyField

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0024_eventtype_alter_event_category_event_event_type'),
    ]

    operations = [
        # Paso 1: Crear un campo temporal para almacenar los contactos actuales
        migrations.AddField(
            model_name='event',
            name='event_contact_temp',
            field=models.ManyToManyField(
                blank=True,
                help_text='Personas de contacto para el evento',
                related_name='events_temp',
                to='events.eventcontact',
                verbose_name='Contactos del Evento Temporal'
            ),
        ),
        # Paso 2: Copiar datos del ForeignKey al ManyToManyField temporal
        migrations.RunPython(
            code=lambda apps, schema_editor: migrate_contacts_forward(apps, schema_editor),
            reverse_code=lambda apps, schema_editor: migrate_contacts_backward(apps, schema_editor),
        ),
        # Paso 3: Eliminar el campo ForeignKey antiguo
        migrations.RemoveField(
            model_name='event',
            name='event_contact',
        ),
        # Paso 4: Renombrar el campo temporal al nombre original
        migrations.RenameField(
            model_name='event',
            old_name='event_contact_temp',
            new_name='event_contact',
        ),
        # Paso 5: Actualizar el related_name
        migrations.AlterField(
            model_name='event',
            name='event_contact',
            field=models.ManyToManyField(
                blank=True,
                help_text='Personas de contacto para el evento',
                related_name='events',
                to='events.eventcontact',
                verbose_name='Contactos del Evento'
            ),
        ),
    ]


def migrate_contacts_forward(apps, schema_editor):
    """Migrar contactos de ForeignKey a ManyToManyField"""
    Event = apps.get_model('events', 'Event')
    db_alias = schema_editor.connection.alias
    
    for event in Event.objects.using(db_alias).all():
        if event.event_contact_id:
            # Si existe un contacto, agregarlo al campo ManyToMany temporal
            event.event_contact_temp.add(event.event_contact_id)


def migrate_contacts_backward(apps, schema_editor):
    """Revertir la migración (tomar el primer contacto del ManyToMany)"""
    Event = apps.get_model('events', 'Event')
    db_alias = schema_editor.connection.alias
    
    for event in Event.objects.using(db_alias).all():
        contacts = event.event_contact_temp.all()
        if contacts.exists():
            # Asignar el primer contacto al ForeignKey
            event.event_contact = contacts.first()
            event.save()


