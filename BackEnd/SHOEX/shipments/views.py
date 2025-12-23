from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Shipment, ShipmentTracking
from .serializers import ShipmentSerializer, ShipmentTrackingSerializer
from .ghtk_service import get_ghtk_service
from django.utils import timezone
from decimal import Decimal

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
    
    @action(detail=False, methods=['post'], url_path='calculate-fee')
    def calculate_shipping_fee(self, request):
        """
        POST /api/shipments/calculate-fee/
        Tính phí vận chuyển GHTK
        
        Body: {
            "province": "TP Hồ Chí Minh", 
            "district": "Quận 1",
            "weight": 1000,
            "value": 500000,
            "deliver_option": "none"  # hoặc "xteam" (nhanh)
        }
        
        Note: pick_province và pick_district sẽ lấy từ settings.WAREHOUSE_ADDRESS
              hoặc có thể override bằng cách gửi trong request body
        """
        from django.conf import settings
        ghtk = get_ghtk_service()
        
        # Lấy địa chỉ kho từ settings, có thể override từ request
        warehouse = settings.WAREHOUSE_ADDRESS
        pick_province = request.data.get('pick_province', warehouse['province'])
        pick_district = request.data.get('pick_district', warehouse['district'])
        
        # Lấy địa chỉ giao hàng từ request
        province = request.data.get('province')
        district = request.data.get('district')
        weight = request.data.get('weight', 1000)
        value = Decimal(request.data.get('value', 0))
        deliver_option = request.data.get('deliver_option', 'none')
        
        if not all([pick_province, pick_district, province, district]):
            return Response({
                'success': False,
                'message': 'Vui lòng cung cấp đầy đủ thông tin địa chỉ'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = ghtk.calculate_fee(
            pick_province=pick_province,
            pick_district=pick_district,
            province=province,
            district=district,
            weight=weight,
            value=value,
            deliver_option=deliver_option
        )
        
        return Response(result)
    
    @action(detail=True, methods=['post'], url_path='sync-ghtk-status')
    def sync_ghtk_status(self, request, pk=None):
        """
        POST /api/shipments/{id}/sync-ghtk-status/
        Đồng bộ trạng thái từ GHTK về hệ thống
        """
        shipment = self.get_object()
        
        if not shipment.tracking_code:
            return Response({
                'success': False,
                'message': 'Đơn hàng chưa có mã vận đơn GHTK'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        ghtk = get_ghtk_service()
        result = ghtk.get_order_status(shipment.tracking_code)
        
        if result['success']:
            order_data = result['order']
            
            # Cập nhật trạng thái shipment
            new_status = ghtk.convert_ghtk_status_to_internal(order_data['status'])
            shipment.status = new_status
            shipment.updated_at = timezone.now()
            shipment.save()
            
            # Tạo tracking history
            ShipmentTracking.objects.update_or_create(
                shipment=shipment,
                timestamp=order_data.get('modified', timezone.now()),
                defaults={
                    'status': order_data.get('status_text', ''),
                    'location': 'GHTK',
                    'details': f"Trạng thái: {order_data.get('status_text')}",
                    'carrier_status_code': str(order_data['status']),
                    'carrier_status_description': order_data.get('status_text', ''),
                    'api_response': order_data,
                    'sync_at': timezone.now()
                }
            )
            
            return Response({
                'success': True,
                'message': 'Đồng bộ trạng thái thành công',
                'status': new_status,
                'ghtk_status': order_data.get('status_text')
            })
        
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # Webhook từ GHTK, cần xác thực bằng cách khác
def ghtk_webhook(request):
    """
    POST /api/shipments/ghtk-webhook/
    Webhook nhận thông báo cập nhật từ GHTK
    
    GHTK sẽ POST dữ liệu khi có thay đổi trạng thái:
    {
        "partner_id": "ORDER_123",
        "label_id": "S12345678",
        "status_id": 5,
        "action_time": "2024-01-18 10:30:00",
        "reason_code": "",
        "reason": ""
    }
    """
    data = request.data
    
    # Xác thực webhook (nên kiểm tra IP hoặc secret key)
    # TODO: Implement webhook authentication
    
    label_id = data.get('label_id')
    status_id = data.get('status_id')
    action_time = data.get('action_time')
    
    if not label_id:
        return Response({'error': 'Missing label_id'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Tìm shipment theo tracking_code
        shipment = Shipment.objects.get(tracking_code=label_id)
        
        # Chuyển đổi status
        ghtk = get_ghtk_service()
        new_status = ghtk.convert_ghtk_status_to_internal(status_id)
        
        # Cập nhật shipment
        shipment.status = new_status
        shipment.save()
        
        # Lưu tracking history
        ShipmentTracking.objects.create(
            shipment=shipment,
            status=data.get('reason', f'Status {status_id}'),
            location='GHTK Webhook',
            details=f"{data.get('reason', 'Cập nhật trạng thái')}",
            timestamp=action_time or timezone.now(),
            carrier_status_code=str(status_id),
            carrier_status_description=data.get('reason'),
            api_response=data,
            sync_at=timezone.now()
        )
        
        return Response({
            'success': True,
            'message': 'Webhook processed successfully'
        })
        
    except Shipment.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Shipment not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)