"""
Vistas administrativas de ubicaciones - Solo staff/superuser, CRUD completo
"""

from django.contrib import messages
from django.db.models import Q, Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .models import (
    City,
    Country,
    Hotel,
    HotelAmenity,
    HotelImage,
    HotelReservation,
    HotelRoom,
    HotelRoomImage,
    HotelRoomRule,
    HotelService,
    Rule,
    Season,
    Site,
    State,
)
from .forms import HotelForm
from apps.core.mixins import StaffRequiredMixin
from apps.media.models import MediaFile
from pathlib import Path


# ===== COUNTRY VIEWS (Admin) =====
class AdminCountryListView(StaffRequiredMixin, ListView):
    """Lista administrativa de países"""

    model = Country
    template_name = "locations/country_list.html"
    context_object_name = "countries"
    paginate_by = 20

    def get_queryset(self):
        queryset = Country.objects.all()
        search = self.request.GET.get("search")
        status = self.request.GET.get("status")
        sort = self.request.GET.get("sort", "name")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(code__icontains=search)
            )

        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)

        # Ordenamiento
        if sort == "name":
            queryset = queryset.order_by("name")
        elif sort == "code":
            queryset = queryset.order_by("code")
        elif sort == "created":
            queryset = queryset.order_by("-created_at")
        else:
            queryset = queryset.order_by("name")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["status_filter"] = self.request.GET.get("status", "")
        context["sort_filter"] = self.request.GET.get("sort", "name")
        context["is_admin"] = True
        return context


class AdminCountryDetailView(StaffRequiredMixin, DetailView):
    """Detalle administrativo de país"""

    model = Country
    template_name = "locations/country_detail.html"
    context_object_name = "country"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["states"] = self.object.states.order_by("name")
        context["states_count"] = self.object.states.count()
        context["cities_count"] = City.objects.filter(
            state__country=self.object
        ).count()
        context["is_admin"] = True
        return context


class AdminCountryCreateView(StaffRequiredMixin, CreateView):
    """Crear país - Solo admin"""

    model = Country
    template_name = "locations/country_form.html"
    fields = ["name", "code", "is_active"]
    success_url = reverse_lazy("locations:admin_country_list")

    def form_valid(self, form):
        messages.success(self.request, "País creado exitosamente.")
        return super().form_valid(form)


class AdminCountryUpdateView(StaffRequiredMixin, UpdateView):
    """Actualizar país - Solo admin"""

    model = Country
    template_name = "locations/country_form.html"
    fields = ["name", "code", "is_active"]

    def get_success_url(self):
        return reverse_lazy(
            "locations:admin_country_detail", kwargs={"pk": self.object.pk}
        )

    def form_valid(self, form):
        messages.success(self.request, "País actualizado exitosamente.")
        return super().form_valid(form)


class AdminCountryDeleteView(StaffRequiredMixin, DeleteView):
    """Eliminar país - Solo admin"""

    model = Country
    template_name = "locations/country_confirm_delete.html"
    success_url = reverse_lazy("locations:admin_country_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "País eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)


# ===== STATE VIEWS (Admin) =====
class AdminStateListView(StaffRequiredMixin, ListView):
    """Lista administrativa de estados"""

    model = State
    template_name = "locations/state_list.html"
    context_object_name = "states"
    paginate_by = 20

    def get_queryset(self):
        queryset = State.objects.select_related("country").all()
        search = self.request.GET.get("search")
        country = self.request.GET.get("country")
        status = self.request.GET.get("status")
        sort = self.request.GET.get("sort", "name")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(code__icontains=search)
                | Q(country__name__icontains=search)
            )
        if country:
            queryset = queryset.filter(country_id=country)
        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)

        # Ordenamiento
        if sort == "name":
            queryset = queryset.order_by("name")
        elif sort == "code":
            queryset = queryset.order_by("code")
        elif sort == "country":
            queryset = queryset.order_by("country__name", "name")
        elif sort == "created":
            queryset = queryset.order_by("-created_at")
        else:
            queryset = queryset.order_by("country__name", "name")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["country_filter"] = self.request.GET.get("country", "")
        context["status_filter"] = self.request.GET.get("status", "")
        context["sort_filter"] = self.request.GET.get("sort", "name")
        context["countries"] = Country.objects.all().order_by("name")
        context["is_admin"] = True

        if context["country_filter"]:
            try:
                context["selected_country"] = Country.objects.get(
                    id=context["country_filter"]
                )
            except Country.DoesNotExist:
                context["selected_country"] = None
        else:
            context["selected_country"] = None

        return context


class AdminStateDetailView(StaffRequiredMixin, DetailView):
    """Detalle administrativo de estado"""

    model = State
    template_name = "locations/state_detail.html"
    context_object_name = "state"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cities"] = self.object.cities.order_by("name")
        context["cities_count"] = self.object.cities.count()
        context["is_admin"] = True
        return context


class AdminStateCreateView(StaffRequiredMixin, CreateView):
    """Crear estado - Solo admin"""

    model = State
    template_name = "locations/state_form.html"
    fields = ["country", "name", "code", "is_active"]
    success_url = reverse_lazy("locations:admin_state_list")

    def form_valid(self, form):
        messages.success(self.request, "Estado creado exitosamente.")
        return super().form_valid(form)


class AdminStateUpdateView(StaffRequiredMixin, UpdateView):
    """Actualizar estado - Solo admin"""

    model = State
    template_name = "locations/state_form.html"
    fields = ["country", "name", "code", "is_active"]

    def get_success_url(self):
        return reverse_lazy(
            "locations:admin_state_detail", kwargs={"pk": self.object.pk}
        )

    def form_valid(self, form):
        messages.success(self.request, "Estado actualizado exitosamente.")
        return super().form_valid(form)


class AdminStateDeleteView(StaffRequiredMixin, DeleteView):
    """Eliminar estado - Solo admin"""

    model = State
    template_name = "locations/state_confirm_delete.html"
    success_url = reverse_lazy("locations:admin_state_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Estado eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)


# ===== CITY VIEWS (Admin) =====
class AdminCityListView(StaffRequiredMixin, ListView):
    """Lista administrativa de ciudades"""

    model = City
    template_name = "locations/city_list.html"
    context_object_name = "cities"
    paginate_by = 20

    def get_queryset(self):
        queryset = City.objects.select_related("state__country").all()
        search = self.request.GET.get("search")
        country = self.request.GET.get("country")
        state = self.request.GET.get("state")
        status = self.request.GET.get("status")
        sort = self.request.GET.get("sort", "name")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(state__name__icontains=search)
                | Q(state__country__name__icontains=search)
            )
        if country:
            queryset = queryset.filter(state__country_id=country)
        if state:
            queryset = queryset.filter(state_id=state)
        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)

        # Ordenamiento
        if sort == "name":
            queryset = queryset.order_by("name")
        elif sort == "state":
            queryset = queryset.order_by("state__name", "name")
        elif sort == "country":
            queryset = queryset.order_by("state__country__name", "state__name", "name")
        elif sort == "created":
            queryset = queryset.order_by("-created_at")
        else:
            queryset = queryset.order_by("state__country__name", "state__name", "name")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["country_filter"] = self.request.GET.get("country", "")
        context["state_filter"] = self.request.GET.get("state", "")
        context["status_filter"] = self.request.GET.get("status", "")
        context["sort_filter"] = self.request.GET.get("sort", "name")
        context["countries"] = Country.objects.all().order_by("name")
        context["states"] = State.objects.all().order_by("country__name", "name")
        context["is_admin"] = True

        if context["country_filter"]:
            try:
                context["selected_country"] = Country.objects.get(
                    id=context["country_filter"]
                )
            except Country.DoesNotExist:
                context["selected_country"] = None
        else:
            context["selected_country"] = None

        if context["state_filter"]:
            try:
                context["selected_state"] = State.objects.get(
                    id=context["state_filter"]
                )
            except State.DoesNotExist:
                context["selected_state"] = None
        else:
            context["selected_state"] = None

        return context


class AdminCityDetailView(StaffRequiredMixin, DetailView):
    """Detalle administrativo de ciudad"""

    model = City
    template_name = "locations/city_detail.html"
    context_object_name = "city"


class AdminCityCreateView(StaffRequiredMixin, CreateView):
    """Crear ciudad - Solo admin"""

    model = City
    template_name = "locations/city_form.html"
    fields = ["state", "name", "is_active"]
    success_url = reverse_lazy("locations:admin_city_list")

    def form_valid(self, form):
        messages.success(self.request, "Ciudad creada exitosamente.")
        return super().form_valid(form)


