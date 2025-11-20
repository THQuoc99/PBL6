from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        return {
            'success': True,
            'token': data['access'],
            'refresh': data['refresh'],
            'username': self.user.username,
            'full_name': self.user.full_name, 
            'email': self.user.email,
            'user_id': self.user.id,       
            'phone': self.user.phone, 
            'message': 'Đăng nhập thành công!'
        }

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer Đăng ký (Register)
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label="Xác nhận mật khẩu")

    class Meta:
        model = User
        fields = (
            'username', 'password', 'password2', 'email', 
            'full_name', 'phone', 'role'
        )

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Mật khẩu xác nhận không khớp."})
        
        # Gán vai trò mặc định là 'buyer' nếu không được cung cấp
        if 'role' not in attrs or not attrs['role']:
             attrs['role'] = 'buyer'
             
        return attrs

    def create(self, validated_data):
        # Băm mật khẩu và tạo User
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            phone=validated_data['phone'],
            role=validated_data['role']
        )
        
        user.set_password(validated_data['password'])
        user.save()
        
        return user
    
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Chỉ cho phép cập nhật 3 trường này
        fields = ['full_name', 'phone', 'email']
        extra_kwargs = {
            'email': {'required': False}, # Cho phép cập nhật riêng lẻ
            'full_name': {'required': False},
            'phone': {'required': False},
        }

    def validate_email(self, value):
        # Kiểm tra xem email mới có bị trùng với người dùng khác không
        user = self.instance # Lấy user hiện tại
        if User.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("Email này đã được sử dụng bởi tài khoản khác.")
        return value