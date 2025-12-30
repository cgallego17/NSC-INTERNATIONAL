"""
URLs privadas - Requieren autenticación
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from . import views_private

# app_name = 'accounts' - definido en nsc_admin/urls.py al incluir con namespace

urlpatterns = [
    # Logout (requiere login) - pero la URL debe estar disponible siempre
    path('logout/', auth_views.LogoutView.as_view(next_page='/accounts/login/'), name='logout'),

    # Panel y perfil
    path('dashboard/', views_private.UserDashboardView.as_view(), name='dashboard'),
    path('profile/', views_private.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views_private.ProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/billing/', views_private.ProfileView.as_view(), name='profile_billing'),
    path('profile/user-edit/', views_private.UserInfoUpdateView.as_view(), name='user_edit'),

    # Equipos
    path('teams/', views_private.TeamListView.as_view(), name='team_list'),
    path('teams/<int:pk>/', views_private.TeamDetailView.as_view(), name='team_detail'),
    path('teams/create/', views_private.TeamCreateView.as_view(), name='team_create'),
    path('teams/<int:pk>/edit/', views_private.TeamUpdateView.as_view(), name='team_edit'),

    # Jugadores
    path('players/', views_private.PlayerListView.as_view(), name='player_list'),
    path('players/<int:pk>/', views_private.PlayerDetailView.as_view(), name='player_detail'),
    path('players/register/', views_private.PlayerRegistrationView.as_view(), name='player_register'),
    path('players/<int:pk>/edit/', views_private.PlayerUpdateView.as_view(), name='player_edit'),

    # Eventos en el panel
    path('events/<int:pk>/', views_private.PanelEventDetailView.as_view(), name='panel_event_detail'),
    path('events/<int:pk>/register/', views_private.register_children_to_event, name='register_children_to_event'),

    # Stripe checkout (evento)
    path('events/<int:pk>/stripe/create-checkout-session/', views_private.create_stripe_event_checkout_session, name='create_stripe_event_checkout_session'),
    path('events/<int:pk>/stripe/success/', views_private.stripe_event_checkout_success, name='stripe_event_checkout_success'),
    path('events/<int:pk>/stripe/cancel/', views_private.stripe_event_checkout_cancel, name='stripe_event_checkout_cancel'),
    path('stripe/webhook/', views_private.stripe_webhook, name='stripe_webhook'),

    # Wallet
    path('wallet/add-funds/', views_private.wallet_add_funds, name='wallet_add_funds'),
]

