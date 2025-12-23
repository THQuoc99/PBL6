from rest_framework import serializers
from .models import ReturnRequest, ReturnItem, ReturnImage, ReturnTracking
from orders.models import OrderItem


class ReturnItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='order_item.variant.product.name', read_only=True)
    product_image = serializers.SerializerMethodField()
    
    class Meta:
        model = ReturnItem
        fields = ['order_item', 'product_name', 'product_image', 'quantity']
    
    def get_product_image(self, obj):
        try:
            img = obj.order_item.variant.product.product_images.filter(is_thumbnail=True).first()
            if img and img.image:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(img.image.url)
                return img.image.url
        except:
            pass
        return None


class ReturnImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnImage
        fields = ['image', 'uploaded_at']
        read_only_fields = ['uploaded_at']


class ReturnTrackingSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.email', read_only=True)
    
    class Meta:
        model = ReturnTracking
        fields = ['status', 'note', 'created_by_name', 'created_at']
        read_only_fields = ['created_at']


class ReturnRequestSerializer(serializers.ModelSerializer):
    items = ReturnItemSerializer(many=True, read_only=True)
    images = ReturnImageSerializer(many=True, read_only=True)
    tracking_history = ReturnTrackingSerializer(many=True, read_only=True)
    
    buyer_name = serializers.CharField(source='buyer.email', read_only=True)
    order_id = serializers.IntegerField(source='order.order_id', read_only=True)
    
    class Meta:
        model = ReturnRequest
        fields = [
            'return_id', 'order_id', 'buyer_name', 'return_type', 'reason',
            'description', 'refund_amount', 'status', 'return_tracking_code',
            'shop_response', 'reject_reason', 'created_at', 'updated_at',
            'approved_at', 'completed_at', 'items', 'images', 'tracking_history'
        ]
        read_only_fields = ['return_id', 'created_at', 'updated_at', 'approved_at', 'completed_at']


class CreateReturnRequestSerializer(serializers.Serializer):
    """Serializer để tạo yêu cầu trả hàng mới"""
    
    order_id = serializers.IntegerField()
    sub_order_id = serializers.IntegerField(required=False, allow_null=True)
    return_type = serializers.ChoiceField(choices=ReturnRequest.TYPE_CHOICES)
    reason = serializers.ChoiceField(choices=ReturnRequest.REASON_CHOICES)
    description = serializers.CharField(max_length=1000)
    
    # Danh sách sản phẩm trả
    items = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField()),
        help_text="[{'order_item_id': 1, 'quantity': 2}]"
    )
    
    # Upload ảnh (optional)
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        allow_empty=True
    )
