from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models


class Country(models.Model):
    """Países donde se juega baseball"""

    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre del País")
    code = models.CharField(
        max_length=3, unique=True, validators=[MinLengthValidator(2), MaxLengthValidator(3)], verbose_name="Código del País"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

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

    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="states", verbose_name="País")
    name = models.CharField(max_length=100, verbose_name="Nombre del Estado")
    code = models.CharField(
        max_length=10, validators=[MinLengthValidator(2), MaxLengthValidator(10)], verbose_name="Código del Estado"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

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

    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="cities", verbose_name="Estado")
    name = models.CharField(max_length=100, verbose_name="Nombre de la Ciudad")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

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
        max_length=20, choices=SEASON_TYPE_CHOICES, default="regular", verbose_name="Tipo de Temporada"
    )
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    end_date = models.DateField(verbose_name="Fecha de Fin")
    status = models.CharField(max_length=20, choices=SEASON_STATUS_CHOICES, default="upcoming", verbose_name="Estado")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activa")

    # Información adicional
    total_games = models.PositiveIntegerField(null=True, blank=True, verbose_name="Total de Juegos")
    teams_count = models.PositiveIntegerField(null=True, blank=True, verbose_name="Número de Equipos")
    league = models.CharField(max_length=100, blank=True, verbose_name="Liga")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

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
            raise ValidationError("La fecha de fin debe ser posterior a la fecha de inicio.")


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
    rule_type = models.CharField(max_length=20, choices=RULE_TYPE_CHOICES, default="standard", verbose_name="Rule Type")
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
    site_name = models.CharField(max_length=200, verbose_name="Site Name", help_text="Nombre del sitio o instalación")
    abbreviation = models.CharField(max_length=50, blank=True, verbose_name="Abbreviation", help_text="Abreviatura del sitio")

    # Dirección
    address_1 = models.CharField(max_length=200, verbose_name="Address 1", help_text="Dirección principal")
    address_2 = models.CharField(
        max_length=200, blank=True, verbose_name="Address 2", help_text="Dirección secundaria (opcional)"
    )
    city = models.ForeignKey(
        "City", on_delete=models.SET_NULL, null=True, blank=True, related_name="sites", verbose_name="City", help_text="Ciudad"
    )
    state = models.ForeignKey(
        "State", on_delete=models.SET_NULL, null=True, blank=True, related_name="sites", verbose_name="State"
    )
    postal_code = models.CharField(max_length=20, verbose_name="Postal Code", help_text="Código postal")
    country = models.ForeignKey(
        "Country", on_delete=models.SET_NULL, null=True, blank=True, related_name="sites", verbose_name="Country"
    )

    # Información adicional
    website = models.URLField(blank=True, verbose_name="Website", help_text="Sitio web del lugar")
    additional_info = models.TextField(
        blank=True, verbose_name="Additional Info", help_text="Información adicional sobre el sitio (ej. Reglas del parque)"
    )

    # Imágenes
    image = models.ImageField(
        upload_to="sites/", blank=True, null=True, verbose_name="Site Image", help_text="Imagen principal del sitio"
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
        address_parts.extend([self.city.name if self.city else "", self.state.name if self.state else "", self.postal_code])
        return ", ".join(filter(None, address_parts))

    @property
    def events_count(self):
        """Cuenta el número de eventos en este sitio"""
        return self.events.count() if hasattr(self, "events") else 0
