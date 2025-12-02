from rest_framework import serializers
from .models import Store, AddressStore, StoreImage, StoreFollower

class AddressStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressStore
        fields = ['address_id', 'province', 'ward', 'detail', 'is_default']

class StoreImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreImage
        fields = ['image', 'title']

class StoreSerializer(serializers.ModelSerializer):
    addresses = AddressStoreSerializer(many=True, read_only=True)
    images = StoreImageSerializer(many=True, read_only=True)
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = [
            'store_id', 'name', 'slug', 'description', 
            'avatar', 'cover_image', 'rating', 
            'followers_count', 'products_count', 
            'is_verified', 'addresses', 'images', 'is_following'
        ]

    def get_is_following(self, obj):
        """Kiểm tra user hiện tại có follow shop không"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return StoreFollower.objects.filter(store=obj, user=request.user, is_active=True).exists()
        return False