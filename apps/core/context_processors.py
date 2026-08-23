from django.conf import settings


def store_settings(request):
    from apps.catalog.models import Category
    from apps.orders.cart import Cart

    return {
        'STORE_NAME': settings.STORE_NAME,
        'WHATSAPP_NUMBER': settings.WHATSAPP_NUMBER,
        'nav_categories': Category.objects.filter(is_active=True).only('name', 'slug', 'order'),
        'cart_count': len(Cart(request)),
    }
