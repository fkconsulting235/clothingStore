import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
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

    order_items = list(order.items.select_related('variant__product'))
    items = ', '.join(
        f'{item.variant.product.name} ({item.variant.color}/{item.variant.size}) x{item.quantity}'
        for item in order_items
    )
    panel_url = request.build_absolute_uri(reverse('dashboard:order_list'))

    context = {
        'order': order,
        'order_items': order_items,
        'panel_url': panel_url,
        'STORE_NAME': settings.STORE_NAME,
        'STORE_CURRENCY_SYMBOL': settings.STORE_CURRENCY_SYMBOL,
    }

    subject = f'🛍️ Nuevo comprobante · Pedido #{order.pk} · {order.customer_name}'
    text_body = (
        f'{order.customer_name} ({order.customer_phone}) subió un comprobante de pago.\n\n'
        f'Prendas: {items}\n'
        f'Total: {settings.STORE_CURRENCY_SYMBOL}{order.total}\n\n'
        f'Revísalo aquí: {panel_url}'
    )
    html_body = render_to_string('emails/new_order_notification.html', context)

    try:
        email = EmailMultiAlternatives(
            subject, text_body, settings.DEFAULT_FROM_EMAIL, [settings.STORE_NOTIFICATION_EMAIL],
        )
        email.attach_alternative(html_body, 'text/html')
        email.send(fail_silently=False)
    except Exception:
        logger.exception('No se pudo enviar el correo de aviso del pedido #%s', order.pk)
