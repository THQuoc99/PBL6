from rest_framework import serializers
from .models import Shipment, ShipmentTracking

class ShipmentTrackingSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ShipmentTracking
        fields = [
            'tracking_id', 'status', 'status_display', 
            'location', 'details', 'timestamp', 
            'carrier_status_description'
        ]

class ShipmentSerializer(serializers.ModelSerializer):
    # Hiển thị thông tin đơn hàng con liên quan
    order_id = serializers.IntegerField(source='sub_order.order.order_id', read_only=True)
    store_name = serializers.CharField(source='sub_order.store.name', read_only=True)
    
    # Hiển thị trạng thái tiếng Việt
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    transport_display = serializers.CharField(source='get_transport_display', read_only=True)
    
    # Lấy lịch sử tracking (chỉ lấy 3 mốc gần nhất để list gọn gàng, chi tiết thì gọi API riêng)
    tracking_history = serializers.SerializerMethodField()

    class Meta:
        model = Shipment
        fields = [
            'shipment_id', 'order_id', 'store_name',
            'tracking_code', 'status', 'status_display',
            'transport', 'transport_display',
            'pick_date', 'estimated_delivery_date', # Nếu bạn có thêm field này, nếu không thì bỏ
            'name', 'phone', 'address', 'full_address', # Thông tin người nhận
            'is_freeship', 'cod_amount', # pick_money
            'tracking_history'
        ]
        # Map lại tên field cho frontend dễ hiểu nếu cần
        extra_kwargs = {
            'pick_money': {'source': 'cod_amount'}
        }

    def get_tracking_history(self, obj):
        # Lấy 3 trạng thái mới nhất
        history = obj.tracking_history.order_by('-timestamp')[:3]
        return ShipmentTrackingSerializer(history, many=True).data

    # Custom field: Địa chỉ đầy đủ
    full_address = serializers.SerializerMethodField()
    
    def get_full_address(self, obj):
        parts = [obj.address]
        if obj.hamlet: parts.append(obj.hamlet)
        parts.extend([obj.ward, obj.province])
        return ", ".join(filter(None, parts))