import hmac
import hashlib
import json
from urllib.parse import quote_plus
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from orders.models import Order 
from settlements.models import Settlement
from graphql_api.order.ultis.create_ghtk_order import create_ghtk_orders

HASH_SECRET_KEY = settings.VNP_HASH_SECRET

def _build_hash_data(params: dict) -> str:
    items = []
    for k in sorted(params.keys()):
        if k == 'vnp_SecureHash':
            continue
        v = params[k]
        items.append(f"{k}={quote_plus(str(v))}")
    return '&'.join(items)

@csrf_exempt
def verify_return(request):
    try:
        body = json.loads(request.body.decode('utf-8')) if request.body else {}
    except Exception:
        return HttpResponseBadRequest('invalid json')

    params = body.get('params') or body  # support both JSON body or raw params
    if not isinstance(params, dict):
        return HttpResponseBadRequest('params required')

    received_hash = (params.get('vnp_SecureHash') or params.get('vnp_SecureHash')) or ''
    hash_data = _build_hash_data(params)
    calculated = hmac.new(HASH_SECRET_KEY.encode('utf-8'), hash_data.encode('utf-8'), hashlib.sha512).hexdigest()

    if calculated.lower() != str(received_hash).lower():
        return JsonResponse({'valid': False, 'reason': 'invalid_hash', 'hash_data': hash_data, 'calculated': calculated, 'received': received_hash})

    # Check response codes
    if params.get('vnp_ResponseCode') != '00' or params.get('vnp_TransactionStatus') != '00':
        return JsonResponse({'valid': False, 'reason': 'payment_not_success', 'responseCode': params.get('vnp_ResponseCode')})

    txn_ref = params.get('vnp_TxnRef')
    amount = params.get('vnp_Amount')  # VNPay often returns amount in smallest unit or without decimals; confirm
    if not txn_ref:
        return JsonResponse({'valid': False, 'reason': 'missing_txnref'})

    # Lookup order in DB (adjust to your Order model)
 # adjust import path
    try:
        order = Order.objects.get(pk=txn_ref)
    except Order.DoesNotExist:
        return JsonResponse({'valid': False, 'reason': 'order_not_found', 'txn_ref': txn_ref})

    # Strict amount verification: try several common VNPay scalings
    try:
        recv_amount = float(str(amount))
        # Order stored amount (assume order.total_amount is in VND as decimal/number)
        order_amount = float(order.total_amount)

        # VNPay sometimes returns amount scaled (e.g., multiplied by 100). Check common possibilities:
        matched = False
        # direct match (allow tiny float rounding)
        if abs(recv_amount - order_amount) < 0.01:
            matched = True
        # VNPay returned amount multiplied by 100
        elif abs(recv_amount - (order_amount * 100)) < 1:
            matched = True
        # VNPay returned amount divided by 100 (rare)
        elif abs((recv_amount * 100) - order_amount) < 1:
            matched = True

        if not matched:
            return JsonResponse({'valid': False, 'reason': 'amount_mismatch', 'recv': recv_amount, 'order': order_amount})
    except Exception:
        # If we cannot parse amounts, fail closed to be safe
        return JsonResponse({'valid': False, 'reason': 'invalid_amount_format', 'amount': amount})

    # Only mark paid and create GHTK orders when payment is confirmed and amounts match
    if order.payment.status != 'completed':
        order.payment.status = 'completed'
        order.payment.paid_at = timezone.now()
        print(f"ĐÃ THANH TOÁN ĐƠN HÀNG {order.pk} THÀNH CÔNG QUA VNPay")
        order.payment.save(update_fields=['status', 'paid_at'])
        # try:
        #     create_ghtk_orders(order_id=order.pk)
        # except Exception as e:
        #     # log lỗi, nhưng không fail verify response
        #     print("create_ghtk_orders error:", e)

    return JsonResponse({'valid': True, 'orderId': str(order.pk)})


