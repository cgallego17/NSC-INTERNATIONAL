from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class EventCategory(models.Model):
    """Categorías de eventos"""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(
        max_length=7, default="#6675ed", help_text="Color en formato hexadecimal"
    )
    icon = models.CharField(
        max_length=50,
        default="fas fa-calendar",
        help_text="Clase de icono Font Awesome",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Categoría de Evento"
        verbose_name_plural = "Categorías de Eventos"
        ordering = ["name"]

    def __str__(self):
        return self.name


class EventType(models.Model):
    """Tipos de eventos (LIGA, SHOWCASES, TORNEO, WORLD SERIES)"""

    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Tipo")
    description = models.TextField(blank=True, verbose_name="Descripción")
    color = models.CharField(
        max_length=7, default="#0d2c54", help_text="Color en formato hexadecimal"
    )
    icon = models.CharField(
        max_length=50,
        default="fas fa-calendar",
        help_text="Clase de icono Font Awesome",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tipo de Evento"
        verbose_name_plural = "Tipos de Eventos"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Division(models.Model):
    """Divisiones de eventos"""

    name = models.CharField(
        max_length=100, unique=True, verbose_name="Nombre de la División"
    )
    description = models.TextField(blank=True, verbose_name="Descripción")
    age_min = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Edad Mínima"
    )
    age_max = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Edad Máxima"
    )
    skill_level = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Nivel de Habilidad",
        help_text="Ej: Principiante, Intermedio, Avanzado",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "División"
        verbose_name_plural = "Divisiones"
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def age_range(self):
        """Retorna el rango de edad como string"""
        if self.age_min and self.age_max:
            return f"{self.age_min}-{self.age_max} años"
        elif self.age_min:
            return f"{self.age_min}+ años"
        elif self.age_max:
            return f"Hasta {self.age_max} años"
        return "Sin restricción de edad"


