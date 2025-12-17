"""
Vistas para gestión de banners del dashboard
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
from .forms_dashboard_banners import DashboardBannerForm
from .models import DashboardBanner


# ===== DASHBOARD BANNER VIEWS =====
class DashboardBannerListView(StaffRequiredMixin, ListView):
    """Lista de banners del dashboard"""

    model = DashboardBanner
    template_name = "accounts/dashboard_banner_list.html"
    context_object_name = "banners"
    paginate_by = 20

    def get_queryset(self):
        queryset = DashboardBanner.objects.all()
        search = self.request.GET.get("search")
        status = self.request.GET.get("status")
        banner_type = self.request.GET.get("banner_type")

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)

        if banner_type:
            queryset = queryset.filter(banner_type=banner_type)

        return queryset.order_by("order", "-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["status_filter"] = self.request.GET.get("status", "")
        context["banner_type_filter"] = self.request.GET.get("banner_type", "")
        return context


class DashboardBannerDetailView(StaffRequiredMixin, DetailView):
    """Detalle de un banner del dashboard"""

    model = DashboardBanner
    template_name = "accounts/dashboard_banner_detail.html"
    context_object_name = "banner"


class DashboardBannerCreateView(StaffRequiredMixin, CreateView):
    """Crear un nuevo banner del dashboard"""

    model = DashboardBanner
    form_class = DashboardBannerForm
    template_name = "accounts/dashboard_banner_form.html"
    success_url = reverse_lazy("accounts:home_content_admin")

    def form_valid(self, form):
        messages.success(self.request, "Banner del panel creado exitosamente.")
        return super().form_valid(form)


class DashboardBannerUpdateView(StaffRequiredMixin, UpdateView):
    """Editar un banner del dashboard existente"""

    model = DashboardBanner
    form_class = DashboardBannerForm
    template_name = "accounts/dashboard_banner_form.html"
    success_url = reverse_lazy("accounts:home_content_admin")

    def form_valid(self, form):
        messages.success(self.request, "Banner del panel actualizado exitosamente.")
        return super().form_valid(form)


class DashboardBannerDeleteView(StaffRequiredMixin, DeleteView):
    """Eliminar un banner del dashboard"""

    model = DashboardBanner
    template_name = "accounts/dashboard_banner_confirm_delete.html"
    success_url = reverse_lazy("accounts:home_content_admin")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Banner del panel eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)


