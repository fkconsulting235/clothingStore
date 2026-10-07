from django.db import migrations
from django.utils.text import slugify


def fix_blank_skus(apps, schema_editor):
    ProductVariant = apps.get_model('catalog', 'ProductVariant')

    for variant in ProductVariant.objects.filter(sku='').select_related('product'):
        color_code = slugify(variant.color)[:10].upper()
        size_code = slugify(variant.size)[:6].upper()
        base_sku = f'{variant.product.code}-{color_code}-{size_code}'

        sku = base_sku
        suffix = 1
        while ProductVariant.objects.filter(sku=sku).exclude(pk=variant.pk).exists():
            suffix += 1
            sku = f'{base_sku}-{suffix}'

        variant.sku = sku
        variant.save(update_fields=['sku'])


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_alter_productimage_image'),
    ]

    operations = [
        migrations.RunPython(fix_blank_skus, migrations.RunPython.noop),
    ]