class GateFeeType(models.Model):
    """Tipos de tarifa de entrada"""

    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Tipo")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tipo de Tarifa de Entrada"
        verbose_name_plural = "Tipos de Tarifas de Entrada"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Event(models.Model):
    """Modelo de eventos"""

    STATUS_CHOICES = [
        ("draft", "Borrador"),
        ("published", "Publicado"),
        ("cancelled", "Cancelado"),
        ("completed", "Completado"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Baja"),
        ("medium", "Media"),
        ("high", "Alta"),
        ("urgent", "Urgente"),
    ]

    STATURE_CHOICES = [
        ("single_points", "Single Points Event"),
        ("double_points", "Double Points Event"),
        ("championship", "Championship Event"),
        ("exhibition", "Exhibition Event"),
    ]

    REGION_CHOICES = [
        ("north", "North Region"),
        ("south", "South Region"),
        ("east", "East Region"),
        ("west", "West Region"),
        ("central", "Central Region"),
    ]

    # Información básica del evento
    title = models.CharField(max_length=200, verbose_name="Event Name")
    short_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Event Short Name",
        help_text="If provided, the short name will be used in event notifications sent via SMS",
    )
    description = models.TextField(verbose_name="Short Description")
    tags = models.CharField(max_length=500, blank=True, verbose_name="Tags")

    # Información específica por tipo de usuario - Individual Player
    description_player = models.TextField(
        blank=True,
        verbose_name="Description (Individual Player)",
        help_text="Descripción del evento para Individual Players",
    )

    # Información específica por tipo de usuario - Team Manager
    title_team_manager = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Event Name (Team Manager)",
        help_text="Nombre del evento para Team Managers",
    )
    description_team_manager = models.TextField(
        blank=True,
        verbose_name="Description (Team Manager)",
        help_text="Descripción del evento para Team Managers",
    )

    # Información específica por tipo de usuario - Spectator
    title_spectator = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Event Name (Spectator)",
        help_text="Nombre del evento para Spectators",
    )
    description_spectator = models.TextField(
        blank=True,
        verbose_name="Description (Spectator)",
        help_text="Descripción del evento para Spectators",
    )

    # Categorización
    category = models.ForeignKey(
        EventCategory,
        on_delete=models.CASCADE,
        related_name="events",
        null=True,
        blank=True,
    )
    event_type = models.ForeignKey(
        "EventType",
        on_delete=models.SET_NULL,
        related_name="events",
        verbose_name="Tipo de Evento",
        null=True,
        blank=True,
    )
    divisions = models.ManyToManyField(
        Division,
        blank=True,
        related_name="events",
        verbose_name="Divisiones",
        help_text="Puedes seleccionar una o más divisiones para este evento",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="medium"
    )

    # Ubicación
    location = models.CharField(max_length=200, blank=True)
    address = models.TextField(blank=True)

    # Relaciones con ubicaciones (requeridas)
    season = models.ForeignKey(
        "locations.Season",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
        verbose_name="Season",
    )
    country = models.ForeignKey(
        "locations.Country",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
        verbose_name="Country",
    )
    state = models.ForeignKey(
        "locations.State",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
        verbose_name="State",
    )
    city = models.ForeignKey(
        "locations.City",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
        verbose_name="City",
    )

    # Sitio primario del evento
    primary_site = models.ForeignKey(
        "locations.Site",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="primary_events",
        verbose_name="Primary Site",
        help_text="Sitio principal donde se realizará el evento",
    )

    # Sitios adicionales del evento
    additional_sites = models.ManyToManyField(
        "locations.Site",
        blank=True,
        related_name="additional_events",
        verbose_name="Additional Sites",
        help_text="Sitios adicionales donde se realizará el evento",
    )

    # Configuración del evento
    region = models.CharField(
        max_length=20, choices=REGION_CHOICES, blank=True, verbose_name="Region"
    )
    rule = models.ForeignKey(
        "locations.Rule",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
        verbose_name="Rule Set",
    )
    stature = models.CharField(
        max_length=20,
        choices=STATURE_CHOICES,
        default="single_points",
        verbose_name="Stature",
    )

    # Fechas y horarios
    start_date = models.DateField(verbose_name="Start Date", null=True, blank=True)
    end_date = models.DateField(verbose_name="End Date", null=True, blank=True)
    entry_deadline = models.DateField(
        verbose_name="Entry Deadline", null=True, blank=True
    )
    all_day = models.BooleanField(default=False)

    # Configuración de participación
    allow_withdrawals = models.BooleanField(
        default=False, verbose_name="Allow Withdrawals"
    )
    withdraw_deadline = models.DateField(
        verbose_name="Withdraw Deadline", null=True, blank=True
    )
    freeze_rosters = models.BooleanField(default=False, verbose_name="Freeze Rosters")
    roster_freeze_date = models.DateField(
        verbose_name="Roster Freeze Date", null=True, blank=True
    )

    # Tarifas y pagos
    default_entry_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Default Entry Fee",
        null=True,
        blank=True,
    )
    payment_deadline = models.DateField(
        verbose_name="Payment Deadline", null=True, blank=True
    )

    # Tarifas y pagos específicos por tipo de usuario - Team Manager
    default_entry_fee_team_manager = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Default Entry Fee (Team Manager)",
        null=True,
        blank=True,
    )
    payment_deadline_team_manager = models.DateField(
        verbose_name="Payment Deadline (Team Manager)", null=True, blank=True
    )
    gate_fee_amount_team_manager = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Gate Fee Amount (Team Manager)",
        null=True,
        blank=True,
    )
    service_fee_team_manager = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Service Fee (%) (Team Manager)",
        null=True,
        blank=True,
        default=0.00,
    )

    # Tarifas y pagos específicos por tipo de usuario - Spectator
    default_entry_fee_spectator = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Default Entry Fee (Spectator)",
        null=True,
        blank=True,
    )
    payment_deadline_spectator = models.DateField(
        verbose_name="Payment Deadline (Spectator)", null=True, blank=True
    )
    gate_fee_amount_spectator = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Gate Fee Amount (Spectator)",
        null=True,
        blank=True,
    )
    service_fee_spectator = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Service Fee (%) (Spectator)",
        null=True,
        blank=True,
        default=0.00,
    )
    gate_fee_type_team_manager = models.ForeignKey(
        "GateFeeType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events_team_manager",
        verbose_name="Tipo de Tarifa de Entrada (Team Manager)",
        help_text="Tipo de tarifa de entrada para Team Manager",
    )
    gate_fee_type_spectator = models.ForeignKey(
        "GateFeeType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events_spectator",
        verbose_name="Tipo de Tarifa de Entrada (Spectator)",
        help_text="Tipo de tarifa de entrada para Spectator",
    )

    accept_deposits = models.BooleanField(default=False, verbose_name="Accept Deposits")
    default_deposit_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Default Deposit Amount",
        null=True,
        blank=True,
    )
    allow_online_pay = models.BooleanField(
        default=False, verbose_name="Allow Online Pay"
    )

    # Tarifas de entrada
    has_gate_fee = models.BooleanField(default=False, verbose_name="Has Gate Fee")
    gate_fee_type = models.ForeignKey(
        "GateFeeType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
        verbose_name="Tipo de Tarifa de Entrada",
        help_text="Tipo de tarifa de entrada (Player Gate Fee, Spectator Gate Fee, etc.)",
    )
    gate_fee_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Gate Fee Amount",
        null=True,
        blank=True,
    )
    service_fee = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Service Fee (%)",
        null=True,
        blank=True,
        default=0.00,
        help_text="Service fee percentage to be added to the checkout total",
    )

    # Recordatorios y solicitudes
    send_payment_reminders = models.BooleanField(
        default=False, verbose_name="Send Payment Reminders"
    )
    payment_reminder_date = models.DateField(
        verbose_name="Payment Reminder Date", null=True, blank=True
    )
    accept_schedule_requests = models.BooleanField(
        default=False, verbose_name="Accept Schedule Requests"
    )
    schedule_request_deadline = models.DateField(
        verbose_name="Schedule Request Deadline", null=True, blank=True
    )

    # Organización
    organizer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="organized_events"
    )
    attendees = models.ManyToManyField(
        User, through="EventAttendance", related_name="attended_events"
    )

    # Configuración
    is_public = models.BooleanField(default=False)
    max_attendees = models.PositiveIntegerField(
        null=True, blank=True, help_text="Límite de asistentes (opcional)"
    )
    requires_registration = models.BooleanField(default=False)

    # Información adicional
    image = models.ImageField(upload_to="events/", blank=True, null=True)
    banner = models.URLField(
        blank=True,
        null=True,
        help_text="URL del banner del evento desde el sistema multimedia",
        verbose_name="Banner del Evento",
    )
    banner_mobile = models.URLField(
        blank=True,
        null=True,
        help_text="URL del banner móvil del evento desde el sistema multimedia",
        verbose_name="Banner Móvil del Evento",
    )
    logo = models.URLField(
        blank=True,
        null=True,
        help_text="URL del logo del evento desde el sistema multimedia",
        verbose_name="Logo del Evento",
    )
    external_link = models.URLField(blank=True, help_text="Enlace externo relacionado")
    notes = models.TextField(blank=True, help_text="Notas internas")

    # Campos restaurados
    stripe_payment_profile = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="ID del perfil de pago de Stripe para este evento",
        verbose_name="Perfil de Pago Stripe",
    )
    display_player_list = models.BooleanField(
        default=False,
        help_text="Mostrar lista de jugadores en el evento",
        verbose_name="Display Player List",
    )
    hotel = models.ForeignKey(
        "locations.Hotel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="primary_events",
        help_text="Hotel sede principal donde se alojarán los participantes del evento",
        verbose_name="Hotel Sede",
    )
    additional_hotels = models.ManyToManyField(
        "locations.Hotel",
        blank=True,
        related_name="additional_events",
        help_text="Hoteles adicionales donde se alojarán los participantes del evento",
        verbose_name="Hoteles Adicionales",
    )
    event_contact = models.ManyToManyField(
        "events.EventContact",
        blank=True,
        related_name="events",
        help_text="Personas de contacto para el evento",
        verbose_name="Contactos del Evento",
    )
    email_welcome_body = models.TextField(
        blank=True,
        null=True,
        help_text="Contenido HTML del correo de bienvenida que se enviará a los participantes",
        verbose_name="Cuerpo del Correo de Bienvenida (HTML)",
    )
    video_url = models.URLField(
        blank=True,
        null=True,
        help_text=_("URL of the event video (YouTube, Vimeo, etc.)"),
        verbose_name=_("Event Video"),
    )
    views = models.PositiveIntegerField(default=0, verbose_name="Visitas")

    # Fechas del sistema
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ["-start_date"]

    def __str__(self):
        return self.title

    @property
    def is_past(self):
        """Verifica si el evento ya pasó"""
        from django.utils import timezone

        if not self.end_date:
            return False
        return self.end_date < timezone.now().date()

    @property
    def is_ongoing(self):
        """Verifica si el evento está en curso"""
        from django.utils import timezone

        if not self.start_date or not self.end_date:
            return False
        now = timezone.now().date()
        return self.start_date <= now <= self.end_date

    @property
    def is_upcoming(self):
        """Verifica si el evento es futuro"""
        from django.utils import timezone

        if not self.start_date:
            return False
        return self.start_date > timezone.now().date()

    @property
    def attendees_count(self):
        """Cuenta el número de asistentes confirmados"""
        return self.attendees.filter(eventattendance__status="confirmed").count()

    @property
    def is_full(self):
        """Verifica si el evento está lleno"""
        if not self.max_attendees:
            return False
        return self.attendees_count >= self.max_attendees

    @property
    def duration(self):
        """Calcula la duración del evento"""
        return self.end_date - self.start_date

    @property
    def full_location(self):
        """Retorna la ubicación completa del evento"""
        location_parts = []
        if self.city:
            location_parts.append(self.city.name)
        if self.state:
            location_parts.append(self.state.name)
        if self.country:
            location_parts.append(self.country.name)

        if location_parts:
            return ", ".join(location_parts)
        elif self.location:
            return self.location
        else:
            return "Ubicación no especificada"

    @property
    def is_baseball_event(self):
        """Verifica si el evento está relacionado con baseball"""
        return self.season is not None

    def clean(self):
        """Validaciones personalizadas"""
        from django.core.exceptions import ValidationError

        # Validar que la fecha de fin sea posterior a la de inicio
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError(
                "La fecha de fin debe ser posterior a la fecha de inicio."
            )

        # Validar consistencia de ubicaciones
        if self.city and self.state and self.city.state != self.state:
            raise ValidationError("La ciudad debe pertenecer al estado seleccionado.")

        if self.state and self.country and self.state.country != self.country:
            raise ValidationError("El estado debe pertenecer al país seleccionado.")

        if self.city and self.country and self.city.state.country != self.country:
            raise ValidationError("La ciudad debe pertenecer al país seleccionado.")


