"""
Vistas públicas - No requieren autenticación
"""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView as BaseLoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    TemplateView,
    DetailView,
    ListView,
    UpdateView,
)
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy

from django.conf import settings
from django.http import JsonResponse, HttpResponse
import requests
from .forms import PublicRegistrationForm, EmailAuthenticationForm, PlayerUpdateForm
from .models import Team, Player, PlayerParent


class PublicHomeView(TemplateView):
    """Vista pública del home"""

    template_name = "accounts/public_home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener eventos próximos (si existe la app events)
        try:
            from apps.events.models import Event

            now = timezone.now()
            upcoming_events = (
                Event.objects.filter(start_date__gte=now.date(), status="published")
                .select_related("category")
                .prefetch_related("divisions")[:6]
            )

            # Eventos de hoy
            today_events = Event.objects.filter(
                start_date=now.date(), status="published"
            )[:3]

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
                    .filter(start_date__gte=now.date(), status="published")
                    .select_related("category", "event_type", "city", "state")
                    .prefetch_related("divisions")
                    .order_by("start_date")
                    .first()
                )

            context["merida_event"] = future_merida
        except ImportError:
            context["upcoming_events"] = []
            context["today_events"] = []
            context["merida_event"] = None

        # Estadísticas públicas
        context["total_teams"] = Team.objects.filter(is_active=True).count()
        context["total_players"] = Player.objects.filter(is_active=True).count()

        # Obtener tipos de eventos activos
        try:
            from apps.events.models import EventType

            context["event_types"] = EventType.objects.filter(is_active=True).order_by(
                "name"
            )
        except ImportError:
            context["event_types"] = []

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


