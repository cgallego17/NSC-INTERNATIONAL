"""
Vistas administrativas de ubicaciones - Solo staff/superuser, CRUD completo
"""

from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
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
    HotelReservation,
    HotelRoom,
    HotelService,
    Rule,
    Season,
    Site,
    State,
)
from apps.core.mixins import StaffRequiredMixin


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
        return context


class AdminHotelCreateView(StaffRequiredMixin, CreateView):
    """Crear hotel - Solo admin"""

    model = Hotel
    template_name = "locations/hotel_form.html"
    fields = [
        "hotel_name",
        "address",
        "city",
        "state",
        "country",
        "photo",
        "information",
        "registration_url",
        "capacity",
        "contact_name",
        "contact_email",
        "contact_phone",
        "is_active",
    ]
    success_url = reverse_lazy("locations:admin_hotel_list")

    def form_valid(self, form):
        messages.success(self.request, "Hotel creado exitosamente.")
        return super().form_valid(form)


class AdminHotelUpdateView(StaffRequiredMixin, UpdateView):
    """Actualizar hotel - Solo admin"""

    model = Hotel
    template_name = "locations/hotel_form.html"
    fields = [
        "hotel_name",
        "address",
        "city",
        "state",
        "country",
        "photo",
        "information",
        "registration_url",
        "capacity",
        "contact_name",
        "contact_email",
        "contact_phone",
        "is_active",
    ]
    success_url = reverse_lazy("locations:admin_hotel_list")

    def form_valid(self, form):
        # Manejar eliminación de foto
        if self.request.POST.get("remove_photo") == "1":
            if self.object.photo:
                self.object.photo.delete()
                self.object.photo = None
                self.object.save()

        messages.success(self.request, "Hotel actualizado exitosamente.")
        return super().form_valid(form)


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
        queryset = HotelRoom.objects.select_related("hotel").all()

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
        "room_type",
        "capacity",
        "price_per_night",
        "description",
        "is_available",
    ]
    success_url = reverse_lazy("locations:admin_hotel_room_list")

    def form_valid(self, form):
        messages.success(self.request, "Habitación creada exitosamente.")
        return super().form_valid(form)


class AdminHotelRoomUpdateView(StaffRequiredMixin, UpdateView):
    """Actualizar habitación - Solo admin"""

    model = HotelRoom
    template_name = "locations/hotel_room_form.html"
    fields = [
        "hotel",
        "room_number",
        "room_type",
        "capacity",
        "price_per_night",
        "description",
        "is_available",
    ]
    success_url = reverse_lazy("locations:admin_hotel_room_list")

    def form_valid(self, form):
        messages.success(self.request, "Habitación actualizada exitosamente.")
        return super().form_valid(form)


class AdminHotelRoomDeleteView(StaffRequiredMixin, DeleteView):
    """Eliminar habitación - Solo admin"""

    model = HotelRoom
    template_name = "locations/hotel_room_confirm_delete.html"
    success_url = reverse_lazy("locations:admin_hotel_room_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Habitación eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)


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
