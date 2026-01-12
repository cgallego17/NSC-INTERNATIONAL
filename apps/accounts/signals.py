"""
Señales para generar notificaciones automáticas
"""
import logging

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.urls import reverse

from .models import Notification, Order

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
        if created:
            # Nueva orden creada
            Notification.create_notification(
                user=instance.user,
                title="Nueva orden creada",
                message=f'Se ha creado la orden #{instance.order_number}',
                notification_type="order",
                order=instance,
                action_url=reverse("accounts:admin_order_detail", args=[instance.pk]),
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
    except Exception as e:
        logger.error(f"Error creating order notification: {str(e)}")
