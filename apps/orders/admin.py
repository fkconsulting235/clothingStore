from django.contrib import admin

from .models import BankAccount, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('variant', 'quantity', 'unit_price')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer_phone', 'status', 'total', 'created_at')
    list_filter = ('status',)
    search_fields = ('customer_name', 'customer_phone')
    readonly_fields = ('payment_proof', 'total', 'created_at', 'reservation')
    inlines = [OrderItemInline]


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('bank_name', 'account_number', 'holder_name', 'order', 'is_active')
    list_editable = ('order', 'is_active')
