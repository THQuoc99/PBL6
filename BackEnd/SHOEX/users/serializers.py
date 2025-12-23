from rest_framework import serializers
import re
from django.core.validators import validate_email as django_validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
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

    def validate_username(self, value):
        """Kiểm tra username đã tồn tại chưa"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Tên đăng nhập này đã tồn tại.")
        return value

    def validate_email(self, value):
        """Kiểm tra định dạng email và đã được đăng ký chưa"""
        # normalize
        if value:
            value = value.strip().lower()

        # format check using Django validator
        try:
            django_validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError("Email không đúng định dạng.")

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email này đã được đăng ký.")
        return value

    def validate_phone(self, value):
        """Kiểm tra định dạng số điện thoại và đã được đăng ký chưa.

        Hỗ trợ định dạng quốc gia cơ bản: chỉ cho phép số, có thể có dấu + ở đầu, độ dài 7..15.
        """
        if not value:
            raise serializers.ValidationError("Số điện thoại không được để trống.")

        phone = value.strip()
        # VN mobile regex: starts with +84 or 0, then operator 3/5/7/8/9, then 8 digits
        if not re.match(r'^(?:\+84|0)(?:3|5|7|8|9)\d{8}$', phone):
            raise serializers.ValidationError("Số điện thoại không đúng định dạng Việt Nam.")

        if User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError("Số điện thoại này đã được đăng ký.")
        return phone

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Mật khẩu xác nhận không khớp."})
        
        if 'role' not in attrs or not attrs['role']:
             attrs['role'] = 'buyer'
        # normalize email if present
        if 'email' in attrs and attrs['email']:
            attrs['email'] = attrs['email'].strip().lower()
             
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

    def validate_phone(self, value):
        user = self.instance
        # Kiểm tra trùng số điện thoại khi update
        if not value:
            raise serializers.ValidationError("Số điện thoại không được để trống.")

        phone = value.strip()
        if not re.match(r'^(?:\+84|0)(?:3|5|7|8|9)\d{8}$', phone):
            raise serializers.ValidationError("Số điện thoại không đúng định dạng Việt Nam.")

        if user and User.objects.filter(phone=phone).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("Số điện thoại này đã được sử dụng bởi tài khoản khác.")
        return phone