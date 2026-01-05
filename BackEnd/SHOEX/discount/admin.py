from django.contrib import admin
from django import forms
from .models import (
    Voucher, VoucherProduct, VoucherCategory,
    VoucherStore, UserVoucher, OrderVoucher
)
from store.models import Store

# FORM CHO ADMIN
class VoucherAdminForm(forms.ModelForm):
    store_select = forms.ModelChoiceField(
        queryset=Store.objects.all(),
        required=False,
        label="Cửa hàng áp dụng (voucher store)"
    )

    class Meta:
        model = Voucher
        fields = "__all__"

# ADMIN VOUCHER
@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    form = VoucherAdminForm

    list_display = [
        'code', 'type',
        'discount_type', 'discount_value',
        'min_order_amount', 'max_discount',
        'start_date', 'end_date',
        'is_active', 'is_auto',
        'created_at', 'updated_at'
    ]

    list_filter = [
        'type', 'discount_type', 'is_active', 'is_auto',
        'start_date', 'end_date',
    ]

    search_fields = ['code']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('code', 'name', 'type', 'store_select', 'description')
        }),
        ('Cấu hình giảm giá', {
            'fields': (
                'discount_type', 'discount_value',
                'min_order_amount', 'max_discount'
            )
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

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        store_selected = form.cleaned_data.get('store_select')
        if obj.type == 'store':
            if not store_selected:
                raise Exception("Vui lòng chọn cửa hàng cho voucher loại 'store'.")
            VoucherStore.objects.get_or_create(
                voucher=obj,
                store=store_selected
            )
        else:
            obj.voucher_stores.all().delete()

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

@admin.register(VoucherStore)
class VoucherStoreAdmin(admin.ModelAdmin):
    list_display = ['voucher', 'store', 'created_at']
    list_filter = ['store', 'created_at']
    search_fields = ['voucher__code', 'store__name']
    raw_id_fields = ['voucher', 'store']

@admin.register(UserVoucher)
class UserVoucherAdmin(admin.ModelAdmin):
    list_display = ['user', 'voucher', 'saved_at', 'used_count', 'can_use']
    list_filter = ['saved_at', 'voucher__type']
    search_fields = ['user__username', 'voucher__code']
    readonly_fields = ['saved_at', 'can_use']
    raw_id_fields = ['user', 'voucher']

@admin.register(OrderVoucher)
class OrderVoucherAdmin(admin.ModelAdmin):
    list_display = ['order', 'voucher', 'discount_amount', 'applied_at']
    list_filter = ['applied_at', 'voucher__type']
    search_fields = ['order__order_id', 'voucher__code']
    readonly_fields = ['applied_at']
    raw_id_fields = ['order', 'voucher']