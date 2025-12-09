"""
Vistas privadas de ubicaciones - Solo lectura, requieren autenticación
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import DetailView, ListView

from .models import City, Country, Rule, Season, Site, State


# ===== COUNTRY VIEWS (Solo Lectura) =====
class CountryListView(LoginRequiredMixin, ListView):
    """Lista de países - Solo lectura"""
    model = Country
    template_name = "locations/country_list.html"
    context_object_name = "countries"
    paginate_by = 20

    def get_queryset(self):
        queryset = Country.objects.filter(is_active=True)
        search = self.request.GET.get("search")
        sort = self.request.GET.get("sort", "name")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(code__icontains=search)
            )

        # Ordenamiento
        if sort == "name":
            queryset = queryset.order_by("name")
        elif sort == "code":
            queryset = queryset.order_by("code")
        else:
            queryset = queryset.order_by("name")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["sort_filter"] = self.request.GET.get("sort", "name")
        context["read_only"] = True  # Indicar que es solo lectura
        return context


class CountryDetailView(LoginRequiredMixin, DetailView):
    """Detalle de país - Solo lectura"""
    model = Country
    template_name = "locations/country_detail.html"
    context_object_name = "country"

    def get_queryset(self):
        return Country.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["states"] = self.object.states.filter(is_active=True).order_by("name")
        context["states_count"] = self.object.states.count()
        context["cities_count"] = City.objects.filter(
            state__country=self.object
        ).count()
        context["read_only"] = True
        return context


# ===== STATE VIEWS (Solo Lectura) =====
class StateListView(LoginRequiredMixin, ListView):
    """Lista de estados - Solo lectura"""
    model = State
    template_name = "locations/state_list.html"
    context_object_name = "states"
    paginate_by = 20

    def get_queryset(self):
        queryset = State.objects.select_related("country").filter(is_active=True)
        search = self.request.GET.get("search")
        country = self.request.GET.get("country")
        sort = self.request.GET.get("sort", "name")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(code__icontains=search)
                | Q(country__name__icontains=search)
            )
        if country:
            queryset = queryset.filter(country_id=country)

        # Ordenamiento
        if sort == "name":
            queryset = queryset.order_by("name")
        elif sort == "code":
            queryset = queryset.order_by("code")
        elif sort == "country":
            queryset = queryset.order_by("country__name", "name")
        else:
            queryset = queryset.order_by("country__name", "name")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["country_filter"] = self.request.GET.get("country", "")
        context["sort_filter"] = self.request.GET.get("sort", "name")
        context["countries"] = Country.objects.filter(is_active=True).order_by("name")
        context["read_only"] = True

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
    """Detalle de estado - Solo lectura"""
    model = State
    template_name = "locations/state_detail.html"
    context_object_name = "state"

    def get_queryset(self):
        return State.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cities"] = self.object.cities.filter(is_active=True).order_by("name")
        context["cities_count"] = self.object.cities.count()
        context["read_only"] = True
        return context


# ===== CITY VIEWS (Solo Lectura) =====
class CityListView(LoginRequiredMixin, ListView):
    """Lista de ciudades - Solo lectura"""
    model = City
    template_name = "locations/city_list.html"
    context_object_name = "cities"
    paginate_by = 20

    def get_queryset(self):
        queryset = City.objects.select_related("state__country").filter(is_active=True)
        search = self.request.GET.get("search")
        country = self.request.GET.get("country")
        state = self.request.GET.get("state")
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

        # Ordenamiento
        if sort == "name":
            queryset = queryset.order_by("name")
        elif sort == "state":
            queryset = queryset.order_by("state__name", "name")
        elif sort == "country":
            queryset = queryset.order_by("state__country__name", "state__name", "name")
        else:
            queryset = queryset.order_by("state__country__name", "state__name", "name")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["country_filter"] = self.request.GET.get("country", "")
        context["state_filter"] = self.request.GET.get("state", "")
        context["sort_filter"] = self.request.GET.get("sort", "name")
        context["countries"] = Country.objects.filter(is_active=True).order_by("name")
        context["states"] = State.objects.filter(is_active=True).order_by(
            "country__name", "name"
        )
        context["read_only"] = True

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
    """Detalle de ciudad - Solo lectura"""
    model = City
    template_name = "locations/city_detail.html"
    context_object_name = "city"

    def get_queryset(self):
        return City.objects.filter(is_active=True)


# ===== SEASON VIEWS (Solo Lectura) =====
class SeasonListView(LoginRequiredMixin, ListView):
    """Lista de temporadas - Solo lectura"""
    model = Season
    template_name = "locations/season_list.html"
    context_object_name = "seasons"
    paginate_by = 20

    def get_queryset(self):
        queryset = Season.objects.filter(is_active=True)
        search = self.request.GET.get("search")
        year = self.request.GET.get("year")
        sort = self.request.GET.get("sort", "year")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        if year:
            queryset = queryset.filter(year=year)

        # Ordenamiento
        if sort == "year":
            queryset = queryset.order_by("-year", "-start_date")
        elif sort == "name":
            queryset = queryset.order_by("name")
        elif sort == "start_date":
            queryset = queryset.order_by("-start_date")
        else:
            queryset = queryset.order_by("-year", "-start_date")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["year_filter"] = self.request.GET.get("year", "")
        context["sort_filter"] = self.request.GET.get("sort", "year")
        context["status_choices"] = Season.SEASON_STATUS_CHOICES
        context["years"] = (
            Season.objects.values_list("year", flat=True).distinct().order_by("-year")
        )
        context["read_only"] = True
        return context


class SeasonDetailView(LoginRequiredMixin, DetailView):
    """Detalle de temporada - Solo lectura"""
    model = Season
    template_name = "locations/season_detail.html"
    context_object_name = "season"

    def get_queryset(self):
        return Season.objects.filter(is_active=True)


# ===== RULE VIEWS (Solo Lectura) =====
class RuleListView(LoginRequiredMixin, ListView):
    """Lista de reglas - Solo lectura"""
    model = Rule
    template_name = "locations/rule_list.html"
    context_object_name = "rules"
    paginate_by = 20

    def get_queryset(self):
        queryset = Rule.objects.filter(is_active=True)

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

        return queryset.order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["rule_type_choices"] = Rule.RULE_TYPE_CHOICES
        context["read_only"] = True
        return context


class RuleDetailView(LoginRequiredMixin, DetailView):
    """Detalle de regla - Solo lectura"""
    model = Rule
    template_name = "locations/rule_detail.html"
    context_object_name = "rule"

    def get_queryset(self):
        return Rule.objects.filter(is_active=True)


# ===== SITE VIEWS (Solo Lectura) =====
class SiteListView(LoginRequiredMixin, ListView):
    """Lista de sitios - Solo lectura"""
    model = Site
    template_name = "locations/site_list.html"
    context_object_name = "sites"
    paginate_by = 20

    def get_queryset(self):
        queryset = Site.objects.select_related("country", "state", "city").filter(
            is_active=True
        )

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

        return queryset.order_by("site_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["countries"] = Country.objects.filter(is_active=True).order_by("name")
        context["states"] = State.objects.filter(is_active=True).order_by("name")
        context["read_only"] = True
        return context


class SiteDetailView(LoginRequiredMixin, DetailView):
    """Detalle de sitio - Solo lectura"""
    model = Site
    template_name = "locations/site_detail.html"
    context_object_name = "site"

    def get_queryset(self):
        return Site.objects.filter(is_active=True)








