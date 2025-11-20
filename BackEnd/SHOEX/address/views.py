from rest_framework import viewsets, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Province, Ward, Hamlet, Address
from .serializers import ProvinceSerializer, WardSerializer, HamletSerializer, AddressSerializer

# --- API ĐỊA CHÍNH ---
class ProvinceListView(generics.ListAPIView):
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer
    permission_classes = [AllowAny]

# (Đã xóa Class DistrictListView)

class WardListView(generics.ListAPIView):
    serializer_class = WardSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        # Lọc Ward theo province_id
        province_id = self.request.query_params.get('province_id')
        if province_id:
            return Ward.objects.filter(province_id=province_id)
        return Ward.objects.none()

class HamletListView(generics.ListAPIView):
    serializer_class = HamletSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        # Lọc Hamlet theo ward_id
        ward_id = self.request.query_params.get('ward_id')
        if ward_id:
            return Hamlet.objects.filter(ward_id=ward_id)
        return Hamlet.objects.none()

# --- API ĐỊA CHỈ USER ---
class UserAddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Xử lý logic địa chỉ mặc định
        if serializer.validated_data.get('is_default', False):
             Address.objects.filter(user=self.request.user).update(is_default=False)
        serializer.save(user=self.request.user)