class AdminCityUpdateView(StaffRequiredMixin, UpdateView):
    """Actualizar ciudad - Solo admin"""

    model = City
    template_name = "locations/city_form.html"
    fields = ["state", "name", "is_active"]

    def get_success_url(self):
        return reverse_lazy(
            "locations:admin_city_detail", kwargs={"pk": self.object.pk}
        )

    def form_valid(self, form):
        messages.success(self.request, "Ciudad actualizada exitosamente.")
        return super().form_valid(form)


class AdminCityDeleteView(StaffRequiredMixin, DeleteView):
    """Eliminar ciudad - Solo admin"""

    model = City
    template_name = "locations/city_confirm_delete.html"
    success_url = reverse_lazy("locations:admin_city_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Ciudad eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)


# ===== SEASON VIEWS (Admin) =====
class AdminSeasonListView(StaffRequiredMixin, ListView):
    """Lista administrativa de temporadas"""

    model = Season
    template_name = "locations/season_list.html"
    context_object_name = "seasons"
    paginate_by = 20

    def get_queryset(self):
        queryset = Season.objects.all()
        search = self.request.GET.get("search")
        status = self.request.GET.get("status")
        year = self.request.GET.get("year")
        active = self.request.GET.get("active")
        sort = self.request.GET.get("sort", "year")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        if status:
            queryset = queryset.filter(status=status)
        if year:
            queryset = queryset.filter(year=year)
        if active == "true":
            queryset = queryset.filter(is_active=True)
        elif active == "false":
            queryset = queryset.filter(is_active=False)

        # Ordenamiento
        if sort == "year":
            queryset = queryset.order_by("-year", "-start_date")
        elif sort == "name":
            queryset = queryset.order_by("name")
        elif sort == "start_date":
            queryset = queryset.order_by("-start_date")
        elif sort == "end_date":
            queryset = queryset.order_by("-end_date")
        elif sort == "created":
            queryset = queryset.order_by("-created_at")
        else:
            queryset = queryset.order_by("-year", "-start_date")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["status_filter"] = self.request.GET.get("status", "")
        context["year_filter"] = self.request.GET.get("year", "")
        context["active_filter"] = self.request.GET.get("active", "")
        context["sort_filter"] = self.request.GET.get("sort", "year")
        context["status_choices"] = Season.SEASON_STATUS_CHOICES
        context["years"] = (
            Season.objects.values_list("year", flat=True).distinct().order_by("-year")
        )
        context["is_admin"] = True
        return context


class AdminSeasonDetailView(StaffRequiredMixin, DetailView):
    """Detalle administrativo de temporada"""

    model = Season
    template_name = "locations/season_detail.html"
    context_object_name = "season"


class AdminSeasonCreateView(StaffRequiredMixin, CreateView):
    """Crear temporada - Solo admin"""

    model = Season
    template_name = "locations/season_form.html"
    fields = [
        "name",
        "year",
        "start_date",
        "end_date",
        "status",
        "description",
        "is_active",
    ]
    success_url = reverse_lazy("locations:admin_season_list")

    def form_valid(self, form):
        messages.success(self.request, "Temporada creada exitosamente.")
        return super().form_valid(form)


class AdminSeasonUpdateView(StaffRequiredMixin, UpdateView):
    """Actualizar temporada - Solo admin"""

    model = Season
    template_name = "locations/season_form.html"
    fields = [
        "name",
        "year",
        "start_date",
        "end_date",
        "status",
        "description",
        "is_active",
    ]

    def get_success_url(self):
        return reverse_lazy(
            "locations:admin_season_detail", kwargs={"pk": self.object.pk}
        )

    def form_valid(self, form):
        messages.success(self.request, "Temporada actualizada exitosamente.")
        return super().form_valid(form)


class AdminSeasonDeleteView(StaffRequiredMixin, DeleteView):
    """Eliminar temporada - Solo admin"""

    model = Season
    template_name = "locations/season_confirm_delete.html"
    success_url = reverse_lazy("locations:admin_season_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Temporada eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)


# ===== RULE VIEWS (Admin) =====
class AdminRuleListView(StaffRequiredMixin, ListView):
    """Lista administrativa de reglas"""

    model = Rule
    template_name = "locations/rule_list.html"
    context_object_name = "rules"
    paginate_by = 20

    def get_queryset(self):
        queryset = Rule.objects.all()

        # Filtro de búsqueda
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(description__icontains=search)
                | Q(rule_type__icontains=search)
            )

        # Filtro por tipo de regla
        rule_type = self.request.GET.get("rule_type")
        if rule_type:
            queryset = queryset.filter(rule_type=rule_type)

        # Filtro por estado activo
        is_active = self.request.GET.get("is_active")
        if is_active == "true":
            queryset = queryset.filter(is_active=True)
        elif is_active == "false":
            queryset = queryset.filter(is_active=False)

        return queryset.order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["rule_type_choices"] = Rule.RULE_TYPE_CHOICES
        context["is_admin"] = True
        return context


class AdminRuleDetailView(StaffRequiredMixin, DetailView):
    """Detalle administrativo de regla"""

    model = Rule
    template_name = "locations/rule_detail.html"
    context_object_name = "rule"


class AdminRuleCreateView(StaffRequiredMixin, CreateView):
    """Crear regla - Solo admin"""

    model = Rule
    template_name = "locations/rule_form.html"
    fields = ["name", "description", "rule_type", "is_active"]
    success_url = reverse_lazy("locations:admin_rule_list")

    def form_valid(self, form):
        messages.success(self.request, "Regla creada exitosamente.")
        return super().form_valid(form)


class AdminRuleUpdateView(StaffRequiredMixin, UpdateView):
    """Actualizar regla - Solo admin"""

    model = Rule
    template_name = "locations/rule_form.html"
    fields = ["name", "description", "rule_type", "is_active"]
    success_url = reverse_lazy("locations:admin_rule_list")

    def form_valid(self, form):
        messages.success(self.request, "Regla actualizada exitosamente.")
        return super().form_valid(form)


class AdminRuleDeleteView(StaffRequiredMixin, DeleteView):
    """Eliminar regla - Solo admin"""

    model = Rule
    template_name = "locations/rule_confirm_delete.html"
    success_url = reverse_lazy("locations:admin_rule_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Regla eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)


# ===== SITE VIEWS (Admin) =====
class AdminSiteListView(StaffRequiredMixin, ListView):
    """Lista administrativa de sitios"""

    model = Site
    template_name = "locations/site_list.html"
    context_object_name = "sites"
    paginate_by = 20

    def get_queryset(self):
        queryset = Site.objects.select_related("country", "state", "city").all()

        # Búsqueda
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(site_name__icontains=search)
                | Q(abbreviation__icontains=search)
                | Q(city__name__icontains=search)
                | Q(address_1__icontains=search)
                | Q(website__icontains=search)
            )

        # Filtro por país
        country = self.request.GET.get("country")
        if country:
            queryset = queryset.filter(country_id=country)

        # Filtro por estado
        state = self.request.GET.get("state")
        if state:
            queryset = queryset.filter(state_id=state)

        # Filtro por estado activo
        status = self.request.GET.get("status")
        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)

        return queryset.order_by("site_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["countries"] = Country.objects.all().order_by("name")
        context["states"] = State.objects.all().order_by("name")
        context["is_admin"] = True
        return context


class AdminSiteDetailView(StaffRequiredMixin, DetailView):
    """Detalle administrativo de sitio"""

    model = Site
    template_name = "locations/site_detail.html"
    context_object_name = "site"


class AdminSiteCreateView(StaffRequiredMixin, CreateView):
    """Crear sitio - Solo admin"""

    model = Site
    template_name = "locations/site_form.html"
    fields = [
        "site_name",
        "abbreviation",
        "address_1",
        "address_2",
        "city",
        "state",
        "postal_code",
        "country",
        "website",
        "image",
        "additional_info",
        "is_active",
    ]
    success_url = reverse_lazy("locations:admin_site_list")

    def form_valid(self, form):
        messages.success(self.request, "Sitio creado exitosamente.")
        return super().form_valid(form)


class AdminSiteUpdateView(StaffRequiredMixin, UpdateView):
    """Actualizar sitio - Solo admin"""

    model = Site
    template_name = "locations/site_form.html"
    fields = [
        "site_name",
        "abbreviation",
        "address_1",
        "address_2",
        "city",
        "state",
        "postal_code",
        "country",
        "website",
        "image",
        "additional_info",
        "is_active",
    ]
    success_url = reverse_lazy("locations:admin_site_list")

    def form_valid(self, form):
        messages.success(self.request, "Sitio actualizado exitosamente.")
        return super().form_valid(form)


class AdminSiteDeleteView(StaffRequiredMixin, DeleteView):
    """Eliminar sitio - Solo admin"""

    model = Site
    template_name = "locations/site_confirm_delete.html"
    success_url = reverse_lazy("locations:admin_site_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Sitio eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)


# ===== HOTEL VIEWS (Admin) =====
class AdminHotelListView(StaffRequiredMixin, ListView):
    """Lista administrativa de hoteles"""

    model = Hotel
    template_name = "locations/hotel_list.html"
    context_object_name = "hotels"
    paginate_by = 20

    def get_queryset(self):
        queryset = Hotel.objects.select_related("country", "state", "city").all()

        # Búsqueda
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(hotel_name__icontains=search)
                | Q(address__icontains=search)
                | Q(city__name__icontains=search)
            )

        # Filtro por país
        country = self.request.GET.get("country")
        if country:
            queryset = queryset.filter(country_id=country)

        # Filtro por estado activo
        status = self.request.GET.get("status")
        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)

        return queryset.order_by("hotel_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["countries"] = Country.objects.all().order_by("name")
        context["is_admin"] = True
        return context


class AdminHotelDetailView(StaffRequiredMixin, DetailView):
    """Detalle administrativo de hotel"""

    model = Hotel
    template_name = "locations/hotel_detail.html"
    context_object_name = "hotel"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["rooms"] = self.object.rooms.all()
        context["services"] = self.object.services.filter(is_active=True)
        context["reservations"] = self.object.reservations.all()[:10]
        context["images"] = self.object.images.all()
        context["amenities"] = self.object.amenities.all()
        return context


class AdminHotelCreateView(StaffRequiredMixin, CreateView):
    """Crear hotel - Solo admin"""

    model = Hotel
    form_class = HotelForm
    template_name = "locations/hotel_form.html"
    success_url = reverse_lazy("locations:admin_hotel_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        hotel = self.object

        # Procesar imágenes múltiples
        images = self.request.FILES.getlist('hotel_images')
        if images:
            for index, image_file in enumerate(images):
                if image_file:
                    # Obtener datos adicionales del formulario usando el índice
                    title = self.request.POST.get(f'image_title_{index}', '').strip() or None
                    alt_text = self.request.POST.get(f'image_alt_{index}', '').strip() or None
                    is_featured = self.request.POST.get(f'image_featured_{index}') == 'on'

                    # Crear la imagen del hotel
                    HotelImage.objects.create(
                        hotel=hotel,
                        image=image_file,
                        title=title,
                        alt_text=alt_text,
                        is_featured=is_featured,
                        order=hotel.images.count()  # Orden basado en el número actual de imágenes
                    )

        # Procesar amenidades seleccionadas (checkboxes)
        amenity_count = 0

        # Mapeo de valores de ícono a nombres y categorías
        amenity_mapping = {
            'wifi': {'name': 'WiFi Gratis', 'category': 'general'},
            'parking': {'name': 'Estacionamiento', 'category': 'general'},
            'pool': {'name': 'Piscina', 'category': 'general'},
            'gym': {'name': 'Gimnasio', 'category': 'general'},
            'spa': {'name': 'Spa', 'category': 'general'},
            'restaurant': {'name': 'Restaurante', 'category': 'food_drink'},
            'bar': {'name': 'Bar', 'category': 'food_drink'},
            'room_service': {'name': 'Servicio a Habitación', 'category': 'services'},
            'cable_tv': {'name': 'TV por Cable', 'category': 'entertainment'},
            'streaming': {'name': 'Streaming', 'category': 'entertainment'},
            'game_room': {'name': 'Sala de Juegos', 'category': 'entertainment'},
            'laundry': {'name': 'Lavandería', 'category': 'services'},
            'concierge': {'name': 'Concierge', 'category': 'services'},
            '24h_reception': {'name': 'Recepción 24h', 'category': 'services'},
            'airport_shuttle': {'name': 'Transporte Aeropuerto', 'category': 'services'},
            'business_center': {'name': 'Centro de Negocios', 'category': 'services'},
            'meeting_rooms': {'name': 'Salas de Reuniones', 'category': 'services'},
            'wheelchair_accessible': {'name': 'Acceso para Sillas de Ruedas', 'category': 'accessibility'},
            'elevator': {'name': 'Ascensor', 'category': 'accessibility'},
            'pet_friendly': {'name': 'Admite Mascotas', 'category': 'general'},
            'smoking_area': {'name': 'Área de Fumadores', 'category': 'general'},
            'non_smoking': {'name': 'No Fumadores', 'category': 'general'},
            'family_friendly': {'name': 'Apto para Familias', 'category': 'general'}
        }

        # Obtener amenidades seleccionadas (checkboxes)
        selected_amenities = []
        for key in self.request.POST.keys():
            if key.startswith('amenity_') and key != 'amenity_available':
                icon_value = key.replace('amenity_', '')
                if icon_value in amenity_mapping:
                    selected_amenities.append(icon_value)

        # Crear nuevas amenidades seleccionadas
        for icon_value in selected_amenities:
            if icon_value in amenity_mapping:
                HotelAmenity.objects.create(
                    hotel=hotel,
                    name=amenity_mapping[icon_value]['name'],
                    category=amenity_mapping[icon_value]['category'],
                    icon=icon_value,
                    is_available=True,
                    order=amenity_count
                )
                amenity_count += 1

        # Procesar amenidades personalizadas
        custom_index = 0
        while True:
            name = self.request.POST.get(f'custom_amenity_name_{custom_index}', '').strip()
            if not name:
                break

            category = self.request.POST.get(f'custom_amenity_category_{custom_index}', 'general')
            icon_value = self.request.POST.get(f'custom_amenity_icon_{custom_index}', 'other')
            description = self.request.POST.get(f'custom_amenity_description_{custom_index}', '').strip() or None

            HotelAmenity.objects.create(
                hotel=hotel,
                name=name,
                category=category,
                icon=icon_value,
                description=description,
                is_available=True,
                order=hotel.amenities.count()
            )
            amenity_count += 1
            custom_index += 1

        messages.success(self.request, f"Hotel '{hotel.hotel_name}' creado exitosamente.")
        if images:
            messages.info(self.request, f"Se agregaron {len(images)} imagen(es) a la galería del hotel.")
        if amenity_count > 0:
            messages.info(self.request, f"Se agregaron {amenity_count} amenidad(es) al hotel.")
        return response


class AdminHotelUpdateView(StaffRequiredMixin, UpdateView):
    """Actualizar hotel - Solo admin"""

    model = Hotel
    form_class = HotelForm
    template_name = "locations/hotel_form.html"
    success_url = reverse_lazy("locations:admin_hotel_list")

    def form_valid(self, form):
        # Manejar eliminación de foto
        if self.request.POST.get("remove_photo") == "1":
            if self.object.photo:
                self.object.photo.delete()
                self.object.photo = None
                self.object.save()

        response = super().form_valid(form)
        hotel = self.object

        # Procesar imágenes múltiples
        images = self.request.FILES.getlist('hotel_images')
        if images:
            # Obtener el último orden para continuar desde ahí
            last_order = hotel.images.aggregate(
                max_order=Max('order')
            )['max_order'] or 0

            for index, image_file in enumerate(images):
                if image_file:
                    # Obtener datos adicionales del formulario usando el índice
                    title = self.request.POST.get(f'image_title_{index}', '').strip() or None
                    alt_text = self.request.POST.get(f'image_alt_{index}', '').strip() or None
                    is_featured = self.request.POST.get(f'image_featured_{index}') == 'on'

                    # Crear la imagen del hotel
                    HotelImage.objects.create(
                        hotel=hotel,
                        image=image_file,
                        title=title,
                        alt_text=alt_text,
                        is_featured=is_featured,
                        order=last_order + index + 1
                    )

        # Procesar amenidades seleccionadas (checkboxes)
        amenity_count = 0

        # Mapeo de valores de ícono a nombres y categorías
        amenity_mapping = {
            'wifi': {'name': 'WiFi Gratis', 'category': 'general'},
            'parking': {'name': 'Estacionamiento', 'category': 'general'},
            'pool': {'name': 'Piscina', 'category': 'general'},
            'gym': {'name': 'Gimnasio', 'category': 'general'},
            'spa': {'name': 'Spa', 'category': 'general'},
            'restaurant': {'name': 'Restaurante', 'category': 'food_drink'},
            'bar': {'name': 'Bar', 'category': 'food_drink'},
            'room_service': {'name': 'Servicio a Habitación', 'category': 'services'},
            'cable_tv': {'name': 'TV por Cable', 'category': 'entertainment'},
            'streaming': {'name': 'Streaming', 'category': 'entertainment'},
            'game_room': {'name': 'Sala de Juegos', 'category': 'entertainment'},
            'laundry': {'name': 'Lavandería', 'category': 'services'},
            'concierge': {'name': 'Concierge', 'category': 'services'},
            '24h_reception': {'name': 'Recepción 24h', 'category': 'services'},
            'airport_shuttle': {'name': 'Transporte Aeropuerto', 'category': 'services'},
            'business_center': {'name': 'Centro de Negocios', 'category': 'services'},
            'meeting_rooms': {'name': 'Salas de Reuniones', 'category': 'services'},
            'wheelchair_accessible': {'name': 'Acceso para Sillas de Ruedas', 'category': 'accessibility'},
            'elevator': {'name': 'Ascensor', 'category': 'accessibility'},
            'pet_friendly': {'name': 'Admite Mascotas', 'category': 'general'},
            'smoking_area': {'name': 'Área de Fumadores', 'category': 'general'},
            'non_smoking': {'name': 'No Fumadores', 'category': 'general'},
            'family_friendly': {'name': 'Apto para Familias', 'category': 'general'}
        }

        # Obtener amenidades seleccionadas (checkboxes)
        selected_amenities = []
        for key in self.request.POST.keys():
            if key.startswith('amenity_') and key != 'amenity_available':
                icon_value = key.replace('amenity_', '')
                if icon_value in amenity_mapping:
                    selected_amenities.append(icon_value)

        # Eliminar amenidades existentes que no están seleccionadas (solo generales del hotel)
        existing_amenities = hotel.amenities.filter(
            category__in=['general', 'entertainment', 'food_drink', 'services', 'accessibility']
        )
        for existing in existing_amenities:
            if existing.icon not in selected_amenities:
                existing.delete()

        # Crear nuevas amenidades seleccionadas
        for icon_value in selected_amenities:
            if icon_value in amenity_mapping:
                # Verificar si ya existe
                existing = hotel.amenities.filter(icon=icon_value).first()
                if not existing:
                    HotelAmenity.objects.create(
                        hotel=hotel,
                        name=amenity_mapping[icon_value]['name'],
                        category=amenity_mapping[icon_value]['category'],
                        icon=icon_value,
                        is_available=True,
                        order=amenity_count
                    )
                    amenity_count += 1

        # Procesar amenidades personalizadas
        custom_index = 0
        while True:
            name = self.request.POST.get(f'custom_amenity_name_{custom_index}', '').strip()
            if not name:
                break

            category = self.request.POST.get(f'custom_amenity_category_{custom_index}', 'general')
            icon_value = self.request.POST.get(f'custom_amenity_icon_{custom_index}', 'other')
            description = self.request.POST.get(f'custom_amenity_description_{custom_index}', '').strip() or None

            HotelAmenity.objects.create(
                hotel=hotel,
                name=name,
                category=category,
                icon=icon_value,
                description=description,
                is_available=True,
                order=hotel.amenities.count()
            )
            amenity_count += 1
            custom_index += 1

        messages.success(self.request, f"Hotel '{hotel.hotel_name}' actualizado exitosamente.")
        if images:
            messages.info(self.request, f"Se agregaron {len(images)} nueva(s) imagen(es) a la galería del hotel.")
        if amenity_count > 0:
            messages.info(self.request, f"Se agregaron {amenity_count} nueva(s) amenidad(es) al hotel.")
        return response


class AdminHotelDeleteView(StaffRequiredMixin, DeleteView):
    """Eliminar hotel - Solo admin"""

    model = Hotel
    template_name = "locations/hotel_confirm_delete.html"
    success_url = reverse_lazy("locations:admin_hotel_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Hotel eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)


# ===== HOTEL ROOM VIEWS (Admin) =====
class AdminHotelRoomListView(StaffRequiredMixin, ListView):
    """Lista administrativa de habitaciones"""

    model = HotelRoom
    template_name = "locations/hotel_room_list.html"
    context_object_name = "rooms"
    paginate_by = 20

    def get_queryset(self):
        queryset = HotelRoom.objects.select_related("hotel").prefetch_related("images__media_file", "images").all()

        # Filtro por hotel
        hotel = self.request.GET.get("hotel")
        if hotel:
            queryset = queryset.filter(hotel_id=hotel)

        # Filtro por disponibilidad
        available = self.request.GET.get("available")
        if available == "yes":
            queryset = queryset.filter(is_available=True)
        elif available == "no":
            queryset = queryset.filter(is_available=False)

        # Búsqueda
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(room_number__icontains=search)
                | Q(name__icontains=search)
                | Q(hotel__hotel_name__icontains=search)
            )

        return queryset.order_by("hotel", "room_number")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hotels"] = Hotel.objects.filter(is_active=True).order_by("hotel_name")
        context["is_admin"] = True
        return context


class AdminHotelRoomCreateView(StaffRequiredMixin, CreateView):
    """Crear habitación - Solo admin"""

    model = HotelRoom
    template_name = "locations/hotel_room_form.html"
    fields = [
        "hotel",
        "room_number",
        "name",
        "room_type",
        "capacity",
        "price_per_night",
        "price_includes_guests",
        "additional_guest_price",
        "breakfast_included",
        "description",
        "is_available",
    ]
    success_url = reverse_lazy("locations:admin_hotel_room_list")

    def form_valid(self, form):
        # Debug: Log todos los campos recibidos
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[CREATE] POST data keys: {list(self.request.POST.keys())}")
        logger.info(f"[CREATE] Form cleaned_data: {form.cleaned_data}")
        logger.info(f"[CREATE] additional_guest_price en POST: {self.request.POST.get('additional_guest_price', 'NO ENCONTRADO')}")
        logger.info(f"[CREATE] price_per_night en POST: {self.request.POST.get('price_per_night', 'NO ENCONTRADO')}")

        # Asegurar que los checkboxes se procesen correctamente
        # Los checkboxes no se envían si no están marcados, así que debemos manejarlos explícitamente
        if 'breakfast_included' not in self.request.POST:
            form.instance.breakfast_included = False
        if 'is_available' not in self.request.POST:
            form.instance.is_available = False

        # Asegurar que additional_guest_price tenga un valor por defecto si está vacío
        additional_price = self.request.POST.get('additional_guest_price', '').strip()
        if not additional_price or additional_price == '':
            form.instance.additional_guest_price = 0.00
        else:
            try:
                form.instance.additional_guest_price = float(additional_price)
            except (ValueError, TypeError):
                form.instance.additional_guest_price = 0.00

        response = super().form_valid(form)
        room = self.object

        # Debug: Verificar que el objeto se guardó correctamente
        logger.info(f"[CREATE] Room guardado - ID: {room.id}, Hotel: {room.hotel_id}, Número: {room.room_number}, Nombre: {room.name}, Tipo: {room.room_type}, Capacidad: {room.capacity}, Precio: {room.price_per_night}, Incluye: {room.price_includes_guests}, Adicional: {room.additional_guest_price}, Desayuno: {room.breakfast_included}, Disponible: {room.is_available}")

        added_images = 0

        # 1) Selección desde biblioteca multimedia (IDs)
        media_ids_raw = self.request.POST.getlist("room_media_ids")
        logger.info(f"[CREATE] Media IDs raw recibidos: {media_ids_raw}")
        media_ids = [i for i in media_ids_raw if str(i).isdigit()]
        logger.info(f"[CREATE] Media IDs procesados: {media_ids}")

        for idx, media_id in enumerate(media_ids):
            try:
                mf = MediaFile.objects.filter(id=int(media_id), status="active", file_type="image").first()
                if not mf:
                    logger.warning(f"[CREATE] MediaFile con ID {media_id} no encontrado o no es imagen activa")
                    continue
                if room.images.filter(media_file_id=mf.id).exists():
                    logger.info(f"[CREATE] Imagen con MediaFile ID {media_id} ya existe para esta habitación, omitiendo")
                    continue
                HotelRoomImage.objects.create(
                    room=room,
                    media_file=mf,
                    title=mf.title or None,
                    alt_text=getattr(mf, "alt_text", "") or "",
                    is_featured=False,
                    order=idx,
                )
                added_images += 1
                logger.info(f"[CREATE] Imagen agregada exitosamente: MediaFile ID {media_id}")
            except Exception as e:
                logger.error(f"[CREATE] Error al agregar imagen con ID {media_id}: {e}")
                continue

        # Debug: Log para verificar imágenes
        logger.info(f"[CREATE] Total imágenes agregadas: {added_images}")

        # Procesar amenidades de habitación
        amenity_count = 0
        amenity_mapping = {
            'air_conditioning': {'name': 'Aire Acondicionado', 'category': 'room'},
            'heating': {'name': 'Calefacción', 'category': 'room'},
            'tv': {'name': 'Televisión', 'category': 'room'},
            'safe': {'name': 'Caja Fuerte', 'category': 'room'},
            'minibar': {'name': 'Minibar', 'category': 'room'},
            'balcony': {'name': 'Balcón', 'category': 'room'},
            'hairdryer': {'name': 'Secador de Pelo', 'category': 'bathroom'},
            'bathtub': {'name': 'Bañera', 'category': 'bathroom'},
            'shower': {'name': 'Ducha', 'category': 'bathroom'}
        }

        selected_amenities = []
        # Buscar checkboxes marcados - los checkboxes solo se envían si están marcados
        amenity_keys = [k for k in self.request.POST.keys() if k.startswith('room_amenity_')]
        logger.info(f"[CREATE] Keys POST que empiezan con 'room_amenity_': {amenity_keys}")

        for key in amenity_keys:
            icon_value = key.replace('room_amenity_', '')
            # Verificar que el checkbox esté marcado (si está en POST, está marcado)
            if icon_value in amenity_mapping:
                selected_amenities.append(icon_value)
                logger.info(f"[CREATE] Amenidad seleccionada: {icon_value}")

        # Debug: Log para verificar amenidades
        logger.info(f"[CREATE] Total amenidades seleccionadas: {len(selected_amenities)} - {selected_amenities}")

        # Asociar amenidades a la habitación
        room_amenities_to_add = []
        for icon_value in selected_amenities:
            if icon_value in amenity_mapping:
                # Buscar o crear la amenidad en el hotel
                amenity, created = HotelAmenity.objects.get_or_create(
                    hotel=room.hotel,
                    icon=icon_value,
                    defaults={
                        'name': amenity_mapping[icon_value]['name'],
                        'category': amenity_mapping[icon_value]['category'],
                        'is_available': True,
                        'order': room.hotel.amenities.count()
                    }
                )
                if created:
                    amenity_count += 1
                # Agregar a la lista para asociar a la habitación
                room_amenities_to_add.append(amenity)

        # Asociar las amenidades a la habitación (siempre, incluso si está vacío para limpiar)
        room.amenities.set(room_amenities_to_add)
        logger.info(f"[CREATE] Amenidades asociadas a la habitación: {[a.icon for a in room_amenities_to_add]}")

        # Procesar reglas de habitación
        rules_count = 0
        rule_index = 0
        while True:
            min_adults_key = f"rule_min_adults_{rule_index}"
            if min_adults_key not in self.request.POST:
                break

            try:
                min_adults = int(self.request.POST.get(min_adults_key, 0))
                max_adults = int(self.request.POST.get(f"rule_max_adults_{rule_index}", 0))
                min_children = int(self.request.POST.get(f"rule_min_children_{rule_index}", 0))
                max_children = int(self.request.POST.get(f"rule_max_children_{rule_index}", 0))
                description = self.request.POST.get(f"rule_description_{rule_index}", "").strip()
                is_active = self.request.POST.get(f"rule_is_active_{rule_index}") == "on"

                # Debug: Log para verificar qué se está recibiendo
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"[CREATE] Procesando regla {rule_index}: min_adults={min_adults}, max_adults={max_adults}, min_children={min_children}, max_children={max_children}")

                if min_adults > 0 and max_adults > 0:
                    HotelRoomRule.objects.create(
                        room=room,
                        min_adults=min_adults,
                        max_adults=max_adults,
                        min_children=min_children,
                        max_children=max_children,
                        description=description or None,
                        is_active=is_active,
                        order=rule_index,
                    )
                    rules_count += 1
                    logger.info(f"[CREATE] Regla {rule_index} creada exitosamente")
                else:
                    logger.warning(f"[CREATE] Regla {rule_index} omitida: min_adults={min_adults}, max_adults={max_adults} (debe ser > 0)")
            except (ValueError, TypeError) as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"[CREATE] Error procesando regla {rule_index}: {e}")
                pass

            rule_index += 1

        messages.success(self.request, f"Habitación '{room.room_number}' creada exitosamente.")
        if added_images:
            messages.info(self.request, f"Se agregaron {added_images} imagen(es) a la galería de la habitación.")
        if amenity_count > 0:
            messages.info(self.request, f"Se agregaron {amenity_count} amenidad(es) al hotel.")
        if rules_count > 0:
            messages.info(self.request, f"Se agregaron {rules_count} regla(s) de ocupación a la habitación.")
        return response


