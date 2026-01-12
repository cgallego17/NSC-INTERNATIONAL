"""
Vistas administrativas de órdenes - Solo staff/superuser
"""

import json
from datetime import timedelta
from decimal import Decimal

from django import forms
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Avg, F, Q, Sum
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView, ListView

from apps.core.mixins import StaffRequiredMixin

from .models import Order, StaffWalletTopUp, UserWallet, WalletTransaction


class AdminOrderListView(StaffRequiredMixin, ListView):
    """Lista administrativa de órdenes"""

    model = Order
    template_name = "accounts/admin/order_list.html"
    context_object_name = "orders"
    paginate_by = 25

    def get_queryset(self):
        queryset = Order.objects.select_related(
            "user", "event", "stripe_checkout"
        ).all()

        # Filtros
        search = self.request.GET.get("search", "")
        status_filter = self.request.GET.get("status", "")
        payment_mode_filter = self.request.GET.get("payment_mode", "")
        payment_method_filter = self.request.GET.get("payment_method", "")
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

        if payment_method_filter:
            queryset = queryset.filter(payment_method=payment_method_filter)

        if date_from:
            try:
                queryset = queryset.filter(created_at__date__gte=date_from)
            except Exception:
                pass

        if date_to:
            try:
                queryset = queryset.filter(created_at__date__lte=date_to)
            except Exception:
                pass

        # Ordenamiento (por defecto: más recientes primero)
        sort = self.request.GET.get("sort", "-created_at")
        if sort:
            queryset = queryset.order_by(sort)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Filtros actuales
        context["search"] = self.request.GET.get("search", "")
        context["status_filter"] = self.request.GET.get("status", "")
        context["payment_mode_filter"] = self.request.GET.get("payment_mode", "")
        context["payment_method_filter"] = self.request.GET.get("payment_method", "")
        context["date_from"] = self.request.GET.get("date_from", "")
        context["date_to"] = self.request.GET.get("date_to", "")
        context["sort"] = self.request.GET.get("sort", "-created_at")

        # Opciones para los filtros
        context["status_choices"] = Order.ORDER_STATUS_CHOICES
        # Order.payment_mode field choices (inline, not a constant)
        context["payment_mode_choices"] = [
            ("plan", "Plan de Pagos"),
            ("now", "Pago Único"),
            ("register_only", "Registrar ahora, pagar después"),
        ]
        context["payment_method_choices"] = Order.PAYMENT_METHOD_CHOICES

        # Estadísticas
        all_orders = Order.objects.all()
        context["total_orders"] = all_orders.count()
        context["total_revenue"] = all_orders.filter(status="paid").aggregate(
            Sum("total_amount")
        )["total_amount__sum"] or Decimal("0.00")
        context["paid_orders"] = all_orders.filter(status="paid").count()
        context["payment_plans"] = all_orders.filter(
            payment_mode="payment_plan"
        ).count()
        context["pending_registration_orders"] = all_orders.filter(
            status="pending_registration"
        ).count()

        context["is_admin"] = True
        return context


class AdminOrderDetailView(StaffRequiredMixin, DetailView):
    """Vista de detalle de orden"""

    model = Order
    template_name = "accounts/admin/order_detail.html"
    context_object_name = "order"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = True
        return context


class AdminWalletTopUpForm(forms.ModelForm):
    user_id = forms.IntegerField(required=True, widget=forms.HiddenInput())

    class Meta:
        model = StaffWalletTopUp
        fields = ["amount", "description"]
        widgets = {
            "description": forms.TextInput(
                attrs={
                    "placeholder": "Reason / note (optional)",
                }
            )
        }

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is None or amount <= 0:
            raise forms.ValidationError("Amount must be greater than 0.")
        return amount

    def clean_user_id(self):
        user_id = self.cleaned_data.get("user_id")
        try:
            user = User.objects.get(id=user_id, is_active=True)
            return user_id
        except User.DoesNotExist:
            raise forms.ValidationError("Selected user does not exist or is inactive.")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bootstrap-ish classes to match existing admin dashboard styling
        for _name, field in self.fields.items():
            css = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (css + " form-control").strip()

    def save(self, commit=True):
        instance = super().save(commit=False)
        user_id = self.cleaned_data.get("user_id")
        instance.user = User.objects.get(id=user_id)
        if commit:
            instance.save()
        return instance


@require_http_methods(["GET"])
def search_users_ajax(request):
    """AJAX endpoint para buscar usuarios por nombre o correo"""
    if not request.user.is_staff:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    query = request.GET.get("q", "").strip()
    if len(query) < 2:
        return JsonResponse({"users": []})

    users = User.objects.filter(is_active=True).filter(
        Q(username__icontains=query)
        | Q(first_name__icontains=query)
        | Q(last_name__icontains=query)
        | Q(email__icontains=query)
    )[:20]

    results = []
    for user in users:
        results.append(
            {
                "id": user.id,
                "username": user.username,
                "full_name": user.get_full_name() or user.username,
                "email": user.email,
            }
        )

    return JsonResponse({"users": results})


