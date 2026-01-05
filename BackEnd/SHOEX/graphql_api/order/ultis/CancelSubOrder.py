import requests
from django.conf import settings
from django.utils import timezone
from shipments.models import Shipment, ShipmentTracking


def cancel_ghtk_order(*, shipment_id: int, reason: str = ""):
    """
    Hủy đơn GHTK theo shipment_id
    """

    shipment = Shipment.objects.get(pk=shipment_id)

    if not shipment.tracking_code:
        raise Exception("Shipment has no GHTK tracking code")

    # ===== Call GHTK Cancel API =====
    url = f"{settings.GHTK_BASE_URL}/services/shipment/cancel/{shipment.tracking_code}"

    headers = {
        "Token": settings.GHTK_API_TOKEN,
        "X-Client-Source": settings.GHTK_PARTNER_CODE,
        "Content-Type": "application/json",
    }

    payload = {
        "reason": reason or "Khách yêu cầu hủy đơn"
    }

    print("Cancel GHTK order payload:", payload)

    res = requests.post(url, json=payload, headers=headers, timeout=15)
    data = res.json()

    if not data.get("success"):
        raise Exception(data.get("message", "Cancel GHTK order failed"))

    # ===== Update Shipment =====
    shipment.status = "cancelled"
    shipment.updated_at = timezone.now()
    shipment.save(update_fields=["status", "updated_at"])

    # ===== Tracking Log =====
    ShipmentTracking.objects.create(
        shipment=shipment,
        label_id=shipment.tracking_code,
        partner_id=None,
        carrier_status="cancelled",
        carrier_status_text="Đã hủy đơn GHTK",
        raw_response=data,
        weight=shipment.total_weight,
        message=data.get("message"),
    )

    return {
        "shipment_id": shipment.shipment_id,
        "tracking_code": shipment.tracking_code,
        "status": "cancelled",
    }
