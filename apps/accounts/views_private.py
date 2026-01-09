"""
Vistas privadas - Requieren autenticación
"""

import json
from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import models, transaction
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone, translation
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from apps.core.mixins import (
    ManagerRequiredMixin,
    OwnerOrStaffRequiredMixin,
    StaffRequiredMixin,
    SuperuserRequiredMixin,
)

from .forms import (
    ParentPlayerRegistrationForm,
    PlayerRegistrationForm,
    PlayerUpdateForm,
    TeamForm,
    UserProfileForm,
    UserUpdateForm,
)
from .models import (
    DashboardContent,
    MarqueeMessage,
    Order,
    Player,
    PlayerParent,
    StripeEventCheckout,
    Team,
    UserProfile,
)


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

        # Si es manager, obtener sus equipos (optimizado)
        if profile.is_team_manager:
            teams_qs = Team.objects.filter(manager=user).order_by("-created_at")
            context["total_teams"] = teams_qs.count()  # Contar antes del slice
            context["teams"] = teams_qs[:5]  # Solo los primeros 5

            players_qs = Player.objects.filter(team__manager=user).select_related(
                "user", "team", "user__profile"
            )
            context["total_players"] = players_qs.count()  # Contar antes del slice
            context["recent_players"] = players_qs.order_by("-created_at")[
                :5
            ]  # Solo los primeros 5

        # Si es padre, obtener sus jugadores (optimizado)
        if profile.is_parent:
            player_parents_qs = (
                PlayerParent.objects.filter(parent=user)
                .select_related(
                    "player",
                    "player__team",
                    "player__user",
                    "player__user__profile",
                    "player__user__profile__country",
                    "player__user__profile__state",
                    "player__user__profile__city",
                )
                .order_by("-created_at")
            )
            context["total_children"] = (
                player_parents_qs.count()
            )  # Contar antes de evaluar
            context["children"] = player_parents_qs  # QuerySet lazy
            context["recent_children"] = player_parents_qs[:5]  # Solo los primeros 5

        # Obtener banners activos del dashboard (siempre devolver al menos uno para el bucle)
        try:
            from .models import DashboardBanner

            banners = DashboardBanner.objects.filter(is_active=True).order_by(
                "order", "-created_at"
            )[
                :10
            ]  # Limitar a 10 banners
            # Si no hay banners, crear una lista vacía (el template mostrará el banner por defecto)
            context["dashboard_banners"] = list(banners) if banners.exists() else []
        except ImportError:
            context["dashboard_banners"] = []

        # Obtener eventos para la pestaña de eventos (optimizado - limitar a 20)
        try:
            from apps.events.models import Event

            now = timezone.now()
            # Obtener solo eventos publicados - limitar a 20 para mejor rendimiento
            context["upcoming_events"] = (
                Event.objects.filter(status="published")
                .select_related(
                    "category", "event_type", "city", "state", "primary_site"
                )
                .prefetch_related("divisions")
                .order_by("start_date")[:20]  # Reducido de 50 a 20 eventos
            )
        except ImportError:
            context["upcoming_events"] = []

        # Obtener contenido del dashboard configurado por el admin según el tipo de usuario
        user_type = profile.user_type
        dashboard_content = (
            DashboardContent.objects.filter(is_active=True)
            .filter(Q(user_type=user_type) | Q(user_type="all"))
            .order_by("order", "-created_at")[:20]  # Limitar a 20 contenidos
        )
        context["dashboard_content"] = dashboard_content

        # Obtener mensajes activos del marquee (limitar a 10)
        marquee_messages = MarqueeMessage.objects.filter(is_active=True).order_by(
            "order", "-created_at"
        )[
            :10
        ]  # Limitar a 10 mensajes[:10]  # Limitar a 10 mensajes
        context["marquee_messages"] = marquee_messages

        # Inicializar contadores de verificaciones pendientes
        context["pending_verifications"] = []
        context["pending_verifications_count"] = 0

        # Si es staff/admin, obtener todos los documentos pendientes (no solo de sus equipos)
        if user.is_staff or user.is_superuser:
            pending_qs = Player.objects.filter(
                age_verification_status="pending",
                age_verification_document__isnull=False,
            ).select_related("user", "team", "user__profile")
            context["pending_verifications"] = pending_qs.order_by("-updated_at")[:20]
            context["pending_verifications_count"] = (
                pending_qs.count()
            )  # Una sola consulta
        # Si es manager (pero no staff), obtener solo documentos de sus equipos
        elif profile.is_team_manager:
            pending_qs = Player.objects.filter(
                team__manager=user,
                age_verification_status="pending",
                age_verification_document__isnull=False,
            ).select_related("user", "team", "user__profile")
            context["pending_verifications"] = pending_qs.order_by("-updated_at")[:10]
            context["pending_verifications_count"] = (
                pending_qs.count()
            )  # Una sola consulta

        # Contexto adicional para los includes de los tabs
        # Formulario de equipo (para managers)
        if profile.is_team_manager:
            from .forms import TeamForm

            context["team_form"] = TeamForm()
            # Limitar equipos a los más recientes (lazy evaluation)
            context["all_teams"] = Team.objects.filter(manager=user).order_by(
                "-created_at"
            )[
                :100
            ]  # Limitar a 100 equipos más recientes

            # Limitar jugadores y usar prefetch para optimizar
            all_players_qs = (
                Player.objects.filter(team__manager=user)
                .select_related("user", "user__profile", "team")
                .order_by("-created_at")[:200]  # Limitar a 200 jugadores más recientes
            )

            # Anotar cada jugador con información sobre si es hijo del usuario actual (optimizado)
            if profile.is_parent:
                # Obtener IDs de jugadores que son hijos del usuario (una sola consulta)
                child_player_ids = set(
                    PlayerParent.objects.filter(parent=user).values_list(
                        "player_id", flat=True
                    )
                )
                # Evaluar el QuerySet una sola vez y agregar atributo is_child
                all_players_list = list(all_players_qs)
                for player in all_players_list:
                    player.is_child = player.pk in child_player_ids
                context["all_players"] = all_players_list
            else:
                # Si no es padre, ningún jugador es hijo - mantener como QuerySet lazy
                context["all_players"] = all_players_qs

        # Formulario de jugador (para managers)
        if profile.is_team_manager:
            from .forms import PlayerRegistrationForm

            context["player_form"] = PlayerRegistrationForm(manager=user)

        # Formulario de jugador para padres (optimizado)
        if profile.is_parent:
            from .forms import ParentPlayerRegistrationForm

            context["parent_player_form"] = ParentPlayerRegistrationForm(parent=user)
            # Limitar jugadores de padres para mejor rendimiento
            context["parent_players"] = (
                Player.objects.filter(parents__parent=user)
                .select_related(
                    "user",
                    "user__profile",
                    "user__profile__country",
                    "user__profile__state",
                    "user__profile__city",
                    "team",
                )
                .order_by("-created_at")[:100]  # Limitar a 100 jugadores más recientes
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

        # Obtener planes de pago y checkouts de Stripe para Plans & Payments
        try:
            from apps.events.models import Event

            # Planes activos: checkouts pagados o creados (para planes, mostrar si tienen subscription_id o están pagados)
            active_checkouts = (
                StripeEventCheckout.objects.filter(user=user)
                .select_related("event")
                .order_by("-created_at")
            )

            # Filtrar planes activos:
            # - Planes: deben estar pagados O tener subscription_id (aunque estén en "created")
            # - Pay Now: solo los pagados
            active_plans = []
            for checkout in active_checkouts:
                if checkout.payment_mode == "plan":
                    # Para planes, incluir si está pagado o tiene subscription_id (indica que se inició)
                    if checkout.status == "paid" or checkout.stripe_subscription_id:
                        active_plans.append(checkout)
                else:
                    # Para pay now, solo incluir si está pagado
                    if checkout.status == "paid":
                        active_plans.append(checkout)

            context["active_payment_plans"] = active_plans

            # Historial de pagos (todos los checkouts pagados)
            context["payment_history"] = (
                StripeEventCheckout.objects.filter(user=user, status="paid")
                .select_related("event")
                .order_by("-paid_at", "-created_at")[:50]
            )

            # Calcular próximos pagos de planes activos
            upcoming_payments = []
            now = timezone.now()

            for plan in active_plans:
                if (
                    plan.payment_mode == "plan"
                    and plan.plan_months
                    and plan.plan_months > 1
                ):
                    # Fecha base: usar paid_at si existe, sino created_at
                    base_date = plan.paid_at if plan.paid_at else plan.created_at
                    if not base_date:
                        continue

                    # Calcular cuántos pagos quedan
                    # El primer pago ya se hizo, así que quedan (plan_months - 1) pagos
                    remaining_payments = plan.plan_months - 1

                    # Calcular las fechas de los próximos pagos
                    # Usar cálculo manual de meses para evitar dependencia de dateutil
                    from calendar import monthrange
                    from datetime import date

                    # Convertir base_date a date si es datetime
                    if hasattr(base_date, "date"):
                        base_date_only = base_date.date()
                        is_aware = timezone.is_aware(base_date)
                    else:
                        base_date_only = base_date
                        is_aware = False

                    for payment_num in range(1, remaining_payments + 1):
                        # Calcular el mes y año objetivo
                        target_month = base_date_only.month + payment_num
                        target_year = base_date_only.year
                        while target_month > 12:
                            target_month -= 12
                            target_year += 1

                        # Ajustar el día si es necesario (evitar días inválidos como 31 de febrero)
                        day = base_date_only.day
                        last_day_of_month = monthrange(target_year, target_month)[1]
                        if day > last_day_of_month:
                            day = last_day_of_month

                        # Crear la fecha del próximo pago
                        from datetime import datetime

                        due_date_date = date(target_year, target_month, day)
                        # Convertir a datetime aware si el base_date era aware
                        if is_aware:
                            due_date = timezone.make_aware(
                                datetime.combine(due_date_date, datetime.min.time())
                            )
                        else:
                            due_date = datetime.combine(
                                due_date_date, datetime.min.time()
                            )

                        # Solo incluir pagos futuros
                        if due_date > now:
                            upcoming_payments.append(
                                {
                                    "checkout": plan,
                                    "event": plan.event,
                                    "due_date": due_date,
                                    "amount": plan.plan_monthly_amount,
                                    "payment_number": payment_num
                                    + 1,  # +1 porque el primer pago fue el 1
                                    "total_payments": plan.plan_months,
                                    "description": f"{plan.event.title} - Payment {payment_num + 1}/{plan.plan_months}",
                                }
                            )

            # Ordenar por fecha de vencimiento (más cercanos primero)
            upcoming_payments.sort(key=lambda x: x["due_date"])
            context["upcoming_payments"] = upcoming_payments[
                :20
            ]  # Limitar a los próximos 20

        except ImportError:
            context["active_payment_plans"] = []
            context["payment_history"] = []
            context["upcoming_payments"] = []

        # Calcular total del carrito (optimizado - evitar múltiples queries)
        from decimal import Decimal

        from apps.locations.models import Hotel, HotelRoom, HotelService

        cart_total = Decimal("0.00")
        if cart:
            # Obtener todos los IDs de habitaciones y servicios de una vez
            room_ids = [
                item_data.get("room_id")
                for item_data in cart.values()
                if item_data.get("type") == "room" and item_data.get("room_id")
            ]
            service_ids = [
                item_data.get("service_id")
                for item_data in cart.values()
                if item_data.get("type") == "service" and item_data.get("service_id")
            ]

            # Hacer una sola consulta para todas las habitaciones
            rooms_dict = (
                {
                    room.id: room
                    for room in HotelRoom.objects.filter(
                        id__in=room_ids
                    ).select_related("hotel")
                }
                if room_ids
                else {}
            )

            # Hacer una sola consulta para todos los servicios
            services_dict = (
                {
                    service.id: service
                    for service in HotelService.objects.filter(
                        id__in=service_ids
                    ).select_related("hotel")
                }
                if service_ids
                else {}
            )

        for item_id, item_data in cart.items():
            try:
                if item_data.get("type") == "room":
                    room = rooms_dict.get(item_data.get("room_id"))
                    if not room:
                        continue
                    nights = int(item_data.get("nights", 1))
                    guests = int(item_data.get("guests", 1))
                    room_total = room.price_per_night * nights
                    services_total = Decimal("0.00")
                    # Usar servicios del diccionario en lugar de consultas individuales
                    for service_data in item_data.get("services", []):
                        service_id = service_data.get("service_id")
                        service = services_dict.get(service_id)
                        if (
                            service
                            and service.hotel_id == room.hotel_id
                            and service.is_active
                        ):
                            quantity = int(service_data.get("quantity", 1))
                            service_price = service.price * quantity
                            if service.is_per_person:
                                service_price = service_price * guests
                            if service.is_per_night:
                                service_price = service_price * nights
                            services_total += service_price
                    cart_total += room_total + services_total
            except (ValueError, KeyError):
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
            from django.core.paginator import Paginator

            from apps.locations.models import HotelReservation

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
                reservations_queryset = reservations_queryset.filter(
                    status=status_filter
                )

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
            context["wallet_transactions"] = WalletTransaction.objects.filter(
                wallet=wallet
            ).order_by("-created_at")[:10]
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
            context["profile_form"] = UserProfileForm(
                instance=self.request.user.profile
            )
            context["user_form"] = UserProfileUpdateForm(instance=self.request.user)
        elif context["active_section"] == "billing":
            context["billing_form"] = BillingAddressForm(
                instance=self.request.user.profile
            )
        elif context["active_section"] == "security":
            context["password_form"] = CustomPasswordChangeForm(user=self.request.user)
        elif context["active_section"] == "notifications":
            # Cargar preferencias desde el perfil o usar valores por defecto
            profile = self.request.user.profile
            initial_data = {
                "email_notifications": getattr(profile, "email_notifications", True),
                "event_notifications": getattr(profile, "event_notifications", True),
                "reservation_notifications": getattr(
                    profile, "reservation_notifications", True
                ),
                "marketing_notifications": getattr(
                    profile, "marketing_notifications", False
                ),
            }
            context["notification_form"] = NotificationPreferencesForm(
                initial=initial_data
            )

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
            profile_form = UserProfileForm(
                request.POST, request.FILES, instance=request.user.profile
            )
            user_form = UserProfileUpdateForm(request.POST, instance=request.user)

            if profile_form.is_valid() and user_form.is_valid():
                profile = profile_form.save()
                user_form.save()

                # Si se actualizó el idioma preferido, guardarlo en la sesión
                if "preferred_language" in profile_form.cleaned_data:
                    preferred_language = (
                        profile_form.cleaned_data["preferred_language"] or "en"
                    )
                    language_key = getattr(
                        translation, "LANGUAGE_SESSION_KEY", "_language"
                    )
                    request.session[language_key] = preferred_language
                    request.session["user_selected_language"] = True
                    request.session.modified = True
                    translation.activate(preferred_language)

                messages.success(request, _("Profile updated successfully."))
                return redirect("accounts:profile?section=profile")
        elif section == "billing":
            billing_form = BillingAddressForm(
                request.POST, instance=request.user.profile
            )
            if billing_form.is_valid():
                billing_form.save()
                messages.success(request, _("Billing address updated successfully."))
                return redirect("accounts:profile?section=billing")
        elif section == "security":
            password_form = CustomPasswordChangeForm(
                user=request.user, data=request.POST
            )
            if password_form.is_valid():
                password_form.save()
                messages.success(request, _("Password changed successfully."))
                return redirect("accounts:profile?section=security")
        elif section == "notifications":
            notification_form = NotificationPreferencesForm(request.POST)
            if notification_form.is_valid():
                # Guardar preferencias en el perfil (necesitarías agregar estos campos al modelo)
                # Por ahora solo mostramos mensaje de éxito
                messages.success(
                    request, _("Notification preferences saved successfully.")
                )
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
    success_url = reverse_lazy("panel")

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


class TeamUpdateView(OwnerOrStaffRequiredMixin, UpdateView):
    """Actualizar equipo"""

    model = Team
    form_class = TeamForm
    template_name = "accounts/team_form.html"

    def get_success_url(self):
        return reverse_lazy("accounts:team_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, _("Team updated successfully."))
        return super().form_valid(form)


# ===== VISTAS DE JUGADORES =====


class PlayerListView(StaffRequiredMixin, ListView):
    """Lista de jugadores"""

    model = Player
    template_name = "accounts/player_list.html"
    context_object_name = "players"
    paginate_by = 20

    def get_queryset(self):
        queryset = Player.objects.filter(is_active=True).select_related(
            "user",
            "team",
            "user__profile",
            "user__profile__country",
            "user__profile__state",
            "user__profile__city",
        )

        # Si es manager, solo mostrar jugadores de sus equipos
        if (
            hasattr(self.request.user, "profile")
            and self.request.user.profile.is_team_manager
        ):
            queryset = queryset.filter(team__manager=self.request.user)

        # Búsqueda por nombre
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(user__username__icontains=search)
                | Q(user__email__icontains=search)
            )

        # Filtros
        country_filter = self.request.GET.get("country")
        state_filter = self.request.GET.get("state")
        city_filter = self.request.GET.get("city")
        division_filter = self.request.GET.get("division")
        is_active_filter = self.request.GET.get("is_active")

        if country_filter:
            queryset = queryset.filter(user__profile__country_id=country_filter)

        if state_filter:
            queryset = queryset.filter(user__profile__state_id=state_filter)

        if city_filter:
            queryset = queryset.filter(user__profile__city_id=city_filter)

        if division_filter:
            queryset = queryset.filter(division_id=division_filter)

        if is_active_filter:
            is_active = is_active_filter.lower() == "true"
            queryset = queryset.filter(is_active=is_active)

        return queryset.order_by("user__last_name", "user__first_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Sidebar (admin dashboard base.html)
        context["active_section"] = "players"
        context["active_subsection"] = "player_list"

        # Agregar site_settings para navbar y footer
        try:
            from .models import SiteSettings

            site_settings = SiteSettings.load()
            context["site_settings"] = site_settings
        except (ImportError, AttributeError):
            context["site_settings"] = None

        # Importar modelos de locations
        from apps.locations.models import City, Country, State

        # Agregar opciones para filtros
        context["countries"] = Country.objects.filter(is_active=True).order_by("name")
        context["states"] = State.objects.filter(is_active=True).order_by("name")
        context["cities"] = City.objects.filter(is_active=True).order_by("name")

        # Divisiones desde el modelo Player
        from apps.events.models import Division
        context["divisions"] = Division.objects.filter(is_active=True).order_by('name')

        # Guardar filtros actuales para mantenerlos en la paginación
        context["current_filters"] = {
            "search": self.request.GET.get("search", ""),
            "country": self.request.GET.get("country", ""),
            "state": self.request.GET.get("state", ""),
            "city": self.request.GET.get("city", ""),
            "division": self.request.GET.get("division", ""),
            "is_active": self.request.GET.get("is_active", ""),
        }

        return context


class PlayerDetailView(LoginRequiredMixin, DetailView):
    """Detalle de jugador"""

    model = Player
    template_name = "accounts/player_detail.html"
    context_object_name = "player"

    def dispatch(self, request, *args, **kwargs):
        """Verificar permisos antes de mostrar el detalle del jugador"""
        if not request.user.is_authenticated:
            return redirect("accounts:login")

        player = self.get_object()
        user = request.user

        # Verificar permisos
        is_staff = user.is_staff or user.is_superuser
        is_manager = player.team and player.team.manager == user
        is_parent = PlayerParent.objects.filter(parent=user, player=player).exists()
        is_owner = player.user == user

        if not (is_staff or is_manager or is_parent or is_owner):
            from django.core.exceptions import PermissionDenied

            raise PermissionDenied(_("No tienes permisos para ver este jugador."))

        return super().dispatch(request, *args, **kwargs)


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
            self.request,
            _("Player %(name)s registered successfully.") % {"name": player_name},
        )
        return redirect("accounts:player_list")


class ParentPlayerRegistrationView(LoginRequiredMixin, CreateView):
    """Vista para que padres registren jugadores"""

    model = Player
    form_class = ParentPlayerRegistrationForm
    template_name = "accounts/parent_player_register.html"
    success_url = reverse_lazy("panel")

    def dispatch(self, request, *args, **kwargs):
        # Verificar que el usuario sea padre
        if not hasattr(request.user, "profile") or not request.user.profile.is_parent:
            messages.error(request, _("Only parents/guardians can register players."))
            return redirect("panel")
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
            _("Player %(name)s registered successfully! The profile is ready to use.")
            % {"name": player_name},
            extra_tags="player_registered",
        )
        return redirect("panel")


