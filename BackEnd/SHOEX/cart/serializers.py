from rest_framework import serializers
from .models import Cart, CartItem
from products.models import ProductImage

class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='variant.product.product_id', read_only=True)
    product_name = serializers.CharField(source='variant.product.name', read_only=True)
    brand = serializers.CharField(source='variant.product.brand', read_only=True)
    price = serializers.DecimalField(source='variant.price', max_digits=12, decimal_places=2, read_only=True)
    attributes = serializers.JSONField(source='variant.option_combinations', read_only=True)
    image = serializers.SerializerMethodField()
    sub_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['item_id', 'variant', 'product_id', 'product_name', 'brand', 'attributes', 
                  'quantity', 'price', 'image', 'sub_total']

    def get_image(self, obj):
        try:
            product = obj.variant.product
            thumbnail = product.gallery_images.filter(is_thumbnail=True).first()
            if thumbnail: return thumbnail.image.url
            first_img = product.gallery_images.first()
            if first_img: return first_img.image.url
            return None
        except:
            return None

    def get_sub_total(self, obj):
        return obj.variant.price * obj.quantity

class CartSerializer(serializers.ModelSerializer):
    # ✅ SỬA LỖI: Bỏ source='items' vì tên field đã là 'items' rồi
    items = CartItemSerializer(many=True, read_only=True) 
    
    total_amount = serializers.SerializerMethodField()
    total_items = serializers.IntegerField(read_only=True) # property count items

    class Meta:
        model = Cart
        fields = ['cart_id', 'total_amount', 'total_items', 'items']

    def get_total_amount(self, obj):
        return obj.total_amount