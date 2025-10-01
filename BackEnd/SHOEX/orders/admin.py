from django.contrib import admin
from .models import Province, District, Ward, Hamlet, Address, Order, SubOrder, OrderItem

@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('province_id', 'name')
    search_fields = ('name',)

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('district_id', 'name', 'province')
    search_fields = ('name',)
    list_filter = ('province',)

@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ('ward_id', 'name', 'district')
    search_fields = ('name',)
    list_filter = ('district',)

@admin.register(Hamlet)
class HamletAdmin(admin.ModelAdmin):
    list_display = ('hamlet_id', 'name', 'ward')
    search_fields = ('name',)
    list_filter = ('ward',)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('address_id', 'user', 'province', 'district', 'ward', 'is_default')
    search_fields = ('user__username', 'detail')
    list_filter = ('province', 'district', 'ward', 'is_default')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'buyer', 'total_amount', 'status', 'created_at')
    search_fields = ('buyer__username',)
    list_filter = ('status', 'created_at')

@admin.register(SubOrder)
class SubOrderAdmin(admin.ModelAdmin):
    list_display = ('sub_order_id', 'order', 'seller', 'total_amount', 'status', 'created_at')
    search_fields = ('order__order_id', 'seller__username')
    list_filter = ('status', 'created_at')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order_item_id', 'order', 'sub_order', 'variant', 'quantity', 'price_at_order')
    search_fields = ('order__order_id', 'sub_order__sub_order_id', 'variant__sku')
    list_filter = ('order', 'sub_order')