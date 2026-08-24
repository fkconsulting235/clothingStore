from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from apps.core.uploads import product_image_upload_to


class Category(models.Model):
    name = models.CharField('nombre', max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    order = models.PositiveIntegerField(
        'orden', default=0, help_text='Orden de aparición de la sección en la tienda.',
    )
    is_active = models.BooleanField('activa', default=True)

    class Meta:
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._unique_slug()
        super().save(*args, **kwargs)

    def _unique_slug(self):
        base = slugify(self.name)
        slug = base
        i = 1
        while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            i += 1
            slug = f'{base}-{i}'
        return slug


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products', verbose_name='categoría')
    name = models.CharField('nombre', max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    code = models.CharField(
        'código', max_length=20, unique=True, blank=True, db_index=True,
        help_text='Código único de la prenda. Se genera solo (ej. PR-0001) y se puede editar.',
    )
    description = models.TextField('descripción', blank=True)
    base_price = models.DecimalField(
        'precio base', max_digits=10, decimal_places=2, validators=[MinValueValidator(0)],
    )
    is_active = models.BooleanField('activa', default=True)
    created_at = models.DateTimeField('creada', auto_now_add=True)

    class Meta:
        verbose_name = 'prenda'
        verbose_name_plural = 'prendas'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.code} · {self.name}' if self.code else self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._unique_slug()
        super().save(*args, **kwargs)
        if not self.code:
            self.code = f'PR-{self.pk:04d}'
            super().save(update_fields=['code'])

    def _unique_slug(self):
        base = slugify(self.name)
        slug = base
        i = 1
        while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            i += 1
            slug = f'{base}-{i}'
        return slug

    def get_absolute_url(self):
        return reverse('catalog:product_detail', args=[self.slug])

    @property
    def main_image(self):
        return self.images.first()

    @property
    def total_available_stock(self):
        return sum(v.available_stock for v in self.variants.all())


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', verbose_name='prenda')
    color = models.CharField('color', max_length=50)
    size = models.CharField('talla', max_length=20)
    sku = models.CharField('sku', max_length=40, unique=True, blank=True, db_index=True)
    price_override = models.DecimalField(
        'precio especial', max_digits=10, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)], help_text='Deja vacío para usar el precio base de la prenda.',
    )
    stock = models.PositiveIntegerField('existencias', default=0)

    class Meta:
        verbose_name = 'variante'
        verbose_name_plural = 'variantes'
        unique_together = ('product', 'color', 'size')
        ordering = ['color', 'size']

    def __str__(self):
        return f'{self.sku or "(sin sku)"} · {self.color}/{self.size}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.sku:
            color_code = slugify(self.color)[:10].upper()
            size_code = slugify(self.size)[:6].upper()
            self.sku = f'{self.product.code}-{color_code}-{size_code}'
            super().save(update_fields=['sku'])

    @property
    def price(self):
        return self.price_override if self.price_override is not None else self.product.base_price

    @property
    def available_stock(self):
        from django.utils import timezone

        from apps.reservations.models import Reservation

        reserved = Reservation.objects.filter(
            variant=self, status='active', expires_at__gt=timezone.now(),
        ).aggregate(total=models.Sum('quantity'))['total'] or 0
        return max(self.stock - reserved, 0)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='prenda')
    image = models.ImageField('imagen', upload_to=product_image_upload_to)
    order = models.PositiveIntegerField('orden', default=0)

    class Meta:
        verbose_name = 'imagen'
        verbose_name_plural = 'imágenes'
        ordering = ['order', 'id']

    def __str__(self):
        return f'Imagen de {self.product.name} (#{self.order})'
