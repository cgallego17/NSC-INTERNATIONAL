"""
URLs privadas de eventos - Requieren autenticación
"""

from django.urls import path
from . import views_private

app_name = "events"

urlpatterns = [
    path("", views_private.DashboardView.as_view(), name="dashboard"),
    path("list/", views_private.PrivateEventListView.as_view(), name="private_list"),
    path(
        "list/", views_private.PrivateEventListView.as_view(), name="list"
    ),  # Alias para compatibilidad
    path("create/", views_private.EventCreateView.as_view(), name="create"),
    path(
        "<int:pk>/",
        views_private.PrivateEventDetailView.as_view(),
        name="private_detail",
    ),
    path(
        "<int:pk>/", views_private.PrivateEventDetailView.as_view(), name="detail"
    ),  # Alias para compatibilidad
    path("<int:pk>/edit/", views_private.EventUpdateView.as_view(), name="update"),
    path("calendar/", views_private.EventCalendarView.as_view(), name="calendar"),
    path(
        "<int:event_id>/attend/",
        views_private.EventAttendanceView.as_view(),
        name="attend",
    ),
]
