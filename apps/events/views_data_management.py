"""
Vistas para gestión de datos maestros (EventContact, EventType, GateFeeType)
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from apps.core.mixins import StaffRequiredMixin

from .forms import EventContactForm, EventTypeForm, GateFeeTypeForm
from .models import EventContact, EventType, GateFeeType


# ===== EVENT CONTACT VIEWS =====
class EventContactListView(StaffRequiredMixin, ListView):
    model = EventContact
    template_name = "events/eventcontact_list.html"
    context_object_name = "contacts"
    paginate_by = 20

    def get_queryset(self):
        queryset = EventContact.objects.select_related("country", "state", "city")
        search = self.request.GET.get("search")
        status = self.request.GET.get("status")
        country = self.request.GET.get("country")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(email__icontains=search)
                | Q(phone__icontains=search)
            )
        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)
        if country:
            queryset = queryset.filter(country_id=country)

        return queryset.order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["status_filter"] = self.request.GET.get("status", "")
        context["active_section"] = "contacts"
        context["active_subsection"] = "contact_list"
        return context


class EventContactDetailView(StaffRequiredMixin, DetailView):
    model = EventContact
    template_name = "events/eventcontact_detail.html"
    context_object_name = "contact"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "contacts"
        context["active_subsection"] = "contact_list"
        return context


class EventContactCreateView(StaffRequiredMixin, CreateView):
    model = EventContact
    form_class = EventContactForm
    template_name = "events/eventcontact_form.html"
    success_url = reverse_lazy("events:eventcontact_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "contacts"
        context["active_subsection"] = "contact_create"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Contacto creado exitosamente.")
        return super().form_valid(form)


class EventContactUpdateView(StaffRequiredMixin, UpdateView):
    model = EventContact
    form_class = EventContactForm
    template_name = "events/eventcontact_form.html"
    success_url = reverse_lazy("events:eventcontact_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "contacts"
        context["active_subsection"] = "contact_list"
        # Pasar datos del objeto para inicializar JavaScript
        if self.object:
            context["initial_country_id"] = self.object.country_id
            context["initial_state_id"] = self.object.state_id
            context["initial_city_id"] = self.object.city_id
        return context

    def form_valid(self, form):
        messages.success(self.request, "Contacto actualizado exitosamente.")
        return super().form_valid(form)


class EventContactDeleteView(StaffRequiredMixin, DeleteView):
    model = EventContact
    template_name = "events/eventcontact_confirm_delete.html"
    success_url = reverse_lazy("events:eventcontact_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "contacts"
        context["active_subsection"] = "contact_list"
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Contacto eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)


# ===== EVENT TYPE VIEWS =====
class EventTypeListView(StaffRequiredMixin, ListView):
    model = EventType
    template_name = "events/eventtype_list.html"
    context_object_name = "event_types"
    paginate_by = 20

    def get_queryset(self):
        queryset = EventType.objects.all()
        search = self.request.GET.get("search")
        status = self.request.GET.get("status")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)

        return queryset.order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["status_filter"] = self.request.GET.get("status", "")
        context["active_section"] = "data_management"
        context["active_subsection"] = "event_types"
        return context


class EventTypeDetailView(StaffRequiredMixin, DetailView):
    model = EventType
    template_name = "events/eventtype_detail.html"
    context_object_name = "event_type"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "data_management"
        context["active_subsection"] = "event_types"
        return context


class EventTypeCreateView(StaffRequiredMixin, CreateView):
    model = EventType
    form_class = EventTypeForm
    template_name = "events/eventtype_form.html"
    success_url = reverse_lazy("events:eventtype_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "data_management"
        context["active_subsection"] = "event_types"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Tipo de evento creado exitosamente.")
        return super().form_valid(form)


class EventTypeUpdateView(StaffRequiredMixin, UpdateView):
    model = EventType
    form_class = EventTypeForm
    template_name = "events/eventtype_form.html"
    success_url = reverse_lazy("events:eventtype_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "data_management"
        context["active_subsection"] = "event_types"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Tipo de evento actualizado exitosamente.")
        return super().form_valid(form)


class EventTypeDeleteView(StaffRequiredMixin, DeleteView):
    model = EventType
    template_name = "events/eventtype_confirm_delete.html"
    success_url = reverse_lazy("events:eventtype_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "data_management"
        context["active_subsection"] = "event_types"
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Tipo de evento eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)


# ===== GATE FEE TYPE VIEWS =====
class GateFeeTypeListView(StaffRequiredMixin, ListView):
    model = GateFeeType
    template_name = "events/gatefeetype_list.html"
    context_object_name = "gate_fee_types"
    paginate_by = 20

    def get_queryset(self):
        queryset = GateFeeType.objects.all()
        search = self.request.GET.get("search")
        status = self.request.GET.get("status")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)

        return queryset.order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["status_filter"] = self.request.GET.get("status", "")
        context["active_section"] = "data_management"
        context["active_subsection"] = "gate_fee_types"
        return context


class GateFeeTypeDetailView(StaffRequiredMixin, DetailView):
    model = GateFeeType
    template_name = "events/gatefeetype_detail.html"
    context_object_name = "gate_fee_type"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "data_management"
        context["active_subsection"] = "gate_fee_types"
        return context


class GateFeeTypeCreateView(StaffRequiredMixin, CreateView):
    model = GateFeeType
    form_class = GateFeeTypeForm
    template_name = "events/gatefeetype_form.html"
    success_url = reverse_lazy("events:gatefeetype_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "data_management"
        context["active_subsection"] = "gate_fee_types"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Tipo de gate fee creado exitosamente.")
        return super().form_valid(form)


class GateFeeTypeUpdateView(StaffRequiredMixin, UpdateView):
    model = GateFeeType
    form_class = GateFeeTypeForm
    template_name = "events/gatefeetype_form.html"
    success_url = reverse_lazy("events:gatefeetype_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "data_management"
        context["active_subsection"] = "gate_fee_types"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Tipo de gate fee actualizado exitosamente.")
        return super().form_valid(form)


class GateFeeTypeDeleteView(StaffRequiredMixin, DeleteView):
    model = GateFeeType
    template_name = "events/gatefeetype_confirm_delete.html"
    success_url = reverse_lazy("events:gatefeetype_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "data_management"
        context["active_subsection"] = "gate_fee_types"
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Tipo de gate fee eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)






