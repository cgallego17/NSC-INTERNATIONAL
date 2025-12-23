from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from datetime import date


class UserProfile(models.Model):
    """Perfil extendido de usuario"""

    USER_TYPE_CHOICES = [
        ("player", "Jugador"),
        ("parent", "Padre/Acudiente"),
        ("team_manager", "Manager de Equipo"),
        ("admin", "Administrador"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default="player",
        verbose_name="Tipo de Usuario",
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    phone_secondary = models.CharField(
        max_length=20, blank=True, verbose_name="Teléfono Secundario"
    )
    address = models.TextField(blank=True, verbose_name="Dirección")
    address_line_2 = models.CharField(
        max_length=200, blank=True, verbose_name="Dirección Línea 2"
    )

    # Relaciones con ubicaciones
    country = models.ForeignKey(
        "locations.Country",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_profiles",
        verbose_name="País",
    )
    state = models.ForeignKey(
        "locations.State",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_profiles",
        verbose_name="Estado",
    )
    city = models.ForeignKey(
        "locations.City",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_profiles",
        verbose_name="Ciudad",
    )

    postal_code = models.CharField(
        max_length=10, blank=True, verbose_name="Código Postal"
    )
    birth_date = models.DateField(
        null=True, blank=True, verbose_name="Fecha de Nacimiento"
    )
    profile_picture = models.ImageField(
        upload_to="accounts/profile_pictures/",
        blank=True,
        null=True,
        verbose_name="Foto de Perfil",
    )
    bio = models.TextField(blank=True, verbose_name="Biografía")
    website = models.URLField(blank=True, verbose_name="Sitio Web")
    social_media = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Redes Sociales",
        help_text="Instagram, Twitter, etc.",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_user_type_display()})"

    @property
    def is_player(self):
        return self.user_type == "player"

    @property
    def is_team_manager(self):
        return self.user_type == "team_manager"

    @property
    def is_parent(self):
        return self.user_type == "parent"

    def get_absolute_url(self):
        return reverse("accounts:profile")


