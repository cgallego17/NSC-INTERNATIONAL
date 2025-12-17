"""
Vistas para gestión de banners del home
"""

from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from apps.core.mixins import StaffRequiredMixin
from .forms import HomeBannerForm, SiteSettingsForm, SponsorForm
from .models import HomeBanner, SiteSettings, Sponsor, DashboardBanner


# ===== HOME BANNER VIEWS =====
class HomeBannerListView(StaffRequiredMixin, ListView):
    """Lista de banners del home"""

    model = HomeBanner
    template_name = "accounts/banner_list.html"
    context_object_name = "banners"
    paginate_by = 20

    def get_queryset(self):
        queryset = HomeBanner.objects.all()
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


class HomeBannerDetailView(StaffRequiredMixin, DetailView):
    """Detalle de un banner"""

    model = HomeBanner
    template_name = "accounts/banner_detail.html"
    context_object_name = "banner"


class HomeBannerCreateView(StaffRequiredMixin, CreateView):
    """Crear un nuevo banner"""

    model = HomeBanner
    form_class = HomeBannerForm
    template_name = "accounts/banner_form.html"
    success_url = reverse_lazy("accounts:home_content_admin")

    def form_valid(self, form):
        messages.success(self.request, "Banner creado exitosamente.")
        return super().form_valid(form)


class HomeBannerUpdateView(StaffRequiredMixin, UpdateView):
    """Editar un banner existente"""

    model = HomeBanner
    form_class = HomeBannerForm
    template_name = "accounts/banner_form.html"
    success_url = reverse_lazy("accounts:home_content_admin")

    def form_valid(self, form):
        messages.success(self.request, "Banner actualizado exitosamente.")
        return super().form_valid(form)


class HomeBannerDeleteView(StaffRequiredMixin, DeleteView):
    """Eliminar un banner"""

    model = HomeBanner
    template_name = "accounts/banner_confirm_delete.html"
    success_url = reverse_lazy("accounts:home_content_admin")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Banner eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)


# ===== SITE SETTINGS VIEWS =====
class SiteSettingsUpdateView(StaffRequiredMixin, UpdateView):
    """Editar configuraciones del sitio"""

    model = SiteSettings
    form_class = SiteSettingsForm
    template_name = "accounts/site_settings_form.html"
    success_url = reverse_lazy("accounts:home_content_admin")

    def get_object(self, queryset=None):
        return SiteSettings.load()

    def form_valid(self, form):
        messages.success(
            self.request, "Configuraciones del sitio actualizadas exitosamente."
        )
        return super().form_valid(form)


class HomeContentAdminView(StaffRequiredMixin, TemplateView):
    """Vista principal de administración de contenido del home"""

    template_name = "accounts/home_content_admin.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Estadísticas de banners
        context["total_banners_count"] = HomeBanner.objects.count()
        context["active_banners_count"] = HomeBanner.objects.filter(
            is_active=True
        ).count()
        context["recent_banners"] = HomeBanner.objects.order_by("-created_at")[:6]

        # Configuraciones del sitio
        context["site_settings"] = SiteSettings.load()

        # Estadísticas de sponsors
        try:
            context["total_sponsors_count"] = Sponsor.objects.count()
            context["active_sponsors_count"] = Sponsor.objects.filter(
                is_active=True
            ).count()
            context["recent_sponsors"] = Sponsor.objects.order_by("-created_at")[:6]
        except:
            context["total_sponsors_count"] = 0
            context["active_sponsors_count"] = 0
            context["recent_sponsors"] = []

        # Estadísticas de banners del dashboard
        try:
            context["total_dashboard_banners_count"] = DashboardBanner.objects.count()
            context["active_dashboard_banners_count"] = DashboardBanner.objects.filter(
                is_active=True
            ).count()
            context["recent_dashboard_banners"] = DashboardBanner.objects.order_by(
                "-created_at"
            )[:6]
        except:
            context["total_dashboard_banners_count"] = 0
            context["active_dashboard_banners_count"] = 0
            context["recent_dashboard_banners"] = []

        return context
