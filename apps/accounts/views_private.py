"""
Vistas privadas - Requieren autenticación
"""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone, translation
from django.views.decorators.http import require_POST
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from apps.core.mixins import ManagerRequiredMixin

from .forms import (
    ParentPlayerRegistrationForm,
    PlayerRegistrationForm,
    PlayerUpdateForm,
    TeamForm,
    UserProfileForm,
    UserUpdateForm,
)
from .models import DashboardContent, Player, PlayerParent, Team, UserProfile


class UserDashboardView(LoginRequiredMixin, TemplateView):
    """Panel de usuario frontal"""

    template_name = "accounts/panel_usuario.html"

    def dispatch(self, request, *args, **kwargs):
        """Respetar el idioma seleccionado por el usuario"""
        # El idioma se maneja automáticamente por Django i18n
        # No necesitamos forzar ningún idioma aquí
        return super().dispatch(request, *args, **kwargs)

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

        # Si es padre, obtener sus jugadores
        if profile.is_parent:
            player_parents = PlayerParent.objects.filter(parent=user).select_related(
                "player", "player__team", "player__user"
            )
            context["children"] = player_parents
            context["total_children"] = player_parents.count()
            context["recent_children"] = player_parents.order_by("-created_at")[:5]

        # Obtener banners activos del dashboard (siempre devolver al menos uno para el bucle)
        try:
            from .models import DashboardBanner

            banners = DashboardBanner.objects.filter(is_active=True).order_by(
                "order", "-created_at"
            )
            # Si no hay banners, crear una lista vacía (el template mostrará el banner por defecto)
            context["dashboard_banners"] = list(banners) if banners.exists() else []
        except ImportError:
            context["dashboard_banners"] = []

        # Obtener eventos para la pestaña de eventos
        try:
            from apps.events.models import Event

            now = timezone.now()
            # Obtener TODOS los eventos creados (excepto cancelados)
            # Mostrar primero los futuros, luego los pasados
            context["upcoming_events"] = (
                Event.objects.exclude(status="cancelled")
                .select_related(
                    "category", "event_type", "city", "state", "primary_site"
                )
                .prefetch_related("divisions")
                .order_by(
                    "start_date"
                )  # Más próximos primero (orden ascendente por fecha)
            )
        except ImportError:
            context["upcoming_events"] = []

        # Obtener contenido del dashboard configurado por el admin según el tipo de usuario
        user_type = profile.user_type
        dashboard_content = (
            DashboardContent.objects.filter(is_active=True)
            .filter(Q(user_type=user_type) | Q(user_type="all"))
            .order_by("order", "-created_at")
        )
        context["dashboard_content"] = dashboard_content

        # Contexto adicional para los includes de los tabs
        # Formulario de equipo (para managers)
        if profile.is_team_manager:
            from .forms import TeamForm

            context["team_form"] = TeamForm()
            context["all_teams"] = Team.objects.filter(manager=user).order_by(
                "-created_at"
            )
            all_players = Player.objects.filter(team__manager=user).order_by(
                "-created_at"
            )
            # Anotar cada jugador con información sobre si es hijo del usuario actual
            if profile.is_parent:
                # Obtener IDs de jugadores que son hijos del usuario
                child_player_ids = set(
                    PlayerParent.objects.filter(parent=user).values_list(
                        "player_id", flat=True
                    )
                )
                # Agregar atributo is_child a cada jugador
                for player in all_players:
                    player.is_child = player.pk in child_player_ids
            else:
                # Si no es padre, ningún jugador es hijo
                for player in all_players:
                    player.is_child = False
            context["all_players"] = all_players

        # Formulario de jugador (para managers)
        if profile.is_team_manager:
            from .forms import PlayerRegistrationForm

            context["player_form"] = PlayerRegistrationForm(manager=user)

        # Formulario de jugador para padres
        if profile.is_parent:
            from .forms import ParentPlayerRegistrationForm

            context["parent_player_form"] = ParentPlayerRegistrationForm(parent=user)
            context["parent_players"] = (
                Player.objects.filter(parents__parent=user)
                .select_related("user", "team")
                .order_by("-created_at")
            )

        # Formulario de perfil
        from .forms import UserProfileForm, UserUpdateForm

        context["profile_form"] = UserProfileForm(instance=profile)
        context["user_form"] = UserUpdateForm(instance=user)

        # Obtener información del carrito de hoteles
        cart = self.request.session.get("hotel_cart", {})
        context["cart_count"] = len(cart)

        # Obtener número de reservas de hoteles del usuario
        try:
            from apps.locations.models import HotelReservation

            context["total_reservations"] = HotelReservation.objects.filter(
                user=user
            ).count()
        except ImportError:
            context["total_reservations"] = 0

        # Calcular total del carrito
        from decimal import Decimal

        from apps.locations.models import Hotel, HotelRoom, HotelService

        cart_total = Decimal("0.00")
        for item_id, item_data in cart.items():
            try:
                if item_data.get("type") == "room":
                    room = HotelRoom.objects.get(id=item_data.get("room_id"))
                    nights = int(item_data.get("nights", 1))
                    guests = int(item_data.get("guests", 1))
                    room_total = room.price_per_night * nights
                    services_total = Decimal("0.00")
                    for service_data in item_data.get("services", []):
                        try:
                            service = HotelService.objects.get(
                                id=service_data.get("service_id"),
                                hotel=room.hotel,
                                is_active=True,
                            )
                            quantity = int(service_data.get("quantity", 1))
                            service_price = service.price * quantity
                            if service.is_per_person:
                                service_price = service_price * guests
                            if service.is_per_night:
                                service_price = service_price * nights
                            services_total += service_price
                        except HotelService.DoesNotExist:
                            pass
                    cart_total += room_total + services_total
            except (HotelRoom.DoesNotExist, ValueError, KeyError):
                pass
        context["cart_total"] = cart_total

        # Obtener hoteles disponibles para la pestaña de reservas (con paginación)
        try:
            from django.core.paginator import Paginator

            hotels_queryset = (
                Hotel.objects.filter(is_active=True)
                .select_related("country", "state", "city")
                .order_by("hotel_name")
            )

            # Aplicar filtros de búsqueda si existen
            search = self.request.GET.get("search")
            if search:
                hotels_queryset = hotels_queryset.filter(
                    Q(hotel_name__icontains=search)
                    | Q(address__icontains=search)
                    | Q(city__name__icontains=search)
                )

            # Filtro por país
            country = self.request.GET.get("country")
            if country:
                hotels_queryset = hotels_queryset.filter(country_id=country)

            # Paginación
            paginator = Paginator(hotels_queryset, 12)  # 12 hoteles por página
            page_number = self.request.GET.get("page", 1)
            page_obj = paginator.get_page(page_number)

            context["hotels"] = page_obj
            context["is_paginated"] = page_obj.has_other_pages()
            context["page_obj"] = page_obj

            # También mantener available_hotels para compatibilidad
            context["available_hotels"] = list(page_obj)[:6]

            # Obtener países para el filtro
            from apps.locations.models import Country

            context["countries"] = Country.objects.filter(is_active=True).order_by(
                "name"
            )
        except Exception as e:
            context["hotels"] = []
            context["available_hotels"] = []
            context["countries"] = []
            context["is_paginated"] = False

        # Obtener reservas del usuario para el dashboard
        try:
            from apps.locations.models import HotelReservation

            context["user_reservations"] = (
                HotelReservation.objects.filter(user=user)
                .select_related("hotel", "room")
                .order_by("-created_at")[:5]
            )
            context["total_reservations"] = HotelReservation.objects.filter(
                user=user
            ).count()
            context["pending_reservations"] = HotelReservation.objects.filter(
                user=user, status="pending"
            ).count()
        except Exception:
            context["user_reservations"] = []
            context["total_reservations"] = 0
            context["pending_reservations"] = 0

        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para actualizar perfil"""

    model = UserProfile
    form_class = UserProfileForm
    template_name = "accounts/profile_edit.html"
    success_url = reverse_lazy("accounts:panel")

    def get_object(self):
        return self.request.user.profile

    def form_valid(self, form):
        # Guardar el perfil
        profile = form.save()

        # Si se actualizó el idioma preferido, guardarlo en la sesión
        if "preferred_language" in form.cleaned_data:
            preferred_language = form.cleaned_data["preferred_language"] or "en"
            language_key = getattr(translation, "LANGUAGE_SESSION_KEY", "_language")
            self.request.session[language_key] = preferred_language
            self.request.session["user_selected_language"] = True
            self.request.session.modified = True
            translation.activate(preferred_language)

        messages.success(self.request, "Perfil actualizado exitosamente.")
        return super().form_valid(form)


class UserInfoUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para actualizar información básica del usuario"""

    model = User
    form_class = UserUpdateForm
    template_name = "accounts/user_edit.html"
    success_url = reverse_lazy("accounts:panel")

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