class Team(models.Model):
    """Modelo de Equipo"""

    name = models.CharField(max_length=200, verbose_name="Nombre del Equipo")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug")
    manager = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="managed_teams",
        verbose_name="Manager",
        limit_choices_to={"profile__user_type": "team_manager"},
    )
    description = models.TextField(blank=True, verbose_name="Descripción")
    logo = models.ImageField(
        upload_to="accounts/team_logos/",
        blank=True,
        null=True,
        verbose_name="Logo del Equipo",
    )

    # Relaciones con ubicaciones
    country = models.ForeignKey(
        "locations.Country",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teams",
        verbose_name="País",
    )
    state = models.ForeignKey(
        "locations.State",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teams",
        verbose_name="Estado",
    )
    city = models.ForeignKey(
        "locations.City",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teams",
        verbose_name="Ciudad",
    )

    website = models.URLField(blank=True, verbose_name="Sitio Web")
    contact_email = models.EmailField(blank=True, verbose_name="Email de Contacto")
    contact_phone = models.CharField(
        max_length=20, blank=True, verbose_name="Teléfono de Contacto"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("accounts:team_detail", kwargs={"pk": self.pk})

    @property
    def players_count(self):
        return self.players.filter(is_active=True).count()

    @property
    def active_players(self):
        return self.players.filter(is_active=True)


class Player(models.Model):
    """Modelo de Jugador"""

    POSITION_CHOICES = [
        ("pitcher", "Pitcher"),
        ("catcher", "Catcher"),
        ("first_base", "First Base"),
        ("second_base", "Second Base"),
        ("third_base", "Third Base"),
        ("shortstop", "Shortstop"),
        ("left_field", "Left Field"),
        ("center_field", "Center Field"),
        ("right_field", "Right Field"),
        ("designated_hitter", "Designated Hitter"),
        ("utility", "Utility"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="player_profile",
        verbose_name="Usuario",
        limit_choices_to={"profile__user_type": "player"},
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="players",
        verbose_name="Equipo",
    )
    jersey_number = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Número de Jersey"
    )
    position = models.CharField(
        max_length=20, choices=POSITION_CHOICES, blank=True, verbose_name="Posición"
    )
    height = models.CharField(
        max_length=10, blank=True, verbose_name="Estatura (ej: 5'10\")"
    )
    weight = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Peso (lbs)"
    )
    batting_hand = models.CharField(
        max_length=1,
        choices=[("L", "Left"), ("R", "Right"), ("S", "Switch")],
        blank=True,
        verbose_name="Bateo",
    )
    throwing_hand = models.CharField(
        max_length=1,
        choices=[("L", "Left"), ("R", "Right")],
        blank=True,
        verbose_name="Lanzamiento",
    )
    emergency_contact_name = models.CharField(
        max_length=200, blank=True, verbose_name="Nombre de Contacto de Emergencia"
    )
    emergency_contact_phone = models.CharField(
        max_length=20, blank=True, verbose_name="Teléfono de Emergencia"
    )
    emergency_contact_relation = models.CharField(
        max_length=50, blank=True, verbose_name="Relación"
    )
    medical_conditions = models.TextField(
        blank=True,
        verbose_name="Condiciones Médicas",
        help_text="Información médica relevante",
    )

    # Tallas de Uniformes
    JERSEY_SIZE_CHOICES = [
        ("YXS", "YXS (Youth Extra Small)"),
        ("YS", "YS (Youth Small)"),
        ("YM", "YM (Youth Medium)"),
        ("YL", "YL (Youth Large)"),
        ("AS", "AS (Adult Small)"),
        ("AM", "AM (Adult Medium)"),
        ("AL", "AL (Adult Large)"),
        ("AXL", "AXL (Adult Extra Large)"),
        ("A2XL", "A2XL (Adult 2 Extra Large)"),
    ]

    HAT_SIZE_CHOICES = [
        ("XS_S", "X-Small / Small"),
        ("SM", "Small-Medium"),
        ("L_XL", "Large / X-Large"),
    ]

    BATTING_GLOVE_SIZE_CHOICES = [
        ("YS", "YS (Youth Small)"),
        ("YM", "YM (Youth Medium)"),
        ("YL", "YL (Youth Large)"),
        ("AS", "AS (Adult Small)"),
        ("AM", "AM (Adult Medium)"),
        ("AL", "AL (Adult Large)"),
    ]

    BATTING_HELMET_SIZE_CHOICES = [
        ("XS", "X-Small"),
        ("SM", "Small / Medium"),
        ("ML", "Medium / Large"),
        ("L_XL", "Large / X-Large"),
    ]

    SHORTS_SIZE_CHOICES = [
        ("YS", "YS (Youth Small)"),
        ("YM", "YM (Youth Medium)"),
        ("YL", "YL (Youth Large)"),
        ("AS", "AS (Adult Small)"),
        ("AM", "AM (Adult Medium)"),
        ("AL", "AL (Adult Large)"),
        ("AXL", "AXL (Adult Extra Large)"),
        ("A2XL", "A2XL (Adult 2 Extra Large)"),
    ]

    jersey_size = models.CharField(
        max_length=10,
        choices=JERSEY_SIZE_CHOICES,
        blank=True,
        verbose_name="Talla de Jersey",
    )
    hat_size = models.CharField(
        max_length=10,
        choices=HAT_SIZE_CHOICES,
        blank=True,
        verbose_name="Talla de Gorra",
    )
    batting_glove_size = models.CharField(
        max_length=10,
        choices=BATTING_GLOVE_SIZE_CHOICES,
        blank=True,
        verbose_name="Talla de Guante de Bateo",
    )
    batting_helmet_size = models.CharField(
        max_length=10,
        choices=BATTING_HELMET_SIZE_CHOICES,
        blank=True,
        verbose_name="Talla de Casco de Bateo",
    )
    shorts_size = models.CharField(
        max_length=10,
        choices=SHORTS_SIZE_CHOICES,
        blank=True,
        verbose_name="Talla de Pantalones",
    )

    # Elegibilidad y División
    GRADE_CHOICES = [
        ("pre_k", "Pre-K"),
        ("kindergarten", "Kindergarten"),
        ("1st", "1st Grade"),
        ("2nd", "2nd Grade"),
        ("3rd", "3rd Grade"),
        ("4th", "4th Grade"),
        ("5th", "5th Grade"),
        ("6th", "6th Grade"),
        ("7th", "7th Grade"),
        ("8th", "8th Grade"),
        ("9th", "9th Grade"),
        ("10th", "10th Grade"),
        ("11th", "11th Grade"),
        ("12th", "12th Grade"),
    ]

    DIVISION_CHOICES = [
        ("05U", "05U"),
        ("06U", "06U"),
        ("07U", "07U"),
        ("08U", "08U"),
        ("09U", "09U"),
        ("10U", "10U"),
        ("11U", "11U"),
        ("12U", "12U"),
        ("13U", "13U"),
        ("14U", "14U"),
        ("15U", "15U"),
        ("16U", "16U"),
        ("17U", "17U"),
        ("18U", "18U"),
    ]

    AGE_VERIFICATION_STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("approved", "Aprobado"),
        ("rejected", "Rechazado"),
    ]

    grade = models.CharField(
        max_length=20,
        choices=GRADE_CHOICES,
        blank=True,
        verbose_name="Grado Actual",
        help_text="Grado escolar actual del jugador",
    )
    division = models.CharField(
        max_length=10,
        choices=DIVISION_CHOICES,
        blank=True,
        verbose_name="División Asignada",
        help_text="División en la que el jugador está asignado",
    )
    age_verification_document = models.FileField(
        upload_to="accounts/age_verification/",
        blank=True,
        null=True,
        verbose_name="Documento de Verificación de Edad",
        help_text="Certificado de nacimiento, pasaporte o ID (original o digital)",
    )
    age_verification_status = models.CharField(
        max_length=20,
        choices=AGE_VERIFICATION_STATUS_CHOICES,
        default="pending",
        verbose_name="Estado de Verificación de Edad",
    )
    age_verification_approved_date = models.DateField(
        null=True, blank=True, verbose_name="Fecha de Aprobación de Verificación"
    )
    age_verification_notes = models.TextField(
        blank=True,
        verbose_name="Notas de Verificación",
        help_text="Notas adicionales sobre la verificación de edad",
    )

    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Jugador"
        verbose_name_plural = "Jugadores"
        ordering = ["user__last_name", "user__first_name"]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.team.name if self.team else 'Sin Equipo'}"

    def get_absolute_url(self):
        if self.pk:
            return reverse("accounts:player_detail", kwargs={"pk": self.pk})
        return "#"

    def get_birth_date(self):
        """Obtiene la fecha de nacimiento del jugador desde el perfil de usuario"""
        if hasattr(self.user, "profile") and self.user.profile.birth_date:
            return self.user.profile.birth_date
        return None

    def calculate_age_as_of_april_30(self, year=None):
        """
        Calcula la edad del jugador al 30 de abril del año especificado.
        Si no se especifica año, usa el año actual.
        """
        birth_date = self.get_birth_date()
        if not birth_date:
            return None

        if year is None:
            year = date.today().year

        # Fecha de corte: 30 de abril
        cutoff_date = date(year, 4, 30)

        # Calcular edad
        age = cutoff_date.year - birth_date.year
        if (cutoff_date.month, cutoff_date.day) < (birth_date.month, birth_date.day):
            age -= 1

        return age

    def get_age_based_division(self, year=None):
        """
        Calcula la división elegible basada en la edad al 30 de abril.
        Regla: La edad del jugador más viejo al 30 de abril determina elegibilidad.
        Un jugador de 10U no puede cumplir 11 años antes del 1 de mayo.
        """
        age = self.calculate_age_as_of_april_30(year)
        if age is None:
            return None

        # Mapeo de edad a división
        # Un jugador de XU no puede cumplir X+1 años antes del 1 de mayo
        # Es decir, si tiene X años al 30 de abril, puede jugar en XU
        division_map = {
            5: "05U",
            6: "06U",
            7: "07U",
            8: "08U",
            9: "09U",
            10: "10U",
            11: "11U",
            12: "12U",
            13: "13U",
            14: "14U",
            15: "15U",
            16: "16U",
            17: "17U",
            18: "18U",
        }

        # Si tiene menos de 5 años, no es elegible
        if age < 5:
            return None

        # Si tiene 18 o más años, puede jugar en 18U
        if age >= 18:
            return "18U"

        return division_map.get(age)

    def get_grade_based_division(self):
        """
        Calcula la división elegible basada en el grado escolar.
        Grade Exceptions permiten jugar en una división basada en grado.
        """
        if not self.grade:
            return None

        # Mapeo de grado a división según la tabla de Grade Exceptions
        grade_division_map = {
            "pre_k": "05U",
            "kindergarten": "06U",
            "1st": "07U",
            "2nd": "08U",
            "3rd": "09U",
            "4th": "10U",
            "5th": "11U",
            "6th": "12U",
            "7th": "13U",
            "8th": "14U",
            "9th": "15U",
            "10th": "16U",
            "11th": "17U",
            "12th": "18U",
        }

        return grade_division_map.get(self.grade)

    def get_eligible_divisions(self):
        """
        Retorna las divisiones elegibles para el jugador.
        Incluye la división basada en edad y la división basada en grado.
        """
        divisions = []

        # División basada en edad
        age_division = self.get_age_based_division()
        if age_division:
            divisions.append(age_division)

        # División basada en grado (Grade Exception)
        grade_division = self.get_grade_based_division()
        if grade_division and grade_division not in divisions:
            divisions.append(grade_division)

        return sorted(set(divisions))

    def can_play_in_division(self, target_division):
        """
        Verifica si el jugador puede jugar en la división especificada.
        Reglas:
        - No puede jugar "down" (solo puede jugar "up" máximo 2 divisiones)
        - Debe tener verificación de edad aprobada
        """
        # Verificar que tenga verificación de edad aprobada
        if self.age_verification_status != "approved":
            return False, "El jugador no tiene verificación de edad aprobada"

        eligible_divisions = self.get_eligible_divisions()
        if not eligible_divisions:
            return False, "No se puede determinar la elegibilidad del jugador"

        # Obtener el número de la división objetivo
        target_num = int(target_division.replace("U", ""))

        # Obtener el número de la división más baja elegible (basada en edad)
        age_division = self.get_age_based_division()
        if not age_division:
            return False, "No se puede determinar la división basada en edad"

        age_division_num = int(age_division.replace("U", ""))

        # No puede jugar "down" (en una división menor)
        if target_num < age_division_num:
            return (
                False,
                f"El jugador no puede jugar en una división menor ({target_division}). División mínima elegible: {age_division}",
            )

        # Puede jugar "up" máximo 2 divisiones
        if target_num > age_division_num + 2:
            return (
                False,
                f"El jugador solo puede jugar hasta 2 divisiones arriba de su división basada en edad ({age_division}). División solicitada: {target_division}",
            )

        # Si la división está en las elegibles o está dentro del rango permitido
        if target_division in eligible_divisions:
            return True, "Elegible"

        # Verificar si está dentro del rango permitido (hasta 2 divisiones arriba)
        if age_division_num <= target_num <= age_division_num + 2:
            return True, "Elegible (jugando arriba)"

        return False, "División no elegible"

    def is_eligible_to_play(self):
        """
        Verifica si el jugador es elegible para jugar.
        Requisitos:
        1. Verificación de edad aprobada
        2. División asignada válida
        """
        if self.age_verification_status != "approved":
            return False, "Verificación de edad pendiente o rechazada"

        if not self.division:
            return False, "No tiene división asignada"

        can_play, message = self.can_play_in_division(self.division)
        return can_play, message


