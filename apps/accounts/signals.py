"""
Señales para generar notificaciones automáticas
"""

import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse

from .models import Notification, Order, Player

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Order)
def track_order_status_before_save(sender, instance, **kwargs):
    """Rastrea el estado anterior de la orden antes de guardar"""
    if instance.pk:
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            instance._previous_status = old_instance.status
        except Order.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None


@receiver(post_save, sender=Order)
def create_order_notification(sender, instance, created, **kwargs):
    """Crea notificaciones cuando se crea o actualiza una orden"""
    try:
        User = get_user_model()
        staff_emails = list(
            User.objects.filter(is_active=True, is_staff=True)
            .exclude(email__isnull=True)
            .exclude(email__exact="")
            .values_list("email", flat=True)
            .distinct()
        )
        from_email = (
            getattr(settings, "DEFAULT_FROM_EMAIL", "")
            or getattr(settings, "EMAIL_HOST_USER", "")
            or "no-reply@localhost"
        )

        site_url = (getattr(settings, "SITE_URL", "") or "").rstrip("/")

        event = getattr(instance, "event", None)
        event_title = getattr(event, "title", "") if event else ""
        event_start_date = getattr(event, "start_date", None) if event else None
        event_end_date = getattr(event, "end_date", None) if event else None
        event_location = getattr(event, "location", "") if event else ""
        event_address = getattr(event, "address", "") if event else ""
        event_city = getattr(getattr(event, "city", None), "name", "") if event else ""
        event_state = (
            getattr(getattr(event, "state", None), "name", "") if event else ""
        )
        event_country = (
            getattr(getattr(event, "country", None), "name", "") if event else ""
        )

        currency = (getattr(instance, "currency", "") or "").upper()

        # Players included in the sale: prefer Order.registered_player_ids, fallback to checkout.player_ids,
        # and finally attempt to read from breakdown.
        raw_player_ids = []
        breakdown_players = []
        try:
            raw_player_ids = list(
                getattr(instance, "registered_player_ids", None) or []
            )
        except Exception:
            raw_player_ids = []

        if not raw_player_ids:
            try:
                co = getattr(instance, "stripe_checkout", None)
                raw_player_ids = (
                    list(getattr(co, "player_ids", None) or []) if co else []
                )
            except Exception:
                raw_player_ids = []

        if not raw_player_ids:
            try:
                bd = getattr(instance, "breakdown", None) or {}
                bd_ids = bd.get("player_ids") or bd.get("registered_player_ids") or []
                raw_player_ids = list(bd_ids or [])
            except Exception:
                raw_player_ids = []

        # If IDs are still missing, attempt to read denormalized player info from breakdown.
        # Supports either:
        # - breakdown['players'] = [{'name': '...', 'email': '...'}, ...]
        # - breakdown['players'] = ['Name 1', 'Name 2']
        if not raw_player_ids:
            try:
                bd = getattr(instance, "breakdown", None) or {}
                breakdown_players = list(bd.get("players") or [])
            except Exception:
                breakdown_players = []

        player_ids = []
        for pid in raw_player_ids:
            try:
                player_ids.append(int(pid))
            except Exception:
                continue

        players_count = len(player_ids)

        registered_players = []
        if player_ids:
            try:
                for p in Player.objects.filter(
                    id__in=player_ids, is_active=True
                ).select_related("user"):
                    user_obj = getattr(p, "user", None)
                    if not user_obj:
                        continue
                    player_name = (
                        user_obj.get_full_name() or user_obj.username or ""
                    ).strip()
                    player_email = (getattr(user_obj, "email", "") or "").strip()
                    if player_name or player_email:
                        registered_players.append(
                            {
                                "name": player_name or "-",
                                "email": player_email,
                            }
                        )
            except Exception:
                registered_players = []
        elif breakdown_players:
            for item in breakdown_players:
                if isinstance(item, dict):
                    name = (item.get("name") or item.get("full_name") or "").strip()
                    email = (item.get("email") or "").strip()
                    if name or email:
                        registered_players.append({"name": name or "-", "email": email})
                else:
                    try:
                        name = str(item).strip()
                    except Exception:
                        name = ""
                    if name:
                        registered_players.append({"name": name, "email": ""})

        # If we got players only from breakdown (no IDs), ensure count reflects it.
        if not players_count and registered_players:
            players_count = len(registered_players)
        try:
            hotel_reservations_count = instance.hotel_reservations.count()
        except Exception:
            hotel_reservations_count = 0

        base_email_context = {
            "brand_name": "NCS International",
            "order_number": instance.order_number,
            "status": instance.status,
            "status_label": instance.get_status_display(),
            "user_name": instance.user.get_full_name() or instance.user.username,
            "user_username": getattr(instance.user, "username", "") or "",
            "user_email": getattr(instance.user, "email", "") or "",
            "event_title": event_title or "-",
            "event_start_date": event_start_date,
            "event_end_date": event_end_date,
            "event_location": event_location,
            "event_address": event_address,
            "event_city": event_city,
            "event_state": event_state,
            "event_country": event_country,
            "payment_method": instance.get_payment_method_display(),
            "payment_mode": instance.get_payment_mode_display(),
            "currency": currency,
            "subtotal": instance.subtotal,
            "discount_amount": instance.discount_amount,
            "tax_amount": instance.tax_amount,
            "total_amount": instance.total_amount,
            "players_count": players_count,
            "registered_players": registered_players,
            "hotel_reservations_count": hotel_reservations_count,
            "created_at": instance.created_at,
            "paid_at": instance.paid_at,
        }

        if created:
            # Nueva orden creada
            Notification.create_notification(
                user=instance.user,
                title="Nueva orden creada",
                message=f"Se ha creado la orden #{instance.order_number}",
                notification_type="order",
                order=instance,
                action_url=reverse("accounts:admin_order_detail", args=[instance.pk]),
            )

            if staff_emails:
                subject = f"Nueva orden creada #{instance.order_number}"
                path = reverse("accounts:admin_order_detail", args=[instance.pk])
                url = f"{site_url}{path}" if site_url else path
                message = (
                    f"Se ha creado una nueva orden.\n\n"
                    f"Orden: #{instance.order_number}\n"
                    f"Usuario: {instance.user.get_full_name() or instance.user.username}\n"
                    f"Evento: {getattr(getattr(instance, 'event', None), 'title', '') or '-'}\n"
                    f"Total: {instance.total_amount}\n"
                    f"Status: {instance.status}\n\n"
                    f"Ver detalle: {url}\n"
                )
                html_message = render_to_string(
                    "emails/order_staff_notification.html",
                    {
                        "email_title": subject,
                        "preheader": f"Order #{instance.order_number} created",
                        "email_tag": "Staff Notification",
                        **base_email_context,
                        "detail_url": url,
                    },
                )
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=message,
                    from_email=from_email,
                    to=staff_emails,
                )
                email.attach_alternative(html_message, "text/html")
                try:
                    email.send(fail_silently=False)
                except Exception:
                    logger.exception(
                        "Error sending staff order-created email for order %s",
                        instance.order_number,
                    )
        else:
            # Orden actualizada - verificar cambios de estado
            if hasattr(instance, "_previous_status"):
                previous_status = instance._previous_status
                current_status = instance.status

                if previous_status != current_status:
                    status_messages = {
                        "paid": "Tu orden ha sido pagada exitosamente",
                        "cancelled": "Tu orden ha sido cancelada",
                        "refunded": "Tu orden ha sido reembolsada",
                        "failed": "El pago de tu orden ha fallado",
                    }

                    if current_status in status_messages:
                        Notification.create_notification(
                            user=instance.user,
                            title=f"Orden #{instance.order_number} - {instance.get_status_display()}",
                            message=status_messages.get(
                                current_status,
                                f"El estado de tu orden ha cambiado a {instance.get_status_display()}",
                            ),
                            notification_type="order",
                            order=instance,
                            action_url=reverse(
                                "accounts:admin_order_detail", args=[instance.pk]
                            ),
                        )

                    if current_status == "paid" and staff_emails:
                        subject = f"Orden pagada #{instance.order_number}"
                        path = reverse(
                            "accounts:admin_order_detail", args=[instance.pk]
                        )
                        url = f"{site_url}{path}" if site_url else path
                        message = (
                            f"Una orden fue marcada como pagada.\n\n"
                            f"Orden: #{instance.order_number}\n"
                            f"Usuario: {instance.user.get_full_name() or instance.user.username}\n"
                            f"Evento: {getattr(getattr(instance, 'event', None), 'title', '') or '-'}\n"
                            f"Total: {instance.total_amount}\n\n"
                            f"Ver detalle: {url}\n"
                        )
                        html_message = render_to_string(
                            "emails/order_staff_notification.html",
                            {
                                "email_title": subject,
                                "preheader": f"Order #{instance.order_number} paid",
                                "email_tag": "Staff Notification",
                                **base_email_context,
                                "detail_url": url,
                            },
                        )
                        email = EmailMultiAlternatives(
                            subject=subject,
                            body=message,
                            from_email=from_email,
                            to=staff_emails,
                        )
                        email.attach_alternative(html_message, "text/html")
                        try:
                            email.send(fail_silently=False)
                        except Exception:
                            logger.exception(
                                "Error sending staff order-paid email for order %s",
                                instance.order_number,
                            )
    except Exception as e:
        logger.error(f"Error creating order notification: {str(e)}")
