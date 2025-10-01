from django.urls import path

from . import views

app_name = "events"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("list/", views.EventListView.as_view(), name="list"),
    path("create/", views.EventCreateView.as_view(), name="create"),
    path("<int:pk>/", views.EventDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.EventUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.EventDeleteView.as_view(), name="delete"),
    path("calendar/", views.EventCalendarView.as_view(), name="calendar"),
    path("<int:event_id>/attend/", views.EventAttendanceView.as_view(), name="attend"),
    # Division URLs
    path("divisions/", views.DivisionListView.as_view(), name="division_list"),
    path("divisions/create/", views.DivisionCreateView.as_view(), name="division_create"),
    path("divisions/<int:pk>/", views.DivisionDetailView.as_view(), name="division_detail"),
    path("divisions/<int:pk>/edit/", views.DivisionUpdateView.as_view(), name="division_update"),
    path("divisions/<int:pk>/delete/", views.DivisionDeleteView.as_view(), name="division_delete"),
]