class AdminHotelRoomUpdateView(StaffRequiredMixin, UpdateView):
    """Actualizar habitación - Solo admin"""

    model = HotelRoom
    template_name = "locations/hotel_room_form.html"
    fields = [
        "hotel",
        "room_number",
        "name",
        "room_type",
        "capacity",
        "price_per_night",
        "price_includes_guests",
        "additional_guest_price",
        "breakfast_included",
        "description",
        "is_available",
    ]
    success_url = reverse_lazy("locations:admin_hotel_room_list")

    def form_valid(self, form):
        # Debug: Log todos los campos recibidos
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[UPDATE] POST data keys: {list(self.request.POST.keys())}")
        logger.info(f"[UPDATE] Form cleaned_data: {form.cleaned_data}")
        logger.info(f"[UPDATE] additional_guest_price en POST: {self.request.POST.get('additional_guest_price', 'NO ENCONTRADO')}")
        logger.info(f"[UPDATE] price_per_night en POST: {self.request.POST.get('price_per_night', 'NO ENCONTRADO')}")

        # Asegurar que los checkboxes se procesen correctamente
        # Los checkboxes no se envían si no están marcados, así que debemos manejarlos explícitamente
        if 'breakfast_included' not in self.request.POST:
            form.instance.breakfast_included = False
        if 'is_available' not in self.request.POST:
            form.instance.is_available = False

        # Asegurar que additional_guest_price tenga un valor por defecto si está vacío
        additional_price = self.request.POST.get('additional_guest_price', '').strip()
        if not additional_price or additional_price == '':
            form.instance.additional_guest_price = 0.00
        else:
            try:
                form.instance.additional_guest_price = float(additional_price)
            except (ValueError, TypeError):
                form.instance.additional_guest_price = 0.00

        response = super().form_valid(form)
        room = self.object

        # Debug: Verificar que el objeto se guardó correctamente
        logger.info(f"[UPDATE] Room guardado - ID: {room.id}, Hotel: {room.hotel_id}, Número: {room.room_number}, Nombre: {room.name}, Tipo: {room.room_type}, Capacidad: {room.capacity}, Precio: {room.price_per_night}, Incluye: {room.price_includes_guests}, Adicional: {room.additional_guest_price}, Desayuno: {room.breakfast_included}, Disponible: {room.is_available}")

        added_images = 0
        last_order = room.images.aggregate(max_order=Max("order"))["max_order"] or 0

        # 1) Selección desde biblioteca multimedia (IDs)
        media_ids_raw = self.request.POST.getlist("room_media_ids")
        logger.info(f"[UPDATE] Media IDs raw recibidos: {media_ids_raw}")
        media_ids = [i for i in media_ids_raw if str(i).isdigit()]
        logger.info(f"[UPDATE] Media IDs procesados: {media_ids}")

        for idx, media_id in enumerate(media_ids):
            try:
                mf = MediaFile.objects.filter(id=int(media_id), status="active", file_type="image").first()
                if not mf:
                    logger.warning(f"[UPDATE] MediaFile con ID {media_id} no encontrado o no es imagen activa")
                    continue
                if room.images.filter(media_file_id=mf.id).exists():
                    logger.info(f"[UPDATE] Imagen con MediaFile ID {media_id} ya existe para esta habitación, omitiendo")
                    continue
                HotelRoomImage.objects.create(
                    room=room,
                    media_file=mf,
                    title=mf.title or None,
                    alt_text=getattr(mf, "alt_text", "") or "",
                    is_featured=False,
                    order=last_order + idx + 1,
                )
                added_images += 1
                logger.info(f"[UPDATE] Imagen agregada exitosamente: MediaFile ID {media_id}")
            except Exception as e:
                logger.error(f"[UPDATE] Error al agregar imagen con ID {media_id}: {e}")
                continue

        # 2) Fallback: archivos subidos (se guardan como MediaFile en MULTIMEDIA)
        uploads = self.request.FILES.getlist("room_images")
        for f in uploads:
            if not f:
                continue
            title = Path(getattr(f, "name", "image")).stem or "Room image"
            mf = MediaFile(
                title=title,
                file_type="image",
                status="active",
                uploaded_by=self.request.user,
                original_file=f,
            )
            mf.save()
            HotelRoomImage.objects.create(
                room=room,
                media_file=mf,
                title=mf.title or None,
                alt_text=getattr(mf, "alt_text", "") or "",
                is_featured=False,
                order=(room.images.aggregate(max_order=Max("order"))["max_order"] or 0) + 1,
            )
            added_images += 1

        # Procesar amenidades de habitación
        amenity_count = 0
        amenity_mapping = {
            'air_conditioning': {'name': 'Aire Acondicionado', 'category': 'room'},
            'heating': {'name': 'Calefacción', 'category': 'room'},
            'tv': {'name': 'Televisión', 'category': 'room'},
            'safe': {'name': 'Caja Fuerte', 'category': 'room'},
            'minibar': {'name': 'Minibar', 'category': 'room'},
            'balcony': {'name': 'Balcón', 'category': 'room'},
            'hairdryer': {'name': 'Secador de Pelo', 'category': 'bathroom'},
            'bathtub': {'name': 'Bañera', 'category': 'bathroom'},
            'shower': {'name': 'Ducha', 'category': 'bathroom'}
        }

        selected_amenities = []
        # Buscar checkboxes marcados - los checkboxes solo se envían si están marcados
        amenity_keys = [k for k in self.request.POST.keys() if k.startswith('room_amenity_')]
        logger.info(f"[UPDATE] Keys POST que empiezan con 'room_amenity_': {amenity_keys}")

        for key in amenity_keys:
            icon_value = key.replace('room_amenity_', '')
            # Verificar que el checkbox esté marcado (si está en POST, está marcado)
            if icon_value in amenity_mapping:
                selected_amenities.append(icon_value)
                logger.info(f"[UPDATE] Amenidad seleccionada: {icon_value}")

        logger.info(f"[UPDATE] Total amenidades seleccionadas: {len(selected_amenities)} - {selected_amenities}")

        # Asociar amenidades a la habitación
        room_amenities_to_add = []
        for icon_value in selected_amenities:
            if icon_value in amenity_mapping:
                # Buscar o crear la amenidad en el hotel
                amenity, created = HotelAmenity.objects.get_or_create(
                    hotel=room.hotel,
                    icon=icon_value,
                    defaults={
                        'name': amenity_mapping[icon_value]['name'],
                        'category': amenity_mapping[icon_value]['category'],
                        'is_available': True,
                        'order': room.hotel.amenities.count()
                    }
                )
                if created:
                    amenity_count += 1
                # Agregar a la lista para asociar a la habitación
                room_amenities_to_add.append(amenity)

        # Asociar las amenidades a la habitación (siempre, incluso si está vacío para limpiar)
        room.amenities.set(room_amenities_to_add)
        logger.info(f"[UPDATE] Amenidades asociadas a la habitación: {[a.icon for a in room_amenities_to_add]}")

        # Procesar reglas de habitación
        # Primero, obtener todas las reglas existentes y las que vienen en el POST
        existing_rule_ids = set(room.rules.values_list('id', flat=True))
        submitted_rule_ids = set()
        delete_rule_ids = [
            int(rule_id) for rule_id in self.request.POST.getlist("delete_rule_ids")
            if str(rule_id).isdigit()
        ]

        # Eliminar reglas marcadas explícitamente para eliminar
        for rule_id in delete_rule_ids:
            try:
                rule = HotelRoomRule.objects.get(id=rule_id, room=room)
                rule.delete()
                existing_rule_ids.discard(rule_id)
            except HotelRoomRule.DoesNotExist:
                pass

        # Actualizar reglas existentes y crear nuevas
        rules_updated = 0
        rules_created = 0
        rule_index = 0

        while True:
            rule_id_key = f"rule_id_{rule_index}"
            min_adults_key = f"rule_min_adults_{rule_index}"

            if min_adults_key not in self.request.POST:
                break

            try:
                rule_id_str = self.request.POST.get(rule_id_key, "").strip()
                min_adults = int(self.request.POST.get(min_adults_key, 0))
                max_adults = int(self.request.POST.get(f"rule_max_adults_{rule_index}", 0))
                min_children = int(self.request.POST.get(f"rule_min_children_{rule_index}", 0))
                max_children = int(self.request.POST.get(f"rule_max_children_{rule_index}", 0))
                description = self.request.POST.get(f"rule_description_{rule_index}", "").strip()
                is_active = self.request.POST.get(f"rule_is_active_{rule_index}") == "on"

                # Debug: Log para verificar qué se está recibiendo
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Procesando regla {rule_index}: rule_id={rule_id_str}, min_adults={min_adults}, max_adults={max_adults}, min_children={min_children}, max_children={max_children}")

                if min_adults > 0 and max_adults > 0:
                    if rule_id_str and rule_id_str.isdigit():
                        # Actualizar regla existente
                        rule_id = int(rule_id_str)
                        try:
                            rule = HotelRoomRule.objects.get(id=rule_id, room=room)
                            rule.min_adults = min_adults
                            rule.max_adults = max_adults
                            rule.min_children = min_children
                            rule.max_children = max_children
                            rule.description = description or None
                            rule.is_active = is_active
                            rule.order = rule_index
                            rule.save()
                            submitted_rule_ids.add(rule_id)
                            rules_updated += 1
                        except HotelRoomRule.DoesNotExist:
                            # Si la regla no existe, crear una nueva
                            HotelRoomRule.objects.create(
                                room=room,
                                min_adults=min_adults,
                                max_adults=max_adults,
                                min_children=min_children,
                                max_children=max_children,
                                description=description or None,
                                is_active=is_active,
                                order=rule_index,
                            )
                            rules_created += 1
                    else:
                        # Crear nueva regla (rule_id está vacío o no es un número)
                        HotelRoomRule.objects.create(
                            room=room,
                            min_adults=min_adults,
                            max_adults=max_adults,
                            min_children=min_children,
                            max_children=max_children,
                            description=description or None,
                            is_active=is_active,
                            order=rule_index,
                        )
                        rules_created += 1
            except (ValueError, TypeError) as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error procesando regla {rule_index}: {e}")
                pass

            rule_index += 1

        # Eliminar reglas existentes que no están en el POST (fueron eliminadas del formulario)
        rules_to_delete = existing_rule_ids - submitted_rule_ids - set(delete_rule_ids)
        for rule_id in rules_to_delete:
            try:
                rule = HotelRoomRule.objects.get(id=rule_id, room=room)
                rule.delete()
            except HotelRoomRule.DoesNotExist:
                pass

        messages.success(self.request, f"Habitación '{room.room_number}' actualizada exitosamente.")
        if added_images:
            messages.info(self.request, f"Se agregaron {added_images} nueva(s) imagen(es) a la galería de la habitación.")
        if amenity_count > 0:
            messages.info(self.request, f"Se agregaron {amenity_count} nueva(s) amenidad(es) al hotel.")
        if rules_updated > 0 or rules_created > 0 or delete_rule_ids or rules_to_delete:
            total_rules = rules_updated + rules_created
            deleted_rules = len(delete_rule_ids) + len(rules_to_delete)
            if total_rules > 0:
                messages.info(self.request, f"Se {'actualizaron' if rules_updated > 0 else 'crearon'} {total_rules} regla(s) de ocupación.")
            if deleted_rules > 0:
                messages.info(self.request, f"Se eliminaron {deleted_rules} regla(s) de ocupación.")
        return response


