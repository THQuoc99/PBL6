from django.contrib import admin
from .models import (
    Voucher, VoucherProduct, VoucherCategory, 
    VoucherSeller, UserVoucher, OrderVoucher
)


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'type', 'discount_type', 'discount_value',
        'start_date', 'end_date', 'is_active', 'is_auto'
    ]
    list_filter = ['type', 'discount_type', 'is_active', 'is_auto', 'start_date', 'end_date']
    search_fields = ['code', 'seller__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('code', 'type', 'seller')
        }),
        ('Cấu hình giảm giá', {
            'fields': ('discount_type', 'discount_value', 'min_order_amount', 'max_discount')
        }),
        ('Thời gian hiệu lực', {
            'fields': ('start_date', 'end_date')
        }),
        ('Giới hạn sử dụng', {
            'fields': ('usage_limit', 'per_user_limit')
        }),
        ('Trạng thái', {
            'fields': ('is_active', 'is_auto')
        }),
        ('Thông tin hệ thống', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VoucherProduct)
class VoucherProductAdmin(admin.ModelAdmin):
    list_display = ['voucher', 'product', 'created_at']
    list_filter = ['voucher__type', 'created_at']
    search_fields = ['voucher__code', 'product__name']
    raw_id_fields = ['voucher', 'product']


@admin.register(VoucherCategory)
class VoucherCategoryAdmin(admin.ModelAdmin):
    list_display = ['voucher', 'category', 'created_at']
    list_filter = ['voucher__type', 'created_at']
    search_fields = ['voucher__code', 'category__name']
    raw_id_fields = ['voucher', 'category']


@admin.register(VoucherSeller)
class VoucherSellerAdmin(admin.ModelAdmin):
    list_display = ['voucher', 'seller', 'created_at']
    list_filter = ['created_at']
    search_fields = ['voucher__code', 'seller__username']
    raw_id_fields = ['voucher', 'seller']


@admin.register(UserVoucher)
class UserVoucherAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'voucher', 'saved_at', 'used_count', 'can_use'
    ]
    list_filter = ['saved_at', 'voucher__type']
    search_fields = ['user__username', 'voucher__code']
    readonly_fields = ['saved_at', 'can_use']
    raw_id_fields = ['user', 'voucher']


@admin.register(OrderVoucher)
class OrderVoucherAdmin(admin.ModelAdmin):
    list_display = [
        'order', 'voucher', 'discount_amount', 'applied_at'
    ]
    list_filter = ['applied_at', 'voucher__type']
    search_fields = ['order__order_id', 'voucher__code']
    readonly_fields = ['applied_at']
    raw_id_fields = ['order', 'voucher']