class PlayerUpdateView(LoginRequiredMixin, UpdateView):
    """Actualizar información de jugador"""

    model = Player
    form_class = PlayerUpdateForm
    template_name = "accounts/player_edit.html"  # Default, se puede sobrescribir en get_template_names

    def get_queryset(self):
        """Optimizar consulta con select_related para evitar múltiples queries"""
        return Player.objects.select_related(
            "user",
            "user__profile",
            "user__profile__country",
            "user__profile__state",
            "user__profile__city",
            "team",
        )

    def dispatch(self, request, *args, **kwargs):
        try:
            # Verificar que el usuario esté autenticado y tenga sesión válida
            if not request.user.is_authenticated:
                from django.http import JsonResponse

                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse(
                        {"error": "Session expired. Please log in again."}, status=401
                    )
                messages.error(
                    request, _("Your session has expired. Please log in again.")
                )
                return redirect("accounts:login")

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
                messages.error(
                    request, _("You do not have permission to edit this player.")
                )
                return redirect("accounts:player_detail", pk=player.pk)
            return super().dispatch(request, *args, **kwargs)

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error in PlayerUpdateView.dispatch: {e}", exc_info=True)

            # Si es una petición AJAX, devolver error JSON
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                from django.http import JsonResponse

                return JsonResponse({"error": f"Session error: {str(e)}"}, status=500)

            # Si no es AJAX, redirigir al login
            messages.error(
                request, _("An error occurred. Please try logging in again.")
            )
            return redirect("accounts:login")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pasar información del usuario para que el formulario sepa si es padre
        kwargs["user"] = self.request.user
        return kwargs

    def get_template_names(self):
        """Usar diferentes templates según si es padre o manager/admin"""
        # Usar self.object si ya está establecido, de lo contrario obtenerlo
        player = getattr(self, "object", None)
        if player is None:
            player = self.get_object()
        user = self.request.user

        # Verificar si existe la relación PlayerParent (optimizado - usar select_related si está disponible)
        # Esto permite que incluso staff que son padres vean el template de hijo
        is_parent = PlayerParent.objects.filter(parent=user, player=player).exists()

        # Si el usuario es padre del jugador (existe la relación PlayerParent),
        # usar el template de hijo, independientemente de si es staff
        if is_parent:
            return ["accounts/player_edit_hijo.html"]
        else:
            return ["accounts/player_edit.html"]

    def get(self, request, *args, **kwargs):
        """Sobrescribir get para manejar peticiones AJAX"""
        # Si es una petición AJAX, devolver un fragmento HTML para mayor eficiencia
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            import logging

            logger = logging.getLogger(__name__)
            try:
                # Obtener el objeto (ya optimizado con get_queryset)
                self.object = self.get_object()

                # Obtener el formulario
                form = self.get_form()

                # Obtener el contexto
                context = self.get_context_data(object=self.object, form=form)

                # Usar una versión parcial del template si existe, o extraer del principal
                # Para mayor robustez, seguimos usando el mismo template pero el frontend extraerá lo que necesita
                # Pero indicamos que es AJAX para que el template pueda omitir bloques si lo desea
                template_names = self.get_template_names()
                template_name = (
                    template_names[0]
                    if isinstance(template_names, list)
                    else template_names
                )

                # Renderizar el template
                from django.http import HttpResponse
                from django.template.loader import render_to_string

                # Devolver el fragmento HTML - el template ahora usa base_ajax.html si es is_ajax
                html = render_to_string(template_name, context, request=request)

                return HttpResponse(html)

            except Exception as e:
                import traceback

                error_traceback = traceback.format_exc()
                logger.error(
                    f"Error in PlayerUpdateView.get for AJAX request: {e}\n{error_traceback}",
                    exc_info=True,
                )
                from django.http import JsonResponse

                return JsonResponse(
                    {"error": str(e), "traceback": error_traceback}, status=500
                )

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Determinar si el usuario es padre del jugador para ocultar campos en el template
        # (optimizado - reutilizar la consulta si ya se hizo en get_template_names)
        is_parent = False
        if (
            hasattr(self.request.user, "profile")
            and self.request.user.profile.is_parent
            and self.object
        ):
            # Usar exists() que es más eficiente que filter().exists() si ya tenemos el objeto
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
                return reverse_lazy("panel")
        return reverse_lazy("accounts:player_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        # Guardar usando el método save() del formulario para asegurar que todos los campos se guarden
        # El método save() del formulario ya maneja User, UserProfile y Player de forma robusta,
        # incluyendo el guardado forzado de secondary_position e is_pitcher.
        form.save()

        messages.success(
            self.request,
            _("Player information updated successfully."),
            extra_tags="player_updated",
        )

        # Si es una petición AJAX, devolver una respuesta JSON
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            from django.http import JsonResponse

            return JsonResponse(
                {
                    "success": True,
                    "message": _("Player information updated successfully."),
                    "redirect_url": str(self.get_success_url()),
                }
            )

        return redirect(self.get_success_url())

    def form_invalid(self, form):
        """Manejar errores de validación del formulario"""
        import logging

        logger = logging.getLogger(__name__)
        logger.error(
            f"PlayerUpdateView.form_invalid - Errores del formulario: {form.errors}"
        )
        logger.error(
            f"PlayerUpdateView.form_invalid - Errores no de campo: {form.non_field_errors()}"
        )

        # Si es una petición AJAX, devolver JSON con los errores
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            from django.http import JsonResponse

            # Construir diccionario de errores
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = [str(error) for error in error_list]

            return JsonResponse(
                {
                    "success": False,
                    "errors": errors,
                    "message": "Por favor corrige los errores en el formulario",
                },
                status=400,
            )

        return super().form_invalid(form)


class AgeVerificationListView(UserPassesTestMixin, LoginRequiredMixin, ListView):
    """Lista de verificaciones de edad pendientes (solo staff y managers)"""

    model = Player
    template_name = "accounts/age_verification_list.html"
    context_object_name = "pending_verifications"
    paginate_by = 20

    def test_func(self):
        """Solo staff, superuser o managers pueden ver las verificaciones"""
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return True
        if hasattr(user, "profile") and user.profile.is_team_manager:
            return True
        return False

    def get_queryset(self):
        """Obtener verificaciones pendientes según el tipo de usuario"""
        user = self.request.user
        queryset = Player.objects.filter(
            age_verification_status="pending",
            age_verification_document__isnull=False,
        ).select_related("user", "team", "user__profile")

        # Si es staff/admin, obtener todos
        if user.is_staff or user.is_superuser:
            return queryset.order_by("-updated_at")

        # Si es manager, solo de sus equipos
        if hasattr(user, "profile") and user.profile.is_team_manager:
            return queryset.filter(team__manager=user).order_by("-updated_at")

        return queryset.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pending_verifications_count"] = self.get_queryset().count()
        # Marcar la sección activa en el sidebar
        context["active_section"] = "age_verifications"
        return context


class UserListView(SuperuserRequiredMixin, ListView):
    """Lista de usuarios (solo admin/superuser)"""

    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "users"
    paginate_by = 20

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
    return redirect("panel")


@method_decorator(never_cache, name="dispatch")
@method_decorator(xframe_options_exempt, name="dispatch")
class PanelEventDetailView(UserDashboardView):
    """Vista para mostrar el detalle del evento en el panel con checkout"""

    def get_context_data(self, **kwargs):
        # Obtener el contexto base del dashboard
        context = super().get_context_data(**kwargs)

        user = self.request.user
        event_id = self.kwargs.get("pk")

        try:
            from django.db.models import Prefetch

            from apps.events.models import Division, Event, EventAttendance

            # Obtener el evento
            from apps.locations.models import HotelRoom

            event = (
                Event.objects.filter(status="published")
                .select_related(
                    "category",
                    "event_type",
                    "country",
                    "state",
                    "city",
                    "hotel",
                    "hotel__city",
                    "hotel__state",
                    "hotel__country",
                    "primary_site",
                )
                .prefetch_related(
                    Prefetch("divisions", queryset=Division.objects.order_by("name")),
                    "hotel__rooms",
                    "hotel__images",
                    "hotel__amenities",
                )
                .get(pk=event_id)
            )

            # Obtener habitaciones disponibles del hotel
            if event.hotel:
                available_rooms = (
                    HotelRoom.objects.filter(hotel=event.hotel, is_available=True)
                    .select_related("hotel")
                    .prefetch_related("amenities", "taxes", "images")
                    .order_by("room_type", "price_per_night")
                )
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
                ).select_related("player", "player__user", "player__user__profile", "player__division")

                # Obtener todos los jugadores activos
                all_active_children = [
                    pp.player for pp in player_parents if pp.player.is_active
                ]
                event_divisions = event.divisions.all()

                # Crear lista de jugadores con su estado de elegibilidad
                children_with_status = []
                ineligible_player_ids = set()

                if event_divisions.exists():
                    # Ahora que ambos usan el mismo modelo Division, comparar directamente por ID
                    event_division_ids = set(event_divisions.values_list("id", flat=True))

                    for pp in player_parents:
                        if pp.player.is_active:
                            is_eligible = False
                            if pp.player.division:
                                # Verificar si la división del jugador está en las divisiones del evento
                                # Comparar directamente los objetos Division (mismo modelo)
                                if pp.player.division.id in event_division_ids:
                                    is_eligible = True
                            # Siempre agregar el jugador, pero marcar si no es elegible
                            children_with_status.append(pp.player)
                            if not is_eligible:
                                ineligible_player_ids.add(pp.player.id)
                else:
                    # Si el evento no tiene divisiones, todos los jugadores son elegibles
                    children_with_status = all_active_children

                # Mostrar TODOS los jugadores (no filtrar)
                children = children_with_status
                # Guardar IDs de jugadores ineligibles para marcarlos como disabled en el template
                context["ineligible_player_ids"] = ineligible_player_ids if ineligible_player_ids else set()
                context["has_ineligible_children"] = len(ineligible_player_ids) > 0

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


