"""
Vistas front para reservas de hoteles - Requieren autenticación, para usuarios del front
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, TemplateView
from decimal import Decimal

from .models import (
    Hotel,
    HotelReservation,
    HotelReservationService,
    HotelRoom,
    HotelService,
)


class FrontHotelListView(LoginRequiredMixin, ListView):
    """Lista de hoteles disponibles para reservas - Front dashboard"""

    model = Hotel
    template_name = "locations/front_hotel_list.html"
    context_object_name = "hotels"
    paginate_by = 12

    def get_queryset(self):
        queryset = Hotel.objects.filter(is_active=True).select_related(
            "country", "state", "city"
        )

        # Búsqueda
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(hotel_name__icontains=search)
                | Q(address__icontains=search)
                | Q(city__name__icontains=search)
            )

        # Filtro por país
        country = self.request.GET.get("country")
        if country:
            queryset = queryset.filter(country_id=country)

        return queryset.order_by("hotel_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import Country

        context["countries"] = Country.objects.filter(is_active=True).order_by("name")
        return context


class FrontHotelDetailView(LoginRequiredMixin, DetailView):
    """Detalle de hotel con habitaciones disponibles - Front dashboard"""

    model = Hotel
    template_name = "locations/front_hotel_detail.html"
    context_object_name = "hotel"

    def get_queryset(self):
        return Hotel.objects.filter(is_active=True).select_related(
            "country", "state", "city"
        )

    def get_template_names(self):
        # Si es una petición AJAX, usar un template sin layout
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return ["locations/front_hotel_detail_ajax.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener habitaciones disponibles
        context["rooms"] = self.object.rooms.filter(is_available=True).order_by(
            "room_number"
        )
        # Obtener servicios activos
        context["services"] = self.object.services.filter(is_active=True).order_by(
            "service_name"
        )
        # Verificar si es una petición AJAX para el modal
        context["is_ajax"] = (
            self.request.headers.get("X-Requested-With") == "XMLHttpRequest"
        )
        return context


class FrontHotelReservationCreateView(LoginRequiredMixin, CreateView):
    """Crear reserva de hotel desde el front - Requiere autenticación"""

    model = HotelReservation
    template_name = "locations/front_hotel_reservation_form.html"
    fields = [
        "hotel",
        "room",
        "guest_name",
        "guest_email",
        "guest_phone",
        "number_of_guests",
        "check_in",
        "check_out",
        "notes",
    ]

    def dispatch(self, request, *args, **kwargs):
        # Pre-llenar hotel y habitación si vienen en GET
        self.hotel_id = request.GET.get("hotel")
        self.room_id = request.GET.get("room")
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        # Pre-llenar con datos del usuario
        initial["user"] = self.request.user
        initial["guest_name"] = (
            self.request.user.get_full_name() or self.request.user.username
        )
        initial["guest_email"] = self.request.user.email
        if hasattr(self.request.user, "profile") and self.request.user.profile.phone:
            initial["guest_phone"] = self.request.user.profile.phone

        # Pre-llenar hotel y habitación si vienen en GET
        if self.hotel_id:
            initial["hotel"] = self.hotel_id
        if self.room_id:
            initial["room"] = self.room_id

        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Ocultar el campo user (se asigna automáticamente)
        if "user" in form.fields:
            form.fields["user"].widget = form.fields["user"].hidden_widget()
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener hoteles activos
        context["hotels"] = Hotel.objects.filter(is_active=True).order_by("hotel_name")

        # Si hay un hotel seleccionado, obtener sus habitaciones y servicios
        hotel_id = self.request.GET.get("hotel") or (
            self.hotel_id if hasattr(self, "hotel_id") else None
        )
        if hotel_id:
            try:
                hotel = Hotel.objects.get(id=hotel_id, is_active=True)
                context["selected_hotel"] = hotel
                context["rooms"] = hotel.rooms.filter(is_available=True).order_by(
                    "room_number"
                )
                context["services"] = hotel.services.filter(is_active=True).order_by(
                    "service_name"
                )
            except Hotel.DoesNotExist:
                context["selected_hotel"] = None
                context["rooms"] = HotelRoom.objects.none()
                context["services"] = HotelService.objects.none()
        else:
            context["selected_hotel"] = None
            context["rooms"] = HotelRoom.objects.none()
            context["services"] = HotelService.objects.none()

        return context

    def form_valid(self, form):
        # Asignar el usuario actual
        reservation = form.save(commit=False)
        reservation.user = self.request.user
        reservation.status = "pending"  # Estado inicial
        reservation.save()

        # Procesar servicios adicionales desde el formulario
        services_data = self.request.POST.getlist("services")
        quantities_data = self.request.POST.getlist("quantities")

        for service_id, quantity in zip(services_data, quantities_data):
            if service_id and quantity:
                try:
                    service = HotelService.objects.get(
                        id=service_id, hotel=reservation.hotel, is_active=True
                    )
                    HotelReservationService.objects.create(
                        reservation=reservation, service=service, quantity=int(quantity)
                    )
                except (HotelService.DoesNotExist, ValueError):
                    pass

        # Recalcular el total después de agregar servicios
        reservation.total_amount = reservation.calculate_total()
        reservation.save()

        messages.success(
            self.request,
            f"Reserva #{reservation.id} creada exitosamente. Total: ${reservation.total_amount:.2f}",
        )
        return redirect("locations:front_hotel_reservation_checkout", pk=reservation.pk)

    def get_success_url(self):
        return reverse_lazy(
            "locations:front_hotel_reservation_checkout",
            kwargs={"pk": self.object.pk},
        )


class FrontHotelReservationCheckoutView(LoginRequiredMixin, DetailView):
    """Vista de checkout/pago para reserva - Front dashboard"""

    model = HotelReservation
    template_name = "locations/front_hotel_reservation_checkout.html"
    context_object_name = "reservation"

    def dispatch(self, request, *args, **kwargs):
        reservation = self.get_object()
        # Verificar que la reserva pertenezca al usuario actual
        if reservation.user != request.user and not (
            request.user.is_staff or request.user.is_superuser
        ):
            messages.error(request, "No tienes permiso para ver esta reserva.")
            return redirect("locations:front_hotel_reservation_list")

        # Manejar confirmación de pago
        if request.method == "POST" and "confirm_payment" in request.POST:
            if reservation.status == "pending":
                reservation.status = "confirmed"
                reservation.save()
                messages.success(
                    request,
                    f"¡Reserva #{reservation.id} confirmada exitosamente! Total pagado: ${reservation.total_amount:.2f}",
                )
                return redirect(
                    "locations:front_hotel_reservation_detail", pk=reservation.pk
                )

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener servicios de la reserva
        context["services"] = self.object.service_reservations.select_related(
            "service"
        ).all()
        return context


class FrontHotelReservationListView(LoginRequiredMixin, ListView):
    """Lista de reservas del usuario - Front dashboard"""

    model = HotelReservation
    template_name = "locations/front_hotel_reservation_list.html"
    context_object_name = "reservations"
    paginate_by = 10

    def get_queryset(self):
        # Solo mostrar reservas del usuario actual
        queryset = (
            HotelReservation.objects.filter(user=self.request.user)
            .select_related("hotel", "room")
            .order_by("-created_at")
        )

        # Filtro por estado
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = HotelReservation.RESERVATION_STATUS_CHOICES
        return context


class FrontHotelReservationDetailView(LoginRequiredMixin, DetailView):
    """Detalle de reserva del usuario - Front dashboard"""

    model = HotelReservation
    template_name = "locations/front_hotel_reservation_detail.html"
    context_object_name = "reservation"

    def dispatch(self, request, *args, **kwargs):
        reservation = self.get_object()
        # Verificar que la reserva pertenezca al usuario actual
        if reservation.user != request.user and not (
            request.user.is_staff or request.user.is_superuser
        ):
            messages.error(request, "No tienes permiso para ver esta reserva.")
            return redirect("locations:front_hotel_reservation_list")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener servicios de la reserva
        context["services"] = self.object.service_reservations.select_related(
            "service"
        ).all()
        return context


# Vista AJAX para obtener habitaciones de un hotel
def get_hotel_rooms(request, hotel_id):
    """API para obtener habitaciones disponibles de un hotel"""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    try:
        hotel = Hotel.objects.get(id=hotel_id, is_active=True)
        rooms = hotel.rooms.filter(is_available=True).order_by("room_number")

        # Obtener fechas de check-in y check-out si están en la petición
        check_in = request.GET.get("check_in")
        check_out = request.GET.get("check_out")

        rooms_data = []
        for room in rooms:
            # Verificar si la habitación está disponible en las fechas especificadas
            is_available = True
            if check_in and check_out:
                from datetime import datetime

                try:
                    check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
                    check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()
                    # Verificar si hay reservas que se solapen
                    overlapping = room.reservations.filter(
                        check_in__lt=check_out_date,
                        check_out__gt=check_in_date,
                        status__in=["pending", "confirmed", "checked_in"],
                    ).exists()
                    is_available = not overlapping
                except ValueError:
                    pass

            rooms_data.append(
                {
                    "id": room.id,
                    "room_number": room.room_number,
                    "room_type": room.get_room_type_display(),
                    "capacity": room.capacity,
                    "price_per_night": str(room.price_per_night),
                    "description": room.description or "",
                    "is_available": is_available,
                }
            )

        return JsonResponse({"rooms": rooms_data}, safe=False)
    except Hotel.DoesNotExist:
        return JsonResponse({"error": "Hotel not found"}, status=404)


# Vista AJAX para obtener servicios de un hotel
def get_hotel_services(request, hotel_id):
    """API para obtener servicios disponibles de un hotel"""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    try:
        hotel = Hotel.objects.get(id=hotel_id, is_active=True)
        services = hotel.services.filter(is_active=True).order_by("service_name")

        services_data = []
        for service in services:
            services_data.append(
                {
                    "id": service.id,
                    "service_name": service.service_name,
                    "service_type": service.get_service_type_display(),
                    "price": str(service.price),
                    "is_per_person": service.is_per_person,
                    "is_per_night": service.is_per_night,
                    "description": service.description or "",
                }
            )

        return JsonResponse({"services": services_data}, safe=False)
    except Hotel.DoesNotExist:
        return JsonResponse({"error": "Hotel not found"}, status=404)


# Vista AJAX para calcular el total de una reserva
def calculate_reservation_total(request):
    """API para calcular el total de una reserva antes de crearla"""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    try:
        room_id = request.GET.get("room_id")
        check_in = request.GET.get("check_in")
        check_out = request.GET.get("check_out")
        number_of_guests = int(request.GET.get("number_of_guests", 1))
        services = request.GET.getlist("services[]")
        quantities = request.GET.getlist("quantities[]")

        if not room_id or not check_in or not check_out:
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        from datetime import datetime

        check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
        check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()
        nights = (check_out_date - check_in_date).days

        if nights <= 0:
            return JsonResponse({"error": "Invalid dates"}, status=400)

        # Obtener habitación
        room = HotelRoom.objects.get(id=room_id, is_available=True)
        room_total = room.price_per_night * nights

        # Calcular servicios
        services_total = Decimal("0.00")
        services_detail = []

        for service_id, quantity in zip(services, quantities):
            if service_id and quantity:
                try:
                    service = HotelService.objects.get(
                        id=service_id, hotel=room.hotel, is_active=True
                    )
                    qty = int(quantity)
                    if service.is_per_person:
                        service_price = service.price * number_of_guests * qty
                    else:
                        service_price = service.price * qty

                    if service.is_per_night:
                        service_price = service_price * nights

                    services_total += service_price
                    services_detail.append(
                        {
                            "name": service.service_name,
                            "price": str(service_price),
                        }
                    )
                except (HotelService.DoesNotExist, ValueError):
                    pass

        total = room_total + services_total

        return JsonResponse(
            {
                "room_total": str(room_total),
                "services_total": str(services_total),
                "total": str(total),
                "nights": nights,
                "services_detail": services_detail,
            }
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)








