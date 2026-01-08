"""
Vistas para el carrito de reservas de hoteles - Usa sesión de Django
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import TemplateView
from decimal import Decimal
import json

from .models import Hotel, HotelRoom, HotelService, HotelReservation


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

                    includes = int(room.price_includes_guests or 1)
                    extra_guests = max(0, guests - includes)
                    per_night_total = room.price_per_night + (room.additional_guest_price or Decimal("0.00")) * extra_guests
                    room_total = per_night_total * nights
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
                return JsonResponse({"error": _("Incomplete data")}, status=400)

            # Verificar que la habitación existe
            room = HotelRoom.objects.get(id=room_id, is_available=True)

            # Calcular noches
            from datetime import datetime, date

            try:
                check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
                check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse(
                    {"error": _("Invalid date format. Use YYYY-MM-DD format.")},
                    status=400
                )

            # Validar que las fechas sean válidas
            today = date.today()
            if check_in_date < today:
                return JsonResponse(
                    {"error": _("Check-in date cannot be in the past.")},
                    status=400
                )

            if check_out_date <= check_in_date:
                return JsonResponse(
                    {"error": _("Check-out date must be after check-in date.")},
                    status=400
                )

            nights = (check_out_date - check_in_date).days

            if nights <= 0:
                return JsonResponse({"error": _("Invalid dates: there must be at least one night.")}, status=400)

            # Verificar disponibilidad
            # Excluir reservas canceladas y reservas pending del mismo usuario (permite cambiar habitación)
            # También excluir reservas checked_out (ya finalizadas)
            overlapping_reservations = room.reservations.filter(
                check_in__lt=check_out_date,
                check_out__gt=check_in_date,
            ).exclude(
                status__in=["cancelled", "checked_out"]  # Excluir canceladas y finalizadas
            ).exclude(
                user=request.user,
                status="pending"  # Permitir que el usuario cambie su propia reserva pending
            )

            if overlapping_reservations.exists():
                # Obtener detalles de la reserva conflictiva para un mensaje más informativo
                conflicting = overlapping_reservations.first()
                status_display = dict(HotelReservation.RESERVATION_STATUS_CHOICES).get(
                    conflicting.status, conflicting.status
                )
                error_msg = _(
                    "Room not available for those dates. "
                    "There is already a reservation from %(check_in)s to %(check_out)s "
                    "(Status: %(status)s)."
                ) % {
                    'check_in': conflicting.check_in.strftime('%d/%m/%Y'),
                    'check_out': conflicting.check_out.strftime('%d/%m/%Y'),
                    'status': status_display
                }
                return JsonResponse({"error": error_msg}, status=400)

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

                includes = int(room.price_includes_guests or 1)
                extra_guests = max(0, guests - includes)
                per_night_total = room.price_per_night + (room.additional_guest_price or Decimal("0.00")) * extra_guests
                room_total = per_night_total * nights
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

                    # Validar que la habitación esté disponible
                    if not room.is_available:
                        errors.append(
                            _("Room #%(room_number)s is not available.")
                            % {'room_number': room.room_number}
                        )
                        continue

                    # Validar stock disponible: contar reservas activas en esas fechas vs stock total
                    # Usar select_for_update para lock y evitar condiciones de carrera
                    if room.stock is not None and room.stock > 0:
                        with transaction.atomic():
                            room_obj = HotelRoom.objects.select_for_update().get(id=room.id)
                            active_reservations_count = room_obj.reservations.filter(
                                check_in__lt=check_out,
                                check_out__gt=check_in,
                                status__in=["pending", "confirmed", "checked_in"],
                            ).count()

                            if active_reservations_count >= room_obj.stock:
                                errors.append(
                                    _("Room #%(room_number)s is not available for the selected dates. "
                                      "All rooms of this type are already reserved.")
                                    % {'room_number': room_obj.room_number}
                                )
                                continue

                        # Refrescar room para usar en la creación de la reserva
                        room.refresh_from_db()

                    # Verificar disponibilidad (overlapping) - excluir reservas del mismo usuario pending
                    overlapping_reservations = room.reservations.filter(
                        check_in__lt=check_out,
                        check_out__gt=check_in,
                    ).exclude(
                        status__in=["cancelled", "checked_out"]
                    ).exclude(
                        user=request.user,
                        status="pending"
                    )

                    if overlapping_reservations.exists():
                        conflicting = overlapping_reservations.first()
                        status_display = dict(HotelReservation.RESERVATION_STATUS_CHOICES).get(
                            conflicting.status, conflicting.status
                        )
                        errors.append(
                            _("Room #%(room_number)s is no longer available "
                              "(conflict with reservation from %(check_in)s to %(check_out)s, Status: %(status)s).")
                            % {
                                'room_number': room.room_number,
                                'check_in': conflicting.check_in.strftime('%d/%m/%Y'),
                                'check_out': conflicting.check_out.strftime('%d/%m/%Y'),
                                'status': status_display
                            }
                        )
                        continue

                    # IMPORTANTE: NO crear la reserva hasta que el pago sea válido
                    # Las reservas SOLO se crean después de un pago exitoso de Stripe
                    # Ver: apps/accounts/views_private.py:_finalize_stripe_event_checkout
                    #
                    # Por ahora, guardar los datos en la sesión para procesarlos después del pago
                    # TODO: Integrar este flujo con Stripe checkout antes de crear reservas
                    created_reservations.append({
                        "room_id": room.id,
                        "check_in": str(check_in),
                        "check_out": str(check_out),
                        "guests": int(item_data.get("guests", 1)),
                        "services": item_data.get("services", []),
                    })
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









