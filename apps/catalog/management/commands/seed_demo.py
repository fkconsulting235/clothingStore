from django.core.management.base import BaseCommand

from apps.catalog.models import Category, Product, ProductVariant

DATA = {
    'Camisas': [
        {
            'name': 'Camisa Oxford Clásica',
            'price': 25.00,
            'desc': 'Camisa de algodón, corte clásico, ideal para toda ocasión.',
            'variants': [('Azul', 'M', 5), ('Azul', 'L', 3), ('Blanco', 'M', 0), ('Blanco', 'S', 2)],
        },
        {
            'name': 'Camisa de Lino Manga Larga',
            'price': 32.00,
            'desc': 'Lino fresco y ligero, perfecta para el calor.',
            'variants': [('Beige', 'M', 4), ('Beige', 'L', 4), ('Blanco', 'S', 6)],
        },
        {
            'name': 'Camisa a Cuadros Casual',
            'price': 28.00,
            'desc': 'Estampado a cuadros, corte relajado.',
            'variants': [('Rojo', 'M', 5), ('Negro', 'L', 2)],
        },
    ],
    'Pantalones': [
        {
            'name': 'Pantalón Chino Slim Fit',
            'price': 35.00,
            'desc': 'Corte entallado, tela con un poco de elastano para mayor comodidad.',
            'variants': [('Caqui', '30', 4), ('Caqui', '32', 5), ('Caqui', '34', 3), ('Negro', '32', 0)],
        },
        {
            'name': 'Jeans Corte Recto',
            'price': 40.00,
            'desc': 'Mezclilla resistente, corte recto clásico.',
            'variants': [('Azul Oscuro', '30', 6), ('Azul Oscuro', '32', 6), ('Azul Oscuro', '34', 4)],
        },
        {
            'name': 'Pantalón de Vestir Formal',
            'price': 45.00,
            'desc': 'Ideal para oficina o eventos formales.',
            'variants': [('Gris', '32', 3), ('Gris', '34', 3)],
        },
    ],
    'Vestidos': [
        {
            'name': 'Vestido Floral Verano',
            'price': 38.00,
            'desc': 'Estampado floral, tela ligera y fresca.',
            'variants': [('Estampado', 'S', 3), ('Estampado', 'M', 4), ('Estampado', 'L', 2)],
        },
        {
            'name': 'Vestido Negro Elegante',
            'price': 55.00,
            'desc': 'Corte entallado, perfecto para ocasiones especiales.',
            'variants': [('Negro', 'S', 2), ('Negro', 'M', 3), ('Negro', 'L', 0)],
        },
        {
            'name': 'Vestido Casual Midi',
            'price': 42.00,
            'desc': 'Largo midi, cómodo para el día a día.',
            'variants': [('Terracota', 'M', 4), ('Terracota', 'L', 3)],
        },
    ],
    'Chaquetas': [
        {
            'name': 'Chaqueta de Mezclilla',
            'price': 50.00,
            'desc': 'Clásica chaqueta de mezclilla, combina con todo.',
            'variants': [('Azul', 'M', 3), ('Azul', 'L', 2)],
        },
        {
            'name': 'Blazer Formal',
            'price': 65.00,
            'desc': 'Corte estructurado, ideal para looks de oficina.',
            'variants': [('Negro', 'M', 2), ('Negro', 'L', 2), ('Azul Marino', 'M', 0)],
        },
        {
            'name': 'Chaqueta Impermeable',
            'price': 58.00,
            'desc': 'Resistente al agua, ligera y práctica.',
            'variants': [('Verde Olivo', 'M', 4), ('Verde Olivo', 'L', 4)],
        },
    ],
    'Zapatos': [
        {
            'name': 'Zapatos Casuales de Cuero',
            'price': 60.00,
            'desc': 'Cuero genuino, suela cómoda para todo el día.',
            'variants': [('Café', '40', 3), ('Café', '41', 3), ('Café', '42', 2)],
        },
        {
            'name': 'Tenis Urbanos',
            'price': 48.00,
            'desc': 'Estilo urbano, suela ligera y transpirable.',
            'variants': [('Blanco', '38', 4), ('Blanco', '39', 4), ('Blanco', '40', 0), ('Negro', '40', 5)],
        },
        {
            'name': 'Botines de Mujer',
            'price': 65.00,
            'desc': 'Tacón bajo, cómodos y versátiles.',
            'variants': [('Negro', '36', 2), ('Negro', '37', 3), ('Negro', '38', 2)],
        },
    ],
    'Accesorios': [
        {
            'name': 'Cinturón de Cuero',
            'price': 18.00,
            'desc': 'Cuero genuino, hebilla metálica.',
            'variants': [('Café', 'Único', 8), ('Negro', 'Único', 8)],
        },
        {
            'name': 'Bufanda de Lana',
            'price': 15.00,
            'desc': 'Lana suave, perfecta para el frío.',
            'variants': [('Gris', 'Único', 6)],
        },
        {
            'name': 'Gorra Deportiva',
            'price': 12.00,
            'desc': 'Ajustable, ideal para uso diario.',
            'variants': [('Negro', 'Único', 10), ('Azul', 'Único', 0)],
        },
    ],
}


class Command(BaseCommand):
    help = 'Llena la tienda con categorías, prendas y variantes de prueba.'

    def handle(self, *args, **options):
        for order, (category_name, products) in enumerate(DATA.items(), start=1):
            category, _ = Category.objects.get_or_create(
                name=category_name, defaults={'order': order},
            )

            for product_data in products:
                product, created = Product.objects.get_or_create(
                    name=product_data['name'],
                    category=category,
                    defaults={
                        'base_price': product_data['price'],
                        'description': product_data['desc'],
                    },
                )
                if not created:
                    continue

                for color, size, stock in product_data['variants']:
                    ProductVariant.objects.get_or_create(
                        product=product, color=color, size=size, defaults={'stock': stock},
                    )

                self.stdout.write(f'  + {product.code} · {product.name} ({len(product_data["variants"])} variantes)')

        total_categories = Category.objects.count()
        total_products = Product.objects.count()
        total_variants = ProductVariant.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f'Listo: {total_categories} categorías, {total_products} prendas, {total_variants} variantes.',
        ))
