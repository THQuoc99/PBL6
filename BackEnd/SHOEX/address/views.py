from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Address
from .serializers import AddressSerializer

class UserAddressViewSet(viewsets.ModelViewSet):
    """
    API endpoint quản lý địa chỉ nhận hàng của User.
    """
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Chỉ lấy địa chỉ của user hiện tại
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Tự động gán user khi tạo mới
        serializer.save(user=self.request.user)
        
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)