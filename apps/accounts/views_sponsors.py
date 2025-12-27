"""
Vistas para gestión de sponsors
"""

from django.contrib import messages
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
from .forms import SponsorForm
from .models import Sponsor


# ===== SPONSOR VIEWS =====
class SponsorListView(StaffRequiredMixin, ListView):
    """Lista de sponsors"""

    model = Sponsor
    template_name = "accounts/sponsor_list.html"
    context_object_name = "sponsors"
    paginate_by = 20

    def get_queryset(self):
        queryset = Sponsor.objects.all()
        search = self.request.GET.get("search")
        status = self.request.GET.get("status")

        if search:
            queryset = queryset.filter(Q(name__icontains=search))

        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)

        return queryset.order_by("order", "name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["status_filter"] = self.request.GET.get("status", "")
        return context


class SponsorDetailView(StaffRequiredMixin, DetailView):
    """Detalle de un sponsor"""

    model = Sponsor
    template_name = "accounts/sponsor_detail.html"
    context_object_name = "sponsor"


class SponsorCreateView(StaffRequiredMixin, CreateView):
    """Crear un nuevo sponsor"""

    model = Sponsor
    form_class = SponsorForm
    template_name = "accounts/sponsor_form.html"
    success_url = reverse_lazy("accounts:home_content_admin")

    def form_valid(self, form):
        messages.success(self.request, "Sponsor creado exitosamente.")
        return super().form_valid(form)


class SponsorUpdateView(StaffRequiredMixin, UpdateView):
    """Editar un sponsor existente"""

    model = Sponsor
    form_class = SponsorForm
    template_name = "accounts/sponsor_form.html"
    success_url = reverse_lazy("accounts:home_content_admin")

    def form_valid(self, form):
        messages.success(self.request, "Sponsor actualizado exitosamente.")
        return super().form_valid(form)


class SponsorDeleteView(StaffRequiredMixin, DeleteView):
    """Eliminar un sponsor"""

    model = Sponsor
    template_name = "accounts/sponsor_confirm_delete.html"
    success_url = reverse_lazy("accounts:home_content_admin")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Sponsor eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)





