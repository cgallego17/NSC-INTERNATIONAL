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
        queryset = Event.objects.select_related("category", "organizer").all()

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

        return queryset

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

        return context


class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = "events/form.html"
    success_url = reverse_lazy("events:list")

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        messages.success(self.request, "Evento creado exitosamente.")
        return super().form_valid(form)


class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = "events/form.html"

    def get_success_url(self):
        return reverse_lazy("events:detail", kwargs={"pk": self.object.pk})

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
        today_events = (
            Event.objects.filter(start_date__gte=today_start, start_date__lt=today_end)
            .select_related("category", "division")
            .order_by("start_date")
        )

        # Próximos eventos (próximos 7 días)
        week_end = now + timedelta(days=7)
        upcoming_week = (
            Event.objects.filter(start_date__gt=now, start_date__lte=week_end)
            .select_related("category", "division")
            .order_by("start_date")[:5]
        )

        # Eventos por categoría
        events_by_category = (
            Event.objects.values("category__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )

        # Eventos por división
        events_by_division = (
            Event.objects.values("division__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )

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