class EventView(models.Model):
    """Registro de visitas a eventos"""

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="event_views"
    )
    ip_address = models.GenericIPAddressField(verbose_name="Dirección IP")
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="event_views",
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Visita de Evento"
        verbose_name_plural = "Visitas de Eventos"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event", "ip_address"]),
            models.Index(fields=["event", "session_key"]),
        ]

    def __str__(self):
        return f"{self.event.title} - {self.ip_address}"


class EventAttendance(models.Model):
    """Asistencia a eventos"""

    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("confirmed", "Confirmado"),
        ("cancelled", "Cancelado"),
        ("waiting", "Lista de espera"),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    registered_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Asistencia a Evento"
        verbose_name_plural = "Asistencias a Eventos"
        unique_together = ["event", "user"]
        ordering = ["-registered_at"]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.event.title}"


class EventComment(models.Model):
    """Comentarios en eventos"""

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    is_internal = models.BooleanField(
        default=False, help_text="Comentario interno solo visible para organizadores"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Comentario de Evento"
        verbose_name_plural = "Comentarios de Eventos"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comentario de {self.user.get_full_name()} en {self.event.title}"


class EventItinerary(models.Model):
    """Itinerario diario del evento"""

    USER_TYPE_CHOICES = [
        ("player", "Jugador"),
        ("team_manager", "Team Manager"),
        ("spectator", "Spectator"),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="itinerary_items",
        verbose_name="Evento",
    )
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default="player",
        verbose_name="Tipo de Usuario",
        help_text="Tipo de usuario para el que es este itinerario",
    )
    day = models.DateField(verbose_name="Día", help_text="Fecha del día del itinerario")
    day_number = models.PositiveIntegerField(
        verbose_name="Número de Día",
        help_text="Número del día en el evento (Día 1, Día 2, etc.)",
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Título del Día",
        help_text="Título o nombre del día (ej: 'Día de Apertura', 'Día de Competencia', etc.)",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
        help_text="Descripción detallada de las actividades del día",
    )
    schedule_items = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Actividades del Día",
        help_text="Lista de actividades con hora y descripción (formato JSON)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Item de Itinerario"
        verbose_name_plural = "Items de Itinerario"
        ordering = ["user_type", "day", "day_number"]
        unique_together = [["event", "user_type", "day"]]
        indexes = [
            models.Index(fields=["event", "user_type", "day"]),
        ]

    def __str__(self):
        user_type_display = self.get_user_type_display()
        return f"{self.event.title} - {self.title} ({user_type_display}) - {self.day}"


