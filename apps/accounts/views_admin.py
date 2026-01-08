"""
Vistas administrativas de órdenes - Solo staff/superuser
"""
from decimal import Decimal

from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView

from apps.core.mixins import StaffRequiredMixin

from .models import Order


class AdminOrderListView(StaffRequiredMixin, ListView):
    """Lista administrativa de órdenes"""

    model = Order
    template_name = "accounts/admin/order_list.html"
    context_object_name = "orders"
    paginate_by = 25

    def get_queryset(self):
        queryset = Order.objects.select_related("user", "event", "stripe_checkout").all()

        # Filtros
        search = self.request.GET.get("search", "")
        status_filter = self.request.GET.get("status", "")
        payment_mode_filter = self.request.GET.get("payment_mode", "")
        date_from = self.request.GET.get("date_from", "")
        date_to = self.request.GET.get("date_to", "")

        if search:
            queryset = queryset.filter(
                Q(order_number__icontains=search)
                | Q(user__username__icontains=search)
                | Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(user__email__icontains=search)
                | Q(stripe_session_id__icontains=search)
            )

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if payment_mode_filter:
            queryset = queryset.filter(payment_mode=payment_mode_filter)

        if date_from:
            try:
                queryset = queryset.filter(created_at__gte=date_from)
            except Exception:
                pass

        if date_to:
            try:
                queryset = queryset.filter(created_at__lte=date_to)
            except Exception:
                pass

        # Ordenamiento
        sort = self.request.GET.get("sort", "-created_at")
        if sort in ["order_number", "-order_number", "created_at", "-created_at", "total_amount", "-total_amount", "status", "-status"]:
            queryset = queryset.order_by(sort)
        else:
            queryset = queryset.order_by("-created_at")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Estadísticas
        all_orders = Order.objects.all()
        context["total_orders"] = all_orders.count()
        context["total_revenue"] = all_orders.filter(status="paid").aggregate(
            Sum("total_amount")
        )["total_amount__sum"] or Decimal("0.00")
        context["pending_orders"] = all_orders.filter(status="pending").count()
        context["paid_orders"] = all_orders.filter(status="paid").count()
        context["cancelled_orders"] = all_orders.filter(status="cancelled").count()
        context["payment_plans"] = all_orders.filter(payment_mode="plan").count()

        # Filtros actuales para mantener en el template
        context["search"] = self.request.GET.get("search", "")
        context["status_filter"] = self.request.GET.get("status", "")
        context["payment_mode_filter"] = self.request.GET.get("payment_mode", "")
        context["date_from"] = self.request.GET.get("date_from", "")
        context["date_to"] = self.request.GET.get("date_to", "")
        context["sort"] = self.request.GET.get("sort", "-created_at")

        # Opciones de filtro
        context["status_choices"] = Order.ORDER_STATUS_CHOICES
        context["payment_mode_choices"] = [
            ("plan", "Plan de Pagos"),
            ("now", "Pago Único"),
        ]

        # Marcar como vista admin
        context["is_admin"] = True

        return context


class AdminOrderDetailView(StaffRequiredMixin, DetailView):
    """Detalle administrativo de orden"""

    model = Order
    template_name = "accounts/admin/order_detail.html"
    context_object_name = "order"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        order = self.object

        # 1. Información de jugadores registrados
        if order.registered_player_ids:
            from apps.accounts.models import Player
            context["registered_players"] = list(Player.objects.filter(
                id__in=order.registered_player_ids
            ).select_related('user', 'team', 'user__profile'))
        else:
            context["registered_players"] = []

        # 2. Reservas de hotel - CARGA EXPLÍCITA CON DETALLES
        hotel_res_queryset = order.hotel_reservations.select_related(
            "hotel", "room", "user", "user__profile"
        )

        hotel_reservations_data = []
        for res in hotel_res_queryset:
            # Forzamos la carga de propiedades para que estén disponibles en el template
            # Usar additional_guest_details_json directamente ya que es el campo fuente
            res.extra_guests = res.additional_guest_details
            # Asegurar que additional_guest_details_json esté disponible como lista
            if res.additional_guest_details_json:
                # Ya es una lista de diccionarios, no necesita procesamiento
                pass
            hotel_reservations_data.append(res)

        context["hotel_reservations"] = hotel_reservations_data
        context["actual_hotel_reservations"] = hotel_res_queryset
        context["has_hotel_reservations"] = len(hotel_reservations_data) > 0

        # Debug: Asegurar que la lista no sea None
        if context["hotel_reservations"] is None:
            context["hotel_reservations"] = []

        # Información del plan de pagos
        if order.is_payment_plan:
            context["payment_plan_summary"] = order.payment_plan_summary

        # Breakdown de Stripe (JSON organizado)
        context["breakdown"] = order.breakdown or {}

        # Breakdown del checkout de Stripe (si existe)
        if order.stripe_checkout:
            context["stripe_checkout_breakdown"] = order.stripe_checkout.breakdown or {}
            context["stripe_checkout_hotel_cart"] = order.stripe_checkout.hotel_cart_snapshot or {}

        # Marcar como vista admin
        context["is_admin"] = True

        return context

