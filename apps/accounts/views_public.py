"""
Vistas públicas - No requieren autenticación
"""

import requests

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as BaseLoginView
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from .forms import EmailAuthenticationForm, PublicRegistrationForm
from .models import Player, PlayerParent, Team


class PublicHomeView(TemplateView):
    """Vista pública del home"""

    template_name = "accounts/public_home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener eventos próximos (si existe la app events)
        try:
            from apps.events.models import Event

            now = timezone.now()
            # Mostrar solo eventos futuros publicados
            upcoming_events = (
                Event.objects.filter(status="published", start_date__gte=now.date())
                .select_related("category")
                .prefetch_related("divisions")
                .order_by("start_date")[:6]  # Ordenar por fecha más próxima primero
            )

            # Eventos de hoy (solo publicados)
            today_events = Event.objects.filter(
                status="published", start_date=now.date()
            ).order_by("start_date")[
                :3
            ]  # Ordenar por fecha/hora más próxima primero

            context["upcoming_events"] = upcoming_events
            context["today_events"] = today_events

            # Evento de Mérida (para el bloque promocional del home)
            # Buscar en título, ciudad, estado y campo location
            merida_q = (
                Q(title__icontains="merida")
                | Q(title__icontains="mérida")
                | Q(city__name__icontains="merida")
                | Q(city__name__icontains="mérida")
                | Q(state__name__icontains="yucatan")
                | Q(state__name__icontains="yucatán")
                | Q(location__icontains="merida")
                | Q(location__icontains="mérida")
            )
            # Priorizar eventos futuros, luego los más recientes (solo publicados)
            merida_event = (
                Event.objects.filter(status="published")
                .filter(merida_q)
                .select_related("category", "event_type", "city", "state")
                .prefetch_related("divisions")
            )
            # Primero intentar eventos futuros
            future_merida = (
                merida_event.filter(start_date__gte=now.date())
                .order_by("start_date")
                .first()
            )
            # Si no hay futuros, tomar el más reciente
            if not future_merida:
                future_merida = merida_event.order_by("-start_date").first()

            # Si aún no hay evento de Mérida, usar el primer evento próximo como fallback (solo publicados)
            if not future_merida:
                future_merida = (
                    Event.objects.filter(status="published", start_date__gte=now.date())
                    .select_related("category", "event_type", "city", "state")
                    .prefetch_related("divisions")
                    .order_by("start_date")
                    .first()
                )

            context["merida_event"] = future_merida

            # Obtener eventos con videos promocionales para el carrusel de videos
            # Priorizar eventos futuros con video_url, luego los más recientes (solo publicados)
            promo_events = (
                Event.objects.filter(status="published")
                .exclude(video_url__isnull=True)
                .exclude(video_url="")
                .select_related("category", "event_type", "city", "state", "country")
                .prefetch_related("divisions")
                .order_by("start_date")
            )

            # Si hay eventos futuros, priorizarlos
            future_promo_events = promo_events.filter(start_date__gte=now.date())
            if future_promo_events.exists():
                context["promo_events"] = list(
                    future_promo_events[:10]
                )  # Máximo 10 eventos
            else:
                # Si no hay futuros, tomar los más recientes
                context["promo_events"] = list(
                    promo_events.order_by("-start_date")[:10]
                )
        except ImportError:
            context["upcoming_events"] = []
            context["today_events"] = []
            context["merida_event"] = None
            context["promo_events"] = []

        # Estadísticas públicas
        context["total_teams"] = Team.objects.filter(is_active=True).count()
        context["total_players"] = Player.objects.filter(is_active=True).count()

        # Obtener tipos de eventos activos
        try:
            from apps.events.models import EventType

            context["event_types"] = EventType.objects.filter(is_active=True).order_by(
                "name"
            )
            # Buscar tipos específicos para los botones de showcase y prospect games
            showcase_type = EventType.objects.filter(
                is_active=True, name__icontains="showcase"
            ).first()
            prospect_type = EventType.objects.filter(
                is_active=True, name__icontains="prospect"
            ).first()
            context["showcase_event_type"] = showcase_type
            context["prospect_event_type"] = prospect_type
        except ImportError:
            context["event_types"] = []
            context["showcase_event_type"] = None
            context["prospect_event_type"] = None

        # Instagram username y perfil
        instagram_username = getattr(
            settings, "INSTAGRAM_USERNAME", "ncs_international"
        )
        context["instagram_username"] = instagram_username

        # Valores por defecto para el perfil de Instagram (solo RSS feed, sin API)
        context["instagram_display_name"] = instagram_username.replace("_", " ").title()
        context["instagram_profile_picture"] = None
        context["instagram_is_verified"] = False
        context["instagram_posts_count"] = 0
        context["instagram_followers_count"] = 0
        context["instagram_following_count"] = 0

        # Obtener banners activos del home
        try:
            from .models import HomeBanner

            context["home_banners"] = HomeBanner.objects.filter(
                is_active=True
            ).order_by("order", "-created_at")
        except ImportError:
            context["home_banners"] = []

        # Obtener configuraciones del sitio
        try:
            from django.utils.translation import get_language

            from .models import SiteSettings

            site_settings = SiteSettings.load()
            context["site_settings"] = site_settings
            # Pasar traducciones al JavaScript
            context["site_settings_translations"] = (
                site_settings.get_translations_dict()
            )
            # Obtener el idioma actual del request
            current_lang = get_language() or "en"
            # Pasar valores directamente para facilitar el acceso en templates
            # Usar el idioma actual del request para obtener los valores correctos
            context["schedule_title"] = site_settings.get_schedule_title(current_lang)
            context["schedule_subtitle"] = site_settings.get_schedule_subtitle(
                current_lang
            )
            context["schedule_description"] = site_settings.get_schedule_description(
                current_lang
            )
            context["showcase_title"] = site_settings.get_showcase_title(current_lang)
            context["showcase_subtitle"] = site_settings.get_showcase_subtitle(
                current_lang
            )
            context["showcase_description"] = site_settings.get_showcase_description(
                current_lang
            )
        except ImportError:
            context["site_settings"] = None
            context["site_settings_translations"] = None
            context["schedule_title"] = None
            context["schedule_subtitle"] = None
            context["schedule_description"] = None
            context["showcase_title"] = None
            context["showcase_subtitle"] = None
            context["showcase_description"] = None

        # Obtener sponsors activos
        try:
            from .models import Sponsor

            context["sponsors"] = Sponsor.objects.filter(is_active=True).order_by(
                "order", "name"
            )
        except ImportError:
            context["sponsors"] = []

        # Si hay un error de login en la sesión, pasar el formulario con errores
        login_error = self.request.session.pop("login_error", None)
        login_form_data = self.request.session.pop("login_form_data", None)

        if login_error or self.request.GET.get("login_error") == "1":
            if login_form_data:
                form = EmailAuthenticationForm(data=login_form_data)
                form.is_valid()  # Esto activará los errores
            else:
                form = EmailAuthenticationForm()
            context["form"] = form
            context["show_login_modal"] = True

        return context