@csrf_exempt
def verify_return_store(request):
    """
    Verify VNPay return for Store Settlement payment.
    Similar to verify_return but updates Settlement instead of Order.
    """
    try:
        body = json.loads(request.body.decode('utf-8')) if request.body else {}
    except Exception:
        return HttpResponseBadRequest('invalid json')

    params = body.get('params') or body
    if not isinstance(params, dict):
        return HttpResponseBadRequest('params required')

    received_hash = (params.get('vnp_SecureHash') or params.get('vnp_SecureHash')) or ''
    hash_data = _build_hash_data(params)
    calculated = hmac.new(HASH_SECRET_KEY.encode('utf-8'), hash_data.encode('utf-8'), hashlib.sha512).hexdigest()

    if calculated.lower() != str(received_hash).lower():
        return JsonResponse({
            'valid': False, 
            'reason': 'invalid_hash', 
            'hash_data': hash_data, 
            'calculated': calculated, 
            'received': received_hash
        })

    # Check response codes
    if params.get('vnp_ResponseCode') != '00' or params.get('vnp_TransactionStatus') != '00':
        return JsonResponse({
            'valid': False, 
            'reason': 'payment_not_success', 
            'responseCode': params.get('vnp_ResponseCode')
        })

    txn_ref = params.get('vnp_TxnRef')
    amount = params.get('vnp_Amount')
    if not txn_ref:
        return JsonResponse({'valid': False, 'reason': 'missing_txnref'})

    # Lookup Settlement in DB
    try:
        settlement = Settlement.objects.get(settlement_id=txn_ref)
    except Settlement.DoesNotExist:
        return JsonResponse({
            'valid': False, 
            'reason': 'settlement_not_found', 
            'txn_ref': txn_ref
        })

    # Verify amount
    try:
        recv_amount = float(str(amount))
        settlement_amount = float(settlement.total_amount)

        matched = False
        # Direct match
        if abs(recv_amount - settlement_amount) < 0.01:
            matched = True
        # VNPay returned amount multiplied by 100
        elif abs(recv_amount - (settlement_amount * 100)) < 1:
            matched = True
        # VNPay returned amount divided by 100 (rare)
        elif abs((recv_amount * 100) - settlement_amount) < 1:
            matched = True

        if not matched:
            return JsonResponse({
                'valid': False, 
                'reason': 'amount_mismatch', 
                'recv': recv_amount, 
                'settlement': settlement_amount
            })
    except Exception:
        return JsonResponse({
            'valid': False, 
            'reason': 'invalid_amount_format', 
            'amount': amount
        })

    # Update settlement status to 'paid'
    if settlement.status != 'paid':
        settlement.status = 'paid'
        settlement.paid_at = timezone.now()
        settlement.save(update_fields=['status', 'paid_at'])
        print(f"✅ SETTLEMENT {settlement.settlement_id} ĐÃ THANH TOÁN THÀNH CÔNG QUA VNPay")

    return JsonResponse({
        'valid': True, 
        'settlementId': str(settlement.settlement_id),
        'totalAmount': float(settlement.total_amount),
        'status': settlement.status
    })


@csrf_exempt
def vnpay_ipn(request):
    params = request.GET.dict()
    vnp_secure_hash = params.pop("vnp_SecureHash", None)
    params.pop("vnp_SecureHashType", None)

    sorted_items = sorted(params.items())
    raw = "&".join([f"{k}={v}" for k, v in sorted_items])
    my_hash = hmac.new(HASH_SECRET_KEY.encode(), raw.encode(), hashlib.sha512).hexdigest()

    if my_hash != vnp_secure_hash:
        return JsonResponse({"RspCode": "97", "Message": "Checksum invalid"})

    txn_ref = params.get("vnp_TxnRef")
    resp_code = params.get("vnp_ResponseCode")

    # load order by txn_ref, verify amount, etc.
    order = Order.objects.filter(id=txn_ref).first()
    if not order:
        return JsonResponse({"RspCode": "01", "Message": "Order not found"})

    if resp_code == "00":
        order.payment.status = "completed"
        print(f"    IPN :   ĐÃ THANH TOÁN ĐƠN HÀNG {order.pk} THÀNH CÔNG QUA VNPay")
        order.payment_confirmed = True
        order.payment.save(update_fields=['status'])
        # optional: notify frontend via websocket/push
        
    else:
        order.payment.status = "failed"
        order.payment.save(update_fields=['status'])

    return JsonResponse({"RspCode": "00", "Message": "Confirm Success"})