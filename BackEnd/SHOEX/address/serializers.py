from rest_framework import serializers
from .models import Address

class AddressSerializer(serializers.ModelSerializer):
    full_address = serializers.CharField(read_only=True)
    
    class Meta:
        model = Address
        fields = [
            'address_id', 
            'user', 
            'province', 
            'ward', 
            'hamlet', 
            'detail', 
            'is_default',
            'full_address',
            'name',
            'phone'
        ]
        read_only_fields = ['user'] # User lấy từ request.user

    def create(self, validated_data):
        return super().create(validated_data)