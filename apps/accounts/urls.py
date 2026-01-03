"""
URLs de accounts - Combinación de públicas y privadas
"""

from django.contrib.auth import views as auth_views
from django.urls import path

from . import (
    views,
    views_banners,
    views_dashboard_banners,
    views_hotels,
    views_private,
    views_public,
    views_sponsors,
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
    # ===== URLs PRIVADAS =====
    # Logout (requiere login) - pero la URL debe estar disponible siempre
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="/accounts/login/"),
        name="logout",
    ),
    # Panel y perfil
    path("panel/", views_private.UserDashboardView.as_view(), name="panel"),
    path("user-dashboard/", views.UserDashboardView.as_view(), name="user_dashboard"),
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
    path(
        "players/<int:pk>/approve-verification/",
        views_private.approve_age_verification,
        name="approve_age_verification",
    ),
    # Eventos en el panel - BLOQUEADO TEMPORALMENTE
    path(
        "events/",
        views_private.events_blocked_view,
        name="events_blocked",
    ),
    path(
        "events/<int:pk>/",
        views_private.events_blocked_view,
        name="panel_event_detail",
    ),
    path(
        "events/<int:pk>/register/",
        views_private.events_blocked_view,
        name="register_children_to_event",
    ),
    # Stripe checkout (evento) - BLOQUEADO TEMPORALMENTE
    path(
        "events/<int:pk>/stripe/create-checkout-session/",
        views_private.events_blocked_view,
        name="create_stripe_event_checkout_session",
    ),
    path(
        "events/<int:pk>/stripe/success/",
        views_private.events_blocked_view,
        name="stripe_event_checkout_success",
    ),
    path(
        "events/<int:pk>/stripe/cancel/",
        views_private.events_blocked_view,
        name="stripe_event_checkout_cancel",
    ),
    path("stripe/webhook/", views_private.stripe_webhook, name="stripe_webhook"),
    # Wallet
    path(
        "wallet/add-funds/",
        views_private.wallet_add_funds,
        name="wallet_add_funds",
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
    # Redirección desde URL antigua (mantener por compatibilidad)
    path(
        "edit-site-settings/",
        views_banners.SiteSettingsRedirectView.as_view(),
        name="edit_site_settings_redirect",
    ),
    path(
        "edit-schedule-settings/",
        views_banners.ScheduleSettingsUpdateView.as_view(),
        name="edit_schedule_settings",
    ),
    path(
        "edit-showcase-settings/",
        views_banners.ShowcaseSettingsUpdateView.as_view(),
        name="edit_showcase_settings",
    ),
    path(
        "edit-contact-settings/",
        views_banners.ContactSettingsUpdateView.as_view(),
        name="edit_contact_settings",
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
    # ===== GESTIÓN DE HOTELES =====
    # Hoteles
    path("hotels/", views_hotels.HotelListView.as_view(), name="hotel_list"),
    path("hotels/create/", views_hotels.HotelCreateView.as_view(), name="hotel_create"),
    path(
        "hotels/<int:pk>/", views_hotels.HotelDetailView.as_view(), name="hotel_detail"
    ),
    path(
        "hotels/<int:pk>/edit/",
        views_hotels.HotelUpdateView.as_view(),
        name="hotel_update",
    ),
    path(
        "hotels/<int:pk>/delete/",
        views_hotels.HotelDeleteView.as_view(),
        name="hotel_delete",
    ),
    # Imágenes del Hotel
    path(
        "hotels/<int:hotel_pk>/images/",
        views_hotels.HotelImageListView.as_view(),
        name="hotel_image_list",
    ),
    path(
        "hotels/<int:hotel_pk>/images/create/",
        views_hotels.HotelImageCreateView.as_view(),
        name="hotel_image_create",
    ),
    path(
        "hotels/<int:hotel_pk>/images/<int:pk>/edit/",
        views_hotels.HotelImageUpdateView.as_view(),
        name="hotel_image_update",
    ),
    path(
        "hotels/<int:hotel_pk>/images/<int:pk>/delete/",
        views_hotels.HotelImageDeleteView.as_view(),
        name="hotel_image_delete",
    ),
    # Amenidades del Hotel
    path(
        "hotels/<int:hotel_pk>/amenities/",
        views_hotels.HotelAmenityListView.as_view(),
        name="hotel_amenity_list",
    ),
    path(
        "hotels/<int:hotel_pk>/amenities/create/",
        views_hotels.HotelAmenityCreateView.as_view(),
        name="hotel_amenity_create",
    ),
    path(
        "hotels/<int:hotel_pk>/amenities/<int:pk>/edit/",
        views_hotels.HotelAmenityUpdateView.as_view(),
        name="hotel_amenity_update",
    ),
    path(
        "hotels/<int:hotel_pk>/amenities/<int:pk>/delete/",
        views_hotels.HotelAmenityDeleteView.as_view(),
        name="hotel_amenity_delete",
    ),
    # Habitaciones del Hotel
    path(
        "hotels/<int:hotel_pk>/rooms/",
        views_hotels.HotelRoomListView.as_view(),
        name="hotel_room_list",
    ),
    path(
        "hotels/<int:hotel_pk>/rooms/create/",
        views_hotels.HotelRoomCreateView.as_view(),
        name="hotel_room_create",
    ),
    path(
        "hotels/<int:hotel_pk>/rooms/<int:pk>/edit/",
        views_hotels.HotelRoomUpdateView.as_view(),
        name="hotel_room_update",
    ),
    path(
        "hotels/<int:hotel_pk>/rooms/<int:pk>/delete/",
        views_hotels.HotelRoomDeleteView.as_view(),
        name="hotel_room_delete",
    ),
    # Servicios del Hotel
    path(
        "hotels/<int:hotel_pk>/services/",
        views_hotels.HotelServiceListView.as_view(),
        name="hotel_service_list",
    ),
    path(
        "hotels/<int:hotel_pk>/services/create/",
        views_hotels.HotelServiceCreateView.as_view(),
        name="hotel_service_create",
    ),
    path(
        "hotels/<int:hotel_pk>/services/<int:pk>/edit/",
        views_hotels.HotelServiceUpdateView.as_view(),
        name="hotel_service_update",
    ),
    path(
        "hotels/<int:hotel_pk>/services/<int:pk>/delete/",
        views_hotels.HotelServiceDeleteView.as_view(),
        name="hotel_service_delete",
    ),
]
