"""
Vistas administrativas de órdenes - Solo staff/superuser
"""

from datetime import timedelta
from decimal import Decimal, InvalidOperation

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db.models import Avg, Q, Sum
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.html import strip_tags
from django.views.decorators.http import require_http_methods
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from apps.core.mixins import StaffRequiredMixin
from apps.events.models import Division, EventAttendance
from apps.locations.models import City, Country, State

from .forms import AdminEmailBroadcastForm, AdminTeamForm, AdminTodoForm
from .models import (
    AdminEmailBroadcast,
    AdminTodo,
    Order,
    Player,
    StaffWalletTopUp,
    StripeEventCheckout,
    Team,
    UserWallet,
    WalletTransaction,
)

ADMIN_EMAIL_RECIPIENT_WARNING_THRESHOLD = 250


def _get_admin_broadcast_recipients(form):
    """Return a list of recipient emails based on form filters.

    Spectators: only by location.
    Parents/Managers: by location and optionally division.
    """

    send_to_parents = bool(form.cleaned_data.get("send_to_parents"))
    send_to_managers = bool(form.cleaned_data.get("send_to_managers"))
    send_to_spectators = bool(form.cleaned_data.get("send_to_spectators"))

    countries = getattr(form, "_countries", None) or form.cleaned_data.get("country")
    states = getattr(form, "_states", None) or form.cleaned_data.get("state")
    cities = getattr(form, "_cities", None) or form.cleaned_data.get("city")
    divisions = getattr(form, "_divisions", None) or form.cleaned_data.get("division")

    emails = set()

    def apply_location_filters(qs):
        if countries:
            qs = qs.filter(profile__country__in=countries)
        if states:
            qs = qs.filter(profile__state__in=states)
        if cities:
            qs = qs.filter(profile__city__in=cities)
        return qs

    def eligible_profile_location_required(qs):
        # If a location filter is applied, users missing that field are excluded automatically
        # by the FK equality filters above. This extra guard keeps semantics clear.
        if countries:
            qs = qs.exclude(profile__country__isnull=True)
        if states:
            qs = qs.exclude(profile__state__isnull=True)
        if cities:
            qs = qs.exclude(profile__city__isnull=True)
        return qs

    if send_to_spectators:
        qs = (
            User.objects.filter(profile__user_type="spectator")
            .select_related("profile")
            .distinct()
        )
        qs = apply_location_filters(qs)
        qs = eligible_profile_location_required(qs)
        for u in qs:
            if (u.email or "").strip():
                emails.add(u.email.strip())

    if send_to_parents:
        qs = (
            User.objects.filter(profile__user_type="parent")
            .select_related("profile")
            .distinct()
        )
        qs = apply_location_filters(qs)
        qs = eligible_profile_location_required(qs)
        if divisions:
            qs = qs.filter(children__player__division__in=divisions)
        for u in qs:
            if (u.email or "").strip():
                emails.add(u.email.strip())

    if send_to_managers:
        qs = (
            User.objects.filter(profile__user_type="team_manager")
            .select_related("profile")
            .distinct()
        )
        qs = apply_location_filters(qs)
        qs = eligible_profile_location_required(qs)
        if divisions:
            qs = qs.filter(managed_teams__players__division__in=divisions)
        for u in qs:
            if (u.email or "").strip():
                emails.add(u.email.strip())

    return sorted(emails)


def _send_admin_broadcast_email(request, subject, html_body, recipients):
    if not recipients:
        return 0

    wrapped_html_body = render_to_string(
        "emails/admin_broadcast_wrapper.html",
        {
            "subject": subject,
            "content_html": html_body,
            "brand_name": "NCS International",
            "email_tag": "Email Broadcast",
        },
    )

    from_email = (
        getattr(settings, "DEFAULT_FROM_EMAIL", None)
        or "NCS INTERNATIONAL <no-reply@localhost>"
    )
    safe_to = (request.user.email or "").strip() or "no-reply@localhost"

    message_text = strip_tags(wrapped_html_body or "")
    if not message_text.strip():
        message_text = subject

    email = EmailMultiAlternatives(
        subject=subject,
        body=message_text,
        from_email=from_email,
        to=[safe_to],
        bcc=recipients,
    )
    email.attach_alternative(wrapped_html_body, "text/html")
    email.send(fail_silently=False)
    return len(recipients)


