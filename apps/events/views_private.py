"""
Vistas privadas de eventos - Requieren autenticación
"""

from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from .models import Event, EventAttendance, EventCategory
from .forms import EventForm
from apps.core.mixins import OwnerOrStaffRequiredMixin


class PrivateEventListView(LoginRequiredMixin, ListView):
    """Lista de eventos para usuarios autenticados"""

    model = Event
    template_name = "events/list.html"
    context_object_name = "events"
    paginate_by = 20

    def get_queryset(self):
        queryset = Event.objects.select_related("category", "organizer")

        # Si no es staff, solo ver eventos publicados o donde es organizador
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            queryset = queryset.filter(
                Q(status="published") | Q(organizer=self.request.user)
            )
        else:
            # Staff puede ver todos
            queryset = queryset.all()

        # Filtros
        search = self.request.GET.get("search")
        category = self.request.GET.get("category")
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

        return queryset.order_by("-start_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = EventCategory.objects.filter(is_active=True)
        context["status_choices"] = Event.STATUS_CHOICES
        context["time_filters"] = [
            ("upcoming", "Próximos"),
            ("ongoing", "En curso"),
            ("past", "Pasados"),
            ("today", "Hoy"),
        ]
        return context


class PrivateEventDetailView(LoginRequiredMixin, DetailView):
    """Detalle de evento para usuarios autenticados"""

    model = Event
    template_name = "events/detail.html"
    context_object_name = "event"

    def get_queryset(self):
        queryset = Event.objects.all()
        # Si no es staff, solo ver eventos publicados o donde es organizador
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            queryset = queryset.filter(
                Q(status="published") | Q(organizer=self.request.user)
            )
        return queryset

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

        return context


class EventUpdateView(OwnerOrStaffRequiredMixin, UpdateView):
    """Actualizar evento - Solo el organizador o staff"""

    model = Event
    fields = [
        "title",
        "description",
        "start_date",
        "end_date",
        "location",
        "category",
        "status",
    ]
    template_name = "events/form.html"

    def get_success_url(self):
        return reverse_lazy("events:private_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Evento actualizado exitosamente.")
        return super().form_valid(form)


class EventCalendarView(LoginRequiredMixin, ListView):
    """Calendario de eventos"""

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

        queryset = Event.objects.filter(
            start_date__gte=month_start, start_date__lte=month_end
        ).select_related("category", "organizer")

        # Si no es staff, solo ver eventos publicados
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            queryset = queryset.filter(status="published")

        return queryset.order_by("start_date")


class EventAttendanceView(LoginRequiredMixin, CreateView):
    """Registrarse a un evento"""

    model = EventAttendance
    fields = ["notes"]
    template_name = "events/attendance_form.html"

    def get_success_url(self):
        return reverse_lazy(
            "events:private_detail", kwargs={"pk": self.kwargs["event_id"]}
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


class EventCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear eventos"""

    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = reverse_lazy("events:list")

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        messages.success(self.request, "Evento creado exitosamente.")
        return super().form_valid(form)


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard de eventos"""

    template_name = "events/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        # Si es staff, mostrar todas las estadísticas
        if self.request.user.is_staff or self.request.user.is_superuser:
            total_events = Event.objects.count()
            upcoming_events = Event.objects.filter(start_date__gt=now).count()
            ongoing_events = Event.objects.filter(
                start_date__lte=now, end_date__gte=now
            ).count()
            past_events = Event.objects.filter(end_date__lt=now).count()

            try:
                today_events = (
                    Event.objects.filter(
                        start_date__gte=now.replace(
                            hour=0, minute=0, second=0, microsecond=0
                        ),
                        start_date__lt=now.replace(
                            hour=0, minute=0, second=0, microsecond=0
                        )
                        + timedelta(days=1),
                    )
                    .select_related("category")
                    .prefetch_related("divisions")
                    .order_by("start_date")
                )
            except Exception:
                today_events = (
                    Event.objects.filter(
                        start_date__gte=now.replace(
                            hour=0, minute=0, second=0, microsecond=0
                        ),
                        start_date__lt=now.replace(
                            hour=0, minute=0, second=0, microsecond=0
                        )
                        + timedelta(days=1),
                    )
                    .select_related("category")
                    .order_by("start_date")
                )

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

            total_attendances = EventAttendance.objects.count()
            confirmed_attendances = EventAttendance.objects.filter(
                status="confirmed"
            ).count()

            try:
                recent_events = (
                    Event.objects.select_related("category")
                    .prefetch_related("divisions")
                    .order_by("-created_at")[:5]
                )
            except Exception:
                recent_events = Event.objects.select_related("category").order_by(
                    "-created_at"
                )[:5]
        else:
            # Usuario regular solo ve eventos publicados o propios
            total_events = Event.objects.filter(
                Q(status="published") | Q(organizer=self.request.user)
            ).count()
            upcoming_events = Event.objects.filter(
                Q(status="published") | Q(organizer=self.request.user),
                start_date__gt=now,
            ).count()
            ongoing_events = Event.objects.filter(
                Q(status="published") | Q(organizer=self.request.user),
                start_date__lte=now,
                end_date__gte=now,
            ).count()
            past_events = Event.objects.filter(
                Q(status="published") | Q(organizer=self.request.user), end_date__lt=now
            ).count()

            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            try:
                today_events = (
                    Event.objects.filter(
                        Q(status="published") | Q(organizer=self.request.user),
                        start_date__gte=today_start,
                        start_date__lt=today_end,
                    )
                    .select_related("category")
                    .prefetch_related("divisions")
                    .order_by("start_date")
                )
            except Exception:
                today_events = (
                    Event.objects.filter(
                        Q(status="published") | Q(organizer=self.request.user),
                        start_date__gte=today_start,
                        start_date__lt=today_end,
                    )
                    .select_related("category")
                    .order_by("start_date")
                )

            week_end = now + timedelta(days=7)
            try:
                upcoming_week = (
                    Event.objects.filter(
                        Q(status="published") | Q(organizer=self.request.user),
                        start_date__gt=now,
                        start_date__lte=week_end,
                    )
                    .select_related("category")
                    .prefetch_related("divisions")
                    .order_by("start_date")[:5]
                )
            except Exception:
                upcoming_week = (
                    Event.objects.filter(
                        Q(status="published") | Q(organizer=self.request.user),
                        start_date__gt=now,
                        start_date__lte=week_end,
                    )
                    .select_related("category")
                    .order_by("start_date")[:5]
                )

            total_attendances = EventAttendance.objects.filter(
                event__in=Event.objects.filter(
                    Q(status="published") | Q(organizer=self.request.user)
                )
            ).count()
            confirmed_attendances = EventAttendance.objects.filter(
                status="confirmed",
                event__in=Event.objects.filter(
                    Q(status="published") | Q(organizer=self.request.user)
                ),
            ).count()

            try:
                recent_events = (
                    Event.objects.filter(
                        Q(status="published") | Q(organizer=self.request.user)
                    )
                    .select_related("category")
                    .prefetch_related("divisions")
                    .order_by("-created_at")[:5]
                )
            except Exception:
                recent_events = (
                    Event.objects.filter(
                        Q(status="published") | Q(organizer=self.request.user)
                    )
                    .select_related("category")
                    .order_by("-created_at")[:5]
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

        # Eventos más populares
        popular_events = Event.objects.annotate(
            attendee_count=Count("attendees")
        ).order_by("-attendee_count")[:5]

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
            }
        )

        return context