class AdminHotelRoomDeleteView(StaffRequiredMixin, DeleteView):
    """Eliminar habitación - Solo admin"""

    model = HotelRoom
    template_name = "locations/hotel_room_confirm_delete.html"
    success_url = reverse_lazy("locations:admin_hotel_room_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Habitación eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)


@require_http_methods(["POST"])
def admin_hotel_room_image_delete_ajax(request, pk):
    """Eliminar imagen de habitación vía AJAX - Solo elimina la relación, NO el MediaFile"""

    # Verificar que el usuario sea staff
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({
            "success": False,
            "message": "No autorizado. Debes ser staff para realizar esta acción.",
        }, status=403)

    try:
        # Obtener la imagen (sin usar get_object_or_404 para evitar HTML)
        try:
            image = HotelRoomImage.objects.get(pk=pk)
        except HotelRoomImage.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": "La imagen no existe o ya fue eliminada.",
            }, status=404)

        image_id = image.id
        room_id = image.room.id

        # Eliminar solo el HotelRoomImage (la relación)
        # El MediaFile se preserva en la biblioteca multimedia
        image.delete()

        return JsonResponse({
            "success": True,
            "message": "Imagen eliminada de la habitación exitosamente.",
            "image_id": image_id,
            "room_id": room_id,
        })
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error al eliminar imagen de habitación: {e}", exc_info=True)
        return JsonResponse({
            "success": False,
            "message": f"Error al eliminar la imagen: {str(e)}",
        }, status=500)


