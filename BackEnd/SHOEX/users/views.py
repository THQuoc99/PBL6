from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserRegistrationSerializer, CustomTokenObtainPairSerializer, UserProfileSerializer
from .models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

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
        
        return Response({
            "success": True,
            "message": "Đăng ký tài khoản thành công!",
            "token": str(refresh.access_token),
            "username": user.username,
            "full_name": user.full_name, 
            "email": user.email,    
            "user_id": user.id,        
            "phone": user.phone,  
        }, status=status.HTTP_201_CREATED)

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    API Endpoint để Đăng nhập (Login).
    Sử dụng Serializer đã tùy chỉnh.
    """
    serializer_class = CustomTokenObtainPairSerializer
    
class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API Endpoint để LẤY (GET) và CẬP NHẬT (PATCH)
    thông tin người dùng (full_name, phone, email).
    """
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated] # Chỉ cho phép người đã đăng nhập

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
        return Response(serializer.data, status=status.HTTP_200_OK)