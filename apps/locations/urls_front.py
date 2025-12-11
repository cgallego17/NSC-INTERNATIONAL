"""
URLs front para reservas de hoteles - Requieren autenticación
"""

from django.urls import path
from . import views_front
from . import cart_views

# No usar app_name - usa el namespace del archivo principal (locations)

urlpatterns = [
    # Hotel URLs (front)
    path("hotels/", views_front.FrontHotelListView.as_view(), name="front_hotel_list"),
    path(
        "hotels/<int:pk>/",
        views_front.FrontHotelDetailView.as_view(),
        name="front_hotel_detail",
    ),
    # Reservation URLs (front)
    path(
        "hotels/reservations/",
        views_front.FrontHotelReservationListView.as_view(),
        name="front_hotel_reservation_list",
    ),
    path(
        "hotels/reservations/create/",
        views_front.FrontHotelReservationCreateView.as_view(),
        name="front_hotel_reservation_create",
    ),
    path(
        "hotels/reservations/<int:pk>/",
        views_front.FrontHotelReservationDetailView.as_view(),
        name="front_hotel_reservation_detail",
    ),
    path(
        "hotels/reservations/<int:pk>/checkout/",
        views_front.FrontHotelReservationCheckoutView.as_view(),
        name="front_hotel_reservation_checkout",
    ),
    # AJAX URLs (front)
    path(
        "ajax/hotels/<int:hotel_id>/rooms/",
        views_front.get_hotel_rooms,
        name="get_hotel_rooms",
    ),
    path(
        "ajax/hotels/<int:hotel_id>/services/",
        views_front.get_hotel_services,
        name="get_hotel_services",
    ),
    path(
        "ajax/reservations/calculate-total/",
        views_front.calculate_reservation_total,
        name="calculate_reservation_total",
    ),
    # Cart URLs
    path("hotels/cart/", cart_views.HotelCartView.as_view(), name="hotel_cart"),
    path("hotels/cart/add/", cart_views.AddToCartView.as_view(), name="add_to_cart"),
    path(
        "hotels/cart/remove/",
        cart_views.RemoveFromCartView.as_view(),
        name="remove_from_cart",
    ),
    path("hotels/cart/clear/", cart_views.ClearCartView.as_view(), name="clear_cart"),
    path(
        "hotels/cart/checkout/",
        cart_views.CheckoutCartView.as_view(),
        name="checkout_cart",
    ),
    # AJAX para obtener carrito en JSON
    path("ajax/cart/", cart_views.get_cart_json, name="get_cart_json"),
]








