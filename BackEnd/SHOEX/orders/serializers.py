from rest_framework import serializers
from .models import Order, SubOrder, OrderItem
from address.serializers import AddressSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='variant.product.name', read_only=True)
    product_image = serializers.SerializerMethodField()
    attributes = serializers.JSONField(source='variant.option_combinations', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['item_id', 'product_name', 'product_image', 'quantity', 'price_at_order', 'discount_amount', 'attributes']

    def get_product_image(self, obj):
        # Lấy ảnh thumbnail từ sản phẩm
        try:
            img = obj.variant.product.product_images.filter(is_thumbnail=True).first()
            if img: return img.image.url
            return None
        except: return None

class SubOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)

    class Meta:
        model = SubOrder
        # subtotal thay vì total_amount
        fields = ['sub_order_id', 'store_name', 'subtotal', 'status', 'tracking_number', 'items']

class OrderSerializer(serializers.ModelSerializer):
    sub_orders = SubOrderSerializer(many=True, read_only=True)
    address = AddressSerializer(read_only=True) 
    
    class Meta:
        model = Order
        fields = [
            'order_id', 'total_amount', 'shipping_fee', 
            'status', 'payment_status', 'payment_method', 
            'notes', 'created_at', 'address', 'sub_orders'
        ]