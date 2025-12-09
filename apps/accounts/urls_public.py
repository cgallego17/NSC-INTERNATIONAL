"""
URLs públicas - No requieren autenticación
"""
from django.urls import path
from . import views_public

# No usar app_name aquí para evitar conflictos de namespace
# Las URLs se incluyen directamente bajo 'accounts/'

urlpatterns = [
    # Login y registro público
    path('login/', views_public.PublicLoginView.as_view(), name='login'),
    path('register/', views_public.PublicRegistrationView.as_view(), name='register'),
]

