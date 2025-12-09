from django.urls import include, path

from . import views

app_name = "locations"

urlpatterns = [
    # Country URLs
    path("countries/", views.CountryListView.as_view(), name="country_list"),
    path(
        "countries/<int:pk>/", views.CountryDetailView.as_view(), name="country_detail"
    ),
    path("countries/create/", views.CountryCreateView.as_view(), name="country_create"),
    path(
        "countries/<int:pk>/edit/",
        views.CountryUpdateView.as_view(),
        name="country_update",
    ),
    path(
        "countries/<int:pk>/delete/",
        views.CountryDeleteView.as_view(),
        name="country_delete",
    ),
    # State URLs
    path("states/", views.StateListView.as_view(), name="state_list"),
    path("states/<int:pk>/", views.StateDetailView.as_view(), name="state_detail"),
    path("states/create/", views.StateCreateView.as_view(), name="state_create"),
    path("states/<int:pk>/edit/", views.StateUpdateView.as_view(), name="state_update"),
    path(
        "states/<int:pk>/delete/", views.StateDeleteView.as_view(), name="state_delete"
    ),
    # City URLs
    path("cities/", views.CityListView.as_view(), name="city_list"),
    path("cities/<int:pk>/", views.CityDetailView.as_view(), name="city_detail"),
    path("cities/create/", views.CityCreateView.as_view(), name="city_create"),
    path("cities/<int:pk>/edit/", views.CityUpdateView.as_view(), name="city_update"),
    path("cities/<int:pk>/delete/", views.CityDeleteView.as_view(), name="city_delete"),
    # Season URLs
    path("seasons/", views.SeasonListView.as_view(), name="season_list"),
    path("seasons/<int:pk>/", views.SeasonDetailView.as_view(), name="season_detail"),
    path("seasons/create/", views.SeasonCreateView.as_view(), name="season_create"),
    path(
        "seasons/<int:pk>/edit/", views.SeasonUpdateView.as_view(), name="season_update"
    ),
    path(
        "seasons/<int:pk>/delete/",
        views.SeasonDeleteView.as_view(),
        name="season_delete",
    ),
    # Rule URLs
    path("rules/", views.RuleListView.as_view(), name="rule_list"),
    path("rules/<int:pk>/", views.RuleDetailView.as_view(), name="rule_detail"),
    path("rules/create/", views.RuleCreateView.as_view(), name="rule_create"),
    path("rules/<int:pk>/edit/", views.RuleUpdateView.as_view(), name="rule_update"),
    path("rules/<int:pk>/delete/", views.RuleDeleteView.as_view(), name="rule_delete"),
    # Site URLs
    path("sites/", views.SiteListView.as_view(), name="site_list"),
    path("sites/<int:pk>/", views.SiteDetailView.as_view(), name="site_detail"),
    path("sites/create/", views.SiteCreateView.as_view(), name="site_create"),
    path("sites/<int:pk>/edit/", views.SiteUpdateView.as_view(), name="site_update"),
    path("sites/<int:pk>/delete/", views.SiteDeleteView.as_view(), name="site_delete"),
    # AJAX URLs
    path(
        "ajax/states/<int:country_id>/",
        views.get_states_by_country,
        name="get_states_by_country",
    ),
    path(
        "ajax/cities/<int:state_id>/",
        views.get_cities_by_state,
        name="get_cities_by_state",
    ),
    # API URLs
    path("countries/api/", views.countries_api, name="countries_api"),
    path("states/api/", views.states_api, name="states_api"),
    path("cities/api/", views.cities_api, name="cities_api"),
    path("seasons/api/", views.seasons_api, name="seasons_api"),
    path("rules/api/", views.rules_api, name="rules_api"),
    path("sites/api/", views.sites_api, name="sites_api"),
    path("hotels/api/", views.hotels_api, name="hotels_api"),
    # Front URLs (hotels, reservations - require login) - Deben ir antes para evitar conflictos
    path("", include("apps.locations.urls_front")),
    # Admin URLs (hotels, rooms, services, reservations)
    path("", include("apps.locations.urls_admin")),
]
