"""
Vistas privadas - Requieren autenticación
"""

import json
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q, Sum
from django.db.utils import NotSupportedError
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
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
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
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
    Notification,
    Order,
    Player,
    PlayerParent,
    PushSubscription,
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

        # Si el usuario tiene relación PlayerParent pero su perfil quedó como "player" o "spectator",
        # corregirlo para que el panel muestre las tabs correctas.
        has_children_relation = PlayerParent.objects.filter(parent=user).exists()
        if profile.user_type in ("player", "spectator") and has_children_relation:
            profile.user_type = "parent"
            profile.save(update_fields=["user_type"])

        context["profile"] = profile
        context["is_parent_user"] = profile.is_parent or has_children_relation

        # Pending registrations (unpaid): used as badge counter in /panel/?tab=registros
        try:
            context["pending_registrations_count"] = Order.objects.filter(
                user=user, status="pending_registration"
            ).count()
        except Exception:
            context["pending_registrations_count"] = 0

        # Active tab: allow opening a tab directly via /panel/?tab=<id>
        # (Panel JS also reads this param, but we set it server-side as a reliable fallback.)
        tab_param = (self.request.GET.get("tab") or "").strip()
        if tab_param:
            # Whitelist known tabs (and enforce role restrictions)
            spectator_tabs = {"eventos", "reservas", "plan-pagos"}
            default_tabs = {
                "inicio",
                "eventos",
                "registros",
                "reservas",
                "plan-pagos",
                "perfil",
                "detalle-eventos",  # internal tab (opened from events)
                "crear-equipo",
                "registrar-jugador",
                "mis-equipos",
                "ver-jugadores",
                "registrar-hijo",
                "mis-hijos",
                "mi-perfil",
                "perfil-publico",
            }

            allowed = spectator_tabs if profile.is_spectator else default_tabs
            if tab_param in allowed:
                context["active_tab"] = tab_param

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

            context["parent_player_form"] = ParentPlayerRegistrationForm(
                parent=user, prefix="child"
            )
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
        from .forms import (
            BillingAddressForm,
            CustomPasswordChangeForm,
            NotificationPreferencesForm,
            UserProfileForm,
            UserProfileUpdateForm,
        )

        context["profile_form"] = UserProfileForm(instance=profile, prefix="profile")
        context["user_form"] = UserProfileUpdateForm(instance=user, prefix="profile")
        context["billing_form"] = BillingAddressForm(instance=profile, prefix="billing")
        context["password_form"] = CustomPasswordChangeForm(
            user=user, prefix="security"
        )

        # Cargar preferencias de notificación
        initial_notifications = {
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
            initial=initial_notifications
        )

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
                request.POST,
                request.FILES,
                instance=request.user.profile,
                prefix="profile",
            )
            user_form = UserProfileUpdateForm(
                request.POST, instance=request.user, prefix="profile"
            )

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
                if request.GET.get("next") == "panel":
                    return redirect(
                        reverse("panel") + "?tab=perfil&profile_section=profile"
                    )
                return redirect(reverse("accounts:profile") + "?section=profile")
        elif section == "billing":
            billing_form = BillingAddressForm(
                request.POST, instance=request.user.profile, prefix="billing"
            )
            if billing_form.is_valid():
                billing_form.save()
                messages.success(request, _("Billing address updated successfully."))
                if request.GET.get("next") == "panel":
                    return redirect(
                        reverse("panel") + "?tab=perfil&profile_section=billing"
                    )
                return redirect(reverse("accounts:profile") + "?section=billing")
        elif section == "security":
            password_form = CustomPasswordChangeForm(
                user=request.user, data=request.POST, prefix="security"
            )
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Important!
                messages.success(request, _("Password changed successfully."))
                if request.GET.get("next") == "panel":
                    return redirect(
                        reverse("panel") + "?tab=perfil&profile_section=security"
                    )
                return redirect(reverse("accounts:profile") + "?section=security")
        elif section == "notifications":
            notification_form = NotificationPreferencesForm(request.POST)
            if notification_form.is_valid():
                profile = request.user.profile
                profile.email_notifications = notification_form.cleaned_data.get(
                    "email_notifications", True
                )
                profile.event_notifications = notification_form.cleaned_data.get(
                    "event_notifications", True
                )
                profile.reservation_notifications = notification_form.cleaned_data.get(
                    "reservation_notifications", True
                )
                profile.marketing_notifications = notification_form.cleaned_data.get(
                    "marketing_notifications", False
                )
                profile.save()

                messages.success(
                    request, _("Notification preferences saved successfully.")
                )
                if request.GET.get("next") == "panel":
                    return redirect(
                        reverse("panel") + "?tab=perfil&profile_section=notifications"
                    )
                return redirect(reverse("accounts:profile") + "?section=notifications")

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

        context["divisions"] = Division.objects.filter(is_active=True).order_by("name")

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