class TeamCreateView(ManagerRequiredMixin, CreateView):
    """Crear equipo (solo managers)"""

    model = Team
    form_class = TeamForm
    template_name = "accounts/team_form.html"
    success_url = reverse_lazy("accounts:team_list")

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
        if team.manager != request.user and not (
            request.user.is_staff or request.user.is_superuser
        ):
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


class PlayerRegistrationView(ManagerRequiredMixin, CreateView):
    """Vista para que managers registren jugadores"""

    model = Player
    form_class = PlayerRegistrationForm
    template_name = "accounts/player_register.html"
    success_url = reverse_lazy("accounts:player_list")

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


class ParentPlayerRegistrationView(LoginRequiredMixin, CreateView):
    """Vista para que padres registren jugadores"""

    model = Player
    form_class = ParentPlayerRegistrationForm
    template_name = "accounts/parent_player_register.html"
    success_url = reverse_lazy("accounts:panel")

    def dispatch(self, request, *args, **kwargs):
        # Verificar que el usuario sea padre
        if not hasattr(request.user, "profile") or not request.user.profile.is_parent:
            messages.error(
                request, "Solo los padres/acudientes pueden registrar jugadores."
            )
            return redirect("accounts:panel")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["parent"] = self.request.user
        return kwargs

    def form_valid(self, form):
        # El formulario ya creó el usuario, player y la relación
        player = form.save()
        player_name = player.user.get_full_name() or player.user.username
        messages.success(
            self.request,
            f"¡Jugador {player_name} registrado exitosamente! El perfil está listo para usar.",
            extra_tags="player_registered",
        )
        return redirect("accounts:panel")


