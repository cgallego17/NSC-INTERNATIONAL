from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from apps.core.mixins import StaffRequiredMixin, SuperuserRequiredMixin

from .models import City, Country, Hotel, Rule, Season, Site, State


# ===== COUNTRY VIEWS =====
class CountryListView(StaffRequiredMixin, ListView):
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
        return context


class CountryDetailView(StaffRequiredMixin, DetailView):
    model = Country
    template_name = "locations/country_detail.html"
    context_object_name = "country"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["states"] = self.object.states.filter(is_active=True).order_by("name")
        context["states_count"] = self.object.states.count()
        context["cities_count"] = City.objects.filter(
            state__country=self.object
        ).count()
        return context


class CountryCreateView(StaffRequiredMixin, CreateView):
    model = Country
    template_name = "locations/country_form.html"
    fields = ["name", "code", "is_active"]
    success_url = reverse_lazy("locations:country_list")

    def form_valid(self, form):
        messages.success(self.request, "País creado exitosamente.")
        return super().form_valid(form)


class CountryUpdateView(StaffRequiredMixin, UpdateView):
    model = Country
    template_name = "locations/country_form.html"
    fields = ["name", "code", "is_active"]

    def get_success_url(self):
        return reverse_lazy("locations:country_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "País actualizado exitosamente.")
        return super().form_valid(form)


class CountryDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Country
    template_name = "locations/country_confirm_delete.html"
    success_url = reverse_lazy("locations:country_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "País eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)


# ===== STATE VIEWS =====
class StateListView(StaffRequiredMixin, ListView):
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
        context["countries"] = Country.objects.filter(is_active=True).order_by("name")

        # Obtener el país seleccionado para mostrar en el filtro activo
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


class StateDetailView(StaffRequiredMixin, DetailView):
    model = State
    template_name = "locations/state_detail.html"
    context_object_name = "state"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cities"] = self.object.cities.filter(is_active=True).order_by("name")
        context["cities_count"] = self.object.cities.count()
        return context


class StateCreateView(StaffRequiredMixin, CreateView):
    model = State
    template_name = "locations/state_form.html"
    fields = ["country", "name", "code", "is_active"]
    success_url = reverse_lazy("locations:state_list")

    def form_valid(self, form):
        messages.success(self.request, "Estado creado exitosamente.")
        return super().form_valid(form)


class StateUpdateView(StaffRequiredMixin, UpdateView):
    model = State
    template_name = "locations/state_form.html"
    fields = ["country", "name", "code", "is_active"]

    def get_success_url(self):
        return reverse_lazy("locations:state_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Estado actualizado exitosamente.")
        return super().form_valid(form)


class StateDeleteView(SuperuserRequiredMixin, DeleteView):
    model = State
    template_name = "locations/state_confirm_delete.html"
    success_url = reverse_lazy("locations:state_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Estado eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)


# ===== CITY VIEWS =====
class CityListView(StaffRequiredMixin, ListView):
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
        context["countries"] = Country.objects.filter(is_active=True).order_by("name")
        context["states"] = State.objects.filter(is_active=True).order_by(
            "country__name", "name"
        )

        # Obtener el país y estado seleccionados para mostrar en los filtros activos
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


class CityDetailView(StaffRequiredMixin, DetailView):
    model = City
    template_name = "locations/city_detail.html"
    context_object_name = "city"


class CityCreateView(StaffRequiredMixin, CreateView):
    model = City
    template_name = "locations/city_form.html"
    fields = ["state", "name", "is_active"]
    success_url = reverse_lazy("locations:city_list")

    def form_valid(self, form):
        messages.success(self.request, "Ciudad creada exitosamente.")
        return super().form_valid(form)


class CityUpdateView(StaffRequiredMixin, UpdateView):
    model = City
    template_name = "locations/city_form.html"
    fields = ["state", "name", "is_active"]

    def get_success_url(self):
        return reverse_lazy("locations:city_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Ciudad actualizada exitosamente.")
        return super().form_valid(form)


class CityDeleteView(SuperuserRequiredMixin, DeleteView):
    model = City
    template_name = "locations/city_confirm_delete.html"
    success_url = reverse_lazy("locations:city_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Ciudad eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)


# ===== SEASON VIEWS =====
class SeasonListView(StaffRequiredMixin, ListView):
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
        return context


class SeasonDetailView(StaffRequiredMixin, DetailView):
    model = Season
    template_name = "locations/season_detail.html"
    context_object_name = "season"


class SeasonCreateView(StaffRequiredMixin, CreateView):
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
    success_url = reverse_lazy("locations:season_list")

    def form_valid(self, form):
        messages.success(self.request, "Temporada creada exitosamente.")
        return super().form_valid(form)


class SeasonUpdateView(StaffRequiredMixin, UpdateView):
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
        return reverse_lazy("locations:season_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Temporada actualizada exitosamente.")
        return super().form_valid(form)


class SeasonDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Season
    template_name = "locations/season_confirm_delete.html"
    success_url = reverse_lazy("locations:season_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Temporada eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)


# ===== AJAX VIEWS =====
def get_states_by_country(request, country_id):
    """Obtener estados por país para AJAX"""
    states = State.objects.filter(country_id=country_id, is_active=True).order_by(
        "name"
    )
    data = [{"id": state.id, "name": state.name} for state in states]
    return JsonResponse(data, safe=False)


def get_cities_by_state(request, state_id):
    """Obtener ciudades por estado para AJAX"""
    cities = City.objects.filter(state_id=state_id, is_active=True).order_by("name")
    data = [{"id": city.id, "name": city.name} for city in cities]
    return JsonResponse(data, safe=False)


# ===== API VIEWS =====
def countries_api(request):
    """API para obtener países con soporte de búsqueda (ignora tildes)"""
    import unicodedata

    def normalize_text(text):
        """Normaliza texto removiendo acentos y convirtiendo a minúsculas"""
        if not text:
            return ""
        nfd = unicodedata.normalize("NFD", text.lower().strip())
        return "".join(c for c in nfd if unicodedata.category(c) != "Mn")

    # Si hay un ID específico, devolver solo ese país
    country_id = request.GET.get("id")
    if country_id:
        try:
            country = Country.objects.filter(pk=int(country_id), is_active=True).first()
            if country:
                return JsonResponse(
                    [{"id": country.id, "name": country.name, "code": country.code}],
                    safe=False,
                )
        except (ValueError, TypeError):
            pass

    all_countries = Country.objects.filter(is_active=True).order_by("name")

    # Normalizar nombres y eliminar duplicados
    seen_normalized = set()
    unique_countries = []
    for country in all_countries:
        normalized = normalize_text(country.name)
        if normalized not in seen_normalized:
            seen_normalized.add(normalized)
            unique_countries.append(country)

    # Búsqueda por término (ignora tildes)
    search_term = request.GET.get("q", "").strip()
    if search_term:
        normalized_search = normalize_text(search_term)

        filtered_countries = []
        for country in unique_countries:
            # Normalizar nombre del país y código para comparar
            normalized_country_name = normalize_text(country.name)
            normalized_country_code = (
                normalize_text(country.code) if country.code else ""
            )

            if (
                normalized_search in normalized_country_name
                or normalized_search in normalized_country_code
            ):
                filtered_countries.append(country)

        unique_countries = filtered_countries

    # Limitar resultados a 50 para mejor rendimiento
    data = [
        {"id": country.id, "name": country.name, "code": country.code}
        for country in unique_countries[:50]
    ]
    return JsonResponse(data, safe=False)


def states_api(request):
    """API para obtener estados con soporte de búsqueda (ignora tildes)"""
    import unicodedata

    def normalize_text(text):
        """Normaliza texto removiendo acentos y convirtiendo a minúsculas"""
        if not text:
            return ""
        nfd = unicodedata.normalize("NFD", text.lower().strip())
        return "".join(c for c in nfd if unicodedata.category(c) != "Mn")

    # Si hay un ID específico, devolver solo ese estado
    state_id = request.GET.get("id")
    if state_id:
        try:
            state = State.objects.filter(pk=int(state_id), is_active=True).first()
            if state:
                return JsonResponse(
                    [
                        {
                            "id": state.id,
                            "name": state.name,
                            "country_id": state.country.id,
                        }
                    ],
                    safe=False,
                )
        except (ValueError, TypeError):
            pass

    country_id = request.GET.get("country")
    search_term = request.GET.get("q", "").strip()

    if country_id:
        states = State.objects.filter(country_id=country_id, is_active=True).order_by(
            "name"
        )
    else:
        states = State.objects.filter(is_active=True).order_by("country__name", "name")

    # Filtrar por término de búsqueda (ignora tildes)
    if search_term:
        normalized_search = normalize_text(search_term)
        filtered_states = []
        for state in states:
            normalized_state_name = normalize_text(state.name)
            normalized_state_code = normalize_text(state.code) if state.code else ""

            if (
                normalized_search in normalized_state_name
                or normalized_search in normalized_state_code
            ):
                filtered_states.append(state)

        states = filtered_states

    # Limitar resultados a 50 para mejor rendimiento
    data = [
        {"id": state.id, "name": state.name, "country_id": state.country.id}
        for state in states[:50]
    ]
    return JsonResponse(data, safe=False)


def cities_api(request):
    """API para obtener ciudades con soporte de búsqueda (ignora tildes)"""
    import unicodedata

    def normalize_text(text):
        """Normaliza texto removiendo acentos y convirtiendo a minúsculas"""
        if not text:
            return ""
        nfd = unicodedata.normalize("NFD", text.lower().strip())
        return "".join(c for c in nfd if unicodedata.category(c) != "Mn")

    # Si hay un ID específico, devolver solo esa ciudad
    city_id = request.GET.get("id")
    if city_id:
        try:
            city = City.objects.filter(pk=int(city_id), is_active=True).first()
            if city:
                return JsonResponse(
                    [{"id": city.id, "name": city.name, "state_id": city.state.id}],
                    safe=False,
                )
        except (ValueError, TypeError):
            pass

    state_id = request.GET.get("state")
    country_id = request.GET.get("country")
    search_term = request.GET.get("q", "").strip()

    if state_id:
        cities = City.objects.filter(state_id=state_id, is_active=True).order_by("name")
    elif country_id:
        # Si solo hay country_id, obtener ciudades de ese país
        cities = City.objects.filter(
            state__country_id=country_id, is_active=True
        ).order_by("state__name", "name")
    else:
        cities = City.objects.filter(is_active=True).order_by(
            "state__country__name", "state__name", "name"
        )

    # Filtrar por término de búsqueda (ignora tildes)
    if search_term:
        normalized_search = normalize_text(search_term)
        filtered_cities = []
        for city in cities:
            normalized_city_name = normalize_text(city.name)
            if normalized_search in normalized_city_name:
                filtered_cities.append(city)

        cities = filtered_cities

    # Limitar resultados a 50 para mejor rendimiento
    data = [
        {"id": city.id, "name": city.name, "state_id": city.state.id}
        for city in cities[:50]
    ]
    return JsonResponse(data, safe=False)


def seasons_api(request):
    """API para obtener temporadas"""
    seasons = Season.objects.filter(is_active=True).order_by("name")
    data = [
        {"id": season.id, "name": season.name, "year": season.year}
        for season in seasons
    ]
    return JsonResponse(data, safe=False)


# ===== RULE VIEWS =====
class RuleListView(StaffRequiredMixin, ListView):
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
        return context


class RuleDetailView(StaffRequiredMixin, DetailView):
    model = Rule
    template_name = "locations/rule_detail.html"
    context_object_name = "rule"


class RuleCreateView(StaffRequiredMixin, CreateView):
    model = Rule
    template_name = "locations/rule_form.html"
    fields = ["name", "description", "rule_type", "is_active"]
    success_url = reverse_lazy("locations:rule_list")

    def form_valid(self, form):
        messages.success(self.request, "Regla creada exitosamente.")
        return super().form_valid(form)


class RuleUpdateView(StaffRequiredMixin, UpdateView):
    model = Rule
    template_name = "locations/rule_form.html"
    fields = ["name", "description", "rule_type", "is_active"]
    success_url = reverse_lazy("locations:rule_list")

    def form_valid(self, form):
        messages.success(self.request, "Regla actualizada exitosamente.")
        return super().form_valid(form)


class RuleDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Rule
    template_name = "locations/rule_confirm_delete.html"
    success_url = reverse_lazy("locations:rule_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Regla eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)


def rules_api(request):
    """API para obtener reglas"""
    rules = Rule.objects.filter(is_active=True).order_by("name")
    data = [
        {"id": rule.id, "name": rule.name, "rule_type": rule.rule_type}
        for rule in rules
    ]
    return JsonResponse(data, safe=False)


# ===== SITE VIEWS =====
class SiteListView(StaffRequiredMixin, ListView):
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
        context["countries"] = Country.objects.filter(is_active=True).order_by("name")
        context["states"] = State.objects.filter(is_active=True).order_by("name")
        return context


class SiteDetailView(StaffRequiredMixin, DetailView):
    model = Site
    template_name = "locations/site_detail.html"
    context_object_name = "site"


class SiteCreateView(StaffRequiredMixin, CreateView):
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
    success_url = reverse_lazy("locations:site_list")

    def form_valid(self, form):
        messages.success(self.request, "Sitio creado exitosamente.")
        return super().form_valid(form)


class SiteUpdateView(StaffRequiredMixin, UpdateView):
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
    success_url = reverse_lazy("locations:site_list")

    def form_valid(self, form):
        messages.success(self.request, "Sitio actualizado exitosamente.")
        return super().form_valid(form)


class SiteDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Site
    template_name = "locations/site_confirm_delete.html"
    success_url = reverse_lazy("locations:site_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Sitio eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)


def sites_api(request):
    """API para obtener sitios con información de ubicación"""
    city_id = request.GET.get("city")
    site_id = request.GET.get("id")

    sites_query = Site.objects.filter(is_active=True)

    # Filtrar por ID específico si se proporciona (tiene prioridad)
    if site_id:
        try:
            site_id = int(site_id)
            sites_query = sites_query.filter(id=site_id)
        except (ValueError, TypeError):
            pass
    # Filtrar por ciudad si se proporciona (solo si no hay ID específico)
    elif city_id:
        try:
            city_id = int(city_id)
            # Filtrar estrictamente por ciudad
            sites_query = sites_query.filter(city_id=city_id)
        except (ValueError, TypeError):
            pass

    sites = sites_query.select_related("state", "city", "country").values(
        "id",
        "site_name",
        "abbreviation",
        "state_id",
        "state__name",
        "city_id",
        "city__name",
        "country__name",
    )

    # Convert to list and add computed fields
    sites_list = []
    for site in sites:
        sites_list.append(
            {
                "id": site["id"],
                "site_name": site["site_name"],
                "abbreviation": site["abbreviation"],
                "state_id": site["state_id"],
                "state_name": site["state__name"],
                "city_id": site["city_id"],
                "city_name": site["city__name"],
                "country_name": site["country__name"],
            }
        )

    return JsonResponse(sites_list, safe=False)


def hotels_api(request):
    """API para obtener hoteles"""
    city_id = request.GET.get("city")
    hotel_id = request.GET.get("id")

    hotels_query = Hotel.objects.filter(is_active=True)

    # Filtrar por ID específico si se proporciona (tiene prioridad)
    if hotel_id:
        try:
            hotel_id = int(hotel_id)
            hotels_query = hotels_query.filter(id=hotel_id)
        except (ValueError, TypeError):
            pass
    # Filtrar por ciudad si se proporciona (solo si no hay ID específico)
    elif city_id:
        try:
            city_id = int(city_id)
            # Filtrar estrictamente por ciudad
            hotels_query = hotels_query.filter(city_id=city_id)
        except (ValueError, TypeError):
            pass

    hotels = hotels_query.order_by("city__name", "hotel_name")

    data = [
        {
            "id": hotel.id,
            "name": hotel.hotel_name,
            "hotel_name": hotel.hotel_name,  # Incluir ambos campos para compatibilidad
            "city_id": hotel.city.id if hotel.city else None,
        }
        for hotel in hotels
    ]
    return JsonResponse(data, safe=False)