class AdminEmailBroadcastListView(StaffRequiredMixin, ListView):
    model = AdminEmailBroadcast
    template_name = "accounts/admin/email_broadcast_list.html"
    context_object_name = "broadcasts"
    paginate_by = 25

    def get_queryset(self):
        return (
            AdminEmailBroadcast.objects.select_related(
                "created_by", "country", "state", "city", "division"
            )
            .all()
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = True
        return context


class AdminEmailBroadcastDetailView(StaffRequiredMixin, DetailView):
    model = AdminEmailBroadcast
    template_name = "accounts/admin/email_broadcast_detail.html"
    context_object_name = "broadcast"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = True

        broadcast = context.get("broadcast")
        if broadcast:
            country_ids = getattr(broadcast, "country_ids", None) or (
                [] if not broadcast.country_id else [broadcast.country_id]
            )
            state_ids = getattr(broadcast, "state_ids", None) or (
                [] if not broadcast.state_id else [broadcast.state_id]
            )
            city_ids = getattr(broadcast, "city_ids", None) or (
                [] if not broadcast.city_id else [broadcast.city_id]
            )
            division_ids = getattr(broadcast, "division_ids", None) or (
                [] if not broadcast.division_id else [broadcast.division_id]
            )

            context["filter_countries"] = Country.objects.filter(
                id__in=country_ids
            ).order_by("name")
            context["filter_states"] = State.objects.filter(id__in=state_ids).order_by(
                "name"
            )
            context["filter_cities"] = City.objects.filter(id__in=city_ids).order_by(
                "name"
            )
            context["filter_divisions"] = Division.objects.filter(
                id__in=division_ids
            ).order_by("name")

        return context


class AdminEmailBroadcastSendView(StaffRequiredMixin, CreateView):
    model = AdminEmailBroadcast
    form_class = AdminEmailBroadcastForm
    template_name = "accounts/admin/email_send.html"

    def form_valid(self, form):
        subject = (form.cleaned_data.get("subject") or "").strip()
        html_body = form.cleaned_data.get("html_body") or ""

        if not (
            form.cleaned_data.get("send_to_parents")
            or form.cleaned_data.get("send_to_managers")
            or form.cleaned_data.get("send_to_spectators")
        ):
            form.add_error(None, "Selecciona al menos un tipo de destinatario.")
            return self.form_invalid(form)

        recipients = _get_admin_broadcast_recipients(form)
        if not recipients:
            form.add_error(
                None, "No se encontraron destinatarios con los filtros seleccionados."
            )
            return self.form_invalid(form)

        if len(recipients) >= ADMIN_EMAIL_RECIPIENT_WARNING_THRESHOLD:
            messages.warning(
                self.request,
                f"Vas a enviar este correo a {len(recipients)} destinatarios. Esta acción es sincrónica y puede tardar.",
            )

        countries = getattr(form, "_countries", None) or form.cleaned_data.get(
            "country"
        )
        states = getattr(form, "_states", None) or form.cleaned_data.get("state")
        cities = getattr(form, "_cities", None) or form.cleaned_data.get("city")
        divisions = getattr(form, "_divisions", None) or form.cleaned_data.get(
            "division"
        )

        form.instance.country_ids = (
            list(countries.values_list("id", flat=True))
            if hasattr(countries, "values_list")
            else ([] if not countries else [countries.id])
        )
        form.instance.state_ids = (
            list(states.values_list("id", flat=True))
            if hasattr(states, "values_list")
            else ([] if not states else [states.id])
        )
        form.instance.city_ids = (
            list(cities.values_list("id", flat=True))
            if hasattr(cities, "values_list")
            else ([] if not cities else [cities.id])
        )
        form.instance.division_ids = (
            list(divisions.values_list("id", flat=True))
            if hasattr(divisions, "values_list")
            else ([] if not divisions else [divisions.id])
        )

        # FK legacy fields are now handled by AdminEmailBroadcastForm.clean() (single instance).

        form.instance.created_by = self.request.user
        form.instance.total_recipients = len(recipients)
        form.instance.recipient_emails = recipients

        response = super().form_valid(form)

        try:
            sent_count = _send_admin_broadcast_email(
                self.request,
                subject=subject,
                html_body=html_body,
                recipients=recipients,
            )
            messages.success(
                self.request, f"Correo enviado a {sent_count} destinatarios."
            )
        except Exception:
            messages.error(
                self.request,
                "No se pudo enviar el correo. Verifica la configuración de email.",
            )

        return response

    def get_success_url(self):
        return reverse_lazy("accounts:admin_email_broadcast_list")


def _send_todo_assigned_email(request, todo_obj):
    assigned_to = getattr(todo_obj, "assigned_to", None)
    if not assigned_to:
        return
    to_email = (assigned_to.email or "").strip()
    if not to_email:
        return

    try:
        url = request.build_absolute_uri(
            reverse("accounts:admin_todo_detail", kwargs={"pk": todo_obj.pk})
        )
        subject = f"To-Do asignado: {todo_obj.title}"
        message_text = (
            f"Se te ha asignado un To-Do en el dashboard.\n\n"
            f"Título: {todo_obj.title}\n"
            f"Estado: {todo_obj.get_status_display()}\n"
            f"Prioridad: {todo_obj.get_priority_display()}\n\n"
            f"Ver detalle: {url}\n"
        )

        message_html = f"""
        <div style=\"font-family: Arial, Helvetica, sans-serif; line-height: 1.5;\">
          <h2 style=\"margin: 0 0 12px;\">To-Do asignado</h2>
          <p style=\"margin: 0 0 12px;\">Se te ha asignado un To-Do en el dashboard.</p>
          <table style=\"border-collapse: collapse; margin: 0 0 16px;\">
            <tr><td style=\"padding: 4px 12px 4px 0; font-weight: 700;\">Título:</td><td style=\"padding: 4px 0;\">{todo_obj.title}</td></tr>
            <tr><td style=\"padding: 4px 12px 4px 0; font-weight: 700;\">Estado:</td><td style=\"padding: 4px 0;\">{todo_obj.get_status_display()}</td></tr>
            <tr><td style=\"padding: 4px 12px 4px 0; font-weight: 700;\">Prioridad:</td><td style=\"padding: 4px 0;\">{todo_obj.get_priority_display()}</td></tr>
          </table>
          <p style=\"margin: 0 0 12px;\">
            <a href=\"{url}\" style=\"display: inline-block; padding: 10px 14px; background: #0d2c54; color: #ffffff; text-decoration: none; border-radius: 6px;\">Ver To-Do</a>
          </p>
          <p style=\"margin: 24px 0 0; color: #6c757d; font-size: 12px;\">NCS INTERNATIONAL</p>
        </div>
        """

        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
        if not from_email:
            from_email = "NCS INTERNATIONAL <no-reply@localhost>"
        email = EmailMultiAlternatives(
            subject=subject,
            body=message_text,
            from_email=from_email,
            to=[to_email],
        )
        email.attach_alternative(message_html, "text/html")
        email.send(fail_silently=False)
    except Exception:
        messages.warning(
            request,
            "No se pudo enviar el correo de asignación del To-Do. Verifica la configuración de email.",
        )


def _send_todo_completed_email(request, todo_obj, completed_by_user):
    created_by = getattr(todo_obj, "created_by", None)
    if not created_by:
        return
    to_email = (created_by.email or "").strip()
    if not to_email:
        return

    try:
        url = request.build_absolute_uri(
            reverse("accounts:admin_todo_detail", kwargs={"pk": todo_obj.pk})
        )
        completed_by_name = (
            completed_by_user.get_full_name() or completed_by_user.username
            if completed_by_user
            else "-"
        )
        subject = f"To-Do completado: {todo_obj.title}"
        message_text = (
            f"Tu To-Do ha sido marcado como completado.\n\n"
            f"Título: {todo_obj.title}\n"
            f"Completado por: {completed_by_name}\n\n"
            f"Ver detalle: {url}\n"
        )

        message_html = f"""
        <div style=\"font-family: Arial, Helvetica, sans-serif; line-height: 1.5;\">
          <h2 style=\"margin: 0 0 12px;\">To-Do completado</h2>
          <p style=\"margin: 0 0 12px;\">Tu To-Do ha sido marcado como completado.</p>
          <table style=\"border-collapse: collapse; margin: 0 0 16px;\">
            <tr><td style=\"padding: 4px 12px 4px 0; font-weight: 700;\">Título:</td><td style=\"padding: 4px 0;\">{todo_obj.title}</td></tr>
            <tr><td style=\"padding: 4px 12px 4px 0; font-weight: 700;\">Completado por:</td><td style=\"padding: 4px 0;\">{completed_by_name}</td></tr>
          </table>
          <p style=\"margin: 0 0 12px;\">
            <a href=\"{url}\" style=\"display: inline-block; padding: 10px 14px; background: #0d2c54; color: #ffffff; text-decoration: none; border-radius: 6px;\">Ver To-Do</a>
          </p>
          <p style=\"margin: 24px 0 0; color: #6c757d; font-size: 12px;\">NCS INTERNATIONAL</p>
        </div>
        """

        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
        if not from_email:
            from_email = "NCS INTERNATIONAL <no-reply@localhost>"
        email = EmailMultiAlternatives(
            subject=subject,
            body=message_text,
            from_email=from_email,
            to=[to_email],
        )
        email.attach_alternative(message_html, "text/html")
        email.send(fail_silently=False)
    except Exception:
        messages.warning(
            request,
            "No se pudo enviar el correo de finalización del To-Do. Verifica la configuración de email.",
        )


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


class AdminTeamDetailView(StaffRequiredMixin, DetailView):
    model = Team
    template_name = "accounts/admin/team_detail.html"
    context_object_name = "team"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = self.object

        context["players"] = (
            Player.objects.filter(team=team)
            .select_related("user", "division")
            .order_by("user__last_name", "user__first_name")
        )
        context["is_admin"] = True
        return context


class AdminTeamListView(StaffRequiredMixin, ListView):
    model = Team
    template_name = "accounts/admin/team_list.html"
    context_object_name = "teams"
    paginate_by = 25

    def get_queryset(self):
        qs = Team.objects.select_related("manager", "city", "state", "country").all()
        search = (self.request.GET.get("search") or "").strip()
        is_active = (self.request.GET.get("is_active") or "").strip()

        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(manager__username__icontains=search)
                | Q(manager__first_name__icontains=search)
                | Q(manager__last_name__icontains=search)
                | Q(manager__email__icontains=search)
            )

        if is_active in ("0", "1"):
            qs = qs.filter(is_active=(is_active == "1"))

        return qs.order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["is_active_filter"] = self.request.GET.get("is_active", "")
        context["is_admin"] = True
        return context