# ===== HOTEL SERVICE VIEWS (Admin) =====
class AdminHotelServiceListView(StaffRequiredMixin, ListView):
    """Lista administrativa de servicios de hotel"""

    model = HotelService
    template_name = "locations/hotel_service_list.html"
    context_object_name = "services"
    paginate_by = 20

    def get_queryset(self):
        queryset = HotelService.objects.select_related("hotel").all()

        # Filtro por hotel
        hotel = self.request.GET.get("hotel")
        if hotel:
            queryset = queryset.filter(hotel_id=hotel)

        # Filtro por estado activo
        status = self.request.GET.get("status")
        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)

        # Búsqueda
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(service_name__icontains=search)
                | Q(hotel__hotel_name__icontains=search)
            )

        return queryset.order_by("hotel", "service_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hotels"] = Hotel.objects.filter(is_active=True).order_by("hotel_name")
        context["is_admin"] = True
        return context


class AdminHotelServiceCreateView(StaffRequiredMixin, CreateView):
    """Crear servicio de hotel - Solo admin"""

    model = HotelService
    template_name = "locations/hotel_service_form.html"
    fields = [
        "hotel",
        "service_name",
        "service_type",
        "description",
        "price",
        "is_per_person",
        "is_per_night",
        "is_active",
    ]
    success_url = reverse_lazy("locations:admin_hotel_service_list")

    def form_valid(self, form):
        messages.success(self.request, "Servicio creado exitosamente.")
        return super().form_valid(form)


