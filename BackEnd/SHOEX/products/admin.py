from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from django.db import models
import itertools
from .models import Product, Category, ProductImage, ProductVariant, ProductAttribute, ProductAttributeOption

# ==============================================================================
# ACTION: TỰ ĐỘNG TẠO BIẾN THỂ (VARIANTS)
# ==============================================================================
@admin.action(description='⚡ Tự động tạo Biến thể từ các Tùy chọn đã nhập')
def generate_variants_action(modeladmin, request, queryset):
    for product in queryset:
        # 1. Lấy tất cả tùy chọn thuộc tính, sắp xếp theo thứ tự hiển thị của thuộc tính
        # Sắp xếp quan trọng để SKU luôn đồng nhất (VD: Luôn là Màu trước, Size sau)
        options = ProductAttributeOption.objects.filter(
            product=product, 
            is_available=True
        ).select_related('attribute').order_by('attribute__display_order', 'attribute__name')
        
        if not options.exists():
            modeladmin.message_user(request, f"⚠️ Sản phẩm '{product.name}' chưa có tùy chọn nào để tạo biến thể.", level=messages.WARNING)
            continue

        # 2. Gom nhóm theo tên thuộc tính
        attributes_map = {}
        for opt in options:
            attr_name = opt.attribute.name
            if attr_name not in attributes_map:
                attributes_map[attr_name] = []
            # Lưu giá trị vào list nếu chưa tồn tại (tránh trùng lặp logic)
            if opt.value not in attributes_map[attr_name]:
                attributes_map[attr_name].append(opt.value)

        # 3. Tạo tích Đề-các (Cartesian Product)
        # keys sẽ giữ thứ tự nhờ logic order_by phía trên
        keys = list(attributes_map.keys()) 
        values_lists = [attributes_map[k] for k in keys]
        combinations = list(itertools.product(*values_lists))

        created_count = 0
        existing_count = 0

        for combo in combinations:
            # Tạo Dictionary JSON: {"Màu sắc": "Đỏ", "Size": "40"}
            combination_dict = dict(zip(keys, combo))
            
            # Tạo SKU tự động: PRD-0001-DO-40
            sku_parts = [product.model_code if product.model_code else f"PRD-{product.pk}"]
            # Clean string cho SKU (Bỏ dấu cách, Chữ hoa)
            sku_parts.extend([str(v).upper().replace(" ", "").replace("/", "") for v in combo])
            generated_sku = "-".join(sku_parts)

            # 4. Tạo hoặc lấy biến thể
            # get_or_create sẽ dựa vào option_combinations để check trùng
            variant, created = ProductVariant.objects.get_or_create(
                product=product,
                option_combinations=combination_dict, 
                defaults={
                    'sku': generated_sku, # SKU chỉ được set nếu tạo mới
                    'price': product.base_price,
                    'stock': 0,
                    'weight': 0.1,
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
            else:
                existing_count += 1

        msg = f"✅ '{product.name}': Đã tạo {created_count} biến thể mới."
        if existing_count > 0:
            msg += f" (Bỏ qua {existing_count} biến thể đã tồn tại)"
        
        modeladmin.message_user(request, msg, level=messages.SUCCESS)


# ==============================================================================
# INLINES (Bảng con)
# ==============================================================================

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ['image_preview']
    fields = ['image', 'image_preview', 'is_thumbnail', 'alt_text', 'display_order']
    classes = ['collapse'] # Cho phép thu gọn nếu quá dài

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Preview"

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ['sku', 'option_combinations', 'price', 'stock', 'is_active']
    show_change_link = True # Cho phép click vào để sửa chi tiết biến thể
    classes = ['collapse']

class ProductAttributeOptionInline(admin.TabularInline):
    model = ProductAttributeOption
    extra = 1
    fields = ['attribute', 'value', 'value_code', 'image', 'is_available']
    # autocomplete_fields = ['attribute'] # Nếu danh sách thuộc tính quá dài thì bật cái này


# ==============================================================================
# ADMIN CLASSES (Quản lý chính)
# ==============================================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Thêm 'brand' và 'store' vào list_display
    list_display = ['product_id', 'image_tag', 'name', 'model_code', 'brand', 'store', 'base_price', 'count_variants', 'is_active']
    
    # SỬA QUAN TRỌNG: brand và store giờ là ForeignKey, phải dùng brand__name
    search_fields = ['name', 'model_code', 'brand__name', 'store__name']
    
    list_filter = ['is_active', 'is_featured', 'brand', 'category', 'store']
    
    inlines = [ProductImageInline, ProductAttributeOptionInline, ProductVariantInline]
    prepopulated_fields = {'slug': ('name',)}
    actions = [generate_variants_action]
   
    # Tối ưu query: Load trước khóa ngoại để không bị query lặp
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('brand', 'category', 'store')

    def image_tag(self, obj):
        # Lấy ảnh thumbnail đầu tiên để hiển thị ra list
        thumb = obj.product_images.filter(is_thumbnail=True).first()
        if not thumb:
             thumb = obj.product_images.first()
        
        if thumb and thumb.image:
            return format_html('<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px;" />', thumb.image.url)
        return "No Image"
    image_tag.short_description = "Ảnh"

    def count_variants(self, obj):
        # Sử dụng related_name='variants' đã định nghĩa trong model
        return obj.variants.count()
    count_variants.short_description = "Số biến thể"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_id', 'image_tag', 'name', 'parent', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['name']

    def image_tag(self, obj):
        if obj.thumbnail_image:
            return format_html('<img src="{}" style="width: 40px; height: 40px; object-fit: cover;" />', obj.thumbnail_image.url)
        return "-"
    image_tag.short_description = "Ảnh"

@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ['attribute_id', 'name', 'type', 'display_order', 'is_required']
    ordering = ['display_order']
    list_editable = ['display_order', 'is_required'] # Cho phép sửa nhanh thứ tự
    search_fields = ['name']
@admin.register(ProductAttributeOption)
class ProductAttributeOptionAdmin(admin.ModelAdmin):
    list_display = ['option_id', 'product', 'attribute', 'value', 'is_available']
    list_filter = ['attribute', 'is_available']
    search_fields = ['value', 'product__name']
    autocomplete_fields = ['product', 'attribute'] # Giúp chọn sản phẩm nhanh hơn nếu list dài