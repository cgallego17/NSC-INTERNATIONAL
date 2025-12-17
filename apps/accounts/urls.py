"""
URLs de accounts - Combinación de públicas y privadas
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import (
    views_public,
    views_private,
    views_banners,
    views_sponsors,
    views_dashboard_banners,
)

app_name = "accounts"

urlpatterns = [
    # ===== URLs PÚBLICAS =====
    # Login y registro público
    path("login/", views_public.PublicLoginView.as_view(), name="login"),
    path("register/", views_public.PublicRegistrationView.as_view(), name="register"),
    # Perfil público de jugador
    path(
        "player/<int:pk>/",
        views_public.PublicPlayerProfileView.as_view(),
        name="public_player_profile",
    ),
    # Lista pública de jugadores
    path(
        "players/",
        views_public.PublicPlayerListView.as_view(),
        name="public_player_list",
    ),
    # Perfil de jugador para front (requiere login)
    path(
        "players/<int:pk>/",
        views_public.FrontPlayerProfileView.as_view(),
        name="front_player_profile",
    ),
    # Editar jugador para front (requiere login)
    path(
        "players/<int:pk>/edit/",
        views_public.FrontPlayerUpdateView.as_view(),
        name="front_player_edit",
    ),
    # ===== URLs PRIVADAS =====
    # Logout (requiere login) - pero la URL debe estar disponible siempre
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    # Panel y perfil
    path("panel/", views_private.UserDashboardView.as_view(), name="panel"),
    path("profile/", views_private.profile_view, name="profile"),
    path(
        "profile/edit/", views_private.ProfileUpdateView.as_view(), name="profile_edit"
    ),
    path(
        "profile/user-edit/",
        views_private.UserInfoUpdateView.as_view(),
        name="user_edit",
    ),
    # Equipos
    path("teams/", views_private.TeamListView.as_view(), name="team_list"),
    path("teams/<int:pk>/", views_private.TeamDetailView.as_view(), name="team_detail"),
    path("teams/create/", views_private.TeamCreateView.as_view(), name="team_create"),
    path(
        "teams/<int:pk>/edit/", views_private.TeamUpdateView.as_view(), name="team_edit"
    ),
    # Jugadores
    path("players/", views_private.PlayerListView.as_view(), name="player_list"),
    path(
        "players/<int:pk>/",
        views_private.PlayerDetailView.as_view(),
        name="player_detail",
    ),
    path(
        "players/register/",
        views_private.PlayerRegistrationView.as_view(),
        name="player_register",
    ),
    path(
        "players/<int:pk>/edit/",
        views_private.PlayerUpdateView.as_view(),
        name="player_edit",
    ),
    # Registro de jugadores por padres
    path(
        "players/register-child/",
        views_private.ParentPlayerRegistrationView.as_view(),
        name="parent_player_register",
    ),
    # Usuarios (solo staff)
    path("users/", views_private.UserListView.as_view(), name="user_list"),
    # Instagram API
    path(
        "api/instagram/posts/",
        views_public.instagram_posts_api,
        name="instagram_posts_api",
    ),
    path(
        "api/instagram/image-proxy/",
        views_public.instagram_image_proxy,
        name="instagram_image_proxy",
    ),
    # Banners del Home
    path("banners/", views_banners.HomeBannerListView.as_view(), name="banner_list"),
    path(
        "banners/create/",
        views_banners.HomeBannerCreateView.as_view(),
        name="banner_create",
    ),
    path(
        "banners/<int:pk>/",
        views_banners.HomeBannerDetailView.as_view(),
        name="banner_detail",
    ),
    path(
        "banners/<int:pk>/edit/",
        views_banners.HomeBannerUpdateView.as_view(),
        name="banner_update",
    ),
    path(
        "banners/<int:pk>/delete/",
        views_banners.HomeBannerDeleteView.as_view(),
        name="banner_delete",
    ),
    # Configuraciones del Sitio
    path(
        "site-settings/",
        views_banners.SiteSettingsUpdateView.as_view(),
        name="site_settings",
    ),
    # Administración de Contenido del Home
    path(
        "home-content/",
        views_banners.HomeContentAdminView.as_view(),
        name="home_content_admin",
    ),
    # Sponsors
    path("sponsors/", views_sponsors.SponsorListView.as_view(), name="sponsor_list"),
    path(
        "sponsors/create/",
        views_sponsors.SponsorCreateView.as_view(),
        name="sponsor_create",
    ),
    path(
        "sponsors/<int:pk>/",
        views_sponsors.SponsorDetailView.as_view(),
        name="sponsor_detail",
    ),
    path(
        "sponsors/<int:pk>/edit/",
        views_sponsors.SponsorUpdateView.as_view(),
        name="sponsor_update",
    ),
    path(
        "sponsors/<int:pk>/delete/",
        views_sponsors.SponsorDeleteView.as_view(),
        name="sponsor_delete",
    ),
    # Banners del Dashboard
    path(
        "dashboard-banners/",
        views_dashboard_banners.DashboardBannerListView.as_view(),
        name="dashboard_banner_list",
    ),
    path(
        "dashboard-banners/create/",
        views_dashboard_banners.DashboardBannerCreateView.as_view(),
        name="dashboard_banner_create",
    ),
    path(
        "dashboard-banners/<int:pk>/",
        views_dashboard_banners.DashboardBannerDetailView.as_view(),
        name="dashboard_banner_detail",
    ),
    path(
        "dashboard-banners/<int:pk>/edit/",
        views_dashboard_banners.DashboardBannerUpdateView.as_view(),
        name="dashboard_banner_update",
    ),
    path(
        "dashboard-banners/<int:pk>/delete/",
        views_dashboard_banners.DashboardBannerDeleteView.as_view(),
        name="dashboard_banner_delete",
    ),
]
