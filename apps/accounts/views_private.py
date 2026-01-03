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
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.utils import timezone, translation
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)
from django.db import transaction
from decimal import Decimal, ROUND_HALF_UP
import json

from apps.core.mixins import ManagerRequiredMixin

from .forms import (
    ParentPlayerRegistrationForm,
    PlayerRegistrationForm,
    PlayerUpdateForm,
    TeamForm,
    UserProfileForm,
    UserUpdateForm,
)
from .models import DashboardContent, MarqueeMessage, Player, PlayerParent, Team, UserProfile, StripeEventCheckout


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

        # Obtener mensajes activos del marquee
        marquee_messages = MarqueeMessage.objects.filter(is_active=True).order_by("order", "-created_at")
        context["marquee_messages"] = marquee_messages

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
            from django.core.paginator import Paginator

            # Reservas para el dashboard (últimas 5)
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

            # Reservas para la tab de reservas (con paginación)
            reservations_queryset = (
                HotelReservation.objects.filter(user=user)
                .select_related("hotel", "room")
                .order_by("-created_at")
            )

            # Filtro por estado si viene en GET
            status_filter = self.request.GET.get("status")
            if status_filter:
                reservations_queryset = reservations_queryset.filter(status=status_filter)

            # Paginación
            paginator = Paginator(reservations_queryset, 10)  # 10 reservas por página
            page_number = self.request.GET.get("page", 1)
            reservations_page = paginator.get_page(page_number)

            context["reservations"] = reservations_page
            context["is_paginated"] = reservations_page.has_other_pages()
            context["page_obj"] = reservations_page
            context["status_choices"] = HotelReservation.RESERVATION_STATUS_CHOICES
        except Exception:
            context["user_reservations"] = []
            context["total_reservations"] = 0
            context["pending_reservations"] = 0
            context["reservations"] = []
            context["is_paginated"] = False
            context["status_choices"] = []

        # Obtener o crear wallet del usuario
        try:
            from .models import UserWallet, WalletTransaction

            wallet, created = UserWallet.objects.get_or_create(user=user)
            context["wallet"] = wallet
            # Obtener últimas transacciones
            context["wallet_transactions"] = (
                WalletTransaction.objects.filter(wallet=wallet)
                .order_by("-created_at")[:10]
            )
        except Exception:
            context["wallet"] = None
            context["wallet_transactions"] = []

        return context