class AdminHotelServiceUpdateView(StaffRequiredMixin, UpdateView):
    """Actualizar servicio de hotel - Solo admin"""

    model = HotelService
    template_name = "locations/hotel_service_form.html"
    fields = [
        "hotel",
        "service_name",
        "service_type",
        "description",
        "price",
        "is_per_person",
        "is_per_night",
        "is_active",
    ]
    success_url = reverse_lazy("locations:admin_hotel_service_list")

    def form_valid(self, form):
        messages.success(self.request, "Servicio actualizado exitosamente.")
        return super().form_valid(form)


class AdminHotelServiceDeleteView(StaffRequiredMixin, DeleteView):
    """Eliminar servicio de hotel - Solo admin"""

    model = HotelService
    template_name = "locations/hotel_service_confirm_delete.html"
    success_url = reverse_lazy("locations:admin_hotel_service_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Servicio eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)


# ===== HOTEL RESERVATION VIEWS (Admin) =====
class AdminHotelReservationListView(StaffRequiredMixin, ListView):
    """Lista administrativa de reservas de hotel"""

    model = HotelReservation
    template_name = "locations/hotel_reservation_list.html"
    context_object_name = "reservations"
    paginate_by = 20

    def get_queryset(self):
        queryset = HotelReservation.objects.select_related(
            "hotel", "room", "user"
        ).all()

        # Filtro por hotel
        hotel = self.request.GET.get("hotel")
        if hotel:
            queryset = queryset.filter(hotel_id=hotel)

        # Filtro por estado
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        # Búsqueda
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(guest_name__icontains=search)
                | Q(guest_email__icontains=search)
                | Q(hotel__hotel_name__icontains=search)
            )

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hotels"] = Hotel.objects.filter(is_active=True).order_by("hotel_name")
        context["is_admin"] = True
        return context


