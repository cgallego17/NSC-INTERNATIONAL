"""
Vistas para gestión de hoteles desde el dashboard
"""

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    TemplateView,
)

from apps.core.mixins import StaffRequiredMixin
from apps.locations.models import (
    Hotel,
    HotelAmenity,
    HotelImage,
    HotelRoom,
    HotelService,
)


# ===== HOTEL VIEWS =====
class HotelListView(StaffRequiredMixin, ListView):
    """Lista de hoteles"""

    model = Hotel
    template_name = "accounts/hotel_list.html"
    context_object_name = "hotels"
    paginate_by = 20

    def get_queryset(self):
        queryset = Hotel.objects.select_related("city", "state", "country")
        search = self.request.GET.get("search")
        status = self.request.GET.get("status")
        country = self.request.GET.get("country")

        if search:
            queryset = queryset.filter(
                Q(hotel_name__icontains=search)
                | Q(address__icontains=search)
                | Q(city__name__icontains=search)
            )

        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)

        if country:
            queryset = queryset.filter(country_id=country)

        return queryset.order_by("hotel_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["status_filter"] = self.request.GET.get("status", "")
        context["country_filter"] = self.request.GET.get("country", "")

        # Import Country for filters
        from apps.locations.models import Country
        context["countries"] = Country.objects.filter(is_active=True).order_by("name")

        return context


class HotelDetailView(StaffRequiredMixin, DetailView):
    """Detalle de un hotel con todas sus relaciones"""

    model = Hotel
    template_name = "accounts/hotel_detail.html"
    context_object_name = "hotel"

    def get_queryset(self):
        return Hotel.objects.select_related(
            "city", "state", "country"
        ).prefetch_related("images", "amenities", "rooms", "services")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hotel = self.object

        context["images"] = hotel.images.all()
        context["amenities"] = hotel.amenities.all()
        context["rooms"] = hotel.rooms.all()
        context["services"] = hotel.services.all()

        return context


class HotelCreateView(StaffRequiredMixin, CreateView):
    """Crear un nuevo hotel"""

    model = Hotel
    template_name = "accounts/hotel_form.html"
    fields = [
        "hotel_name",
        "address",
        "photo",
        "information",
        "registration_url",
        "city",
        "state",
        "country",
        "capacity",
        "contact_name",
        "contact_email",
        "contact_phone",
        "is_active",
    ]
    success_url = reverse_lazy("accounts:hotel_list")

    def form_valid(self, form):
        messages.success(self.request, f"Hotel '{form.instance.hotel_name}' creado exitosamente.")
        return super().form_valid(form)


class HotelUpdateView(StaffRequiredMixin, UpdateView):
    """Actualizar un hotel existente"""

    model = Hotel
    template_name = "accounts/hotel_form.html"
    fields = [
        "hotel_name",
        "address",
        "photo",
        "information",
        "registration_url",
        "city",
        "state",
        "country",
        "capacity",
        "contact_name",
        "contact_email",
        "contact_phone",
        "is_active",
    ]
    success_url = reverse_lazy("accounts:hotel_list")

    def form_valid(self, form):
        messages.success(self.request, f"Hotel '{form.instance.hotel_name}' actualizado exitosamente.")
        return super().form_valid(form)


class HotelDeleteView(StaffRequiredMixin, DeleteView):
    """Eliminar un hotel"""

    model = Hotel
    template_name = "accounts/hotel_confirm_delete.html"
    success_url = reverse_lazy("accounts:hotel_list")

    def delete(self, request, *args, **kwargs):
        hotel_name = self.get_object().hotel_name
        messages.success(request, f"Hotel '{hotel_name}' eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)


# ===== HOTEL IMAGE VIEWS =====
class HotelImageListView(StaffRequiredMixin, ListView):
    """Lista de imágenes de un hotel"""

    model = HotelImage
    template_name = "accounts/hotel_image_list.html"
    context_object_name = "images"
    paginate_by = 20

    def get_queryset(self):
        self.hotel = get_object_or_404(Hotel, pk=self.kwargs["hotel_pk"])
        return HotelImage.objects.filter(hotel=self.hotel).order_by(
            "order", "-is_featured", "-created_at"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hotel"] = self.hotel
        return context


class HotelImageCreateView(StaffRequiredMixin, CreateView):
    """Agregar nueva imagen al hotel"""

    model = HotelImage
    template_name = "accounts/hotel_image_form.html"
    fields = ["image", "title", "alt_text", "order", "is_featured"]

    def dispatch(self, request, *args, **kwargs):
        self.hotel = get_object_or_404(Hotel, pk=self.kwargs["hotel_pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.hotel = self.hotel
        messages.success(self.request, "Imagen agregada exitosamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("accounts:hotel_image_list", kwargs={"hotel_pk": self.hotel.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hotel"] = self.hotel
        return context


class HotelImageUpdateView(StaffRequiredMixin, UpdateView):
    """Actualizar imagen del hotel"""

    model = HotelImage
    template_name = "accounts/hotel_image_form.html"
    fields = ["image", "title", "alt_text", "order", "is_featured"]

    def get_success_url(self):
        return reverse_lazy(
            "accounts:hotel_image_list", kwargs={"hotel_pk": self.object.hotel.pk}
        )

    def form_valid(self, form):
        messages.success(self.request, "Imagen actualizada exitosamente.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hotel"] = self.object.hotel
        return context


class HotelImageDeleteView(StaffRequiredMixin, DeleteView):
    """Eliminar imagen del hotel"""

    model = HotelImage
    template_name = "accounts/hotel_image_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy(
            "accounts:hotel_image_list", kwargs={"hotel_pk": self.object.hotel.pk}
        )

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Imagen eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hotel"] = self.object.hotel
        return context


# ===== HOTEL AMENITY VIEWS =====
class HotelAmenityListView(StaffRequiredMixin, ListView):
    """Lista de amenidades de un hotel"""

    model = HotelAmenity
    template_name = "accounts/hotel_amenity_list.html"
    context_object_name = "amenities"
    paginate_by = 50

    def get_queryset(self):
        self.hotel = get_object_or_404(Hotel, pk=self.kwargs["hotel_pk"])
        queryset = HotelAmenity.objects.filter(hotel=self.hotel)

        category = self.request.GET.get("category")
        if category:
            queryset = queryset.filter(category=category)

        return queryset.order_by("category", "order", "name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hotel"] = self.hotel
        context["category_filter"] = self.request.GET.get("category", "")
        context["categories"] = HotelAmenity.AMENITY_CATEGORY_CHOICES
        return context


class HotelAmenityCreateView(StaffRequiredMixin, CreateView):
    """Agregar nueva amenidad al hotel"""

    model = HotelAmenity
    template_name = "accounts/hotel_amenity_form.html"
    fields = ["name", "category", "icon", "description", "is_available", "order"]

    def dispatch(self, request, *args, **kwargs):
        self.hotel = get_object_or_404(Hotel, pk=self.kwargs["hotel_pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.hotel = self.hotel
        messages.success(self.request, f"Amenidad '{form.instance.name}' agregada exitosamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("accounts:hotel_amenity_list", kwargs={"hotel_pk": self.hotel.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hotel"] = self.hotel
        return context


class HotelAmenityUpdateView(StaffRequiredMixin, UpdateView):
    """Actualizar amenidad del hotel"""

    model = HotelAmenity
    template_name = "accounts/hotel_amenity_form.html"
    fields = ["name", "category", "icon", "description", "is_available", "order"]

    def get_success_url(self):
        return reverse_lazy(
            "accounts:hotel_amenity_list", kwargs={"hotel_pk": self.object.hotel.pk}
        )

    def form_valid(self, form):
        messages.success(self.request, f"Amenidad '{form.instance.name}' actualizada exitosamente.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hotel"] = self.object.hotel
        return context


class HotelAmenityDeleteView(StaffRequiredMixin, DeleteView):
    """Eliminar amenidad del hotel"""

    model = HotelAmenity
    template_name = "accounts/hotel_amenity_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy(
            "accounts:hotel_amenity_list", kwargs={"hotel_pk": self.object.hotel.pk}
        )

    def delete(self, request, *args, **kwargs):
        amenity_name = self.get_object().name
        messages.success(request, f"Amenidad '{amenity_name}' eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hotel"] = self.object.hotel
        return context


# ===== HOTEL ROOM VIEWS =====
class HotelRoomListView(StaffRequiredMixin, ListView):
    """Lista de habitaciones de un hotel"""

    model = HotelRoom
    template_name = "accounts/hotel_room_list.html"
    context_object_name = "rooms"
    paginate_by = 20

    def get_queryset(self):
        self.hotel = get_object_or_404(Hotel, pk=self.kwargs["hotel_pk"])
        queryset = HotelRoom.objects.filter(hotel=self.hotel)

        room_type = self.request.GET.get("room_type")
        availability = self.request.GET.get("availability")

        if room_type:
            queryset = queryset.filter(room_type=room_type)

        if availability == "available":
            queryset = queryset.filter(is_available=True)
        elif availability == "unavailable":
            queryset = queryset.filter(is_available=False)

        return queryset.order_by("room_number")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hotel"] = self.hotel
        context["room_type_filter"] = self.request.GET.get("room_type", "")
        context["availability_filter"] = self.request.GET.get("availability", "")
        context["room_types"] = HotelRoom.ROOM_TYPE_CHOICES
        return context


class HotelRoomCreateView(StaffRequiredMixin, CreateView):
    """Agregar nueva habitación al hotel"""

    model = HotelRoom
    template_name = "accounts/hotel_room_form.html"
    fields = [
        "room_number",
        "room_type",
        "capacity",
        "price_per_night",
        "description",
        "is_available",
    ]

    def dispatch(self, request, *args, **kwargs):
        self.hotel = get_object_or_404(Hotel, pk=self.kwargs["hotel_pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.hotel = self.hotel
        messages.success(self.request, f"Habitación {form.instance.room_number} agregada exitosamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("accounts:hotel_room_list", kwargs={"hotel_pk": self.hotel.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hotel"] = self.hotel
        return context


class HotelRoomUpdateView(StaffRequiredMixin, UpdateView):
    """Actualizar habitación del hotel"""

    model = HotelRoom
    template_name = "accounts/hotel_room_form.html"
    fields = [
        "room_number",
        "room_type",
        "capacity",
        "price_per_night",
        "description",
        "is_available",
    ]

    def get_success_url(self):
        return reverse_lazy(
            "accounts:hotel_room_list", kwargs={"hotel_pk": self.object.hotel.pk}
        )

    def form_valid(self, form):
        messages.success(self.request, f"Habitación {form.instance.room_number} actualizada exitosamente.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hotel"] = self.object.hotel
        return context


class HotelRoomDeleteView(StaffRequiredMixin, DeleteView):
    """Eliminar habitación del hotel"""

    model = HotelRoom
    template_name = "accounts/hotel_room_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy(
            "accounts:hotel_room_list", kwargs={"hotel_pk": self.object.hotel.pk}
        )

    def delete(self, request, *args, **kwargs):
        room_number = self.get_object().room_number
        messages.success(request, f"Habitación {room_number} eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hotel"] = self.object.hotel
        return context


# ===== HOTEL SERVICE VIEWS =====
class HotelServiceListView(StaffRequiredMixin, ListView):
    """Lista de servicios adicionales de un hotel"""

    model = HotelService
    template_name = "accounts/hotel_service_list.html"
    context_object_name = "services"
    paginate_by = 20

    def get_queryset(self):
        self.hotel = get_object_or_404(Hotel, pk=self.kwargs["hotel_pk"])
        queryset = HotelService.objects.filter(hotel=self.hotel)

        service_type = self.request.GET.get("service_type")
        status = self.request.GET.get("status")

        if service_type:
            queryset = queryset.filter(service_type=service_type)

        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)

        return queryset.order_by("service_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hotel"] = self.hotel
        context["service_type_filter"] = self.request.GET.get("service_type", "")
        context["status_filter"] = self.request.GET.get("status", "")
        context["service_types"] = HotelService.SERVICE_TYPE_CHOICES
        return context


class HotelServiceCreateView(StaffRequiredMixin, CreateView):
    """Agregar nuevo servicio al hotel"""

    model = HotelService
    template_name = "accounts/hotel_service_form.html"
    fields = [
        "service_name",
        "service_type",
        "description",
        "price",
        "is_per_person",
        "is_per_night",
        "is_active",
    ]

    def dispatch(self, request, *args, **kwargs):
        self.hotel = get_object_or_404(Hotel, pk=self.kwargs["hotel_pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.hotel = self.hotel
        messages.success(self.request, f"Servicio '{form.instance.service_name}' agregado exitosamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("accounts:hotel_service_list", kwargs={"hotel_pk": self.hotel.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hotel"] = self.hotel
        return context


class HotelServiceUpdateView(StaffRequiredMixin, UpdateView):
    """Actualizar servicio del hotel"""

    model = HotelService
    template_name = "accounts/hotel_service_form.html"
    fields = [
        "service_name",
        "service_type",
        "description",
        "price",
        "is_per_person",
        "is_per_night",
        "is_active",
    ]

    def get_success_url(self):
        return reverse_lazy(
            "accounts:hotel_service_list", kwargs={"hotel_pk": self.object.hotel.pk}
        )

    def form_valid(self, form):
        messages.success(self.request, f"Servicio '{form.instance.service_name}' actualizado exitosamente.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hotel"] = self.object.hotel
        return context


class HotelServiceDeleteView(StaffRequiredMixin, DeleteView):
    """Eliminar servicio del hotel"""

    model = HotelService
    template_name = "accounts/hotel_service_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy(
            "accounts:hotel_service_list", kwargs={"hotel_pk": self.object.hotel.pk}
        )

    def delete(self, request, *args, **kwargs):
        service_name = self.get_object().service_name
        messages.success(request, f"Servicio '{service_name}' eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hotel"] = self.object.hotel
        return context