class AdminTeamCreateView(StaffRequiredMixin, CreateView):
    model = Team
    form_class = AdminTeamForm
    template_name = "accounts/admin/team_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Team created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("accounts:admin_team_list")


class AdminTodoListView(StaffRequiredMixin, ListView):
    model = AdminTodo
    template_name = "accounts/admin/todo_list.html"
    context_object_name = "todos"
    paginate_by = 25

    def get_queryset(self):
        qs = AdminTodo.objects.select_related("assigned_to", "created_by").all()
        search = (self.request.GET.get("search") or "").strip()
        status = (self.request.GET.get("status") or "").strip()
        priority = (self.request.GET.get("priority") or "").strip()

        if search:
            qs = qs.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        if status:
            qs = qs.filter(status=status)

        if priority:
            qs = qs.filter(priority=priority)

        return qs.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["status_filter"] = self.request.GET.get("status", "")
        context["priority_filter"] = self.request.GET.get("priority", "")
        context["status_choices"] = AdminTodo.STATUS_CHOICES
        context["priority_choices"] = AdminTodo.PRIORITY_CHOICES
        context["is_admin"] = True
        return context


class AdminTodoDetailView(StaffRequiredMixin, DetailView):
    model = AdminTodo
    template_name = "accounts/admin/todo_detail.html"
    context_object_name = "todo"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = True
        return context


