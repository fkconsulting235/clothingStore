from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.catalog.models import ProductVariant
from apps.reservations.models import Reservation

from .cart import Cart
from .forms import CartCheckoutForm, CheckoutForm, PaymentProofForm
from .models import BankAccount, Order, OrderItem


def start_checkout(request, variant_id):
    variant = get_object_or_404(ProductVariant, pk=variant_id)

    reservation = None
    reservation_id = request.GET.get('reservation_id') or request.POST.get('reservation_id')
    if reservation_id:
        reservation = get_object_or_404(
            Reservation, pk=reservation_id, variant=variant, status=Reservation.STATUS_ACTIVE,
        )

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            quantity = reservation.quantity if reservation else form.cleaned_data['quantity']

            with transaction.atomic():
                locked_variant = ProductVariant.objects.select_for_update().get(pk=variant.pk)
                if not reservation and quantity > locked_variant.available_stock:
                    form.add_error('quantity', 'Ya no hay suficiente disponibilidad para esa cantidad.')
                else:
                    order = Order.objects.create(
                        customer_name=form.cleaned_data['customer_name'],
                        customer_phone=form.cleaned_data['customer_phone'],
                        customer_email=form.cleaned_data['customer_email'],
                        total=locked_variant.price * quantity,
                        reservation=reservation,
                    )
                    OrderItem.objects.create(
                        order=order, variant=locked_variant, quantity=quantity, unit_price=locked_variant.price,
                    )
                    return redirect('orders:pay', pk=order.pk)
    else:
        initial = {'quantity': reservation.quantity if reservation else 1}
        if reservation:
            initial['customer_name'] = reservation.customer_name
            initial['customer_phone'] = reservation.customer_phone
        form = CheckoutForm(initial=initial)

    return render(request, 'orders/checkout.html', {
        'form': form, 'variant': variant, 'reservation': reservation,
    })


def pay(request, pk):
    order = get_object_or_404(Order, pk=pk)
    bank_accounts = BankAccount.objects.filter(is_active=True)

    if request.method == 'POST':
        form = PaymentProofForm(request.POST, request.FILES, instance=order)
        if form.is_valid():
            form.save()
            return redirect('orders:pending_review', pk=order.pk)
    else:
        form = PaymentProofForm(instance=order)

    return render(request, 'orders/pay.html', {
        'order': order, 'bank_accounts': bank_accounts, 'form': form,
    })


def pending_review(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'orders/pending_review.html', {'order': order})


@require_POST
def add_to_cart(request, variant_id):
    variant = get_object_or_404(ProductVariant, pk=variant_id)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1
    quantity = max(quantity, 1)

    if quantity > variant.available_stock:
        messages.error(request, 'Ya no hay suficiente disponibilidad para esa cantidad.')
    else:
        Cart(request).add(variant.id, quantity)
        messages.success(request, f'{variant.product.name} ({variant.color}/{variant.size}) agregado al carrito.')

    return redirect('catalog:product_detail', variant.product.slug)


def cart_detail(request):
    cart = Cart(request)

    if request.method == 'POST':
        form = CartCheckoutForm(request.POST)
        lines = cart.lines()
        if not lines:
            messages.error(request, 'Tu carrito está vacío.')
        elif form.is_valid():
            with transaction.atomic():
                variant_ids = sorted(line['variant'].id for line in lines)
                locked_variants = {
                    v.id: v for v in ProductVariant.objects.select_for_update().filter(pk__in=variant_ids)
                }
                insufficient = [
                    line for line in lines
                    if line['quantity'] > locked_variants[line['variant'].id].available_stock
                ]
                if insufficient:
                    names = ', '.join(line['variant'].product.name for line in insufficient)
                    messages.error(request, f'Ya no hay suficiente disponibilidad para: {names}.')
                else:
                    order = Order.objects.create(
                        customer_name=form.cleaned_data['customer_name'],
                        customer_phone=form.cleaned_data['customer_phone'],
                        customer_email=form.cleaned_data['customer_email'],
                        total=cart.total(),
                    )
                    for line in lines:
                        locked_variant = locked_variants[line['variant'].id]
                        OrderItem.objects.create(
                            order=order, variant=locked_variant,
                            quantity=line['quantity'], unit_price=locked_variant.price,
                        )
                    cart.clear()
                    return redirect('orders:pay', pk=order.pk)
    else:
        form = CartCheckoutForm()

    return render(request, 'orders/cart.html', {
        'lines': cart.lines(), 'total': cart.total(), 'form': form,
    })


@require_POST
def cart_update(request, variant_id):
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1
    Cart(request).update(variant_id, quantity)
    return redirect('orders:cart_detail')


@require_POST
def cart_remove(request, variant_id):
    Cart(request).remove(variant_id)
    return redirect('orders:cart_detail')


def mark_order_paid(order):
    if order.status == Order.STATUS_PAID:
        return

    with transaction.atomic():
        order.status = Order.STATUS_PAID
        order.save(update_fields=['status'])

        for item in order.items.select_related('variant'):
            variant = ProductVariant.objects.select_for_update().get(pk=item.variant_id)
            variant.stock = max(variant.stock - item.quantity, 0)
            variant.save(update_fields=['stock'])

        if order.reservation_id:
            Reservation.objects.filter(pk=order.reservation_id).update(status=Reservation.STATUS_CONVERTED)
