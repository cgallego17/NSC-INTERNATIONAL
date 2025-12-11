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
    """API para obtener países - Público
    
    Parámetros:
    - q: término de búsqueda (opcional)
    - id: ID específico de país (opcional)
    """
    import unicodedata

    # Si se solicita un ID específico
    country_id = request.GET.get("id")
    if country_id:
        try:
            country = Country.objects.get(id=country_id, is_active=True)
            data = [{"id": country.id, "name": country.name, "code": country.code}]
            return JsonResponse(data, safe=False)
        except Country.DoesNotExist:
            return JsonResponse([], safe=False)

    # Búsqueda por término
    search_query = request.GET.get("q", "").strip()
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

    # Filtrar por término de búsqueda si se proporciona
    if search_query:
        search_normalized = unicodedata.normalize("NFD", search_query.lower())
        search_normalized = "".join(
            c for c in search_normalized if unicodedata.category(c) != "Mn"
        )

        filtered_countries = []
        for country in unique_countries:
            country_normalized = unicodedata.normalize("NFD", country.name.lower())
            country_normalized = "".join(
                c for c in country_normalized if unicodedata.category(c) != "Mn"
            )

            if search_normalized in country_normalized:
                filtered_countries.append(country)

        unique_countries = filtered_countries

    data = [
        {"id": country.id, "name": country.name, "code": country.code}
        for country in unique_countries
    ]
    return JsonResponse(data, safe=False)


def states_api(request):
    """API para obtener estados - Público
    
    Parámetros:
    - country: ID del país para filtrar (opcional)
    - q: término de búsqueda (opcional)
    - id: ID específico de estado (opcional)
    """
    import unicodedata

    # Si se solicita un ID específico
    state_id = request.GET.get("id")
    if state_id:
        try:
            state = State.objects.get(id=state_id, is_active=True)
            data = [{"id": state.id, "name": state.name, "country_id": state.country.id}]
            return JsonResponse(data, safe=False)
        except State.DoesNotExist:
            return JsonResponse([], safe=False)

    # Filtrar por país si se proporciona
    country_id = request.GET.get("country")
    if country_id:
        states = State.objects.filter(country_id=country_id, is_active=True).order_by(
            "name"
        )
    else:
        states = State.objects.filter(is_active=True).order_by("country__name", "name")

    # Filtrar por término de búsqueda si se proporciona
    search_query = request.GET.get("q", "").strip()
    if search_query:
        search_normalized = unicodedata.normalize("NFD", search_query.lower())
        search_normalized = "".join(
            c for c in search_normalized if unicodedata.category(c) != "Mn"
        )

        filtered_states = []
        for state in states:
            state_normalized = unicodedata.normalize("NFD", state.name.lower())
            state_normalized = "".join(
                c for c in state_normalized if unicodedata.category(c) != "Mn"
            )

            if search_normalized in state_normalized:
                filtered_states.append(state)

        states = filtered_states

    data = [
        {"id": state.id, "name": state.name, "country_id": state.country.id}
        for state in states
    ]
    return JsonResponse(data, safe=False)


def cities_api(request):
    """API para obtener ciudades - Público
    
    Parámetros:
    - state: ID del estado para filtrar (opcional)
    - q: término de búsqueda (opcional)
    - id: ID específico de ciudad (opcional)
    """
    import unicodedata

    # Si se solicita un ID específico
    city_id = request.GET.get("id")
    if city_id:
        try:
            city = City.objects.get(id=city_id, is_active=True)
            data = [{"id": city.id, "name": city.name, "state_id": city.state.id}]
            return JsonResponse(data, safe=False)
        except City.DoesNotExist:
            return JsonResponse([], safe=False)

    # Filtrar por estado si se proporciona
    state_id = request.GET.get("state")
    if state_id:
        cities = City.objects.filter(state_id=state_id, is_active=True).order_by("name")
    else:
        cities = City.objects.filter(is_active=True).order_by(
            "state__country__name", "state__name", "name"
        )

    # Filtrar por término de búsqueda si se proporciona
    search_query = request.GET.get("q", "").strip()
    if search_query:
        search_normalized = unicodedata.normalize("NFD", search_query.lower())
        search_normalized = "".join(
            c for c in search_normalized if unicodedata.category(c) != "Mn"
        )

        filtered_cities = []
        for city in cities:
            city_normalized = unicodedata.normalize("NFD", city.name.lower())
            city_normalized = "".join(
                c for c in city_normalized if unicodedata.category(c) != "Mn"
            )

            if search_normalized in city_normalized:
                filtered_cities.append(city)

        cities = filtered_cities

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