class AdminTodoCreateView(StaffRequiredMixin, CreateView):
    model = AdminTodo
    form_class = AdminTodoForm
    template_name = "accounts/admin/todo_form.html"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "To-Do created successfully.")
        response = super().form_valid(form)
        _send_todo_assigned_email(self.request, self.object)
        return response

    def get_success_url(self):
        return reverse_lazy("accounts:admin_todo_list")


@require_http_methods(["POST"])
def admin_todo_mark_completed(request, pk):
    if not request.user.is_authenticated:
        return redirect("accounts:login")

    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({"error": "Unauthorized"}, status=403)

    todo_obj = get_object_or_404(AdminTodo, pk=pk)
    if todo_obj.status != "completed":
        todo_obj.status = "completed"
        todo_obj.save(update_fields=["status", "updated_at"])
        messages.success(request, "To-Do marked as completed.")
        _send_todo_completed_email(request, todo_obj, request.user)
    else:
        messages.info(request, "To-Do is already completed.")

    return redirect("accounts:admin_todo_list")


class AdminTodoUpdateView(StaffRequiredMixin, UpdateView):
    model = AdminTodo
    form_class = AdminTodoForm
    template_name = "accounts/admin/todo_form.html"

    def form_valid(self, form):
        old_assigned_to_id = None
        try:
            old_assigned_to_id = self.get_object().assigned_to_id
        except Exception:
            old_assigned_to_id = None
        messages.success(self.request, "To-Do updated successfully.")
        response = super().form_valid(form)
        new_assigned_to_id = getattr(self.object, "assigned_to_id", None)
        if new_assigned_to_id and new_assigned_to_id != old_assigned_to_id:
            _send_todo_assigned_email(self.request, self.object)
        return response

    def get_success_url(self):
        return reverse_lazy("accounts:admin_todo_list")


