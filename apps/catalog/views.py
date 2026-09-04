from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Product, ProductVariant


def home(request):
    categories = Category.objects.filter(is_active=True).prefetch_related('products__images', 'products__variants')
    return render(request, 'catalog/home.html', {'categories': categories})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = category.products.filter(is_active=True).prefetch_related('images', 'variants')
    return render(request, 'catalog/category.html', {'category': category, 'products': products})


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.prefetch_related('variants', 'images'), slug=slug, is_active=True,
    )
    whatsapp_message = f'Hola, me interesa la prenda {product.code} - {product.name}'
    return render(request, 'catalog/product_detail.html', {
        'product': product, 'whatsapp_message': whatsapp_message,
    })


def search(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.none()
    if query:
        products = Product.objects.filter(is_active=True).filter(
            Q(name__icontains=query) | Q(code__icontains=query),
        ).prefetch_related('images', 'variants')

    return render(request, 'catalog/search.html', {'products': products, 'query': query})


def by_size(request):
    size = request.GET.get('talla', '').strip()

    available_sizes = ProductVariant.objects.filter(
        product__is_active=True,
    ).order_by('size').values_list('size', flat=True).distinct()

    products = Product.objects.none()
    if size:
        products = Product.objects.filter(
            is_active=True, variants__size__iexact=size,
        ).distinct().prefetch_related('images', 'variants')

    return render(request, 'catalog/by_size.html', {
        'products': products, 'selected_size': size, 'available_sizes': available_sizes,
    })
