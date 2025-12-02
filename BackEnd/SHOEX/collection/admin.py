from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Collection, ProductCollection


class ProductCollectionInline(admin.TabularInline):
    """Inline để quản lý sản phẩm trong bộ sưu tập"""
    model = ProductCollection
    extra = 0
    raw_id_fields = ('product',)
    fields = ('product', 'is_featured_in_collection', 'added_at')
    readonly_fields = ('added_at',)


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = (
        'collection_id', 'name', 'featured', 'season_display', 
        'product_count', 'display_order', 'is_active', 'created_at'
    )
    list_filter = ('featured', 'season', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'collection_id')
    list_editable = ('featured', 'is_active', 'display_order')
    ordering = ('display_order', '-featured', '-created_at')
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('collection_id', 'name', 'description', 'image')
        }),
        ('Phân loại', {
            'fields': ('season', 'featured', 'display_order')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Cài đặt', {
            'fields': ('is_active',)
        })
    )
    
    readonly_fields = ('product_count',)
    inlines = [ProductCollectionInline]
    
    def season_display(self, obj):
        """Hiển thị mùa"""
        return obj.get_season_display()
    season_display.short_description = "Mùa/Thời gian"
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Cập nhật số lượng sản phẩm sau khi lưu
        obj.update_product_count()


@admin.register(ProductCollection)
class ProductCollectionAdmin(admin.ModelAdmin):
    list_display = ('product', 'collection', 'is_featured_in_collection', 'added_at')
    list_filter = ('collection', 'is_featured_in_collection', 'added_at')
    search_fields = ('product__name', 'collection__name')
    raw_id_fields = ('product',)
    date_hierarchy = 'added_at'
