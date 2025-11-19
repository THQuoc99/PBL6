from django.contrib import admin
from .models import Order, SubOrder, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'buyer', 'total_amount', 'status', 'created_at')
    search_fields = ('buyer__username',)
    list_filter = ('status', 'created_at')

@admin.register(SubOrder)
class SubOrderAdmin(admin.ModelAdmin):
    list_display = ['sub_order_id', 'order', 'store', 'subtotal', 'status', 'created_at']
    search_fields = ('order__order_id', 'store__name')
    list_filter = ('status', 'created_at')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('item_id', 'order', 'sub_order', 'variant', 'quantity', 'price_at_order')
    search_fields = ('order__order_id', 'sub_order__sub_order_id', 'variant__sku')
    list_filter = ('order', 'sub_order')