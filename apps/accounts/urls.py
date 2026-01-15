"""
URLs de accounts - Combinación de públicas y privadas
"""

from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from apps.core.views import custom_logout_view

from . import (
    views_admin,
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
    path(
        "confirm-email/sent/",
        views_public.EmailConfirmationSentView.as_view(),
        name="email_confirmation_sent",
    ),
    path(
        "confirm-email/<uidb64>/<token>/",
        views_public.confirm_email,
        name="confirm_email",
    ),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.html",
            html_email_template_name="registration/password_reset_email_html.html",
            subject_template_name="registration/password_reset_subject.txt",
            success_url=reverse_lazy("accounts:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            success_url=reverse_lazy("accounts:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
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
        custom_logout_view,
        name="logout",
    ),
    # Panel y perfil (movido a /panel/ en nsc_admin/urls.py)
    path(
        "user-dashboard/",
        views_private.UserDashboardView.as_view(),
        name="user_dashboard",
    ),
    path("profile/", views_private.ProfileView.as_view(), name="profile"),
    path(
        "profile/edit/", views_private.ProfileUpdateView.as_view(), name="profile_edit"
    ),
    path(
        "profile/user-edit/",
        views_private.UserInfoUpdateView.as_view(),
        name="user_edit",
    ),
    # Equipos (gestión privada - requiere login)
    path("teams/", views_private.TeamListView.as_view(), name="team_list"),
    path("teams/<int:pk>/", views_private.TeamDetailView.as_view(), name="team_detail"),
    path("teams/create/", views_private.TeamCreateView.as_view(), name="team_create"),
    path(
        "teams/<int:pk>/edit/", views_private.TeamUpdateView.as_view(), name="team_edit"
    ),
    # Jugadores (gestión privada - requiere login)
    path("players/manage/", views_private.PlayerListView.as_view(), name="player_list"),
    path(
        "players/<int:pk>/admin-detail/",
        views_private.AdminPlayerDetailView.as_view(),
        name="admin_player_detail",
    ),
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
        "players/<int:pk>/delete/",
        views_private.PlayerDeleteView.as_view(),
        name="player_delete",
    ),
    path(
        "players/<int:pk>/approve-verification/",
        views_private.approve_age_verification,
        name="approve_age_verification",
    ),
    path(
        "players/<int:player_id>/age-verification-document/",
        views_private.serve_age_verification_document,
        name="serve_age_verification_document",
    ),
    # Verificaciones de edad (solo staff y managers)
    path(
        "age-verifications/",
        views_private.AgeVerificationListView.as_view(),
        name="age_verification_list",
    ),
    # Eventos en el panel
    path(
        "events/<int:pk>/",
        views_private.PanelEventDetailView.as_view(),
        name="panel_event_detail",
    ),
    path(
        "events/<int:pk>/register/",
        views_private.register_children_to_event,
        name="register_children_to_event",
    ),
    # ===== EMBEDS (IFRAME) PARA TABS DEL PANEL =====
    path(
        "panel-tabs/eventos/",
        views_private.PanelEventosEmbedView.as_view(),
        name="panel_eventos_embed",
    ),
    path(
        "panel-tabs/events/<int:pk>/",
        views_private.PanelEventDetailEmbedView.as_view(),
        name="panel_event_detail_embed",
    ),
    # Stripe checkout (evento)
    path(
        "events/<int:pk>/stripe/create-checkout-session/",
        views_private.create_stripe_event_checkout_session,
        name="create_stripe_event_checkout_session",
    ),
    path(
        "events/<int:pk>/stripe/success/",
        views_private.stripe_event_checkout_success,
        name="stripe_event_checkout_success",
    ),
    path(
        "events/<int:pk>/stripe/cancel/",
        views_private.stripe_event_checkout_cancel,
        name="stripe_event_checkout_cancel",
    ),
    path("stripe/webhook/", views_private.stripe_webhook, name="stripe_webhook"),
    path(
        "stripe/invoice/<int:pk>/",
        views_private.StripeInvoiceView.as_view(),
        name="stripe_invoice",
    ),
    path(
        "payment/confirmation/<int:pk>/",
        views_private.PaymentConfirmationView.as_view(),
        name="payment_confirmation",
    ),
    # Register Now, Pay Later
    path(
        "registration/confirmation/<int:pk>/",
        views_private.registration_confirmation,
        name="registration_confirmation",
    ),
    path(
        "pending-payments/",
        views_private.pending_payments,
        name="pending_payments",
    ),
    path(
        "start-payment/<int:checkout_id>/",
        views_private.start_pending_payment,
        name="start_pending_payment",
    ),
    path(
        "resume-checkout/<int:checkout_id>/",
        views_private.resume_checkout_data,
        name="resume_checkout_data",
    ),
    path(
        "complete-hotel-payment/<int:order_id>/",
        views_private.complete_hotel_payment,
        name="complete_hotel_payment",
    ),
    path(
        "hotel-payment-success/<int:order_id>/",
        views_private.hotel_payment_success,
        name="hotel_payment_success",
    ),
    path(
        "registrations/",
        views_private.registration_list,
        name="registration_list",
    ),
    path(
        "registrations-panel/",
        views_private.registration_list_panel,
        name="registration_list_panel",
    ),
    # Wallet
    path(
        "wallet/add-funds/",
        views_private.wallet_add_funds,
        name="wallet_add_funds",
    ),
    path(
        "wallet/transactions/",
        views_private.wallet_transactions,
        name="wallet_transactions",
    ),
    path(
        "panel-tabs/wallet-transactions/",
        views_private.WalletTransactionsEmbedView.as_view(),
        name="wallet_transactions_embed",
    ),
    # Stripe Billing Portal
    path(
        "stripe/billing-portal/",
        views_private.StripeBillingPortalView.as_view(),
        name="stripe_billing_portal",
    ),
    path(
        "stripe/billing-setup/success/",
        views_private.stripe_billing_setup_success,
        name="stripe_billing_setup_success",
    ),
    # Registro de jugadores por padres
    path(
        "players/register-child/",
        views_private.ParentPlayerRegistrationView.as_view(),
        name="parent_player_register",
    ),
    # Usuarios (solo staff)
    path("users/", views_private.UserListView.as_view(), name="user_list"),
    path(
        "users/<int:pk>/detail/",
        views_private.AdminUserDetailView.as_view(),
        name="admin_user_detail",
    ),
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
    # Órdenes (Admin)
    path(
        "admin/orders/",
        views_admin.AdminOrderListView.as_view(),
        name="admin_order_list",
    ),
    path(
        "admin/orders/<int:pk>/",
        views_admin.AdminOrderDetailView.as_view(),
        name="admin_order_detail",
    ),
    path(
        "admin/wallet-topups/",
        views_admin.AdminWalletTopUpListView.as_view(),
        name="admin_wallet_topups",
    ),
    path(
        "admin/wallet-topups/search-users/",
        views_admin.search_users_ajax,
        name="admin_wallet_topups_search_users",
    ),
    path(
        "admin/wallet/checkouts/<int:pk>/release-reservation/",
        views_admin.admin_release_wallet_reservation_for_checkout,
        name="admin_release_wallet_reservation_for_checkout",
    ),
    # Equipos (Admin)
    path(
        "admin/teams/",
        views_admin.AdminTeamListView.as_view(),
        name="admin_team_list",
    ),
    path(
        "admin/teams/create/",
        views_admin.AdminTeamCreateView.as_view(),
        name="admin_team_create",
    ),
    path(
        "admin/teams/<int:pk>/edit/",
        views_admin.AdminTeamUpdateView.as_view(),
        name="admin_team_edit",
    ),
    path(
        "admin/teams/<int:pk>/delete/",
        views_admin.AdminTeamDeleteView.as_view(),
        name="admin_team_delete",
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
    # ===== NOTIFICATIONS API =====
    path(
        "api/notifications/",
        views_private.get_notifications_api,
        name="notifications_api",
    ),
    path(
        "api/notifications/count/",
        views_private.get_notification_count_api,
        name="notifications_count_api",
    ),
    path(
        "api/notifications/<int:notification_id>/mark-read/",
        views_private.mark_notification_read_api,
        name="mark_notification_read_api",
    ),
    path(
        "api/notifications/mark-all-read/",
        views_private.mark_all_notifications_read_api,
        name="mark_all_notifications_read_api",
    ),
    # ===== WEB PUSH (STAFF) =====
    path(
        "api/push/public-key/",
        views_private.push_public_key_api,
        name="push_public_key_api",
    ),
    path(
        "api/push/subscribe/",
        views_private.push_subscribe_api,
        name="push_subscribe_api",
    ),
    path(
        "api/push/unsubscribe/",
        views_private.push_unsubscribe_api,
        name="push_unsubscribe_api",
    ),
]