class AdminPlayerDetailView(StaffRequiredMixin, DetailView):
    model = Player
    template_name = "accounts/admin/player_admin_detail.html"
    context_object_name = "player_obj"

    def get_queryset(self):
        return Player.objects.select_related(
            "user",
            "user__profile",
            "team",
            "division",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        player_obj = context["player_obj"]

        profile = getattr(player_obj.user, "profile", None)

        age_as_of_april_30 = None
        age_division = None
        grade_division = None
        eligible_divisions = []
        is_eligible = None
        eligible_message = ""
        try:
            age_as_of_april_30 = player_obj.calculate_age_as_of_april_30()
            age_division = player_obj.get_age_based_division()
            grade_division = player_obj.get_grade_based_division()
            eligible_divisions = player_obj.get_eligible_divisions()
            is_eligible, eligible_message = player_obj.is_eligible_to_play()
        except Exception:
            age_as_of_april_30 = None
            age_division = None
            grade_division = None
            eligible_divisions = []
            is_eligible = None
            eligible_message = ""

        parent_relations = (
            PlayerParent.objects.filter(player=player_obj)
            .select_related("parent", "parent__profile")
            .order_by("-created_at")
        )

        try:
            related_orders = list(
                Order.objects.filter(registered_player_ids__contains=[player_obj.pk])
                .select_related("event", "stripe_checkout", "user")
                .order_by("-created_at")[:50]
            )

            related_payment_plan_orders = list(
                Order.objects.filter(
                    registered_player_ids__contains=[player_obj.pk], payment_mode="plan"
                )
                .select_related("event", "stripe_checkout", "user")
                .order_by("-created_at")[:50]
            )

            related_active_payment_plan_orders = list(
                Order.objects.filter(
                    registered_player_ids__contains=[player_obj.pk], payment_mode="plan"
                )
                .filter(
                    Q(plan_payments_remaining__gt=0) | ~Q(stripe_subscription_id="")
                )
                .select_related("event", "stripe_checkout", "user")
                .order_by("-created_at")[:50]
            )
        except NotSupportedError:
            recent_orders = Order.objects.select_related(
                "event", "stripe_checkout", "user"
            ).order_by("-created_at")[:1000]
            related_orders = [
                o
                for o in recent_orders
                if player_obj.pk in (getattr(o, "registered_player_ids", None) or [])
            ][:50]
            related_payment_plan_orders = [
                o for o in related_orders if getattr(o, "payment_mode", "") == "plan"
            ]
            related_active_payment_plan_orders = [
                o
                for o in related_payment_plan_orders
                if (getattr(o, "plan_payments_remaining", 0) or 0) > 0
                or bool(getattr(o, "stripe_subscription_id", ""))
            ]

        try:
            related_checkouts = list(
                StripeEventCheckout.objects.filter(player_ids__contains=[player_obj.pk])
                .select_related("event", "user")
                .order_by("-created_at")[:50]
            )

            related_plan_checkouts = list(
                StripeEventCheckout.objects.filter(
                    player_ids__contains=[player_obj.pk], payment_mode="plan"
                )
                .select_related("event", "user")
                .order_by("-created_at")[:50]
            )

            related_active_plan_checkouts = list(
                StripeEventCheckout.objects.filter(
                    player_ids__contains=[player_obj.pk], payment_mode="plan"
                )
                .filter(~Q(stripe_subscription_id=""))
                .select_related("event", "user")
                .order_by("-created_at")[:50]
            )
        except NotSupportedError:
            recent_checkouts = StripeEventCheckout.objects.select_related(
                "event", "user"
            ).order_by("-created_at")[:1000]
            related_checkouts = [
                co
                for co in recent_checkouts
                if player_obj.pk in (getattr(co, "player_ids", None) or [])
            ][:50]
            related_plan_checkouts = [
                co
                for co in related_checkouts
                if getattr(co, "payment_mode", "") == "plan"
            ]
            related_active_plan_checkouts = [
                co
                for co in related_plan_checkouts
                if bool(getattr(co, "stripe_subscription_id", ""))
            ]

        from apps.events.models import EventAttendance

        attended_events = (
            EventAttendance.objects.filter(user=player_obj.user)
            .select_related("event")
            .order_by("-registered_at")[:50]
        )

        notifications = (
            Notification.objects.filter(user=player_obj.user)
            .select_related("order", "event")
            .order_by("-created_at")[:50]
        )

        push_subscriptions = PushSubscription.objects.filter(
            user=player_obj.user
        ).order_by("-created_at")

        wallet = None
        try:
            from .models import UserWallet

            wallet = getattr(player_obj.user, "wallet", None)
            if wallet is None:
                wallet = UserWallet.objects.filter(user=player_obj.user).first()
        except Exception:
            wallet = None

        context["parent_relations"] = parent_relations
        context["profile"] = profile
        context["age_as_of_april_30"] = age_as_of_april_30
        context["age_division"] = age_division
        context["grade_division"] = grade_division
        context["eligible_divisions"] = eligible_divisions
        context["is_eligible"] = is_eligible
        context["eligible_message"] = eligible_message
        context["related_orders"] = related_orders
        context["related_payment_plan_orders"] = related_payment_plan_orders
        context["related_active_payment_plan_orders"] = (
            related_active_payment_plan_orders
        )
        context["related_checkouts"] = related_checkouts
        context["related_plan_checkouts"] = related_plan_checkouts
        context["related_active_plan_checkouts"] = related_active_plan_checkouts
        context["attended_events"] = attended_events
        context["notifications"] = notifications
        context["push_subscriptions"] = push_subscriptions
        context["wallet"] = wallet

        context["active_section"] = "players"
        context["active_subsection"] = "player_admin_detail"
        return context


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


class PlayerDeleteView(UserPassesTestMixin, DeleteView):
    model = Player
    template_name = "accounts/player_confirm_delete.html"
    context_object_name = "player"
    success_url = reverse_lazy("accounts:player_list")

    def test_func(self):
        user = self.request.user
        return bool(
            user and user.is_authenticated and (user.is_staff or user.is_superuser)
        )


class ParentPlayerRegistrationView(LoginRequiredMixin, CreateView):
    """Vista para que padres registren jugadores"""

    model = Player
    form_class = ParentPlayerRegistrationForm
    template_name = "accounts/parent_player_register.html"
    success_url = reverse_lazy("panel")
    prefix = "child"

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


class AdminUserDetailView(SuperuserRequiredMixin, DetailView):
    model = User
    template_name = "accounts/admin/user_admin_detail.html"
    context_object_name = "user_obj"

    def get_queryset(self):
        return User.objects.select_related("profile")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_obj = context["user_obj"]

        # Wallet + last transactions
        wallet = None
        wallet_transactions = []
        try:
            from .models import UserWallet

            wallet = getattr(user_obj, "wallet", None)
            if wallet is None:
                wallet = UserWallet.objects.filter(user=user_obj).first()
            if wallet is not None:
                wallet_transactions = list(
                    wallet.transactions.all().order_by("-created_at", "-id")[:50]
                )
        except Exception:
            wallet = None
            wallet_transactions = []

        # Orders
        orders = (
            Order.objects.filter(user=user_obj)
            .select_related("event", "stripe_checkout")
            .order_by("-created_at")[:50]
        )

        # Payment plans (Orders + Stripe checkouts)
        payment_plan_orders = (
            Order.objects.filter(user=user_obj, payment_mode="plan")
            .select_related("event", "stripe_checkout")
            .order_by("-created_at")[:50]
        )
        active_payment_plan_orders = (
            Order.objects.filter(user=user_obj, payment_mode="plan")
            .filter(Q(plan_payments_remaining__gt=0) | ~Q(stripe_subscription_id=""))
            .select_related("event", "stripe_checkout")
            .order_by("-created_at")[:50]
        )

        # Stripe checkouts
        stripe_checkouts = (
            StripeEventCheckout.objects.filter(user=user_obj)
            .select_related("event")
            .order_by("-created_at")[:50]
        )

        payment_plan_checkouts = (
            StripeEventCheckout.objects.filter(user=user_obj, payment_mode="plan")
            .select_related("event")
            .order_by("-created_at")[:50]
        )
        active_payment_plan_checkouts = (
            StripeEventCheckout.objects.filter(user=user_obj, payment_mode="plan")
            .filter(~Q(stripe_subscription_id=""))
            .select_related("event")
            .order_by("-created_at")[:50]
        )

        # Notifications
        notifications = (
            Notification.objects.filter(user=user_obj)
            .select_related("order", "event")
            .order_by("-created_at")[:50]
        )

        # Push subscriptions
        push_subscriptions = PushSubscription.objects.filter(user=user_obj).order_by(
            "-created_at"
        )

        # Teams managed + players on those teams
        managed_teams = user_obj.managed_teams.all().prefetch_related("players")

        managed_team_players = (
            Player.objects.filter(team__manager=user_obj)
            .select_related("user", "user__profile", "team", "division")
            .order_by("-created_at")
        )

        # Player profile
        player_profile = getattr(user_obj, "player_profile", None)

        # Parent/children relationships
        children_relations = (
            PlayerParent.objects.filter(parent=user_obj)
            .select_related(
                "player",
                "player__team",
                "player__user",
                "player__user__profile",
            )
            .order_by("-created_at")
        )

        parent_relations = PlayerParent.objects.none()
        if player_profile is not None:
            parent_relations = (
                PlayerParent.objects.filter(player=player_profile)
                .select_related("parent", "parent__profile")
                .order_by("-created_at")
            )

        # Events (if events app is installed)
        organized_events = []
        attended_events = []
        try:
            from apps.events.models import Event, EventAttendance

            organized_events = list(
                Event.objects.filter(organizer=user_obj).order_by("-start_date")[:50]
            )
            attended_events = list(
                EventAttendance.objects.filter(user=user_obj)
                .select_related("event")
                .order_by("-registered_at")[:50]
            )
        except Exception:
            organized_events = []
            attended_events = []

        # Staff wallet top-ups (if applicable)
        staff_wallet_topups = []
        try:
            staff_wallet_topups = list(
                user_obj.staff_wallet_topups.all()
                .select_related("created_by")
                .order_by("-created_at")[:50]
            )
        except Exception:
            staff_wallet_topups = []

        context["wallet"] = wallet
        context["wallet_transactions"] = wallet_transactions
        context["orders"] = orders
        context["payment_plan_orders"] = payment_plan_orders
        context["active_payment_plan_orders"] = active_payment_plan_orders
        context["stripe_checkouts"] = stripe_checkouts
        context["payment_plan_checkouts"] = payment_plan_checkouts
        context["active_payment_plan_checkouts"] = active_payment_plan_checkouts
        context["notifications"] = notifications
        context["push_subscriptions"] = push_subscriptions
        context["managed_teams"] = managed_teams
        context["managed_team_players"] = managed_team_players
        context["player_profile"] = player_profile
        context["children_relations"] = children_relations
        context["parent_relations"] = parent_relations
        context["organized_events"] = organized_events
        context["attended_events"] = attended_events
        context["staff_wallet_topups"] = staff_wallet_topups

        context["active_section"] = "users"
        context["active_subsection"] = "user_admin_detail"
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

            # Verificar si el usuario es espectador
            context["is_spectator"] = (
                hasattr(user, "profile") and user.profile.is_spectator
            )

            # Obtener servicios adicionales del evento (en lugar del hotel)
            from apps.events.models import EventService

            context["event_services"] = EventService.objects.filter(
                event=event, is_active=True
            ).order_by("order", "service_name")

            # Obtener los hijos/jugadores del usuario
            children = []
            if hasattr(user, "profile") and user.profile.is_parent:
                # Obtener jugadores relacionados a través de PlayerParent
                from .models import PlayerParent

                player_parents = PlayerParent.objects.filter(
                    parent=user
                ).select_related(
                    "player",
                    "player__user",
                    "player__user__profile",
                    "player__division",
                )

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
                    event_division_ids = set(
                        event_divisions.values_list("id", flat=True)
                    )

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
                context["ineligible_player_ids"] = (
                    ineligible_player_ids if ineligible_player_ids else set()
                )
                context["has_ineligible_children"] = len(ineligible_player_ids) > 0

            context["children"] = children

            # Verificar si ya hay registros para este evento
            registered_players = []
            # IMPORTANT: treat a player as "registered" (locked) ONLY if the registration is PAID.
            # If a player has a pending/unpaid checkout, the user must be able to edit the checkout.
            try:
                from apps.events.models import EventAttendance

                paid_player_ids = set()

                # 1) Paid Orders (source of truth for panel payment state)
                for o in (
                    Order.objects.filter(event=event, status="paid")
                    .only("registered_player_ids")
                    .iterator()
                ):
                    for pid in o.registered_player_ids or []:
                        try:
                            paid_player_ids.add(int(pid))
                        except Exception:
                            continue

                # 2) Paid Stripe checkouts (fallback)
                for co in (
                    StripeEventCheckout.objects.filter(event=event, status="paid")
                    .only("player_ids")
                    .iterator()
                ):
                    for pid in co.player_ids or []:
                        try:
                            paid_player_ids.add(int(pid))
                        except Exception:
                            continue

                attendance_user_ids = set(
                    EventAttendance.objects.filter(
                        event=event,
                        status__in=["pending", "confirmed", "waiting"],
                    ).values_list("user_id", flat=True)
                )

                for child in children:
                    if child.pk in paid_player_ids:
                        registered_players.append(child.pk)
                        continue
                    if getattr(child, "user_id", None) in attendance_user_ids:
                        registered_players.append(child.pk)
            except Exception:
                registered_players = []

            context["registered_players"] = registered_players

        except Event.DoesNotExist:
            context["event"] = None
            messages.error(self.request, _("Event not found."))
        except ImportError:
            context["event"] = None
            messages.error(self.request, _("Events app is not available."))

        # Get user wallet balance (available balance = balance - pending)
        try:
            from .models import UserWallet

            wallet, _created = UserWallet.objects.get_or_create(user=user)
            context["wallet_balance"] = wallet.available_balance  # Balance disponible
            context["wallet_balance_total"] = wallet.balance  # Balance total
            context["wallet_balance_pending"] = (
                wallet.pending_balance
            )  # Balance reservado
        except Exception:
            context["wallet_balance"] = Decimal("0.00")
            context["wallet_balance_total"] = Decimal("0.00")
            context["wallet_balance_pending"] = Decimal("0.00")

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

    for room_key, item_data in (cart or {}).items():
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


@login_required
def get_event_services(request, event_id):
    """API para obtener servicios adicionales disponibles de un evento (wrapper para acceso desde panel)"""
    from apps.events.views import get_event_services as events_get_event_services

    return events_get_event_services(request, event_id)


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
    from apps.events.models import Event, EventAttendance

    event = get_object_or_404(Event, pk=pk)
    user = request.user

    # Verificar si el usuario es espectador
    is_spectator = hasattr(user, "profile") and user.profile.is_spectator

    # Solo padres y espectadores pueden pagar por registros
    if not (hasattr(user, "profile") and (user.profile.is_parent or is_spectator)):
        return JsonResponse(
            {
                "success": False,
                "error": _("Only parents and spectators can pay for registrations."),
            },
            status=403,
        )

    player_ids = request.POST.getlist("players")
    valid_players = []

    # Si NO es espectador, requerir jugadores
    if not is_spectator:
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

        # Bloquear duplicados si el jugador ya tiene asistencia registrada (cualquier estado activo).
        # Esto cubre órdenes legacy sin registered_player_ids.
        player_users = [p.user for p in valid_players if getattr(p, "user", None)]
        if player_users:
            existing_attendance_users = set(
                EventAttendance.objects.filter(
                    event=event,
                    user__in=player_users,
                    status__in=["pending", "confirmed", "waiting"],
                ).values_list("user_id", flat=True)
            )
            if existing_attendance_users:
                already_names = []
                for p in valid_players:
                    if getattr(p, "user_id", None) in existing_attendance_users:
                        already_names.append(p.user.get_full_name() or p.user.username)
                if already_names:
                    return JsonResponse(
                        {
                            "success": False,
                            "error": _(
                                "The following players are already registered for this event: %(players)s"
                            )
                            % {"players": ", ".join(already_names)},
                        },
                        status=400,
                    )

        # Si existe un checkout pendiente (created/registered) para este mismo usuario/evento que ya incluye
        # alguno de los jugadores seleccionados, forzar reanudar en vez de crear otro checkout.
        resume_checkout_id = request.POST.get("resume_checkout_id") or request.POST.get(
            "resume_checkout"
        )
        try:
            requested_player_ids = {int(p.pk) for p in valid_players}
        except Exception:
            requested_player_ids = set()

        if requested_player_ids and not resume_checkout_id:
            pending_checkout = (
                StripeEventCheckout.objects.filter(
                    user=user,
                    event=event,
                    status__in=["created", "registered"],
                )
                .only("id", "player_ids", "status")
                .order_by("-created_at")
                .first()
            )
            if pending_checkout:
                try:
                    pending_ids = {
                        int(pid) for pid in (pending_checkout.player_ids or [])
                    }
                except Exception:
                    pending_ids = set()
                if pending_ids and (pending_ids & requested_player_ids):
                    return JsonResponse(
                        {
                            "success": False,
                            "error": _(
                                "There is already a pending registration for one or more selected players. Please resume the existing checkout."
                            ),
                            "resume_checkout_id": pending_checkout.pk,
                            "resume_checkout": pending_checkout.pk,
                        },
                        status=400,
                    )

        # Bloquear duplicados si ya existe una orden (incluye pending/pending_registration además de paid)
        # que ya contiene alguno de los jugadores.
        if requested_player_ids:
            try:
                order_player_ids = set()
                for o in (
                    Order.objects.filter(
                        event=event,
                        status__in=["paid", "pending", "pending_registration"],
                    )
                    .only("registered_player_ids")
                    .iterator()
                ):
                    for pid in o.registered_player_ids or []:
                        try:
                            order_player_ids.add(int(pid))
                        except Exception:
                            continue
                if order_player_ids & requested_player_ids:
                    dup_names = []
                    for p in valid_players:
                        if p.pk in order_player_ids:
                            dup_names.append(p.user.get_full_name() or p.user.username)
                    if dup_names:
                        return JsonResponse(
                            {
                                "success": False,
                                "error": _(
                                    "The following players already have an order/registration for this event: %(players)s"
                                )
                                % {"players": ", ".join(dup_names)},
                            },
                            status=400,
                        )
            except Exception:
                pass

        # Verificar que ningún jugador ya esté PAGADO para este evento.
        # Si existe un checkout/orden pendiente, debe poder editarse y pagarse (resume flow).
        already_registered = []
        try:
            paid_player_ids = set()

            for o in (
                Order.objects.filter(event=event, status="paid")
                .only("registered_player_ids")
                .iterator()
            ):
                for pid in o.registered_player_ids or []:
                    try:
                        paid_player_ids.add(int(pid))
                    except Exception:
                        continue

            for co in (
                StripeEventCheckout.objects.filter(event=event, status="paid")
                .only("player_ids")
                .iterator()
            ):
                for pid in co.player_ids or []:
                    try:
                        paid_player_ids.add(int(pid))
                    except Exception:
                        continue
        except Exception:
            paid_player_ids = set()

        for player in valid_players:
            if player.pk in paid_player_ids:
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

    # Si es espectador y no hay jugadores ni hotel/adicionales, requerir al menos hotel
    if is_spectator and not player_ids:
        hotel_payload_raw = request.POST.get("hotel_reservation_json") or ""
        cart = request.session.get("hotel_cart", {}) or {}
        if not hotel_payload_raw and not cart:
            return JsonResponse(
                {
                    "success": False,
                    "error": _(
                        "Spectators must select hotel accommodation or additional services."
                    ),
                },
                status=400,
            )

    payment_mode = request.POST.get("payment_mode", "plan")
    if payment_mode not in ("plan", "now", "register_only"):
        payment_mode = "plan"

    # Usar entry_fee específico según el tipo de usuario
    if is_spectator:
        entry_fee = _decimal(
            getattr(event, "default_entry_fee_spectator", None), default="0.00"
        )
    else:
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

    subtotal = (players_total + hotel_total + hotel_buy_out_fee).quantize(
        Decimal("0.01")
    )

    # Service fee: porcentaje del subtotal
    service_fee_percent = _decimal(getattr(event, "service_fee", None), default="0.00")
    service_fee_amount = (subtotal * (service_fee_percent / Decimal("100"))).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    # Aplicar descuento al subtotal + service fee
    total_before_discount = (subtotal + service_fee_amount).quantize(Decimal("0.01"))
    total = (total_before_discount * discount_multiplier).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    # Wallet payment handling
    use_wallet = request.POST.get("use_wallet") == "1"
    wallet_amount_used = Decimal("0.00")
    wallet_deduction = Decimal("0.00")

    if use_wallet:
        try:
            from .models import UserWallet

            wallet, _created = UserWallet.objects.get_or_create(user=user)
            wallet_amount_str = request.POST.get("wallet_amount", "0")
            try:
                wallet_amount_used = Decimal(str(wallet_amount_str))
            except (ValueError, TypeError, InvalidOperation):
                wallet_amount_used = Decimal("0.00")

            # Reserve wallet amount (cannot exceed available balance or total)
            # available_balance = balance - pending_balance
            if (
                wallet_amount_used > 0
                and wallet.available_balance >= wallet_amount_used
            ):
                wallet_deduction = min(wallet_amount_used, total)
                try:
                    wallet.reserve_funds(
                        amount=wallet_deduction,
                        description=f"Reserva para checkout: {event.title}",
                        reference_id=f"event_checkout_pending:{event.pk}",
                    )
                except ValueError as e:
                    # Wallet balance insufficient or error
                    return JsonResponse({"success": False, "error": str(e)}, status=400)
        except Exception as e:
            # If wallet processing fails, continue without wallet
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Wallet processing error: {e}")
            use_wallet = False
            wallet_deduction = Decimal("0.00")

    # Adjust total after wallet deduction
    total_after_wallet = max(Decimal("0.00"), total - wallet_deduction)

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

    plan_months = _plan_months_until_deadline(getattr(event, "payment_deadline", None))
    plan_monthly_amount = Decimal("0.00")

    if payment_mode == "plan":
        # Plan monthly amount should be calculated from total_after_wallet (after wallet deduction)
        plan_monthly_amount = (total_after_wallet / Decimal(str(plan_months))).quantize(
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
            plan_description += f" Includes service fee ({service_fee_percent}%)."

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
    elif payment_mode == "register_only":
        # Register now, pay later: DO NOT create a Stripe session.
        # We create/update a pending StripeEventCheckout + pending Order and redirect to confirmation.
        from uuid import uuid4

        placeholder_session_id = f"manual_{uuid4().hex}"

        resume_checkout_id = request.POST.get("resume_checkout") or request.GET.get(
            "resume_checkout"
        )

        if resume_checkout_id:
            checkout = get_object_or_404(
                StripeEventCheckout, pk=resume_checkout_id, user=user, event=event
            )
            if checkout.status == "paid":
                return JsonResponse(
                    {
                        "success": False,
                        "error": _("This registration is already paid."),
                    },
                    status=400,
                )
            checkout.stripe_session_id = placeholder_session_id
            checkout.payment_mode = "register_only"
            checkout.discount_percent = 0
            checkout.player_ids = [int(p.pk) for p in valid_players]
            checkout.hotel_cart_snapshot = enriched_cart
            checkout.breakdown = {
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
                "discount_percent": 0,
                "wallet_deduction": str(wallet_deduction),
                "total": str(total_after_wallet),
            }
            checkout.amount_total = total_after_wallet
            checkout.plan_months = plan_months
            checkout.plan_monthly_amount = plan_monthly_amount
            checkout.status = "registered"
            checkout.save()
        else:
            checkout = StripeEventCheckout.objects.create(
                user=user,
                event=event,
                stripe_session_id=placeholder_session_id,
                payment_mode="register_only",
                discount_percent=0,
                player_ids=[int(p.pk) for p in valid_players],
                hotel_cart_snapshot=enriched_cart,
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
                    "discount_percent": 0,
                    "wallet_deduction": str(wallet_deduction),
                    "total": str(total_after_wallet),
                },
                amount_total=total_after_wallet,
                plan_months=plan_months,
                plan_monthly_amount=plan_monthly_amount,
                status="registered",
            )

        # Ensure there's a pending order tied to this checkout
        order = (
            Order.objects.filter(user=user, stripe_checkout=checkout)
            .order_by("-created_at")
            .first()
        )
        if not order:
            Order.objects.create(
                user=user,
                stripe_checkout=checkout,
                event=event,
                status="pending_registration",
                payment_method="stripe",
                payment_mode="register_only",
                stripe_session_id="",
                subtotal=subtotal,
                total_amount=total_after_wallet,
                currency=currency,
                breakdown=checkout.breakdown or {},
                registered_player_ids=checkout.player_ids or [],
            )
        else:
            order.payment_mode = "register_only"
            order.stripe_session_id = ""
            order.subtotal = subtotal
            order.total_amount = total_after_wallet
            order.currency = currency
            order.breakdown = checkout.breakdown or {}
            order.registered_player_ids = checkout.player_ids or []
            if order.status != "paid":
                order.status = "pending_registration"
            order.save(
                update_fields=[
                    "payment_mode",
                    "stripe_session_id",
                    "subtotal",
                    "total_amount",
                    "currency",
                    "breakdown",
                    "registered_player_ids",
                    "status",
                    "updated_at",
                ]
            )

        return JsonResponse(
            {
                "success": True,
                "redirect_url": reverse(
                    "accounts:registration_confirmation", kwargs={"pk": checkout.pk}
                ),
            }
        )
    else:
        # Build Stripe line items (pay now)
        # When wallet is used, we need to adjust line_items to sum to total_after_wallet
        line_items = []
        line_items_total = Decimal("0.00")

        if players_total > 0 and players_count > 0:
            item_amount = scale(entry_fee)
            line_items.append(
                {
                    "price_data": {
                        "currency": currency,
                        "product_data": {"name": f"Event registration - {event.title}"},
                        "unit_amount": _money_to_cents(item_amount),
                    },
                    "quantity": players_count,
                }
            )
            line_items_total += item_amount * players_count

        if hotel_total > 0:
            hotel_name = ""
            try:
                hotel_name = event.hotel.hotel_name if event.hotel else ""
            except Exception:
                hotel_name = ""
            item_amount = scale(hotel_total)
            line_items.append(
                {
                    "price_data": {
                        "currency": currency,
                        "product_data": {
                            "name": f"Hotel stay{(' - ' + hotel_name) if hotel_name else ''}"
                        },
                        "unit_amount": _money_to_cents(item_amount),
                    },
                    "quantity": 1,
                }
            )
            line_items_total += item_amount

        if hotel_buy_out_fee > 0:
            item_amount = scale(hotel_buy_out_fee)
            line_items.append(
                {
                    "price_data": {
                        "currency": currency,
                        "product_data": {"name": "Hotel buy out fee"},
                        "unit_amount": _money_to_cents(item_amount),
                    },
                    "quantity": 1,
                }
            )
            line_items_total += item_amount

        if service_fee_amount > 0:
            item_amount = scale(service_fee_amount)
            line_items.append(
                {
                    "price_data": {
                        "currency": currency,
                        "product_data": {
                            "name": f"Service fee ({service_fee_percent}%)"
                        },
                        "unit_amount": _money_to_cents(item_amount),
                    },
                    "quantity": 1,
                }
            )
            line_items_total += item_amount

        # Adjust line_items to match total_after_wallet if wallet was used
        if (
            use_wallet
            and wallet_deduction > 0
            and line_items_total > total_after_wallet
        ):
            # Calculate the exact difference
            difference = line_items_total - total_after_wallet

            if difference > 0 and line_items:
                # Recalculate line_items_total to be exact
                # Adjust items from last to first to distribute the difference
                remaining_diff = difference

                # Start from the last item and work backwards
                for i in range(len(line_items) - 1, -1, -1):
                    if remaining_diff <= 0:
                        break

                    item = line_items[i]
                    if "price_data" in item and "unit_amount" in item["price_data"]:
                        current_amount = Decimal(
                            item["price_data"]["unit_amount"]
                        ) / Decimal("100")
                        quantity = item.get("quantity", 1)
                        item_total = current_amount * quantity

                        # Adjust this item, but don't go below 0.01
                        adjustment = min(
                            remaining_diff, item_total - Decimal("0.01") * quantity
                        )
                        if adjustment > 0:
                            new_item_amount = max(
                                Decimal("0.01"), (item_total - adjustment) / quantity
                            )
                            item["price_data"]["unit_amount"] = _money_to_cents(
                                new_item_amount
                            )
                            remaining_diff -= adjustment

                # Final verification: recalculate total
                recalculated_total = Decimal("0.00")
                for item in line_items:
                    if "price_data" in item and "unit_amount" in item["price_data"]:
                        amount = Decimal(item["price_data"]["unit_amount"]) / Decimal(
                            "100"
                        )
                        quantity = item.get("quantity", 1)
                        recalculated_total += amount * quantity

                # If there's still a small rounding difference, adjust the last item
                final_diff = recalculated_total - total_after_wallet
                if abs(final_diff) > Decimal("0.005") and line_items:
                    last_item = line_items[-1]
                    if (
                        "price_data" in last_item
                        and "unit_amount" in last_item["price_data"]
                    ):
                        current_amount = Decimal(
                            last_item["price_data"]["unit_amount"]
                        ) / Decimal("100")
                        quantity = last_item.get("quantity", 1)
                        adjusted_amount = max(
                            Decimal("0.01"), current_amount - (final_diff / quantity)
                        )
                        last_item["price_data"]["unit_amount"] = _money_to_cents(
                            adjusted_amount
                        )

                # Log the adjustment for debugging
                import logging

                logger = logging.getLogger(__name__)
                final_total = sum(
                    Decimal(item["price_data"]["unit_amount"])
                    / Decimal("100")
                    * item.get("quantity", 1)
                    for item in line_items
                    if "price_data" in item and "unit_amount" in item["price_data"]
                )
                logger.info(
                    f"Wallet adjustment: original_total={line_items_total}, "
                    f"wallet_deduction={wallet_deduction}, "
                    f"target_total={total_after_wallet}, "
                    f"final_total={final_total}"
                )

        if not line_items:
            return JsonResponse(
                {"success": False, "error": _("There is nothing to charge.")},
                status=400,
            )

    # From here on we need Stripe configured (plan / now)
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

    # If resuming an existing pending checkout (from Registrations -> Pay),
    # update it instead of creating a new one so the pending order remains editable.
    resume_checkout_id = request.POST.get("resume_checkout") or request.GET.get(
        "resume_checkout"
    )
    if resume_checkout_id:
        checkout = get_object_or_404(
            StripeEventCheckout, pk=resume_checkout_id, user=user, event=event
        )
        checkout.stripe_session_id = session.id
        checkout.payment_mode = payment_mode
        checkout.discount_percent = discount_percent
        checkout.player_ids = [int(p.pk) for p in valid_players]
        checkout.hotel_cart_snapshot = enriched_cart
        checkout.breakdown = {
            "players": [
                {
                    "id": int(p.pk),
                    "name": (p.user.get_full_name() or p.user.username),
                    "email": (p.user.email or ""),
                }
                for p in (valid_players or [])
                if getattr(p, "user", None)
            ],
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
            "wallet_deduction": str(wallet_deduction),
            "total": str(total_after_wallet),
        }
        checkout.amount_total = total_after_wallet
        checkout.plan_months = plan_months
        checkout.plan_monthly_amount = plan_monthly_amount
        # Keep status as created/registered (do not mark paid here)
        checkout.status = "created"
        checkout.save()

        # Ensure there's a pending order tied to this checkout
        order = (
            Order.objects.filter(user=user, stripe_checkout=checkout)
            .order_by("-created_at")
            .first()
        )
        if not order:
            # Crear orden con status "pending" cuando se redirige a Stripe
            # Si el usuario no completa el pago, se marcará como "abandoned" más tarde
            Order.objects.create(
                user=user,
                stripe_checkout=checkout,
                event=event,
                status="pending",
                payment_method="stripe",
                payment_mode=payment_mode,
                stripe_session_id=session.id,
                subtotal=subtotal,
                total_amount=total_after_wallet,
                currency=currency,
                breakdown=checkout.breakdown or {},
                registered_player_ids=checkout.player_ids or [],
            )
        else:
            order.payment_mode = payment_mode
            order.stripe_session_id = session.id
            order.subtotal = subtotal
            order.total_amount = total_after_wallet
            order.currency = currency
            order.breakdown = checkout.breakdown or {}
            order.registered_player_ids = checkout.player_ids or []
            if order.status != "paid":
                # Actualizar status según el modo de pago
                order.status = (
                    "pending"
                    if payment_mode != "register_only"
                    else "pending_registration"
                )
            order.save(
                update_fields=[
                    "payment_mode",
                    "stripe_session_id",
                    "subtotal",
                    "total_amount",
                    "currency",
                    "breakdown",
                    "registered_player_ids",
                    "status",
                    "updated_at",
                ]
            )
    else:
        StripeEventCheckout.objects.create(
            user=user,
            event=event,
            stripe_session_id=session.id,
            payment_mode=payment_mode,
            discount_percent=discount_percent,
            player_ids=[int(p.pk) for p in valid_players],
            hotel_cart_snapshot=enriched_cart,  # Usar el carrito enriquecido con info de extra guests
            breakdown={
                "players": [
                    {
                        "id": int(p.pk),
                        "name": (p.user.get_full_name() or p.user.username),
                        "email": (p.user.email or ""),
                    }
                    for p in (valid_players or [])
                    if getattr(p, "user", None)
                ],
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
                "wallet_deduction": str(wallet_deduction),
                "total": str(total_after_wallet),
            },
            amount_total=total_after_wallet,
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
    Si ya existe una Order para este checkout, la actualiza a "paid".
    """
    # Verificar si ya existe una Order para este checkout
    existing_order = Order.objects.filter(stripe_checkout=checkout).first()
    if existing_order:
        # Si ya existe, actualizarla a "paid" y actualizar campos importantes
        existing_order.status = "paid"
        existing_order.paid_at = checkout.paid_at or timezone.now()
        existing_order.total_amount = checkout.amount_total
        existing_order.breakdown = checkout.breakdown or {}
        existing_order.registered_player_ids = checkout.player_ids or []
        existing_order.save(
            update_fields=[
                "status",
                "paid_at",
                "total_amount",
                "breakdown",
                "registered_player_ids",
                "updated_at",
            ]
        )
        return existing_order

    # Calcular desglose desde breakdown o desde el checkout
    breakdown = checkout.breakdown or {}
    # Ensure breakdown includes player snapshot for email/admin visibility
    if not (breakdown or {}).get("players"):
        try:
            player_ids = [int(pid) for pid in (checkout.player_ids or [])]
        except Exception:
            player_ids = []
        if player_ids:
            try:
                from apps.accounts.models import Player

                players_qs = Player.objects.filter(
                    id__in=player_ids, is_active=True
                ).select_related("user")
                breakdown["players"] = [
                    {
                        "id": int(p.pk),
                        "name": (p.user.get_full_name() or p.user.username),
                        "email": (p.user.email or ""),
                    }
                    for p in players_qs
                    if getattr(p, "user", None)
                ]
            except Exception:
                pass
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
        hotel_buy_out_fee = breakdown_data.get(
            "hotel_buy_out_fee"
        ) or breakdown_data.get("no_show_fee", Decimal("0.00"))
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
            hotel_buy_out_fee = (
                Decimal(str(hotel_buy_out_fee))
                if hotel_buy_out_fee
                else Decimal("0.00")
            )
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

    # StripeEventCheckout ya no guarda currency (fue removido en migración 0044),
    # así que usamos la moneda configurada del sistema.
    from django.conf import settings

    currency = (getattr(settings, "STRIPE_CURRENCY", "usd") or "usd").lower()

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
        currency=currency,
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
            attendance, _created = EventAttendance.objects.get_or_create(
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

        # Crear Order para esta transacción ANTES de marcar como paid
        # Si falla la creación de la Order, el checkout no se marca como paid
        try:
            order = _create_order_from_stripe_checkout(checkout)
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(
                f"Error creating order from checkout {checkout.pk}: {e}", exc_info=True
            )
            # Re-lanzar la excepción para que la transacción se revierta
            raise

        # Solo marcar como paid si la Order se creó exitosamente
        checkout.status = "paid"
        checkout.paid_at = timezone.now()
        checkout.save(update_fields=["status", "paid_at", "updated_at"])

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

    # Confirmar y descontar fondos reservados del wallet
    breakdown = checkout.breakdown or {}
    wallet_deduction_str = breakdown.get("wallet_deduction", "0")
    try:
        wallet_deduction = Decimal(str(wallet_deduction_str))
        if wallet_deduction > 0:
            try:
                from .models import UserWallet

                wallet, _created = UserWallet.objects.get_or_create(user=checkout.user)
                wallet.confirm_reserved_funds(
                    amount=wallet_deduction,
                    description=f"Pago confirmado para: {checkout.event.title}",
                    reference_id=f"checkout_confirmed:{checkout.pk}",
                )
            except Exception as e:
                import logging

                logger = logging.getLogger(__name__)
                logger.error(f"Error confirming wallet funds: {e}")
    except (ValueError, TypeError, InvalidOperation):
        pass

    _finalize_stripe_event_checkout(checkout)

    # Clear live session cart (UX)
    request.session["hotel_cart"] = {}
    request.session.modified = True

    messages.success(request, _("Payment completed. Registration confirmed."))
    # Redirigir a la página de confirmación
    return redirect("accounts:payment_confirmation", pk=checkout.pk)


@login_required
def stripe_event_checkout_cancel(request, pk):
    """
    Maneja la cancelación del checkout de Stripe.
    Si se usó wallet, libera los fondos reservados.
    """
    import logging

    from apps.events.models import Event

    from .models import UserWallet

    logger = logging.getLogger(__name__)
    event = get_object_or_404(Event, pk=pk)

    # Buscar el checkout más reciente del usuario para este evento
    # Buscar primero en estado "created", luego en cualquier estado reciente (últimos 10 minutos)
    try:
        from datetime import timedelta

        from django.utils import timezone

        # Primero intentar encontrar checkout en estado "created"
        checkout = (
            StripeEventCheckout.objects.filter(
                user=request.user, event=event, status="created"
            )
            .order_by("-created_at")
            .first()
        )

        # Si no se encuentra, buscar cualquier checkout reciente (últimas 24 horas)
        # que no esté pagado ni cancelado. Las sesiones de Stripe expiran después de 24 horas.
        if not checkout:
            recent_time = timezone.now() - timedelta(hours=24)
            checkout = (
                StripeEventCheckout.objects.filter(
                    user=request.user,
                    event=event,
                    created_at__gte=recent_time,
                    status__in=["created", "registered"],
                )
                .order_by("-created_at")
                .first()
            )

        if checkout:
            logger.info(
                f"Processing cancel for checkout {checkout.pk}, status: {checkout.status}"
            )

            # Verificar si se usó wallet (está en breakdown)
            breakdown = checkout.breakdown or {}
            wallet_deduction_str = breakdown.get("wallet_deduction", "0")
            logger.info(
                f"Checkout {checkout.pk} breakdown: {breakdown}, wallet_deduction: {wallet_deduction_str}"
            )

            try:
                wallet_deduction = Decimal(str(wallet_deduction_str))

                if wallet_deduction > 0:
                    # Liberar fondos reservados del wallet
                    try:
                        wallet, _created = UserWallet.objects.get_or_create(
                            user=request.user
                        )
                        logger.info(
                            f"Releasing ${wallet_deduction} reserved funds from wallet {wallet.pk} for cancelled checkout {checkout.pk}"
                        )
                        wallet.release_reserved_funds(
                            amount=wallet_deduction,
                            description=f"Reserva liberada por cancelación: {event.title}",
                            reference_id=f"checkout_cancel:{checkout.pk}",
                        )
                        messages.success(
                            request,
                            _(
                                "Payment cancelled. Your wallet reservation has been released. $%(amount)s is now available."
                            )
                            % {"amount": wallet_deduction},
                        )
                        logger.info(
                            f"Successfully released ${wallet_deduction} reserved funds from wallet {wallet.pk}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Error refunding wallet on cancel: {e}", exc_info=True
                        )
                        messages.warning(
                            request,
                            _(
                                "Payment cancelled. Please contact support to refund your wallet."
                            ),
                        )
                else:
                    logger.info(f"No wallet deduction found for checkout {checkout.pk}")
                    messages.info(request, _("Payment cancelled."))
            except (ValueError, TypeError, InvalidOperation) as e:
                logger.error(
                    f"Error parsing wallet_deduction '{wallet_deduction_str}': {e}"
                )
                messages.info(request, _("Payment cancelled."))

            # Marcar el checkout como cancelado
            checkout.status = "cancelled"
            checkout.save(update_fields=["status", "updated_at"])

            # Marcar la orden asociada como "abandoned" si existe
            # Esto aplica tanto para pagos únicos como para planes de pago
            try:
                from .models import Order

                order = Order.objects.filter(stripe_checkout=checkout).first()
                if order and order.status in ["pending", "pending_registration"]:
                    order.status = "abandoned"
                    order.save(update_fields=["status", "updated_at"])
                    logger.info(
                        f"Order {order.order_number} (payment_mode: {order.payment_mode}) marked as abandoned due to checkout cancellation"
                    )
            except Exception as e:
                logger.error(f"Error marking order as abandoned: {e}", exc_info=True)
            logger.info(f"Checkout {checkout.pk} marked as cancelled")
        else:
            logger.warning(
                f"No checkout found for user {request.user.pk} and event {event.pk} to cancel"
            )
            messages.info(request, _("Payment cancelled."))
    except Exception as e:
        logger.error(f"Error processing checkout cancel: {e}", exc_info=True)
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

                # Confirmar y descontar fondos reservados del wallet
                breakdown = checkout.breakdown or {}
                wallet_deduction_str = breakdown.get("wallet_deduction", "0")
                try:
                    wallet_deduction = Decimal(str(wallet_deduction_str))
                    if wallet_deduction > 0:
                        try:
                            from .models import UserWallet

                            wallet, _created = UserWallet.objects.get_or_create(
                                user=checkout.user
                            )
                            wallet.confirm_reserved_funds(
                                amount=wallet_deduction,
                                description=f"Pago confirmado (webhook): {checkout.event.title}",
                                reference_id=f"checkout_confirmed_webhook:{checkout.pk}",
                            )
                        except Exception as e:
                            import logging

                            logger = logging.getLogger(__name__)
                            logger.error(
                                f"Error confirming wallet funds in webhook: {e}"
                            )
                except (ValueError, TypeError, InvalidOperation):
                    pass

                _finalize_stripe_event_checkout(checkout)
            except StripeEventCheckout.DoesNotExist:
                pass

    if event_type == "checkout.session.expired":
        session_id = obj.get("id")
        if session_id:
            try:
                checkout = StripeEventCheckout.objects.get(
                    stripe_session_id=session_id, status="created"
                )

                # Verificar si se usó wallet y liberar fondos reservados
                breakdown = checkout.breakdown or {}
                wallet_deduction_str = breakdown.get("wallet_deduction", "0")

                try:
                    wallet_deduction = Decimal(str(wallet_deduction_str))

                    if wallet_deduction > 0:
                        try:
                            from .models import UserWallet

                            wallet, _created = UserWallet.objects.get_or_create(
                                user=checkout.user
                            )
                            wallet.release_reserved_funds(
                                amount=wallet_deduction,
                                description=f"Reserva liberada por expiración: {checkout.event.title}",
                                reference_id=f"checkout_expired:{checkout.pk}",
                            )
                            import logging

                            logger = logging.getLogger(__name__)
                            logger.info(
                                f"Wallet reservation released for expired checkout {checkout.pk}: ${wallet_deduction}"
                            )
                        except Exception as e:
                            import logging

                            logger = logging.getLogger(__name__)
                            logger.error(
                                f"Error releasing wallet reservation on expired checkout: {e}"
                            )
                except (ValueError, TypeError, InvalidOperation):
                    pass

                # Marcar como expirado
                checkout.status = "expired"
                checkout.save(update_fields=["status", "updated_at"])

                # Marcar la orden asociada como "abandoned" si existe
                # Esto aplica tanto para pagos únicos como para planes de pago
                try:
                    from .models import Order

                    order = Order.objects.filter(stripe_checkout=checkout).first()
                    if order and order.status in ["pending", "pending_registration"]:
                        order.status = "abandoned"
                        order.save(update_fields=["status", "updated_at"])
                        import logging

                        logger = logging.getLogger(__name__)
                        logger.info(
                            f"Order {order.order_number} (payment_mode: {order.payment_mode}) marked as abandoned due to checkout expiration"
                        )
                except Exception as e:
                    import logging

                    logger = logging.getLogger(__name__)
                    logger.error(
                        f"Error marking order as abandoned: {e}", exc_info=True
                    )
            except StripeEventCheckout.DoesNotExist:
                pass

    # Manejar cancelación de suscripciones (planes de pago)
    if event_type == "customer.subscription.deleted":
        subscription_id = obj.get("id")
        if subscription_id:
            try:
                checkout = StripeEventCheckout.objects.filter(
                    stripe_subscription_id=str(subscription_id),
                    payment_mode="plan",
                    status__in=["created", "registered"],
                ).first()
                if checkout:
                    # Marcar checkout como cancelado
                    checkout.status = "cancelled"
                    checkout.save(update_fields=["status", "updated_at"])

                    # Marcar la orden asociada como "abandoned" si existe
                    try:
                        from .models import Order

                        order = Order.objects.filter(stripe_checkout=checkout).first()
                        if order and order.status in [
                            "pending",
                            "pending_registration",
                        ]:
                            order.status = "abandoned"
                            order.save(update_fields=["status", "updated_at"])
                            import logging

                            logger = logging.getLogger(__name__)
                            logger.info(
                                f"Order {order.order_number} (payment_mode: plan) marked as abandoned due to subscription cancellation"
                            )
                    except Exception as e:
                        import logging

                        logger = logging.getLogger(__name__)
                        logger.error(
                            f"Error marking order as abandoned on subscription cancel: {e}",
                            exc_info=True,
                        )
            except Exception as e:
                import logging

                logger = logging.getLogger(__name__)
                logger.error(
                    f"Error processing subscription.deleted webhook: {e}", exc_info=True
                )

    # Manejar fallos de pago en suscripciones (planes de pago)
    if event_type == "invoice.payment_failed":
        subscription_id = obj.get("subscription")
        if subscription_id:
            try:
                checkout = StripeEventCheckout.objects.filter(
                    stripe_subscription_id=str(subscription_id),
                    payment_mode="plan",
                    status__in=["created", "registered"],
                ).first()
                if checkout:
                    # Si el checkout aún no está pagado y falla el primer pago, marcar como abandonado
                    # Si ya está pagado, no hacer nada (puede ser un pago recurrente que falló)
                    if checkout.status != "paid":
                        checkout.status = "failed"
                        checkout.save(update_fields=["status", "updated_at"])

                        # Marcar la orden asociada como "abandoned" si existe
                        try:
                            from .models import Order

                            order = Order.objects.filter(
                                stripe_checkout=checkout
                            ).first()
                            if order and order.status in [
                                "pending",
                                "pending_registration",
                            ]:
                                order.status = "abandoned"
                                order.save(update_fields=["status", "updated_at"])
                                import logging

                                logger = logging.getLogger(__name__)
                                logger.info(
                                    f"Order {order.order_number} (payment_mode: plan) marked as abandoned due to payment failure"
                                )
                        except Exception as e:
                            import logging

                            logger = logging.getLogger(__name__)
                            logger.error(
                                f"Error marking order as abandoned on payment failure: {e}",
                                exc_info=True,
                            )
            except Exception as e:
                import logging

                logger = logging.getLogger(__name__)
                logger.error(
                    f"Error processing invoice.payment_failed webhook: {e}",
                    exc_info=True,
                )

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


@login_required
def wallet_transactions(request):
    """Vista para mostrar el historial completo de transacciones del wallet"""
    from django.core.paginator import Paginator

    from .models import UserWallet, WalletTransaction

    # Obtener o crear wallet del usuario
    try:
        wallet, _created = UserWallet.objects.get_or_create(user=request.user)
    except Exception:
        wallet = None

    # Obtener transacciones
    transactions = []
    transaction_type = request.GET.get("type", "")
    if wallet:
        transactions = (
            WalletTransaction.objects.filter(wallet=wallet)
            .select_related("wallet")
            .order_by("-created_at")
        )

        # Filtros opcionales
        if transaction_type:
            transactions = transactions.filter(transaction_type=transaction_type)

        # Paginación
        paginator = Paginator(transactions, 20)  # 20 transacciones por página
        page_number = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)
    else:
        page_obj = None

    # Estadísticas
    stats = {}
    if wallet:
        stats["total_deposits"] = WalletTransaction.objects.filter(
            wallet=wallet, transaction_type="deposit"
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        stats["total_payments"] = WalletTransaction.objects.filter(
            wallet=wallet, transaction_type="payment"
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        stats["total_refunds"] = WalletTransaction.objects.filter(
            wallet=wallet, transaction_type="refund"
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        stats["total_withdrawals"] = WalletTransaction.objects.filter(
            wallet=wallet, transaction_type="withdrawal"
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    context = {
        "wallet": wallet,
        "transactions": page_obj,
        "stats": stats,
        "current_filter": transaction_type,
        "transaction_types": WalletTransaction.TRANSACTION_TYPE_CHOICES,
    }

    return render(request, "accounts/wallet_transactions.html", context)


@method_decorator(xframe_options_exempt, name="dispatch")
class WalletTransactionsEmbedView(LoginRequiredMixin, TemplateView):
    """Vista embed para mostrar el historial de transacciones del wallet en un tab del panel"""

    template_name = "accounts/panel_tabs/embed_base.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["inner_template"] = "accounts/panel_tabs/wallet_transactions.html"

        # Obtener datos del wallet
        from django.core.paginator import Paginator

        from .models import UserWallet, WalletTransaction

        try:
            wallet, _created = UserWallet.objects.get_or_create(user=self.request.user)
        except Exception:
            wallet = None

        # Obtener transacciones
        transactions = []
        transaction_type = self.request.GET.get("type", "")
        if wallet:
            transactions = (
                WalletTransaction.objects.filter(wallet=wallet)
                .select_related("wallet")
                .order_by("-created_at")
            )

            # Filtros opcionales
            if transaction_type:
                transactions = transactions.filter(transaction_type=transaction_type)

            # Paginación
            paginator = Paginator(transactions, 20)
            page_number = self.request.GET.get("page", 1)
            page_obj = paginator.get_page(page_number)
        else:
            page_obj = None

        # Estadísticas
        stats = {}
        if wallet:
            stats["total_deposits"] = WalletTransaction.objects.filter(
                wallet=wallet, transaction_type="deposit"
            ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

            stats["total_payments"] = WalletTransaction.objects.filter(
                wallet=wallet, transaction_type="payment"
            ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

            stats["total_refunds"] = WalletTransaction.objects.filter(
                wallet=wallet, transaction_type="refund"
            ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

            stats["total_withdrawals"] = WalletTransaction.objects.filter(
                wallet=wallet, transaction_type="withdrawal"
            ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        context.update(
            {
                "wallet": wallet,
                "transactions": page_obj,
                "stats": stats,
                "current_filter": transaction_type,
                "transaction_types": WalletTransaction.TRANSACTION_TYPE_CHOICES,
            }
        )

        return context


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


def _build_registration_cards_for_user(user):
    """
    Shared helper for `registration_list` and `registration_list_panel`.
    Returns (registration_data, events_list).
    """
    # Get checkouts for the current user
    checkouts = list(
        StripeEventCheckout.objects.filter(user=user)
        .select_related("event")
        .order_by("-created_at")
    )

    # Map orders by checkout id
    orders_by_checkout_id = {}
    checkout_ids = [c.pk for c in checkouts]
    if checkout_ids:
        for order in (
            Order.objects.filter(user=user, stripe_checkout_id__in=checkout_ids)
            .select_related("event", "stripe_checkout")
            .order_by("-created_at")
        ):
            # Keep latest by created_at
            orders_by_checkout_id[order.stripe_checkout_id] = order

    # Fetch all involved players in one query
    all_player_ids = set()
    for c in checkouts:
        for pid in c.player_ids or []:
            try:
                all_player_ids.add(int(pid))
            except Exception:
                continue

    players_by_id = {}
    if all_player_ids:
        players_qs = (
            Player.objects.filter(pk__in=all_player_ids)
            .select_related("user", "user__profile", "team", "division")
            .all()
        )
        players_by_id = {p.pk: p for p in players_qs}

    # Build card data
    registration_data = []
    for checkout in checkouts:
        order = orders_by_checkout_id.get(checkout.pk)

        registered_players = []
        for pid in checkout.player_ids or []:
            try:
                pid_int = int(pid)
            except Exception:
                continue
            player = players_by_id.get(pid_int)
            if player:
                registered_players.append(player)

        registration_data.append(
            {
                "checkout": checkout,
                "order": order,
                "event": checkout.event,
                "status": checkout.status,
                "payment_mode": checkout.payment_mode,
                "created_at": checkout.created_at,
                "paid_at": checkout.paid_at,
                "amount_total": checkout.amount_total,
                "breakdown": checkout.breakdown,
                "has_hotel": bool(checkout.hotel_cart_snapshot),
                "hotel_cart_snapshot": checkout.hotel_cart_snapshot,
                "players": registered_players,
                "player_count": len(registered_players),
                "is_completed": (order.status == "paid") if order else False,
                "is_pending": (
                    (order.status in ["pending_registration", "pending"])
                    if order
                    else (checkout.status in ["created", "registered"])
                ),
            }
        )

    # Distinct events preserving order
    events_list = []
    seen = set()
    for c in checkouts:
        if c.event_id and c.event_id not in seen:
            events_list.append(c.event)
            seen.add(c.event_id)

    return registration_data, events_list


@login_required
def registration_list(request):
    """List current user's registrations (standalone page)."""
    from django.shortcuts import render

    registrations, _events = _build_registration_cards_for_user(request.user)
    return render(
        request,
        "accounts/registration_list.html",
        {"registrations": registrations},
    )


@login_required
@xframe_options_exempt
def registration_list_panel(request):
    """List current user's registrations (panel tab iframe)."""
    from django.shortcuts import render

    registrations, events = _build_registration_cards_for_user(request.user)
    return render(
        request,
        "accounts/panel_tabs/embed_base.html",
        {
            "inner_template": "accounts/panel_tabs/registrations.html",
            "registrations": registrations,
            "events": events,
            "request": request,
        },
    )


@login_required
def resume_checkout_data(request, checkout_id):
    """Return saved pending registration selections so the event checkout UI can be pre-filled."""
    checkout = get_object_or_404(StripeEventCheckout, pk=checkout_id, user=request.user)
    if checkout.status == "paid":
        return JsonResponse(
            {"success": False, "error": _("This registration is already paid.")},
            status=400,
        )

    return JsonResponse(
        {
            "success": True,
            "checkout_id": checkout.pk,
            "event_id": checkout.event_id,
            "payment_mode": checkout.payment_mode,
            "player_ids": checkout.player_ids or [],
            "hotel_cart_snapshot": checkout.hotel_cart_snapshot or {},
        }
    )


@login_required
def registration_confirmation(request, pk):
    """Show registration confirmation page"""
    from django.shortcuts import render

    checkout = get_object_or_404(StripeEventCheckout, pk=pk, user=request.user)
    order = Order.objects.filter(stripe_checkout=checkout).first()

    # Build rich display context (players, hotel summary, formatted JSON)
    from decimal import Decimal

    try:
        from .models import Player
    except Exception:
        Player = None  # type: ignore

    # Players
    registered_players = []
    if Player and (checkout.player_ids or []):
        player_ids = []
        for pid in checkout.player_ids or []:
            try:
                player_ids.append(int(pid))
            except Exception:
                continue

        players_qs = (
            Player.objects.filter(pk__in=player_ids)
            .select_related("user", "team", "division")
            .order_by("user__first_name", "user__last_name", "user__username")
        )
        for p in players_qs:
            registered_players.append(
                {
                    "id": p.pk,
                    "name": p.user.get_full_name() or p.user.username,
                    "email": getattr(p.user, "email", "") or "",
                    "team": getattr(getattr(p, "team", None), "team_name", "") or "",
                    "division": getattr(getattr(p, "division", None), "name", "") or "",
                    "jersey_number": getattr(p, "jersey_number", None),
                    "position": getattr(p, "position", "") or "",
                    "secondary_position": getattr(p, "secondary_position", "") or "",
                    "batting_hand": getattr(p, "batting_hand", "") or "",
                    "throwing_hand": getattr(p, "throwing_hand", "") or "",
                    "height": getattr(p, "height", "") or "",
                    "weight": getattr(p, "weight", None),
                    "grade": getattr(p, "grade", "") or "",
                    "emergency_contact_name": getattr(p, "emergency_contact_name", "")
                    or "",
                    "emergency_contact_phone": getattr(p, "emergency_contact_phone", "")
                    or "",
                }
            )

    # Hotel snapshot summary
    hotel_snapshot = checkout.hotel_cart_snapshot or {}
    hotel_rooms = []
    if isinstance(hotel_snapshot, dict):
        for key, item in (hotel_snapshot or {}).items():
            if not isinstance(item, dict):
                continue
            if item.get("type") != "room":
                continue
            hotel_rooms.append(
                {
                    "room_id": item.get("room_id") or item.get("roomId") or "",
                    "room_name": item.get("room_name") or item.get("roomLabel") or "",
                    "check_in": item.get("check_in") or item.get("check_in_date") or "",
                    "check_out": item.get("check_out")
                    or item.get("check_out_date")
                    or "",
                    "capacity": item.get("capacity") or "",
                    "guests": item.get("guests") or "",
                    "guests_included": item.get("guests_included") or "",
                    "extra_guests": item.get("extra_guests") or "",
                    "additional_guest_price": item.get("additional_guest_price") or "",
                    "total_price": item.get("total_price") or item.get("price") or "",
                    "services": item.get("services") or [],
                    "guest_assignments": item.get("guest_assignments") or {},
                    "additional_guest_details": item.get("additional_guest_details")
                    or [],
                    "taxes": item.get("taxes") or [],
                    "rules": item.get("rules") or [],
                }
            )

    breakdown = checkout.breakdown or {}
    has_hotel = bool(hotel_rooms) or (
        isinstance(breakdown, dict)
        and Decimal(str(breakdown.get("hotel_total", "0") or "0")) > Decimal("0.00")
    )

    context = {
        "checkout": checkout,
        "order": order,
        "event": checkout.event,
        "registered_players": registered_players,
        "has_hotel": has_hotel,
        "hotel_rooms": hotel_rooms,
    }

    return render(request, "accounts/registration_confirmation_panel.html", context)


@login_required
def pending_payments(request):
    """Show pending payments for the user"""
    from django.shortcuts import render

    pending_orders = (
        Order.objects.filter(user=request.user, status="pending_registration")
        .select_related("stripe_checkout", "event")
        .order_by("-created_at")
    )

    context = {
        "pending_orders": pending_orders,
    }

    return render(request, "accounts/pending_payments.html", context)


@login_required
@require_POST
def complete_hotel_payment(request, order_id):
    """
    Complete payment for a pending registration (event + hotel) - returns JSON.

    Note: kept name for backwards-compat with existing URL/template JS.
    """
    import logging

    import stripe

    logger = logging.getLogger(__name__)

    # Check Stripe configuration
    if not hasattr(settings, "STRIPE_SECRET_KEY") or not settings.STRIPE_SECRET_KEY:
        return JsonResponse(
            {"success": False, "error": _("Payment system is not configured.")}
        )

    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
    except Exception:
        return JsonResponse(
            {"success": False, "error": _("Payment system is not available.")}
        )

    try:
        order = get_object_or_404(
            Order, pk=order_id, user=request.user, status="pending_registration"
        )
        checkout = order.stripe_checkout
        if not checkout:
            return JsonResponse(
                {"success": False, "error": _("Order is missing checkout information.")}
            )

        # Rebuild the EVENT checkout (with the stored selections) and redirect to Stripe.
        event = checkout.event
        payment_mode = "plan" if checkout.payment_mode == "plan" else "now"

        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe_account = (
            event.stripe_payment_profile
            if getattr(event, "stripe_payment_profile", None)
            else None
        )

        currency = (getattr(settings, "STRIPE_CURRENCY", "usd") or "usd").lower()

        # Totals come from checkout.breakdown (already includes discounts/fees as captured at creation time).
        breakdown = checkout.breakdown or {}
        players_count = int(len(checkout.player_ids or []))

        players_total = _decimal(breakdown.get("players_total"), default="0.00")
        hotel_total = _decimal(breakdown.get("hotel_total"), default="0.00")
        hotel_buy_out_fee = _decimal(breakdown.get("hotel_buy_out_fee"), default="0.00")
        service_fee_percent = int(breakdown.get("service_fee_percent") or 0)
        service_fee_amount = _decimal(
            breakdown.get("service_fee_amount"), default="0.00"
        )
        total_before_discount = _decimal(
            breakdown.get("total_before_discount"), default="0.00"
        )
        discount_percent = int(
            breakdown.get("discount_percent") or checkout.discount_percent or 0
        )

        line_items = []
        if payment_mode == "plan":
            plan_months = int(checkout.plan_months or 1)
            plan_monthly_amount = _decimal(checkout.plan_monthly_amount, default="0.00")
            if plan_monthly_amount <= 0:
                # fallback to compute from subtotal-ish
                plan_monthly_amount = (
                    total_before_discount / Decimal(str(max(1, plan_months)))
                ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            if plan_monthly_amount <= 0:
                return JsonResponse(
                    {"success": False, "error": _("There is nothing to charge.")}
                )

            plan_description = f"First charge today, then {max(0, plan_months - 1)} monthly charge(s). Ends automatically."
            if service_fee_amount > 0:
                plan_description += f" Includes service fee ({service_fee_percent}%)."

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
            # Event registration per player (use stored players_total to preserve totals)
            if players_total > 0 and players_count > 0:
                unit = (players_total / Decimal(str(players_count))).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                line_items.append(
                    {
                        "price_data": {
                            "currency": currency,
                            "product_data": {
                                "name": f"Event registration - {event.title}"
                            },
                            "unit_amount": _money_to_cents(unit),
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
                            "unit_amount": _money_to_cents(hotel_total),
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
                            "unit_amount": _money_to_cents(hotel_buy_out_fee),
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
                            "unit_amount": _money_to_cents(service_fee_amount),
                        },
                        "quantity": 1,
                    }
                )

            if not line_items:
                return JsonResponse(
                    {"success": False, "error": _("There is nothing to charge.")}
                )

        success_url = (
            request.build_absolute_uri(
                reverse(
                    "accounts:stripe_event_checkout_success", kwargs={"pk": event.pk}
                )
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
            "customer_email": request.user.email or None,
            "metadata": {
                "event_id": str(event.pk),
                "user_id": str(request.user.pk),
                "payment_mode": payment_mode,
                "discount_percent": str(discount_percent),
                "service_fee_percent": str(service_fee_percent),
                "service_fee_amount": str(service_fee_amount),
                "player_ids": ",".join([str(x) for x in (checkout.player_ids or [])]),
                "existing_checkout_id": str(checkout.pk),
                "order_id": str(order.pk),
            },
            "stripe_account": stripe_account,
        }
        if payment_mode == "plan":
            session_params["payment_method_types"] = ["card"]

        session = stripe.checkout.Session.create(**session_params)

        # IMPORTANT: success/webhook look up StripeEventCheckout by stripe_session_id,
        # so we must update this checkout to the new session id.
        checkout.stripe_session_id = session.id
        checkout.payment_mode = payment_mode
        checkout.discount_percent = discount_percent
        checkout.save(
            update_fields=[
                "stripe_session_id",
                "payment_mode",
                "discount_percent",
                "updated_at",
            ]
        )

        return JsonResponse({"success": True, "checkout_url": session.url})

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating payment session: {str(e)}")
        return JsonResponse(
            {
                "success": False,
                "error": _("Error creating payment session. Please try again."),
            }
        )
    except Exception as e:
        logger.error(f"Error completing hotel payment: {str(e)}")
        return JsonResponse(
            {
                "success": False,
                "error": _("Error processing payment. Please try again."),
            }
        )


@login_required
def hotel_payment_success(request, order_id):
    """Handle successful hotel payment and show confirmation page."""
    from django.shortcuts import render

    order = get_object_or_404(Order, pk=order_id, user=request.user)
    checkout = order.stripe_checkout
    if not checkout:
        messages.error(request, _("Order is missing checkout information."))
        return redirect("accounts:pending_payments")

    # Mark order + checkout as paid (best-effort; Stripe webhook is still the source of truth)
    try:
        order.mark_as_paid()
    except Exception:
        # Fallback if mark_as_paid is not safe for some edge-case
        order.status = "paid"
        order.save(update_fields=["status", "updated_at"])

    try:
        checkout.status = "paid"
        checkout.paid_at = timezone.now()
        checkout.save(update_fields=["status", "paid_at", "updated_at"])
    except Exception:
        pass

    messages.success(
        request,
        _("Hotel payment completed successfully! Your reservation is confirmed."),
    )
    return render(
        request,
        "accounts/hotel_payment_success.html",
        {"order": order, "checkout": checkout, "event": checkout.event},
    )


@login_required
def start_pending_payment(request, checkout_id):
    """Redirect user to the EVENT Stripe checkout rebuilt from the saved pending registration."""
    # Use the same logic as `complete_hotel_payment` but as a redirect (not JSON).
    order = (
        Order.objects.filter(user=request.user, stripe_checkout_id=checkout_id)
        .order_by("-created_at")
        .first()
    )
    if not order or order.status != "pending_registration":
        messages.error(request, _("This order is not pending payment."))
        return redirect("accounts:pending_payments")

    # Call the JSON builder and redirect to the returned Stripe URL
    resp = complete_hotel_payment(request, order.pk)
    try:
        data = json.loads(resp.content.decode("utf-8"))
    except Exception:
        messages.error(request, _("Error creating payment session. Please try again."))
        return redirect("accounts:pending_payments")

    if not data.get("success") or not data.get("checkout_url"):
        messages.error(
            request, data.get("error") or _("Error creating payment session.")
        )
        return redirect("accounts:pending_payments")

    return redirect(data["checkout_url"])


# ===== NOTIFICATION API VIEWS =====
@login_required
def get_notifications_api(request):
    """API para obtener notificaciones del usuario"""
    try:
        # Obtener parámetros opcionales
        limit = int(request.GET.get("limit", 50))
        unread_only = request.GET.get("unread_only", "false").lower() == "true"

        # Construir query
        notifications_query = Notification.objects.filter(user=request.user)

        if unread_only:
            notifications_query = notifications_query.filter(read=False)

        # Obtener notificaciones
        notifications = notifications_query.select_related("order", "event").order_by(
            "-created_at"
        )[:limit]

        # Formatear respuesta
        notifications_data = []
        for notification in notifications:
            # Calcular tiempo relativo
            time_ago = _get_time_ago(notification.created_at)

            notifications_data.append(
                {
                    "id": notification.id,
                    "type": notification.type,
                    "title": notification.title,
                    "message": notification.message,
                    "read": notification.read,
                    "time": time_ago,
                    "action_url": notification.action_url or "",
                    "order_id": notification.order_id,
                    "event_id": notification.event_id,
                }
            )

        # Contar no leídas
        unread_count = Notification.objects.filter(
            user=request.user, read=False
        ).count()

        return JsonResponse(
            {
                "success": True,
                "notifications": notifications_data,
                "unread_count": unread_count,
            }
        )
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error getting notifications: {str(e)}")
        return JsonResponse(
            {"success": False, "error": "Error al obtener notificaciones"}, status=500
        )


@login_required
def get_notification_count_api(request):
    """API para obtener solo el conteo de notificaciones no leídas"""
    try:
        unread_count = Notification.objects.filter(
            user=request.user, read=False
        ).count()
        return JsonResponse({"success": True, "count": unread_count})
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error getting notification count: {str(e)}")
        return JsonResponse({"success": False, "count": 0})


@login_required
@require_POST
def mark_notification_read_api(request, notification_id):
    """API para marcar una notificación como leída"""
    try:
        notification = get_object_or_404(
            Notification, id=notification_id, user=request.user
        )
        notification.mark_as_read()

        # Obtener nuevo conteo
        unread_count = Notification.objects.filter(
            user=request.user, read=False
        ).count()

        return JsonResponse({"success": True, "unread_count": unread_count})
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error marking notification as read: {str(e)}")
        return JsonResponse(
            {"success": False, "error": "Error al marcar notificación como leída"},
            status=500,
        )


@login_required
@require_POST
def mark_all_notifications_read_api(request):
    """API para marcar todas las notificaciones como leídas"""
    try:
        from django.utils import timezone

        updated = Notification.objects.filter(user=request.user, read=False).update(
            read=True, read_at=timezone.now()
        )

        return JsonResponse(
            {"success": True, "updated_count": updated, "unread_count": 0}
        )
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error marking all notifications as read: {str(e)}")
        return JsonResponse(
            {"success": False, "error": "Error al marcar todas como leídas"},
            status=500,
        )


# ===== WEB PUSH (STAFF) API VIEWS =====
@login_required
def push_public_key_api(request):
    if not request.user.is_staff:
        return JsonResponse({"success": False, "error": "Forbidden"}, status=403)
    public_key = getattr(settings, "VAPID_PUBLIC_KEY", "") or ""
    return JsonResponse({"success": True, "public_key": public_key})


@login_required
@require_POST
def push_subscribe_api(request):
    if not request.user.is_staff:
        return JsonResponse({"success": False, "error": "Forbidden"}, status=403)
    try:
        payload = json.loads(request.body.decode("utf-8")) if request.body else {}
    except Exception:
        payload = {}

    endpoint = (payload.get("endpoint") or "").strip()
    keys = payload.get("keys") or {}
    p256dh = (keys.get("p256dh") or "").strip()
    auth = (keys.get("auth") or "").strip()
    if not endpoint or not p256dh or not auth:
        return JsonResponse(
            {"success": False, "error": "Invalid subscription"}, status=400
        )

    user_agent = (request.META.get("HTTP_USER_AGENT") or "").strip()[:255]
    sub, _created = PushSubscription.objects.update_or_create(
        endpoint=endpoint,
        defaults={
            "user": request.user,
            "p256dh": p256dh,
            "auth": auth,
            "user_agent": user_agent,
            "is_active": True,
        },
    )
    return JsonResponse({"success": True, "subscription_id": sub.pk})


@login_required
@require_POST
def push_unsubscribe_api(request):
    if not request.user.is_staff:
        return JsonResponse({"success": False, "error": "Forbidden"}, status=403)
    try:
        payload = json.loads(request.body.decode("utf-8")) if request.body else {}
    except Exception:
        payload = {}
    endpoint = (payload.get("endpoint") or "").strip()
    if not endpoint:
        return JsonResponse({"success": False, "error": "Invalid endpoint"}, status=400)
    PushSubscription.objects.filter(user=request.user, endpoint=endpoint).update(
        is_active=False
    )
    return JsonResponse({"success": True})


def _get_time_ago(created_at):
    """Helper para calcular tiempo relativo"""
    now = timezone.now()
    diff = now - created_at

    if diff.days > 0:
        if diff.days == 1:
            return "Hace 1 día"
        elif diff.days < 7:
            return f"Hace {diff.days} días"
        elif diff.days < 30:
            weeks = diff.days // 7
            return f"Hace {weeks} semana{'s' if weeks > 1 else ''}"
        elif diff.days < 365:
            months = diff.days // 30
            return f"Hace {months} mes{'es' if months > 1 else ''}"
        else:
            years = diff.days // 365
            return f"Hace {years} año{'s' if years > 1 else ''}"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"Hace {hours} hora{'s' if hours > 1 else ''}"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"Hace {minutes} minuto{'s' if minutes > 1 else ''}"
    else:
        return "Hace unos segundos"


def _get_stripe_api_key():
    """Helper to get Stripe API key and validate configuration"""
    if not settings.STRIPE_SECRET_KEY:
        raise ValueError(_("Stripe is not configured (STRIPE_SECRET_KEY)."))
    return settings.STRIPE_SECRET_KEY


class StripeBillingPortalView(LoginRequiredMixin, View):
    """Vista para redirigir al portal de facturación de Stripe o crear setup session"""

    def get(self, request, *args, **kwargs):
        try:
            import stripe

            stripe.api_key = _get_stripe_api_key()

            user = request.user
            profile = user.profile
            customer_id = profile.stripe_customer_id

            return_url = (
                request.build_absolute_uri(reverse("panel"))
                + "?tab=perfil&profile_section=billing"
            )

            if customer_id:
                # Crear sesión de portal para gestionar métodos de pago
                try:
                    session = stripe.billing_portal.Session.create(
                        customer=customer_id,
                        return_url=return_url,
                    )
                    return redirect(session.url)
                except stripe.error.InvalidRequestError:
                    # Si el customer no existe en Stripe (borrado?), limpiar y fallar al setup
                    profile.stripe_customer_id = ""
                    profile.save()
                    customer_id = None

            if not customer_id:
                # Crear sesión de checkout modo setup para guardar tarjeta
                session = stripe.checkout.Session.create(
                    payment_method_types=["card"],
                    mode="setup",
                    customer_email=user.email,
                    success_url=return_url
                    + "&setup_success=true&session_id={CHECKOUT_SESSION_ID}",
                    cancel_url=return_url,
                )
                return redirect(session.url)

        except Exception as e:
            messages.error(request, f"Error connecting to billing portal: {str(e)}")
            return redirect(reverse("panel") + "?tab=perfil&profile_section=billing")


@login_required
def stripe_billing_setup_success(request):
    """Callback para guardar el customer ID después de un setup exitoso"""
    session_id = request.GET.get("session_id")
    if session_id:
        try:
            import stripe

            stripe.api_key = _get_stripe_api_key()
            session = stripe.checkout.Session.retrieve(session_id)
            customer_id = session.customer

            if customer_id:
                profile = request.user.profile
                profile.stripe_customer_id = customer_id
                profile.save()
                messages.success(request, _("Payment method added successfully."))
        except Exception:
            messages.error(request, _("Could not verify payment setup."))

    return redirect(reverse("panel") + "?tab=perfil&profile_section=billing")
