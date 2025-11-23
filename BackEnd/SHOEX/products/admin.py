# products/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib import messages
import json
from itertools import product as cartesian_product

from .models import (
    Category, Product, ProductAttribute, ProductAttributeOption,
    ProductVariant, ProductImage
)


# ===================== INLINES =====================

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'is_thumbnail', 'alt_text', 'display_order', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.pk and obj.image:
            return format_html('<img src="{}" style="max-height: 80px; object-fit: contain;" />', obj.image.url)
        return "(Chưa upload)"
    image_preview.short_description = "Preview"


class ProductAttributeOptionInline(admin.TabularInline):
    model = ProductAttributeOption
    extra = 1
    fields = ('attribute', 'value', 'value_code', 'image', 'display_order', 'is_available', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.pk and obj.image:
            return format_html('<img src="{}" style="width: 40px; height: 40px; object-fit: cover;" />', obj.image.url)
        return "(Không có)"
    image_preview.short_description = "Ảnh"


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ('sku', 'price', 'stock', 'weight', 'is_active', 'option_display')
    readonly_fields = ('option_display',)

    def option_display(self, obj):
        if not obj.pk:
            return "-"
        try:
            opts = json.loads(obj.option_combinations) if isinstance(obj.option_combinations, str) else obj.option_combinations
            return " | ".join([f"{k}: {v}" for k, v in opts.items()])
        except Exception:
            return str(obj.option_combinations)
    option_display.short_description = "Kết hợp thuộc tính"


# ===================== ACTIONS =====================

def generate_all_variants(modeladmin, request, queryset):
    total_created = 0
    for product in queryset.prefetch_related('attribute_options__attribute'):
        options = product.attribute_options.select_related('attribute').filter(is_available=True)
        if not options.exists():
            messages.warning(request, f"[ {product.name} ] Chưa có tùy chọn thuộc tính nào để tạo variant!")
            continue

        # Group by attribute
        groups = {}
        for opt in options:
            attr_name = opt.attribute.name
            groups.setdefault(attr_name, []).append(opt)

        if not groups:
            continue

        keys = list(groups.keys())
        value_lists = [groups[k] for k in keys]
        created_for_this = 0

        for combo in cartesian_product(*value_lists):
            combination_dict = {opt.attribute.name: opt.value for opt in combo}
            combination_json = json.dumps(combination_dict, ensure_ascii=False)

            # Tạo SKU
            suffix = "".join([str(opt.value_code or opt.value)[:4] for opt in combo]).upper()
            base_sku = f"{product.model_code or product.product_id}-{suffix}"
            sku = base_sku
            i = 1
            while ProductVariant.objects.filter(sku=sku).exists():
                sku = f"{base_sku}-{i}"
                i += 1

            variant, created = ProductVariant.objects.get_or_create(
                product=product,
                option_combinations=combination_json,
                defaults={
                    'sku': sku,
                    'price': product.base_price,
                    'stock': 0,
                    'weight': 0.3,
                    'is_active': True,
                }
            )
            if created:
                created_for_this += 1

        total_created += created_for_this
        messages.success(request, f"Đã tạo {created_for_this} variant cho [{product.name}]")

    if total_created == 0:
        messages.info(request, "Không có variant nào được tạo mới.")
generate_all_variants.short_description = "Tạo toàn bộ biến thể từ tùy chọn thuộc tính"


# ===================== ADMIN CLASSES =====================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'name', 'parent', 'is_active', 'product_count')
    list_filter = ('is_active', 'parent')
    search_fields = ('name',)
    ordering = ('name',)

    def product_count(self, obj):
        count = obj.products.count()
        url = reverse("admin:products_product_changelist") + f"?category__id__exact={obj.pk}"
        return format_html('<a href="{}">{} sản phẩm</a>', url, count)
    product_count.short_description = "Số sản phẩm"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'name', 'store', 'category', 'brand', 'price_range', 'total_stock_colored', 'variant_count', 'is_featured', 'is_active')
    list_filter = ('store', 'category', 'brand', 'is_active', 'is_featured', 'created_at')
    search_fields = ('name', 'model_code', 'brand', 'description')
    ordering = ('-created_at',)
    actions = [generate_all_variants]
    inlines = [ProductImageInline, ProductAttributeOptionInline, ProductVariantInline]
    readonly_fields = ('size_guide_preview',)

    fieldsets = (
        ('Thông tin chính', {
            'fields': ('store', 'category', 'name', 'slug', 'description')
        }),
        ('Thương hiệu & Mã', {
            'fields': ('brand', 'model_code'),
            'classes': ('collapse',)
        }),
        ('Giá & Ảnh hướng dẫn', {
            'fields': ('base_price', 'size_guide_image', 'size_guide_preview')
        }),
        ('Trạng thái', {
            'fields': ('is_active', 'is_featured')
        }),
    )

    def price_range(self, obj):
        if obj.variants.exists():
            return f"{obj.min_price:,.0f}₫ → {obj.max_price:,.0f}₫"
        return f"{obj.base_price:,.0f}₫"
    price_range.short_description = "Khoảng giá"

    def total_stock_colored(self, obj):
        stock = obj.total_stock
        color = "green" if stock > 50 else "orange" if stock > 10 else "red"
        return format_html('<b style="color:{};">{}</b>', color, stock)
    total_stock_colored.short_description = "Tồn kho"

    def variant_count(self, obj):
        count = obj.variants.count()
        return format_html('<b>{}</b>', count)
    variant_count.short_description = "Biến thể"

    def size_guide_preview(self, obj):
        if obj.size_guide_image:
            return format_html('<img src="{}" style="max-height: 250px;" />', obj.size_guide_image.url)
        return "Không có ảnh hướng dẫn size"
    size_guide_preview.short_description = "Hướng dẫn chọn size"


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('sku', 'product_link', 'color_with_image', 'size', 'price', 'stock_colored', 'is_active')
    list_filter = ('is_active', 'product__category', 'product__store')
    search_fields = ('sku', 'product__name')
    readonly_fields = ('option_pretty',)  # <-- ĐÃ THÊM METHOD DƯỚI ĐÂY

    def product_link(self, obj):
        url = reverse("admin:products_product_change", args=[obj.product.pk])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = "Sản phẩm"

    def color_with_image(self, obj):
        color = obj.color_name
        img_obj = obj.color_image
        if img_obj and img_obj.image:
            return format_html('<img src="{}" width=24 height=24 style="vertical-align:middle; margin-right:6px;"> {}', img_obj.image.url, color)
        return color or "-"
    color_with_image.short_description = "Màu"

    def size(self, obj):
        return obj.size_name or "-"
    size.short_description = "Size"

    def stock_colored(self, obj):
        color = "green" if obj.stock > 20 else "orange" if obj.stock > 0 else "red"
        return format_html('<b style="color:{};">{}</b>', color, obj.stock)
    stock_colored.short_description = "Tồn kho"

    # ← ĐÂY LÀ METHOD BỊ THIẾU TRƯỚC ĐÓ
    def option_pretty(self, obj):
        try:
            opts = json.loads(obj.option_combinations) if isinstance(obj.option_combinations, str) else obj.option_combinations
            return " | ".join([f"{k}: {v}" for k, v in opts.items()])
        except Exception:
            return str(obj.option_combinations)
    option_pretty.short_description = "Thuộc tính"


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'is_required', 'has_image', 'display_order')
    list_editable = ('display_order', 'is_required')
    ordering = ('display_order', 'name')


@admin.register(ProductAttributeOption)
class ProductAttributeOptionAdmin(admin.ModelAdmin):
    list_display = ('product', 'attribute', 'value', 'value_code', 'image_preview', 'is_available')
    list_filter = ('attribute', 'is_available')
    search_fields = ('product__name', 'value', 'value_code')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width=40 height=40 />', obj.image.url)
        return "-"
    image_preview.short_description = "Ảnh"


# ĐĂNG KÝ THÊM NẾU MUỐN
admin.site.register(ProductImage)  # hoặc tạo riêng nếu cần