from django.contrib import admin
from .models import Order, SubOrder, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['variant', 'quantity', 'price_at_order', 'discount_amount']

class SubOrderInline(admin.StackedInline):
    model = SubOrder
    extra = 0
    inlines = [OrderItemInline]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'buyer', 'total_amount', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_id', 'buyer__username']
    inlines = [SubOrderInline]

@admin.register(SubOrder)
class SubOrderAdmin(admin.ModelAdmin):
    list_display = ['sub_order_id', 'order', 'store', 'subtotal', 'status']
    list_filter = ['status', 'store']