class EventIncludes(models.Model):
    """Items incluidos en el evento por tipo de usuario"""

    USER_TYPE_CHOICES = [
        ("player", "Jugador"),
        ("team_manager", "Team Manager"),
        ("spectator", "Spectator"),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="includes_items",
        verbose_name="Evento",
    )
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default="player",
        verbose_name="Tipo de Usuario",
        help_text="Tipo de usuario para el que es este item incluido",
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Título",
        help_text="Título del item incluido (ej: 'Comida incluida', 'Transporte incluido', etc.)",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
        help_text="Descripción detallada del item incluido (opcional)",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Orden",
        help_text="Orden de visualización (menor número aparece primero)",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Indica si este item está activo y se mostrará",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Item Incluido"
        verbose_name_plural = "Items Incluidos"
        ordering = ["user_type", "order", "title"]
        unique_together = [["event", "user_type", "title"]]
        indexes = [
            models.Index(fields=["event", "user_type", "order"]),
        ]

    def __str__(self):
        user_type_display = self.get_user_type_display()
        return f"{self.event.title} - {self.title} ({user_type_display})"


class EventReminder(models.Model):
    """Recordatorios de eventos"""

    REMINDER_TYPES = [
        ("email", "Email"),
        ("notification", "Notificación"),
        ("sms", "SMS"),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="reminders")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reminder_type = models.CharField(
        max_length=20, choices=REMINDER_TYPES, default="notification"
    )
    minutes_before = models.PositiveIntegerField(help_text="Minutos antes del evento")
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Recordatorio de Evento"
        verbose_name_plural = "Recordatorios de Eventos"
        unique_together = ["event", "user", "minutes_before"]

    def __str__(self):
        return f"Recordatorio para {self.user.get_full_name()} - {self.event.title}"


