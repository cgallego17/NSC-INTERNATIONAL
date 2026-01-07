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
    buy_out_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Buy Out Fee",
        help_text="Cargo por no hospedarse en el hotel sede",
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


class HotelRoomTax(models.Model):
    """Impuestos aplicables a las habitaciones"""

    event = models.ForeignKey(
        "events.Event",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hotel_taxes",
        verbose_name="Evento",
        help_text="Opcional: Vincular este impuesto a un evento específico",
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Nombre del Impuesto",
        help_text="Nombre descriptivo del impuesto (ej: IVA, Tasa Municipal)",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Monto",
        help_text="Monto fijo del impuesto",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )

    class Meta:
        verbose_name = "Impuesto de Habitación"
        verbose_name_plural = "Impuestos de Habitación"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} (${self.amount})"


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
    name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nombre de la Habitación",
        help_text="Nombre descriptivo de la habitación (ej: Suite Presidencial, Habitación con Vista al Mar)",
    )
    room_type = models.CharField(
        max_length=20,
        choices=ROOM_TYPE_CHOICES,
        default="double",
        verbose_name="Tipo de Habitación",
    )
    capacity = models.PositiveIntegerField(
        verbose_name="Capacidad Total",
        help_text="Número máximo de personas que puede alojar (incluyendo adultos y niños)",
    )
    # Campos de capacidad individuales removidos - ahora se usan las reglas de ocupación (HotelRoomRule)
    # min_adults, max_adults, max_children se mantienen en el modelo para compatibilidad pero no se usan en el formulario
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio por Noche",
        help_text="Precio de la habitación por noche",
    )
    price_includes_guests = models.PositiveIntegerField(
        default=1,
        verbose_name="Personas Incluidas en el Precio",
        help_text="Número de personas incluidas en el precio por noche (si hay personas adicionales, puede haber un cargo extra)",
    )
    additional_guest_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Precio por Persona Adicional",
        help_text="Precio adicional por noche por cada persona que exceda el número de personas incluidas en el precio base",
    )
    breakfast_included = models.BooleanField(
        default=False,
        verbose_name="Desayuno Incluido",
        help_text="Indica si el desayuno está incluido en el precio de la habitación",
    )
    stock = models.PositiveIntegerField(
        default=0,
        verbose_name="Stock",
        help_text="Cantidad de habitaciones disponibles de este tipo",
    )
    taxes = models.ManyToManyField(
        "HotelRoomTax",
        related_name="rooms",
        blank=True,
        verbose_name="Impuestos",
        help_text="Impuestos aplicables a esta habitación",
    )
    amenities = models.ManyToManyField(
        'HotelAmenity',
        related_name='rooms',
        blank=True,
        verbose_name="Amenidades",
        help_text="Amenidades específicas de esta habitación",
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


class HotelRoomRule(models.Model):
    """Reglas de ocupación para habitaciones - Define combinaciones válidas de adultos y niños"""

    room = models.ForeignKey(
        HotelRoom,
        on_delete=models.CASCADE,
        related_name="rules",
        verbose_name="Habitación",
    )
    min_adults = models.PositiveIntegerField(
        verbose_name="Adultos Mínimos",
        help_text="Número mínimo de adultos requeridos en esta regla",
    )
    max_adults = models.PositiveIntegerField(
        verbose_name="Adultos Máximos",
        help_text="Número máximo de adultos permitidos en esta regla",
    )
    min_children = models.PositiveIntegerField(
        default=0,
        verbose_name="Niños Mínimos",
        help_text="Número mínimo de niños requeridos en esta regla",
    )
    max_children = models.PositiveIntegerField(
        default=0,
        verbose_name="Niños Máximos",
        help_text="Número máximo de niños permitidos en esta regla",
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Descripción",
        help_text="Descripción opcional de esta regla (ej: 'Mínimo 1 niño y máximo 3 adultos')",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activa",
        help_text="Indica si esta regla está activa",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Orden",
        help_text="Orden de visualización",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )

    class Meta:
        verbose_name = "Regla de Habitación"
        verbose_name_plural = "Reglas de Habitación"
        ordering = ["room", "order", "min_adults", "min_children"]

    def __str__(self):
        desc = f"Ad: {self.min_adults}-{self.max_adults}, Niños: {self.min_children}-{self.max_children}"
        if self.description:
            return f"{self.description} ({desc})"
        return desc

    def clean(self):
        """Validar que los valores sean consistentes"""
        from django.core.exceptions import ValidationError

        if self.min_adults > self.max_adults:
            raise ValidationError("Los adultos mínimos no pueden ser mayores que los adultos máximos.")
        if self.min_children > self.max_children:
            raise ValidationError("Los niños mínimos no pueden ser mayores que los niños máximos.")
        if self.min_adults + self.min_children > self.room.capacity:
            raise ValidationError(
                f"La suma de adultos mínimos ({self.min_adults}) y niños mínimos ({self.min_children}) "
                f"no puede exceder la capacidad total de la habitación ({self.room.capacity})."
            )
        if self.max_adults + self.max_children > self.room.capacity:
            raise ValidationError(
                f"La suma de adultos máximos ({self.max_adults}) y niños máximos ({self.max_children}) "
                f"no puede exceder la capacidad total de la habitación ({self.room.capacity})."
            )


class HotelRoomImage(models.Model):
    """Galería de imágenes de habitaciones"""

    room = models.ForeignKey(
        HotelRoom,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Habitación",
    )
    media_file = models.ForeignKey(
        "media.MediaFile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hotel_room_images",
        verbose_name="Archivo Multimedia",
        help_text="Archivo seleccionado desde la biblioteca multimedia",
    )
    image = models.ImageField(
        upload_to="hotels/rooms/gallery/",
        blank=True,
        null=True,
        verbose_name="Imagen",
        help_text="Imagen para la galería de la habitación",
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Título",
        help_text="Título o descripción de la imagen",
    )
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Texto Alternativo",
        help_text="Texto alternativo para accesibilidad",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Orden",
        help_text="Orden de visualización",
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name="Destacada",
        help_text="Marca esta imagen como destacada",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )

    class Meta:
        verbose_name = "Imagen de Habitación"
        verbose_name_plural = "Imágenes de Habitaciones"
        ordering = ["room", "order", "-is_featured", "-created_at"]

    def __str__(self):
        return f"{self.room} - Imagen {self.id}"

    @property
    def image_url(self):
        """URL de imagen unificada (MediaFile si existe, fallback a ImageField)."""
        try:
            if self.media_file_id:
                return self.media_file.get_file_url()
        except Exception:
            pass
        try:
            if self.image and hasattr(self.image, "url"):
                return self.image.url
        except Exception:
            pass
        return ""

    @property
    def image_alt(self):
        """Alt text unificado."""
        if self.alt_text:
            return self.alt_text
        try:
            if self.media_file_id and getattr(self.media_file, "alt_text", None):
                return self.media_file.alt_text
        except Exception:
            pass
        return self.title or "Room image"


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


