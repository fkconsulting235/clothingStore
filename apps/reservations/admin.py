from django.contrib import admin

from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('variant', 'customer_name', 'customer_phone', 'quantity', 'status', 'created_at', 'expires_at')
    list_filter = ('status',)
    search_fields = ('customer_name', 'customer_phone', 'variant__sku')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
