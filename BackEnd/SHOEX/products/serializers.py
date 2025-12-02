from rest_framework import serializers
from .models import Product, Category, ProductImage, ProductVariant

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        # option_combinations lưu JSON: {"Màu": "Đỏ", "Size": "39"}
        fields = ['variant_id', 'sku', 'price', 'stock', 'option_combinations']

class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['category_id', 'name', 'image', 'description']
        
    def get_image(self, obj):
        if obj.thumbnail_image:
            return obj.thumbnail_image.url
        return None

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    variants = ProductVariantSerializer(many=True, read_only=True)
    
    # Lấy thông tin Store từ quan hệ khóa ngoại
    store_name = serializers.CharField(source='store.name', read_only=True)
    store_id = serializers.CharField(source='store.store_id', read_only=True)
    
    # ✅ SỬA: Lấy Tên Thương Hiệu từ bảng Brand (thay vì lấy ID)
    brand = serializers.CharField(source='brand.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'product_id', 'name', 'description', 'base_price', 
            'image', 'slug', 'brand', 'rating', 'review_count',
            'store_name', 'store_id', 'variants'
        ]

    def get_image(self, obj):
        # 1. Ưu tiên ảnh thumbnail
        thumbnail = obj.product_images.filter(is_thumbnail=True).first()
        if thumbnail and thumbnail.image:
            return thumbnail.image.url
        
        # 2. Nếu không có, lấy ảnh đầu tiên trong danh sách
        first_img = obj.product_images.first()
        if first_img and first_img.image:
            return first_img.image.url
            
        return None