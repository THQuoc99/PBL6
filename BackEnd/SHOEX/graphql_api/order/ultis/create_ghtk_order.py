import requests
from django.conf import settings
from django.utils import timezone
from orders.models import Order, SubOrder
from shipments.models import Shipment, ShipmentTracking
from store.models import AddressStore
from payments.models import Payment


def create_ghtk_orders(*, order_id: int):
    """
    Đăng đơn GHTK cho toàn bộ Order
    Mỗi SubOrder = 1 Shipment = 1 đơn GHTK
    """

    # fetch order to iterate suborders
    order = (
        Order.objects
        .select_related('address', 'buyer')
        .prefetch_related(
            'sub_orders__store',
            'sub_orders__items__variant__product',
        )
        .get(pk=order_id)
    )

    results = []
    for sub_order in order.sub_orders.all():
        res = create_ghtk_order_for_suborder(sub_order.sub_order_id)
        results.append(res)

    print('GHTK orders created for Order', order_id, 'results=', results)
    return results


def create_ghtk_order_for_suborder(sub_order_id: int):
    """
    Create a single GHTK order for the given SubOrder id.
    Returns a dict with sub_order_id, shipment_id and tracking_code on success.
    """
    sub_order = (
        SubOrder.objects
        .select_related('order__address', 'order__buyer', 'store',)
        .prefetch_related('items__variant__product')
        .get(pk=sub_order_id)
    )

    order = sub_order.order
    shipment = getattr(sub_order, 'shipment', None)

    if not shipment:
        raise Exception(f"SubOrder {sub_order_id} has no shipment attached")

    # ===== 1. Địa chỉ shop =====
    store_address = AddressStore.objects.filter(
        store=sub_order.store,
        is_default=True
    ).first()

    if not store_address:
        raise Exception(f"Store {sub_order.store.name} has no default address")

    # ===== 2. Địa chỉ người mua =====
    user_address = order.address

    # ===== 3. Products =====
    products = [
        {
            "name": item.variant.product.name,
            "weight": float(item.variant.weight),
            "quantity": item.quantity,
            "product_code": item.variant.sku,
        }
        for item in sub_order.items.all()
    ]

    # ===== 4. COD =====
    payment = Payment.objects.filter(order=order).first()
    if payment and getattr(payment, 'payment_method', '').lower() == 'cod':
        pick_money = int(shipment.pick_money)
        if payment.paid_at is None:
            payment.paid_at = timezone.now()
            payment.save(update_fields=["paid_at"])
    else:
        pick_money = 0

    payload = {
        "products": products,
        "order": {
            "id": f"SUB_{sub_order.sub_order_id}",

            # PICK
            "pick_name": sub_order.store.name,
            "pick_address": store_address.detail,
            "pick_province": store_address.province,
            "pick_district": '',
            "pick_ward": store_address.ward,
            "pick_street": store_address.hamlet or "Khác",
            "pick_tel": store_address.phone,

            # RECEIVE
            "name": order.buyer.full_name,
            "address": user_address.detail,
            "province": user_address.province,
            "district": '',
            "ward": user_address.ward,
            "hamlet": user_address.hamlet or "Khác",
            "tel": user_address.phone_number,

            # MONEY
            "pick_money": pick_money,
            "value": int(shipment.value),
            "total_weight": float(shipment.total_weight),
            "is_freeship": "1",
            # OPTIONS
            "transport": shipment.transport,
            "pick_option": "cod" if pick_money > 0 else "post",
            "note": shipment.note or "",
        }
    }

    print('Creating GHTK order with payload:', payload)
    headers = {
        "Token": settings.GHTK_API_TOKEN,
        "X-Client-Source": settings.GHTK_PARTNER_CODE,
        "Content-Type": "application/json",
    }

    url = f"{settings.GHTK_BASE_URL}/services/shipment/order/?ver=1.5"

    res = requests.post(url, json=payload, headers=headers, timeout=15)
    data = res.json()

    if not data.get("success"):
        raise Exception(data.get("message", "GHTK error"))

    ghtk_order = data["order"]

    # ===== Update Shipment =====
    shipment.tracking_code = ghtk_order.get("label")
    shipment.status = "shipping"
    shipment.updated_at = timezone.now()
    shipment.save(update_fields=["tracking_code", "status", "updated_at"])

    # ===== Tracking =====
    ShipmentTracking.objects.create(
        shipment=shipment,
        label_id=ghtk_order.get("label"),
        partner_id=ghtk_order.get("partner_id"),
        carrier_status=str(ghtk_order.get("status_id")),
        carrier_status_text="Đã tạo đơn GHTK",
        raw_response=data,
        weight=shipment.total_weight,
        message=data.get("message") or data.get("warning_message"),
        estimated_pick_time=ghtk_order.get("estimated_pick_time"),
        estimated_deliver_time=ghtk_order.get("estimated_deliver_time"),
    )

    result = {
        "sub_order_id": sub_order.sub_order_id,
        "shipment_id": shipment.shipment_id,
        "tracking_code": ghtk_order.get("label"),
    }

    return result
