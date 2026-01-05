# shipping/webhooks.py
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now

from .models import Shipment, ShipmentTracking
from .constants import GHTK_STATUS_TO_SHIPMENT


@csrf_exempt
def ghtk_webhook(request):
    """
    Webhook nhận cập nhật trạng thái từ GHTK
    - Lưu lịch sử tracking (RAW)
    - Map trạng thái tổng cho Shipment
    """

    if request.method != 'POST':
        return HttpResponse(status=405)

    data = request.POST

    # ===== 1. Parse dữ liệu =====
    label_id = data.get('label_id')            # mã vận đơn GHTK
    partner_id = data.get('partner_id')        # mã SubOrder (tham khảo)
    status_id = data.get('status_id')
    action_time = data.get('action_time')
    reason = data.get('reason', '')
    reason_code = data.get('reason_code', '')

    # Validate tối thiểu
    if not label_id or not status_id:
        return HttpResponse(status=200)

    try:
        status_id = int(status_id)
    except ValueError:
        return HttpResponse(status=200)

    event_time = parse_datetime(action_time) if action_time else now()

    # ===== 2. Tìm shipment =====
    try:
        shipment = Shipment.objects.get(tracking_code=label_id)
    except Shipment.DoesNotExist:
        # Không tìm thấy vẫn trả 200 để GHTK không retry
        return HttpResponse(status=200)

    # ===== 3. Lưu TRACKING (RAW – không ép logic) =====
    ShipmentTracking.objects.create(
        shipment=shipment,
        carrier_status_code=str(status_id),
        carrier_status_description=reason,
        location='GHTK',
        timestamp=event_time,
        details=f"{reason_code} - {reason}".strip(' -'),
        api_response=dict(data),
    )

    # ===== 4. Map trạng thái chính cho Shipment =====
    shipment_status = GHTK_STATUS_TO_SHIPMENT.get(status_id)

    # ❌ KHÔNG cho webhook set trạng thái "pending"
    if shipment_status and shipment_status != 'pending':
        if shipment.status != shipment_status:
            shipment.status = shipment_status
            shipment.updated_at = now()
            shipment.save(update_fields=['status', 'updated_at'])

    # ===== 5. ACK cho GHTK =====
    return HttpResponse(status=200)