class ProfileView(LoginRequiredMixin, TemplateView):
    """Vista principal de perfil con sidebar"""

    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        from .forms import (
            BillingAddressForm,
            CustomPasswordChangeForm,
            NotificationPreferencesForm,
            UserProfileForm,
            UserProfileUpdateForm,
        )

        context = super().get_context_data(**kwargs)
        context["profile"] = self.request.user.profile
        context["user"] = self.request.user
        # Determinar qué sección mostrar (por defecto 'profile')
        context["active_section"] = self.request.GET.get("section", "profile")

        # Pasar formularios según la sección activa
        if context["active_section"] == "profile":
            context["profile_form"] = UserProfileForm(instance=self.request.user.profile)
            context["user_form"] = UserProfileUpdateForm(instance=self.request.user)
        elif context["active_section"] == "billing":
            context["billing_form"] = BillingAddressForm(instance=self.request.user.profile)
        elif context["active_section"] == "security":
            context["password_form"] = CustomPasswordChangeForm(user=self.request.user)
        elif context["active_section"] == "notifications":
            # Cargar preferencias desde el perfil o usar valores por defecto
            profile = self.request.user.profile
            initial_data = {
                "email_notifications": getattr(profile, "email_notifications", True),
                "event_notifications": getattr(profile, "event_notifications", True),
                "reservation_notifications": getattr(profile, "reservation_notifications", True),
                "marketing_notifications": getattr(profile, "marketing_notifications", False),
            }
            context["notification_form"] = NotificationPreferencesForm(initial=initial_data)

        return context

    def post(self, request, *args, **kwargs):
        """Manejar POST de diferentes secciones"""
        from .forms import (
            BillingAddressForm,
            CustomPasswordChangeForm,
            NotificationPreferencesForm,
            UserProfileForm,
            UserProfileUpdateForm,
        )

        section = request.GET.get("section", "profile")

        if section == "profile":
            profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
            user_form = UserProfileUpdateForm(request.POST, instance=request.user)

            if profile_form.is_valid() and user_form.is_valid():
                profile = profile_form.save()
                user_form.save()

                # Si se actualizó el idioma preferido, guardarlo en la sesión
                if "preferred_language" in profile_form.cleaned_data:
                    preferred_language = profile_form.cleaned_data["preferred_language"] or "en"
                    language_key = getattr(translation, "LANGUAGE_SESSION_KEY", "_language")
                    request.session[language_key] = preferred_language
                    request.session["user_selected_language"] = True
                    request.session.modified = True
                    translation.activate(preferred_language)

                messages.success(request, _("Profile updated successfully."))
                return redirect("accounts:profile?section=profile")
        elif section == "billing":
            billing_form = BillingAddressForm(request.POST, instance=request.user.profile)
            if billing_form.is_valid():
                billing_form.save()
                messages.success(request, _("Billing address updated successfully."))
                return redirect("accounts:profile?section=billing")
        elif section == "security":
            password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, _("Password changed successfully."))
                return redirect("accounts:profile?section=security")
        elif section == "notifications":
            notification_form = NotificationPreferencesForm(request.POST)
            if notification_form.is_valid():
                # Guardar preferencias en el perfil (necesitarías agregar estos campos al modelo)
                # Por ahora solo mostramos mensaje de éxito
                messages.success(request, _("Notification preferences saved successfully."))
                return redirect("accounts:profile?section=notifications")

        # Si hay errores, volver a mostrar el formulario con errores
        context = self.get_context_data(**kwargs)
        if section == "profile":
            context["profile_form"] = profile_form
            context["user_form"] = user_form
        elif section == "billing":
            context["billing_form"] = billing_form
        elif section == "security":
            context["password_form"] = password_form
        elif section == "notifications":
            context["notification_form"] = notification_form

        return self.render_to_response(context)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para actualizar perfil"""

    model = UserProfile
    form_class = UserProfileForm
    template_name = "accounts/profile_edit.html"
    success_url = reverse_lazy("accounts:profile")

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

        messages.success(self.request, _("Profile updated successfully."))
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
        messages.success(self.request, _("Information updated successfully."))
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
        messages.success(self.request, _("Team created successfully."))
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
            messages.error(request, _("You do not have permission to edit this team."))
            return redirect("accounts:team_list")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("accounts:team_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, _("Team updated successfully."))
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
            self.request, _("Player %(name)s registered successfully.") % {"name": player_name}
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
                request, _("Only parents/guardians can register players.")
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
            _("Player %(name)s registered successfully! The profile is ready to use.") % {"name": player_name},
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
            messages.error(request, _("You do not have permission to edit this player."))
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
            self.request, _("Player information updated successfully.")
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
                ).select_related("hotel").prefetch_related("amenities").order_by("room_type", "price_per_night")
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
            messages.error(self.request, _("Event not found."))
        except ImportError:
            context["event"] = None
            messages.error(self.request, _("Events app is not available."))

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
            messages.error(request, _("You must be a parent to register children to events."))
            return redirect("accounts:panel")

        # Obtener los IDs de los jugadores seleccionados
        player_ids = request.POST.getlist("players")

        if not player_ids:
            messages.warning(request, _("Please select at least one child/player to register."))
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
                _("Successfully registered %(count)d child/children to the event.") % {"count": registered_count},
            )
        else:
            messages.info(request, _("The selected children are already registered to this event."))

        return redirect("accounts:panel_event_detail", pk=pk)

    except ImportError:
        messages.error(request, _("Events app is not available."))
        return redirect("accounts:panel")
    except Exception as e:
        messages.error(request, _("An error occurred: %(error)s") % {"error": str(e)})
        return redirect("accounts:panel")


def _money_to_cents(amount: Decimal) -> int:
    if amount is None:
        amount = Decimal("0.00")
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))
    quantized = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int((quantized * 100).to_integral_value(rounding=ROUND_HALF_UP))


def _decimal(value, default="0.00") -> Decimal:
    try:
        if value is None:
            return Decimal(default)
        return Decimal(str(value))
    except Exception:
        return Decimal(default)


def _compute_hotel_amount_from_cart(cart: dict) -> dict:
    """
    Compute hotel totals from session cart using server-side room/service data.
    Taxes (IVA 16% + ISH 5%) are applied to room base (incl. extra guests), mirroring the UI.
    """
    from apps.locations.models import HotelRoom, HotelService
    from datetime import datetime

    room_base = Decimal("0.00")
    services_total = Decimal("0.00")

    for _, item_data in (cart or {}).items():
        if item_data.get("type") != "room":
            continue

        try:
            room = HotelRoom.objects.get(id=item_data.get("room_id"))
        except HotelRoom.DoesNotExist:
            continue

        try:
            check_in = datetime.strptime(item_data.get("check_in"), "%Y-%m-%d").date()
            check_out = datetime.strptime(item_data.get("check_out"), "%Y-%m-%d").date()
        except Exception:
            continue

        nights = (check_out - check_in).days
        if nights <= 0:
            continue

        guests = int(item_data.get("guests", 1) or 1)
        includes = int(room.price_includes_guests or 1)
        extra_guests = max(0, guests - includes)

        per_night_total = room.price_per_night + (room.additional_guest_price or Decimal("0.00")) * extra_guests
        item_room_base = per_night_total * nights
        room_base += item_room_base

        for service_data in item_data.get("services", []) or []:
            try:
                service = HotelService.objects.get(
                    id=service_data.get("service_id"),
                    hotel=room.hotel,
                    is_active=True,
                )
            except HotelService.DoesNotExist:
                continue

            quantity = int(service_data.get("quantity", 1) or 1)
            price = service.price * quantity
            if service.is_per_person:
                price = price * guests
            if service.is_per_night:
                price = price * nights
            services_total += price

    iva = room_base * Decimal("0.16")
    ish = room_base * Decimal("0.05")
    total = room_base + iva + ish + services_total

    return {
        "room_base": room_base,
        "services_total": services_total,
        "iva": iva,
        "ish": ish,
        "total": total,
    }


def _plan_months_until_deadline(payment_deadline):
    """
    Matches the frontend: inclusive months from current month through deadline month.
    If no deadline or invalid, returns 1.
    """
    try:
        if not payment_deadline:
            return 1
        now = timezone.localdate()
        months = (payment_deadline.year - now.year) * 12 + (payment_deadline.month - now.month) + 1
        if not months or months < 1:
            months = 1
        return int(months)
    except Exception:
        return 1


@login_required
@require_POST
def create_stripe_event_checkout_session(request, pk):
    if not settings.STRIPE_SECRET_KEY:
        return JsonResponse(
            {"success": False, "error": _("Stripe is not configured (STRIPE_SECRET_KEY).")},
            status=500,
        )

    try:
        import stripe  # type: ignore
    except Exception:
        return JsonResponse({"success": False, "error": _("Stripe SDK is not installed.")}, status=500)

    from apps.events.models import Event

    event = get_object_or_404(Event, pk=pk)
    user = request.user

    if not (hasattr(user, "profile") and user.profile.is_parent):
        return JsonResponse({"success": False, "error": _("Only parents can pay for registrations.")}, status=403)

    player_ids = request.POST.getlist("players")
    if not player_ids:
        return JsonResponse({"success": False, "error": _("Select at least 1 player.")}, status=400)

    player_parents = PlayerParent.objects.filter(
        parent=user, player_id__in=player_ids
    ).select_related("player", "player__user")
    valid_players = [pp.player for pp in player_parents if getattr(pp.player, "is_active", True)]
    if len(valid_players) != len(player_ids):
        return JsonResponse(
            {"success": False, "error": _("There are invalid players or players that do not belong to the user.")},
            status=400,
        )

    payment_mode = request.POST.get("payment_mode", "plan")
    if payment_mode not in ("plan", "now"):
        payment_mode = "plan"

    entry_fee = _decimal(getattr(event, "default_entry_fee", None), default="0.00")
    players_count = int(len(valid_players))
    players_total = (entry_fee * Decimal(str(players_count))).quantize(Decimal("0.01"))

    cart = request.session.get("hotel_cart", {}) or {}
    hotel_breakdown = _compute_hotel_amount_from_cart(cart) if cart else {
        "room_base": Decimal("0.00"),
        "services_total": Decimal("0.00"),
        "iva": Decimal("0.00"),
        "ish": Decimal("0.00"),
        "total": Decimal("0.00"),
    }
    hotel_total = hotel_breakdown["total"]

    # Pay now discount only applies if a hotel stay is included
    discount_percent = 5 if (payment_mode == "now" and hotel_total > 0) else 0
    discount_multiplier = Decimal("1.00") - (Decimal(str(discount_percent)) / Decimal("100"))

    no_show_fee = Decimal("1000.00") if (players_count > 0 and not cart) else Decimal("0.00")

    subtotal = (players_total + hotel_total + no_show_fee).quantize(Decimal("0.01"))
    total = (subtotal * discount_multiplier).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    currency = (getattr(settings, "STRIPE_CURRENCY", "usd") or "usd").lower()

    def scale(amount: Decimal) -> Decimal:
        return (amount * discount_multiplier).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Build Stripe line items differently for pay-now vs plan:
    # - now: one-time payment line items
    # - plan: recurring monthly subscription line item (card saved + auto charges)
    line_items = []
    plan_months = _plan_months_until_deadline(getattr(event, "payment_deadline", None))
    plan_monthly_amount = Decimal("0.00")

    if payment_mode == "plan":
        # Plan doesn't apply discount. Monthly amount is approximate = subtotal / months.
        plan_monthly_amount = (subtotal / Decimal(str(plan_months))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if plan_monthly_amount <= 0:
            return JsonResponse({"success": False, "error": _("There is nothing to charge.")}, status=400)

        line_items = [
            {
                "price_data": {
                    "currency": currency,
                    "product_data": {
                        "name": f"Payment plan ({plan_months} month{'s' if plan_months != 1 else ''}) - {event.title}",
                        "description": (
                            f"First charge today, then {max(0, plan_months - 1)} monthly charge(s). "
                            f"Ends automatically."
                        ),
                    },
                    "unit_amount": _money_to_cents(plan_monthly_amount),
                    "recurring": {"interval": "month"},
                },
                "quantity": 1,
            }
        ]
    else:
        if players_total > 0 and players_count > 0:
            line_items.append(
                {
                    "price_data": {
                        "currency": currency,
                        "product_data": {"name": f"Event registration - {event.title}"},
                        "unit_amount": _money_to_cents(scale(entry_fee)),
                    },
                    "quantity": players_count,
                }
            )

        if hotel_total > 0:
            hotel_name = ""
            try:
                hotel_name = event.hotel.hotel_name if event.hotel else ""
            except Exception:
                hotel_name = ""
            line_items.append(
                {
                    "price_data": {
                        "currency": currency,
                        "product_data": {"name": f"Hotel stay{(' - ' + hotel_name) if hotel_name else ''}"},
                        "unit_amount": _money_to_cents(scale(hotel_total)),
                    },
                    "quantity": 1,
                }
            )

        if no_show_fee > 0:
            line_items.append(
                {
                    "price_data": {
                        "currency": currency,
                        "product_data": {"name": "Hotel buy out fee"},
                        "unit_amount": _money_to_cents(scale(no_show_fee)),
                    },
                    "quantity": 1,
                }
            )

        if not line_items:
            return JsonResponse({"success": False, "error": _("There is nothing to charge.")}, status=400)

    stripe.api_key = settings.STRIPE_SECRET_KEY
    stripe_account = event.stripe_payment_profile if getattr(event, "stripe_payment_profile", None) else None

    success_url = request.build_absolute_uri(
        reverse("accounts:stripe_event_checkout_success", kwargs={"pk": event.pk})
    ) + "?session_id={CHECKOUT_SESSION_ID}"
    cancel_url = request.build_absolute_uri(
        reverse("accounts:stripe_event_checkout_cancel", kwargs={"pk": event.pk})
    )

    session_params = {
        "mode": "subscription" if payment_mode == "plan" else "payment",
        "line_items": line_items,
        "success_url": success_url,
        "cancel_url": cancel_url,
        "customer_email": user.email or None,
        "metadata": {
            "event_id": str(event.pk),
            "user_id": str(user.pk),
            "payment_mode": payment_mode,
            "discount_percent": str(discount_percent),
            "player_ids": ",".join([str(p.pk) for p in valid_players]),
            "plan_months": str(plan_months),
        },
        "stripe_account": stripe_account,
    }
    # For payment plans, only allow card payments (Stripe "card" includes credit/debit cards).
    if payment_mode == "plan":
        session_params["payment_method_types"] = ["card"]
    session = stripe.checkout.Session.create(**session_params)

    StripeEventCheckout.objects.create(
        user=user,
        event=event,
        stripe_session_id=session.id,
        currency=currency,
        payment_mode=payment_mode,
        discount_percent=discount_percent,
        player_ids=[int(p.pk) for p in valid_players],
        hotel_cart_snapshot=cart,
        breakdown={
            "players_total": str(players_total),
            "hotel_room_base": str(hotel_breakdown["room_base"]),
            "hotel_services_total": str(hotel_breakdown["services_total"]),
            "hotel_iva": str(hotel_breakdown["iva"]),
            "hotel_ish": str(hotel_breakdown["ish"]),
            "hotel_total": str(hotel_total),
            "no_show_fee": str(no_show_fee),
            "subtotal": str(subtotal),
            "discount_percent": discount_percent,
            "total": str(total),
        },
        amount_total=total,
        plan_months=plan_months,
        plan_monthly_amount=plan_monthly_amount,
        status="created",
    )

    return JsonResponse({"success": True, "checkout_url": session.url, "session_id": session.id})


def _finalize_stripe_event_checkout(checkout: StripeEventCheckout) -> None:
    """Idempotent finalize: confirm event attendance + create hotel reservations."""
    from apps.events.models import EventAttendance
    from apps.locations.models import (
        HotelReservation,
        HotelReservationService,
        HotelRoom,
        HotelService,
    )
    from datetime import datetime

    with transaction.atomic():
        checkout.refresh_from_db()
        if checkout.status == "paid":
            return

        user = checkout.user
        event = checkout.event

        # Confirm event attendance
        player_ids = checkout.player_ids or []
        player_parents = PlayerParent.objects.filter(
            parent=user, player_id__in=player_ids
        ).select_related("player", "player__user")

        for pp in player_parents:
            player_user = pp.player.user
            attendance, _ = EventAttendance.objects.get_or_create(
                event=event, user=player_user, defaults={"status": "confirmed"}
            )
            if attendance.status != "confirmed":
                attendance.status = "confirmed"
            attendance.notes = (attendance.notes or "") + f"\nPaid via Stripe session {checkout.stripe_session_id}"
            attendance.save()

        # Create hotel reservations from snapshot
        cart = checkout.hotel_cart_snapshot or {}
        for _, item_data in cart.items():
            if item_data.get("type") != "room":
                continue

            try:
                room = HotelRoom.objects.get(id=item_data.get("room_id"))
                check_in = datetime.strptime(item_data.get("check_in"), "%Y-%m-%d").date()
                check_out = datetime.strptime(item_data.get("check_out"), "%Y-%m-%d").date()
            except Exception:
                continue

            overlapping = room.reservations.filter(
                check_in__lt=check_out,
                check_out__gt=check_in,
                status__in=["pending", "confirmed", "checked_in"],
            ).exists()
            if overlapping:
                continue

            reservation = HotelReservation.objects.create(
                hotel=room.hotel,
                room=room,
                user=user,
                guest_name=user.get_full_name() or user.username,
                guest_email=user.email,
                guest_phone=getattr(getattr(user, "profile", None), "phone", "") or "",
                number_of_guests=int(item_data.get("guests", 1) or 1),
                check_in=check_in,
                check_out=check_out,
                status="confirmed",
                notes=f"Reserva pagada vía Stripe session {checkout.stripe_session_id}",
            )

            for service_data in item_data.get("services", []) or []:
                try:
                    service = HotelService.objects.get(
                        id=service_data.get("service_id"),
                        hotel=room.hotel,
                        is_active=True,
                    )
                    HotelReservationService.objects.create(
                        reservation=reservation,
                        service=service,
                        quantity=int(service_data.get("quantity", 1) or 1),
                    )
                except HotelService.DoesNotExist:
                    pass

            reservation.total_amount = reservation.calculate_total()
            reservation.save()

        checkout.status = "paid"
        checkout.paid_at = timezone.now()
        checkout.save(update_fields=["status", "paid_at", "updated_at"])


def _ensure_plan_subscription_schedule(event, subscription_id: str, months: int):
    """
    Ensure a SubscriptionSchedule exists so the plan charges exactly N months then stops.
    Uses the current subscription's price and creates a schedule with iterations=months.
    """
    if not subscription_id or not months or months < 1:
        return ""

    # The first charge happens today when the subscription is created via Checkout.
    # A schedule created from an existing subscription takes over for future billing periods,
    # so we only need to schedule the remaining (months - 1) charges.
    remaining_months = max(0, int(months) - 1)
    if remaining_months <= 0:
        return ""

    if not settings.STRIPE_SECRET_KEY:
        return ""

    try:
        import stripe  # type: ignore
        stripe.api_key = settings.STRIPE_SECRET_KEY
    except Exception:
        return ""

    stripe_account = event.stripe_payment_profile if getattr(event, "stripe_payment_profile", None) else None

    try:
        sub = stripe.Subscription.retrieve(subscription_id, stripe_account=stripe_account)
        items = (sub.get("items", {}) or {}).get("data", []) or []
        if not items:
            return ""
        price_id = (items[0].get("price") or {}).get("id")
        if not price_id:
            return ""

        schedule = stripe.SubscriptionSchedule.create(
            from_subscription=subscription_id,
            end_behavior="cancel",
            phases=[
                {
                    "items": [{"price": price_id, "quantity": 1}],
                    "iterations": int(remaining_months),
                }
            ],
            stripe_account=stripe_account,
        )
        return schedule.get("id", "") or ""
    except Exception:
        return ""


@login_required
def stripe_event_checkout_success(request, pk):
    session_id = request.GET.get("session_id")
    if not session_id:
        messages.error(request, _("Stripe did not return session_id."))
        return redirect("accounts:panel_event_detail", pk=pk)

    if not settings.STRIPE_SECRET_KEY:
        messages.error(request, _("Stripe is not configured."))
        return redirect("accounts:panel_event_detail", pk=pk)

    try:
        import stripe  # type: ignore
        stripe.api_key = settings.STRIPE_SECRET_KEY
    except Exception:
        messages.error(request, _("Stripe SDK is not installed."))
        return redirect("accounts:panel_event_detail", pk=pk)

    from apps.events.models import Event

    event = get_object_or_404(Event, pk=pk)
    stripe_account = event.stripe_payment_profile if getattr(event, "stripe_payment_profile", None) else None

    try:
        session = stripe.checkout.Session.retrieve(session_id, stripe_account=stripe_account)
    except Exception as e:
        messages.error(request, _("Could not verify payment: %(error)s") % {"error": str(e)})
        return redirect("accounts:panel_event_detail", pk=pk)

    if getattr(session, "payment_status", "") != "paid":
        messages.warning(request, _("Payment is not yet confirmed."))
        return redirect("accounts:panel_event_detail", pk=pk)

    try:
        checkout = StripeEventCheckout.objects.get(stripe_session_id=session_id)
    except StripeEventCheckout.DoesNotExist:
        messages.error(request, _("Checkout not found in the system."))
        return redirect("accounts:panel_event_detail", pk=pk)

    # Store subscription id (plan payments)
    subscription_id = getattr(session, "subscription", "") or ""
    if subscription_id and not checkout.stripe_subscription_id:
        checkout.stripe_subscription_id = str(subscription_id)

    # If it's a plan, create schedule to stop after N months
    if checkout.payment_mode == "plan" and subscription_id:
        schedule_id = _ensure_plan_subscription_schedule(checkout.event, str(subscription_id), int(checkout.plan_months or 1))
        if schedule_id and not checkout.stripe_subscription_schedule_id:
            checkout.stripe_subscription_schedule_id = schedule_id

    checkout.save(update_fields=["stripe_subscription_id", "stripe_subscription_schedule_id", "updated_at"])

    _finalize_stripe_event_checkout(checkout)

    # Clear live session cart (UX)
    request.session["hotel_cart"] = {}
    request.session.modified = True

    messages.success(request, _("Payment completed. Registration confirmed."))
    return redirect("accounts:panel_event_detail", pk=pk)


@login_required
def stripe_event_checkout_cancel(request, pk):
    messages.info(request, _("Payment cancelled."))
    return redirect("accounts:panel_event_detail", pk=pk)


@csrf_exempt
def stripe_webhook(request):
    if not settings.STRIPE_SECRET_KEY:
        return HttpResponse(status=500)

    try:
        import stripe  # type: ignore
        stripe.api_key = settings.STRIPE_SECRET_KEY
    except Exception:
        return HttpResponse(status=500)

    if not settings.STRIPE_WEBHOOK_SECRET:
        # If webhook secret is not configured, acknowledge but avoid processing.
        return HttpResponse(status=200)

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        evt = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except Exception:
        return HttpResponse(status=400)

    event_type = evt.get("type")
    obj = (evt.get("data", {}) or {}).get("object", {}) or {}

    if event_type == "checkout.session.completed":
        session_id = obj.get("id")
        if session_id:
            try:
                checkout = StripeEventCheckout.objects.get(stripe_session_id=session_id)
                # Persist subscription + schedule for plan
                subscription_id = obj.get("subscription") or ""
                if subscription_id and not checkout.stripe_subscription_id:
                    checkout.stripe_subscription_id = str(subscription_id)
                if checkout.payment_mode == "plan" and subscription_id and not checkout.stripe_subscription_schedule_id:
                    schedule_id = _ensure_plan_subscription_schedule(checkout.event, str(subscription_id), int(checkout.plan_months or 1))
                    if schedule_id:
                        checkout.stripe_subscription_schedule_id = schedule_id
                checkout.save(update_fields=["stripe_subscription_id", "stripe_subscription_schedule_id", "updated_at"])
                _finalize_stripe_event_checkout(checkout)
            except StripeEventCheckout.DoesNotExist:
                pass

    if event_type == "checkout.session.expired":
        session_id = obj.get("id")
        if session_id:
            StripeEventCheckout.objects.filter(
                stripe_session_id=session_id, status="created"
            ).update(status="expired")

    return HttpResponse(status=200)


@login_required
@require_POST
def wallet_add_funds(request):
    """Vista para agregar fondos a la wallet del usuario"""
    from .models import UserWallet
    from decimal import Decimal

    try:
        amount = Decimal(request.POST.get("amount", "0"))
        description = request.POST.get("description", "Depósito de fondos")

        if amount <= 0:
            messages.error(request, _("The amount must be greater than zero."))
            return redirect("accounts:panel")

        # Obtener o crear wallet
        wallet, created = UserWallet.objects.get_or_create(user=request.user)

        # Aquí iría la integración con el gateway de pagos
        # Por ahora, simulamos el depósito directamente
        # En producción, esto debería redirigir a un gateway de pago
        wallet.add_funds(amount, description)

        messages.success(
            request, _("$%(amount)s successfully added to your wallet.") % {"amount": amount}
        )
    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, _("Error processing deposit: %(error)s") % {"error": str(e)})

    return redirect("accounts:panel")
