from django.contrib import admin
from .models import (
    Voucher, VoucherProduct, VoucherCategory, 
    VoucherStore, UserVoucher, OrderVoucher
)

class VoucherProductInline(admin.TabularInline):
    model = VoucherProduct
    raw_id_fields = ['product']
    extra = 1

class VoucherStoreInline(admin.TabularInline):
    model = VoucherStore
    raw_id_fields = ['store']
    extra = 1

@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ['code', 'type', 'seller', 'discount_value', 'start_date', 'end_date', 'is_active']
    list_filter = ['type', 'is_active', 'start_date', 'end_date']
    search_fields = ['code', 'seller__name'] # Search theo tên Store
    raw_id_fields = ['seller'] # Để chọn Store dễ dàng hơn
    inlines = [VoucherProductInline, VoucherStoreInline]
    
    fieldsets = (
        ('Thông tin chung', {
            'fields': ('code', 'type', 'seller', 'is_active', 'is_auto')
        }),
        ('Giảm giá', {
            'fields': ('discount_type', 'discount_value', 'min_order_amount', 'max_discount')
        }),
        ('Thời hạn & Giới hạn', {
            'fields': ('start_date', 'end_date', 'usage_limit', 'per_user_limit')
        }),
    )

@admin.register(UserVoucher)
class UserVoucherAdmin(admin.ModelAdmin):
    list_display = ['user', 'voucher', 'used_count', 'saved_at']
    raw_id_fields = ['user', 'voucher']

@admin.register(OrderVoucher)
class OrderVoucherAdmin(admin.ModelAdmin):
    list_display = ['order', 'voucher', 'discount_amount', 'applied_at']
    raw_id_fields = ['order', 'voucher']