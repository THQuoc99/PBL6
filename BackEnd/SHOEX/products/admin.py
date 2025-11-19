from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Category, Product, ProductAttribute, ProductAttributeOption, 
    ProductVariant, ProductImage
)

# ===== INLINE ADMIN CLASSES =====

class ProductImageInline(admin.TabularInline):
    """Inline cho ảnh sản phẩm"""
    model = ProductImage
    extra = 1
    fields = ('image_url', 'is_thumbnail', 'alt_text', 'display_order', 'image_preview')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 100px;" />',
                obj.image_url
            )
        return "No image"
    image_preview.short_description = "Preview"


class ProductAttributeOptionInline(admin.TabularInline):
    """Inline cho tùy chọn thuộc tính"""
    model = ProductAttributeOption
    extra = 1
    fields = ('attribute', 'value', 'value_code', 'image_url', 'display_order', 'is_available', 'image_preview')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="max-height: 30px; max-width: 50px;" />',
                obj.image_url
            )
        return "No image"
    image_preview.short_description = "Preview"


class ProductVariantInline(admin.TabularInline):
    """Inline cho variants"""
    model = ProductVariant
    extra = 1
    fields = ('sku', 'price', 'stock', 'weight', 'option_combinations', 'is_active')
    readonly_fields = ('color_info', 'size_info')
    
    def color_info(self, obj):
        return obj.color_name
    color_info.short_description = "Color"
    
    def size_info(self, obj):
        return obj.size_name
    size_info.short_description = "Size"


