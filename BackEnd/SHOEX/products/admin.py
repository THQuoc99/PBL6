from django.contrib import admin
from .models import Product, Category, ProductImage, ProductVariant, ProductAttribute, ProductAttributeOption
from django.utils.html import format_html

# Inline cho ProductImage
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    # ✅ SỬA LỖI: image_url là property, nên phải để trong readonly_fields
    readonly_fields = ['image_preview'] 
    fields = ['image', 'image_preview', 'is_thumbnail', 'alt_text', 'display_order']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: auto;" />', obj.image.url)
        return ""
    image_preview.short_description = "Xem trước"

# Inline cho ProductVariant
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ['sku', 'price', 'stock', 'weight', 'option_combinations', 'is_active']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'name', 'base_price', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'is_featured']
    search_fields = ['name', 'model_code']
    inlines = [ProductImageInline, ProductVariantInline]
    
    # Tự động tạo slug từ name
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_id', 'name', 'parent', 'is_active']
    list_filter = ['parent', 'is_active']
    search_fields = ['name']

@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ['attribute_id', 'name', 'type', 'display_order']

@admin.register(ProductAttributeOption)
class ProductAttributeOptionAdmin(admin.ModelAdmin):
    list_display = ['option_id', 'product', 'attribute', 'value', 'is_available']
    list_filter = ['attribute', 'product']