class PublicPlayerListView(ListView):
    """Vista pública de lista de jugadores - No requiere autenticación"""

    model = Player
    template_name = "accounts/public_player_list.html"
    context_object_name = "players"
    paginate_by = 12

    def get_queryset(self):
        queryset = (
            Player.objects.filter(is_active=True)
            .select_related("user", "user__profile", "team")
            .order_by("user__last_name", "user__first_name")
        )

        # Búsqueda
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(user__email__icontains=search)
                | Q(team__name__icontains=search)
            )

        # Filtro por equipo
        team_filter = self.request.GET.get("team")
        if team_filter:
            queryset = queryset.filter(team_id=team_filter)

        # Filtro por posición
        position_filter = self.request.GET.get("position")
        if position_filter:
            queryset = queryset.filter(position=position_filter)

        # Filtro por división
        division_filter = self.request.GET.get("division")
        if division_filter:
            queryset = queryset.filter(division=division_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Agregar equipos para el filtro
        context["teams"] = Team.objects.filter(is_active=True).order_by("name")

        # Agregar opciones de posición
        context["position_choices"] = Player.POSITION_CHOICES

        # Agregar opciones de división
        context["division_choices"] = Player.DIVISION_CHOICES

        # Filtros actuales
        context["current_filters"] = {
            "search": self.request.GET.get("search", ""),
            "team": self.request.GET.get("team", ""),
            "position": self.request.GET.get("position", ""),
            "division": self.request.GET.get("division", ""),
        }

        return context


class PublicLoginView(BaseLoginView):
    """Vista de login público con diseño MLB - Usa correo electrónico"""

    template_name = "accounts/public_login.html"
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        """Redirigir según el tipo de usuario después del login"""
        response = super().form_valid(form)
        user = form.get_user()

        # Verificar que la cuenta esté activa
        if not user.is_active:
            from django.contrib.auth import logout

            logout(self.request)
            messages.error(
                self.request,
                "Esta cuenta está inactiva. Por favor, contacta al administrador.",
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
                "Los jugadores no pueden iniciar sesión. Por favor, contacta a tu padre/acudiente para gestionar tu información.",
            )
            return redirect("accounts:login")

        # Redirigir según el tipo de usuario
        if user.is_superuser or user.is_staff:
            # Admin va al admin panel
            return redirect("/admin/")
        elif hasattr(user, "profile"):
            if user.profile.is_team_manager:
                # Manager va al panel
                messages.success(self.request, f"¡Bienvenido, {user.get_full_name()}!")
                return redirect("accounts:panel")
            elif user.profile.is_parent:
                # Padre va al panel
                messages.success(self.request, f"¡Bienvenido, {user.get_full_name()}!")
                return redirect("accounts:panel")

        # Por defecto, ir al panel
        return redirect("accounts:panel")

    def form_invalid(self, form):
        """Si el formulario es inválido, redirigir a la página principal con el modal abierto"""
        # Guardar los datos del formulario y errores en la sesión
        self.request.session["login_error"] = True
        self.request.session["login_form_data"] = {
            "username": self.request.POST.get("username", ""),
        }
        # Redirigir a la página principal con parámetro de error
        return redirect(f"/?login_error=1")


class PublicRegistrationView(CreateView):
    """Vista pública de registro"""

    form_class = PublicRegistrationForm
    template_name = "accounts/public_register.html"
    success_url = reverse_lazy("accounts:profile")

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
        elif user_type == "parent":
            messages.info(
                self.request,
                "Ahora puedes registrar a tu(s) jugador(es) desde el panel.",
            )
            return redirect("accounts:panel")

        return response


class PublicPlayerProfileView(DetailView):
    """Vista pública del perfil de jugador - No requiere autenticación"""

    model = Player
    template_name = "accounts/public_player_profile.html"
    context_object_name = "player"

    def get_queryset(self):
        # Solo mostrar jugadores activos públicamente
        return Player.objects.filter(is_active=True).select_related(
            "user", "user__profile", "team"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        player = context["player"]

        # Obtener eventos relacionados si existe la app events
        try:
            from apps.events.models import Event
            from django.utils import timezone

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
            from apps.events.models import Event
            from django.utils import timezone

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


class FrontPlayerUpdateView(LoginRequiredMixin, UpdateView):
    """Vista de edición de jugador para el front - Requiere autenticación"""

    model = Player
    form_class = PlayerUpdateForm
    template_name = "accounts/front_player_edit.html"

    def dispatch(self, request, *args, **kwargs):
        player = self.get_object()

        # Verificar si el usuario es padre/acudiente del jugador
        is_parent = False
        if hasattr(request.user, "profile") and request.user.profile.is_parent:
            is_parent = PlayerParent.objects.filter(
                parent=request.user, player=player
            ).exists()

        # Verificar si es manager del equipo del jugador
        is_manager = False
        if hasattr(request.user, "profile"):
            is_manager = (
                request.user.profile.is_team_manager
                and player.team
                and player.team.manager == request.user
            )

        is_staff = request.user.is_staff or request.user.is_superuser

        # Los jugadores NO pueden editar su propia información (están inactivos)
        # Solo padres, managers y staff pueden editar
        if not is_parent and not is_manager and not is_staff:
            messages.error(request, "No tienes permiso para editar este jugador.")
            return redirect("accounts:front_player_profile", pk=player.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pasar información del usuario para que el formulario sepa si es padre
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Determinar si el usuario es padre del jugador para ocultar campos en el template
        is_parent = False
        if (
            hasattr(self.request.user, "profile")
            and self.request.user.profile.is_parent
        ):
            is_parent = PlayerParent.objects.filter(
                parent=self.request.user, player=self.object
            ).exists()
        context["is_parent_editing"] = is_parent and not (
            self.request.user.is_staff or self.request.user.is_superuser
        )
        return context

    def get_success_url(self):
        # Redirigir al perfil del front después de editar
        return reverse_lazy(
            "accounts:front_player_profile", kwargs={"pk": self.object.pk}
        )

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
            return redirect("accounts:front_player_profile", pk=player.pk)
        else:
            messages.success(
                self.request, "Información del jugador actualizada exitosamente."
            )
            return super().form_valid(form)


def instagram_posts_api(request):
    """
    API endpoint para obtener posts de Instagram
    Siempre devuelve exactamente 12 posts (completa con placeholders si es necesario)
    """
    try:
        from .instagram_api import get_instagram_posts
        from urllib.parse import quote

        username = getattr(settings, "INSTAGRAM_USERNAME", "ncs_international")
        # Solicitar 6 posts del RSS feed
        posts = get_instagram_posts(username=username, limit=6)

        # Reemplazar URLs de imágenes con URLs de proxy para evitar CORS
        for post in posts:
            if post.get("image_url"):
                # Usar el endpoint de proxy en lugar de la URL directa
                image_url = post["image_url"]
                post["image_url"] = (
                    f"/accounts/api/instagram/image-proxy/?url={quote(image_url)}"
                )

        # Limitar a exactamente 6 posts (sin placeholders)
        posts = posts[:6]

        # Log para debugging
        print(
            f"Instagram API: Devolviendo {len(posts)} posts para {username} (solicitados: 6)"
        )
        if posts:
            print(
                f"Primer post: {posts[0].get('image_url', 'No image_url')[:100] if posts[0].get('image_url') else 'Placeholder'}"
            )

        return JsonResponse(posts, safe=False)
    except Exception as e:
        # Si hay error, retornar lista vacía con información del error
        print(f"Error en instagram_posts_api: {e}")
        import traceback

        traceback.print_exc()
        return JsonResponse([], safe=False)


def instagram_image_proxy(request):
    """
    Proxy para imágenes de Instagram que evita problemas de CORS.
    Descarga la imagen desde Instagram y la sirve desde nuestro servidor.
    """
    image_url = request.GET.get("url")
    if not image_url:
        return HttpResponse(status=400)

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

        # Retornar la imagen con headers apropiados
        django_response = HttpResponse(response.content, content_type=content_type)
        # Headers para evitar problemas de CORS
        django_response["Access-Control-Allow-Origin"] = "*"
        django_response["Access-Control-Allow-Methods"] = "GET"
        # Cache por 1 hora
        django_response["Cache-Control"] = "public, max-age=3600"
        return django_response

    except Exception as e:
        print(f"Error descargando imagen de Instagram: {e}")
        import traceback

        traceback.print_exc()
        return HttpResponse(status=500)
