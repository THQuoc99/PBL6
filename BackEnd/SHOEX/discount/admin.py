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
    # Cập nhật tên trường: type -> scope, seller -> store
    list_display = ['code', 'scope', 'store', 'discount_value', 'start_date', 'end_date', 'is_active']
    
    # list_filter phải dùng field thật trong DB (scope), không dùng property (type)
    list_filter = ['scope', 'is_active', 'start_date', 'end_date']
    
    # Search theo store__name thay vì seller__name
    search_fields = ['code', 'store__name'] 
    
    # Dùng store thay vì seller
    raw_id_fields = ['store'] 
    
    inlines = [VoucherProductInline, VoucherStoreInline]
    
    fieldsets = (
        ('Thông tin chung', {
            # Thay is_auto bằng is_free_shipping (vì model mới không có is_auto)
            'fields': ('code', 'scope', 'store', 'is_active', 'is_free_shipping', 'payment_method_required')
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
                
                # Cập nhật logic dùng scope và store
                if obj.scope == 'platform':
                    # Platform voucher - notify all users
                    discount_text = f"{obj.discount_value}%" if obj.discount_type == 'percent' else f"{obj.discount_value:,.0f}đ"
                    notify_platform_voucher(all_users, obj.code, discount_text)
                
                elif obj.scope == 'store' and obj.store:
                    # Store voucher - notify shop followers
                    discount_text = f"{obj.discount_value}%" if obj.discount_type == 'percent' else f"{obj.discount_value:,.0f}đ"
                    
                    # Giả sử store_id là số, nếu là chuỗi hash tạm
                    try:
                        shop_id_int = int(obj.store.pk)
                    except:
                        shop_id_int = hash(obj.store.pk) % 1000000
                    
                    notify_shop_promotion(all_users, shop_id_int, obj.store.name, f"Giảm {discount_text}", discount_text)
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