"""
Vistas públicas de ubicaciones - APIs públicas sin autenticación
"""

from django.core.cache import cache
from django.http import JsonResponse
from .models import City, Country, Rule, Season, Site, State


def _get_client_ip(request):
    """Obtiene la IP del cliente, considerando proxies"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', 'unknown')
    return ip


def _check_rate_limit(request, cache_key_prefix, max_requests=150, window_seconds=3600):
    """
    Verifica rate limiting usando caché de Django.

    Args:
        request: HttpRequest object
        cache_key_prefix: Prefijo para la clave de caché
        max_requests: Número máximo de requests permitidos (por defecto 150/hora)
        window_seconds: Ventana de tiempo en segundos (por defecto 1 hora)

    Returns:
        tuple: (is_allowed, remaining_requests)
    """
    # Obtener IP del cliente
    ip_address = _get_client_ip(request)

    # Crear clave de caché única por IP
    cache_key = f"{cache_key_prefix}_{ip_address}"

    # Obtener contador actual
    request_count = cache.get(cache_key, 0)

    # Verificar si se excedió el límite
    if request_count >= max_requests:
        return False, 0

    # Incrementar contador
    cache.set(cache_key, request_count + 1, window_seconds)

    return True, max_requests - request_count - 1


def get_states_by_country(request, country_id):
    """
    Obtener estados por país para AJAX - Público

    Rate Limiting: 150 requests por hora por IP
    Caché: 30 minutos
    """
    # Rate limiting: 150 requests por hora por IP
    is_allowed, remaining = _check_rate_limit(
        request,
        "locations_states_by_country",
        max_requests=150,
        window_seconds=3600
    )

    if not is_allowed:
        return JsonResponse(
            {"error": "Rate limit exceeded. Please try again later."},
            status=429
        )

    # Validar country_id
    try:
        country_id = int(country_id)
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid country ID"}, status=400)

    # Clave de caché
    cache_key = f"locations_states_by_country_{country_id}"

    # Intentar obtener del caché
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        response = JsonResponse(cached_data, safe=False)
        response['X-RateLimit-Remaining'] = str(remaining)
        response['X-RateLimit-Limit'] = '150'
        return response

    # Obtener datos
    states = State.objects.filter(country_id=country_id, is_active=True).order_by(
        "name"
    )
    data = [{"id": state.id, "name": state.name} for state in states]

    # Guardar en caché por 30 minutos (1800 segundos)
    cache.set(cache_key, data, 1800)

    # Agregar headers de rate limit
    response = JsonResponse(data, safe=False)
    response['X-RateLimit-Remaining'] = str(remaining)
    response['X-RateLimit-Limit'] = '150'
    return response


def get_cities_by_state(request, state_id):
    """
    Obtener ciudades por estado para AJAX - Público

    Rate Limiting: 150 requests por hora por IP
    Caché: 30 minutos
    """
    # Rate limiting: 150 requests por hora por IP
    is_allowed, remaining = _check_rate_limit(
        request,
        "locations_cities_by_state",
        max_requests=150,
        window_seconds=3600
    )

    if not is_allowed:
        return JsonResponse(
            {"error": "Rate limit exceeded. Please try again later."},
            status=429
        )

    # Validar state_id
    try:
        state_id = int(state_id)
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid state ID"}, status=400)

    # Clave de caché
    cache_key = f"locations_cities_by_state_{state_id}"

    # Intentar obtener del caché
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        response = JsonResponse(cached_data, safe=False)
        response['X-RateLimit-Remaining'] = str(remaining)
        response['X-RateLimit-Limit'] = '150'
        return response

    # Obtener datos
    cities = City.objects.filter(state_id=state_id, is_active=True).order_by("name")
    data = [{"id": city.id, "name": city.name} for city in cities]

    # Guardar en caché por 30 minutos (1800 segundos)
    cache.set(cache_key, data, 1800)

    # Agregar headers de rate limit
    response = JsonResponse(data, safe=False)
    response['X-RateLimit-Remaining'] = str(remaining)
    response['X-RateLimit-Limit'] = '150'
    return response


def countries_api(request):
    """
    API para obtener países - Público

    Parámetros:
    - q: término de búsqueda (opcional, máximo 100 caracteres)
    - id: ID específico de país (opcional)

    Rate Limiting: 150 requests por hora por IP
    Caché: 30 minutos
    """
    import unicodedata

    # Rate limiting: 150 requests por hora por IP
    is_allowed, remaining = _check_rate_limit(
        request,
        "locations_countries_api",
        max_requests=150,
        window_seconds=3600
    )

    if not is_allowed:
        return JsonResponse(
            {"error": "Rate limit exceeded. Please try again later."},
            status=429
        )

    # Validar y limitar tamaño de parámetros
    search_query = request.GET.get("q", "").strip()
    if len(search_query) > 100:
        search_query = search_query[:100]

    country_id = request.GET.get("id")
    if country_id:
        try:
            country_id = int(country_id)
        except (ValueError, TypeError):
            return JsonResponse({"error": "Invalid country ID"}, status=400)

    # Crear clave de caché basada en parámetros
    cache_key = f"locations_countries_api_{country_id or ''}_{search_query}"

    # Intentar obtener del caché
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        response = JsonResponse(cached_data, safe=False)
        response['X-RateLimit-Remaining'] = str(remaining)
        response['X-RateLimit-Limit'] = '150'
        return response

    # Si se solicita un ID específico
    if country_id:
        try:
            country = Country.objects.get(id=country_id, is_active=True)
            data = [{"id": country.id, "name": country.name, "code": country.code}]
            # Guardar en caché
            cache.set(cache_key, data, 1800)  # 30 minutos
            response = JsonResponse(data, safe=False)
            response['X-RateLimit-Remaining'] = str(remaining)
            response['X-RateLimit-Limit'] = '150'
            return response
        except Country.DoesNotExist:
            data = []
            cache.set(cache_key, data, 1800)
            response = JsonResponse(data, safe=False)
            response['X-RateLimit-Remaining'] = str(remaining)
            response['X-RateLimit-Limit'] = '150'
            return response

    # Búsqueda por término
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

    # Guardar en caché por 30 minutos
    cache.set(cache_key, data, 1800)

    # Agregar headers de rate limit
    response = JsonResponse(data, safe=False)
    response['X-RateLimit-Remaining'] = str(remaining)
    response['X-RateLimit-Limit'] = '150'
    return response


def states_api(request):
    """
    API para obtener estados - Público

    Parámetros:
    - country: ID del país para filtrar (opcional)
    - q: término de búsqueda (opcional, máximo 100 caracteres)
    - id: ID específico de estado (opcional)

    Rate Limiting: 150 requests por hora por IP
    Caché: 30 minutos
    """
    import unicodedata

    # Rate limiting: 150 requests por hora por IP
    is_allowed, remaining = _check_rate_limit(
        request,
        "locations_states_api",
        max_requests=150,
        window_seconds=3600
    )

    if not is_allowed:
        return JsonResponse(
            {"error": "Rate limit exceeded. Please try again later."},
            status=429
        )

    # Validar y limitar tamaño de parámetros
    search_query = request.GET.get("q", "").strip()
    if len(search_query) > 100:
        search_query = search_query[:100]

    country_id = request.GET.get("country")
    if country_id:
        try:
            country_id = int(country_id)
        except (ValueError, TypeError):
            return JsonResponse({"error": "Invalid country ID"}, status=400)

    state_id = request.GET.get("id")
    if state_id:
        try:
            state_id = int(state_id)
        except (ValueError, TypeError):
            return JsonResponse({"error": "Invalid state ID"}, status=400)

    # Crear clave de caché basada en parámetros
    cache_key = f"locations_states_api_{country_id or ''}_{state_id or ''}_{search_query}"

    # Intentar obtener del caché
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        response = JsonResponse(cached_data, safe=False)
        response['X-RateLimit-Remaining'] = str(remaining)
        response['X-RateLimit-Limit'] = '150'
        return response

    # Si se solicita un ID específico
    if state_id:
        try:
            state = State.objects.get(id=state_id, is_active=True)
            data = [{"id": state.id, "name": state.name, "country_id": state.country.id}]
            cache.set(cache_key, data, 1800)
            response = JsonResponse(data, safe=False)
            response['X-RateLimit-Remaining'] = str(remaining)
            response['X-RateLimit-Limit'] = '150'
            return response
        except State.DoesNotExist:
            data = []
            cache.set(cache_key, data, 1800)
            response = JsonResponse(data, safe=False)
            response['X-RateLimit-Remaining'] = str(remaining)
            response['X-RateLimit-Limit'] = '150'
            return response

    # Filtrar por país si se proporciona
    if country_id:
        states = State.objects.filter(country_id=country_id, is_active=True).order_by(
            "name"
        )
    else:
        states = State.objects.filter(is_active=True).order_by("country__name", "name")

    # Filtrar por término de búsqueda si se proporciona
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

    # Guardar en caché por 30 minutos
    cache.set(cache_key, data, 1800)

    # Agregar headers de rate limit
    response = JsonResponse(data, safe=False)
    response['X-RateLimit-Remaining'] = str(remaining)
    response['X-RateLimit-Limit'] = '150'
    return response


def cities_api(request):
    """
    API para obtener ciudades - Público

    Parámetros:
    - state: ID del estado para filtrar (opcional)
    - q: término de búsqueda (opcional, máximo 100 caracteres)
    - id: ID específico de ciudad (opcional)

    Rate Limiting: 150 requests por hora por IP
    Caché: 30 minutos
    """
    import unicodedata

    # Rate limiting: 150 requests por hora por IP
    is_allowed, remaining = _check_rate_limit(
        request,
        "locations_cities_api",
        max_requests=150,
        window_seconds=3600
    )

    if not is_allowed:
        return JsonResponse(
            {"error": "Rate limit exceeded. Please try again later."},
            status=429
        )

    # Validar y limitar tamaño de parámetros
    search_query = request.GET.get("q", "").strip()
    if len(search_query) > 100:
        search_query = search_query[:100]

    state_id = request.GET.get("state")
    if state_id:
        try:
            state_id = int(state_id)
        except (ValueError, TypeError):
            return JsonResponse({"error": "Invalid state ID"}, status=400)

    city_id = request.GET.get("id")
    if city_id:
        try:
            city_id = int(city_id)
        except (ValueError, TypeError):
            return JsonResponse({"error": "Invalid city ID"}, status=400)

    # Crear clave de caché basada en parámetros
    cache_key = f"locations_cities_api_{state_id or ''}_{city_id or ''}_{search_query}"

    # Intentar obtener del caché
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        response = JsonResponse(cached_data, safe=False)
        response['X-RateLimit-Remaining'] = str(remaining)
        response['X-RateLimit-Limit'] = '150'
        return response

    # Si se solicita un ID específico
    if city_id:
        try:
            city = City.objects.get(id=city_id, is_active=True)
            data = [{"id": city.id, "name": city.name, "state_id": city.state.id}]
            cache.set(cache_key, data, 1800)
            response = JsonResponse(data, safe=False)
            response['X-RateLimit-Remaining'] = str(remaining)
            response['X-RateLimit-Limit'] = '150'
            return response
        except City.DoesNotExist:
            data = []
            cache.set(cache_key, data, 1800)
            response = JsonResponse(data, safe=False)
            response['X-RateLimit-Remaining'] = str(remaining)
            response['X-RateLimit-Limit'] = '150'
            return response

    # Filtrar por estado si se proporciona
    if state_id:
        cities = City.objects.filter(state_id=state_id, is_active=True).order_by("name")
    else:
        cities = City.objects.filter(is_active=True).order_by(
            "state__country__name", "state__name", "name"
        )

    # Filtrar por término de búsqueda si se proporciona
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

    # Guardar en caché por 30 minutos
    cache.set(cache_key, data, 1800)

    # Agregar headers de rate limit
    response = JsonResponse(data, safe=False)
    response['X-RateLimit-Remaining'] = str(remaining)
    response['X-RateLimit-Limit'] = '150'
    return response


def seasons_api(request):
    """
    API para obtener temporadas - Público

    Rate Limiting: 150 requests por hora por IP
    Caché: 30 minutos
    """
    # Rate limiting: 150 requests por hora por IP
    is_allowed, remaining = _check_rate_limit(
        request,
        "locations_seasons_api",
        max_requests=150,
        window_seconds=3600
    )

    if not is_allowed:
        return JsonResponse(
            {"error": "Rate limit exceeded. Please try again later."},
            status=429
        )

    # Clave de caché
    cache_key = "locations_seasons_api_all"

    # Intentar obtener del caché
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        response = JsonResponse(cached_data, safe=False)
        response['X-RateLimit-Remaining'] = str(remaining)
        response['X-RateLimit-Limit'] = '150'
        return response

    # Obtener datos
    seasons = Season.objects.filter(is_active=True).order_by("name")
    data = [
        {"id": season.id, "name": season.name, "year": season.year}
        for season in seasons
    ]

    # Guardar en caché por 30 minutos
    cache.set(cache_key, data, 1800)

    # Agregar headers de rate limit
    response = JsonResponse(data, safe=False)
    response['X-RateLimit-Remaining'] = str(remaining)
    response['X-RateLimit-Limit'] = '150'
    return response


def rules_api(request):
    """
    API para obtener reglas - Público

    Rate Limiting: 150 requests por hora por IP
    Caché: 30 minutos
    """
    # Rate limiting: 150 requests por hora por IP
    is_allowed, remaining = _check_rate_limit(
        request,
        "locations_rules_api",
        max_requests=150,
        window_seconds=3600
    )

    if not is_allowed:
        return JsonResponse(
            {"error": "Rate limit exceeded. Please try again later."},
            status=429
        )

    # Clave de caché
    cache_key = "locations_rules_api_all"

    # Intentar obtener del caché
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        response = JsonResponse(cached_data, safe=False)
        response['X-RateLimit-Remaining'] = str(remaining)
        response['X-RateLimit-Limit'] = '150'
        return response

    # Obtener datos
    rules = Rule.objects.filter(is_active=True).order_by("name")
    data = [
        {"id": rule.id, "name": rule.name, "rule_type": rule.rule_type}
        for rule in rules
    ]

    # Guardar en caché por 30 minutos
    cache.set(cache_key, data, 1800)

    # Agregar headers de rate limit
    response = JsonResponse(data, safe=False)
    response['X-RateLimit-Remaining'] = str(remaining)
    response['X-RateLimit-Limit'] = '150'
    return response


def sites_api(request):
    """
    API para obtener sitios - Público

    Parámetros:
    - city: ID de la ciudad para filtrar (opcional)

    Rate Limiting: 150 requests por hora por IP
    Caché: 30 minutos
    """
    # Rate limiting: 150 requests por hora por IP
    is_allowed, remaining = _check_rate_limit(
        request,
        "locations_sites_api",
        max_requests=150,
        window_seconds=3600
    )

    if not is_allowed:
        return JsonResponse(
            {"error": "Rate limit exceeded. Please try again later."},
            status=429
        )

    # Validar city_id
    city_id = request.GET.get("city")
    if city_id:
        try:
            city_id = int(city_id)
        except (ValueError, TypeError):
            return JsonResponse({"error": "Invalid city ID"}, status=400)

    # Crear clave de caché basada en parámetros
    cache_key = f"locations_sites_api_{city_id or 'all'}"

    # Intentar obtener del caché
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        response = JsonResponse(cached_data, safe=False)
        response['X-RateLimit-Remaining'] = str(remaining)
        response['X-RateLimit-Limit'] = '150'
        return response

    sites_query = Site.objects.filter(is_active=True)

    # Filtrar por ciudad si se proporciona
    if city_id:
        # Filtrar estrictamente por ciudad
        sites_query = sites_query.filter(city_id=city_id)

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

    # Guardar en caché por 30 minutos
    cache.set(cache_key, sites_list, 1800)

    # Agregar headers de rate limit
    response = JsonResponse(sites_list, safe=False)
    response['X-RateLimit-Remaining'] = str(remaining)
    response['X-RateLimit-Limit'] = '150'
    return response