class PlayerUpdateView(LoginRequiredMixin, UpdateView):
    """Actualizar información de jugador"""

    model = Player
    form_class = PlayerUpdateForm
    template_name = "accounts/player_edit.html"  # Default, se puede sobrescribir en get_template_names

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
            return redirect("accounts:player_detail", pk=player.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pasar información del usuario para que el formulario sepa si es padre
        kwargs["user"] = self.request.user
        return kwargs

    def get_template_names(self):
        """Usar diferentes templates según si es padre o manager/admin"""
        player = self.get_object()
        user = self.request.user

        # Verificar si existe la relación PlayerParent (independientemente de si el usuario es staff)
        # Esto permite que incluso staff que son padres vean el template de hijo
        is_parent = PlayerParent.objects.filter(
            parent=user, player=player
        ).exists()

        # Si el usuario es padre del jugador (existe la relación PlayerParent),
        # usar el template de hijo, independientemente de si es staff
        if is_parent:
            return ["accounts/player_edit_hijo.html"]
        else:
            return ["accounts/player_edit.html"]

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
        # Indicar si es una petición AJAX para devolver solo el contenido del formulario
        context["is_ajax"] = (
            self.request.headers.get("X-Requested-With") == "XMLHttpRequest"
        )
        return context

    def get_success_url(self):
        # Si es padre, redirigir al dashboard después de editar
        if (
            hasattr(self.request.user, "profile")
            and self.request.user.profile.is_parent
        ):
            from .models import PlayerParent

            if PlayerParent.objects.filter(
                parent=self.request.user, player=self.object
            ).exists():
                return reverse_lazy("accounts:panel")
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
        else:
            form.save()

        messages.success(
            self.request, "Información del jugador actualizada exitosamente."
        )

        # Si es una petición AJAX, devolver una respuesta JSON
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            from django.http import JsonResponse

            return JsonResponse(
                {
                    "success": True,
                    "message": "Jugador actualizado exitosamente",
                    "redirect_url": str(self.get_success_url()),
                }
            )

        return redirect(self.get_success_url())


class UserListView(UserPassesTestMixin, LoginRequiredMixin, ListView):
    """Lista de usuarios (solo staff)"""

    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "users"
    paginate_by = 20

    def test_func(self):
        """Solo staff puede ver la lista de usuarios"""
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_queryset(self):
        queryset = User.objects.select_related("profile").all()

        # Filtros de búsqueda
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
            )

        # Filtro por tipo de usuario
        user_type = self.request.GET.get("user_type")
        if user_type:
            queryset = queryset.filter(profile__user_type=user_type)

        # Filtro por estado activo
        is_active_filter = self.request.GET.get("is_active")
        if is_active_filter == "true":
            queryset = queryset.filter(is_active=True)
        elif is_active_filter == "false":
            queryset = queryset.filter(is_active=False)

        return queryset.order_by("-date_joined")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Opciones de tipo de usuario para el filtro
        context["user_type_choices"] = UserProfile.USER_TYPE_CHOICES

        # Filtros actuales para mantener en el formulario
        context["current_filters"] = {
            "search": self.request.GET.get("search", ""),
            "user_type": self.request.GET.get("user_type", ""),
            "is_active": self.request.GET.get("is_active", ""),
        }

        # Marcar la sección activa en el sidebar
        context["active_section"] = "users"
        context["active_subsection"] = "user_list"

        return context


