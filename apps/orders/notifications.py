import logging

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

logger = logging.getLogger(__name__)


def notify_new_order(request, order):
    """Avisa por correo a la encargada que llegó un comprobante de pago nuevo.

    No debe romper el flujo de compra del cliente si el envío falla (ej. el
    correo no está configurado todavía, o el servidor de correo está caído),
    por eso cualquier error solo se registra en el log.
    """
    if not settings.STORE_NOTIFICATION_EMAIL:
        return

    items = ', '.join(
        f'{item.variant.product.name} ({item.variant.color}/{item.variant.size}) x{item.quantity}'
        for item in order.items.select_related('variant__product')
    )
    panel_url = request.build_absolute_uri(reverse('dashboard:order_list'))

    subject = f'🛍️ Nuevo comprobante · Pedido #{order.pk} · {order.customer_name}'
    message = (
        f'{order.customer_name} ({order.customer_phone}) subió un comprobante de pago.\n\n'
        f'Prendas: {items}\n'
        f'Total: {settings.STORE_CURRENCY_SYMBOL}{order.total}\n\n'
        f'Revísalo aquí: {panel_url}'
    )

    try:
        send_mail(
            subject, message, settings.DEFAULT_FROM_EMAIL, [settings.STORE_NOTIFICATION_EMAIL],
            fail_silently=False,
        )
    except Exception:
        logger.exception('No se pudo enviar el correo de aviso del pedido #%s', order.pk)
