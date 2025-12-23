from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserRegistrationSerializer, CustomTokenObtainPairSerializer, UserProfileSerializer
from .models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser


class ChangePasswordView(APIView):
    """REST API endpoint để đổi mật khẩu (POST).

    Body: { "current_password": "...", "new_password": "..." }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        current = request.data.get('current_password')
        new = request.data.get('new_password')

        if not current or not new:
            return Response({'error': 'Thiếu current_password hoặc new_password'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(current):
            return Response({'error': 'Mật khẩu hiện tại không đúng'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(new, user)
        except ValidationError as e:
            return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user.set_password(new)
            user.save()
            return Response({'success': True, 'message': 'Đổi mật khẩu thành công'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserRegistrationView(generics.CreateAPIView):
    """
    API Endpoint để Đăng ký người dùng mới (Register).
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,) # Cho phép bất kỳ ai đăng ký
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            # Trả về lỗi 400 với message thân thiện
             return Response({
                "success": False,
                "message": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
            
        user = serializer.save()
        
        # Tạo token cho người dùng vừa đăng ký
        refresh = RefreshToken.for_user(user)
        
        # Lấy URL avatar nếu có (đề phòng user không up ảnh)
        avatar_url = None
        if user.avatar:
            try:
                avatar_url = request.build_absolute_uri(user.avatar.url)
            except:
                avatar_url = user.avatar.url

        return Response({
            "success": True,
            "message": "Đăng ký tài khoản thành công!",
            "token": str(refresh.access_token),
            "user_id": user.id,        
            "username": user.username,
            "full_name": user.full_name, 
            "email": user.email,    
            "phone": user.phone,  
            # --- CÁC TRƯỜNG MỚI TỪ DB MỚI ---
            "role": user.role,
            "avatar": avatar_url,
            "birth_date": user.birth_date
        }, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    API Endpoint để Đăng nhập (Login).
    Sử dụng Serializer đã tùy chỉnh để trả về full info + avatar.
    """
    serializer_class = CustomTokenObtainPairSerializer
    
class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API Endpoint để LẤY (GET) và CẬP NHẬT (PATCH)
    thông tin người dùng (full_name, phone, email, avatar, birth_date).
    """
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated] # Chỉ cho phép người đã đăng nhập
    parser_classes = [JSONParser, MultiPartParser, FormParser]  # Cho phép tải lên tệp tin

    def get_object(self):
        # Trả về thông tin của chính user đang gửi request
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True) # Cho phép cập nhật PATCH (chỉ 1 phần)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Trả về dữ liệu mới nhất (đã cập nhật)
        return Response({
            "success": True,
            "message": "Cập nhật thông tin thành công",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

class UploadAvatarView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        avatar_file = request.FILES.get('avatar')
        if not avatar_file:
            return Response({'success': False, 'message': 'Không tìm thấy file avatar'}, status=400)
        user = request.user
        user.avatar = avatar_file
        user.save()
        try:
            avatar_url = request.build_absolute_uri(user.avatar.url)
        except:
            avatar_url = user.avatar.url
        return Response({'success': True, 'avatar': avatar_url}, status=200)