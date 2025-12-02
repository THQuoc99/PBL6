from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Trả về thêm avatar url trong token response nếu cần
        avatar_url = None
        if self.user.avatar:
            try:
                # Nếu dùng storage local, cần đảm bảo url đầy đủ
                avatar_url = self.user.avatar.url
            except:
                pass

        return {
            'success': True,
            'token': data['access'],
            'refresh': data['refresh'],
            'username': self.user.username,
            'full_name': self.user.full_name, 
            'email': self.user.email,
            'user_id': self.user.id,       
            'phone': self.user.phone, 
            'role': self.user.role,
            'avatar': avatar_url,
            
            # --- QUAN TRỌNG: Trả về ngày sinh khi login ---
            'birth_date': self.user.birth_date, 
            # ----------------------------------------------
            
            'message': 'Đăng nhập thành công!'
        }

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label="Xác nhận mật khẩu")

    class Meta:
        model = User
        fields = (
            'username', 'password', 'password2', 'email', 
            'full_name', 'phone', 'role', 'birth_date' 
        )

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Mật khẩu xác nhận không khớp."})
        
        if 'role' not in attrs or not attrs['role']:
             attrs['role'] = 'buyer'
             
        return attrs

    def create(self, validated_data):
        # Tách password ra để dùng set_password
        password = validated_data.pop('password')
        validated_data.pop('password2')
        
        # Tách birth_date ra xử lý riêng nếu cần
        birth_date = validated_data.pop('birth_date', None)

        user = User.objects.create(
            **validated_data
        )
        
        if birth_date:
            user.birth_date = birth_date

        user.set_password(password)
        user.save()
        return user
    
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Cho phép update thêm avatar và ngày sinh
        fields = ['full_name', 'phone', 'email', 'avatar', 'birth_date']
        extra_kwargs = {
            'email': {'required': False},
            'full_name': {'required': False},
            'phone': {'required': False},
            'avatar': {'required': False},
            'birth_date': {'required': False},
        }

    def validate_email(self, value):
        user = self.instance 
        # Chỉ kiểm tra trùng email khi update (user đã tồn tại)
        if user and User.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("Email này đã được sử dụng bởi tài khoản khác.")
        return value