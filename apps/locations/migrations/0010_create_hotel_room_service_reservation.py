# Generated manually for hotel reservation system
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("locations", "0009_hotel_contact_email_hotel_contact_name_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="HotelRoom",
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
                    "room_number",
                    models.CharField(
                        help_text="Número o identificador de la habitación",
                        max_length=50,
                        verbose_name="Número de Habitación",
                    ),
                ),
                (
                    "room_type",
                    models.CharField(
                        choices=[
                            ("single", "Individual"),
                            ("double", "Doble"),
                            ("twin", "Dos Camas"),
                            ("triple", "Triple"),
                            ("quad", "Cuádruple"),
                            ("suite", "Suite"),
                            ("family", "Familiar"),
                        ],
                        default="double",
                        max_length=20,
                        verbose_name="Tipo de Habitación",
                    ),
                ),
                (
                    "capacity",
                    models.PositiveIntegerField(
                        help_text="Número máximo de personas que puede alojar",
                        verbose_name="Capacidad",
                    ),
                ),
                (
                    "price_per_night",
                    models.DecimalField(
                        decimal_places=2,
                        help_text="Precio de la habitación por noche",
                        max_digits=10,
                        verbose_name="Precio por Noche",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Descripción de la habitación (amenidades, vista, etc.)",
                        verbose_name="Descripción",
                    ),
                ),
                (
                    "is_available",
                    models.BooleanField(
                        default=True,
                        help_text="Indica si la habitación está disponible para reservas",
                        verbose_name="Disponible",
                    ),
                ),
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
                    "hotel",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="rooms",
                        to="locations.hotel",
                        verbose_name="Hotel",
                    ),
                ),
            ],
            options={
                "verbose_name": "Habitación",
                "verbose_name_plural": "Habitaciones",
                "ordering": ["hotel", "room_number"],
                "unique_together": {("hotel", "room_number")},
            },
        ),
        migrations.CreateModel(
            name="HotelService",
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
                    "service_name",
                    models.CharField(
                        help_text="Nombre del servicio adicional",
                        max_length=200,
                        verbose_name="Nombre del Servicio",
                    ),
                ),
                (
                    "service_type",
                    models.CharField(
                        choices=[
                            ("breakfast", "Desayuno"),
                            ("lunch", "Almuerzo"),
                            ("dinner", "Cena"),
                            ("parking", "Estacionamiento"),
                            ("wifi", "WiFi"),
                            ("laundry", "Lavandería"),
                            ("airport_shuttle", "Transporte al Aeropuerto"),
                            ("gym", "Gimnasio"),
                            ("pool", "Piscina"),
                            ("spa", "Spa"),
                            ("other", "Otro"),
                        ],
                        default="other",
                        max_length=30,
                        verbose_name="Tipo de Servicio",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Descripción detallada del servicio",
                        verbose_name="Descripción",
                    ),
                ),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2,
                        help_text="Precio del servicio",
                        max_digits=10,
                        verbose_name="Precio",
                    ),
                ),
                (
                    "is_per_person",
                    models.BooleanField(
                        default=False,
                        help_text="Indica si el precio es por persona o por servicio",
                        verbose_name="Por Persona",
                    ),
                ),
                (
                    "is_per_night",
                    models.BooleanField(
                        default=False,
                        help_text="Indica si el precio es por noche",
                        verbose_name="Por Noche",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Indica si el servicio está disponible",
                        verbose_name="Activo",
                    ),
                ),
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
                    "hotel",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="services",
                        to="locations.hotel",
                        verbose_name="Hotel",
                    ),
                ),
            ],
            options={
                "verbose_name": "Servicio de Hotel",
                "verbose_name_plural": "Servicios de Hotel",
                "ordering": ["hotel", "service_name"],
            },
        ),
        migrations.CreateModel(
            name="HotelReservation",
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
                    "guest_name",
                    models.CharField(
                        help_text="Nombre completo del huésped principal",
                        max_length=200,
                        verbose_name="Nombre del Huésped",
                    ),
                ),
                (
                    "guest_email",
                    models.EmailField(
                        help_text="Correo electrónico del huésped",
                        max_length=254,
                        verbose_name="Email del Huésped",
                    ),
                ),
                (
                    "guest_phone",
                    models.CharField(
                        help_text="Número de teléfono del huésped",
                        max_length=20,
                        verbose_name="Teléfono del Huésped",
                    ),
                ),
                (
                    "number_of_guests",
                    models.PositiveIntegerField(
                        help_text="Número de personas que se alojarán",
                        verbose_name="Número de Huéspedes",
                    ),
                ),
                (
                    "check_in",
                    models.DateField(
                        help_text="Fecha de entrada", verbose_name="Fecha de Check-in"
                    ),
                ),
                (
                    "check_out",
                    models.DateField(
                        help_text="Fecha de salida", verbose_name="Fecha de Check-out"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pendiente"),
                            ("confirmed", "Confirmada"),
                            ("checked_in", "Check-in Realizado"),
                            ("checked_out", "Check-out Realizado"),
                            ("cancelled", "Cancelada"),
                        ],
                        default="pending",
                        max_length=20,
                        verbose_name="Estado",
                    ),
                ),
                (
                    "total_amount",
                    models.DecimalField(
                        decimal_places=2,
                        default=0.0,
                        help_text="Monto total de la reserva",
                        max_digits=10,
                        verbose_name="Monto Total",
                    ),
                ),
                (
                    "notes",
                    models.TextField(
                        blank=True,
                        help_text="Notas adicionales sobre la reserva",
                        verbose_name="Notas",
                    ),
                ),
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
                    "hotel",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reservations",
                        to="locations.hotel",
                        verbose_name="Hotel",
                    ),
                ),
                (
                    "room",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reservations",
                        to="locations.hotelroom",
                        verbose_name="Habitación",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="Usuario que realiza la reserva",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="hotel_reservations",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Usuario",
                    ),
                ),
            ],
            options={
                "verbose_name": "Reserva de Hotel",
                "verbose_name_plural": "Reservas de Hotel",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="HotelReservationService",
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
                    "quantity",
                    models.PositiveIntegerField(
                        default=1,
                        help_text="Cantidad del servicio",
                        verbose_name="Cantidad",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Fecha de Creación"
                    ),
                ),
                (
                    "reservation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="service_reservations",
                        to="locations.hotelreservation",
                        verbose_name="Reserva",
                    ),
                ),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reservation_services",
                        to="locations.hotelservice",
                        verbose_name="Servicio",
                    ),
                ),
            ],
            options={
                "verbose_name": "Servicio de Reserva",
                "verbose_name_plural": "Servicios de Reserva",
                "unique_together": {("reservation", "service")},
            },
        ),
    ]










