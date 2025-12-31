"""
URL configuration for nsc_admin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog

from apps.accounts.views_public import PublicHomeView
from apps.core.views import set_language
from apps.events.views import DashboardView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("admin/login/", admin.site.login, name="admin_login"),  # Login admin separado
    path("", PublicHomeView.as_view(), name="home"),  # Home público
    path(
        "dashboard/", DashboardView.as_view(), name="dashboard"
    ),  # Dashboard principal
    path("events/", include("apps.events.urls")),
    path("locations/", include("apps.locations.urls")),
    path("accounts/", include("apps.accounts.urls")),  # Login público aquí
    path("users/", include("django.contrib.auth.urls")),  # Mantener para compatibilidad
    path("media/", include("apps.media.urls")),  # Multimedia
    path("i18n/setlang/", set_language, name="set_language"),  # Language switching
    # JavaScript i18n catalog (uses djangojs.po)
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Serve multimedia files
    multimedia_root = getattr(settings, "MULTIMEDIA_ROOT", None)
    if multimedia_root:
        urlpatterns += static(settings.MULTIMEDIA_URL, document_root=multimedia_root)
