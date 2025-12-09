"""
Vistas públicas de ubicaciones - APIs públicas sin autenticación
"""

from django.http import JsonResponse
from .models import City, Country, Rule, Season, Site, State


def get_states_by_country(request, country_id):
    """Obtener estados por país para AJAX - Público"""
    states = State.objects.filter(country_id=country_id, is_active=True).order_by(
        "name"
    )
    data = [{"id": state.id, "name": state.name} for state in states]
    return JsonResponse(data, safe=False)


def get_cities_by_state(request, state_id):
    """Obtener ciudades por estado para AJAX - Público"""
    cities = City.objects.filter(state_id=state_id, is_active=True).order_by("name")
    data = [{"id": city.id, "name": city.name} for city in cities]
    return JsonResponse(data, safe=False)


def countries_api(request):
    """API para obtener países - Público"""
    import unicodedata

    all_countries = Country.objects.filter(is_active=True).order_by("name")

    # Normalizar nombres y eliminar duplicados
    seen_normalized = set()
    unique_countries = []
    for country in all_countries:
        # Normalizar nombre (remover acentos)
        nfd = unicodedata.normalize("NFD", country.name.lower().strip())
        normalized = "".join(c for c in nfd if unicodedata.category(c) != "Mn")

        if normalized not in seen_normalized:
            seen_normalized.add(normalized)
            unique_countries.append(country)

    data = [
        {"id": country.id, "name": country.name, "code": country.code}
        for country in unique_countries
    ]
    return JsonResponse(data, safe=False)


def states_api(request):
    """API para obtener estados - Público"""
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
    """API para obtener ciudades - Público"""
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
    """API para obtener temporadas - Público"""
    seasons = Season.objects.filter(is_active=True).order_by("name")
    data = [
        {"id": season.id, "name": season.name, "year": season.year}
        for season in seasons
    ]
    return JsonResponse(data, safe=False)


def rules_api(request):
    """API para obtener reglas - Público"""
    rules = Rule.objects.filter(is_active=True).order_by("name")
    data = [
        {"id": rule.id, "name": rule.name, "rule_type": rule.rule_type}
        for rule in rules
    ]
    return JsonResponse(data, safe=False)


def sites_api(request):
    """API para obtener sitios - Público"""
    city_id = request.GET.get("city")

    sites_query = Site.objects.filter(is_active=True)

    # Filtrar por ciudad si se proporciona
    if city_id:
        try:
            city_id = int(city_id)
            # Filtrar estrictamente por ciudad
            sites_query = sites_query.filter(city_id=city_id)
        except (ValueError, TypeError):
            pass

    sites = (
        sites_query.select_related("state", "city", "country")
        .order_by("site_name")
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
