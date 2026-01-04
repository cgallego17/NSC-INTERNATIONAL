from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView as BaseLoginView
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    TemplateView,
)
from django.db.models import Q
from django.utils import timezone

from .forms import (
    PublicRegistrationForm,
    UserProfileForm,
    UserUpdateForm,
    TeamForm,
    PlayerRegistrationForm,
    PlayerUpdateForm,
)
from .models import UserProfile, Team, Player


class PublicHomeView(TemplateView):
    """Vista pública del home"""

    template_name = "accounts/public_home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener eventos próximos (si existe la app events)
        try:
            from apps.events.models import Event, EventType

            now = timezone.now()
            # Obtener todos los eventos activos (excluyendo cancelados)
            # Mostrar todos los eventos disponibles, priorizando los futuros
            upcoming_events = (
                Event.objects.exclude(status="cancelled")
                .select_related("category", "event_type")
                .prefetch_related("divisions")
                .order_by("-start_date")  # Más recientes primero
            )

            # Eventos de hoy
            today_events = Event.objects.filter(start_date=now.date()).exclude(
                status="cancelled"
            )[:3]

            # Tipos de eventos activos
            event_types = EventType.objects.filter(is_active=True).order_by("name")

            context["upcoming_events"] = upcoming_events
            context["today_events"] = today_events
            context["event_types"] = event_types

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
            # Priorizar eventos futuros, luego los más recientes
            merida_event = (
                Event.objects.exclude(status="cancelled")
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

            # Si aún no hay evento de Mérida, usar el primer evento próximo como fallback
            if not future_merida:
                future_merida = (
                    Event.objects.exclude(status="cancelled")
                    .filter(start_date__gte=now.date())
                    .select_related("category", "event_type", "city", "state")
                    .prefetch_related("divisions")
                    .order_by("start_date")
                    .first()
                )

            context["merida_event"] = future_merida
        except ImportError:
            context["upcoming_events"] = []
            context["today_events"] = []
            context["event_types"] = []
            context["merida_event"] = None

        # Estadísticas públicas
        context["total_teams"] = Team.objects.filter(is_active=True).count()
        context["total_players"] = Player.objects.filter(is_active=True).count()

        # Instagram username
        context["instagram_username"] = getattr(
            settings, "INSTAGRAM_USERNAME", "ncs_international"
        )

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

        return context


class PublicLoginView(BaseLoginView):
    """Vista de login público con diseño MLB"""

    template_name = "accounts/public_login.html"

    def form_valid(self, form):
        """Redirigir según el tipo de usuario después del login"""
        super().form_valid(form)
        user = form.get_user()

        # Crear perfil si no existe
        if not hasattr(user, "profile"):
            UserProfile.objects.create(user=user, user_type="player")

        # Redirigir según el tipo de usuario
        if user.is_superuser or user.is_staff:
            # Admin va al admin panel
            return redirect("/admin/")
        elif hasattr(user, "profile"):
            if user.profile.is_team_manager:
                # Manager va al panel
                messages.success(self.request, f"¡Bienvenido, {user.get_full_name()}!")
                return redirect("panel")
            elif user.profile.is_player:
                # Jugador va al panel
                messages.success(self.request, f"¡Bienvenido, {user.get_full_name()}!")
                return redirect("panel")

        # Por defecto, ir al panel
        return redirect("panel")


class PublicRegistrationView(CreateView):
    """Vista pública de registro"""

    form_class = PublicRegistrationForm
    template_name = "accounts/public_register.html"
    success_url = reverse_lazy("accounts:profile")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Asegurar que el idioma esté activado
        from django.utils import translation
        language = translation.get_language() or 'en'
        translation.activate(language)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        # Autenticar al usuario después del registro
        login(self.request, self.object)

        # Mostrar mensaje con el username generado
        username = self.object.username
        messages.success(
            self.request,
            f"¡Registro exitoso! Bienvenido. Tu nombre de usuario es: {username}",
        )

        # Si es manager, redirigir a crear equipo
        user_type = form.cleaned_data.get("user_type")
        if user_type == "team_manager":
            messages.info(
                self.request, "Ahora puedes crear tu primer equipo para comenzar."
            )
            return redirect("accounts:team_create")

        return response


class UserDashboardView(LoginRequiredMixin, TemplateView):
    """Panel de usuario frontal"""

    template_name = "accounts/user_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            # Crear perfil si no existe
            profile = UserProfile.objects.create(user=user, user_type="player")

        context["profile"] = profile

        # Si es jugador, obtener información del jugador
        if profile.is_player:
            try:
                context["player"] = user.player_profile
            except Player.DoesNotExist:
                context["player"] = None

        # Si es manager, obtener sus equipos
        if profile.is_team_manager:
            context["teams"] = Team.objects.filter(manager=user).order_by(
                "-created_at"
            )[:5]
            context["total_teams"] = Team.objects.filter(manager=user).count()
            context["total_players"] = Player.objects.filter(team__manager=user).count()
            context["recent_players"] = Player.objects.filter(
                team__manager=user
            ).order_by("-created_at")[:5]

        # Obtener eventos próximos si existe la app events
        try:
            from apps.events.models import Event

            now = timezone.now()
            context["upcoming_events"] = (
                Event.objects.filter(start_date__gte=now.date(), status="published")
                .select_related("category")
                .prefetch_related("divisions")[:5]
            )
        except ImportError:
            context["upcoming_events"] = []

        # Obtener mensajes activos del marquee
        from .models import MarqueeMessage
        marquee_messages = MarqueeMessage.objects.filter(is_active=True).order_by("order", "-created_at")
        context["marquee_messages"] = marquee_messages

        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para actualizar perfil"""

    model = UserProfile
    form_class = UserProfileForm
    template_name = "accounts/profile_edit.html"
    success_url = reverse_lazy("panel")

    def get_object(self):
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, "Perfil actualizado exitosamente.")
        return super().form_valid(form)


class UserInfoUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para actualizar información básica del usuario"""

    model = User
    form_class = UserUpdateForm
    template_name = "accounts/user_edit.html"
    success_url = reverse_lazy("panel")

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Información actualizada exitosamente.")
        return super().form_valid(form)


# ===== VISTAS DE EQUIPOS =====


class TeamListView(LoginRequiredMixin, ListView):
    """Lista de equipos"""

    model = Team
    template_name = "accounts/team_list.html"
    context_object_name = "teams"
    paginate_by = 20

    def get_queryset(self):
        queryset = Team.objects.filter(is_active=True)
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(city__name__icontains=search)
                | Q(state__name__icontains=search)
            )
        return queryset.order_by("name")


