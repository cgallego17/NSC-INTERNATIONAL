"""
URLs de accounts - Combinación de públicas y privadas
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views_public, views_private

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
    path("dashboard/", views_private.UserDashboardView.as_view(), name="dashboard"),
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
]
