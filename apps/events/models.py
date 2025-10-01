from django.contrib.auth.models import User
from django.db import models


class EventCategory(models.Model):
    """Categorías de eventos"""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default="#6675ed", help_text="Color en formato hexadecimal")
    icon = models.CharField(max_length=50, default="fas fa-calendar", help_text="Clase de icono Font Awesome")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Categoría de Evento"
        verbose_name_plural = "Categorías de Eventos"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Division(models.Model):
    """Divisiones de eventos"""

    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la División")
    description = models.TextField(blank=True, verbose_name="Descripción")
    age_min = models.PositiveIntegerField(null=True, blank=True, verbose_name="Edad Mínima")
    age_max = models.PositiveIntegerField(null=True, blank=True, verbose_name="Edad Máxima")
    skill_level = models.CharField(
        max_length=50, blank=True, verbose_name="Nivel de Habilidad", help_text="Ej: Principiante, Intermedio, Avanzado"
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

    # Categorización
    category = models.ForeignKey(EventCategory, on_delete=models.CASCADE, related_name="events")
    division = models.ForeignKey(
        Division, on_delete=models.SET_NULL, null=True, blank=True, related_name="events", verbose_name="División"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")

    # Ubicación
    location = models.CharField(max_length=200, blank=True)
    address = models.TextField(blank=True)

    # Relaciones con ubicaciones (requeridas)
    season = models.ForeignKey(
        "locations.Season", on_delete=models.SET_NULL, null=True, blank=True, related_name="events", verbose_name="Season"
    )
    country = models.ForeignKey(
        "locations.Country", on_delete=models.SET_NULL, null=True, blank=True, related_name="events", verbose_name="Country"
    )
    state = models.ForeignKey(
        "locations.State", on_delete=models.SET_NULL, null=True, blank=True, related_name="events", verbose_name="State"
    )
    city = models.ForeignKey(
        "locations.City", on_delete=models.SET_NULL, null=True, blank=True, related_name="events", verbose_name="City"
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
    region = models.CharField(max_length=20, choices=REGION_CHOICES, blank=True, verbose_name="Region")
    rule = models.ForeignKey(
        "locations.Rule", on_delete=models.SET_NULL, null=True, blank=True, related_name="events", verbose_name="Rule Set"
    )
    stature = models.CharField(max_length=20, choices=STATURE_CHOICES, default="single_points", verbose_name="Stature")

    # Fechas y horarios
    start_date = models.DateField(verbose_name="Start Date", null=True, blank=True)
    end_date = models.DateField(verbose_name="End Date", null=True, blank=True)
    entry_deadline = models.DateField(verbose_name="Entry Deadline", null=True, blank=True)
    all_day = models.BooleanField(default=False)

    # Configuración de participación
    allow_withdrawals = models.BooleanField(default=False, verbose_name="Allow Withdrawals")
    withdraw_deadline = models.DateField(verbose_name="Withdraw Deadline", null=True, blank=True)
    freeze_rosters = models.BooleanField(default=False, verbose_name="Freeze Rosters")
    roster_freeze_date = models.DateField(verbose_name="Roster Freeze Date", null=True, blank=True)

    # Tarifas y pagos
    default_entry_fee = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Default Entry Fee", null=True, blank=True
    )
    payment_deadline = models.DateField(verbose_name="Payment Deadline", null=True, blank=True)
    accept_deposits = models.BooleanField(default=False, verbose_name="Accept Deposits")
    default_deposit_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Default Deposit Amount", null=True, blank=True
    )
    allow_online_pay = models.BooleanField(default=False, verbose_name="Allow Online Pay")

    # Tarifas de entrada
    has_gate_fee = models.BooleanField(default=False, verbose_name="Has Gate Fee")
    GATE_FEE_TYPE_CHOICES = [
        ("per_person", "Per Person"),
        ("per_car", "Per Car"),
        ("per_day", "Per Day"),
        ("flat_fee", "Flat Fee"),
    ]
    gate_fee_type = models.CharField(
        max_length=20, choices=GATE_FEE_TYPE_CHOICES, null=True, blank=True, verbose_name="Gate Fee Type"
    )
    gate_fee_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Gate Fee Amount", null=True, blank=True
    )

    # Recordatorios y solicitudes
    send_payment_reminders = models.BooleanField(default=False, verbose_name="Send Payment Reminders")
    payment_reminder_date = models.DateField(verbose_name="Payment Reminder Date", null=True, blank=True)
    accept_schedule_requests = models.BooleanField(default=False, verbose_name="Accept Schedule Requests")
    schedule_request_deadline = models.DateField(verbose_name="Schedule Request Deadline", null=True, blank=True)

    # Organización
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_events")
    attendees = models.ManyToManyField(User, through="EventAttendance", related_name="attended_events")

    # Configuración
    is_public = models.BooleanField(default=False)
    max_attendees = models.PositiveIntegerField(null=True, blank=True, help_text="Límite de asistentes (opcional)")
    requires_registration = models.BooleanField(default=False)

    # Información adicional
    image = models.ImageField(upload_to="events/", blank=True, null=True)
    external_link = models.URLField(blank=True, help_text="Enlace externo relacionado")
    notes = models.TextField(blank=True, help_text="Notas internas")

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

        return self.end_date < timezone.now()

    @property
    def is_ongoing(self):
        """Verifica si el evento está en curso"""
        from django.utils import timezone

        now = timezone.now()
        return self.start_date <= now <= self.end_date

    @property
    def is_upcoming(self):
        """Verifica si el evento es futuro"""
        from django.utils import timezone

        return self.start_date > timezone.now()

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
            raise ValidationError("La fecha de fin debe ser posterior a la fecha de inicio.")

        # Validar consistencia de ubicaciones
        if self.city and self.state and self.city.state != self.state:
            raise ValidationError("La ciudad debe pertenecer al estado seleccionado.")

        if self.state and self.country and self.state.country != self.country:
            raise ValidationError("El estado debe pertenecer al país seleccionado.")

        if self.city and self.country and self.city.state.country != self.country:
            raise ValidationError("La ciudad debe pertenecer al país seleccionado.")


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
    is_internal = models.BooleanField(default=False, help_text="Comentario interno solo visible para organizadores")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Comentario de Evento"
        verbose_name_plural = "Comentarios de Eventos"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comentario de {self.user.get_full_name()} en {self.event.title}"


class EventReminder(models.Model):
    """Recordatorios de eventos"""

    REMINDER_TYPES = [
        ("email", "Email"),
        ("notification", "Notificación"),
        ("sms", "SMS"),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="reminders")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPES, default="notification")
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
