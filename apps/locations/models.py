from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


class Country(models.Model):
    """Países donde se juega baseball"""

    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre del País")
    code = models.CharField(
        max_length=3,
        unique=True,
        validators=[MinLengthValidator(2), MaxLengthValidator(3)],
        verbose_name="Código del País",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )

    class Meta:
        verbose_name = "País"
        verbose_name_plural = "Países"
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def states_count(self):
        """Cuenta el número de estados del país"""
        return self.states.count()

    @property
    def cities_count(self):
        """Cuenta el número de ciudades del país"""
        return City.objects.filter(state__country=self).count()

    @property
    def events_count(self):
        """Cuenta el número de eventos del país"""
        return self.events.count()


class State(models.Model):
    """Estados/Provincias de los países"""

    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name="states", verbose_name="País"
    )
    name = models.CharField(max_length=100, verbose_name="Nombre del Estado")
    code = models.CharField(
        max_length=10,
        validators=[MinLengthValidator(2), MaxLengthValidator(10)],
        verbose_name="Código del Estado",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )

    class Meta:
        verbose_name = "Estado"
        verbose_name_plural = "Estados"
        ordering = ["country__name", "name"]
        unique_together = ["country", "name"]

    def __str__(self):
        return f"{self.name}, {self.country.name}"

    @property
    def cities_count(self):
        """Cuenta el número de ciudades del estado"""
        return self.cities.count()

    @property
    def events_count(self):
        """Cuenta el número de eventos del estado"""
        return self.events.count()


class City(models.Model):
    """Ciudades de los estados"""

    state = models.ForeignKey(
        State, on_delete=models.CASCADE, related_name="cities", verbose_name="Estado"
    )
    name = models.CharField(max_length=100, verbose_name="Nombre de la Ciudad")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )

    class Meta:
        verbose_name = "Ciudad"
        verbose_name_plural = "Ciudades"
        ordering = ["state__country__name", "state__name", "name"]
        unique_together = ["state", "name"]

    def __str__(self):
        return f"{self.name}, {self.state.name}, {self.state.country.name}"

    @property
    def events_count(self):
        """Cuenta el número de eventos de la ciudad"""
        return self.events.count()

    @property
    def country(self):
        """Retorna el país de la ciudad"""
        return self.state.country