class EventContact(models.Model):
    """Contacto para eventos"""

    name = models.CharField(
        max_length=200,
        help_text="Nombre completo de la persona de contacto",
        verbose_name="Nombre",
    )
    position = models.CharField(
        max_length=200,
        blank=True,
        help_text="Cargo o posición (ej: Director Ejecutivo, Coordinador, Manager)",
        verbose_name="Cargo",
    )
    organization = models.CharField(
        max_length=200,
        blank=True,
        help_text="Organización o empresa a la que pertenece",
        verbose_name="Organización",
    )
    photo = models.ImageField(
        upload_to="event_contacts/",
        blank=True,
        null=True,
        help_text="Foto de la persona de contacto",
        verbose_name="Foto",
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Número de teléfono de contacto",
        verbose_name="Teléfono",
    )
    email = models.EmailField(
        blank=True,
        help_text="Correo electrónico de contacto",
        verbose_name="Email",
    )
    information = models.TextField(
        blank=True,
        help_text="Información adicional sobre el contacto",
        verbose_name="Información",
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
        "locations.City",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="event_contacts",
        help_text="Ciudad de la persona de contacto",
        verbose_name="Ciudad",
    )
    state = models.ForeignKey(
        "locations.State",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="event_contacts",
        help_text="Estado de la persona de contacto",
        verbose_name="Estado",
    )
    country = models.ForeignKey(
        "locations.Country",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="event_contacts",
        help_text="País de la persona de contacto",
        verbose_name="País",
    )

    class Meta:
        verbose_name = "Contacto"
        verbose_name_plural = "Contactos"
        ordering = ["name"]

    def __str__(self):
        if self.position and self.organization:
            return f"{self.name} - {self.position} ({self.organization})"
        elif self.position:
            return f"{self.name} - {self.position}"
        elif self.organization:
            return f"{self.name} ({self.organization})"
        return self.name

    @property
    def display_title(self):
        """Retorna el cargo y organización formateado"""
        if self.position and self.organization:
            return f"{self.position} en {self.organization}"
        elif self.position:
            return self.position
        elif self.organization:
            return self.organization
        return ""


