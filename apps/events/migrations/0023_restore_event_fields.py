# Generated migration to restore event fields that were removed

from django.db import migrations, models
import django.db.models.deletion


def restore_event_fields(apps, schema_editor):
    """Restaurar campos eliminados en la migración 0022"""
    pass


def reverse_restore_event_fields(apps, schema_editor):
    """Función reversa"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0022_remove_event_additional_hotels_and_more"),
        ("locations", "0009_hotel_contact_email_hotel_contact_name_and_more"),
    ]

    operations = [
        # Restaurar stripe_payment_profile
        migrations.AddField(
            model_name="event",
            name="stripe_payment_profile",
            field=models.CharField(
                blank=True,
                help_text="ID del perfil de pago de Stripe para este evento",
                max_length=255,
                null=True,
                verbose_name="Perfil de Pago Stripe",
            ),
        ),
        # Restaurar display_player_list
        migrations.AddField(
            model_name="event",
            name="display_player_list",
            field=models.BooleanField(
                default=False,
                help_text="Mostrar lista de jugadores en el evento",
                verbose_name="Display Player List",
            ),
        ),
        # Restaurar hotel
        migrations.AddField(
            model_name="event",
            name="hotel",
            field=models.ForeignKey(
                blank=True,
                help_text="Hotel sede principal donde se alojarán los participantes del evento",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="primary_events",
                to="locations.hotel",
                verbose_name="Hotel Sede",
            ),
        ),
        # Restaurar additional_hotels
        migrations.AddField(
            model_name="event",
            name="additional_hotels",
            field=models.ManyToManyField(
                blank=True,
                help_text="Hoteles adicionales donde se alojarán los participantes del evento",
                related_name="additional_events",
                to="locations.hotel",
                verbose_name="Hoteles Adicionales",
            ),
        ),
        # Restaurar email_welcome_body
        migrations.AddField(
            model_name="event",
            name="email_welcome_body",
            field=models.TextField(
                blank=True,
                help_text="Contenido HTML del correo de bienvenida que se enviará a los participantes",
                null=True,
                verbose_name="Cuerpo del Correo de Bienvenida (HTML)",
            ),
        ),
        # Restaurar video_url (campo nuevo para video)
        migrations.AddField(
            model_name="event",
            name="video_url",
            field=models.URLField(
                blank=True,
                help_text="URL del video del evento (YouTube, Vimeo, etc.)",
                null=True,
                verbose_name="Video del Evento",
            ),
        ),
        # Recrear EventContact
        migrations.CreateModel(
            name="EventContact",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Nombre completo de la persona de contacto",
                        max_length=200,
                        verbose_name="Nombre",
                    ),
                ),
                (
                    "photo",
                    models.ImageField(
                        blank=True,
                        help_text="Foto de la persona de contacto",
                        null=True,
                        upload_to="event_contacts/",
                        verbose_name="Foto",
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True,
                        help_text="Número de teléfono de contacto",
                        max_length=20,
                        verbose_name="Teléfono",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True,
                        help_text="Correo electrónico de contacto",
                        max_length=254,
                        verbose_name="Email",
                    ),
                ),
                (
                    "information",
                    models.TextField(
                        blank=True,
                        help_text="Información adicional sobre el contacto",
                        verbose_name="Información",
                    ),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="Activo")),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Fecha de Creación"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Fecha de Actualización"
                    ),
                ),
                (
                    "city",
                    models.ForeignKey(
                        blank=True,
                        help_text="Ciudad de la persona de contacto",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="event_contacts",
                        to="locations.city",
                        verbose_name="Ciudad",
                    ),
                ),
                (
                    "country",
                    models.ForeignKey(
                        blank=True,
                        help_text="País de la persona de contacto",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="event_contacts",
                        to="locations.country",
                        verbose_name="País",
                    ),
                ),
                (
                    "state",
                    models.ForeignKey(
                        blank=True,
                        help_text="Estado de la persona de contacto",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="event_contacts",
                        to="locations.state",
                        verbose_name="Estado",
                    ),
                ),
            ],
            options={
                "verbose_name": "Contacto de Evento",
                "verbose_name_plural": "Contactos de Eventos",
                "ordering": ["name"],
            },
        ),
        # Restaurar event_contact
        migrations.AddField(
            model_name="event",
            name="event_contact",
            field=models.ForeignKey(
                blank=True,
                help_text="Persona de contacto para el evento",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="events",
                to="events.eventcontact",
                verbose_name="Contacto del Evento",
            ),
        ),
    ]