class Season(models.Model):
    """Temporadas de baseball"""

    SEASON_STATUS_CHOICES = [
        ("upcoming", "Próxima"),
        ("active", "Activa"),
        ("completed", "Completada"),
        ("cancelled", "Cancelada"),
    ]

    SEASON_TYPE_CHOICES = [
        ("regular", "Temporada Regular"),
        ("playoffs", "Playoffs"),
        ("world_series", "Serie Mundial"),
        ("all_star", "Juego de Estrellas"),
        ("spring_training", "Entrenamiento de Primavera"),
        ("winter_league", "Liga de Invierno"),
        ("international", "Competencia Internacional"),
    ]

    name = models.CharField(max_length=100, verbose_name="Nombre de la Temporada")
    year = models.PositiveIntegerField(verbose_name="Año")
    season_type = models.CharField(
        max_length=20,
        choices=SEASON_TYPE_CHOICES,
        default="regular",
        verbose_name="Tipo de Temporada",
    )
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    end_date = models.DateField(verbose_name="Fecha de Fin")
    status = models.CharField(
        max_length=20,
        choices=SEASON_STATUS_CHOICES,
        default="upcoming",
        verbose_name="Estado",
    )
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activa")

    # Información adicional
    total_games = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Total de Juegos"
    )
    teams_count = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Número de Equipos"
    )
    league = models.CharField(max_length=100, blank=True, verbose_name="Liga")

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )

    class Meta:
        verbose_name = "Temporada"
        verbose_name_plural = "Temporadas"
        ordering = ["-year", "-start_date"]
        unique_together = ["name", "year"]

    def __str__(self):
        return f"{self.name} {self.year}"

    @property
    def duration_days(self):
        """Calcula la duración de la temporada en días"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return 0

    @property
    def is_current_season(self):
        """Verifica si es la temporada actual"""
        from django.utils import timezone

        today = timezone.now().date()
        return self.start_date <= today <= self.end_date

    @property
    def progress_percentage(self):
        """Calcula el porcentaje de progreso de la temporada"""
        if not self.start_date or not self.end_date:
            return 0

        from django.utils import timezone

        today = timezone.now().date()

        if today < self.start_date:
            return 0
        elif today > self.end_date:
            return 100

        total_days = self.duration_days
        if total_days == 0:
            return 0

        elapsed_days = (today - self.start_date).days
        return min(100, (elapsed_days / total_days) * 100)

    @property
    def events_count(self):
        """Cuenta el número de eventos asociados a esta temporada"""
        return self.events.count()

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError(
                "La fecha de fin debe ser posterior a la fecha de inicio."
            )


class Rule(models.Model):
    """Modelo para reglas del sistema"""

    RULE_TYPE_CHOICES = [
        ("standard", "Standard Rules"),
        ("modified", "Modified Rules"),
        ("custom", "Custom Rules"),
        ("championship", "Championship Rules"),
        ("exhibition", "Exhibition Rules"),
    ]

    name = models.CharField(max_length=100, unique=True, verbose_name="Rule Name")
    description = models.TextField(blank=True, verbose_name="Description")
    rule_type = models.CharField(
        max_length=20,
        choices=RULE_TYPE_CHOICES,
        default="standard",
        verbose_name="Rule Type",
    )
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Rule"
        verbose_name_plural = "Rules"
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def events_count(self):
        """Cuenta el número de eventos que usan esta regla"""
        return self.events.count()


class Site(models.Model):
    """Sitios/Instalaciones donde se realizan eventos"""

    # Información básica del sitio
    site_name = models.CharField(
        max_length=200,
        verbose_name="Site Name",
        help_text="Nombre del sitio o instalación",
    )
    abbreviation = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Abbreviation",
        help_text="Abreviatura del sitio",
    )

    # Dirección
    address_1 = models.CharField(
        max_length=200, verbose_name="Address 1", help_text="Dirección principal"
    )
    address_2 = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Address 2",
        help_text="Dirección secundaria (opcional)",
    )
    city = models.ForeignKey(
        "City",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sites",
        verbose_name="City",
        help_text="Ciudad",
    )
    state = models.ForeignKey(
        "State",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sites",
        verbose_name="State",
    )
    postal_code = models.CharField(
        max_length=20, verbose_name="Postal Code", help_text="Código postal"
    )
    country = models.ForeignKey(
        "Country",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sites",
        verbose_name="Country",
    )

    # Información adicional
    website = models.URLField(
        blank=True, verbose_name="Website", help_text="Sitio web del lugar"
    )
    additional_info = models.TextField(
        blank=True,
        verbose_name="Additional Info",
        help_text="Información adicional sobre el sitio (ej. Reglas del parque)",
    )

    # Imágenes
    image = models.ImageField(
        upload_to="sites/",
        blank=True,
        null=True,
        verbose_name="Site Image",
        help_text="Imagen principal del sitio",
    )

    # Configuración
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Site"
        verbose_name_plural = "Sites"
        ordering = ["site_name"]

    def __str__(self):
        return self.site_name

    @property
    def full_address(self):
        """Retorna la dirección completa formateada"""
        address_parts = [self.address_1]
        if self.address_2:
            address_parts.append(self.address_2)
        address_parts.extend(
            [
                self.city.name if self.city else "",
                self.state.name if self.state else "",
                self.postal_code,
            ]
        )
        return ", ".join(filter(None, address_parts))

    @property
    def events_count(self):
        """Cuenta el número de eventos en este sitio"""
        return self.events.count() if hasattr(self, "events") else 0


class Hotel(models.Model):
    """Hoteles disponibles para eventos"""

    hotel_name = models.CharField(
        max_length=200,
        verbose_name="Nombre del Hotel",
        help_text="Nombre del hotel",
    )
    address = models.CharField(
        max_length=500,
        verbose_name="Dirección",
        help_text="Dirección completa del hotel",
    )
    photo = models.ImageField(
        upload_to="hotels/",
        blank=True,
        null=True,
        verbose_name="Foto",
        help_text="Foto del hotel",
    )
    information = models.TextField(
        blank=True,
        verbose_name="Información",
        help_text="Información adicional sobre el hotel",
    )
    registration_url = models.URLField(
        blank=True,
        verbose_name="URL Hotel Registro",
        help_text="URL para registro en el hotel",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )

    # Ubicación
    city = models.ForeignKey(
        "City",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hotels",
        verbose_name="Ciudad",
        help_text="Ciudad donde se encuentra el hotel",
    )
    state = models.ForeignKey(
        "State",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hotels",
        verbose_name="Estado",
        help_text="Estado donde se encuentra el hotel",
    )
    country = models.ForeignKey(
        "Country",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hotels",
        verbose_name="País",
        help_text="País donde se encuentra el hotel",
    )

    # Capacidad y contacto
    capacity = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Capacidad",
        help_text="Capacidad del hotel (número de habitaciones o personas)",
    )
    contact_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nombre de Contacto",
        help_text="Nombre de la persona de contacto del hotel",
    )
    contact_email = models.EmailField(
        blank=True,
        verbose_name="Email de Contacto",
        help_text="Correo electrónico de la persona de contacto",
    )
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Teléfono de Contacto",
        help_text="Número de teléfono de la persona de contacto",
    )

    class Meta:
        verbose_name = "Hotel"
        verbose_name_plural = "Hoteles"
        ordering = ["hotel_name"]

    def __str__(self):
        return self.hotel_name

    @property
    def total_rooms(self):
        """Retorna el total de habitaciones del hotel"""
        return self.rooms.count()

    @property
    def available_rooms_count(self):
        """Retorna el número de habitaciones disponibles"""
        return self.rooms.filter(is_available=True).count()


class HotelRoom(models.Model):
    """Habitaciones de los hoteles"""

    ROOM_TYPE_CHOICES = [
        ("single", "Individual"),
        ("double", "Doble"),
        ("twin", "Dos Camas"),
        ("triple", "Triple"),
        ("quad", "Cuádruple"),
        ("suite", "Suite"),
        ("family", "Familiar"),
    ]

    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name="rooms",
        verbose_name="Hotel",
    )
    room_number = models.CharField(
        max_length=50,
        verbose_name="Número de Habitación",
        help_text="Número o identificador de la habitación",
    )
    room_type = models.CharField(
        max_length=20,
        choices=ROOM_TYPE_CHOICES,
        default="double",
        verbose_name="Tipo de Habitación",
    )
    capacity = models.PositiveIntegerField(
        verbose_name="Capacidad",
        help_text="Número máximo de personas que puede alojar",
    )
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio por Noche",
        help_text="Precio de la habitación por noche",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
        help_text="Descripción de la habitación (amenidades, vista, etc.)",
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name="Disponible",
        help_text="Indica si la habitación está disponible para reservas",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )

    class Meta:
        verbose_name = "Habitación"
        verbose_name_plural = "Habitaciones"
        ordering = ["hotel", "room_number"]
        unique_together = ["hotel", "room_number"]

    def __str__(self):
        return f"{self.hotel.hotel_name} - Habitación {self.room_number}"

    @property
    def is_reserved(self):
        """Verifica si la habitación tiene reservas activas"""
        from django.utils import timezone

        today = timezone.now().date()
        return self.reservations.filter(
            check_in__lte=today,
            check_out__gte=today,
            status__in=["confirmed", "checked_in"],
        ).exists()


class HotelService(models.Model):
    """Servicios adicionales que ofrece el hotel con costo"""

    SERVICE_TYPE_CHOICES = [
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
    ]

    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name="services",
        verbose_name="Hotel",
    )
    service_name = models.CharField(
        max_length=200,
        verbose_name="Nombre del Servicio",
        help_text="Nombre del servicio adicional",
    )
    service_type = models.CharField(
        max_length=30,
        choices=SERVICE_TYPE_CHOICES,
        default="other",
        verbose_name="Tipo de Servicio",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
        help_text="Descripción detallada del servicio",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio",
        help_text="Precio del servicio",
    )
    is_per_person = models.BooleanField(
        default=False,
        verbose_name="Por Persona",
        help_text="Indica si el precio es por persona o por servicio",
    )
    is_per_night = models.BooleanField(
        default=False,
        verbose_name="Por Noche",
        help_text="Indica si el precio es por noche",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Indica si el servicio está disponible",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )

    class Meta:
        verbose_name = "Servicio de Hotel"
        verbose_name_plural = "Servicios de Hotel"
        ordering = ["hotel", "service_name"]

    def __str__(self):
        return f"{self.hotel.hotel_name} - {self.service_name}"


class HotelReservation(models.Model):
    """Reservas de hoteles"""

    RESERVATION_STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("confirmed", "Confirmada"),
        ("checked_in", "Check-in Realizado"),
        ("checked_out", "Check-out Realizado"),
        ("cancelled", "Cancelada"),
    ]

    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name="reservations",
        verbose_name="Hotel",
    )
    room = models.ForeignKey(
        HotelRoom,
        on_delete=models.CASCADE,
        related_name="reservations",
        verbose_name="Habitación",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="hotel_reservations",
        verbose_name="Usuario",
        help_text="Usuario que realiza la reserva",
    )
    guest_name = models.CharField(
        max_length=200,
        verbose_name="Nombre del Huésped",
        help_text="Nombre completo del huésped principal",
    )
    guest_email = models.EmailField(
        verbose_name="Email del Huésped",
        help_text="Correo electrónico del huésped",
    )
    guest_phone = models.CharField(
        max_length=20,
        verbose_name="Teléfono del Huésped",
        help_text="Número de teléfono del huésped",
    )
    number_of_guests = models.PositiveIntegerField(
        verbose_name="Número de Huéspedes",
        help_text="Número de personas que se alojarán",
    )
    check_in = models.DateField(
        verbose_name="Fecha de Check-in",
        help_text="Fecha de entrada",
    )
    check_out = models.DateField(
        verbose_name="Fecha de Check-out",
        help_text="Fecha de salida",
    )
    status = models.CharField(
        max_length=20,
        choices=RESERVATION_STATUS_CHOICES,
        default="pending",
        verbose_name="Estado",
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Monto Total",
        help_text="Monto total de la reserva",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notas",
        help_text="Notas adicionales sobre la reserva",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )

    class Meta:
        verbose_name = "Reserva de Hotel"
        verbose_name_plural = "Reservas de Hotel"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Reserva #{self.id} - {self.hotel.hotel_name} - {self.guest_name}"

    def calculate_total(self):
        """Calcula el total de la reserva"""
        from django.utils import timezone
        from datetime import timedelta

        # Calcular número de noches
        if self.check_in and self.check_out:
            nights = (self.check_out - self.check_in).days
        else:
            nights = 0

        # Precio base de la habitación
        if self.room:
            room_total = self.room.price_per_night * nights
        else:
            room_total = Decimal("0.00")

        # Agregar servicios adicionales (solo si el objeto ya tiene un ID)
        services_total = Decimal("0.00")
        if self.pk:  # Solo si el objeto ya está guardado
            for service_reservation in self.service_reservations.all():
                service = service_reservation.service
                if service.is_per_person:
                    service_price = service.price * self.number_of_guests
                else:
                    service_price = service.price

                if service.is_per_night:
                    service_price = service_price * nights

                services_total += service_price * service_reservation.quantity

        return room_total + services_total

    def save(self, *args, **kwargs):
        """Sobrescribe save para calcular el total automáticamente"""
        # Calcular total antes de guardar
        self.total_amount = self.calculate_total()
        super().save(*args, **kwargs)

    @property
    def number_of_nights(self):
        """Calcula el número de noches"""
        if self.check_in and self.check_out:
            return (self.check_out - self.check_in).days
        return 0


class HotelReservationService(models.Model):
    """Servicios adicionales asociados a una reserva"""

    reservation = models.ForeignKey(
        HotelReservation,
        on_delete=models.CASCADE,
        related_name="service_reservations",
        verbose_name="Reserva",
    )
    service = models.ForeignKey(
        HotelService,
        on_delete=models.CASCADE,
        related_name="reservation_services",
        verbose_name="Servicio",
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Cantidad",
        help_text="Cantidad del servicio",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )

    class Meta:
        verbose_name = "Servicio de Reserva"
        verbose_name_plural = "Servicios de Reserva"
        unique_together = ["reservation", "service"]

    def __str__(self):
        return f"{self.reservation} - {self.service.service_name}"
