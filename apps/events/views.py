from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
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
        queryset = Event.objects.select_related(
            "category", "organizer", "event_type", "country", "state", "city"
        ).all()

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
        return context


class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = "events/detail.html"
    context_object_name = "event"

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

        # Optimizar consultas relacionadas para mejor rendimiento
        event = (
            Event.objects.select_related(
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
            .get(pk=self.object.pk)
        )
        context["event"] = event

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
        from .models import Division
        import json

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
        return reverse_lazy("events:detail", kwargs={"pk": self.object.pk})

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


class EventCalendarView(LoginRequiredMixin, ListView):
    model = Event
    template_name = "events/calendar.html"
    context_object_name = "events"

    def get_queryset(self):
        # Obtener eventos del mes actual
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(
            days=1
        )

        return (
            Event.objects.filter(start_date__gte=month_start, start_date__lte=month_end)
            .select_related("category", "organizer")
            .order_by("start_date")
        )


class EventAttendanceView(LoginRequiredMixin, CreateView):
    model = EventAttendance
    fields = ["notes"]
    template_name = "events/attendance_form.html"

    def get_success_url(self):
        return reverse_lazy("events:detail", kwargs={"pk": self.kwargs["event_id"]})

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

        # Estadísticas generales
        total_events = Event.objects.count()
        upcoming_events = Event.objects.filter(start_date__gt=now).count()
        ongoing_events = Event.objects.filter(
            start_date__lte=now, end_date__gte=now
        ).count()
        past_events = Event.objects.filter(end_date__lt=now).count()

        # Eventos de hoy
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        try:
            today_events = (
                Event.objects.filter(
                    start_date__gte=today_start, start_date__lt=today_end
                )
                .select_related("category")
                .prefetch_related("divisions")
                .order_by("start_date")
            )
        except Exception:
            today_events = (
                Event.objects.filter(
                    start_date__gte=today_start, start_date__lt=today_end
                )
                .select_related("category")
                .order_by("start_date")
            )

        # Próximos eventos (próximos 7 días)
        week_end = now + timedelta(days=7)
        try:
            upcoming_week = (
                Event.objects.filter(start_date__gt=now, start_date__lte=week_end)
                .select_related("category")
                .prefetch_related("divisions")
                .order_by("start_date")[:5]
            )
        except Exception:
            upcoming_week = (
                Event.objects.filter(start_date__gt=now, start_date__lte=week_end)
                .select_related("category")
                .order_by("start_date")[:5]
            )

        # Eventos por categoría
        events_by_category = (
            Event.objects.values("category__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )

        # Eventos por división
        try:
            events_by_division = (
                Event.objects.values("divisions__name")
                .annotate(count=Count("id"))
                .order_by("-count")[:5]
            )
        except Exception:
            # Si la tabla no existe aún, retornar lista vacía
            events_by_division = []

        # Eventos más populares (por número de asistentes)
        popular_events = Event.objects.annotate(
            attendee_count=Count("attendees")
        ).order_by("-attendee_count")[:5]

        # Estadísticas de asistencia
        total_attendances = EventAttendance.objects.count()
        confirmed_attendances = EventAttendance.objects.filter(
            status="confirmed"
        ).count()

        # Eventos recientes
        recent_events = Event.objects.order_by("-created_at")[:5]

        # Estadísticas de usuarios
        try:
            from django.contrib.auth import get_user_model
            from apps.accounts.models import UserProfile, Player

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
        context["events"] = self.object.events.all().order_by("-start_date")[:10]
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
