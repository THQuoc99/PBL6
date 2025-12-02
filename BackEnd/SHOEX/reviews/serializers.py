from rest_framework import serializers
from .models import Review, ReviewImage, ReviewVideo, ReviewHelpful
from orders.models import OrderItem

class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ['image_id', 'image', 'caption']

class ReviewVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewVideo
        fields = ['video_id', 'video', 'thumbnail']

class ReviewSerializer(serializers.ModelSerializer):
    images = ReviewImageSerializer(many=True, read_only=True)
    videos = ReviewVideoSerializer(many=True, read_only=True)
    
    # Lấy thông tin người đánh giá
    user_name = serializers.CharField(source='order_item.order.buyer.full_name', read_only=True)
    user_avatar = serializers.ImageField(source='order_item.order.buyer.avatar', read_only=True)
    
    # Lấy thông tin biến thể đã mua (Màu/Size)
    variant_info = serializers.JSONField(source='order_item.variant.option_combinations', read_only=True)
    
    helpful_count = serializers.SerializerMethodField()
    is_helpful_by_me = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'review_id', 'rating', 'comment', 'created_at',
            'size_accuracy', 'color_accuracy', 'material_quality',
            'images', 'videos', 
            'user_name', 'user_avatar', 'variant_info',
            'helpful_count', 'is_helpful_by_me'
        ]

    def get_helpful_count(self, obj):
        return obj.helpful_votes.filter(is_helpful=True).count()

    def get_is_helpful_by_me(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.helpful_votes.filter(user=request.user, is_helpful=True).exists()
        return False

class CreateReviewSerializer(serializers.ModelSerializer):
    # Dùng để upload ảnh/video (nếu dùng Multipart/Form-data)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True, required=False
    )
    
    class Meta:
        model = Review
        fields = [
            'order_item', 'rating', 'comment', 
            'size_accuracy', 'color_accuracy', 'material_quality',
            'uploaded_images'
        ]

    def validate_order_item(self, value):
        # Kiểm tra xem người dùng hiện tại có phải là chủ đơn hàng không
        user = self.context['request'].user
        if value.order.buyer != user:
            raise serializers.ValidationError("Bạn không có quyền đánh giá đơn hàng này.")
        return value

    def create(self, validated_data):
        images_data = validated_data.pop('uploaded_images', [])
        review = Review.objects.create(**validated_data)
        
        # Lưu ảnh
        for img in images_data:
            ReviewImage.objects.create(review=review, image=img)
            
        return review