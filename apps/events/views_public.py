"""
Vistas públicas de eventos - No requieren autenticación
"""

from datetime import timedelta

from django.db.models import Case, IntegerField, Q, Value, When
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView

from .models import Event, EventCategory, EventType


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
        time_filter = self.request.GET.get("time_filter")

        if search:
            # Buscar en título, descripción, ubicación y nombre del tipo de evento
            search_lower = search.lower()
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(location__icontains=search)
                | Q(event_type__name__icontains=search)
            )

            # Si la búsqueda es "showcase" o "gateway", también intentar filtrar por tipo de evento
            if search_lower in ["showcase", "gateway"]:
                # Buscar tipos de eventos que contengan la palabra en su nombre
                matching_types = EventType.objects.filter(
                    name__icontains=search,
                    is_active=True
                )
                if matching_types.exists():
                    # Si hay tipos que coinciden, filtrar por esos tipos
                    queryset = queryset.filter(event_type__in=matching_types)

        if category:
            queryset = queryset.filter(category__id=category)

        if event_type:
            queryset = queryset.filter(event_type__id=event_type)

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
        return context


class PublicEventDetailView(DetailView):
    """Vista pública de detalle de evento - No requiere autenticación"""

    model = Event
    template_name = "events/public_detail.html"
    context_object_name = "event"

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
        return context



