from django.contrib import messages
from django.db import transaction
from django.db.models import ProtectedError, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.catalog.models import Category, Product
from apps.orders.models import BankAccount, Order
from apps.orders.views import mark_order_paid, undo_order_paid
from apps.reservations.models import Reservation

from .decorators import staff_required
from .forms import BankAccountForm, CategoryForm, ImageFormSet, ProductForm, VariantFormSet


@staff_required
def home(request):
    paid_orders = Order.objects.filter(status=Order.STATUS_PAID)
    today = timezone.localdate()

    context = {
        'total_products': Product.objects.filter(is_active=True).count(),
        'total_categories': Category.objects.filter(is_active=True).count(),
        'active_reservations': Reservation.objects.filter(
            status=Reservation.STATUS_ACTIVE, expires_at__gt=timezone.now(),
        ).count(),
        'paid_orders': paid_orders.count(),
        'sales_today': paid_orders.filter(created_at__date=today).aggregate(total=Sum('total'))['total'] or 0,
        'sales_month': paid_orders.filter(
            created_at__year=today.year, created_at__month=today.month,
        ).aggregate(total=Sum('total'))['total'] or 0,
        'sales_total': paid_orders.aggregate(total=Sum('total'))['total'] or 0,
    }
    return render(request, 'dashboard/home.html', context)


@staff_required
def product_list(request):
    products = Product.objects.select_related('category').prefetch_related('variants').order_by('-created_at')

    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(Q(name__icontains=query) | Q(code__icontains=query))

    category_id = request.GET.get('category', '')
    if category_id:
        products = products.filter(category_id=category_id)

    return render(request, 'dashboard/product_list.html', {
        'products': products,
        'categories': Category.objects.all(),
        'query': query,
        'selected_category': category_id,
    })


@staff_required
def product_form(request, pk=None):
    product = get_object_or_404(Product, pk=pk) if pk else Product()

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        variant_formset = VariantFormSet(request.POST, instance=product, prefix='variants')
        image_formset = ImageFormSet(request.POST, request.FILES, instance=product, prefix='images')

        form_valid = form.is_valid()
        variants_valid = variant_formset.is_valid()
        images_valid = image_formset.is_valid()

        if form_valid and variants_valid and images_valid:
            with transaction.atomic():
                product = form.save()
                variant_formset.instance = product
                variant_formset.save()
                image_formset.instance = product
                image_formset.save()
            messages.success(request, 'Prenda guardada correctamente.')
            return redirect('dashboard:product_list')
    else:
        form = ProductForm(instance=product)
        variant_formset = VariantFormSet(instance=product, prefix='variants')
        image_formset = ImageFormSet(instance=product, prefix='images')

    return render(request, 'dashboard/product_form.html', {
        'form': form,
        'variant_formset': variant_formset,
        'image_formset': image_formset,
        'product': product,
    })


@staff_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, f'Se eliminó la prenda {product.code}.')
        return redirect('dashboard:product_list')
    return render(request, 'dashboard/product_confirm_delete.html', {'product': product})


@staff_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'dashboard/category_list.html', {'categories': categories})


@staff_required
def category_form(request, pk=None):
    category = get_object_or_404(Category, pk=pk) if pk else None

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría guardada correctamente.')
            return redirect('dashboard:category_list')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'dashboard/category_form.html', {'form': form, 'category': category})


@staff_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        try:
            category.delete()
        except ProtectedError:
            messages.error(
                request,
                f'No se puede eliminar "{category.name}" porque todavía tiene prendas asignadas. '
                'Muévelas a otra categoría primero.',
            )
            return redirect('dashboard:category_list')
        messages.success(request, f'Se eliminó la categoría {category.name}.')
        return redirect('dashboard:category_list')
    return render(request, 'dashboard/category_confirm_delete.html', {'category': category})


@staff_required
def reservation_list(request):
    reservations = Reservation.objects.select_related('variant__product')

    status = request.GET.get('status', '')
    if status:
        reservations = reservations.filter(status=status)

    return render(request, 'dashboard/reservation_list.html', {
        'reservations': reservations,
        'status_choices': Reservation.STATUS_CHOICES,
        'selected_status': status,
    })


@staff_required
def order_list(request):
    orders = Order.objects.prefetch_related('items__variant__product')

    status = request.GET.get('status', '')
    if status:
        orders = orders.filter(status=status)

    return render(request, 'dashboard/order_list.html', {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
        'selected_status': status,
    })


@staff_required
@require_POST
def order_mark_paid(request, pk):
    order = get_object_or_404(Order, pk=pk)
    mark_order_paid(order)
    messages.success(request, f'Pedido #{order.id} marcado como pagado.')
    return redirect('dashboard:order_list')


@staff_required
@require_POST
def order_undo_paid(request, pk):
    order = get_object_or_404(Order, pk=pk)
    undo_order_paid(order)
    messages.success(request, f'Pedido #{order.id} regresado a pendiente.')
    return redirect('dashboard:order_list')


@staff_required
@require_POST
def order_reject(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.status = Order.STATUS_CANCELLED
    order.save(update_fields=['status'])
    messages.success(request, f'Pedido #{order.id} rechazado.')
    return redirect('dashboard:order_list')


@staff_required
def bank_account_list(request):
    bank_accounts = BankAccount.objects.all()
    return render(request, 'dashboard/bank_account_list.html', {'bank_accounts': bank_accounts})


@staff_required
def bank_account_form(request, pk=None):
    bank_account = get_object_or_404(BankAccount, pk=pk) if pk else None

    if request.method == 'POST':
        form = BankAccountForm(request.POST, instance=bank_account)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cuenta bancaria guardada correctamente.')
            return redirect('dashboard:bank_account_list')
    else:
        form = BankAccountForm(instance=bank_account)

    return render(request, 'dashboard/bank_account_form.html', {'form': form, 'bank_account': bank_account})


@staff_required
def bank_account_delete(request, pk):
    bank_account = get_object_or_404(BankAccount, pk=pk)
    if request.method == 'POST':
        bank_account.delete()
        messages.success(request, f'Se eliminó la cuenta de {bank_account.bank_name}.')
        return redirect('dashboard:bank_account_list')
    return render(request, 'dashboard/bank_account_confirm_delete.html', {'bank_account': bank_account})