class EventService(models.Model):
    """Servicios adicionales que ofrece el evento con costo"""

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
        ("transportation", "Transporte"),
        ("meal_plan", "Plan de Comidas"),
        ("equipment_rental", "Alquiler de Equipo"),
        ("tournament_fee", "Tarifa de Torneo"),
        ("registration_packet", "Paquete de Registro"),
        ("merchandise", "Mercancía"),
        ("other", "Otro"),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="additional_services",
        verbose_name="Evento",
        help_text="Evento al que pertenece este servicio adicional",
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
        help_text="Indica si el precio es por noche (útil para servicios de hotel)",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Indica si el servicio está disponible para este evento",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Orden",
        help_text="Orden de visualización (menor número aparece primero)",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )

    class Meta:
        verbose_name = "Servicio Adicional del Evento"
        verbose_name_plural = "Servicios Adicionales del Evento"
        ordering = ["event", "order", "service_name"]

    def __str__(self):
        return (
            f"{self.event.title if self.event else 'Sin Evento'} - {self.service_name}"
        )

    def get_service_type_display_with_icon(self):
        """Retorna el tipo de servicio con un ícono"""
        icon_mapping = {
            "breakfast": "fa-coffee",
            "lunch": "fa-utensils",
            "dinner": "fa-utensils",
            "parking": "fa-parking",
            "wifi": "fa-wifi",
            "laundry": "fa-tshirt",
            "airport_shuttle": "fa-shuttle-van",
            "gym": "fa-dumbbell",
            "pool": "fa-swimming-pool",
            "spa": "fa-spa",
            "transportation": "fa-bus",
            "meal_plan": "fa-plate-wheat",
            "equipment_rental": "fa-baseball-bat-ball",
            "tournament_fee": "fa-trophy",
            "registration_packet": "fa-box",
            "merchandise": "fa-tshirt",
            "other": "fa-star",
        }
        icon = icon_mapping.get(self.service_type, "fa-check-circle")
        return f"<i class='fas {icon}'></i> {self.get_service_type_display()}"