class PlayerParent(models.Model):
    """Modelo para relacionar padres/acudientes con jugadores"""

    RELATIONSHIP_CHOICES = [
        ("father", "Padre"),
        ("mother", "Madre"),
        ("guardian", "Acudiente"),
        ("other", "Otro"),
    ]

    parent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="children",
        verbose_name="Padre/Acudiente",
        limit_choices_to={"profile__user_type": "parent"},
    )
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="parents", verbose_name="Jugador"
    )
    relationship = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_CHOICES,
        default="guardian",
        verbose_name="Relación",
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name="Contacto Principal",
        help_text="Marcar si es el contacto principal del jugador",
    )
    can_pickup = models.BooleanField(
        default=True,
        verbose_name="Puede Recoger",
        help_text="Marcar si esta persona puede recoger al jugador",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Padre/Acudiente de Jugador"
        verbose_name_plural = "Padres/Acudientes de Jugadores"
        ordering = ["-is_primary", "parent__last_name", "parent__first_name"]
        unique_together = [["parent", "player"]]

    def __str__(self):
        return f"{self.parent.get_full_name()} - {self.player.user.get_full_name()}"


class DashboardContent(models.Model):
    """Modelo para contenido del dashboard configurable por el admin"""

    USER_TYPE_CHOICES = [
        ("player", "Jugador"),
        ("parent", "Padre/Acudiente"),
        ("team_manager", "Manager de Equipo"),
        ("all", "Todos los Usuarios"),
    ]

    title = models.CharField(
        max_length=200, verbose_name="Título", default="Bienvenido"
    )
    content = models.TextField(
        verbose_name="Contenido", help_text="Contenido HTML permitido"
    )
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default="all",
        verbose_name="Tipo de Usuario",
        help_text="Seleccione para qué tipo de usuario es este contenido"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Contenido del Dashboard"
        verbose_name_plural = "Contenidos del Dashboard"
        ordering = ["order", "-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_user_type_display()})"


class HomeBanner(models.Model):
    """Modelo para banners del carousel del home"""

    BANNER_TYPE_CHOICES = [
        ("image", "Imagen"),
        ("gradient", "Gradiente con Texto"),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name="Título",
        blank=True,
        help_text="Título del banner (opcional)",
    )
    description = models.TextField(
        verbose_name="Descripción",
        blank=True,
        help_text="Descripción del banner (opcional)",
    )
    banner_type = models.CharField(
        max_length=20,
        choices=BANNER_TYPE_CHOICES,
        default="image",
        verbose_name="Tipo de Banner",
    )
    image = models.ImageField(
        upload_to="banners/",
        blank=True,
        null=True,
        verbose_name="Imagen",
        help_text='Imagen del banner (requerido si tipo es "Imagen")',
    )
    gradient_color_1 = models.CharField(
        max_length=7,
        default="#0d2c54",
        verbose_name="Color Gradiente 1",
        help_text="Color hexadecimal (ej: #0d2c54)",
    )
    gradient_color_2 = models.CharField(
        max_length=7,
        default="#132448",
        verbose_name="Color Gradiente 2",
        help_text="Color hexadecimal (ej: #132448)",
    )
    gradient_color_3 = models.CharField(
        max_length=7,
        blank=True,
        verbose_name="Color Gradiente 3",
        help_text="Color hexadecimal opcional (ej: #64b5f6)",
    )
    button_text = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Texto del Botón",
        help_text="Texto del botón principal (opcional)",
    )
    button_url = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="URL del Botón",
        help_text="URL a donde lleva el botón (opcional)",
    )
    button_text_2 = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Texto del Botón Secundario",
        help_text="Texto del segundo botón (opcional)",
    )
    button_url_2 = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="URL del Botón Secundario",
        help_text="URL del segundo botón (opcional)",
    )
    icon_class = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Clase del Icono",
        help_text="Clase Font Awesome (ej: fa-trophy, fa-baseball-ball)",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    order = models.PositiveIntegerField(
        default=0, verbose_name="Orden", help_text="Orden de aparición en el carousel"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Banner del Home"
        verbose_name_plural = "Banners del Home"
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title or f"Banner #{self.id}"


class SiteSettings(models.Model):
    """Modelo para configuraciones generales del sitio"""

    schedule_image = models.ImageField(
        upload_to="site_settings/",
        blank=True,
        null=True,
        verbose_name="Imagen del Schedule",
        help_text='Imagen que se muestra en la sección "Season Schedule" del home',
    )
    # Campos en inglés
    schedule_title_en = models.CharField(
        max_length=200,
        default="2026 EVENT CALENDAR",
        verbose_name="Schedule Title (English)",
        help_text="Título principal de la sección Schedule en inglés",
    )
    schedule_subtitle_en = models.CharField(
        max_length=300,
        default="REGIONAL EXPANSION AND NEW NATIONAL AND REGIONAL CHAMPIONSHIPS FOR 2026",
        verbose_name="Schedule Subtitle (English)",
        help_text="Subtítulo de la sección Schedule en inglés",
    )
    schedule_description_en = models.TextField(
        blank=True,
        default="As we move forward into 2026, NSC International continues to elevate its tournament and showcase platform. With a regional presence expansion for ages 7U-18U, new and improved National and Regional Championship events, and an even broader showcase schedule across the country, NSC remains dedicated to providing the highest standard of competition and experience for players, coaches and families alike.",
        verbose_name="Schedule Description (English)",
        help_text="Descripción de la sección Schedule en inglés",
    )
    
    # Campos en español
    schedule_title_es = models.CharField(
        max_length=200,
        default="CALENDARIO DE EVENTOS 2026",
        verbose_name="Schedule Title (Spanish)",
        help_text="Título principal de la sección Schedule en español",
    )
    schedule_subtitle_es = models.CharField(
        max_length=300,
        default="EXPANSIÓN REGIONAL Y NUEVOS CAMPEONATOS NACIONALES Y REGIONALES PARA 2026",
        verbose_name="Schedule Subtitle (Spanish)",
        help_text="Subtítulo de la sección Schedule en español",
    )
    schedule_description_es = models.TextField(
        blank=True,
        default="A medida que avanzamos hacia 2026, NSC International continúa elevando su plataforma de torneos y exhibiciones. Con una expansión de la presencia regional para edades 7U-18U, nuevos y mejorados eventos de Campeonatos Nacionales y Regionales, y una programación aún más amplia de exhibiciones en todo el país, NSC se mantiene dedicado a ofrecer el más alto estándar de competencia y experiencia para jugadores, entrenadores y familias por igual.",
        verbose_name="Schedule Description (Spanish)",
        help_text="Descripción de la sección Schedule en español",
    )
    
    # Campos legacy (mantener por compatibilidad, usar los nuevos métodos)
    schedule_title = models.CharField(
        max_length=200,
        default="2026 EVENT CALENDAR",
        verbose_name="Título del Schedule (Legacy)",
        help_text="[DEPRECATED] Usar schedule_title_en y schedule_title_es",
        editable=False,
    )
    schedule_subtitle = models.CharField(
        max_length=300,
        default="REGIONAL EXPANSION AND NEW NATIONAL AND REGIONAL CHAMPIONSHIPS FOR 2026",
        verbose_name="Subtítulo del Schedule (Legacy)",
        help_text="[DEPRECATED] Usar schedule_subtitle_en y schedule_subtitle_es",
        editable=False,
    )
    schedule_description = models.TextField(
        blank=True,
        verbose_name="Descripción del Schedule (Legacy)",
        help_text="[DEPRECATED] Usar schedule_description_en y schedule_description_es",
        editable=False,
    )
    showcase_image = models.ImageField(
        upload_to="site_settings/",
        blank=True,
        null=True,
        verbose_name="Imagen del Showcase",
        help_text='Imagen que se muestra en la sección "Showcases and Prospect Gateways" del home',
    )
    # Campos en inglés
    showcase_title_en = models.CharField(
        max_length=200,
        default="SHOWCASES AND PROSPECT GATEWAYS",
        verbose_name="Showcase Title (English)",
        help_text="Título principal de la sección Showcase en inglés",
    )
    showcase_subtitle_en = models.CharField(
        max_length=300,
        default="REGIONAL AND NATIONAL SHOWCASES",
        verbose_name="Showcase Subtitle (English)",
        help_text="Subtítulo de la sección Showcase en inglés",
    )
    showcase_description_en = models.TextField(
        blank=True,
        default="Perfect Game is thrilled to offer showcases (HS) and Prospect Gateways (13U/14U) across the country for the 2025 calendar. This includes regional events for all ages and new invite only events! PG strives to delivery the very best events and experience for all players, coaches and families across the country.",
        verbose_name="Showcase Description (English)",
        help_text="Descripción de la sección Showcase en inglés",
    )
    
    # Campos en español
    showcase_title_es = models.CharField(
        max_length=200,
        default="SHOWCASES Y PORTALES DE PROSPECTO",
        verbose_name="Showcase Title (Spanish)",
        help_text="Título principal de la sección Showcase en español",
    )
    showcase_subtitle_es = models.CharField(
        max_length=300,
        default="SHOWCASES REGIONALES Y NACIONALES",
        verbose_name="Showcase Subtitle (Spanish)",
        help_text="Subtítulo de la sección Showcase en español",
    )
    showcase_description_es = models.TextField(
        blank=True,
        default="Perfect Game se complace en ofrecer showcases (HS) y Prospect Gateways (13U/14U) en todo el país para el calendario 2025. Esto incluye eventos regionales para todas las edades y nuevos eventos solo por invitación. PG se esfuerza por ofrecer los mejores eventos y experiencias para todos los jugadores, entrenadores y familias en todo el país.",
        verbose_name="Showcase Description (Spanish)",
        help_text="Descripción de la sección Showcase en español",
    )
    
    # Campos legacy (mantener por compatibilidad)
    showcase_title = models.CharField(
        max_length=200,
        default="SHOWCASES AND PROSPECT GATEWAYS",
        verbose_name="Título del Showcase (Legacy)",
        help_text="[DEPRECATED] Usar showcase_title_en y showcase_title_es",
        editable=False,
    )
    showcase_subtitle = models.CharField(
        max_length=300,
        default="REGIONAL AND NATIONAL SHOWCASES",
        verbose_name="Subtítulo del Showcase (Legacy)",
        help_text="[DEPRECATED] Usar showcase_subtitle_en y showcase_subtitle_es",
        editable=False,
    )
    showcase_description = models.TextField(
        blank=True,
        verbose_name="Descripción del Showcase (Legacy)",
        help_text="[DEPRECATED] Usar showcase_description_en y showcase_description_es",
        editable=False,
    )
    dashboard_welcome_banner = models.ImageField(
        upload_to="site_settings/",
        blank=True,
        null=True,
        verbose_name="Banner de Bienvenida del Panel",
        help_text="Imagen que se muestra en el welcome banner del panel de usuario (/accounts/panel/)",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuración del Sitio"
        verbose_name_plural = "Configuraciones del Sitio"

    def __str__(self):
        return "Configuración del Sitio"

    def save(self, *args, **kwargs):
        # Asegurar que solo haya una instancia
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """Cargar o crear la instancia única de configuración"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    # Métodos para obtener valores según el idioma
    def get_schedule_title(self, lang=None):
        """Retorna el título del schedule según el idioma especificado o el actual"""
        from django.utils.translation import get_language
        target_lang = (lang or get_language() or 'en')[:2]
        if target_lang == 'es':
            return self.schedule_title_es or self.schedule_title_en or "CALENDARIO DE EVENTOS 2026"
        return self.schedule_title_en or "2026 EVENT CALENDAR"
    
    def get_schedule_subtitle(self, lang=None):
        """Retorna el subtítulo del schedule según el idioma especificado o el actual"""
        from django.utils.translation import get_language
        target_lang = (lang or get_language() or 'en')[:2]
        if target_lang == 'es':
            return self.schedule_subtitle_es or self.schedule_subtitle_en or "EXPANSIÓN REGIONAL Y NUEVOS CAMPEONATOS NACIONALES Y REGIONALES PARA 2026"
        return self.schedule_subtitle_en or "REGIONAL EXPANSION AND NEW NATIONAL AND REGIONAL CHAMPIONSHIPS FOR 2026"
    
    def get_schedule_description(self, lang=None):
        """Retorna la descripción del schedule según el idioma especificado o el actual"""
        from django.utils.translation import get_language
        target_lang = (lang or get_language() or 'en')[:2]
        if target_lang == 'es':
            return self.schedule_description_es or self.schedule_description_en or ""
        return self.schedule_description_en or ""
    
    def get_showcase_title(self, lang=None):
        """Retorna el título del showcase según el idioma especificado o el actual"""
        from django.utils.translation import get_language
        target_lang = (lang or get_language() or 'en')[:2]
        if target_lang == 'es':
            return self.showcase_title_es or self.showcase_title_en or "SHOWCASES Y PORTALES DE PROSPECTO"
        return self.showcase_title_en or "SHOWCASES AND PROSPECT GATEWAYS"
    
    def get_showcase_subtitle(self, lang=None):
        """Retorna el subtítulo del showcase según el idioma especificado o el actual"""
        from django.utils.translation import get_language
        target_lang = (lang or get_language() or 'en')[:2]
        if target_lang == 'es':
            return self.showcase_subtitle_es or self.showcase_subtitle_en or "SHOWCASES REGIONALES Y NACIONALES"
        return self.showcase_subtitle_en or "REGIONAL AND NATIONAL SHOWCASES"
    
    def get_showcase_description(self, lang=None):
        """Retorna la descripción del showcase según el idioma especificado o el actual"""
        from django.utils.translation import get_language
        target_lang = (lang or get_language() or 'en')[:2]
        if target_lang == 'es':
            return self.showcase_description_es or self.showcase_description_en or ""
        return self.showcase_description_en or ""
    
    # Métodos legacy (mantener por compatibilidad)
    def get_schedule_title_translated(self):
        """[DEPRECATED] Usar get_schedule_title()"""
        return self.get_schedule_title()
    
    def get_schedule_subtitle_translated(self):
        """[DEPRECATED] Usar get_schedule_subtitle()"""
        return self.get_schedule_subtitle()
    
    def get_schedule_description_translated(self):
        """[DEPRECATED] Usar get_schedule_description()"""
        return self.get_schedule_description()
    
    def get_showcase_title_translated(self):
        """[DEPRECATED] Usar get_showcase_title()"""
        return self.get_showcase_title()
    
    def get_showcase_subtitle_translated(self):
        """[DEPRECATED] Usar get_showcase_subtitle()"""
        return self.get_showcase_subtitle()
    
    def get_showcase_description_translated(self):
        """[DEPRECATED] Usar get_showcase_description()"""
        return self.get_showcase_description()
    
    def get_translations_dict(self):
        """Retorna un diccionario con todas las traducciones para uso en JavaScript"""
        return {
            'en': {
                'schedule_title': self.get_schedule_title('en'),
                'schedule_subtitle': self.get_schedule_subtitle('en'),
                'schedule_description': self.get_schedule_description('en'),
                'showcase_title': self.get_showcase_title('en'),
                'showcase_subtitle': self.get_showcase_subtitle('en'),
                'showcase_description': self.get_showcase_description('en'),
            },
            'es': {
                'schedule_title': self.get_schedule_title('es'),
                'schedule_subtitle': self.get_schedule_subtitle('es'),
                'schedule_description': self.get_schedule_description('es'),
                'showcase_title': self.get_showcase_title('es'),
                'showcase_subtitle': self.get_showcase_subtitle('es'),
                'showcase_description': self.get_showcase_description('es'),
            }
        }


class DashboardBanner(models.Model):
    """Modelo para banners del welcome banner del panel de usuario"""

    BANNER_TYPE_CHOICES = [
        ("image", "Imagen"),
        ("gradient", "Gradiente con Texto"),
    ]

    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Título",
        help_text="Título del banner (opcional)",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
        help_text="Descripción del banner (opcional)",
    )
    banner_type = models.CharField(
        max_length=20,
        choices=BANNER_TYPE_CHOICES,
        default="image",
        verbose_name="Tipo de Banner",
    )
    image = models.ImageField(
        upload_to="dashboard_banners/",
        blank=True,
        null=True,
        verbose_name="Imagen",
        help_text='Imagen del banner (requerido si tipo es "Imagen")',
    )
    gradient_color_1 = models.CharField(
        max_length=7,
        default="#0d2c54",
        verbose_name="Color Gradiente 1",
        help_text="Color hexadecimal (ej: #0d2c54)",
    )
    gradient_color_2 = models.CharField(
        max_length=7,
        default="#132448",
        verbose_name="Color Gradiente 2",
        help_text="Color hexadecimal (ej: #132448)",
    )
    gradient_color_3 = models.CharField(
        max_length=7,
        blank=True,
        verbose_name="Color Gradiente 3",
        help_text="Color hexadecimal opcional (ej: #64b5f6)",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Orden",
        help_text="Orden de aparición (menor número aparece primero)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Banner del Panel"
        verbose_name_plural = "Banners del Panel"
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title or f"Banner Panel #{self.id}"


class Sponsor(models.Model):
    """Modelo para sponsors del home"""

    name = models.CharField(
        max_length=200,
        verbose_name="Nombre del Sponsor",
        help_text="Nombre de la empresa o marca",
    )
    logo = models.ImageField(
        upload_to="sponsors/",
        verbose_name="Logo",
        help_text="Logo del sponsor (recomendado: formato PNG con fondo transparente)",
    )
    website_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="URL del Sitio Web",
        help_text="URL del sitio web del sponsor (opcional)",
    )
    is_active = models.BooleanField(
        default=True, verbose_name="Activo", help_text="Mostrar este sponsor en el home"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Orden",
        help_text="Orden de aparición (menor número aparece primero)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sponsor"
        verbose_name_plural = "Sponsors"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name