# Vista para manejar el perfil (redirige según el tipo de usuario)
@login_required
def profile_view(request):
    """Vista de perfil que redirige al panel"""
    return redirect("accounts:panel")


class PanelEventDetailView(UserDashboardView):
    """Vista para mostrar el detalle del evento en el panel con checkout"""

    def get_context_data(self, **kwargs):
        # Obtener el contexto base del dashboard
        context = super().get_context_data(**kwargs)

        user = self.request.user
        event_id = self.kwargs.get("pk")

        try:
            from apps.events.models import Event, EventAttendance

            # Obtener el evento
            from apps.locations.models import HotelRoom

            event = Event.objects.select_related(
                "category", "event_type", "country", "state", "city",
                "hotel", "hotel__city", "hotel__state", "hotel__country",
                "primary_site"
            ).prefetch_related(
                "divisions",
                "hotel__rooms",
                "hotel__images",
                "hotel__amenities"
            ).get(pk=event_id)

            # Obtener habitaciones disponibles del hotel
            if event.hotel:
                available_rooms = HotelRoom.objects.filter(
                    hotel=event.hotel,
                    is_available=True
                ).select_related("hotel").order_by("room_type", "price_per_night")
                context["available_rooms"] = available_rooms
            else:
                context["available_rooms"] = []

            context["event"] = event
            context["active_tab"] = "detalle-eventos"
            context["event_detail_template"] = "accounts/panel_tabs/detalle_evento.html"

            # Obtener los hijos/jugadores del usuario
            children = []
            if hasattr(user, "profile") and user.profile.is_parent:
                # Obtener jugadores relacionados a través de PlayerParent
                from .models import PlayerParent

                player_parents = PlayerParent.objects.filter(
                    parent=user
                ).select_related("player", "player__user", "player__user__profile")

                children = [pp.player for pp in player_parents if pp.player.is_active]

            context["children"] = children

            # Verificar si ya hay registros para este evento
            registered_players = []
            for child in children:
                try:
                    attendance = EventAttendance.objects.get(
                        event=event, user=child.user
                    )
                    registered_players.append(child.pk)
                except EventAttendance.DoesNotExist:
                    pass

            context["registered_players"] = registered_players

        except Event.DoesNotExist:
            context["event"] = None
            messages.error(self.request, "Event not found.")
        except ImportError:
            context["event"] = None
            messages.error(self.request, "Events app is not available.")

        return context


@login_required
@require_POST
def register_children_to_event(request, pk):
    """Vista para registrar hijos/jugadores a un evento"""
    try:
        from apps.events.models import Event, EventAttendance

        event = get_object_or_404(Event, pk=pk)
        user = request.user

        # Verificar que el usuario es padre
        if not (hasattr(user, "profile") and user.profile.is_parent):
            messages.error(request, "You must be a parent to register children to events.")
            return redirect("accounts:panel")

        # Obtener los IDs de los jugadores seleccionados
        player_ids = request.POST.getlist("players")

        if not player_ids:
            messages.warning(request, "Please select at least one child/player to register.")
            return redirect("accounts:panel_event_detail", pk=pk)

        # Obtener los jugadores relacionados al usuario
        from .models import PlayerParent, Player

        player_parents = PlayerParent.objects.filter(
            parent=user, player_id__in=player_ids
        ).select_related("player")

        registered_count = 0
        for player_parent in player_parents:
            player = player_parent.player
            # Crear o actualizar el registro de asistencia
            attendance, created = EventAttendance.objects.get_or_create(
                event=event, user=player.user, defaults={"status": "pending"}
            )
            if created:
                registered_count += 1
            else:
                # Si ya existe, actualizar el estado a pending si estaba cancelado
                if attendance.status == "cancelled":
                    attendance.status = "pending"
                    attendance.save()
                    registered_count += 1

        if registered_count > 0:
            messages.success(
                request,
                f"Successfully registered {registered_count} child/children to the event.",
            )
        else:
            messages.info(request, "The selected children are already registered to this event.")

        return redirect("accounts:panel_event_detail", pk=pk)

    except ImportError:
        messages.error(request, "Events app is not available.")
        return redirect("accounts:panel")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect("accounts:panel")
