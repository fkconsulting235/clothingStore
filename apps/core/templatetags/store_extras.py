from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def money(value):
    """Formatea un número como C$1,234.56 (punto decimal, coma de miles),
    sin importar el idioma/localización activa del sitio."""
    try:
        value = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return value
    return f'{value:,.2f}'