@method_decorator(xframe_options_exempt, name="dispatch")
class PanelEventosEmbedView(UserDashboardView):
    """
    Renderiza el tab 'eventos' dentro de un iframe (sin el panel completo),
    usando el wrapper templates/accounts/panel_tabs/embed_base.html
    """

    template_name = "accounts/panel_tabs/embed_base.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["inner_template"] = "accounts/panel_tabs/eventos.html"
        # En el iframe no necesitamos activar tabs del panel
        context["active_tab"] = "eventos"
        return context


@method_decorator(xframe_options_exempt, name="dispatch")
class PanelEventDetailEmbedView(PanelEventDetailView):
    """
    Renderiza el detalle del evento dentro de un iframe (sin panel completo).
    Reutiliza la lógica de PanelEventDetailView para poblar 'event' y contexto.
    """

    template_name = "accounts/panel_tabs/embed_base.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["inner_template"] = "accounts/panel_tabs/detalle_evento_vue.html"

        # Agregar el tipo de usuario del usuario actual al contexto
        user = self.request.user
        if hasattr(user, "profile"):
            context["user_type"] = user.profile.user_type
        else:
            context["user_type"] = "player"  # Default

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
            messages.error(
                request, _("You must be a parent to register children to events.")
            )
            return redirect("panel")

        # Obtener los IDs de los jugadores seleccionados
        player_ids = request.POST.getlist("players")

        if not player_ids:
            messages.warning(
                request, _("Please select at least one child/player to register.")
            )
            return redirect("accounts:panel_event_detail", pk=pk)

        # Obtener los jugadores relacionados al usuario
        from .models import Player, PlayerParent

        player_parents = PlayerParent.objects.filter(
            parent=user, player_id__in=player_ids
        ).select_related("player")

        # IMPORTANTE: NO crear EventAttendance aquí
        # El registro al evento SOLO se crea después de que el pago sea exitoso
        # en _finalize_stripe_event_checkout()
        # Esta función solo prepara los jugadores para el checkout de Stripe
        # Los jugadores seleccionados se almacenan en la sesión o se envían directamente al checkout

        # Verificar si el evento tiene entry_fee
        if event.default_entry_fee and event.default_entry_fee > 0:
            messages.info(
                request,
                _("Please proceed to payment to complete the registration."),
            )
        else:
            # Si no hay entry_fee, los jugadores ya están seleccionados para registro gratuito
            messages.success(
                request,
                _("Players selected. Please proceed to complete registration."),
            )

        return redirect("accounts:panel_event_detail", pk=pk)

    except ImportError:
        messages.error(request, _("Events app is not available."))
        return redirect("panel")
    except Exception as e:
        messages.error(request, _("An error occurred: %(error)s") % {"error": str(e)})
        return redirect("panel")


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
    from datetime import datetime

    from apps.locations.models import HotelRoom, HotelService

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

        per_night_total = (
            room.price_per_night
            + (room.additional_guest_price or Decimal("0.00")) * extra_guests
        )
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


