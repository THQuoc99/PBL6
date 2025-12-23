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
    product_id = serializers.IntegerField(write_only=True, required=False)
    variant_id = serializers.IntegerField(write_only=True, required=False)
    order_item = serializers.PrimaryKeyRelatedField(
        queryset=OrderItem.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Review
        fields = [
            'order_item', 'product_id', 'variant_id', 'rating', 'comment',
            'size_accuracy', 'color_accuracy', 'material_quality',
        ]

    def validate(self, attrs):
        request = self.context['request']
        user = request.user

        order_item = attrs.get('order_item')
        product_id = attrs.get('product_id')
        variant_id = attrs.get('variant_id')

        if order_item is None and product_id is None:
            raise serializers.ValidationError("Phải cung cấp 'order_item' hoặc 'product_id'.")

        # If order_item provided: verify ownership
        if order_item is not None:
            if order_item.order.buyer != user:
                raise serializers.ValidationError("Bạn không có quyền đánh giá đơn hàng này.")
            return attrs

        # product_id provided: ensure int
        try:
            product_id_int = int(product_id)
        except Exception:
            raise serializers.ValidationError("product_id không hợp lệ.")

        qs = OrderItem.objects.filter(
            order__buyer=user,
            order__status='completed',
            variant__product_id=product_id_int
        ).order_by('-order__created_at')

        # If variant_id provided, narrow down to that variant
        if variant_id is not None:
            try:
                variant_id_int = int(variant_id)
                qs = qs.filter(variant__variant_id=variant_id_int)
            except Exception:
                raise serializers.ValidationError("variant_id không hợp lệ.")

        candidate = qs.first()

        if not candidate:
            raise serializers.ValidationError("Không tìm thấy sản phẩm đã mua phù hợp để đánh giá.")

        attrs['order_item'] = candidate
        attrs.pop('product_id', None)
        attrs.pop('variant_id', None)
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        # Extract files from request.FILES (works for multipart uploads where files are named 'uploaded_images')
        files = []
        if request is not None:
            files = request.FILES.getlist('uploaded_images')

        review = Review.objects.create(**validated_data)

        # Save uploaded images (if any)
        for f in files:
            ReviewImage.objects.create(review=review, image=f)

        return review