# ===== MAIN ADMIN CLASSES =====

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'name', 'parent', 'product_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'description')
    ordering = ('name',)
    list_per_page = 20
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('name', 'description', 'parent')
        }),
        ('Cài đặt', {
            'fields': ('is_active',),
            'classes': ('collapse',)
        })
    )
    
    def product_count(self, obj):
        count = obj.products.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:products_product_changelist') + f'?category__id__exact={obj.category_id}'
            return format_html('<a href="{}">{} sản phẩm</a>', url, count)
        return "0 sản phẩm"
    product_count.short_description = "Số sản phẩm"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'product_id', 'name', 'brand', 'category', 'store', 
        'price_display', 'stock_display', 'variant_count', 
        'is_featured', 'is_hot', 'is_active', 'created_at'
    )
    list_filter = ('is_active', 'is_featured', 'is_hot', 'category', 'brand', 'created_at')
    search_fields = ('name', 'brand', 'model_code', 'store__name', 'description')
    ordering = ('-created_at',)
    list_per_page = 20
    date_hierarchy = 'created_at'
    readonly_fields = ('size_guide_display',)
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('store', 'category', 'name', 'description', 'size_guide_image', 'size_guide_display')
        }),
        ('Thương hiệu & Model', {
            'fields': ('brand', 'model_code'),
            'classes': ('collapse',)
        }),
        ('Giá cả', {
            'fields': ('base_price',)
        }),
        ('Cài đặt', {
            'fields': ('is_active', 'is_featured', 'is_hot'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [ProductImageInline, ProductAttributeOptionInline, ProductVariantInline]
    
    def price_display(self, obj):
        return f"{obj.min_price:,.0f}đ - {obj.max_price:,.0f}đ"
    price_display.short_description = "Khoảng giá"
    
    def stock_display(self, obj):
        stock = obj.total_stock
        if stock > 20:
            color = "green"
        elif stock > 5:
            color = "orange"
        else:
            color = "red"
        return format_html(
            '<span style="color: {};">{} sản phẩm</span>',
            color, stock
        )
    stock_display.short_description = "Tồn kho"
    
    def variant_count(self, obj):
        count = obj.variants.filter(is_active=True).count()
        return f"{count} variants"
    variant_count.short_description = "Số variants"
    
    def size_guide_display(self, obj):
        """Hiển thị ảnh hướng dẫn chọn size"""
        if obj.size_guide_image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 150px;" />',
                obj.size_guide_image.url
            )
        return "Chưa có hướng dẫn"
    size_guide_display.short_description = "Hướng dẫn size"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('image_id', 'product', 'image_preview', 'is_thumbnail', 'display_order', 'created_at')
    list_filter = ('is_thumbnail', 'created_at')
    search_fields = ('product__name', 'alt_text')
    ordering = ('product', '-is_thumbnail', 'display_order')
    
    def image_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="max-height: 80px; max-width: 120px;" />',
                obj.image_url
            )
        return "No image"
    image_preview.short_description = "Preview"


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ('attribute_id', 'name', 'type', 'is_required', 'has_image', 'display_order', 'option_count')
    list_filter = ('type', 'is_required', 'has_image')
    search_fields = ('name',)
    ordering = ('display_order', 'name')
    
    def option_count(self, obj):
        count = obj.product_options.filter(is_available=True).count()
        return f"{count} options"
    option_count.short_description = "Số options"


@admin.register(ProductAttributeOption)
class ProductAttributeOptionAdmin(admin.ModelAdmin):
    list_display = (
        'option_id', 'product', 'attribute', 'value', 'value_code', 
        'image_preview', 'variant_count', 'display_order', 'is_available'
    )
    list_filter = ('attribute', 'is_available', 'created_at')
    search_fields = ('product__name', 'attribute__name', 'value')
    ordering = ('product', 'attribute__display_order', 'display_order')
    
    def image_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="max-height: 40px; max-width: 60px;" />',
                obj.image_url
            )
        return "No image"
    image_preview.short_description = "Preview"
    
    def variant_count(self, obj):
        count = obj.get_variants().count()
        if count > 0:
            return format_html('<strong>{}</strong>', count)
        return "0"
    variant_count.short_description = "Variants"


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        'variant_id', 'product', 'sku', 'color_display', 'size_display',
        'price', 'stock_display', 'weight', 'is_active', 'created_at'
    )
    list_filter = ('is_active', 'created_at')
    search_fields = ('sku', 'product__name')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('product', 'sku')
        }),
        ('Giá & Kho', {
            'fields': ('price', 'stock', 'weight')
        }),
        ('Thuộc tính', {
            'fields': ('option_combinations',),
            'classes': ('collapse',)
        }),
        ('Cài đặt', {
            'fields': ('is_active',),
            'classes': ('collapse',)
        })
    )
    
    def color_display(self, obj):
        color = obj.color_name
        if color != 'N/A':
            color_image = obj.color_image
            if color_image and color_image.image_url:
                return format_html(
                    '<img src="{}" style="width: 20px; height: 20px; border-radius: 50%; margin-right: 5px;" />{}'.format(
                        color_image.image_url, color
                    )
                )
            return color
        return "N/A"
    color_display.short_description = "Màu"
    
    def size_display(self, obj):
        size = obj.size_name
        if size != 'N/A':
            return format_html('<strong>{}</strong>', size)
        return "N/A"
    size_display.short_description = "Size"
    
    def stock_display(self, obj):
        stock = obj.stock
        if stock > 20:
            color = "green"
        elif stock > 5:
            color = "orange"
        elif stock > 0:
            color = "red"
        else:
            color = "gray"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, stock
        )
    stock_display.short_description = "Tồn kho"


# ===== CUSTOM ADMIN ACTIONS =====

def make_featured(modeladmin, request, queryset):
    """Đánh dấu sản phẩm nổi bật"""
    updated = queryset.update(is_featured=True)
    modeladmin.message_user(request, f'{updated} sản phẩm đã được đánh dấu nổi bật.')
make_featured.short_description = "Đánh dấu nổi bật"

def remove_featured(modeladmin, request, queryset):
    """Bỏ đánh dấu sản phẩm nổi bật"""
    updated = queryset.update(is_featured=False)
    modeladmin.message_user(request, f'{updated} sản phẩm đã bỏ đánh dấu nổi bật.')
remove_featured.short_description = "Bỏ đánh dấu nổi bật"

def make_active(modeladmin, request, queryset):
    """Kích hoạt sản phẩm"""
    updated = queryset.update(is_active=True)
    modeladmin.message_user(request, f'{updated} sản phẩm đã được kích hoạt.')
make_active.short_description = "Kích hoạt"

def make_inactive(modeladmin, request, queryset):
    """Vô hiệu hóa sản phẩm"""
    updated = queryset.update(is_active=False)
    modeladmin.message_user(request, f'{updated} sản phẩm đã bị vô hiệu hóa.')
make_inactive.short_description = "Vô hiệu hóa"

# Thêm actions vào ProductAdmin
ProductAdmin.actions = [make_featured, remove_featured, make_active, make_inactive]