class AdminTodoDeleteView(StaffRequiredMixin, DeleteView):
    model = AdminTodo
    template_name = "accounts/admin/todo_confirm_delete.html"

    def form_valid(self, form):
        messages.success(self.request, "To-Do deleted successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("accounts:admin_todo_list")


@require_http_methods(["POST"])
def admin_team_toggle_active(request, pk):
    if not request.user.is_authenticated:
        return redirect("accounts:login")

    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({"error": "Unauthorized"}, status=403)

    team = get_object_or_404(Team, pk=pk)
    team.is_active = not team.is_active
    team.save(update_fields=["is_active"])

    if team.is_active:
        messages.success(request, "Team activated successfully.")
    else:
        messages.success(request, "Team deactivated successfully.")

    return redirect("accounts:admin_team_list")


class AdminTeamUpdateView(StaffRequiredMixin, UpdateView):
    model = Team
    form_class = AdminTeamForm
    template_name = "accounts/admin/team_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Team updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("accounts:admin_team_list")


class AdminTeamDeleteView(StaffRequiredMixin, DeleteView):
    model = Team
    template_name = "accounts/admin/team_confirm_delete.html"

    def form_valid(self, form):
        messages.success(self.request, "Team deleted successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("accounts:admin_team_list")


class AdminOrderDetailView(StaffRequiredMixin, DetailView):
    """Vista de detalle de orden"""

    model = Order
    template_name = "accounts/admin/order_detail.html"
    context_object_name = "order"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        order = self.object
        context["is_admin"] = True

        profile_user_type = (
            getattr(getattr(order.user, "profile", None), "user_type", "") or ""
        )
        user_type_map = {
            "spectator": "spectator",
            "parent": "parent",
            "team_manager": "coach",
        }
        context["customer_user_type"] = user_type_map.get(
            profile_user_type, profile_user_type or "-"
        )

        # Jugadores registrados en esta orden (si aplica)
        try:
            registered_players = order.registered_players
        except Exception:
            registered_players = []

        # Fallback para órdenes antiguas sin registered_player_ids:
        # reconstruir jugadores a partir de EventAttendance y stripe_session_id
        event_attendances = None
        if not registered_players and order.event:
            session_id = None
            if order.stripe_checkout and order.stripe_checkout.stripe_session_id:
                session_id = order.stripe_checkout.stripe_session_id
            elif order.stripe_session_id:
                session_id = order.stripe_session_id

            if session_id:
                try:
                    attendances_qs = EventAttendance.objects.filter(
                        event=order.event,
                        notes__contains=session_id,
                    ).select_related("user")
                    if attendances_qs.exists():
                        player_users = [a.user for a in attendances_qs]
                        fallback_players = Player.objects.filter(
                            user__in=player_users,
                            is_active=True,
                        ).select_related("user")
                        if fallback_players:
                            registered_players = list(fallback_players)
                            event_attendances = attendances_qs
                except Exception:
                    # Si falla el fallback, simplemente dejamos la lista vacía
                    pass

        # Si tenemos jugadores registrados pero aún no hemos cargado asistencias,
        # obtener EventAttendance por user_id
        if order.event and registered_players and event_attendances is None:
            try:
                player_user_ids = [p.user_id for p in registered_players]
                event_attendances = EventAttendance.objects.filter(
                    event=order.event,
                    user_id__in=player_user_ids,
                )
            except Exception:
                event_attendances = None

        context["registered_players"] = registered_players

        # Reservas de hotel vinculadas a esta orden (si aplica)
        hotel_reservations = order.hotel_reservations
        # Optimización de consulta si es un QuerySet
        if hasattr(hotel_reservations, "select_related"):
            hotel_reservations = hotel_reservations.select_related(
                "room", "hotel"
            ).prefetch_related("service_reservations", "service_reservations__service")
        context["hotel_reservations"] = hotel_reservations

        # Resumen de plan de pagos (solo si la orden es un plan)
        context["payment_plan_summary"] = order.payment_plan_summary

        # Desglose JSON almacenado en la orden (jugadores, hotel, etc.)
        breakdown = order.breakdown or {}
        # Compatibilidad con órdenes antiguas: algunas claves nuevas pueden no existir.
        # El template usa acceso con punto (breakdown.no_show_fee), lo que puede fallar
        # si la clave no está presente.
        if isinstance(breakdown, dict):
            breakdown.setdefault("no_show_fee", "0.00")
            breakdown.setdefault("hotel_buy_out_fee", "0.00")
            breakdown.setdefault("wallet_deduction", "0.00")

            breakdown.setdefault("hotel_room_base", "0.00")
            breakdown.setdefault("hotel_services_total", "0.00")
            breakdown.setdefault("hotel_iva", "0.00")
            breakdown.setdefault("hotel_ish", "0.00")
            breakdown.setdefault("hotel_total_taxes", "0.00")
            breakdown.setdefault("hotel_total", "0.00")

            try:
                hotel_total = Decimal(str(breakdown.get("hotel_total") or "0"))
                hotel_room_base = Decimal(str(breakdown.get("hotel_room_base") or "0"))
                hotel_services_total = Decimal(
                    str(breakdown.get("hotel_services_total") or "0")
                )
                hotel_iva = Decimal(str(breakdown.get("hotel_iva") or "0"))
                hotel_ish = Decimal(str(breakdown.get("hotel_ish") or "0"))
                hotel_total_taxes = Decimal(
                    str(breakdown.get("hotel_total_taxes") or "0")
                )

                if hotel_total > 0 and hotel_total_taxes == 0:
                    derived_taxes = hotel_total - hotel_room_base - hotel_services_total
                    if derived_taxes > 0:
                        hotel_total_taxes = derived_taxes

                # If the order has actual hotel reservations, prefer taxes defined on the room
                # (HotelRoomTax) instead of assuming fixed rates.
                if hotel_total > 0 and hotel_iva == 0 and hotel_ish == 0:
                    try:
                        taxes_iva = Decimal("0.00")
                        taxes_ish = Decimal("0.00")
                        taxes_other = Decimal("0.00")

                        reservations_qs = getattr(order, "hotel_reservations", None)
                        if reservations_qs is not None and hasattr(
                            reservations_qs, "select_related"
                        ):
                            reservations_qs = reservations_qs.select_related(
                                "room"
                            ).prefetch_related("room__taxes")

                        for res in reservations_qs or []:
                            room = getattr(res, "room", None)
                            if not room:
                                continue
                            try:
                                nights = int(getattr(res, "number_of_nights", 0) or 0)
                            except Exception:
                                nights = 0
                            if nights < 1:
                                nights = 1

                            for tax in getattr(room, "taxes", []).all():
                                name = (getattr(tax, "name", "") or "").lower()
                                amount = Decimal(
                                    str(getattr(tax, "amount", "0") or "0")
                                )
                                amount = (amount * Decimal(str(nights))).quantize(
                                    Decimal("0.01")
                                )
                                if "iva" in name:
                                    taxes_iva += amount
                                elif "ish" in name:
                                    taxes_ish += amount
                                else:
                                    taxes_other += amount

                        if taxes_iva > 0:
                            hotel_iva = taxes_iva
                        if taxes_ish > 0:
                            hotel_ish = taxes_ish
                        if taxes_iva > 0 or taxes_ish > 0 or taxes_other > 0:
                            hotel_total_taxes = taxes_iva + taxes_ish + taxes_other
                    except Exception:
                        pass

                breakdown["hotel_iva"] = f"{hotel_iva:.2f}"
                breakdown["hotel_ish"] = f"{hotel_ish:.2f}"
                breakdown["hotel_total_taxes"] = f"{hotel_total_taxes:.2f}"
            except Exception:
                pass
        context["breakdown"] = breakdown

        # Asistencias al evento para los jugadores de esta orden (estado de registro)
        context["event_attendances"] = event_attendances

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
            User.objects.get(id=user_id, is_active=True)
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

    q = query.lower()

    users = (
        User.objects.filter(is_active=True)
        .annotate(
            username_l=Lower("username"),
            first_name_l=Lower("first_name"),
            last_name_l=Lower("last_name"),
            email_l=Lower("email"),
        )
        .filter(
            Q(username_l__contains=q)
            | Q(first_name_l__contains=q)
            | Q(last_name_l__contains=q)
            | Q(email_l__contains=q)
        )[:20]
    )

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


@require_http_methods(["GET", "POST"])
def admin_release_wallet_reservation_for_checkout(request, pk):
    if not request.user.is_staff:
        return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)

    checkout = (
        StripeEventCheckout.objects.filter(pk=pk)
        .select_related("event", "user")
        .first()
    )
    if not checkout:
        return JsonResponse(
            {"success": False, "error": "Checkout not found"}, status=404
        )

    if checkout.status == "paid":
        return JsonResponse(
            {
                "success": False,
                "error": "Checkout is paid; cannot release wallet reservation.",
            },
            status=400,
        )

    breakdown = checkout.breakdown or {}
    wallet_deduction_str = breakdown.get("wallet_deduction", "0")
    inferred_wallet_deduction = False
    try:
        wallet_deduction = Decimal(str(wallet_deduction_str))
    except (ValueError, TypeError, InvalidOperation):
        wallet_deduction = Decimal("0.00")

    wallet, _created = UserWallet.objects.get_or_create(user=checkout.user)

    if wallet_deduction <= 0:
        # Fallback: older data may not persist wallet_deduction inside checkout.breakdown.
        # Infer amount from the wallet reserve transaction created at checkout start.
        reserve_ref = f"event_checkout_pending:{checkout.event_id}"
        window_start = (checkout.created_at or timezone.now()) - timedelta(hours=2)
        window_end = (checkout.created_at or timezone.now()) + timedelta(hours=2)
        reserve_tx = (
            WalletTransaction.objects.filter(
                wallet=wallet,
                reference_id=reserve_ref,
                transaction_type="payment",
                created_at__gte=window_start,
                created_at__lte=window_end,
            )
            .order_by("-created_at")
            .first()
        )

        if reserve_tx and reserve_tx.amount and reserve_tx.amount > 0:
            wallet_deduction = reserve_tx.amount
            inferred_wallet_deduction = True
        elif wallet.pending_balance > 0 and wallet.pending_balance <= wallet.balance:
            # As a last resort, if the wallet has exactly one reservation (typical stuck case),
            # treat pending_balance as the amount to release.
            wallet_deduction = wallet.pending_balance
            inferred_wallet_deduction = True
        else:
            return JsonResponse(
                {
                    "success": False,
                    "error": "No wallet_deduction found for this checkout.",
                },
                status=400,
            )

    processed_refs = [
        f"checkout_expired:{checkout.pk}",
        f"checkout_cancel:{checkout.pk}",
        f"checkout_confirmed:{checkout.pk}",
        f"checkout_confirmed_webhook:{checkout.pk}",
    ]
    already_processed = WalletTransaction.objects.filter(
        wallet=wallet, reference_id__in=processed_refs
    ).exists()

    if already_processed:
        return JsonResponse(
            {
                "success": False,
                "error": "Reservation already processed for this checkout.",
            },
            status=400,
        )

    try:
        wallet.release_reserved_funds(
            amount=wallet_deduction,
            description=f"Reserva liberada por admin: {checkout.event.title}",
            reference_id=f"checkout_expired:{checkout.pk}",
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)

    checkout.status = "expired"
    checkout.save(update_fields=["status", "updated_at"])

    return JsonResponse(
        {
            "success": True,
            "checkout_id": checkout.pk,
            "user_id": checkout.user_id,
            "released": str(wallet_deduction),
            "wallet_pending_balance": str(wallet.pending_balance),
            "inferred_wallet_deduction": inferred_wallet_deduction,
        }
    )


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
