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
        """
        Lấy ảnh thumbnail từ ProductImage model.
        Sau khi chạy command fix_product_images, đường dẫn sẽ đúng format.
        """
        try:
            request = self.context.get('request')
            product = obj.variant.product
            
            # Lấy thumbnail từ ProductImage
            img = product.product_images.filter(is_thumbnail=True).first()
            
            if img and img.image:
                # Dùng img.image.url - Django tự động thêm MEDIA_URL
                if request:
                    return request.build_absolute_uri(img.image.url)
                return img.image.url
            
            # Fallback: Generate URL nếu không có ProductImage
            if request:
                fallback_url = f'/media/products/{product.product_id}/{product.product_id}_0.jpg'
                return request.build_absolute_uri(fallback_url)
            
            return None
        except Exception as e:
            print(f"Error getting product image: {e}")
            return None

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
    has_return_request = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'order_id', 'total_amount', 'shipping_fee', 
            'status', 'payment_status', 'payment_method', 
            'notes', 'created_at', 'address', 'sub_orders', 'has_return_request'
        ]
    
    def get_has_return_request(self, obj):
        """Check if order has any return request"""
        return obj.return_requests.filter(
            status__in=['pending', 'approved', 'shipping_back', 'received', 'completed']
        ).exists()