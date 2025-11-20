from rest_framework import serializers
from .models import Product, Category, ProductImage, ProductVariant

# 1. Tạo Serializer cho Variant (Mới thêm)
class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['variant_id', 'sku', 'price', 'stock', 'option_combinations']

class CategorySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(source='thumbnail_image', read_only=True)

    class Meta:
        model = Category
        fields = ['category_id', 'name', 'image', 'description'] 

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    # 2. Thêm field variants vào đây (Mới thêm)
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        # 3. Nhớ thêm 'variants' vào danh sách fields
        fields = ['product_id', 'name', 'description', 'base_price', 'image', 'slug', 'brand', 'variants']

    def get_image(self, obj):
        # Logic lấy ảnh (giữ nguyên của bạn)
        # 1. Ưu tiên ảnh thumbnail
        thumbnail = obj.gallery_images.filter(is_thumbnail=True).first()
        if thumbnail and thumbnail.image:
            try:
                return thumbnail.image.url
            except:
                return None
        
        # 2. Nếu không có thumbnail, lấy ảnh đầu tiên
        first_img = obj.gallery_images.first()
        if first_img and first_img.image:
            try:
                return first_img.image.url
            except:
                return None
                
        return None