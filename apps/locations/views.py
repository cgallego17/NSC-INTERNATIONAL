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

from .models import City, Country, Rule, Season, Site, State


# ===== COUNTRY VIEWS =====
class CountryListView(LoginRequiredMixin, ListView):
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


class CountryDetailView(LoginRequiredMixin, DetailView):
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


class CountryCreateView(LoginRequiredMixin, CreateView):
    model = Country
    template_name = "locations/country_form.html"
    fields = ["name", "code", "is_active"]
    success_url = reverse_lazy("locations:country_list")

    def form_valid(self, form):
        messages.success(self.request, "País creado exitosamente.")
        return super().form_valid(form)


class CountryUpdateView(LoginRequiredMixin, UpdateView):
    model = Country
    template_name = "locations/country_form.html"
    fields = ["name", "code", "is_active"]

    def get_success_url(self):
        return reverse_lazy("locations:country_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "País actualizado exitosamente.")
        return super().form_valid(form)


class CountryDeleteView(LoginRequiredMixin, DeleteView):
    model = Country
    template_name = "locations/country_confirm_delete.html"
    success_url = reverse_lazy("locations:country_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "País eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)


# ===== STATE VIEWS =====
class StateListView(LoginRequiredMixin, ListView):
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


class StateDetailView(LoginRequiredMixin, DetailView):
    model = State
    template_name = "locations/state_detail.html"
    context_object_name = "state"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cities"] = self.object.cities.filter(is_active=True).order_by("name")
        context["cities_count"] = self.object.cities.count()
        return context


class StateCreateView(LoginRequiredMixin, CreateView):
    model = State
    template_name = "locations/state_form.html"
    fields = ["country", "name", "code", "is_active"]
    success_url = reverse_lazy("locations:state_list")

    def form_valid(self, form):
        messages.success(self.request, "Estado creado exitosamente.")
        return super().form_valid(form)


class StateUpdateView(LoginRequiredMixin, UpdateView):
    model = State
    template_name = "locations/state_form.html"
    fields = ["country", "name", "code", "is_active"]

    def get_success_url(self):
        return reverse_lazy("locations:state_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Estado actualizado exitosamente.")
        return super().form_valid(form)


class StateDeleteView(LoginRequiredMixin, DeleteView):
    model = State
    template_name = "locations/state_confirm_delete.html"
    success_url = reverse_lazy("locations:state_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Estado eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)


# ===== CITY VIEWS =====
class CityListView(LoginRequiredMixin, ListView):
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


class CityDetailView(LoginRequiredMixin, DetailView):
    model = City
    template_name = "locations/city_detail.html"
    context_object_name = "city"


class CityCreateView(LoginRequiredMixin, CreateView):
    model = City
    template_name = "locations/city_form.html"
    fields = ["state", "name", "is_active"]
    success_url = reverse_lazy("locations:city_list")

    def form_valid(self, form):
        messages.success(self.request, "Ciudad creada exitosamente.")
        return super().form_valid(form)


class CityUpdateView(LoginRequiredMixin, UpdateView):
    model = City
    template_name = "locations/city_form.html"
    fields = ["state", "name", "is_active"]

    def get_success_url(self):
        return reverse_lazy("locations:city_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Ciudad actualizada exitosamente.")
        return super().form_valid(form)


class CityDeleteView(LoginRequiredMixin, DeleteView):
    model = City
    template_name = "locations/city_confirm_delete.html"
    success_url = reverse_lazy("locations:city_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Ciudad eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)


# ===== SEASON VIEWS =====
class SeasonListView(LoginRequiredMixin, ListView):
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


class SeasonDetailView(LoginRequiredMixin, DetailView):
    model = Season
    template_name = "locations/season_detail.html"
    context_object_name = "season"


class SeasonCreateView(LoginRequiredMixin, CreateView):
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


class SeasonUpdateView(LoginRequiredMixin, UpdateView):
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


class SeasonDeleteView(LoginRequiredMixin, DeleteView):
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
    """API para obtener países"""
    countries = Country.objects.filter(is_active=True).order_by("name")
    data = [
        {"id": country.id, "name": country.name, "code": country.code}
        for country in countries
    ]
    return JsonResponse(data, safe=False)


def states_api(request):
    """API para obtener estados"""
    country_id = request.GET.get("country")
    if country_id:
        states = State.objects.filter(country_id=country_id, is_active=True).order_by(
            "name"
        )
    else:
        states = State.objects.filter(is_active=True).order_by("country__name", "name")

    data = [
        {"id": state.id, "name": state.name, "country_id": state.country.id}
        for state in states
    ]
    return JsonResponse(data, safe=False)


def cities_api(request):
    """API para obtener ciudades"""
    state_id = request.GET.get("state")
    if state_id:
        cities = City.objects.filter(state_id=state_id, is_active=True).order_by("name")
    else:
        cities = City.objects.filter(is_active=True).order_by(
            "state__country__name", "state__name", "name"
        )

    data = [
        {"id": city.id, "name": city.name, "state_id": city.state.id} for city in cities
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
class RuleListView(LoginRequiredMixin, ListView):
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


class RuleDetailView(LoginRequiredMixin, DetailView):
    model = Rule
    template_name = "locations/rule_detail.html"
    context_object_name = "rule"


class RuleCreateView(LoginRequiredMixin, CreateView):
    model = Rule
    template_name = "locations/rule_form.html"
    fields = ["name", "description", "rule_type", "is_active"]
    success_url = reverse_lazy("locations:rule_list")

    def form_valid(self, form):
        messages.success(self.request, "Regla creada exitosamente.")
        return super().form_valid(form)


class RuleUpdateView(LoginRequiredMixin, UpdateView):
    model = Rule
    template_name = "locations/rule_form.html"
    fields = ["name", "description", "rule_type", "is_active"]
    success_url = reverse_lazy("locations:rule_list")

    def form_valid(self, form):
        messages.success(self.request, "Regla actualizada exitosamente.")
        return super().form_valid(form)


class RuleDeleteView(LoginRequiredMixin, DeleteView):
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
class SiteListView(LoginRequiredMixin, ListView):
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


class SiteDetailView(LoginRequiredMixin, DetailView):
    model = Site
    template_name = "locations/site_detail.html"
    context_object_name = "site"


class SiteCreateView(LoginRequiredMixin, CreateView):
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


class SiteUpdateView(LoginRequiredMixin, UpdateView):
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


class SiteDeleteView(LoginRequiredMixin, DeleteView):
    model = Site
    template_name = "locations/site_confirm_delete.html"
    success_url = reverse_lazy("locations:site_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Sitio eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)


def sites_api(request):
    """API para obtener sitios con información de ubicación"""
    sites = (
        Site.objects.filter(is_active=True)
        .select_related("state", "city", "country")
        .values(
            "id",
            "site_name",
            "abbreviation",
            "state_id",
            "state__name",
            "city_id",
            "city__name",
            "country__name",
        )
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