class HotelImage(models.Model):
    """Galería de imágenes del hotel"""

    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Hotel",
    )
    image = models.ImageField(
        upload_to="hotels/gallery/",
        verbose_name="Imagen",
        help_text="Imagen para la galería del hotel",
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Título",
        help_text="Título o descripción de la imagen",
    )
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Texto Alternativo",
        help_text="Texto alternativo para accesibilidad",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Orden",
        help_text="Orden de visualización (menor número aparece primero)",
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name="Destacada",
        help_text="Marcar como imagen destacada/principal",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )

    class Meta:
        verbose_name = "Imagen de Hotel"
        verbose_name_plural = "Imágenes de Hotel"
        ordering = ["hotel", "order", "-is_featured", "-created_at"]

    def __str__(self):
        return f"{self.hotel.hotel_name} - {self.title or 'Imagen'}"


class HotelAmenity(models.Model):
    """Amenidades/servicios incluidos del hotel (sin costo adicional)"""

    AMENITY_CATEGORY_CHOICES = [
        ("general", "General"),
        ("room", "Habitación"),
        ("bathroom", "Baño"),
        ("entertainment", "Entretenimiento"),
        ("food_drink", "Comida y Bebida"),
        ("services", "Servicios"),
        ("accessibility", "Accesibilidad"),
    ]

    AMENITY_ICON_CHOICES = [
        # General
        ("wifi", "WiFi"),
        ("parking", "Estacionamiento"),
        ("pool", "Piscina"),
        ("gym", "Gimnasio"),
        ("spa", "Spa"),
        ("restaurant", "Restaurante"),
        ("bar", "Bar"),
        ("room_service", "Servicio a Habitación"),
        # Habitación
        ("air_conditioning", "Aire Acondicionado"),
        ("heating", "Calefacción"),
        ("tv", "Televisión"),
        ("safe", "Caja Fuerte"),
        ("minibar", "Minibar"),
        ("balcony", "Balcón"),
        # Baño
        ("hairdryer", "Secador de Pelo"),
        ("bathtub", "Bañera"),
        ("shower", "Ducha"),
        # Entretenimiento
        ("cable_tv", "TV por Cable"),
        ("streaming", "Streaming"),
        ("game_room", "Sala de Juegos"),
        # Servicios
        ("laundry", "Lavandería"),
        ("concierge", "Concierge"),
        ("24h_reception", "Recepción 24h"),
        ("airport_shuttle", "Transporte Aeropuerto"),
        ("business_center", "Centro de Negocios"),
        ("meeting_rooms", "Salas de Reuniones"),
        # Accesibilidad
        ("wheelchair_accessible", "Acceso para Sillas de Ruedas"),
        ("elevator", "Ascensor"),
        # Otros
        ("pet_friendly", "Admite Mascotas"),
        ("smoking_area", "Área de Fumadores"),
        ("non_smoking", "No Fumadores"),
        ("family_friendly", "Apto para Familias"),
        ("other", "Otro"),
    ]

    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name="amenities",
        verbose_name="Hotel",
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Nombre",
        help_text="Nombre de la amenidad",
    )
    category = models.CharField(
        max_length=30,
        choices=AMENITY_CATEGORY_CHOICES,
        default="general",
        verbose_name="Categoría",
    )
    icon = models.CharField(
        max_length=30,
        choices=AMENITY_ICON_CHOICES,
        default="other",
        verbose_name="Ícono",
        help_text="Ícono representativo de la amenidad",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
        help_text="Descripción detallada de la amenidad",
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name="Disponible",
        help_text="Indica si la amenidad está disponible actualmente",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Orden",
        help_text="Orden de visualización",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )

    class Meta:
        verbose_name = "Amenidad de Hotel"
        verbose_name_plural = "Amenidades de Hotel"
        ordering = ["hotel", "category", "order", "name"]

    def __str__(self):
        return f"{self.hotel.hotel_name} - {self.name}"

    def get_icon_class(self):
        """Retorna la clase de Font Awesome correspondiente al ícono"""
        icon_mapping = {
            "wifi": "fa-wifi",
            "parking": "fa-parking",
            "pool": "fa-swimming-pool",
            "gym": "fa-dumbbell",
            "spa": "fa-spa",
            "restaurant": "fa-utensils",
            "bar": "fa-glass-martini-alt",
            "room_service": "fa-concierge-bell",
            "air_conditioning": "fa-snowflake",
            "heating": "fa-fire",
            "tv": "fa-tv",
            "safe": "fa-lock",
            "minibar": "fa-wine-bottle",
            "balcony": "fa-door-open",
            "hairdryer": "fa-wind",
            "bathtub": "fa-bath",
            "shower": "fa-shower",
            "cable_tv": "fa-satellite-dish",
            "streaming": "fa-play-circle",
            "game_room": "fa-gamepad",
            "laundry": "fa-tshirt",
            "concierge": "fa-user-tie",
            "24h_reception": "fa-clock",
            "airport_shuttle": "fa-shuttle-van",
            "business_center": "fa-briefcase",
            "meeting_rooms": "fa-users",
            "wheelchair_accessible": "fa-wheelchair",
            "elevator": "fa-elevator",
            "pet_friendly": "fa-paw",
            "smoking_area": "fa-smoking",
            "non_smoking": "fa-smoking-ban",
            "family_friendly": "fa-child",
            "other": "fa-star",
        }
        return icon_mapping.get(self.icon, "fa-check-circle")


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

        # Precio base de la habitación (incluye costo por persona adicional)
        if self.room:
            includes = int(self.room.price_includes_guests or 1)
            extra_guests = max(0, int(self.number_of_guests or 0) - includes)
            per_night_total = self.room.price_per_night + (self.room.additional_guest_price or Decimal("0.00")) * extra_guests
            room_total = per_night_total * nights
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
