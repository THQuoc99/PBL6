# ...existing code...
from django.contrib import admin
from .models import Order, SubOrder, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'buyer', 'total_amount', 'shipping_fee', 'created_at')
    search_fields = ('order_id', 'buyer__username', 'buyer__email')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['buyer']
    ordering = ('-created_at',)

@admin.register(SubOrder)
class SubOrderAdmin(admin.ModelAdmin):
    list_display = ('sub_order_id', 'order', 'store', 'subtotal', 'shipping_fee', 'created_at')
    search_fields = ('sub_order_id', 'order__order_id', 'store__name')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['order', 'store']
    ordering = ('-created_at',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('item_id', 'order', 'sub_order', 'variant', 'quantity', 'price_at_order', 'subtotal_display')
    search_fields = ('item_id', 'order__order_id', 'sub_order__sub_order_id', 'variant__sku', 'variant__product__name')
    list_filter = ('order', 'sub_order', 'variant')
    autocomplete_fields = ['order', 'sub_order', 'variant']

    def subtotal_display(self, obj):
        return obj.subtotal
    subtotal_display.short_description = 'Subtotal'
# ...existing code...