class PublicTeamListView(ListView):
    """Vista pública de lista de equipos - No requiere autenticación"""

    model = Team
    template_name = "accounts/public_team_list.html"
    context_object_name = "teams"
    paginate_by = 20

    def get_queryset(self):
        queryset = Team.objects.filter(is_active=True).select_related(
            "city", "state", "country", "manager"
        )
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(city__name__icontains=search)
                | Q(state__name__icontains=search)
            )
        return queryset.order_by("name")


class PublicPlayerListView(ListView):
    """Vista pública de lista de jugadores - No requiere autenticación"""

    model = Player
    template_name = "accounts/public_player_list.html"
    context_object_name = "players"
    paginate_by = 12

    def get_queryset(self):
        queryset = (
            Player.objects.filter(is_active=True)
            .select_related(
                "user",
                "user__profile",
                "team",
                "user__profile__country",
                "user__profile__state",
                "user__profile__city",
            )
            .only(
                "id",
                "jersey_number",
                "position",
                "division",
                "height",
                "user__first_name",
                "user__last_name",
                "user__email",
                "user__profile__profile_picture",
                "user__profile__birth_date",
                "user__profile__country__name",
                "user__profile__state__name",
                "user__profile__city__name",
                "team__name",
            )
            .order_by("user__last_name", "user__first_name")
        )

        # Búsqueda por nombre
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(user__email__icontains=search)
                | Q(team__name__icontains=search)
            )

        # Filtro por país
        country_filter = self.request.GET.get("country")
        if country_filter:
            queryset = queryset.filter(user__profile__country_id=country_filter)

        # Filtro por estado
        state_filter = self.request.GET.get("state")
        if state_filter:
            queryset = queryset.filter(user__profile__state_id=state_filter)

        # Filtro por ciudad
        city_filter = self.request.GET.get("city")
        if city_filter:
            queryset = queryset.filter(user__profile__city_id=city_filter)

        # Filtro por división
        division_filter = self.request.GET.get("division")
        if division_filter:
            queryset = queryset.filter(division_id=division_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Importar modelos de locations
        from django.db.models import Count

        from apps.locations.models import City, Country, State

        # Optimizar: Solo cargar países/estados/ciudades que tienen jugadores activos
        # Esto reduce significativamente la carga si hay muchos países/estados/ciudades
        active_players = Player.objects.filter(is_active=True).select_related(
            "user__profile__country", "user__profile__state", "user__profile__city"
        )

        # Países que tienen jugadores activos
        country_ids = (
            active_players.exclude(user__profile__country__isnull=True)
            .values_list("user__profile__country_id", flat=True)
            .distinct()
        )
        context["countries"] = Country.objects.filter(
            id__in=country_ids, is_active=True
        ).order_by("name")[
            :100
        ]  # Limitar a 100 para evitar cargar demasiados

        # Estados que tienen jugadores activos (solo si hay filtro de país)
        country_filter = self.request.GET.get("country")
        if country_filter:
            state_ids = (
                active_players.filter(user__profile__country_id=country_filter)
                .exclude(user__profile__state__isnull=True)
                .values_list("user__profile__state_id", flat=True)
                .distinct()
            )
            context["states"] = State.objects.filter(
                id__in=state_ids, is_active=True
            ).order_by("name")[:100]
        else:
            context["states"] = State.objects.none()

        # Ciudades que tienen jugadores activos (solo si hay filtro de estado)
        state_filter = self.request.GET.get("state")
        if state_filter:
            city_ids = (
                active_players.filter(user__profile__state_id=state_filter)
                .exclude(user__profile__city__isnull=True)
                .values_list("user__profile__city_id", flat=True)
                .distinct()
            )
            context["cities"] = City.objects.filter(
                id__in=city_ids, is_active=True
            ).order_by("name")[:100]
        else:
            context["cities"] = City.objects.none()

        # Divisiones desde el modelo Player
        from apps.events.models import Division

        context["divisions"] = Division.objects.filter(is_active=True).order_by("name")

        # Filtros actuales
        context["current_filters"] = {
            "search": self.request.GET.get("search", ""),
            "country": self.request.GET.get("country", ""),
            "state": self.request.GET.get("state", ""),
            "city": self.request.GET.get("city", ""),
            "division": self.request.GET.get("division", ""),
        }

        return context


def _get_client_ip(request):
    """Obtiene la IP del cliente, considerando proxies"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR", "unknown")
    return ip


def _check_login_rate_limit(request):
    """
    Verifica rate limiting para login y previene ataques de fuerza bruta.

    Returns:
        tuple: (is_allowed, remaining_attempts, is_blocked, block_seconds_remaining)
    """
    from django.core.cache import cache

    ip_address = _get_client_ip(request)

    # Configuración de rate limiting
    MAX_ATTEMPTS_PER_HOUR = 10  # Máximo 10 intentos por hora
    MAX_FAILED_ATTEMPTS = 5  # Máximo 5 intentos fallidos consecutivos
    BLOCK_DURATION = 900  # Bloquear por 15 minutos después de 5 intentos fallidos

    # Claves de caché
    rate_limit_key = f"login_rate_limit_{ip_address}"
    failed_attempts_key = f"login_failed_attempts_{ip_address}"
    blocked_key = f"login_blocked_{ip_address}"

    # Verificar si está bloqueado
    blocked_until = cache.get(blocked_key)
    if blocked_until:
        import time

        current_time = time.time()
        if current_time < blocked_until:
            seconds_remaining = int(blocked_until - current_time)
            return False, 0, True, seconds_remaining
        else:
            # El bloqueo expiró, limpiar
            cache.delete(blocked_key)
            cache.delete(failed_attempts_key)

    # Verificar rate limiting general (intentos por hora)
    attempts_count = cache.get(rate_limit_key, 0)
    if attempts_count >= MAX_ATTEMPTS_PER_HOUR:
        return False, 0, False, 0

    # Obtener intentos fallidos consecutivos
    failed_attempts = cache.get(failed_attempts_key, 0)

    remaining = MAX_ATTEMPTS_PER_HOUR - attempts_count
    return True, remaining, False, 0


def _increment_login_attempts(request, is_successful=False):
    """
    Incrementa contadores de intentos de login.

    Args:
        request: HttpRequest object
        is_successful: Si el login fue exitoso
    """
    import time

    from django.core.cache import cache

    ip_address = _get_client_ip(request)

    # Configuración
    MAX_FAILED_ATTEMPTS = 5
    BLOCK_DURATION = 900  # 15 minutos
    RATE_LIMIT_WINDOW = 3600  # 1 hora

    # Claves de caché
    rate_limit_key = f"login_rate_limit_{ip_address}"
    failed_attempts_key = f"login_failed_attempts_{ip_address}"
    blocked_key = f"login_blocked_{ip_address}"

    if is_successful:
        # Login exitoso: limpiar contadores de intentos fallidos
        cache.delete(failed_attempts_key)
        # Pero mantener el rate limit general (para prevenir abuso)
        # No incrementar el contador general en login exitoso
    else:
        # Login fallido: incrementar contadores
        # Incrementar rate limit general
        attempts_count = cache.get(rate_limit_key, 0)
        cache.set(rate_limit_key, attempts_count + 1, RATE_LIMIT_WINDOW)

        # Incrementar intentos fallidos consecutivos
        failed_attempts = cache.get(failed_attempts_key, 0) + 1
        cache.set(failed_attempts_key, failed_attempts, BLOCK_DURATION)

        # Si se exceden los intentos fallidos, bloquear
        if failed_attempts >= MAX_FAILED_ATTEMPTS:
            block_until = time.time() + BLOCK_DURATION
            cache.set(blocked_key, block_until, BLOCK_DURATION)


class PublicLoginView(BaseLoginView):
    """
    Vista de login público con diseño MLB - Usa correo electrónico

    Rate Limiting:
    - Máximo 10 intentos por hora por IP
    - Bloqueo de 15 minutos después de 5 intentos fallidos consecutivos
    """

    template_name = "accounts/public_login.html"
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        """Verificar rate limiting antes de procesar el request"""
        # Verificar rate limiting
        is_allowed, remaining, is_blocked, seconds_remaining = _check_login_rate_limit(
            request
        )

        if is_blocked:
            messages.error(
                request,
                _(
                    "Too many failed login attempts. Please try again in %(minutes)d minutes."
                )
                % {"minutes": (seconds_remaining // 60) + 1},
            )
            # Redirigir a home con mensaje de error
            request.session["login_error"] = True
            request.session["login_blocked"] = True
            request.session["block_seconds_remaining"] = seconds_remaining
            return redirect(f"/?login_error=1&blocked=1")

        if not is_allowed:
            messages.error(
                request,
                _(
                    "Too many login attempts. Please try again later. (Remaining attempts: %(remaining)d)"
                )
                % {"remaining": remaining},
            )
            request.session["login_error"] = True
            return redirect(f"/?login_error=1&rate_limit=1")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Redirigir según el tipo de usuario después del login"""
        # Login exitoso: limpiar contadores de intentos fallidos
        _increment_login_attempts(self.request, is_successful=True)

        super().form_valid(form)
        user = form.get_user()

        # Verificar que la cuenta esté activa
        if not user.is_active:
            from django.contrib.auth import logout

            logout(self.request)
            messages.error(
                self.request,
                _("This account is inactive. Please contact the administrator."),
            )
            return redirect("accounts:login")

        # Crear perfil si no existe
        from .models import UserProfile

        if not hasattr(user, "profile"):
            UserProfile.objects.create(user=user, user_type="player")

        # IMPORTANTE: Los jugadores NO pueden iniciar sesión
        # Solo padres, managers y administradores
        if hasattr(user, "profile") and user.profile.is_player:
            from django.contrib.auth import logout

            logout(self.request)
            messages.error(
                self.request,
                _(
                    "Players cannot log in. Please contact your parent/guardian to manage your information."
                ),
            )
            return redirect("accounts:login")

        # Redirigir según el tipo de usuario
        if user.is_superuser or user.is_staff:
            # Admin va al dashboard
            messages.success(
                self.request,
                _("Welcome, %(name)s!") % {"name": user.get_full_name()},
            )
            return redirect("/dashboard/")
        elif hasattr(user, "profile"):
            if user.profile.is_team_manager:
                # Manager va al panel
                messages.success(
                    self.request,
                    _("Welcome, %(name)s!") % {"name": user.get_full_name()},
                )
                return redirect("panel")
            elif user.profile.is_parent:
                # Padre va al panel
                messages.success(
                    self.request,
                    _("Welcome, %(name)s!") % {"name": user.get_full_name()},
                )
                return redirect("panel")

        # Por defecto, ir al panel
        return redirect("panel")

    def form_invalid(self, form):
        """Si el formulario es inválido, registrar intento fallido y redirigir"""
        # Registrar intento fallido
        _increment_login_attempts(self.request, is_successful=False)

        # Verificar si ahora está bloqueado después de este intento
        is_allowed, remaining, is_blocked, seconds_remaining = _check_login_rate_limit(
            self.request
        )

        # Guardar los datos del formulario y errores en la sesión
        self.request.session["login_error"] = True
        self.request.session["login_form_data"] = {
            "username": self.request.POST.get("username", ""),
        }

        if is_blocked:
            self.request.session["login_blocked"] = True
            self.request.session["block_seconds_remaining"] = seconds_remaining
            messages.error(
                self.request,
                _(
                    "Too many failed login attempts. Your IP has been temporarily blocked. Please try again in %(minutes)d minutes."
                )
                % {"minutes": (seconds_remaining // 60) + 1},
            )
            return redirect(f"/?login_error=1&blocked=1")
        elif not is_allowed:
            messages.error(
                self.request,
                _(
                    "Too many login attempts. Please try again later. (Remaining attempts: %(remaining)d)"
                )
                % {"remaining": remaining},
            )
            return redirect(f"/?login_error=1&rate_limit=1")

        # Redirigir a la página principal con parámetro de error
        return redirect(f"/?login_error=1")


class PublicRegistrationView(CreateView):
    """
    Vista pública de registro

    Security Features:
    - Rate Limiting: Máximo 3 registros por hora por IP
    - Protección contra spam y bots
    """

    form_class = PublicRegistrationForm
    template_name = "accounts/public_register.html"
    success_url = reverse_lazy("panel")

    def dispatch(self, request, *args, **kwargs):
        """Verificar rate limiting antes de procesar el request"""
        from django.core.cache import cache

        # Obtener IP del cliente
        ip_address = _get_client_ip(request)

        # Configuración de rate limiting
        MAX_REGISTRATIONS_PER_HOUR = 3

        # Clave de caché única por IP
        cache_key = f"registration_attempts_{ip_address}"

        # Obtener intentos actuales
        attempts = cache.get(cache_key, 0)

        if attempts >= MAX_REGISTRATIONS_PER_HOUR:
            messages.error(
                request,
                _(
                    "Too many registration attempts from your IP address. "
                    "Please try again later. Maximum %(max)d registrations per hour allowed."
                )
                % {"max": MAX_REGISTRATIONS_PER_HOUR},
            )
            return redirect("accounts:public_register")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        from django.core.cache import cache

        # Incrementar contador de intentos de registro
        ip_address = _get_client_ip(self.request)
        cache_key = f"registration_attempts_{ip_address}"
        attempts = cache.get(cache_key, 0)
        cache.set(cache_key, attempts + 1, 3600)  # Incrementar y guardar por 1 hora

        super().form_valid(form)
        # Autenticar al usuario después del registro
        login(self.request, self.object)

        # Mostrar mensaje con el username generado
        username = self.object.username
        messages.success(
            self.request,
            _("Registration successful! Welcome. Your username is: %(username)s")
            % {"username": username},
        )

        return redirect("panel")

    def form_invalid(self, form):
        """Si el formulario es inválido, registrar intento fallido y redirigir"""
        # Registrar intento fallido
        _increment_login_attempts(self.request, is_successful=False)

        # Verificar si ahora está bloqueado después de este intento
        is_allowed, remaining, is_blocked, seconds_remaining = _check_login_rate_limit(
            self.request
        )

        # Guardar los datos del formulario y errores en la sesión
        self.request.session["login_error"] = True
        self.request.session["login_form_data"] = {
            "username": self.request.POST.get("username", ""),
        }

        if is_blocked:
            self.request.session["login_blocked"] = True
            self.request.session["block_seconds_remaining"] = seconds_remaining
            messages.error(
                self.request,
                _(
                    "Too many failed login attempts. Your IP has been temporarily blocked. Please try again in %(minutes)d minutes."
                )
                % {"minutes": (seconds_remaining // 60) + 1},
            )
            return redirect(f"/?login_error=1&blocked=1")
        elif not is_allowed:
            messages.error(
                self.request,
                _(
                    "Too many login attempts. Please try again later. (Remaining attempts: %(remaining)d)"
                )
                % {"remaining": remaining},
            )
            return redirect(f"/?login_error=1&rate_limit=1")

        # Redirigir a la página principal con parámetro de error
        return redirect(f"/?login_error=1")


class PublicPlayerProfileView(DetailView):
    """Vista pública del perfil de jugador - No requiere autenticación"""

    model = Player
    template_name = "accounts/public_player_profile.html"
    context_object_name = "player"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        # Solo mostrar jugadores activos públicamente
        return Player.objects.filter(is_active=True).select_related(
            "user", "user__profile", "team"
        )

    def get_object(self, queryset=None):
        """Obtiene el objeto por slug o pk"""
        if queryset is None:
            queryset = self.get_queryset()

        # Verificar si viene pk primero (URL con int tiene prioridad)
        pk = self.kwargs.get("pk")
        if pk is not None:
            try:
                player = queryset.get(pk=pk)
                # Si el jugador no tiene slug, generarlo
                if not player.slug:
                    player.save()  # Esto generará el slug automáticamente
                return player
            except Player.DoesNotExist:
                from django.http import Http404

                raise Http404("No se encontró el jugador con ese ID")

        # Si no hay pk, buscar por slug
        slug = self.kwargs.get(self.slug_url_kwarg)
        if slug:
            try:
                return queryset.get(slug=slug)
            except Player.DoesNotExist:
                from django.http import Http404

                raise Http404("No se encontró el jugador con ese slug")

        # Si no hay ni pk ni slug, usar el método por defecto
        return super().get_object(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        player = context["player"]

        # Calcular edad actual basada en fecha de nacimiento
        from datetime import date

        current_age = None
        if player.user.profile.birth_date:
            today = date.today()
            birth_date = player.user.profile.birth_date
            current_age = today.year - birth_date.year
            # Ajustar si aún no ha cumplido años este año
            if (today.month, today.day) < (birth_date.month, birth_date.day):
                current_age -= 1
        context["current_age"] = current_age

        # Generar código QR para el perfil del jugador
        context["player_qr_code"] = None
        try:
            import base64
            from io import BytesIO

            import qrcode

            player_url = player.get_absolute_url()
            if player_url and player_url != "#":
                qr_url = self.request.build_absolute_uri(player_url)
            else:
                qr_url = self.request.build_absolute_uri(self.request.path)

            # Crear código QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=1,
            )
            qr.add_data(qr_url)
            qr.make(fit=True)

            # Crear imagen del QR
            img = qr.make_image(fill_color="black", back_color="white")

            # Convertir a base64 para incluir en el HTML
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode()
            context["player_qr_code"] = f"data:image/png;base64,{img_str}"
        except ImportError as e:
            # Si no está instalada la librería, usar fallback
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(f"qrcode library not installed: {e}")
            context["player_qr_code"] = None
        except Exception as e:
            # Log del error pero continuar
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error generating QR code: {e}")
            context["player_qr_code"] = None

        # Obtener eventos relacionados si existe la app events
        try:
            from django.utils import timezone

            from apps.events.models import Event

            # Eventos futuros relacionados con la división del jugador
            upcoming_events = []
            if player.division:
                upcoming_events = (
                    Event.objects.filter(
                        divisions__name=player.division,
                        start_date__gte=timezone.now().date(),
                        status="published",
                    )
                    .distinct()
                    .order_by("start_date")[:7]
                )

            context["upcoming_events"] = upcoming_events
        except ImportError:
            context["upcoming_events"] = []

        return context


class FrontPlayerProfileView(LoginRequiredMixin, DetailView):
    """Vista del perfil de jugador para el front - Requiere autenticación"""

    model = Player
    template_name = "accounts/front_player_profile.html"
    context_object_name = "player"

    def get_queryset(self):
        # Solo mostrar jugadores activos
        return Player.objects.filter(is_active=True).select_related(
            "user", "user__profile", "team"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        player = context["player"]

        # Obtener eventos relacionados si existe la app events
        try:
            from django.utils import timezone

            from apps.events.models import Event

            # Eventos futuros relacionados con la división del jugador
            upcoming_events = []
            if player.division:
                upcoming_events = (
                    Event.objects.filter(
                        divisions__name=player.division,
                        start_date__gte=timezone.now().date(),
                        status="published",
                    )
                    .distinct()
                    .order_by("start_date")[:7]
                )

            context["upcoming_events"] = upcoming_events
        except ImportError:
            context["upcoming_events"] = []

        return context


def _check_rate_limit(request, cache_key_prefix, max_requests=100, window_seconds=3600):
    """
    Verifica rate limiting usando caché de Django.

    Args:
        request: HttpRequest object
        cache_key_prefix: Prefijo para la clave de caché
        max_requests: Número máximo de requests permitidos
        window_seconds: Ventana de tiempo en segundos (por defecto 1 hora)

    Returns:
        tuple: (is_allowed, remaining_requests)
    """
    from django.core.cache import cache
    from django.utils import timezone

    # Obtener IP del cliente
    ip_address = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
    if not ip_address:
        ip_address = request.META.get("REMOTE_ADDR", "unknown")

    # Crear clave de caché única por IP
    cache_key = f"{cache_key_prefix}_{ip_address}"

    # Obtener contador actual
    request_count = cache.get(cache_key, 0)

    # Verificar si se excedió el límite
    if request_count >= max_requests:
        return False, 0

    # Incrementar contador
    cache.set(cache_key, request_count + 1, window_seconds)

    return True, max_requests - request_count - 1


def instagram_posts_api(request):
    """
    API endpoint para obtener posts de Instagram
    Siempre devuelve exactamente 6 posts (completa con placeholders si es necesario)

    Rate Limiting: 100 requests por hora por IP
    Caché: 15 minutos
    """
    from urllib.parse import quote

    from django.core.cache import cache
    from django.http import JsonResponse

    # Rate limiting: 100 requests por hora por IP
    is_allowed, remaining = _check_rate_limit(
        request, "instagram_posts_api", max_requests=100, window_seconds=3600
    )

    if not is_allowed:
        return JsonResponse(
            {"error": "Rate limit exceeded. Please try again later."}, status=429
        )

    # Validar parámetros GET
    limit = request.GET.get("limit", "6")
    try:
        limit = int(limit)
        # Limitar entre 1 y 12
        limit = max(1, min(12, limit))
    except (ValueError, TypeError):
        limit = 6

    # Clave de caché
    cache_key = f"instagram_posts_api_{limit}"

    # Intentar obtener del caché
    cached_posts = cache.get(cache_key)
    if cached_posts is not None:
        # Agregar header de rate limit
        response = JsonResponse(cached_posts, safe=False)
        response["X-RateLimit-Remaining"] = str(remaining)
        response["X-RateLimit-Limit"] = "100"
        return response

    try:
        from .instagram_api import get_instagram_posts

        username = getattr(settings, "INSTAGRAM_USERNAME", "ncs_international")
        # Solicitar posts del RSS feed
        posts = get_instagram_posts(username=username, limit=limit)

        # Reemplazar URLs de imágenes con URLs de proxy para evitar CORS
        for post in posts:
            if post.get("image_url"):
                # Usar el endpoint de proxy en lugar de la URL directa
                image_url = post["image_url"]
                post["image_url"] = (
                    f"/accounts/api/instagram/image-proxy/?url={quote(image_url)}"
                )

        # Limitar a exactamente el número solicitado
        posts = posts[:limit]

        # Guardar en caché por 15 minutos (900 segundos)
        cache.set(cache_key, posts, 900)

        # Log para debugging
        print(
            f"Instagram API: Devolviendo {len(posts)} posts para {username} (solicitados: {limit})"
        )

        # Agregar headers de rate limit
        response = JsonResponse(posts, safe=False)
        response["X-RateLimit-Remaining"] = str(remaining)
        response["X-RateLimit-Limit"] = "100"
        return response

    except Exception as e:
        # Si hay error, retornar lista vacía con información del error
        print(f"Error en instagram_posts_api: {e}")
        import traceback

        traceback.print_exc()
        response = JsonResponse([], safe=False)
        response["X-RateLimit-Remaining"] = str(remaining)
        response["X-RateLimit-Limit"] = "100"
        return response


def instagram_image_proxy(request):
    """
    Proxy para imágenes de Instagram que evita problemas de CORS.
    Descarga la imagen desde Instagram y la sirve desde nuestro servidor.

    Rate Limiting: 200 requests por hora por IP
    Validación: Solo URLs de Instagram permitidas
    Caché: 1 hora
    """
    import hashlib
    from urllib.parse import unquote, urlparse

    from django.core.cache import cache
    from django.http import HttpResponse

    # Rate limiting: 200 requests por hora por IP (más permisivo para imágenes)
    is_allowed, remaining = _check_rate_limit(
        request, "instagram_image_proxy", max_requests=200, window_seconds=3600
    )

    if not is_allowed:
        return HttpResponse("Rate limit exceeded. Please try again later.", status=429)

    # Validar y obtener URL
    image_url = request.GET.get("url")
    if not image_url:
        return HttpResponse("Missing 'url' parameter", status=400)

    # Decodificar URL
    try:
        image_url = unquote(image_url)
    except Exception:
        pass

    # Validar que sea una URL válida
    try:
        parsed_url = urlparse(image_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return HttpResponse("Invalid URL format", status=400)

        # Validar que sea de un dominio permitido (Instagram)
        allowed_domains = [
            "instagram.com",
            "cdninstagram.com",
            "fbcdn.net",
            "scontent",
            "scontent.cdninstagram.com",
        ]

        domain_valid = any(
            allowed_domain in parsed_url.netloc.lower()
            for allowed_domain in allowed_domains
        )

        if not domain_valid:
            return HttpResponse("Only Instagram image URLs are allowed", status=403)
    except Exception as e:
        return HttpResponse(f"Invalid URL: {str(e)}", status=400)

    # Validar referer (opcional pero recomendado)
    referer = request.META.get("HTTP_REFERER", "")
    if referer:
        from django.conf import settings

        allowed_hosts = getattr(settings, "ALLOWED_HOSTS", [])
        referer_host = urlparse(referer).netloc
        # Permitir si el referer es de nuestro dominio o está vacío
        if referer_host and referer_host not in allowed_hosts:
            # No bloquear, solo registrar
            print(f"Warning: Request from unexpected referer: {referer_host}")

    # Crear clave de caché basada en la URL
    url_hash = hashlib.md5(image_url.encode()).hexdigest()
    cache_key = f"instagram_image_proxy_{url_hash}"

    # Intentar obtener del caché
    cached_image = cache.get(cache_key)
    if cached_image is not None:
        content, content_type = cached_image
        response = HttpResponse(content, content_type=content_type)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET"
        response["Cache-Control"] = "public, max-age=3600"
        response["X-RateLimit-Remaining"] = str(remaining)
        response["X-RateLimit-Limit"] = "200"
        return response

    try:
        # Descargar la imagen desde Instagram
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.instagram.com/",
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
        }
        response = requests.get(image_url, headers=headers, timeout=10, stream=True)
        response.raise_for_status()

        # Determinar content type
        content_type = response.headers.get("Content-Type", "image/jpeg")

        # Validar que sea una imagen
        if not content_type.startswith("image/"):
            return HttpResponse("URL does not point to an image", status=400)

        # Limitar tamaño de imagen (10MB máximo)
        content = response.content
        if len(content) > 10 * 1024 * 1024:  # 10MB
            return HttpResponse("Image too large (max 10MB)", status=413)

        # Guardar en caché por 1 hora (3600 segundos)
        cache.set(cache_key, (content, content_type), 3600)

        # Retornar la imagen con headers apropiados
        django_response = HttpResponse(content, content_type=content_type)
        # Headers para evitar problemas de CORS
        django_response["Access-Control-Allow-Origin"] = "*"
        django_response["Access-Control-Allow-Methods"] = "GET"
        # Cache por 1 hora
        django_response["Cache-Control"] = "public, max-age=3600"
        django_response["X-RateLimit-Remaining"] = str(remaining)
        django_response["X-RateLimit-Limit"] = "200"
        return django_response

    except requests.exceptions.Timeout:
        return HttpResponse("Request timeout", status=504)
    except requests.exceptions.RequestException as e:
        print(f"Error descargando imagen de Instagram: {e}")
        return HttpResponse("Error fetching image", status=502)
    except Exception as e:
        print(f"Error descargando imagen de Instagram: {e}")
        import traceback

        traceback.print_exc()
        return HttpResponse("Internal server error", status=500)