def _compute_hotel_amount_from_vue_payload(payload: dict) -> dict:
    """
    Compute hotel totals from Vue payload (hotel_reservation_json).

    Matches the current Vue implementation:
    - Room base price is per-night and multiplied by nights
    - Additional guests are per-night and multiplied by nights
    - Taxes are taken from room.taxes[] as fixed per-night amounts and multiplied by nights
    """
    from datetime import datetime, timedelta

    from apps.locations.models import HotelRoom

    def _as_decimal(v) -> Decimal:
        try:
            return Decimal(str(v)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except Exception:
            return Decimal("0.00")

    check_in_date = (payload or {}).get("check_in_date") or ""
    check_out_date = (payload or {}).get("check_out_date") or ""
    nights = payload.get("nights")

    # Determine nights
    computed_nights = None
    try:
        if check_in_date and check_out_date:
            d_in = datetime.strptime(check_in_date, "%Y-%m-%d").date()
            d_out = datetime.strptime(check_out_date, "%Y-%m-%d").date()
            computed_nights = (d_out - d_in).days
    except Exception:
        computed_nights = None

    try:
        nights_int = int(nights) if nights is not None else None
    except Exception:
        nights_int = None

    nights_final = computed_nights if (computed_nights is not None) else nights_int
    if not nights_final or nights_final < 1:
        nights_final = 1

    rooms = (payload or {}).get("rooms") or []
    guest_assignments = (payload or {}).get("guest_assignments") or {}

    room_base = Decimal("0.00")  # includes extra guests, before taxes
    total_taxes = Decimal("0.00")

    for r in rooms:
        room_id = str((r or {}).get("roomId") or (r or {}).get("room_id") or "")
        if not room_id:
            continue

        # Guests assigned to this room
        assigned = (
            guest_assignments.get(room_id) or guest_assignments.get(str(room_id)) or []
        )
        try:
            guests_count = int(len(assigned))
        except Exception:
            guests_count = 0

        # Per-night prices (from payload if present; otherwise, fallback to DB)
        price_per_night = _as_decimal((r or {}).get("price"))
        includes = (r or {}).get("priceIncludesGuests")
        additional_guest_price = _as_decimal((r or {}).get("additionalGuestPrice"))

        # Fallback to DB if payload missing/zero (defensive)
        try:
            room_obj = HotelRoom.objects.filter(pk=int(room_id)).first()
        except Exception:
            room_obj = None

        if room_obj:
            if price_per_night == Decimal("0.00"):
                price_per_night = _as_decimal(room_obj.price_per_night)
            try:
                includes_int = (
                    int(includes)
                    if includes is not None
                    else int(room_obj.price_includes_guests or 1)
                )
            except Exception:
                includes_int = int(room_obj.price_includes_guests or 1)
            if additional_guest_price == Decimal("0.00"):
                additional_guest_price = _as_decimal(
                    room_obj.additional_guest_price or Decimal("0.00")
                )
        else:
            try:
                includes_int = int(includes) if includes is not None else 1
            except Exception:
                includes_int = 1

        extra_guests = max(0, guests_count - (includes_int or 1))
        per_night_total = price_per_night + (
            additional_guest_price * Decimal(str(extra_guests))
        )
        item_room_base = (per_night_total * Decimal(str(nights_final))).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        room_base += item_room_base

        # Taxes: fixed per-night amounts per room.
        # Prefer payload taxes (what the UI is showing). If missing, fallback to DB room.taxes.
        taxes = (r or {}).get("taxes") or []
        if not taxes and room_obj:
            try:
                taxes = list(room_obj.taxes.values("name", "amount"))
            except Exception:
                taxes = []

        for tx in taxes:
            # tx can be dict from payload, or dict from values()
            amt = _as_decimal((tx or {}).get("amount"))
            if amt <= 0:
                continue
            total_taxes += (amt * Decimal(str(nights_final))).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

    total = (room_base + total_taxes).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return {
        "room_base": room_base,
        "total_taxes": total_taxes,
        "total": total,
        "nights": int(nights_final),
        "check_in": check_in_date,
        "check_out": check_out_date,
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
        months = (
            (payment_deadline.year - now.year) * 12
            + (payment_deadline.month - now.month)
            + 1
        )
        if not months or months < 1:
            months = 1
        return int(months)
    except Exception:
        return 1


@login_required
@require_POST
@csrf_exempt
def create_stripe_event_checkout_session(request, pk):
    if not settings.STRIPE_SECRET_KEY:
        return JsonResponse(
            {
                "success": False,
                "error": _("Stripe is not configured (STRIPE_SECRET_KEY)."),
            },
            status=500,
        )

    try:
        import stripe  # type: ignore
    except Exception:
        return JsonResponse(
            {"success": False, "error": _("Stripe SDK is not installed.")}, status=500
        )

    from apps.events.models import Event

    event = get_object_or_404(Event, pk=pk)
    user = request.user

    if not (hasattr(user, "profile") and user.profile.is_parent):
        return JsonResponse(
            {"success": False, "error": _("Only parents can pay for registrations.")},
            status=403,
        )

    player_ids = request.POST.getlist("players")
    if not player_ids:
        return JsonResponse(
            {"success": False, "error": _("Select at least 1 player.")}, status=400
        )

    player_parents = PlayerParent.objects.filter(
        parent=user, player_id__in=player_ids
    ).select_related("player", "player__user")
    valid_players = [
        pp.player for pp in player_parents if getattr(pp.player, "is_active", True)
    ]
    if len(valid_players) != len(player_ids):
        return JsonResponse(
            {
                "success": False,
                "error": _(
                    "There are invalid players or players that do not belong to the user."
                ),
            },
            status=400,
        )

    # Verificar que ningún jugador ya esté registrado en el evento (solo confirmed, no pending)
    # porque pendientes pueden existir de intentos anteriores que no completaron el pago
    from apps.events.models import EventAttendance

    already_registered = []
    for player in valid_players:
        # Solo verificar status="confirmed", no "pending", porque pending puede existir sin pago
        if EventAttendance.objects.filter(
            event=event, user=player.user, status="confirmed"
        ).exists():
            already_registered.append(
                player.user.get_full_name() or player.user.username
            )

    if already_registered:
        return JsonResponse(
            {
                "success": False,
                "error": _(
                    "The following players are already registered and confirmed for this event: %(players)s"
                )
                % {"players": ", ".join(already_registered)},
            },
            status=400,
        )

    payment_mode = request.POST.get("payment_mode", "plan")
    if payment_mode not in ("plan", "now"):
        payment_mode = "plan"

    entry_fee = _decimal(getattr(event, "default_entry_fee", None), default="0.00")
    players_count = int(len(valid_players))
    players_total = (entry_fee * Decimal(str(players_count))).quantize(Decimal("0.01"))

    # Prefer Vue payload (hotel_reservation_json) over legacy session cart.
    hotel_payload_raw = request.POST.get("hotel_reservation_json") or ""
    hotel_payload = None
    vue_cart_snapshot = {}

    if hotel_payload_raw:
        try:
            hotel_payload = json.loads(hotel_payload_raw)
        except Exception:
            hotel_payload = None

    # Legacy cart (server-side) fallback
    cart = request.session.get("hotel_cart", {}) or {}

    if (
        hotel_payload
        and isinstance(hotel_payload, dict)
        and (hotel_payload.get("rooms") or [])
    ):
        # Validar disponibilidad de stock ANTES de crear el checkout
        check_in_date = hotel_payload.get("check_in_date") or ""
        check_out_date = hotel_payload.get("check_out_date") or ""

        if check_in_date and check_out_date:
            try:
                from datetime import datetime

                from apps.locations.models import HotelRoom

                check_in = datetime.strptime(check_in_date, "%Y-%m-%d").date()
                check_out = datetime.strptime(check_out_date, "%Y-%m-%d").date()

                # Validar stock para cada habitación seleccionada
                for r in hotel_payload.get("rooms") or []:
                    room_id = str((r or {}).get("roomId") or "")
                    if not room_id:
                        continue

                    try:
                        room = HotelRoom.objects.get(id=room_id)

                        # Validar que la habitación esté disponible
                        if not room.is_available:
                            return JsonResponse(
                                {
                                    "success": False,
                                    "error": _("Room %(room_number)s is not available.")
                                    % {"room_number": room.room_number},
                                },
                                status=400,
                            )

                        # Validar stock disponible
                        if room.stock is not None and room.stock > 0:
                            active_reservations_count = room.reservations.filter(
                                check_in__lt=check_out,
                                check_out__gt=check_in,
                                status__in=["pending", "confirmed", "checked_in"],
                            ).count()

                            if active_reservations_count >= room.stock:
                                return JsonResponse(
                                    {
                                        "success": False,
                                        "error": _(
                                            "Room %(room_number)s is not available for the selected dates. "
                                            "All rooms of this type are already reserved."
                                        )
                                        % {"room_number": room.room_number},
                                    },
                                    status=400,
                                )
                    except HotelRoom.DoesNotExist:
                        return JsonResponse(
                            {
                                "success": False,
                                "error": _("Room with ID %(room_id)s not found.")
                                % {"room_id": room_id},
                            },
                            status=400,
                        )
            except (ValueError, TypeError) as e:
                # Error al parsear fechas, continuar sin validar stock (mejor que fallar completamente)
                pass

        hotel_breakdown = _compute_hotel_amount_from_vue_payload(hotel_payload)
        hotel_total = hotel_breakdown["total"]

        # Build a snapshot compatible with _finalize_stripe_event_checkout()
        # (one room item per selected room; services currently not supported in Vue)
        check_in = hotel_breakdown.get("check_in") or ""
        check_out = hotel_breakdown.get("check_out") or ""
        guest_assignments = hotel_payload.get("guest_assignments") or {}
        all_guests = (
            hotel_payload.get("guests", []) or []
        )  # Lista completa de huéspedes desde Vue

        # IMPORTANTE: Preservar el orden de selección de las habitaciones
        for room_order, r in enumerate(hotel_payload.get("rooms") or []):
            room_id = str((r or {}).get("roomId") or "")
            if not room_id:
                continue
            assigned_indices = (
                guest_assignments.get(room_id)
                or guest_assignments.get(str(room_id))
                or []
            )

            # Calcular número de huéspedes: usar assigned_indices si está disponible, sino usar el valor del payload
            try:
                if assigned_indices and len(assigned_indices) > 0:
                    guests_count = int(len(assigned_indices))
                else:
                    # Fallback: usar el número de huéspedes del payload de la habitación
                    guests_count = int(
                        (r or {}).get("guests") or (r or {}).get("guestsCount") or 0
                    )
                    if guests_count == 0:
                        guests_count = 1  # Mínimo 1 huésped
            except (ValueError, TypeError):
                guests_count = 1

            # Extraer información completa de huéspedes adicionales (excluyendo el principal)
            additional_guest_names = []
            additional_guest_details = []
            guest_names_text = ""

            if (
                isinstance(assigned_indices, list)
                and len(assigned_indices) > 0
                and isinstance(all_guests, list)
            ):
                # assigned_indices contiene índices que referencian all_guests
                for idx, guest_index in enumerate(assigned_indices):
                    if idx == 0:
                        continue  # Skip el primero (principal)

                    # Obtener el objeto completo del huésped
                    try:
                        guest_index_int = (
                            int(guest_index)
                            if isinstance(guest_index, (int, str))
                            else None
                        )
                        if guest_index_int is not None and 0 <= guest_index_int < len(
                            all_guests
                        ):
                            guest_obj = all_guests[guest_index_int]

                            # Construir nombre completo
                            guest_name = ""
                            if isinstance(guest_obj, dict):
                                guest_name = (
                                    guest_obj.get("displayName", "")
                                    or guest_obj.get("name", "")
                                    or f"{guest_obj.get('first_name', '')} {guest_obj.get('last_name', '')}".strip()
                                ).strip()

                                # Construir objeto con datos completos
                                guest_detail = {
                                    "name": guest_name,
                                    "type": guest_obj.get(
                                        "type", "adult"
                                    ),  # "adult" o "child"
                                    "birth_date": guest_obj.get("birth_date", "")
                                    or guest_obj.get("birthDate", ""),
                                    "email": guest_obj.get("email", "")
                                    or guest_obj.get("email_address", ""),
                                }
                                additional_guest_details.append(guest_detail)
                                additional_guest_names.append(guest_name)

                    except (ValueError, IndexError, TypeError):
                        # Fallback: si no podemos obtener el objeto, intentar usar el índice como nombre
                        continue

                # Construir texto para notas (compatibilidad legacy)
                if additional_guest_names:
                    guest_names_text = "Additional guests: " + ", ".join(
                        additional_guest_names
                    )

            # Obtener información de la habitación para calcular personas adicionales como fallback
            # Este fallback se ejecuta SIEMPRE, incluso si no hay guest_assignments del frontend
            try:
                from apps.locations.models import HotelRoom

                room_obj = HotelRoom.objects.filter(pk=int(room_id)).first()
                if room_obj:
                    price_includes_guests = room_obj.price_includes_guests or 1

                    # Si no tenemos datos detallados pero hay más huéspedes que los incluidos, crear placeholders
                    if (
                        not additional_guest_names
                        and guests_count > price_includes_guests
                    ):
                        extra_guests_count = guests_count - price_includes_guests
                        for i in range(extra_guests_count):
                            guest_num = i + 1
                            placeholder_name = f"Additional Guest {guest_num}"
                            additional_guest_names.append(placeholder_name)
                            additional_guest_details.append(
                                {
                                    "name": placeholder_name,
                                    "type": "adult",
                                    "birth_date": "",
                                    "email": "",
                                }
                            )
            except Exception as e:
                # Log del error para debugging
                import logging

                logger = logging.getLogger(__name__)
                logger.warning(
                    f"Error al calcular huéspedes adicionales para room_id={room_id}: {e}"
                )

            vue_cart_snapshot[f"vue-room-{room_id}"] = {
                "type": "room",
                "room_id": int(room_id) if str(room_id).isdigit() else room_id,
                "room_order": room_order,  # Índice para preservar el orden de selección
                "check_in": check_in,
                "check_out": check_out,
                "guests": max(1, guests_count),
                "services": [],
                "additional_guest_names": additional_guest_names,  # SIEMPRE guardar (puede estar vacío)
                "additional_guest_details": additional_guest_details,  # SIEMPRE guardar (puede estar vacío)
                "guest_assignments": guest_assignments,  # Guardar para referencia
                "all_guests": all_guests,  # Guardar lista completa de huéspedes
                "notes": guest_names_text,  # Texto para compatibilidad
            }

        # Agregar datos adicionales del evento, registrant y jugadores registrados al snapshot
        # Estos datos están disponibles en hotel_cart_snapshot para poblar toda la información
        # cuando se procese el checkout y se cree la Order y las HotelReservation
        enriched_cart = vue_cart_snapshot.copy()
        # Agregar datos del evento si están disponibles en el payload
        # Incluye: id, pk, title, start_date, end_date, location, hotel (pk, name, address)
        if hotel_payload.get("event"):
            enriched_cart["_event_data"] = hotel_payload.get("event")
        # Agregar datos del registrant si están disponibles en el payload
        # Incluye: id, username, email, first_name, last_name, name, phone
        if hotel_payload.get("registrant"):
            enriched_cart["_registrant_data"] = hotel_payload.get("registrant")
        # Agregar datos de jugadores registrados si están disponibles en el payload
        # Incluye: id, first_name, last_name, name, email, phone, birth_date, age, grade, division, team, jersey_number, position
        if hotel_payload.get("registered_players"):
            enriched_cart["_registered_players_data"] = hotel_payload.get(
                "registered_players"
            )
    else:
        # Enriquecer el snapshot del carrito con información de huéspedes adicionales
        enriched_cart = {}
        for item_id, item_data in cart.items():
            if item_data.get("type") == "room":
                try:
                    from apps.locations.models import HotelRoom

                    room = HotelRoom.objects.get(id=item_data.get("room_id"))
                    guests = int(item_data.get("guests", 1) or 1)
                    includes = int(room.price_includes_guests or 1)
                    extra_guests = max(0, guests - includes)

                    # Agregar información de huéspedes adicionales al snapshot
                    enriched_item = item_data.copy()
                    enriched_item["guests_included"] = includes
                    enriched_item["extra_guests"] = extra_guests
                    enriched_item["additional_guest_price"] = str(
                        room.additional_guest_price or Decimal("0.00")
                    )
                    enriched_cart[item_id] = enriched_item
                except Exception:
                    # Si hay error, usar el item original
                    enriched_cart[item_id] = item_data
            else:
                enriched_cart[item_id] = item_data

        hotel_breakdown = (
            _compute_hotel_amount_from_cart(enriched_cart)
            if enriched_cart
            else {
                "room_base": Decimal("0.00"),
                "services_total": Decimal("0.00"),
                "iva": Decimal("0.00"),
                "ish": Decimal("0.00"),
                "total": Decimal("0.00"),
            }
        )
        hotel_total = hotel_breakdown["total"]

    # Pay now discount only applies if a hotel stay is included
    discount_percent = 5 if (payment_mode == "now" and hotel_total > 0) else 0
    discount_multiplier = Decimal("1.00") - (
        Decimal(str(discount_percent)) / Decimal("100")
    )

    # Hotel buy out fee: solo aplica si el evento tiene hotel, hay jugadores y NO se añadió hotel al checkout
    has_event_hotel = getattr(event, "hotel", None) is not None
    buy_out_fee = _decimal(
        getattr(getattr(event, "hotel", None), "buy_out_fee", None), default="0.00"
    )
    hotel_buy_out_fee = (
        buy_out_fee
        if (has_event_hotel and players_count > 0 and not enriched_cart)
        else Decimal("0.00")
    )

    subtotal = (players_total + hotel_total + hotel_buy_out_fee).quantize(Decimal("0.01"))

    # Service fee: porcentaje del subtotal
    service_fee_percent = _decimal(getattr(event, "service_fee", None), default="0.00")
    service_fee_amount = (
        subtotal * (service_fee_percent / Decimal("100"))
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Aplicar descuento al subtotal + service fee
    total_before_discount = (subtotal + service_fee_amount).quantize(Decimal("0.01"))
    total = (total_before_discount * discount_multiplier).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    # Debug log to compare totals (helps diagnose mismatches with frontend)
    try:
        import logging

        logger = logging.getLogger(__name__)
        fe_players_total = request.POST.get("frontend_players_total")
        fe_hotel_total = request.POST.get("frontend_hotel_total")
        fe_hotel_buy_out_fee = request.POST.get("frontend_hotel_buy_out_fee")
        fe_subtotal = request.POST.get("frontend_subtotal")
        fe_discount = request.POST.get("frontend_discount_percent")
        fe_paynow_total = request.POST.get("frontend_paynow_total")
        fe_plan_months = request.POST.get("frontend_plan_months")
        fe_plan_monthly = request.POST.get("frontend_plan_monthly")
        fe_hotel_nights = request.POST.get("frontend_hotel_nights")

        logger.info(
            "[StripeCheckout] event=%s user=%s mode=%s players=%s players_total=%s hotel_total=%s hotel_buy_out_fee=%s service_fee_percent=%s service_fee_amount=%s total_before_discount=%s discount=%s total=%s source=%s nights=%s | FE players_total=%s hotel_total=%s hotel_buy_out_fee=%s subtotal=%s service_fee_percent=%s service_fee_amount=%s total_before_discount=%s discount=%s paynow_total=%s plan_months=%s plan_monthly=%s nights=%s",
            event.pk,
            user.pk,
            payment_mode,
            players_count,
            str(players_total),
            str(hotel_total),
            str(hotel_buy_out_fee),
            str(service_fee_percent),
            str(service_fee_amount),
            str(total_before_discount),
            str(discount_percent),
            str(total),
            "vue" if hotel_payload else "session_cart",
            (
                str(hotel_breakdown.get("nights", ""))
                if isinstance(hotel_breakdown, dict)
                else ""
            ),
            fe_players_total,
            fe_hotel_total,
            fe_hotel_buy_out_fee,
            fe_subtotal,
            request.POST.get("frontend_service_fee_percent"),
            request.POST.get("frontend_service_fee_amount"),
            request.POST.get("frontend_total_before_discount"),
            fe_discount,
            fe_paynow_total,
            fe_plan_months,
            fe_plan_monthly,
            fe_hotel_nights,
        )
    except Exception:
        pass

    currency = (getattr(settings, "STRIPE_CURRENCY", "usd") or "usd").lower()

    def scale(amount: Decimal) -> Decimal:
        return (amount * discount_multiplier).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    # Build Stripe line items differently for pay-now vs plan:
    # - now: one-time payment line items
    # - plan: recurring monthly subscription line item (card saved + auto charges)
    line_items = []
    plan_months = _plan_months_until_deadline(getattr(event, "payment_deadline", None))
    plan_monthly_amount = Decimal("0.00")

    if payment_mode == "plan":
        # Plan doesn't apply discount. Monthly amount is approximate = (subtotal + service_fee) / months.
        plan_monthly_amount = (total_before_discount / Decimal(str(plan_months))).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if plan_monthly_amount <= 0:
            return JsonResponse(
                {"success": False, "error": _("There is nothing to charge.")},
                status=400,
            )

        # Build description including service fee if applicable
        plan_description = (
            f"First charge today, then {max(0, plan_months - 1)} monthly charge(s). "
            f"Ends automatically."
        )
        if service_fee_amount > 0:
            plan_description += (
                f" Includes service fee ({service_fee_percent}%)."
            )

        line_items = [
            {
                "price_data": {
                    "currency": currency,
                    "product_data": {
                        "name": f"Payment plan ({plan_months} month{'s' if plan_months != 1 else ''}) - {event.title}",
                        "description": plan_description,
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
                        "product_data": {
                            "name": f"Hotel stay{(' - ' + hotel_name) if hotel_name else ''}"
                        },
                        "unit_amount": _money_to_cents(scale(hotel_total)),
                    },
                    "quantity": 1,
                }
            )

        if hotel_buy_out_fee > 0:
            line_items.append(
                {
                    "price_data": {
                        "currency": currency,
                        "product_data": {"name": "Hotel buy out fee"},
                        "unit_amount": _money_to_cents(scale(hotel_buy_out_fee)),
                    },
                    "quantity": 1,
                }
            )

        if service_fee_amount > 0:
            line_items.append(
                {
                    "price_data": {
                        "currency": currency,
                        "product_data": {
                            "name": f"Service fee ({service_fee_percent}%)"
                        },
                        "unit_amount": _money_to_cents(scale(service_fee_amount)),
                    },
                    "quantity": 1,
                }
            )

        if not line_items:
            return JsonResponse(
                {"success": False, "error": _("There is nothing to charge.")},
                status=400,
            )

    stripe.api_key = settings.STRIPE_SECRET_KEY
    stripe_account = (
        event.stripe_payment_profile
        if getattr(event, "stripe_payment_profile", None)
        else None
    )

    success_url = (
        request.build_absolute_uri(
            reverse("accounts:stripe_event_checkout_success", kwargs={"pk": event.pk})
        )
        + "?session_id={CHECKOUT_SESSION_ID}"
    )
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
            "service_fee_percent": str(service_fee_percent),
            "service_fee_amount": str(service_fee_amount),
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
        hotel_cart_snapshot=enriched_cart,  # Usar el carrito enriquecido con info de extra guests
        breakdown={
            "players_total": str(players_total),
            "hotel_room_base": str(hotel_breakdown["room_base"]),
            "hotel_services_total": str(
                hotel_breakdown.get("services_total", Decimal("0.00"))
            ),
            "hotel_iva": str(hotel_breakdown.get("iva", Decimal("0.00"))),
            "hotel_ish": str(hotel_breakdown.get("ish", Decimal("0.00"))),
            "hotel_total_taxes": str(
                hotel_breakdown.get("total_taxes", Decimal("0.00"))
            ),
            "hotel_nights": str(hotel_breakdown.get("nights", "")),
            "hotel_total": str(hotel_total),
            "hotel_buy_out_fee": str(hotel_buy_out_fee),
            "service_fee_percent": str(service_fee_percent),
            "service_fee_amount": str(service_fee_amount),
            "subtotal": str(subtotal),
            "total_before_discount": str(total_before_discount),
            "discount_percent": discount_percent,
            "total": str(total),
        },
        amount_total=total,
        plan_months=plan_months,
        plan_monthly_amount=plan_monthly_amount,
        status="created",
    )

    return JsonResponse(
        {"success": True, "checkout_url": session.url, "session_id": session.id}
    )


def _create_order_from_stripe_checkout(checkout: StripeEventCheckout) -> Order:
    """
    Crea un Order desde un StripeEventCheckout completado.
    Centraliza toda la información de la compra.
    """
    # Verificar si ya existe una Order para este checkout
    if Order.objects.filter(stripe_checkout=checkout).exists():
        return Order.objects.get(stripe_checkout=checkout)

    # Calcular desglose desde breakdown o desde el checkout
    breakdown = checkout.breakdown or {}
    subtotal = breakdown.get("subtotal", Decimal("0.00"))
    # Asegurar que subtotal es Decimal
    if isinstance(subtotal, str):
        subtotal = Decimal(subtotal)
    elif not isinstance(subtotal, Decimal):
        subtotal = Decimal(str(subtotal))

    if subtotal == Decimal("0.00"):
        # Intentar calcular desde el breakdown del checkout
        breakdown_data = checkout.breakdown or {}
        players_total = breakdown_data.get("players_total", Decimal("0.00"))
        hotel_total = breakdown_data.get("hotel_total", Decimal("0.00"))
        # Soporte para ambos nombres (legacy: no_show_fee, nuevo: hotel_buy_out_fee)
        hotel_buy_out_fee = breakdown_data.get("hotel_buy_out_fee") or breakdown_data.get("no_show_fee", Decimal("0.00"))
        # Asegurar que son Decimal
        if isinstance(players_total, str):
            players_total = Decimal(players_total)
        elif not isinstance(players_total, Decimal):
            players_total = Decimal(str(players_total))
        if isinstance(hotel_total, str):
            hotel_total = Decimal(hotel_total)
        elif not isinstance(hotel_total, Decimal):
            hotel_total = Decimal(str(hotel_total))
        if isinstance(hotel_buy_out_fee, str):
            hotel_buy_out_fee = Decimal(hotel_buy_out_fee)
        elif not isinstance(hotel_buy_out_fee, Decimal):
            hotel_buy_out_fee = Decimal(str(hotel_buy_out_fee)) if hotel_buy_out_fee else Decimal("0.00")
        subtotal = players_total + hotel_total + hotel_buy_out_fee

    tax_amount = breakdown.get("tax_amount", Decimal("0.00"))
    if isinstance(tax_amount, str):
        tax_amount = Decimal(tax_amount)
    elif not isinstance(tax_amount, Decimal):
        tax_amount = Decimal(str(tax_amount))

    discount_amount = Decimal("0.00")
    if checkout.discount_percent > 0:
        discount_amount = (
            subtotal * Decimal(str(checkout.discount_percent)) / Decimal("100")
        )

    # Obtener stripe_customer_id si existe
    stripe_customer_id = ""
    if hasattr(checkout.user, "profile") and hasattr(
        checkout.user.profile, "stripe_customer_id"
    ):
        stripe_customer_id = (
            getattr(checkout.user.profile, "stripe_customer_id", "") or ""
        )

    # Calcular información del plan de pagos
    plan_months = checkout.plan_months or 1
    plan_monthly_amount = checkout.plan_monthly_amount or Decimal("0.00")
    plan_total_amount = plan_monthly_amount * Decimal(str(plan_months))

    # Si es un plan de pagos, el primer pago ya se completó
    plan_payments_completed = (
        1 if checkout.payment_mode == "plan" and checkout.status == "paid" else 0
    )
    plan_payments_remaining = max(0, plan_months - plan_payments_completed)

    # Extraer información de huéspedes adicionales del hotel_cart_snapshot
    # IMPORTANTE: Mantener el orden de las habitaciones como fueron seleccionadas
    hotel_reservations_info = []
    hotel_cart = checkout.hotel_cart_snapshot or {}

    # Ordenar las habitaciones para mantener el orden de selección original
    # Usar room_order si está disponible, sino usar el orden de inserción del diccionario
    sorted_room_items = []
    for room_key, item_data in hotel_cart.items():
        if item_data.get("type") != "room":
            continue
        # Usar room_order si está disponible (preserva el orden de selección)
        room_order = item_data.get(
            "room_order", 999999
        )  # Default alto para items sin order
        sorted_room_items.append((room_order, room_key, item_data))

    # Ordenar por room_order para mantener el orden de selección original
    sorted_room_items.sort(key=lambda x: x[0])

    for room_order, room_key, item_data in sorted_room_items:

        # Obtener información del hotel desde la habitación
        hotel_name = ""
        room_number = item_data.get("room_number", "")
        try:
            from apps.locations.models import HotelRoom

            room_id = item_data.get("room_id")
            if room_id:
                room = (
                    HotelRoom.objects.select_related("hotel").filter(id=room_id).first()
                )
                if room:
                    if room.hotel:
                        hotel_name = room.hotel.hotel_name
                    # Si no hay room_number en item_data, obtenerlo de la habitación
                    if not room_number:
                        room_number = room.room_number
        except Exception:
            pass

        reservation_info = {
            "room_id": item_data.get("room_id"),
            "room_number": room_number,
            "hotel_name": hotel_name,
            "check_in": item_data.get("check_in", ""),
            "check_out": item_data.get("check_out", ""),
            "number_of_guests": item_data.get("guests", 1),
            "guest_name": item_data.get(
                "guest_name", checkout.user.get_full_name() or checkout.user.username
            ),
            "guest_email": item_data.get("guest_email", checkout.user.email),
            "guest_phone": item_data.get("guest_phone", ""),
            "additional_guest_names": [],
        }

        # Extraer información completa de huéspedes adicionales
        # IMPORTANTE: Mantener el orden de los huéspedes como fueron asignados
        # Priorizar additional_guest_details (datos completos)
        additional_guest_details_list = item_data.get("additional_guest_details", [])
        if (
            isinstance(additional_guest_details_list, list)
            and additional_guest_details_list
        ):
            # Si tenemos datos completos, usarlos EN EL MISMO ORDEN que fueron asignados
            # Preservar el orden de la lista original
            reservation_info["additional_guest_names"] = [
                g.get("name", "")
                for g in additional_guest_details_list
                if g.get("name", "").strip()
            ]
            # Guardar los detalles completos manteniendo el orden exacto
            reservation_info["additional_guest_details"] = additional_guest_details_list
        elif item_data.get("additional_guest_names"):
            # Fallback: usar lista de nombres
            additional_guest_names = item_data.get("additional_guest_names", [])
            if isinstance(additional_guest_names, list) and additional_guest_names:
                reservation_info["additional_guest_names"] = [
                    name for name in additional_guest_names if name and name.strip()
                ]
                reservation_info["additional_guest_details"] = [
                    {"name": name}
                    for name in additional_guest_names
                    if name and name.strip()
                ]
        else:
            # Fallback: extraer desde las notas (código legacy)
            notes_text = item_data.get("notes", "") or ""
            if notes_text:
                import re

                guest_names_list = []

                # Extraer nombres de "Selected players/children:"
                players_match = re.search(
                    r"Selected players/children:\s*([^|]+)", notes_text
                )
                if players_match:
                    players_str = players_match.group(1).strip()
                    player_names = [
                        p.strip() for p in re.split(r"[,|]", players_str) if p.strip()
                    ]
                    guest_names_list.extend(player_names)

                # Extraer nombres de "Additional adults:"
                adults_match = re.search(r"Additional adults:\s*([^|]+)", notes_text)
                if adults_match:
                    adults_str = adults_match.group(1).strip()
                    adult_names = re.findall(r"([^(|]+?)(?:\s*\([^)]+\))?", adults_str)
                    guest_names_list.extend(
                        [a.strip() for a in adult_names if a.strip()]
                    )

                # Extraer nombres de "Additional children:"
                children_match = re.search(
                    r"Additional children:\s*([^|]+)", notes_text
                )
                if children_match:
                    children_str = children_match.group(1).strip()
                    child_names = re.findall(
                        r"([^(|]+?)(?:\s*\([^)]+\))?", children_str
                    )
                    guest_names_list.extend(
                        [c.strip() for c in child_names if c.strip()]
                    )

                # Remover el nombre principal si está en la lista
                primary_guest = reservation_info["guest_name"]
                if primary_guest in guest_names_list:
                    guest_names_list.remove(primary_guest)

                reservation_info["additional_guest_names"] = guest_names_list
            else:
                reservation_info["additional_guest_names"] = []

        hotel_reservations_info.append(reservation_info)

    # Agregar información de reservas al breakdown
    if hotel_reservations_info:
        breakdown["hotel_reservations"] = hotel_reservations_info

    # Crear la Order
    order = Order.objects.create(
        user=checkout.user,
        stripe_checkout=checkout,
        event=checkout.event,
        status="paid",
        payment_method="stripe",
        payment_mode=checkout.payment_mode,
        stripe_session_id=checkout.stripe_session_id,
        stripe_customer_id=stripe_customer_id,
        stripe_subscription_id=checkout.stripe_subscription_id or "",
        stripe_subscription_schedule_id=checkout.stripe_subscription_schedule_id or "",
        subtotal=subtotal,
        discount_amount=discount_amount,
        tax_amount=tax_amount,
        total_amount=checkout.amount_total,
        currency=checkout.currency,
        breakdown=breakdown,
        registered_player_ids=checkout.player_ids or [],
        plan_months=plan_months,
        plan_monthly_amount=plan_monthly_amount,
        plan_total_amount=plan_total_amount,
        plan_payments_completed=plan_payments_completed,
        plan_payments_remaining=plan_payments_remaining,
        notes=f"Orden creada desde Stripe checkout #{checkout.pk}",
        paid_at=checkout.paid_at,
    )

    return order


def _finalize_stripe_event_checkout(checkout: StripeEventCheckout) -> None:
    """Idempotent finalize: confirm event attendance + create hotel reservations."""
    from datetime import datetime

    from apps.events.models import EventAttendance
    from apps.locations.models import (
        HotelReservation,
        HotelReservationService,
        HotelRoom,
        HotelService,
    )

    with transaction.atomic():
        checkout.refresh_from_db()
        # Verificar si ya está pagado ANTES de procesar (idempotencia)
        if checkout.status == "paid":
            # Si ya está pagado, verificar si ya existe una orden/reservas
            # Si no existen, crearlas (por si falló antes)
            if not Order.objects.filter(stripe_checkout=checkout).exists():
                # Continuar con el procesamiento aunque esté marcado como paid
                pass
            else:
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
            attendance.notes = (
                attendance.notes or ""
            ) + f"\nPaid via Stripe session {checkout.stripe_session_id}"
            attendance.save()

        # Create hotel reservations from snapshot
        # IMPORTANTE: Mantener el orden de las habitaciones como fueron seleccionadas
        reservations_to_update = []  # Lista de reservas para asignar a la orden después
        cart = checkout.hotel_cart_snapshot or {}

        # Ordenar las habitaciones para mantener el orden de selección original
        # Usar room_order si está disponible, sino usar el orden de inserción del diccionario
        sorted_room_items_for_reservations = []
        for room_key, item_data in cart.items():
            if item_data.get("type") != "room":
                continue
            # Usar room_order si está disponible (preserva el orden de selección)
            room_order = item_data.get(
                "room_order", 999999
            )  # Default alto para items sin order
            sorted_room_items_for_reservations.append((room_order, item_data))

        # Ordenar por room_order para mantener el orden de selección original
        sorted_room_items_for_reservations.sort(key=lambda x: x[0])

        for room_order, item_data in sorted_room_items_for_reservations:

            try:
                # Usar select_for_update para lock en la transacción y evitar condiciones de carrera
                room = HotelRoom.objects.select_for_update().get(
                    id=item_data.get("room_id")
                )
                check_in = datetime.strptime(
                    item_data.get("check_in"), "%Y-%m-%d"
                ).date()
                check_out = datetime.strptime(
                    item_data.get("check_out"), "%Y-%m-%d"
                ).date()
            except Exception:
                continue

            # Validar que la habitación esté disponible
            if not room.is_available:
                continue

            # Validar stock disponible: contar reservas activas en esas fechas vs stock total
            # El stock representa cuántas habitaciones físicas hay de ese tipo
            # Si stock es None o 0, se asume que no hay límite de disponibilidad
            if room.stock is not None and room.stock > 0:
                active_reservations_count = room.reservations.filter(
                    check_in__lt=check_out,
                    check_out__gt=check_in,
                    status__in=["pending", "confirmed", "checked_in"],
                ).count()

                # Si ya hay reservas >= stock, no hay disponibilidad
                if active_reservations_count >= room.stock:
                    # No hay habitaciones disponibles de este tipo en esas fechas
                    continue

            # Extraer información de huéspedes adicionales
            notes_text = item_data.get("notes", "") or ""
            additional_guest_names = ""
            additional_guest_details_json = []
            clean_notes = (
                f"Reserva pagada vía Stripe session {checkout.stripe_session_id}"
            )

            # Priorizar additional_guest_details (datos completos) desde item_data (Vue payload)
            # IMPORTANTE: Mantener el orden de los huéspedes como fueron asignados
            additional_guest_details_list = item_data.get(
                "additional_guest_details", []
            )
            if (
                isinstance(additional_guest_details_list, list)
                and additional_guest_details_list
            ):
                # Si tenemos datos completos, usarlos EN EL MISMO ORDEN que fueron asignados
                # Preservar el orden de la lista original
                additional_guest_details_json = additional_guest_details_list
                additional_guest_names = "\n".join(
                    [
                        g.get("name", "")
                        for g in additional_guest_details_list
                        if g.get("name", "").strip()
                    ]
                )
            # Fallback: usar additional_guest_names (solo nombres)
            elif item_data.get("additional_guest_names"):
                additional_guest_names_list = item_data.get(
                    "additional_guest_names", []
                )
                if (
                    isinstance(additional_guest_names_list, list)
                    and additional_guest_names_list
                ):
                    # Si tenemos una lista directa de nombres, usarla
                    additional_guest_names = "\n".join(
                        [
                            name
                            for name in additional_guest_names_list
                            if name and name.strip()
                        ]
                    )
                    # Crear JSON básico con la información disponible (solo nombres, sin tipo ni fecha)
                    additional_guest_details_json = [
                        {
                            "name": name.strip(),
                            "type": "adult",
                            "birth_date": "",
                            "email": "",
                        }
                        for name in additional_guest_names_list
                        if name and name.strip()
                    ]
            # Si las notas contienen información de jugadores/huéspedes, extraerla (fallback para código legacy)
            elif (
                "Selected players/children:" in notes_text
                or "Additional adults:" in notes_text
                or "Additional children:" in notes_text
            ):
                # Parsear la información de las notas
                import re

                guest_names_list = []

                # Extraer nombres de "Selected players/children:"
                players_match = re.search(
                    r"Selected players/children:\s*([^|]+)", notes_text
                )
                if players_match:
                    players_str = players_match.group(1).strip()
                    # Dividir por comas o "|" si hay múltiples jugadores
                    player_names = [
                        p.strip() for p in re.split(r"[,|]", players_str) if p.strip()
                    ]
                    guest_names_list.extend(player_names)

                # Extraer nombres de "Additional adults:"
                adults_match = re.search(r"Additional adults:\s*([^|]+)", notes_text)
                if adults_match:
                    adults_str = adults_match.group(1).strip()
                    # Extraer solo el nombre (antes del paréntesis con fecha)
                    adult_names = re.findall(r"([^(|]+?)(?:\s*\([^)]+\))?", adults_str)
                    guest_names_list.extend(
                        [a.strip() for a in adult_names if a.strip()]
                    )

                # Extraer nombres de "Additional children:"
                children_match = re.search(
                    r"Additional children:\s*([^|]+)", notes_text
                )
                if children_match:
                    children_str = children_match.group(1).strip()
                    # Extraer solo el nombre (antes del paréntesis con fecha)
                    child_names = re.findall(
                        r"([^(|]+?)(?:\s*\([^)]+\))?", children_str
                    )
                    guest_names_list.extend(
                        [c.strip() for c in child_names if c.strip()]
                    )

                if guest_names_list:
                    additional_guest_names = "\n".join(guest_names_list)
                    # Crear JSON básico con la información disponible (solo nombres, sin tipo ni fecha)
                    additional_guest_details_json = [
                        {
                            "name": name.strip(),
                            "type": "adult",
                            "birth_date": "",
                            "email": "",
                        }
                        for name in guest_names_list
                        if name and name.strip()
                    ]
                    # Limpiar las notas para que solo contengan la información del pago
                    clean_notes = f"Reserva pagada vía Stripe session {checkout.stripe_session_id}"

            # Construir texto mejorado para additional_guest_names que incluya fecha de nacimiento si está disponible
            additional_guest_names_text = additional_guest_names
            if additional_guest_details_json:
                # Formato: "Nombre (YYYY-MM-DD)" si hay fecha de nacimiento
                names_with_dates = []
                for guest_detail in additional_guest_details_json:
                    name = guest_detail.get("name", "").strip()
                    if name:
                        birth_date = guest_detail.get("birth_date", "").strip()
                        if birth_date:
                            names_with_dates.append(f"{name} ({birth_date})")
                        else:
                            names_with_dates.append(name)
                if names_with_dates:
                    additional_guest_names_text = "\n".join(names_with_dates)

            # Crear la reserva (la relación con order se asignará después)
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
                notes=clean_notes,
                additional_guest_names=(
                    additional_guest_names_text if additional_guest_names_text else ""
                ),
                additional_guest_details_json=(
                    additional_guest_details_json
                    if additional_guest_details_json
                    else []
                ),
            )

            # Guardar la reserva para actualizarla después con la orden
            reservations_to_update.append(reservation)

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

            # Descontar stock de la habitación SOLO cuando el pago es exitoso y la reserva está confirmada
            # (lock para evitar condiciones de carrera)
            # Solo descontar si el stock es mayor a 0
            # IMPORTANTE: Este código solo se ejecuta después de un pago exitoso de Stripe
            if (
                reservation.status == "confirmed"
                and room.stock is not None
                and room.stock > 0
            ):
                room.stock -= 1
                room.save(update_fields=["stock"])

        checkout.status = "paid"
        checkout.paid_at = timezone.now()
        checkout.save(update_fields=["status", "paid_at", "updated_at"])

        # Crear Order para esta transacción
        order = _create_order_from_stripe_checkout(checkout)

        # Actualizar las reservas para asignar la relación con la orden
        if order and reservations_to_update:
            for reservation in reservations_to_update:
                reservation.order = order
                reservation.save(update_fields=["order"])


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

    stripe_account = (
        event.stripe_payment_profile
        if getattr(event, "stripe_payment_profile", None)
        else None
    )

    try:
        sub = stripe.Subscription.retrieve(
            subscription_id, stripe_account=stripe_account
        )
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
    stripe_account = (
        event.stripe_payment_profile
        if getattr(event, "stripe_payment_profile", None)
        else None
    )

    try:
        session = stripe.checkout.Session.retrieve(
            session_id, stripe_account=stripe_account
        )
    except Exception as e:
        messages.error(
            request, _("Could not verify payment: %(error)s") % {"error": str(e)}
        )
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
        schedule_id = _ensure_plan_subscription_schedule(
            checkout.event, str(subscription_id), int(checkout.plan_months or 1)
        )
        if schedule_id and not checkout.stripe_subscription_schedule_id:
            checkout.stripe_subscription_schedule_id = schedule_id

    checkout.save(
        update_fields=[
            "stripe_subscription_id",
            "stripe_subscription_schedule_id",
            "updated_at",
        ]
    )

    _finalize_stripe_event_checkout(checkout)

    # Clear live session cart (UX)
    request.session["hotel_cart"] = {}
    request.session.modified = True

    messages.success(request, _("Payment completed. Registration confirmed."))
    # Redirigir a la página de confirmación
    return redirect("accounts:payment_confirmation", pk=checkout.pk)


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
                if (
                    checkout.payment_mode == "plan"
                    and subscription_id
                    and not checkout.stripe_subscription_schedule_id
                ):
                    schedule_id = _ensure_plan_subscription_schedule(
                        checkout.event,
                        str(subscription_id),
                        int(checkout.plan_months or 1),
                    )
                    if schedule_id:
                        checkout.stripe_subscription_schedule_id = schedule_id
                checkout.save(
                    update_fields=[
                        "stripe_subscription_id",
                        "stripe_subscription_schedule_id",
                        "updated_at",
                    ]
                )
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
def events_blocked_view(request, *args, **kwargs):
    """Vista temporal para bloquear acceso a eventos desde accounts"""
    messages.error(request, _("Access to events is temporarily blocked."))
    return redirect("panel")


@login_required
@require_POST
def approve_age_verification(request, pk):
    """Vista para aprobar o rechazar verificación de edad de un jugador"""
    from django.utils import timezone

    player = get_object_or_404(Player, pk=pk)
    user = request.user

    # Verificar permisos: SOLO staff o superuser pueden aprobar verificaciones
    if not (user.is_staff or user.is_superuser):
        messages.error(
            request, _("Solo el staff puede aprobar verificaciones de edad.")
        )
        return redirect("accounts:age_verification_list")

    action = request.POST.get("action")  # "approve" or "reject"
    notes = request.POST.get("notes", "")

    if action == "approve":
        player.age_verification_status = "approved"
        player.age_verification_approved_date = timezone.now().date()
        if notes:
            player.age_verification_notes = notes
        player.save()
        messages.success(
            request,
            _("Age verification approved for player %(name)s.")
            % {"name": player.user.get_full_name() or player.user.username},
        )
    elif action == "reject":
        player.age_verification_status = "rejected"
        if notes:
            player.age_verification_notes = notes
        player.save()
        messages.warning(
            request,
            _("Age verification rejected for player %(name)s.")
            % {"name": player.user.get_full_name() or player.user.username},
        )
    else:
        messages.error(request, _("Invalid action."))

    # Redirigir a la lista de verificaciones en el dashboard admin
    return redirect("accounts:age_verification_list")


@login_required
@require_POST
def events_blocked_view(request, *args, **kwargs):
    """Vista temporal para bloquear acceso a eventos desde accounts"""
    messages.error(request, _("Access to events is temporarily blocked."))
    return redirect("panel")


@login_required
@require_POST
def wallet_add_funds(request):
    """Wallet top-ups are disabled."""
    messages.error(request, _("Add Funds is currently disabled."))
    return redirect("panel")


@method_decorator(xframe_options_exempt, name="dispatch")
class StripeInvoiceView(LoginRequiredMixin, DetailView):
    """Vista para mostrar el invoice/factura de un pago de Stripe."""

    model = StripeEventCheckout
    template_name = "accounts/panel_tabs/invoice.html"
    context_object_name = "checkout"

    def get_queryset(self):
        """Solo permitir ver invoices del usuario actual."""
        return StripeEventCheckout.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        checkout = self.object

        # Obtener jugadores relacionados
        from .models import PlayerParent

        player_ids = checkout.player_ids or []
        player_parents = PlayerParent.objects.filter(
            parent=checkout.user, player_id__in=player_ids
        ).select_related("player", "player__user")

        players = [pp.player for pp in player_parents]

        # Obtener reservas de hotel relacionadas
        from apps.locations.models import HotelReservation

        reservations = HotelReservation.objects.filter(
            user=checkout.user,
            notes__icontains=checkout.stripe_session_id,
        ).select_related("hotel", "room")

        # Parsear breakdown para mostrar detalles
        breakdown = checkout.breakdown or {}
        hotel_cart = checkout.hotel_cart_snapshot or {}

        # Calcular valores faltantes del breakdown
        from decimal import Decimal

        # Calcular players_count y price_per_player
        # Usar el count de player_ids si está disponible, sino usar len(players)
        player_ids = checkout.player_ids or []
        players_count = len(player_ids) if player_ids else len(players)

        players_total = Decimal(str(breakdown.get("players_total", "0.00")))
        price_per_player = (
            players_total / Decimal(str(players_count))
            if players_count > 0 and players_total > 0
            else Decimal("0.00")
        )

        # Calcular discount_amount
        subtotal = Decimal(str(breakdown.get("subtotal", "0.00")))
        discount_percent = breakdown.get("discount_percent", 0)
        discount_amount = (
            subtotal * Decimal(str(discount_percent)) / Decimal("100")
            if discount_percent > 0
            else Decimal("0.00")
        )

        # Agregar valores calculados al breakdown para el template
        breakdown["players_count"] = players_count
        breakdown["price_per_player"] = str(price_per_player.quantize(Decimal("0.01")))
        breakdown["discount_amount"] = str(discount_amount.quantize(Decimal("0.01")))

        context.update(
            {
                "players": players,
                "reservations": reservations,
                "breakdown": breakdown,
                "hotel_cart": hotel_cart,
            }
        )

        return context


@method_decorator(xframe_options_exempt, name="dispatch")
class PaymentConfirmationView(LoginRequiredMixin, DetailView):
    """Vista para mostrar la confirmación de pago exitoso."""

    model = StripeEventCheckout
    template_name = "accounts/panel_tabs/payment_confirmation.html"
    context_object_name = "checkout"

    def get_queryset(self):
        """Solo permitir ver confirmaciones del usuario actual y que estén pagadas."""
        return StripeEventCheckout.objects.filter(user=self.request.user, status="paid")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        checkout = self.object

        # Obtener jugadores relacionados
        from .models import PlayerParent

        player_ids = checkout.player_ids or []
        player_parents = PlayerParent.objects.filter(
            parent=checkout.user, player_id__in=player_ids
        ).select_related("player", "player__user")

        players = [pp.player for pp in player_parents]

        # Obtener reservas de hotel relacionadas
        from apps.locations.models import HotelReservation

        reservations = HotelReservation.objects.filter(
            user=checkout.user,
            notes__icontains=checkout.stripe_session_id,
        ).select_related("hotel", "room")

        # Parsear breakdown para mostrar detalles
        breakdown = checkout.breakdown or {}

        context.update(
            {
                "players": players,
                "reservations": reservations,
                "breakdown": breakdown,
            }
        )

        return context


@login_required
def serve_age_verification_document(request, player_id):
    """Serve age verification documents privately, checking permissions."""
    player = get_object_or_404(Player, pk=player_id)
    user = request.user

    # Permissions:
    # 1. Owner of the player (parent or self)
    # 2. Staff / Superuser
    # 3. Team Manager of the player's team
    is_owner = (player.user == user) or (
        hasattr(user, "profile")
        and user.profile.is_parent
        and PlayerParent.objects.filter(parent=user, player=player).exists()
    )
    is_staff = user.is_staff or user.is_superuser
    is_manager = player.team and player.team.manager == user

    if not (is_owner or is_staff or is_manager):
        raise PermissionDenied(_("You do not have permission to view this document."))

    if not player.age_verification_document:
        raise Http404(_("No document uploaded."))

    try:
        return FileResponse(player.age_verification_document.open())
    except Exception as e:
        raise Http404(_("Error opening document: %(error)s") % {"error": str(e)})


@login_required
def forbidden_media(request, *args, **kwargs):
    """Bloquea acceso directo a carpetas sensibles de media."""
    raise PermissionDenied(_("Direct access to this folder is forbidden."))
