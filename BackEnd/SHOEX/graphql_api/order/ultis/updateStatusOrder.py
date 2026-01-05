import json
from typing import List, Dict, Any

import requests
from django.conf import settings
from django.utils import timezone

from orders.models import Order, SubOrder
from shipments.models import Shipment, ShipmentTracking
from shipments import constants as shipment_constants


def update_status_for_order(order_id: int, timeout: int = 15) -> List[Dict[str, Any]]:
    """
    Lấy trạng thái từ GHTK cho tất cả `shipment.tracking_code` thuộc `order_id`.

    - Gọi endpoint GET /services/shipment/v2/{tracking_code}
    - Tạo một bản ghi `ShipmentTracking` với `raw_response`
    - Map trạng thái GHTK sang `Shipment.status` theo `shipments/constants.py`

    Trả về danh sách kết quả cho mỗi shipment đã xử lý.
    """

    try:
        order = (
            Order.objects
            .prefetch_related('sub_orders__shipment')
            .get(pk=order_id)
        )
    except Order.DoesNotExist:
        raise

    results: List[Dict[str, Any]] = []

    headers = {
        "Token": getattr(settings, 'GHTK_API_TOKEN', ''),
        "X-Client-Source": getattr(settings, 'GHTK_PARTNER_CODE', ''),
        "Content-Type": "application/json",
    }

    for sub_order in order.sub_orders.all():
        # Delegate to suborder-level updater
        try:
            res = update_status_for_suborder(sub_order.sub_order_id, timeout=timeout)
        except Exception as e:
            res = {"sub_order_id": sub_order.sub_order_id, "success": False, "error": str(e)}
        results.append(res)

    return results


__all__ = ["update_status_for_order", "update_status_for_suborder"]


def update_status_for_suborder(sub_order_id: int, timeout: int = 15) -> Dict[str, Any]:
    """
    Update shipment status and tracking for a single SubOrder identified by `sub_order_id`.
    Returns a result dict similar to the per-item results produced by `update_status_for_order`.
    """
    try:
        sub_order = SubOrder.objects.select_related('shipment').get(pk=sub_order_id)
    except SubOrder.DoesNotExist:
        raise

    shipment = getattr(sub_order, 'shipment', None)
    if not shipment:
        return {"sub_order_id": sub_order_id, "skipped": True, "reason": "no_shipment"}

    tracking_code = shipment.tracking_code
    if not tracking_code:
        return {"sub_order_id": sub_order_id, "shipment_id": shipment.shipment_id, "skipped": True, "reason": "no_tracking_code"}

    headers = {
        "Token": getattr(settings, 'GHTK_API_TOKEN', ''),
        "X-Client-Source": getattr(settings, 'GHTK_PARTNER_CODE', ''),
        "Content-Type": "application/json",
    }

    url = f"{getattr(settings, 'GHTK_BASE_URL', '').rstrip('/')}/services/shipment/v2/{tracking_code}"

    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        data = resp.json()
    except Exception as e:  # network / json errors
        ShipmentTracking.objects.create(
            shipment=shipment,
            label_id=tracking_code,
            partner_id=None,
            carrier_status=None,
            carrier_status_text=f"fetch_error: {str(e)}",
            raw_response={"error": str(e)},
        )
        return {"sub_order_id": sub_order_id, "shipment_id": shipment.shipment_id, "tracking_code": tracking_code, "success": False, "error": str(e)}

    # Lưu raw response và parse
    if not data.get('success'):
        ShipmentTracking.objects.create(
            shipment=shipment,
            label_id=tracking_code,
            partner_id=data.get('order', {}).get('partner_id') if isinstance(data.get('order'), dict) else None,
            carrier_status=None,
            carrier_status_text=data.get('message'),
            raw_response=data,
        )
        return {"sub_order_id": sub_order_id, "shipment_id": shipment.shipment_id, "tracking_code": tracking_code, "success": False, "error": data.get('message')}

    ghtk_order = data.get('order', {}) or {}

    # Thử lấy mã trạng thái từ nhiều trường khả dĩ
    status_candidates = [ghtk_order.get(k) for k in ('status_id', 'status', 'status_code', 'code') if ghtk_order.get(k) is not None]
    status_int = None
    if status_candidates:
        try:
            status_int = int(status_candidates[0])
        except Exception:
            status_int = None

    mapped_status = None
    if status_int is not None:
        mapped_status = shipment_constants.GHTK_STATUS_TO_SHIPMENT.get(status_int)

    # Nếu không map được, giữ nguyên trạng thái cũ
    new_status = mapped_status or shipment.status

    changed = False
    if new_status != shipment.status:
        shipment.status = new_status
        shipment.updated_at = timezone.now()
        shipment.save(update_fields=["status", "updated_at"])
        changed = True

    # Tạo tracking record
    ShipmentTracking.objects.create(
        shipment=shipment,
        label_id=ghtk_order.get('label_id') or tracking_code,
        partner_id=ghtk_order.get('partner_id'),
        carrier_status=str(status_int) if status_int is not None else None,
        carrier_status_text=ghtk_order.get('status_text') or ghtk_order.get('status_name') or None,
        raw_response=data,
        weight=ghtk_order.get('total_weight') or shipment.total_weight,
        message=ghtk_order.get('message') or data.get('message'),
        estimated_pick_time=ghtk_order.get('estimated_pick_time'),
        estimated_deliver_time=ghtk_order.get('estimated_deliver_time'),
    )

    return {
        "sub_order_id": sub_order_id,
        "shipment_id": shipment.shipment_id,
        "tracking_code": tracking_code,
        "success": True,
        "changed": changed,
        "mapped_status": mapped_status,
        "raw_status": status_int,
    }
