from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils import timezone
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

from .forms import EventForm
from .models import Division, Event, EventAttendance, EventCategory


class EventListView(LoginRequiredMixin, ListView):
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

        if status:
            queryset = queryset.filter(status=status)

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

        # Ordenar por fecha de inicio más próxima primero
        return queryset.order_by("start_date")

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
        return context


class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = "events/detail.html"
    context_object_name = "event"

    def get_queryset(self):
        """
        Admin/detail view.

        - Staff: can view any event (published/draft/etc.)
        - Non-staff: only published events
        """
        base_qs = Event.objects.all() if self.request.user.is_staff else Event.objects.filter(status="published")

        # Optimizar consultas relacionadas para mejor rendimiento
        return (
            base_qs.select_related(
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
            )
            .prefetch_related(
                "divisions",
                "additional_sites__city",
                "additional_sites__state",
                "additional_hotels__city",
                "additional_hotels__state",
                "event_contact",
            )
        )

    def get_context_data(self, **kwargs):
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

        return context


class EventCreateView(LoginRequiredMixin, CreateView):
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
        messages.success(self.request, "Evento creado exitosamente.")
        return super().form_valid(form)


class EventUpdateView(LoginRequiredMixin, UpdateView):
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
        messages.success(self.request, "Evento actualizado exitosamente.")
        return super().form_valid(form)


class EventDeleteView(LoginRequiredMixin, DeleteView):
    model = Event
    template_name = "events/confirm_delete.html"
    success_url = reverse_lazy("events:list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Evento eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)


class EventTogglePublishView(LoginRequiredMixin, View):
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


class EventDetailAPIView(LoginRequiredMixin, View):
    """API view para obtener detalles del evento en JSON"""

    def get(self, request, pk):
        from apps.accounts.models import Player, PlayerParent

        event = get_object_or_404(
            Event.objects.all().select_related(
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
            ).prefetch_related("divisions"),
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


class EventCalendarView(LoginRequiredMixin, ListView):
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
                start_date__lte=month_end
            )
            .select_related("category", "organizer")
            .order_by("start_date")
        )


class EventAttendanceView(LoginRequiredMixin, CreateView):
    model = EventAttendance
    fields = ["notes"]
    template_name = "events/attendance_form.html"

    def get_success_url(self):
        return reverse_lazy("events:admin_detail", kwargs={"pk": self.kwargs["event_id"]})

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


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "events/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Marcar la sección activa en el sidebar
        context["active_section"] = "dashboard"
        now = timezone.now()

        # Estadísticas generales (solo eventos publicados)
        total_events = Event.objects.filter(status="published").count()
        upcoming_events = Event.objects.filter(status="published", start_date__gt=now).count()
        ongoing_events = Event.objects.filter(
            status="published", start_date__lte=now, end_date__gte=now
        ).count()
        past_events = Event.objects.filter(status="published", end_date__lt=now).count()

        # Eventos de hoy (solo publicados)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        try:
            today_events = (
                Event.objects.filter(
                    status="published",
                    start_date__gte=today_start, start_date__lt=today_end
                )
                .select_related("category")
                .prefetch_related("divisions")
                .order_by("start_date")
            )
        except Exception:
            today_events = (
                Event.objects.filter(
                    status="published",
                    start_date__gte=today_start, start_date__lt=today_end
                )
                .select_related("category")
                .order_by("start_date")
            )

        # Próximos eventos (próximos 7 días, solo publicados)
        week_end = now + timedelta(days=7)
        try:
            upcoming_week = (
                Event.objects.filter(
                    status="published",
                    start_date__gt=now, start_date__lte=week_end
                )
                .select_related("category")
                .prefetch_related("divisions")
                .order_by("start_date")[:5]
            )
        except Exception:
            upcoming_week = (
                Event.objects.filter(
                    status="published",
                    start_date__gt=now, start_date__lte=week_end
                )
                .select_related("category")
                .order_by("start_date")[:5]
            )

        # Eventos por categoría (solo publicados)
        events_by_category = (
            Event.objects.filter(status="published")
            .values("category__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )

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

        # Eventos más populares (por número de asistentes, solo publicados)
        popular_events = Event.objects.filter(status="published").annotate(
            attendee_count=Count("attendees")
        ).order_by("-attendee_count")[:5]

        # Estadísticas de asistencia
        total_attendances = EventAttendance.objects.count()
        confirmed_attendances = EventAttendance.objects.filter(
            status="confirmed"
        ).count()

        # Eventos recientes (solo publicados)
        recent_events = Event.objects.filter(status="published").order_by("-created_at")[:5]

        # Estadísticas de usuarios
        try:
            from django.contrib.auth import get_user_model

            from apps.accounts.models import Player, UserProfile

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
                    "upcoming_week": upcoming_week,
                    "events_by_category": events_by_category,
                    "events_by_division": events_by_division,
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
                    "upcoming_week": upcoming_week,
                    "events_by_category": events_by_category,
                    "events_by_division": events_by_division,
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

        return context


# ===== DIVISION VIEWS =====
class DivisionListView(LoginRequiredMixin, ListView):
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


class DivisionDetailView(LoginRequiredMixin, DetailView):
    model = Division
    template_name = "events/division_detail.html"
    context_object_name = "division"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["events"] = self.object.events.filter(status="published").order_by("-start_date")[:10]
        context["events_count"] = self.object.events.count()
        context["active_section"] = "configuration"
        context["active_subsection"] = "division_list"
        return context


class DivisionCreateView(LoginRequiredMixin, CreateView):
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


class DivisionUpdateView(LoginRequiredMixin, UpdateView):
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


class DivisionDeleteView(LoginRequiredMixin, DeleteView):
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
