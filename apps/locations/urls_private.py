"""
URLs privadas de ubicaciones - Solo lectura, requieren autenticación
"""
from django.urls import path
from . import views_private

app_name = "locations"

urlpatterns = [
    # Country URLs (solo lectura)
    path("countries/", views_private.CountryListView.as_view(), name="country_list"),
    path(
        "countries/<int:pk>/",
        views_private.CountryDetailView.as_view(),
        name="country_detail",
    ),
    # State URLs (solo lectura)
    path("states/", views_private.StateListView.as_view(), name="state_list"),
    path("states/<int:pk>/", views_private.StateDetailView.as_view(), name="state_detail"),
    # City URLs (solo lectura)
    path("cities/", views_private.CityListView.as_view(), name="city_list"),
    path("cities/<int:pk>/", views_private.CityDetailView.as_view(), name="city_detail"),
    # Season URLs (solo lectura)
    path("seasons/", views_private.SeasonListView.as_view(), name="season_list"),
    path("seasons/<int:pk>/", views_private.SeasonDetailView.as_view(), name="season_detail"),
    # Rule URLs (solo lectura)
    path("rules/", views_private.RuleListView.as_view(), name="rule_list"),
    path("rules/<int:pk>/", views_private.RuleDetailView.as_view(), name="rule_detail"),
    # Site URLs (solo lectura)
    path("sites/", views_private.SiteListView.as_view(), name="site_list"),
    path("sites/<int:pk>/", views_private.SiteDetailView.as_view(), name="site_detail"),
]

