from django.urls import path

from . import views, views_data_management, views_public

app_name = "events"

urlpatterns = [
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("list/", views.EventListView.as_view(), name="list"),
    # URLs públicas (no requieren autenticación)
    path("", views_public.PublicEventListView.as_view(), name="public_list"),
    path(
        "<int:pk>/",
        views_public.PublicEventDetailView.as_view(),
        name="public_detail",
    ),
    path("create/", views.EventCreateView.as_view(), name="create"),
    path("admin/<int:pk>/", views.EventDetailView.as_view(), name="admin_detail"),
    path("admin/<int:pk>/send-email/", views.SendEventEmailView.as_view(), name="send_email"),
    path("admin/<int:pk>/recipients/", views.GetEventRecipientsView.as_view(), name="get_recipients"),
    path("<int:pk>/edit/", views.EventUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.EventDeleteView.as_view(), name="delete"),
    path(
        "<int:pk>/change-status/",
        views.EventChangeStatusView.as_view(),
        name="change_status",
    ),
    path(
        "<int:pk>/toggle-publish/",
        views.EventTogglePublishView.as_view(),
        name="toggle_publish",
    ),
    path("calendar/", views.EventCalendarView.as_view(), name="calendar"),
    path("<int:event_id>/attend/", views.EventAttendanceView.as_view(), name="attend"),
    # Division URLs
    path("divisions/", views.DivisionListView.as_view(), name="division_list"),
    path(
        "divisions/create/", views.DivisionCreateView.as_view(), name="division_create"
    ),
    path(
        "divisions/<int:pk>/",
        views.DivisionDetailView.as_view(),
        name="division_detail",
    ),
    path(
        "divisions/<int:pk>/edit/",
        views.DivisionUpdateView.as_view(),
        name="division_update",
    ),
    path(
        "divisions/<int:pk>/delete/",
        views.DivisionDeleteView.as_view(),
        name="division_delete",
    ),
    # Event Contact URLs
    path(
        "event-contacts/",
        views_data_management.EventContactListView.as_view(),
        name="eventcontact_list",
    ),
    path(
        "event-contacts/create/",
        views_data_management.EventContactCreateView.as_view(),
        name="eventcontact_create",
    ),
    path(
        "event-contacts/<int:pk>/",
        views_data_management.EventContactDetailView.as_view(),
        name="eventcontact_detail",
    ),
    path(
        "event-contacts/<int:pk>/edit/",
        views_data_management.EventContactUpdateView.as_view(),
        name="eventcontact_update",
    ),
    path(
        "event-contacts/<int:pk>/delete/",
        views_data_management.EventContactDeleteView.as_view(),
        name="eventcontact_delete",
    ),
    # Event Type URLs
    path(
        "event-types/",
        views_data_management.EventTypeListView.as_view(),
        name="eventtype_list",
    ),
    path(
        "event-types/create/",
        views_data_management.EventTypeCreateView.as_view(),
        name="eventtype_create",
    ),
    path(
        "event-types/<int:pk>/",
        views_data_management.EventTypeDetailView.as_view(),
        name="eventtype_detail",
    ),
    path(
        "event-types/<int:pk>/edit/",
        views_data_management.EventTypeUpdateView.as_view(),
        name="eventtype_update",
    ),
    path(
        "event-types/<int:pk>/delete/",
        views_data_management.EventTypeDeleteView.as_view(),
        name="eventtype_delete",
    ),
    # Gate Fee Type URLs
    path(
        "gate-fee-types/",
        views_data_management.GateFeeTypeListView.as_view(),
        name="gatefeetype_list",
    ),
    path(
        "gate-fee-types/create/",
        views_data_management.GateFeeTypeCreateView.as_view(),
        name="gatefeetype_create",
    ),
    path(
        "gate-fee-types/<int:pk>/",
        views_data_management.GateFeeTypeDetailView.as_view(),
        name="gatefeetype_detail",
    ),
    path(
        "gate-fee-types/<int:pk>/edit/",
        views_data_management.GateFeeTypeUpdateView.as_view(),
        name="gatefeetype_update",
    ),
    path(
        "gate-fee-types/<int:pk>/delete/",
        views_data_management.GateFeeTypeDeleteView.as_view(),
        name="gatefeetype_delete",
    ),
    # API endpoints
    path("api/detail/<int:pk>/", views.EventDetailAPIView.as_view(), name="api_detail"),
    path("ajax/<int:event_id>/services/", views.get_event_services, name="get_event_services"),
]
