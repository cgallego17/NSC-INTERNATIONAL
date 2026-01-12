import json
from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, Count, IntegerField, Q, Sum, Value, When
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from apps.core.mixins import StaffRequiredMixin, SuperuserRequiredMixin

from .forms import EventForm
from .models import (
    Division,
    Event,
    EventAttendance,
    EventCategory,
    EventIncludes,
    EventItinerary,
)


class EventListView(StaffRequiredMixin, ListView):
    model = Event
    template_name = "events/list.html"
    context_object_name = "events"
    paginate_by = 20

    def get_queryset(self):
        # Forzar consulta fresca desde la base de datos
        # Mostrar todos los eventos (incluyendo despublicados/borradores)
        queryset = Event.objects.all().select_related(
            "category", "organizer", "event_type", "country", "state", "city"
        )

        # Filtros
        search = self.request.GET.get("search")
        category = self.request.GET.get("category")
        event_type = self.request.GET.get("event_type")
        status = self.request.GET.get("status")
        time_filter = self.request.GET.get("time_filter")

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(location__icontains=search)
            )

        if category:
            queryset = queryset.filter(category__id=category)

        if event_type:
            queryset = queryset.filter(event_type__id=event_type)

        # Default to 'published' if no status filter is provided
        # But if status is explicitly 'all', don't filter by status
        if status == "all":
            # Don't filter by status - show all
            pass
        elif status:
            queryset = queryset.filter(status=status)
        else:
            # Default to 'published' when no status parameter
            queryset = queryset.filter(status="published")

        if time_filter:
            now = timezone.now()
            if time_filter == "upcoming":
                queryset = queryset.filter(start_date__gt=now)
            elif time_filter == "ongoing":
                queryset = queryset.filter(start_date__lte=now, end_date__gte=now)
            elif time_filter == "past":
                queryset = queryset.filter(end_date__lt=now)
            elif time_filter == "today":
                today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                today_end = today_start + timedelta(days=1)
                queryset = queryset.filter(
                    start_date__gte=today_start, start_date__lt=today_end
                )

        # Ordenar: completados primero (por fecha de inicio descendente), luego el resto por fecha ascendente
        status_filter = self.request.GET.get("status")
        if status_filter == "completed":
            # Para completados, ordenar por fecha descendente (más recientes primero)
            queryset = queryset.order_by("-start_date")
        else:
            # Para otros estados, ordenar por fecha ascendente (próximos primero)
            queryset = queryset.annotate(
                status_priority=Case(
                    When(status="completed", then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            ).order_by("status_priority", "start_date")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = EventCategory.objects.filter(is_active=True)
        from apps.events.models import EventType

        context["event_types"] = EventType.objects.filter(is_active=True)
        context["status_choices"] = Event.STATUS_CHOICES
        context["time_filters"] = [
            ("upcoming", "Próximos"),
            ("ongoing", "En curso"),
            ("past", "Pasados"),
            ("today", "Hoy"),
        ]

        # Obtener conteos por estado para los tabs
        base_queryset = Event.objects.all()
        search = self.request.GET.get("search")
        category = self.request.GET.get("category")
        event_type = self.request.GET.get("event_type")
        time_filter = self.request.GET.get("time_filter")

        # Aplicar los mismos filtros que se aplican en get_queryset (excepto status)
        if search:
            base_queryset = base_queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(location__icontains=search)
            )
        if category:
            base_queryset = base_queryset.filter(category__id=category)
        if event_type:
            base_queryset = base_queryset.filter(event_type__id=event_type)
        if time_filter:
            now = timezone.now()
            if time_filter == "upcoming":
                base_queryset = base_queryset.filter(start_date__gt=now)
            elif time_filter == "ongoing":
                base_queryset = base_queryset.filter(
                    start_date__lte=now, end_date__gte=now
                )
            elif time_filter == "past":
                base_queryset = base_queryset.filter(end_date__lt=now)
            elif time_filter == "today":
                today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                today_end = today_start + timedelta(days=1)
                base_queryset = base_queryset.filter(
                    start_date__gte=today_start, start_date__lt=today_end
                )

        # Contar eventos por estado
        context["status_counts"] = {
            "all": base_queryset.count(),
            "draft": base_queryset.filter(status="draft").count(),
            "published": base_queryset.filter(status="published").count(),
            "cancelled": base_queryset.filter(status="cancelled").count(),
            "completed": base_queryset.filter(status="completed").count(),
        }

        # Estado activo actual (default: 'all')
        context["active_status"] = self.request.GET.get(
            "status", "published"
        )  # Default to published

        return context


class EventDetailView(StaffRequiredMixin, DetailView):
    model = Event
    template_name = "events/detail.html"
    context_object_name = "event"

    def get_queryset(self):
        """
        Admin/detail view.

        - Staff: can view any event (published/draft/etc.)
        - Non-staff: only published events
        """
        base_qs = (
            Event.objects.all()
            if self.request.user.is_staff
            else Event.objects.filter(status="published")
        )

        # Optimizar consultas relacionadas para mejor rendimiento
        return base_qs.select_related(
            "category",
            "organizer",
            "event_type",
            "country",
            "state",
            "city",
            "season",
            "rule",
            "gate_fee_type",
            "primary_site__city",
            "primary_site__state",
            "hotel__city",
            "hotel__state",
        ).prefetch_related(
            "divisions",
            "additional_sites__city",
            "additional_sites__state",
            "additional_hotels__city",
            "additional_hotels__state",
            "event_contact",
        )

    def get_context_data(self, **kwargs):
        from decimal import Decimal

        from django.db.models import Sum

        from apps.accounts.models import Order, Player

        context = super().get_context_data(**kwargs)
        context["attendees"] = self.object.attendees.filter(
            eventattendance__status="confirmed"
        ).select_related()
        context["comments"] = (
            self.object.comments.filter(is_internal=False)
            .select_related("user")
            .order_by("-created_at")[:10]
        )

        # Verificar si el usuario está registrado
        if self.request.user.is_authenticated:
            try:
                attendance = EventAttendance.objects.get(
                    event=self.object, user=self.request.user
                )
                context["user_attendance"] = attendance
            except EventAttendance.DoesNotExist:
                context["user_attendance"] = None

        # Ya tenemos el evento cargado desde get_queryset() (con select_related/prefetch)
        context["event"] = self.object

        # Datos para el admin: jugadores registrados al evento
        # Los jugadores pueden estar registrados a través de:
        # 1. Order (registered_player_ids)
        # 2. StripeEventCheckout (player_ids)
        # 3. EventAttendance (user -> Player)

        player_ids = set()

        # 1. De órdenes pagadas
        paid_orders = Order.objects.filter(
            event=self.object, status="paid"
        ).values_list("registered_player_ids", flat=True)
        for player_ids_list in paid_orders:
            if player_ids_list:
                player_ids.update(player_ids_list)

        # 2. De StripeEventCheckout pagados
        from apps.accounts.models import StripeEventCheckout

        paid_checkouts = StripeEventCheckout.objects.filter(
            event=self.object, status="paid"
        )
        for checkout in paid_checkouts:
            if checkout.player_ids:
                player_ids.update(checkout.player_ids)

        # 3. De EventAttendance confirmados
        confirmed_attendances = EventAttendance.objects.filter(
            event=self.object, status="confirmed"
        ).select_related("user")
        for attendance in confirmed_attendances:
            try:
                player = Player.objects.get(user=attendance.user)
                player_ids.add(player.id)
            except Player.DoesNotExist:
                pass

        # Obtener los jugadores con sus relaciones optimizadas
        registered_players = (
            Player.objects.filter(id__in=player_ids)
            .select_related("user", "division", "user__profile")
            .prefetch_related("parents__parent")
            .order_by("user__last_name", "user__first_name")
        )

        context["registered_players"] = registered_players
        context["registered_players_count"] = registered_players.count()

        # Contar padres únicos
        # Los jugadores tienen una relación con padres a través de PlayerParent
        from apps.accounts.models import PlayerParent

        unique_parents = {}
        for player in registered_players:
            # Obtener el padre principal del jugador
            parent_relation = (
                PlayerParent.objects.filter(player=player, is_primary=True)
                .select_related("parent")
                .first()
            )

            if not parent_relation:
                # Si no hay padre principal, tomar el primero
                parent_relation = (
                    PlayerParent.objects.filter(player=player)
                    .select_related("parent")
                    .first()
                )

            if parent_relation and parent_relation.parent:
                parent = parent_relation.parent
                parent_id = parent.id
                if parent_id not in unique_parents:
                    unique_parents[parent_id] = {
                        "id": parent_id,
                        "get_full_name": parent.get_full_name() or parent.username,
                        "username": parent.username,
                        "email": parent.email,
                        "players_count": 0,
                    }
                unique_parents[parent_id]["players_count"] += 1

        context["unique_parents"] = list(unique_parents.values())
        context["unique_parents_count"] = len(unique_parents)

        # Contar registros por división
        if self.object.divisions.exists():
            # Crear lista de divisiones con conteos
            divisions_list = []
            for division in self.object.divisions.all():
                # Ahora division es un ForeignKey, podemos comparar directamente
                division_count = registered_players.filter(division=division).count()

                # Agregar el atributo registered_count a la división
                division.registered_count = division_count
                divisions_list.append(division)

            # También crear el diccionario para mantener compatibilidad
            divisions_with_counts = [
                {"division": div, "registered_count": div.registered_count}
                for div in divisions_list
            ]
            context["divisions_with_counts"] = divisions_with_counts

        # Estadísticas de órdenes y checkouts
        orders = Order.objects.filter(event=self.object, status="paid")
        paid_checkouts = StripeEventCheckout.objects.filter(
            event=self.object, status="paid"
        )
        # Contar todas las transacciones pagadas (órdenes + checkouts)
        context["orders_count"] = orders.count() + paid_checkouts.count()

        # Calcular ingresos de órdenes
        # Para órdenes con plan de pago, usar plan_total_amount, sino usar total_amount
        order_revenue = Decimal("0.00")
        for order in orders:
            if order.payment_mode == "plan" and order.plan_total_amount:
                order_revenue += order.plan_total_amount
            else:
                order_revenue += order.total_amount or Decimal("0.00")

        # Calcular ingresos de StripeEventCheckout
        from apps.accounts.models import StripeEventCheckout

        paid_checkouts = StripeEventCheckout.objects.filter(
            event=self.object, status="paid"
        )
        checkout_revenue = Decimal("0.00")
        for checkout in paid_checkouts:
            if (
                checkout.payment_mode == "plan"
                and checkout.plan_months
                and checkout.plan_monthly_amount
            ):
                # Para planes, usar el total del plan (meses * monto mensual)
                checkout_revenue += checkout.plan_months * checkout.plan_monthly_amount
            else:
                # Para pagos completos, usar amount_total
                checkout_revenue += checkout.amount_total or Decimal("0.00")

        # Total de ingresos
        total_revenue = order_revenue + checkout_revenue
        context["total_revenue"] = total_revenue

        # Estadísticas de hotel
        from apps.locations.models import HotelReservation

        hotel_reservations_count = 0
        rooms_sold_count = 0

        if self.object.hotel:
            # Obtener usuarios que tienen órdenes o checkouts pagados para este evento
            users_with_payments = set()
            for order in orders:
                users_with_payments.add(order.user_id)
            for checkout in paid_checkouts:
                users_with_payments.add(checkout.user_id)

            # 1. Contar reservas de hotel confirmadas de estos usuarios en el hotel del evento
            if users_with_payments:
                all_reservations = HotelReservation.objects.filter(
                    hotel=self.object.hotel,
                    user_id__in=users_with_payments,
                    status__in=["confirmed", "checked_in", "checked_out"],
                )
                hotel_reservations_count = all_reservations.count()

                # Contar habitaciones únicas vendidas desde reservas
                rooms_from_reservations = (
                    all_reservations.values("room").distinct().count()
                )
                rooms_sold_count = rooms_from_reservations

            # 2. Si no hay reservas creadas, contar habitaciones desde hotel_cart_snapshot de checkouts
            if rooms_sold_count == 0:
                rooms_from_checkouts = set()
                for checkout in paid_checkouts:
                    hotel_cart = checkout.hotel_cart_snapshot or {}
                    rooms = hotel_cart.get("rooms", [])
                    for room_data in rooms:
                        room_id = room_data.get("roomId") or room_data.get("room_id")
                        if room_id:
                            try:
                                rooms_from_checkouts.add(int(room_id))
                            except (ValueError, TypeError):
                                pass

                # 3. También contar desde órdenes (reservas directas)
                for order in orders:
                    order_reservations = order.hotel_reservations_direct.filter(
                        hotel=self.object.hotel,
                        status__in=["confirmed", "checked_in", "checked_out"],
                    )
                    order_rooms = order_reservations.values_list("room_id", flat=True)
                    rooms_from_checkouts.update(order_rooms)
                    hotel_reservations_count += order_reservations.count()

                # Actualizar contadores
                if rooms_from_checkouts:
                    rooms_sold_count = len(rooms_from_checkouts)
                    # Si hay habitaciones en cart pero no reservas, estimar 1 reserva por habitación
                    if hotel_reservations_count == 0:
                        hotel_reservations_count = rooms_sold_count

        context["hotel_reservations_count"] = hotel_reservations_count
        context["rooms_sold_count"] = rooms_sold_count

        return context


class EventCreateView(StaffRequiredMixin, CreateView):
    """Vista para crear eventos"""

    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = reverse_lazy("events:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar divisiones al contexto para JavaScript
        import json

        from .models import Division

        divisions_queryset = Division.objects.filter(is_active=True).order_by("name")
        context["available_divisions"] = json.dumps(
            list(divisions_queryset.values("id", "name"))
        )
        context["available_divisions_count"] = divisions_queryset.count()
        return context

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        response = super().form_valid(form)

        # Procesar itinerario después de guardar el evento
        self.save_itinerary(self.object)
        # Procesar includes después de guardar el evento
        self.save_includes(self.object)

        messages.success(self.request, "Evento creado exitosamente.")
        return response

    def save_itinerary(self, event):
        """Guarda el itinerario del evento para cada tipo de usuario"""
        import json
        import logging
        from datetime import datetime

        from django.db import IntegrityError

        logger = logging.getLogger(__name__)

        # Eliminar itinerario existente si estamos editando
        EventItinerary.objects.filter(event=event).delete()

        # Procesar itinerarios para cada tipo de usuario
        user_types = ["player", "team_manager", "spectator"]

        for user_type in user_types:
            # Obtener todos los días del itinerario para este tipo de usuario
            field_name = f"itinerary_days_{user_type}"
            itinerary_days_data = self.request.POST.getlist(field_name)

            logger.info(
                f"Guardando itinerario para {user_type}: {len(itinerary_days_data)} días encontrados"
            )

            # Validar días duplicados antes de crear
            seen_days = set()

            # Procesar cada día del itinerario
            for idx, day_data_str in enumerate(itinerary_days_data):
                try:
                    # Decodificar el HTML entity
                    day_data_str = day_data_str.replace("&#39;", "'").replace(
                        "&quot;", '"'
                    )
                    day_data = json.loads(day_data_str)

                    # Convertir el string de fecha a objeto date
                    day_str = day_data.get("day", "").strip()
                    if not day_str:
                        logger.warning(
                            f"Día {idx} de {user_type} sin fecha, omitiendo..."
                        )
                        continue

                    try:
                        # Intentar parsear la fecha (formato ISO: YYYY-MM-DD)
                        day_date = datetime.strptime(day_str, "%Y-%m-%d").date()
                    except (ValueError, TypeError) as e:
                        logger.error(
                            f"Error al parsear fecha '{day_str}' en día {idx} de {user_type}: {e}"
                        )
                        continue

                    # Validar que no sea un día duplicado para este user_type
                    day_key = (user_type, day_date)
                    if day_key in seen_days:
                        logger.warning(
                            f"Día duplicado ignorado: {user_type} - {day_date} (día {idx})"
                        )
                        continue
                    seen_days.add(day_key)

                    # Crear el item de itinerario con el user_type correcto
                    try:
                        itinerary_obj = EventItinerary.objects.create(
                            event=event,
                            user_type=user_type,
                            day=day_date,
                            day_number=int(day_data.get("dayNumber", 1)) or 1,
                            title=day_data.get("title", "").strip() or "",
                            description=day_data.get("description", "").strip() or "",
                            schedule_items=day_data.get("scheduleItems", []) or [],
                        )
                        logger.info(
                            f"Itinerario creado: {itinerary_obj.title} ({user_type}) - {day_date} - Día #{itinerary_obj.day_number}"
                        )

                    except IntegrityError as e:
                        logger.error(
                            f"Error de integridad al guardar día {idx} ({user_type}): {e}. Día: {day_date}"
                        )
                        # Este error no debería ocurrir si validamos bien los duplicados, pero lo capturamos por seguridad
                        continue

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.error(
                        f"Error al procesar día del itinerario {idx} ({user_type}): {e}. Datos: {day_data_str[:200]}"
                    )
                    import traceback

                    logger.error(traceback.format_exc())
                    continue

    def save_includes(self, event):
        """Guarda los items incluidos del evento para cada tipo de usuario"""
        import json
        import logging

        logger = logging.getLogger(__name__)

        # Eliminar includes existentes si estamos editando
        EventIncludes.objects.filter(event=event).delete()

        # Procesar includes para cada tipo de usuario
        user_types = ["player", "team_manager", "spectator"]

        for user_type in user_types:
            # Obtener todos los items incluidos para este tipo de usuario
            field_name = f"includes_items_{user_type}"
            includes_items_data = self.request.POST.getlist(field_name)

            logger.info(
                f"Guardando includes para {user_type}: {len(includes_items_data)} items encontrados"
            )

            # Procesar cada item incluido
            for idx, item_data_str in enumerate(includes_items_data):
                try:
                    # Decodificar el HTML entity
                    item_data_str = item_data_str.replace("&#39;", "'").replace(
                        "&quot;", '"'
                    )

                    # Intentar parsear el JSON
                    try:
                        item_data = json.loads(item_data_str)
                    except json.JSONDecodeError as e:
                        logger.error(
                            f"Error de JSON en item {idx} de {user_type}: {e}. String recibido: {item_data_str[:100]}"
                        )
                        continue

                    # Validar que el título no esté vacío
                    title = item_data.get("title", "").strip()
                    if not title:
                        logger.warning(
                            f"Item {idx} de {user_type} sin título, omitiendo..."
                        )
                        continue

                    # Crear el item incluido con el user_type correcto
                    include_obj = EventIncludes.objects.create(
                        event=event,
                        user_type=user_type,
                        title=title,
                        description=item_data.get("description", "").strip() or "",
                        order=int(item_data.get("order", 0)) or 0,
                        is_active=(
                            bool(item_data.get("isActive", True))
                            if "isActive" in item_data
                            else True
                        ),
                    )
                    logger.info(
                        f"Include creado: {include_obj.title} ({include_obj.user_type}) - Orden: {include_obj.order}"
                    )

                except (json.JSONDecodeError, KeyError, ValueError, Exception) as e:
                    # Si hay un error, registrar y continuar con el siguiente
                    logger.error(
                        f"Error al procesar item incluido {idx} ({user_type}): {e}. Datos: {item_data_str[:200]}"
                    )
                    import traceback

                    logger.error(traceback.format_exc())
                    continue


class EventUpdateView(StaffRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"

    def get_success_url(self):
        return reverse_lazy("events:admin_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar divisiones al contexto para JavaScript
        context["divisions"] = Division.objects.filter(is_active=True)
        # Debug: Verificar si el evento tiene hotel
        if self.object:
            context["debug_hotel"] = {
                "exists": bool(self.object.hotel),
                "id": self.object.hotel.id if self.object.hotel else None,
                "name": self.object.hotel.hotel_name if self.object.hotel else None,
                "object_id": self.object.id,
            }
        else:
            context["debug_hotel"] = {"exists": False, "object_id": None}
        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        # Procesar itinerario después de actualizar el evento
        self.save_itinerary(self.object)
        # Procesar includes después de actualizar el evento
        self.save_includes(self.object)

        messages.success(self.request, "Evento actualizado exitosamente.")
        return response

    def save_itinerary(self, event):
        """Guarda el itinerario del evento para cada tipo de usuario"""
        import json
        import logging
        from datetime import datetime

        from django.db import IntegrityError

        logger = logging.getLogger(__name__)

        # Eliminar itinerario existente si estamos editando
        EventItinerary.objects.filter(event=event).delete()

        # Procesar itinerarios para cada tipo de usuario
        user_types = ["player", "team_manager", "spectator"]

        for user_type in user_types:
            # Obtener todos los días del itinerario para este tipo de usuario
            field_name = f"itinerary_days_{user_type}"
            itinerary_days_data = self.request.POST.getlist(field_name)

            logger.info(
                f"Guardando itinerario para {user_type}: {len(itinerary_days_data)} días encontrados"
            )

            # Validar días duplicados antes de crear
            seen_days = set()

            # Procesar cada día del itinerario
            for idx, day_data_str in enumerate(itinerary_days_data):
                try:
                    # Decodificar el HTML entity
                    day_data_str = day_data_str.replace("&#39;", "'").replace(
                        "&quot;", '"'
                    )
                    day_data = json.loads(day_data_str)

                    # Convertir el string de fecha a objeto date
                    day_str = day_data.get("day", "").strip()
                    if not day_str:
                        logger.warning(
                            f"Día {idx} de {user_type} sin fecha, omitiendo..."
                        )
                        continue

                    try:
                        # Intentar parsear la fecha (formato ISO: YYYY-MM-DD)
                        day_date = datetime.strptime(day_str, "%Y-%m-%d").date()
                    except (ValueError, TypeError) as e:
                        logger.error(
                            f"Error al parsear fecha '{day_str}' en día {idx} de {user_type}: {e}"
                        )
                        continue

                    # Validar que no sea un día duplicado para este user_type
                    day_key = (user_type, day_date)
                    if day_key in seen_days:
                        logger.warning(
                            f"Día duplicado ignorado: {user_type} - {day_date} (día {idx})"
                        )
                        continue
                    seen_days.add(day_key)

                    # Crear el item de itinerario con el user_type correcto
                    try:
                        itinerary_obj = EventItinerary.objects.create(
                            event=event,
                            user_type=user_type,
                            day=day_date,
                            day_number=int(day_data.get("dayNumber", 1)) or 1,
                            title=day_data.get("title", "").strip() or "",
                            description=day_data.get("description", "").strip() or "",
                            schedule_items=day_data.get("scheduleItems", []) or [],
                        )
                        logger.info(
                            f"Itinerario creado: {itinerary_obj.title} ({user_type}) - {day_date} - Día #{itinerary_obj.day_number}"
                        )

                    except IntegrityError as e:
                        logger.error(
                            f"Error de integridad al guardar día {idx} ({user_type}): {e}. Día: {day_date}"
                        )
                        # Este error no debería ocurrir si validamos bien los duplicados, pero lo capturamos por seguridad
                        continue

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.error(
                        f"Error al procesar día del itinerario {idx} ({user_type}): {e}. Datos: {day_data_str[:200]}"
                    )
                    import traceback

                    logger.error(traceback.format_exc())
                    continue

    def save_includes(self, event):
        """Guarda los items incluidos del evento para cada tipo de usuario"""
        import json
        import logging

        logger = logging.getLogger(__name__)

        # Eliminar includes existentes si estamos editando
        EventIncludes.objects.filter(event=event).delete()

        # Procesar includes para cada tipo de usuario
        user_types = ["player", "team_manager", "spectator"]

        for user_type in user_types:
            # Obtener todos los items incluidos para este tipo de usuario
            field_name = f"includes_items_{user_type}"
            includes_items_data = self.request.POST.getlist(field_name)

            logger.info(
                f"Guardando includes para {user_type}: {len(includes_items_data)} items encontrados"
            )

            # Procesar cada item incluido
            for idx, item_data_str in enumerate(includes_items_data):
                try:
                    # Decodificar el HTML entity
                    item_data_str = item_data_str.replace("&#39;", "'").replace(
                        "&quot;", '"'
                    )

                    # Intentar parsear el JSON
                    try:
                        item_data = json.loads(item_data_str)
                    except json.JSONDecodeError as e:
                        logger.error(
                            f"Error de JSON en item {idx} de {user_type}: {e}. String recibido: {item_data_str[:100]}"
                        )
                        continue

                    # Validar que el título no esté vacío
                    title = item_data.get("title", "").strip()
                    if not title:
                        logger.warning(
                            f"Item {idx} de {user_type} sin título, omitiendo..."
                        )
                        continue

                    # Crear el item incluido con el user_type correcto
                    include_obj = EventIncludes.objects.create(
                        event=event,
                        user_type=user_type,
                        title=title,
                        description=item_data.get("description", "").strip() or "",
                        order=int(item_data.get("order", 0)) or 0,
                        is_active=(
                            bool(item_data.get("isActive", True))
                            if "isActive" in item_data
                            else True
                        ),
                    )
                    logger.info(
                        f"Include creado: {include_obj.title} ({include_obj.user_type}) - Orden: {include_obj.order}"
                    )

                except (json.JSONDecodeError, KeyError, ValueError, Exception) as e:
                    # Si hay un error, registrar y continuar con el siguiente
                    logger.error(
                        f"Error al procesar item incluido {idx} ({user_type}): {e}. Datos: {item_data_str[:200]}"
                    )
                    import traceback

                    logger.error(traceback.format_exc())
                    continue


class EventDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Event
    template_name = "events/confirm_delete.html"
    success_url = reverse_lazy("events:list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Evento eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)


class EventChangeStatusView(StaffRequiredMixin, View):
    """Vista AJAX para cambiar el estado de un evento"""

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        new_status = request.POST.get("status")

        if new_status not in dict(Event.STATUS_CHOICES):
            return JsonResponse(
                {"success": False, "error": "Estado inválido"}, status=400
            )

        event.status = new_status
        event.save()

        status_labels = {
            "draft": "Borrador",
            "published": "Publicado",
            "cancelled": "Cancelado",
            "completed": "Completado",
        }

        return JsonResponse(
            {
                "success": True,
                "status": new_status,
                "status_label": status_labels.get(new_status, new_status),
            }
        )


class EventTogglePublishView(SuperuserRequiredMixin, View):
    """Vista para publicar/despublicar un evento"""

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        if event.status == "published":
            event.status = "draft"
            action = "despublicado"
        else:
            event.status = "published"
            action = "publicado"

        event.save()
        messages.success(request, f'Evento "{event.title}" {action} exitosamente.')

        # Redirigir de vuelta a la lista con los mismos filtros
        redirect_url = reverse_lazy("events:list")
        query_params = request.GET.urlencode()
        if query_params:
            redirect_url = f"{redirect_url}?{query_params}"

        from django.shortcuts import redirect

        return redirect(redirect_url)


class EventDetailAPIView(StaffRequiredMixin, View):
    """API view para obtener detalles del evento en JSON"""

    def get(self, request, pk):
        from apps.accounts.models import Player, PlayerParent

        event = get_object_or_404(
            Event.objects.all()
            .select_related(
                "category",
                "event_type",
                "country",
                "state",
                "city",
                "primary_site",
                "hotel",
                "hotel__city",
                "hotel__city__state",
                "hotel__city__state__country",
                "gate_fee_type",
            )
            .prefetch_related("divisions"),
            pk=pk,
        )

        # Construir información de ubicación
        location_parts = []
        if event.primary_site:
            location_parts.append(f"Lugar: {event.primary_site.site_name}")
        if event.city:
            location_parts.append(f"Ciudad: {event.city.name}")
        if event.state:
            location_parts.append(f"Estado: {event.state.name}")
        if event.country:
            location_parts.append(f"País: {event.country.name}")

        # Obtener precios (valores por defecto si no existen)
        entry_fee = float(event.default_entry_fee) if event.default_entry_fee else 0.0
        gate_fee = float(event.gate_fee_amount) if event.gate_fee_amount else 0.0

        # Precios adicionales (estos podrían venir de configuraciones del evento o modelos relacionados)
        # Por ahora usamos valores por defecto o del hotel si existe
        hotel_price = 0.0
        hotel_info = None

        if event.hotel:
            try:
                # Obtener información completa del hotel
                hotel = event.hotel

                # Obtener información de ubicación de forma segura
                city_name = None
                state_name = None
                country_name = None

                try:
                    if hotel.city:
                        city_name = hotel.city.name
                        if hasattr(hotel.city, "state") and hotel.city.state:
                            state_name = hotel.city.state.name
                            if (
                                hasattr(hotel.city.state, "country")
                                and hotel.city.state.country
                            ):
                                country_name = hotel.city.state.country.name
                except (AttributeError, Exception):
                    pass

                hotel_info = {
                    "id": hotel.pk,
                    "name": hotel.hotel_name,
                    "address": hotel.address or "",
                    "photo": hotel.photo.url if hotel.photo else None,
                    "information": hotel.information or "",
                    "registration_url": hotel.registration_url or "",
                    "city": city_name,
                    "state": state_name,
                    "country": country_name,
                }
                # Aquí podrías obtener el precio del hotel desde el modelo Hotel
                # Por ahora usamos un valor por defecto
                hotel_price = 150.0  # Valor ejemplo
            except Exception as e:
                # Si hay algún error al obtener la información del hotel, usar valores por defecto
                import logging

                logger = logging.getLogger(__name__)
                logger.error(f"Error obteniendo información del hotel: {e}")
                hotel_info = None
                hotel_price = 150.0  # Valor ejemplo

        welcome_dinner_price = 50.0  # Valor ejemplo
        uniform_package_price = 75.0  # Valor ejemplo

        # Obtener jugadores disponibles para el usuario
        players_list = []
        user = request.user
        try:
            profile = user.profile
            if profile.is_parent:
                # Si es padre, obtener sus hijos/jugadores
                player_parents = PlayerParent.objects.filter(
                    parent=user
                ).select_related("player", "player__user", "player__user__profile")
                for pp in player_parents:
                    player = pp.player
                    player_user = player.user
                    player_profile = player_user.profile
                    photo_url = None
                    if player_profile and player_profile.profile_picture:
                        photo_url = player_profile.profile_picture.url
                    division = player.division if player.division else None
                    players_list.append(
                        {
                            "id": player.pk,
                            "name": player_user.get_full_name() or player_user.username,
                            "division": division,
                            "photo": photo_url,
                        }
                    )
            elif profile.is_player:
                # Si es jugador, incluirse a sí mismo
                try:
                    player = user.player_profile
                    photo_url = None
                    if profile.profile_picture:
                        photo_url = profile.profile_picture.url
                    division = player.division if player.division else None
                    players_list.append(
                        {
                            "id": player.pk,
                            "name": user.get_full_name() or user.username,
                            "division": division,
                            "photo": photo_url,
                        }
                    )
                except Player.DoesNotExist:
                    pass
        except Exception:
            pass

        data = {
            "id": event.pk,
            "title": event.title,
            "description": event.description or "",
            "category": event.category.name if event.category else None,
            "logo": event.logo if event.logo else None,
            "start_date": (
                event.start_date.strftime("%d %b %Y") if event.start_date else None
            ),
            "end_date": event.end_date.strftime("%d %b %Y") if event.end_date else None,
            "location_info": "<br>".join(location_parts) if location_parts else None,
            "country": event.country.name if event.country else None,
            "state": event.state.name if event.state else None,
            "city": event.city.name if event.city else None,
            "primary_site": (
                event.primary_site.site_name if event.primary_site else None
            ),
            "divisions": [div.name for div in event.divisions.all()],
            "entry_fee": entry_fee,
            "gate_fee": gate_fee,
            "hotel_price": hotel_price,
            "hotel_info": hotel_info,
            "welcome_dinner_price": welcome_dinner_price,
            "uniform_package_price": uniform_package_price,
            "players": players_list,
        }

        return JsonResponse(data)


class EventCalendarView(StaffRequiredMixin, ListView):
    model = Event
    template_name = "events/calendar.html"
    context_object_name = "events"

    @method_decorator(xframe_options_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        # Obtener eventos del mes actual (solo publicados)
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(
            days=1
        )

        return (
            Event.objects.filter(
                status="published",
                start_date__gte=month_start,
                start_date__lte=month_end,
            )
            .select_related("category", "organizer")
            .order_by("start_date")
        )


class EventAttendanceView(LoginRequiredMixin, CreateView):
    model = EventAttendance
    fields = ["notes"]
    template_name = "events/attendance_form.html"

    def get_success_url(self):
        return reverse_lazy(
            "events:admin_detail", kwargs={"pk": self.kwargs["event_id"]}
        )

    def form_valid(self, form):
        event = get_object_or_404(Event, pk=self.kwargs["event_id"])

        # Verificar si ya está registrado
        if EventAttendance.objects.filter(event=event, user=self.request.user).exists():
            messages.error(self.request, "Ya estás registrado en este evento.")
            return self.form_invalid(form)

        # Verificar si el evento está lleno
        if event.is_full:
            messages.error(self.request, "Este evento está lleno.")
            return self.form_invalid(form)

        form.instance.event = event
        form.instance.user = self.request.user
        form.instance.status = "confirmed"

        messages.success(self.request, "Te has registrado exitosamente en el evento.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event"] = get_object_or_404(Event, pk=self.kwargs["event_id"])
        return context


class DashboardView(StaffRequiredMixin, TemplateView):
    template_name = "events/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Marcar la sección activa en el sidebar
        context["active_section"] = "dashboard"
        now = timezone.now()
        today = now.date()

        # Estadísticas generales (solo eventos publicados)
        total_events = Event.objects.filter(status="published").count()
        upcoming_events = Event.objects.filter(
            status="published", start_date__gt=today
        ).count()
        ongoing_events = Event.objects.filter(
            status="published", start_date__lte=today, end_date__gte=today
        ).count()
        past_events = Event.objects.filter(
            status="published", end_date__lt=today
        ).count()

        # Eventos de hoy (solo publicados)
        try:
            today_events = (
                Event.objects.filter(status="published", start_date=today)
                .select_related("category")
                .prefetch_related("divisions")
                .order_by("start_date")
            )
        except Exception:
            today_events = (
                Event.objects.filter(status="published", start_date=today)
                .select_related("category")
                .order_by("start_date")
            )

        today_events_count = today_events.count()

        # Próximos eventos (próximos 7 días, solo publicados)
        week_end = today + timedelta(days=7)
        try:
            upcoming_week = (
                Event.objects.filter(
                    status="published", start_date__gt=today, start_date__lte=week_end
                )
                .select_related("category")
                .prefetch_related("divisions")
                .order_by("start_date")[:5]
            )
        except Exception:
            upcoming_week = (
                Event.objects.filter(
                    status="published", start_date__gt=today, start_date__lte=week_end
                )
                .select_related("category")
                .order_by("start_date")[:5]
            )

        upcoming_week_count = Event.objects.filter(
            status="published", start_date__gt=today, start_date__lte=week_end
        ).count()

        # Eventos por categoría (solo publicados)
        events_by_category = (
            Event.objects.filter(status="published")
            .values("category__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )

        events_by_category_json = json.dumps(list(events_by_category))

        # Eventos por división (solo publicados)
        try:
            events_by_division = (
                Event.objects.filter(status="published")
                .values("divisions__name")
                .annotate(count=Count("id"))
                .order_by("-count")[:5]
            )
        except Exception:
            # Si la tabla no existe aún, retornar lista vacía
            events_by_division = []

        events_by_division_json = json.dumps(list(events_by_division))

        # Eventos más populares (por número de asistentes, solo publicados)
        popular_events = (
            Event.objects.filter(status="published")
            .annotate(attendee_count=Count("attendees"))
            .order_by("-attendee_count")[:5]
        )

        # Estadísticas de asistencia
        total_attendances = EventAttendance.objects.count()
        confirmed_attendances = EventAttendance.objects.filter(
            status="confirmed"
        ).count()

        # Eventos recientes (solo publicados)
        recent_events = Event.objects.filter(status="published").order_by(
            "-created_at"
        )[:5]

        # Estadísticas de usuarios
        try:
            from django.contrib.auth import get_user_model

            from apps.accounts.models import Player

            User = get_user_model()
            total_users = User.objects.count()
            active_users = User.objects.filter(is_active=True).count()
            total_players = Player.objects.count()
            recent_users = User.objects.select_related("profile").order_by(
                "-date_joined"
            )[:10]

            context.update(
                {
                    "total_events": total_events,
                    "upcoming_events": upcoming_events,
                    "ongoing_events": ongoing_events,
                    "past_events": past_events,
                    "today_events": today_events,
                    "today_events_count": today_events_count,
                    "upcoming_week": upcoming_week,
                    "upcoming_week_count": upcoming_week_count,
                    "events_by_category": events_by_category,
                    "events_by_category_json": events_by_category_json,
                    "events_by_division": events_by_division,
                    "events_by_division_json": events_by_division_json,
                    "popular_events": popular_events,
                    "total_attendances": total_attendances,
                    "confirmed_attendances": confirmed_attendances,
                    "recent_events": recent_events,
                    "total_users": total_users,
                    "active_users": active_users,
                    "total_players": total_players,
                    "recent_users": recent_users,
                }
            )
        except ImportError:
            context.update(
                {
                    "total_events": total_events,
                    "upcoming_events": upcoming_events,
                    "ongoing_events": ongoing_events,
                    "past_events": past_events,
                    "today_events": today_events,
                    "today_events_count": today_events_count,
                    "upcoming_week": upcoming_week,
                    "upcoming_week_count": upcoming_week_count,
                    "events_by_category": events_by_category,
                    "events_by_category_json": events_by_category_json,
                    "events_by_division": events_by_division,
                    "events_by_division_json": events_by_division_json,
                    "popular_events": popular_events,
                    "total_attendances": total_attendances,
                    "confirmed_attendances": confirmed_attendances,
                    "recent_events": recent_events,
                    "total_users": 0,
                    "active_users": 0,
                    "total_players": 0,
                    "recent_users": [],
                }
            )

        # Estadísticas de órdenes y reservas (solo para staff)
        orders_stats = {
            "total": 0,
            "pending": 0,
            "paid": 0,
            "cancelled": 0,
            "total_revenue": Decimal("0.00"),
            "monthly_revenue": Decimal("0.00"),
        }
        reservations_stats = {
            "total": 0,
            "pending": 0,
            "confirmed": 0,
            "checked_in": 0,
            "cancelled": 0,
            "revenue": Decimal("0.00"),
        }
        recent_orders = []
        upcoming_reservations = []

        if self.request.user.is_staff or self.request.user.is_superuser:
            try:
                from apps.accounts.models import Order
                from apps.locations.models import HotelReservation

                # Estadísticas de órdenes
                total_orders = Order.objects.count()
                pending_orders = Order.objects.filter(status="pending").count()
                paid_orders = Order.objects.filter(status="paid").count()
                cancelled_orders = Order.objects.filter(status="cancelled").count()

                # Ingresos
                total_revenue_result = Order.objects.filter(status="paid").aggregate(
                    total=Sum("total_amount")
                )
                total_revenue = total_revenue_result.get("total")
                if total_revenue is None:
                    total_revenue = Decimal("0.00")
                else:
                    total_revenue = Decimal(str(total_revenue))

                # Ingresos del mes actual
                current_month_start = now.replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0
                )
                monthly_revenue_result = Order.objects.filter(
                    status="paid", created_at__gte=current_month_start
                ).aggregate(total=Sum("total_amount"))
                monthly_revenue = monthly_revenue_result.get("total")
                if monthly_revenue is None:
                    monthly_revenue = Decimal("0.00")
                else:
                    monthly_revenue = Decimal(str(monthly_revenue))

                # Órdenes recientes
                recent_orders = list(
                    Order.objects.select_related("user", "event").order_by(
                        "-created_at"
                    )[:10]
                )

                orders_stats = {
                    "total": total_orders,
                    "pending": pending_orders,
                    "paid": paid_orders,
                    "cancelled": cancelled_orders,
                    "total_revenue": total_revenue,
                    "monthly_revenue": monthly_revenue,
                }

                # Estadísticas de reservas
                total_reservations = HotelReservation.objects.count()
                pending_reservations = HotelReservation.objects.filter(
                    status="pending"
                ).count()
                confirmed_reservations = HotelReservation.objects.filter(
                    status="confirmed"
                ).count()
                checked_in_reservations = HotelReservation.objects.filter(
                    status="checked_in"
                ).count()
                cancelled_reservations = HotelReservation.objects.filter(
                    status="cancelled"
                ).count()

                # Reservas próximas (check-in en los próximos 7 días)
                today_date = now.date()
                next_week = today_date + timedelta(days=7)
                upcoming_reservations = list(
                    HotelReservation.objects.filter(
                        status__in=["confirmed", "pending"],
                        check_in__gte=today_date,
                        check_in__lte=next_week,
                    )
                    .select_related("hotel", "room", "user")
                    .order_by("check_in")[:10]
                )

                # Ingresos de reservas
                reservations_revenue_result = HotelReservation.objects.filter(
                    status__in=["confirmed", "checked_in"]
                ).aggregate(total=Sum("total_amount"))
                reservations_revenue = reservations_revenue_result.get("total")
                if reservations_revenue is None:
                    reservations_revenue = Decimal("0.00")
                else:
                    reservations_revenue = Decimal(str(reservations_revenue))

                reservations_stats = {
                    "total": total_reservations,
                    "pending": pending_reservations,
                    "confirmed": confirmed_reservations,
                    "checked_in": checked_in_reservations,
                    "cancelled": cancelled_reservations,
                    "revenue": reservations_revenue,
                }

            except Exception as e:
                # Si hay algún error, registrar pero continuar con stats vacíos
                import logging

                logger = logging.getLogger(__name__)
                logger.error(
                    f"Error al obtener estadísticas de órdenes y reservas: {e}",
                    exc_info=True,
                )

        # Actualizar el contexto con las estadísticas de órdenes y reservas
        context.update(
            {
                "orders_stats": orders_stats,
                "reservations_stats": reservations_stats,
                "recent_orders": recent_orders,
                "upcoming_reservations": upcoming_reservations,
            }
        )

        # Alertas / pendientes (contenido accionable)
        missing_dates_events = (
            Event.objects.filter(Q(start_date__isnull=True) | Q(end_date__isnull=True))
            .select_related("category")
            .order_by("-created_at")[:5]
        )
        draft_events_count = Event.objects.filter(status="draft").count()
        missing_dates_count = Event.objects.filter(
            Q(start_date__isnull=True) | Q(end_date__isnull=True)
        ).count()

        entry_deadline_soon_events = (
            Event.objects.filter(
                entry_deadline__isnull=False,
                entry_deadline__gte=today,
                entry_deadline__lte=today + timedelta(days=7),
            )
            .select_related("category")
            .order_by("entry_deadline")[:5]
        )
        entry_deadline_soon_count = Event.objects.filter(
            entry_deadline__isnull=False,
            entry_deadline__gte=today,
            entry_deadline__lte=today + timedelta(days=7),
        ).count()

        context.update(
            {
                "draft_events_count": draft_events_count,
                "missing_dates_events": missing_dates_events,
                "missing_dates_count": missing_dates_count,
                "entry_deadline_soon_events": entry_deadline_soon_events,
                "entry_deadline_soon_count": entry_deadline_soon_count,
            }
        )

        return context


# ===== DIVISION VIEWS =====
class DivisionListView(StaffRequiredMixin, ListView):
    model = Division
    template_name = "events/division_list.html"
    context_object_name = "divisions"
    paginate_by = 20

    def get_queryset(self):
        queryset = Division.objects.all()
        search = self.request.GET.get("search")
        skill_level = self.request.GET.get("skill_level")
        status = self.request.GET.get("status")
        sort = self.request.GET.get("sort", "name")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(description__icontains=search)
                | Q(skill_level__icontains=search)
            )
        if skill_level:
            queryset = queryset.filter(skill_level__icontains=skill_level)
        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)

        # Ordenamiento
        if sort == "name":
            queryset = queryset.order_by("name")
        elif sort == "age_min":
            queryset = queryset.order_by("age_min")
        elif sort == "skill_level":
            queryset = queryset.order_by("skill_level")
        elif sort == "created":
            queryset = queryset.order_by("-created_at")
        else:
            queryset = queryset.order_by("name")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["skill_level_filter"] = self.request.GET.get("skill_level", "")
        context["status_filter"] = self.request.GET.get("status", "")
        context["sort_filter"] = self.request.GET.get("sort", "name")
        context["active_section"] = "configuration"
        context["active_subsection"] = "division_list"
        return context


class DivisionDetailView(StaffRequiredMixin, DetailView):
    model = Division
    template_name = "events/division_detail.html"
    context_object_name = "division"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["events"] = self.object.events.filter(status="published").order_by(
            "-start_date"
        )[:10]
        context["events_count"] = self.object.events.count()
        context["active_section"] = "configuration"
        context["active_subsection"] = "division_list"
        return context


class DivisionCreateView(StaffRequiredMixin, CreateView):
    model = Division
    template_name = "events/division_form.html"
    fields = ["name", "description", "age_min", "age_max", "skill_level", "is_active"]
    success_url = reverse_lazy("events:division_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "configuration"
        context["active_subsection"] = "division_list"
        return context

    def form_valid(self, form):
        messages.success(self.request, "División creada exitosamente.")
        return super().form_valid(form)


class DivisionUpdateView(StaffRequiredMixin, UpdateView):
    model = Division
    template_name = "events/division_form.html"
    fields = ["name", "description", "age_min", "age_max", "skill_level", "is_active"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "configuration"
        context["active_subsection"] = "division_list"
        return context

    def get_success_url(self):
        return reverse_lazy("events:division_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "División actualizada exitosamente.")
        return super().form_valid(form)


class DivisionDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Division
    template_name = "events/division_confirm_delete.html"
    success_url = reverse_lazy("events:division_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "configuration"
        context["active_subsection"] = "division_list"
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "División eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)


class GetEventRecipientsView(StaffRequiredMixin, View):
    """Vista AJAX para obtener la lista de destinatarios filtrados"""

    def get(self, request, pk):
        from apps.accounts.models import Order, Player, PlayerParent

        event = get_object_or_404(Event, pk=pk)
        recipient_filter = request.GET.get("filter", "all")

        # Obtener los jugadores registrados según el filtro
        # Los jugadores están relacionados a través de las órdenes pagadas
        paid_orders = Order.objects.filter(event=event, status="paid").values_list(
            "registered_player_ids", flat=True
        )

        # Obtener todos los IDs únicos de jugadores
        player_ids = set()
        for player_ids_list in paid_orders:
            if player_ids_list:
                player_ids.update(player_ids_list)

        # Obtener los jugadores
        registered_players = Player.objects.filter(id__in=player_ids).select_related(
            "user"
        )

        # Filtrar por división si es necesario
        if recipient_filter.startswith("division_"):
            division_id = recipient_filter.replace("division_", "")
            try:
                division = Division.objects.get(pk=division_id)
                registered_players = registered_players.filter(division=division)
            except Division.DoesNotExist:
                return JsonResponse(
                    {"success": False, "error": "División no encontrada"}, status=404
                )

        # Obtener emails únicos de los padres
        parent_data = {}

        for player in registered_players:
            # Obtener el padre principal del jugador
            parent_relation = (
                PlayerParent.objects.filter(player=player, is_primary=True)
                .select_related("parent")
                .first()
            )

            if not parent_relation:
                # Si no hay padre principal, tomar el primero
                parent_relation = (
                    PlayerParent.objects.filter(player=player)
                    .select_related("parent")
                    .first()
                )

            if parent_relation and parent_relation.parent:
                parent = parent_relation.parent
                email = parent.email
                if email:
                    if email not in parent_data:
                        parent_data[email] = {
                            "id": parent.id,
                            "name": parent.get_full_name() or parent.username,
                            "email": email,
                            "players_count": 0,
                        }
                    parent_data[email]["players_count"] += 1

        recipients = list(parent_data.values())

        return JsonResponse(
            {"success": True, "recipients": recipients, "count": len(recipients)}
        )


class SendEventEmailView(StaffRequiredMixin, View):
    """Vista para enviar emails masivos a los registrados de un evento"""

    def post(self, request, pk):
        from django.conf import settings
        from django.core.mail import send_mass_mail

        from apps.accounts.models import Order, Player, PlayerParent

        event = get_object_or_404(Event, pk=pk)

        # Obtener datos del formulario
        recipient_filter = request.POST.get("recipient_filter", "all")
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()

        if not subject or not message:
            messages.error(request, "El asunto y el mensaje son requeridos.")
            return JsonResponse(
                {"success": False, "error": "Asunto y mensaje requeridos"}, status=400
            )

        # Obtener los jugadores registrados según el filtro
        # Los jugadores están relacionados a través de las órdenes pagadas
        paid_orders = Order.objects.filter(event=event, status="paid").values_list(
            "registered_player_ids", flat=True
        )

        # Obtener todos los IDs únicos de jugadores
        player_ids = set()
        for player_ids_list in paid_orders:
            if player_ids_list:
                player_ids.update(player_ids_list)

        # Obtener los jugadores
        registered_players = Player.objects.filter(id__in=player_ids).select_related(
            "user"
        )

        # Filtrar por división si es necesario
        if recipient_filter.startswith("division_"):
            division_id = recipient_filter.replace("division_", "")
            try:
                division = Division.objects.get(pk=division_id)
                registered_players = registered_players.filter(division=division)
            except Division.DoesNotExist:
                messages.error(request, "División no encontrada.")
                return JsonResponse(
                    {"success": False, "error": "División no encontrada"}, status=404
                )

        # Obtener emails únicos de los padres
        parent_emails = set()
        parent_data = {}

        for player in registered_players:
            # Obtener el padre principal del jugador
            parent_relation = (
                PlayerParent.objects.filter(player=player, is_primary=True)
                .select_related("parent")
                .first()
            )

            if not parent_relation:
                # Si no hay padre principal, tomar el primero
                parent_relation = (
                    PlayerParent.objects.filter(player=player)
                    .select_related("parent")
                    .first()
                )

            if parent_relation and parent_relation.parent:
                parent = parent_relation.parent
                email = parent.email
                if email:
                    parent_emails.add(email)
                    if email not in parent_data:
                        parent_data[email] = {
                            "name": parent.get_full_name() or parent.username,
                            "players": [],
                        }
                    # Obtener nombre del jugador desde el user
                    player_name = (
                        f"{player.user.first_name} {player.user.last_name}"
                        if player.user
                        else "Jugador"
                    )
                    parent_data[email]["players"].append(player_name)

        if not parent_emails:
            messages.warning(request, "No se encontraron destinatarios válidos.")
            return JsonResponse(
                {"success": False, "error": "No hay destinatarios"}, status=400
            )

        # Preparar mensajes personalizados
        email_messages = []
        from_email = settings.DEFAULT_FROM_EMAIL

        for email in parent_emails:
            data = parent_data[email]
            # Personalizar mensaje con nombre del padre y jugadores
            personalized_message = f"Hola {data['name']},\n\n{message}\n\n"
            personalized_message += (
                f"Este mensaje es para los jugadores: {', '.join(data['players'])}\n\n"
            )
            personalized_message += f"Atentamente,\nEquipo de {event.title}"

            email_messages.append((subject, personalized_message, from_email, [email]))

        try:
            # Enviar todos los emails
            send_mass_mail(email_messages, fail_silently=False)
            messages.success(
                request,
                f"Se enviaron {len(email_messages)} email{'s' if len(email_messages) != 1 else ''} exitosamente.",
            )
            return JsonResponse(
                {
                    "success": True,
                    "sent_count": len(email_messages),
                    "redirect_url": reverse_lazy(
                        "events:admin_detail", kwargs={"pk": pk}
                    ),
                }
            )
        except Exception as e:
            messages.error(request, f"Error al enviar emails: {str(e)}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
def get_event_services(request, event_id):
    """API para obtener servicios adicionales disponibles de un evento"""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    try:
        event = Event.objects.get(id=event_id, status="published")
        services = event.additional_services.filter(is_active=True).order_by(
            "order", "service_name"
        )

        services_data = []
        for service in services:
            services_data.append(
                {
                    "id": service.id,
                    "service_name": service.service_name,
                    "service_type": service.get_service_type_display(),
                    "price": str(service.price),
                    "is_per_person": service.is_per_person,
                    "is_per_night": service.is_per_night,
                    "description": service.description or "",
                }
            )

        return JsonResponse({"services": services_data}, safe=False)
    except Event.DoesNotExist:
        return JsonResponse({"error": "Event not found"}, status=404)
