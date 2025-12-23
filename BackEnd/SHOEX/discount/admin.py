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
    
    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)
        
        # Send notification for new voucher
        if is_new and obj.is_active:
            from notifications.utils import notify_platform_voucher, notify_shop_promotion
            try:
                from users.models import User
                all_users = User.objects.filter(is_active=True)[:50]  # Limit for testing
                
                if obj.type == 'platform':
                    # Platform voucher - notify all users
                    discount_text = f"{obj.discount_value}%" if obj.discount_type == 'percent' else f"{obj.discount_value}đ"
                    notify_platform_voucher(all_users, obj.code, discount_text)
                elif obj.type == 'store' and obj.seller:
                    # Store voucher - notify shop followers
                    discount_text = f"{obj.discount_value}%" if obj.discount_type == 'percent' else f"{obj.discount_value}đ"
                    shop_id_int = hash(obj.seller.store_id) % 1000000  # Convert to positive integer
                    notify_shop_promotion(all_users, shop_id_int, obj.seller.name, f"Giảm {discount_text}", discount_text)
            except Exception as e:
                print(f"Voucher notification error: {str(e)}")

@admin.register(UserVoucher)
class UserVoucherAdmin(admin.ModelAdmin):
    list_display = ['user', 'voucher', 'used_count', 'saved_at']
    raw_id_fields = ['user', 'voucher']

@admin.register(OrderVoucher)
class OrderVoucherAdmin(admin.ModelAdmin):
    list_display = ['order', 'voucher', 'discount_amount', 'applied_at']
    raw_id_fields = ['order', 'voucher']