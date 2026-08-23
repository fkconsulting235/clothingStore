from datetime import timedelta

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Reservation(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_EXPIRED = 'expired'
    STATUS_CONVERTED = 'converted'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Activa'),
        (STATUS_EXPIRED, 'Vencida'),
        (STATUS_CONVERTED, 'Convertida en pedido'),
        (STATUS_CANCELLED, 'Cancelada'),
    ]

    variant = models.ForeignKey(
        'catalog.ProductVariant', on_delete=models.CASCADE, related_name='reservations', verbose_name='variante',
    )
    customer_name = models.CharField('nombre del cliente', max_length=120)
    customer_phone = models.CharField('teléfono del cliente', max_length=30)
    quantity = models.PositiveIntegerField('cantidad', default=1, validators=[MinValueValidator(1)])
    status = models.CharField(
        'estado', max_length=12, choices=STATUS_CHOICES, default=STATUS_ACTIVE, db_index=True,
    )
    created_at = models.DateTimeField('creada', auto_now_add=True)
    expires_at = models.DateTimeField('vence', blank=True)

    class Meta:
        verbose_name = 'reserva'
        verbose_name_plural = 'reservas'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.variant.sku} x{self.quantity} · {self.customer_name}'

    def save(self, *args, **kwargs):
        if not self.expires_at:
            hours = getattr(settings, 'RESERVATION_HOURS', 24)
            self.expires_at = timezone.now() + timedelta(hours=hours)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return self.status == self.STATUS_ACTIVE and self.expires_at <= timezone.now()

    @property
    def time_left(self):
        remaining = self.expires_at - timezone.now()
        return remaining if remaining.total_seconds() > 0 else timedelta(0)