class TeamDetailView(LoginRequiredMixin, DetailView):
    """Detalle de equipo"""

    model = Team
    template_name = "accounts/team_detail.html"
    context_object_name = "team"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["players"] = self.object.players.filter(is_active=True)
        return context


class TeamCreateView(LoginRequiredMixin, CreateView):
    """Crear equipo (solo managers)"""

    model = Team
    form_class = TeamForm
    template_name = "accounts/team_form.html"
    success_url = reverse_lazy("accounts:team_list")

    def dispatch(self, request, *args, **kwargs):
        if (
            not hasattr(request.user, "profile")
            or not request.user.profile.is_team_manager
        ):
            messages.error(request, "Solo los managers pueden crear equipos.")
            return redirect("panel")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.manager = self.request.user
        messages.success(self.request, "Equipo creado exitosamente.")
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class TeamUpdateView(LoginRequiredMixin, UpdateView):
    """Actualizar equipo"""

    model = Team
    form_class = TeamForm
    template_name = "accounts/team_form.html"

    def dispatch(self, request, *args, **kwargs):
        team = self.get_object()
        if team.manager != request.user:
            messages.error(request, "No tienes permiso para editar este equipo.")
            return redirect("accounts:team_list")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("accounts:team_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Equipo actualizado exitosamente.")
        return super().form_valid(form)


# ===== VISTAS DE JUGADORES =====


class PlayerListView(LoginRequiredMixin, ListView):
    """Lista de jugadores"""

    model = Player
    template_name = "accounts/player_list.html"
    context_object_name = "players"
    paginate_by = 20

    def get_queryset(self):
        queryset = Player.objects.filter(is_active=True).select_related("user", "team")

        # Si es manager, solo mostrar jugadores de sus equipos
        if (
            hasattr(self.request.user, "profile")
            and self.request.user.profile.is_team_manager
        ):
            queryset = queryset.filter(team__manager=self.request.user)

        search = self.request.GET.get("search")
        team_filter = self.request.GET.get("team")

        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(user__username__icontains=search)
            )

        if team_filter:
            queryset = queryset.filter(team_id=team_filter)

        return queryset.order_by("user__last_name", "user__first_name")


class PlayerDetailView(LoginRequiredMixin, DetailView):
    """Detalle de jugador"""

    model = Player
    template_name = "accounts/player_detail.html"
    context_object_name = "player"


class PlayerRegistrationView(LoginRequiredMixin, CreateView):
    """Vista para que managers registren jugadores"""

    model = Player
    form_class = PlayerRegistrationForm
    template_name = "accounts/player_register.html"
    success_url = reverse_lazy("accounts:player_list")

    def dispatch(self, request, *args, **kwargs):
        if (
            not hasattr(request.user, "profile")
            or not request.user.profile.is_team_manager
        ):
            messages.error(request, "Solo los managers pueden registrar jugadores.")
            return redirect("panel")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["manager"] = self.request.user
        return kwargs

    def form_valid(self, form):
        # El formulario ya creó el usuario y el player, solo necesitamos obtener el nombre
        player = form.save()
        player_name = player.user.get_full_name() or player.user.username
        messages.success(
            self.request, f"Jugador {player_name} registrado exitosamente."
        )
        return redirect("accounts:player_list")


class PlayerUpdateView(LoginRequiredMixin, UpdateView):
    """Actualizar información de jugador"""

    model = Player
    form_class = PlayerUpdateForm
    template_name = "accounts/player_edit.html"

    def dispatch(self, request, *args, **kwargs):
        player = self.get_object()
        # Solo el jugador mismo o su manager pueden editar
        is_manager = False
        if hasattr(request.user, "profile"):
            is_manager = (
                request.user.profile.is_team_manager
                and player.team
                and player.team.manager == request.user
            )

        if player.user != request.user and not is_manager:
            messages.error(request, "No tienes permiso para editar este jugador.")
            return redirect("accounts:player_detail", pk=player.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("accounts:player_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        # Guardar la foto de perfil si se subió una nueva
        if (
            "profile_picture" in form.cleaned_data
            and form.cleaned_data["profile_picture"]
        ):
            player = form.save(commit=False)
            # Actualizar la foto de perfil del UserProfile
            if hasattr(player.user, "profile"):
                player.user.profile.profile_picture = form.cleaned_data[
                    "profile_picture"
                ]
                player.user.profile.save()
            player.save()
            messages.success(
                self.request, "Información del jugador actualizada exitosamente."
            )
            return redirect("accounts:player_detail", pk=player.pk)
        else:
            messages.success(
                self.request, "Información del jugador actualizada exitosamente."
            )
            return super().form_valid(form)


# Vista para manejar el perfil (redirige según el tipo de usuario)
@login_required
def profile_view(request):
    """Vista de perfil que redirige al dashboard"""
    return redirect("panel")
