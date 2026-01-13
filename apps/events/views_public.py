"""
Vistas públicas de eventos - No requieren autenticación
"""

from datetime import timedelta

from django.db.models import Case, IntegerField, Q, Value, When
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView

from .models import Event, EventCategory, EventType, EventView


class PublicEventListView(ListView):
    """Lista pública de eventos - No requiere autenticación"""

    model = Event
    template_name = "events/public_list.html"
    context_object_name = "events"
    paginate_by = 12

    def get_queryset(self):
        # Solo mostrar eventos publicados y no cancelados
        now = timezone.now().date()
        queryset = (
            Event.objects.filter(status="published")
            .exclude(status="cancelled")
            .select_related("category", "event_type", "country", "state", "city")
            .prefetch_related("divisions")
        )

        # Filtros
        search = self.request.GET.get("search")
        category = self.request.GET.get("category")
        event_type = self.request.GET.get("event_type")
        country = self.request.GET.get("country")
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

        if country:
            queryset = queryset.filter(country__id=country)

        if time_filter:
            if time_filter == "upcoming":
                queryset = queryset.filter(start_date__gt=now)
            elif time_filter == "ongoing":
                queryset = queryset.filter(start_date__lte=now, end_date__gte=now)
            elif time_filter == "past":
                queryset = queryset.filter(end_date__lt=now)
            elif time_filter == "today":
                queryset = queryset.filter(start_date=now)

        # Ordenar: eventos futuros primero (por start_date ascendente), luego pasados (por start_date descendente)
        queryset = queryset.annotate(
            is_future=Case(
                When(start_date__gte=now, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by("-is_future", "start_date")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = EventCategory.objects.filter(is_active=True)
        context["event_types"] = EventType.objects.filter(is_active=True)
        context["time_filters"] = [
            ("upcoming", _("Upcoming")),
            ("ongoing", _("Ongoing")),
            ("past", _("Past")),
            ("today", _("Today")),
        ]
        # Obtener países que tienen eventos publicados
        try:
            from apps.locations.models import Country

            # Obtener países únicos que tienen eventos publicados y no cancelados
            countries_with_events = (
                Country.objects.filter(events__status="published")
                .exclude(events__status="cancelled")
                .distinct()
                .order_by("name")
            )
            context["countries"] = countries_with_events
        except ImportError:
            context["countries"] = []
        return context


class PublicEventDetailView(DetailView):
    """Vista pública de detalle de evento - No requiere autenticación"""

    model = Event
    template_name = "events/public_detail.html"
    context_object_name = "event"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.record_view(request)
        return response

    def record_view(self, request):
        try:
            event = self.object
            ip = self.get_client_ip(request)

            # Verificar si ya existe una visita para este evento e IP
            if not EventView.objects.filter(event=event, ip_address=ip).exists():
                # Crear registro de visita
                EventView.objects.create(
                    event=event,
                    ip_address=ip,
                    user=request.user if request.user.is_authenticated else None,
                    session_key=request.session.session_key,
                )

                # Incrementar contador en el evento
                event.views += 1
                event.save(update_fields=["views"])
        except Exception:
            # Ignorar errores al registrar visita para no afectar la experiencia del usuario
            pass

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def get_queryset(self):
        # Solo mostrar eventos publicados y no cancelados
        return (
            Event.objects.filter(status="published")
            .exclude(status="cancelled")
            .select_related(
                "category",
                "event_type",
                "country",
                "state",
                "city",
                "primary_site",
                "hotel",
            )
            .prefetch_related("divisions", "additional_sites", "additional_hotels")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener eventos relacionados
        event = context["event"]
        context["related_events"] = (
            Event.objects.filter(status="published")
            .exclude(status="cancelled")
            .exclude(pk=event.pk)
            .filter(Q(category=event.category) | Q(event_type=event.event_type))
            .select_related("category", "event_type", "city", "state")
            .order_by("start_date")[:6]
        )

        # Obtener includes filtrados por user_type y activos
        try:
            from .models import EventIncludes

            context["includes_player"] = EventIncludes.objects.filter(
                event=event, user_type="player", is_active=True
            ).order_by("order", "title")
            context["includes_team_manager"] = EventIncludes.objects.filter(
                event=event, user_type="team_manager", is_active=True
            ).order_by("order", "title")
            context["includes_spectator"] = EventIncludes.objects.filter(
                event=event, user_type="spectator", is_active=True
            ).order_by("order", "title")
        except ImportError:
            context["includes_player"] = []
            context["includes_team_manager"] = []
            context["includes_spectator"] = []

        return context