class AdminHotelReservationDetailView(StaffRequiredMixin, DetailView):
    """Detalle administrativo de reserva"""

    model = HotelReservation
    template_name = "locations/hotel_reservation_detail.html"
    context_object_name = "reservation"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["services"] = self.object.service_reservations.select_related(
            "service"
        ).all()
        return context


class AdminHotelReservationCreateView(StaffRequiredMixin, CreateView):
    """Crear reserva de hotel - Solo admin"""

    model = HotelReservation
    template_name = "locations/hotel_reservation_form.html"
    fields = [
        "hotel",
        "room",
        "user",
        "guest_name",
        "guest_email",
        "guest_phone",
        "number_of_guests",
        "check_in",
        "check_out",
        "status",
        "notes",
    ]
    success_url = reverse_lazy("locations:admin_hotel_reservation_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Personalizar el campo user para evitar enlaces a user_list
        if "user" in form.fields:
            from django.contrib.auth import get_user_model
            from django import forms

            User = get_user_model()
            form.fields["user"].queryset = User.objects.all().order_by("username")
            form.fields["user"].widget = forms.Select(attrs={"class": "form-select"})
        return form

    def form_valid(self, form):
        messages.success(self.request, "Reserva creada exitosamente.")
        return super().form_valid(form)


class AdminHotelReservationUpdateView(StaffRequiredMixin, UpdateView):
    """Actualizar reserva de hotel - Solo admin"""

    model = HotelReservation
    template_name = "locations/hotel_reservation_form.html"
    fields = [
        "hotel",
        "room",
        "user",
        "guest_name",
        "guest_email",
        "guest_phone",
        "number_of_guests",
        "check_in",
        "check_out",
        "status",
        "notes",
    ]
    success_url = reverse_lazy("locations:admin_hotel_reservation_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Personalizar el campo user para evitar enlaces a user_list
        if "user" in form.fields:
            from django.contrib.auth import get_user_model
            from django import forms

            User = get_user_model()
            form.fields["user"].queryset = User.objects.all().order_by("username")
            form.fields["user"].widget = forms.Select(attrs={"class": "form-select"})
        return form

    def form_valid(self, form):
        messages.success(self.request, "Reserva actualizada exitosamente.")
        return super().form_valid(form)


class AdminHotelReservationDeleteView(StaffRequiredMixin, DeleteView):
    """Eliminar reserva de hotel - Solo admin"""

    model = HotelReservation
    template_name = "locations/hotel_reservation_confirm_delete.html"
    success_url = reverse_lazy("locations:admin_hotel_reservation_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Reserva eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)


# ===== HOTEL IMAGE VIEWS (Admin) =====
class AdminHotelImageListView(StaffRequiredMixin, ListView):
    """Lista administrativa de imágenes de hotel"""

    model = HotelImage
    template_name = "locations/hotel_image_list.html"
    context_object_name = "images"
    paginate_by = 20

    def get_queryset(self):
        hotel_pk = self.kwargs.get("hotel_pk")
        if hotel_pk:
            return HotelImage.objects.filter(hotel_id=hotel_pk).order_by(
                "order", "-is_featured", "-created_at"
            )
        return HotelImage.objects.select_related("hotel").order_by(
            "hotel", "order", "-is_featured", "-created_at"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hotel_pk = self.kwargs.get("hotel_pk")
        if hotel_pk:
            context["hotel"] = Hotel.objects.get(pk=hotel_pk)
        return context


class AdminHotelImageCreateView(StaffRequiredMixin, CreateView):
    """Crear imagen de hotel - Solo admin"""

    model = HotelImage
    template_name = "locations/hotel_image_form.html"
    fields = ["hotel", "image", "title", "alt_text", "order", "is_featured"]
    success_url = reverse_lazy("locations:admin_hotel_list")

    def form_valid(self, form):
        messages.success(self.request, "Imagen agregada exitosamente.")
        return super().form_valid(form)

    def get_success_url(self):
        hotel_pk = self.object.hotel.pk
        return reverse_lazy(
            "locations:admin_hotel_image_list", kwargs={"hotel_pk": hotel_pk}
        )


class AdminHotelImageUpdateView(StaffRequiredMixin, UpdateView):
    """Actualizar imagen de hotel - Solo admin"""

    model = HotelImage
    template_name = "locations/hotel_image_form.html"
    fields = ["hotel", "image", "title", "alt_text", "order", "is_featured"]

    def form_valid(self, form):
        messages.success(self.request, "Imagen actualizada exitosamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "locations:admin_hotel_image_list",
            kwargs={"hotel_pk": self.object.hotel.pk},
        )


class AdminHotelImageDeleteView(StaffRequiredMixin, DeleteView):
    """Eliminar imagen de hotel - Solo admin"""

    model = HotelImage
    template_name = "locations/hotel_image_confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        hotel_pk = self.get_object().hotel.pk
        messages.success(request, "Imagen eliminada exitosamente.")
        result = super().delete(request, *args, **kwargs)
        return result

    def get_success_url(self):
        return reverse_lazy(
            "locations:admin_hotel_image_list",
            kwargs={"hotel_pk": self.object.hotel.pk},
        )


# ===== HOTEL AMENITY VIEWS (Admin) =====
class AdminHotelAmenityListView(StaffRequiredMixin, ListView):
    """Lista administrativa de amenidades de hotel"""

    model = HotelAmenity
    template_name = "locations/hotel_amenity_list.html"
    context_object_name = "amenities"
    paginate_by = 50

    def get_queryset(self):
        hotel_pk = self.kwargs.get("hotel_pk")
        queryset = HotelAmenity.objects.filter(hotel_id=hotel_pk) if hotel_pk else HotelAmenity.objects.select_related("hotel").all()

        category = self.request.GET.get("category")
        if category:
            queryset = queryset.filter(category=category)

        return queryset.order_by("category", "order", "name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hotel_pk = self.kwargs.get("hotel_pk")
        if hotel_pk:
            context["hotel"] = Hotel.objects.get(pk=hotel_pk)
        context["category_filter"] = self.request.GET.get("category", "")
        context["categories"] = HotelAmenity.AMENITY_CATEGORY_CHOICES
        return context


class AdminHotelAmenityCreateView(StaffRequiredMixin, CreateView):
    """Crear amenidad de hotel - Solo admin"""

    model = HotelAmenity
    template_name = "locations/hotel_amenity_form.html"
    fields = ["hotel", "name", "category", "icon", "description", "is_available", "order"]
    success_url = reverse_lazy("locations:admin_hotel_list")

    def form_valid(self, form):
        messages.success(self.request, f"Amenidad '{form.instance.name}' creada exitosamente.")
        return super().form_valid(form)

    def get_success_url(self):
        hotel_pk = self.object.hotel.pk
        return reverse_lazy(
            "locations:admin_hotel_amenity_list", kwargs={"hotel_pk": hotel_pk}
        )


class AdminHotelAmenityUpdateView(StaffRequiredMixin, UpdateView):
    """Actualizar amenidad de hotel - Solo admin"""

    model = HotelAmenity
    template_name = "locations/hotel_amenity_form.html"
    fields = ["hotel", "name", "category", "icon", "description", "is_available", "order"]

    def form_valid(self, form):
        messages.success(self.request, f"Amenidad '{form.instance.name}' actualizada exitosamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "locations:admin_hotel_amenity_list",
            kwargs={"hotel_pk": self.object.hotel.pk},
        )


class AdminHotelAmenityDeleteView(StaffRequiredMixin, DeleteView):
    """Eliminar amenidad de hotel - Solo admin"""

    model = HotelAmenity
    template_name = "locations/hotel_amenity_confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        amenity_name = self.get_object().name
        messages.success(request, f"Amenidad '{amenity_name}' eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            "locations:admin_hotel_amenity_list",
            kwargs={"hotel_pk": self.object.hotel.pk},
        )


# ===== HOTEL IMAGE VIEWS (Admin) =====
class AdminHotelImageListView(StaffRequiredMixin, ListView):
    """Lista administrativa de imágenes de hotel"""

    model = HotelImage
    template_name = "locations/hotel_image_list.html"
    context_object_name = "images"
    paginate_by = 20

    def get_queryset(self):
        hotel_pk = self.kwargs.get("hotel_pk")
        if hotel_pk:
            return HotelImage.objects.filter(hotel_id=hotel_pk).order_by(
                "order", "-is_featured", "-created_at"
            )
        return HotelImage.objects.select_related("hotel").order_by(
            "hotel", "order", "-is_featured", "-created_at"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hotel_pk = self.kwargs.get("hotel_pk")
        if hotel_pk:
            context["hotel"] = Hotel.objects.get(pk=hotel_pk)
        return context


class AdminHotelImageCreateView(StaffRequiredMixin, CreateView):
    """Crear imagen de hotel - Solo admin"""

    model = HotelImage
    template_name = "locations/hotel_image_form.html"
    fields = ["hotel", "image", "title", "alt_text", "order", "is_featured"]
    success_url = reverse_lazy("locations:admin_hotel_list")

    def form_valid(self, form):
        messages.success(self.request, "Imagen agregada exitosamente.")
        return super().form_valid(form)

    def get_success_url(self):
        hotel_pk = self.object.hotel.pk
        return reverse_lazy(
            "locations:admin_hotel_image_list", kwargs={"hotel_pk": hotel_pk}
        )


class AdminHotelImageUpdateView(StaffRequiredMixin, UpdateView):
    """Actualizar imagen de hotel - Solo admin"""

    model = HotelImage
    template_name = "locations/hotel_image_form.html"
    fields = ["hotel", "image", "title", "alt_text", "order", "is_featured"]

    def form_valid(self, form):
        messages.success(self.request, "Imagen actualizada exitosamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "locations:admin_hotel_image_list",
            kwargs={"hotel_pk": self.object.hotel.pk},
        )


class AdminHotelImageDeleteView(StaffRequiredMixin, DeleteView):
    """Eliminar imagen de hotel - Solo admin"""

    model = HotelImage
    template_name = "locations/hotel_image_confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        hotel_pk = self.get_object().hotel.pk
        messages.success(request, "Imagen eliminada exitosamente.")
        result = super().delete(request, *args, **kwargs)
        return result

    def get_success_url(self):
        return reverse_lazy(
            "locations:admin_hotel_image_list",
            kwargs={"hotel_pk": self.object.hotel.pk},
        )


# ===== HOTEL AMENITY VIEWS (Admin) =====
class AdminHotelAmenityListView(StaffRequiredMixin, ListView):
    """Lista administrativa de amenidades de hotel"""

    model = HotelAmenity
    template_name = "locations/hotel_amenity_list.html"
    context_object_name = "amenities"
    paginate_by = 50

    def get_queryset(self):
        hotel_pk = self.kwargs.get("hotel_pk")
        queryset = HotelAmenity.objects.filter(hotel_id=hotel_pk) if hotel_pk else HotelAmenity.objects.select_related("hotel").all()

        category = self.request.GET.get("category")
        if category:
            queryset = queryset.filter(category=category)

        return queryset.order_by("category", "order", "name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hotel_pk = self.kwargs.get("hotel_pk")
        if hotel_pk:
            context["hotel"] = Hotel.objects.get(pk=hotel_pk)
        context["category_filter"] = self.request.GET.get("category", "")
        context["categories"] = HotelAmenity.AMENITY_CATEGORY_CHOICES
        return context


class AdminHotelAmenityCreateView(StaffRequiredMixin, CreateView):
    """Crear amenidad de hotel - Solo admin"""

    model = HotelAmenity
    template_name = "locations/hotel_amenity_form.html"
    fields = ["hotel", "name", "category", "icon", "description", "is_available", "order"]
    success_url = reverse_lazy("locations:admin_hotel_list")

    def form_valid(self, form):
        messages.success(self.request, f"Amenidad '{form.instance.name}' creada exitosamente.")
        return super().form_valid(form)

    def get_success_url(self):
        hotel_pk = self.object.hotel.pk
        return reverse_lazy(
            "locations:admin_hotel_amenity_list", kwargs={"hotel_pk": hotel_pk}
        )


class AdminHotelAmenityUpdateView(StaffRequiredMixin, UpdateView):
    """Actualizar amenidad de hotel - Solo admin"""

    model = HotelAmenity
    template_name = "locations/hotel_amenity_form.html"
    fields = ["hotel", "name", "category", "icon", "description", "is_available", "order"]

    def form_valid(self, form):
        messages.success(self.request, f"Amenidad '{form.instance.name}' actualizada exitosamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "locations:admin_hotel_amenity_list",
            kwargs={"hotel_pk": self.object.hotel.pk},
        )


class AdminHotelAmenityDeleteView(StaffRequiredMixin, DeleteView):
    """Eliminar amenidad de hotel - Solo admin"""

    model = HotelAmenity
    template_name = "locations/hotel_amenity_confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        amenity_name = self.get_object().name
        messages.success(request, f"Amenidad '{amenity_name}' eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            "locations:admin_hotel_amenity_list",
            kwargs={"hotel_pk": self.object.hotel.pk},
        )