class AdminWalletTopUpListView(StaffRequiredMixin, ListView):
    """
    Custom admin dashboard page to create staff wallet top-ups and view history.
    """

    model = StaffWalletTopUp
    template_name = "accounts/admin/wallet_topups.html"
    context_object_name = "topups"
    paginate_by = 25

    def get_queryset(self):
        # Filter out any objects without created_by (shouldn't happen, but safety first)
        qs = StaffWalletTopUp.objects.select_related("user", "created_by").filter(
            created_by__isnull=False
        )

        search = (self.request.GET.get("search") or "").strip()
        created_by = (self.request.GET.get("created_by") or "").strip()
        date_from = (self.request.GET.get("date_from") or "").strip()
        date_to = (self.request.GET.get("date_to") or "").strip()

        if search:
            qs = qs.filter(
                Q(user__username__icontains=search)
                | Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(user__email__icontains=search)
            )
        if created_by:
            qs = qs.filter(created_by__username__icontains=created_by)
        if date_from:
            try:
                qs = qs.filter(created_at__date__gte=date_from)
            except Exception:
                pass
        if date_to:
            try:
                qs = qs.filter(created_at__date__lte=date_to)
            except Exception:
                pass

        return qs.order_by("-created_at")

    def post(self, request, *args, **kwargs):
        form = AdminWalletTopUpForm(request.POST)
        if form.is_valid():
            # Create StaffWalletTopUp with created_by set before save
            obj = form.save(commit=False)
            obj.created_by = request.user
            # Save will trigger _apply_credit which creates the wallet transaction
            obj.save()

            # Fetch resulting balance for message (best-effort)
            balance = None
            try:
                balance = UserWallet.objects.get(user=obj.user).balance
            except Exception:
                pass

            if balance is not None:
                messages.success(
                    request,
                    f"Wallet credited successfully. New balance: ${balance}",
                )
            else:
                messages.success(request, "Wallet credited successfully.")
            return redirect("accounts:admin_wallet_topups")

        # Render page with errors
        self.object_list = self.get_queryset()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["form"] = kwargs.get("form") or AdminWalletTopUpForm()
        context["search"] = self.request.GET.get("search", "")
        context["created_by_filter"] = self.request.GET.get("created_by", "")
        context["date_from"] = self.request.GET.get("date_from", "")
        context["date_to"] = self.request.GET.get("date_to", "")

        # Stats - All time (only count objects with created_by to avoid RelatedObjectDoesNotExist)
        all_topups = StaffWalletTopUp.objects.filter(created_by__isnull=False)
        context["total_topups"] = all_topups.count()
        context["total_amount"] = all_topups.aggregate(Sum("amount"))[
            "amount__sum"
        ] or Decimal("0.00")
        context["average_amount"] = all_topups.aggregate(Avg("amount"))[
            "amount__avg"
        ] or Decimal("0.00")

        # Stats - This month
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        this_month_topups = all_topups.filter(created_at__gte=start_of_month)
        context["this_month_count"] = this_month_topups.count()
        context["this_month_amount"] = this_month_topups.aggregate(Sum("amount"))[
            "amount__sum"
        ] or Decimal("0.00")

        # Stats - Last month
        if start_of_month.month == 1:
            last_month_start = start_of_month.replace(
                year=start_of_month.year - 1, month=12
            )
        else:
            last_month_start = start_of_month.replace(month=start_of_month.month - 1)
        last_month_end = start_of_month - timedelta(microseconds=1)
        last_month_topups = all_topups.filter(
            created_at__gte=last_month_start, created_at__lte=last_month_end
        )
        context["last_month_count"] = last_month_topups.count()
        context["last_month_amount"] = last_month_topups.aggregate(Sum("amount"))[
            "amount__sum"
        ] or Decimal("0.00")

        # Attach balance_after from WalletTransaction by reference_id = staff_topup:<pk>
        # Get topups from context (ListView provides them via context_object_name="topups")
        topups = list(context.get("topups", []))
        ref_ids = [f"staff_topup:{t.pk}" for t in topups if t.pk]
        tx_map = {}
        if ref_ids:
            for tx in WalletTransaction.objects.filter(
                reference_id__in=ref_ids
            ).select_related("wallet", "wallet__user"):
                tx_map[tx.reference_id] = tx

        for t in topups:
            t.balance_after = None
            ref = f"staff_topup:{t.pk}"
            tx = tx_map.get(ref)
            if tx:
                t.balance_after = tx.balance_after

        context["is_admin"] = True
        return context
