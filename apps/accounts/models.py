from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class UserProfile(models.Model):
    """Perfil extendido de usuario"""
    
    USER_TYPE_CHOICES = [
        ('player', 'Jugador'),
        ('team_manager', 'Manager de Equipo'),
        ('admin', 'Administrador'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='player',
        verbose_name='Tipo de Usuario'
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    phone_secondary = models.CharField(max_length=20, blank=True, verbose_name='Teléfono Secundario')
    address = models.TextField(blank=True, verbose_name='Dirección')
    address_line_2 = models.CharField(max_length=200, blank=True, verbose_name='Dirección Línea 2')
    
    # Relaciones con ubicaciones
    country = models.ForeignKey(
        'locations.Country',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_profiles',
        verbose_name='País'
    )
    state = models.ForeignKey(
        'locations.State',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_profiles',
        verbose_name='Estado'
    )
    city = models.ForeignKey(
        'locations.City',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_profiles',
        verbose_name='Ciudad'
    )
    
    postal_code = models.CharField(max_length=10, blank=True, verbose_name='Código Postal')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Fecha de Nacimiento')
    profile_picture = models.ImageField(
        upload_to='accounts/profile_pictures/',
        blank=True,
        null=True,
        verbose_name='Foto de Perfil'
    )
    bio = models.TextField(blank=True, verbose_name='Biografía')
    website = models.URLField(blank=True, verbose_name='Sitio Web')
    social_media = models.CharField(max_length=200, blank=True, verbose_name='Redes Sociales', help_text='Instagram, Twitter, etc.')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_user_type_display()})"
    
    @property
    def is_player(self):
        return self.user_type == 'player'
    
    @property
    def is_team_manager(self):
        return self.user_type == 'team_manager'
    
    def get_absolute_url(self):
        return reverse('accounts:profile')


class Team(models.Model):
    """Modelo de Equipo"""
    
    name = models.CharField(max_length=200, verbose_name='Nombre del Equipo')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Slug')
    manager = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='managed_teams',
        verbose_name='Manager',
        limit_choices_to={'profile__user_type': 'team_manager'}
    )
    description = models.TextField(blank=True, verbose_name='Descripción')
    logo = models.ImageField(
        upload_to='accounts/team_logos/',
        blank=True,
        null=True,
        verbose_name='Logo del Equipo'
    )
    
    # Relaciones con ubicaciones
    country = models.ForeignKey(
        'locations.Country',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teams',
        verbose_name='País'
    )
    state = models.ForeignKey(
        'locations.State',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teams',
        verbose_name='Estado'
    )
    city = models.ForeignKey(
        'locations.City',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teams',
        verbose_name='Ciudad'
    )
    
    website = models.URLField(blank=True, verbose_name='Sitio Web')
    contact_email = models.EmailField(blank=True, verbose_name='Email de Contacto')
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono de Contacto')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('accounts:team_detail', kwargs={'pk': self.pk})
    
    @property
    def players_count(self):
        return self.players.filter(is_active=True).count()
    
    @property
    def active_players(self):
        return self.players.filter(is_active=True)


class Player(models.Model):
    """Modelo de Jugador"""
    
    POSITION_CHOICES = [
        ('pitcher', 'Pitcher'),
        ('catcher', 'Catcher'),
        ('first_base', 'First Base'),
        ('second_base', 'Second Base'),
        ('third_base', 'Third Base'),
        ('shortstop', 'Shortstop'),
        ('left_field', 'Left Field'),
        ('center_field', 'Center Field'),
        ('right_field', 'Right Field'),
        ('designated_hitter', 'Designated Hitter'),
        ('utility', 'Utility'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='player_profile',
        verbose_name='Usuario',
        limit_choices_to={'profile__user_type': 'player'}
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='players',
        verbose_name='Equipo'
    )
    jersey_number = models.PositiveIntegerField(null=True, blank=True, verbose_name='Número de Jersey')
    position = models.CharField(
        max_length=20,
        choices=POSITION_CHOICES,
        blank=True,
        verbose_name='Posición'
    )
    height = models.CharField(max_length=10, blank=True, verbose_name='Estatura (ej: 5\'10")')
    weight = models.PositiveIntegerField(null=True, blank=True, verbose_name='Peso (lbs)')
    batting_hand = models.CharField(
        max_length=1,
        choices=[('L', 'Left'), ('R', 'Right'), ('S', 'Switch')],
        blank=True,
        verbose_name='Bateo'
    )
    throwing_hand = models.CharField(
        max_length=1,
        choices=[('L', 'Left'), ('R', 'Right')],
        blank=True,
        verbose_name='Lanzamiento'
    )
    emergency_contact_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Nombre de Contacto de Emergencia'
    )
    emergency_contact_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Teléfono de Emergencia'
    )
    emergency_contact_relation = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Relación'
    )
    medical_conditions = models.TextField(
        blank=True,
        verbose_name='Condiciones Médicas',
        help_text='Información médica relevante'
    )
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Jugador'
        verbose_name_plural = 'Jugadores'
        ordering = ['user__last_name', 'user__first_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.team.name if self.team else 'Sin Equipo'}"
    
    def get_absolute_url(self):
        return reverse('accounts:player_detail', kwargs={'pk': self.pk})
