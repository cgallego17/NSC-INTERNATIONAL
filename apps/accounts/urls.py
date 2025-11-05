from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'accounts'

urlpatterns = [
    # Login y Logout público
    path('login/', views.PublicLoginView.as_view(), name='login'),
    path('logout/', login_required(auth_views.LogoutView.as_view(next_page='/accounts/login/')), name='logout'),
    # Registro público
    path('register/', views.PublicRegistrationView.as_view(), name='register'),
    
    # Panel y perfil
    path('dashboard/', views.UserDashboardView.as_view(), name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/user-edit/', views.UserInfoUpdateView.as_view(), name='user_edit'),
    
    # Equipos
    path('teams/', views.TeamListView.as_view(), name='team_list'),
    path('teams/<int:pk>/', views.TeamDetailView.as_view(), name='team_detail'),
    path('teams/create/', views.TeamCreateView.as_view(), name='team_create'),
    path('teams/<int:pk>/edit/', views.TeamUpdateView.as_view(), name='team_edit'),
    
    # Jugadores
    path('players/', views.PlayerListView.as_view(), name='player_list'),
    path('players/<int:pk>/', views.PlayerDetailView.as_view(), name='player_detail'),
    path('players/register/', views.PlayerRegistrationView.as_view(), name='player_register'),
    path('players/<int:pk>/edit/', views.PlayerUpdateView.as_view(), name='player_edit'),
]

