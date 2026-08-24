from django.db import models

from apps.core.uploads import payment_proof_upload_to


class BankAccount(models.Model):
    bank_name = models.CharField('banco', max_length=100)
    account_type = models.CharField('tipo de cuenta', max_length=50, blank=True)
    account_number = models.CharField('número de cuenta', max_length=60)
    holder_name = models.CharField('a nombre de', max_length=120)
    order = models.PositiveIntegerField('orden', default=0)
    is_active = models.BooleanField('activa', default=True)

    class Meta:
        verbose_name = 'cuenta bancaria'
        verbose_name_plural = 'cuentas bancarias'
        ordering = ['order', 'bank_name']

    def __str__(self):
        return f'{self.bank_name} · {self.account_number}'


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendiente'),
        (STATUS_PAID, 'Pagado'),
        (STATUS_CANCELLED, 'Cancelado'),
    ]

    customer_name = models.CharField('nombre del cliente', max_length=120)
    customer_phone = models.CharField('teléfono del cliente', max_length=30)
    customer_email = models.EmailField('correo del cliente', blank=True)
    status = models.CharField(
        'estado', max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True,
    )
    payment_proof = models.ImageField(
        'comprobante de pago', upload_to=payment_proof_upload_to, blank=True,
    )
    total = models.DecimalField('total', max_digits=10, decimal_places=2, default=0)
    reservation = models.ForeignKey(
        'reservations.Reservation', null=True, blank=True, on_delete=models.SET_NULL, related_name='orders',
        verbose_name='reserva',
    )
    created_at = models.DateTimeField('creado', auto_now_add=True)

    class Meta:
        verbose_name = 'pedido'
        verbose_name_plural = 'pedidos'
        ordering = ['-created_at']

    def __str__(self):
        return f'Pedido #{self.pk} · {self.customer_name} · {self.get_status_display()}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='pedido')
    variant = models.ForeignKey(
        'catalog.ProductVariant', on_delete=models.PROTECT, related_name='order_items', verbose_name='variante',
    )
    quantity = models.PositiveIntegerField('cantidad')
    unit_price = models.DecimalField('precio unitario', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'artículo del pedido'
        verbose_name_plural = 'artículos del pedido'

    def __str__(self):
        return f'{self.variant.sku} x{self.quantity}'

    @property
    def subtotal(self):
        return self.unit_price * self.quantity
