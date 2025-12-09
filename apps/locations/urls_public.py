"""
URLs públicas de ubicaciones - APIs sin autenticación
"""
from django.urls import path
from . import views_public

# No usar app_name para evitar conflictos - se incluye directamente

urlpatterns = [
    # AJAX URLs (públicas)
    path(
        "ajax/states/<int:country_id>/",
        views_public.get_states_by_country,
        name="get_states_by_country",
    ),
    path(
        "ajax/cities/<int:state_id>/",
        views_public.get_cities_by_state,
        name="get_cities_by_state",
    ),
    # API URLs (públicas)
    path("api/countries/", views_public.countries_api, name="countries_api"),
    path("api/states/", views_public.states_api, name="states_api"),
    path("api/cities/", views_public.cities_api, name="cities_api"),
    path("api/seasons/", views_public.seasons_api, name="seasons_api"),
    path("api/rules/", views_public.rules_api, name="rules_api"),
    path("api/sites/", views_public.sites_api, name="sites_api"),
]

