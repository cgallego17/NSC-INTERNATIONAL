"""
Vistas para el carrito de reservas de hoteles - Usa sesión de Django
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView
from decimal import Decimal
import json

from .models import Hotel, HotelRoom, HotelService


class HotelCartView(LoginRequiredMixin, TemplateView):
    """Vista del carrito de reservas de hoteles"""

    template_name = "locations/hotel_cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.request.session.get("hotel_cart", {})

        # Procesar items del carrito
        cart_items = []
        total = Decimal("0.00")

        for item_id, item_data in cart.items():
            try:
                if item_data.get("type") == "room":
                    room = HotelRoom.objects.get(id=item_data.get("room_id"))
                    hotel = room.hotel
                    nights = int(item_data.get("nights", 1))
                    guests = int(item_data.get("guests", 1))

                    room_total = room.price_per_night * nights
                    services_total = Decimal("0.00")
                    services_list = []

                    # Calcular servicios
                    for service_data in item_data.get("services", []):
                        try:
                            service = HotelService.objects.get(
                                id=service_data.get("service_id"),
                                hotel=hotel,
                                is_active=True,
                            )
                            quantity = int(service_data.get("quantity", 1))

                            service_price = service.price * quantity
                            if service.is_per_person:
                                service_price = service_price * guests
                            if service.is_per_night:
                                service_price = service_price * nights

                            services_total += service_price
                            services_list.append(
                                {
                                    "service": service,
                                    "quantity": quantity,
                                    "price": service_price,
                                }
                            )
                        except HotelService.DoesNotExist:
                            pass

                    item_total = room_total + services_total
                    total += item_total

                    cart_items.append(
                        {
                            "id": item_id,
                            "type": "room",
                            "hotel": hotel,
                            "room": room,
                            "check_in": item_data.get("check_in"),
                            "check_out": item_data.get("check_out"),
                            "nights": nights,
                            "guests": guests,
                            "services": services_list,
                            "room_total": room_total,
                            "services_total": services_total,
                            "total": item_total,
                        }
                    )
            except (HotelRoom.DoesNotExist, ValueError, KeyError):
                # Si el item ya no existe, eliminarlo del carrito
                if item_id in cart:
                    del cart[item_id]
                    self.request.session["hotel_cart"] = cart

        context["cart_items"] = cart_items
        context["cart_total"] = total
        context["cart_count"] = len(cart_items)
        return context


class AddToCartView(LoginRequiredMixin, View):
    """Agregar item al carrito"""

    def post(self, request):
        try:
            data = json.loads(request.body)
            room_id = data.get("room_id")
            check_in = data.get("check_in")
            check_out = data.get("check_out")
            guests = int(data.get("guests", 1))
            services = data.get("services", [])

            if not room_id or not check_in or not check_out:
                return JsonResponse({"error": "Datos incompletos"}, status=400)

            # Verificar que la habitación existe
            room = HotelRoom.objects.get(id=room_id, is_available=True)

            # Calcular noches
            from datetime import datetime

            check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
            check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()
            nights = (check_out_date - check_in_date).days

            if nights <= 0:
                return JsonResponse({"error": "Fechas inválidas"}, status=400)

            # Verificar disponibilidad
            overlapping = room.reservations.filter(
                check_in__lt=check_out_date,
                check_out__gt=check_in_date,
                status__in=["pending", "confirmed", "checked_in"],
            ).exists()

            if overlapping:
                return JsonResponse(
                    {"error": "Habitación no disponible en esas fechas"}, status=400
                )

            # Crear item del carrito
            cart = request.session.get("hotel_cart", {})
            item_id = f"room_{room_id}_{check_in}_{check_out}"

            cart[item_id] = {
                "type": "room",
                "room_id": room_id,
                "hotel_id": room.hotel.id,
                "check_in": check_in,
                "check_out": check_out,
                "nights": nights,
                "guests": guests,
                "services": services,
            }

            request.session["hotel_cart"] = cart
            request.session.modified = True

            return JsonResponse(
                {
                    "success": True,
                    "message": "Agregado al carrito",
                    "cart_count": len(cart),
                }
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class RemoveFromCartView(LoginRequiredMixin, View):
    """Eliminar item del carrito"""

    def post(self, request):
        try:
            data = json.loads(request.body)
            item_id = data.get("item_id")

            if not item_id:
                return JsonResponse({"error": "ID de item requerido"}, status=400)

            cart = request.session.get("hotel_cart", {})
            if item_id in cart:
                del cart[item_id]
                request.session["hotel_cart"] = cart
                request.session.modified = True

                return JsonResponse(
                    {
                        "success": True,
                        "message": "Item eliminado del carrito",
                        "cart_count": len(cart),
                    }
                )
            else:
                return JsonResponse({"error": "Item no encontrado"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class ClearCartView(LoginRequiredMixin, View):
    """Limpiar todo el carrito"""

    def post(self, request):
        request.session["hotel_cart"] = {}
        request.session.modified = True
        messages.success(request, "Carrito limpiado exitosamente.")
        return redirect("locations:hotel_cart")


@login_required
def get_cart_json(request):
    """API para obtener el carrito en formato JSON para el sidebar"""
    cart = request.session.get("hotel_cart", {})

    if not cart:
        return JsonResponse({"success": True, "items": [], "total": "0.00", "count": 0})

    cart_items = []
    total = Decimal("0.00")

    for item_id, item_data in cart.items():
        try:
            if item_data.get("type") == "room":
                room = HotelRoom.objects.get(id=item_data.get("room_id"))
                hotel = room.hotel
                nights = int(item_data.get("nights", 1))
                guests = int(item_data.get("guests", 1))

                room_total = room.price_per_night * nights
                services_total = Decimal("0.00")

                # Calcular servicios
                for service_data in item_data.get("services", []):
                    try:
                        service = HotelService.objects.get(
                            id=service_data.get("service_id"),
                            hotel=hotel,
                            is_active=True,
                        )
                        quantity = int(service_data.get("quantity", 1))

                        service_price = service.price * quantity
                        if service.is_per_person:
                            service_price = service_price * guests
                        if service.is_per_night:
                            service_price = service_price * nights

                        services_total += service_price
                    except HotelService.DoesNotExist:
                        pass

                item_total = room_total + services_total
                total += item_total

                cart_items.append(
                    {
                        "id": item_id,
                        "hotel_name": hotel.hotel_name,
                        "room_number": room.room_number,
                        "room_type": room.get_room_type_display(),
                        "check_in": item_data.get("check_in"),
                        "check_out": item_data.get("check_out"),
                        "nights": nights,
                        "guests": guests,
                        "total": str(item_total),
                    }
                )
        except (HotelRoom.DoesNotExist, ValueError, KeyError):
            pass

    return JsonResponse(
        {
            "success": True,
            "items": cart_items,
            "total": str(total),
            "count": len(cart_items),
        }
    )


class CheckoutCartView(LoginRequiredMixin, View):
    """Procesar checkout del carrito - Crear todas las reservas"""

    def post(self, request):
        cart = request.session.get("hotel_cart", {})

        if not cart:
            messages.error(request, "El carrito está vacío.")
            return redirect("locations:hotel_cart")

        from .models import HotelReservation, HotelReservationService
        from datetime import datetime

        created_reservations = []
        errors = []

        for item_id, item_data in cart.items():
            try:
                if item_data.get("type") == "room":
                    room = HotelRoom.objects.get(id=item_data.get("room_id"))
                    check_in = datetime.strptime(
                        item_data.get("check_in"), "%Y-%m-%d"
                    ).date()
                    check_out = datetime.strptime(
                        item_data.get("check_out"), "%Y-%m-%d"
                    ).date()

                    # Verificar disponibilidad nuevamente
                    overlapping = room.reservations.filter(
                        check_in__lt=check_out,
                        check_out__gt=check_in,
                        status__in=["pending", "confirmed", "checked_in"],
                    ).exists()

                    if overlapping:
                        errors.append(
                            f"Habitación #{room.room_number} ya no está disponible."
                        )
                        continue

                    # Crear reserva
                    reservation = HotelReservation.objects.create(
                        hotel=room.hotel,
                        room=room,
                        user=request.user,
                        guest_name=request.user.get_full_name()
                        or request.user.username,
                        guest_email=request.user.email,
                        guest_phone=(
                            getattr(request.user.profile, "phone", "")
                            if hasattr(request.user, "profile")
                            else ""
                        ),
                        number_of_guests=int(item_data.get("guests", 1)),
                        check_in=check_in,
                        check_out=check_out,
                        status="pending",
                        notes="Reserva desde carrito",
                    )

                    # Agregar servicios
                    for service_data in item_data.get("services", []):
                        try:
                            service = HotelService.objects.get(
                                id=service_data.get("service_id"),
                                hotel=room.hotel,
                                is_active=True,
                            )
                            HotelReservationService.objects.create(
                                reservation=reservation,
                                service=service,
                                quantity=int(service_data.get("quantity", 1)),
                            )
                        except HotelService.DoesNotExist:
                            pass

                    # Recalcular total
                    reservation.total_amount = reservation.calculate_total()
                    reservation.save()

                    created_reservations.append(reservation)
            except Exception as e:
                errors.append(f"Error al crear reserva: {str(e)}")

        # Limpiar carrito si todo fue exitoso
        if created_reservations and not errors:
            request.session["hotel_cart"] = {}
            request.session.modified = True
            messages.success(
                request,
                f"¡{len(created_reservations)} reserva(s) creada(s) exitosamente! Total: ${sum(r.total_amount for r in created_reservations):.2f}",
            )
            return redirect("locations:front_hotel_reservation_list")
        elif created_reservations:
            messages.warning(
                request,
                f"{len(created_reservations)} reserva(s) creada(s), pero hubo {len(errors)} error(es).",
            )
            for error in errors:
                messages.error(request, error)
        else:
            messages.error(request, "No se pudo crear ninguna reserva.")
            for error in errors:
                messages.error(request, error)

        return redirect("locations:hotel_cart")









