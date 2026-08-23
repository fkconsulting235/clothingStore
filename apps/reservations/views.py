from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from apps.catalog.models import ProductVariant

from .forms import ReservationForm
from .models import Reservation


def create_reservation(request, variant_id):
    variant = get_object_or_404(ProductVariant, pk=variant_id)

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            with transaction.atomic():
                locked_variant = ProductVariant.objects.select_for_update().get(pk=variant.pk)
                if quantity > locked_variant.available_stock:
                    form.add_error('quantity', 'Ya no hay suficiente disponibilidad para esa cantidad.')
                else:
                    reservation = form.save(commit=False)
                    reservation.variant = locked_variant
                    reservation.save()
                    return redirect('reservations:confirmation', pk=reservation.pk)
    else:
        form = ReservationForm(initial={'quantity': 1})

    return render(request, 'reservations/form.html', {'form': form, 'variant': variant})


def reservation_confirmation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    return render(request, 'reservations/confirmation.html', {'reservation': reservation})
