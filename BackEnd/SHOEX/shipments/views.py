from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Shipment, ShipmentTracking
from .serializers import ShipmentSerializer, ShipmentTrackingSerializer

class ShipmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API Vận chuyển (Chỉ xem)
    Người dùng chỉ xem được vận đơn của chính mình (thông qua SubOrder -> Order -> Buyer)
    """
    serializer_class = ShipmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Lọc vận đơn thuộc về các đơn hàng của user đang đăng nhập
        return Shipment.objects.filter(sub_order__order__buyer=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['get'])
    def tracking(self, request, pk=None):
        """
        GET /api/shipments/{id}/tracking/
        Xem lịch sử di chuyển chi tiết của đơn hàng
        """
        shipment = self.get_object()
        history = shipment.tracking_history.all().order_by('-timestamp')
        serializer = ShipmentTrackingSerializer(history, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='track-by-code')
    def track_by_code(self, request):
        """
        GET /api/shipments/track-by-code/?code=SHOEX123456
        Tra cứu nhanh bằng mã vận đơn (Tracking Code)
        """
        code = request.query_params.get('code')
        if not code:
            return Response({'error': 'Vui lòng cung cấp mã vận đơn'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Chỉ cho phép tìm nếu đúng là đơn của user (bảo mật)
            shipment = Shipment.objects.get(
                tracking_code=code, 
                sub_order__order__buyer=request.user
            )
            serializer = self.get_serializer(shipment)
            return Response(serializer.data)
        except Shipment.DoesNotExist:
            return Response({'error': 'Không tìm thấy vận đơn hoặc bạn không có quyền truy cập'}, status=status.HTTP_404_NOT_FOUND)