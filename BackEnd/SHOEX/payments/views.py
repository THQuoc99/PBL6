import paypalrestsdk
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.shortcuts import render, redirect
from .models import Payment
from orders.models import Order

# ✅ IMPORT ĐẦY ĐỦ CÁC THƯ VIỆN CẦN THIẾT
import hmac
import hashlib
import urllib.parse
import datetime

# ------------------ CUSTOM DEEP LINK REDIRECT ------------------
class DeepLinkRedirect(HttpResponseRedirect):
    allowed_schemes = ['http', 'https', 'ftp', 'myapp']

# ------------------ CẤU HÌNH CHUNG ------------------
# Thay bằng domain ngrok của bạn hoặc http://10.0.2.2:8000 nếu chạy local hoàn toàn
NGROK_HOST = "https://successive-idella-unsparingly.ngrok-free.dev" 
USD_RATE = 26360.0

# ------------------ PAYPAL CONFIG ------------------
paypalrestsdk.configure({
    "mode": "sandbox",
    "client_id": "AWkK0zZPsDl_dqfy1ARrkcGb_OTYuOQJH6aprgGTZxrJ4emsrqReTwYWlKqhbFdtKtUX-TEqgO_I-hyw",
    "client_secret": "EP4bwQ6zIbheyDrH4q7lhSpV3L-qV3NeAhoLi7Z27MqJlCqawMcun18xoN-9oku15zKlvTkFwyFQhkkP"
})

# ------------------ VNPAY CONFIG ------------------
VNP_TMN = "OBGZ0ZPP"
VNP_SECRET = "HJAVSX9RF6QOB7WCAVRMACG52XHB43PD"
VNP_URL = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
VNP_RETURN = f"{NGROK_HOST}/payments/vnpay-return/"

# ==============================================================================
# PAYPAL VIEWS
# ==============================================================================

def create_paypal_payment(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id)
        
        total_vnd = order.total_amount
        total_usd = round(float(total_vnd) / USD_RATE, 2)

        if total_usd <= 0:
            # Fix trường hợp test giá trị nhỏ, PayPal yêu cầu tối thiểu > 0
            total_usd = 1.00 

        return_url = f"{NGROK_HOST}/payments/paypal-success"
        cancel_url = f"{NGROK_HOST}/payments/paypal-cancel"

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "redirect_urls": {
                "return_url": return_url,
                "cancel_url": cancel_url
            },
            "transactions": [{
                "amount": {
                    "total": str(total_usd),
                    "currency": "USD"
                },
                "description": f"Thanh toan don hang #{order.order_id}"
            }]
        })

        if payment.create():
            Payment.objects.update_or_create(
                order=order,
                defaults={
                    "amount": order.total_amount,
                    "payment_method": "paypal",
                    "transaction_id": payment.id,
                    "status": "pending"
                }
            )

            for link in payment.links:
                if link.rel == "approval_url":
                    return redirect(link.href)

        return JsonResponse({"error": payment.error})

    except Order.DoesNotExist:
        return JsonResponse({"error": "Order not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def paypal_success(request):
    payment_id = request.GET.get("paymentId")
    payer_id = request.GET.get("PayerID")

    if not payment_id or not payer_id:
        return DeepLinkRedirect("myapp://payment-return?status=error&message=MissingParams")

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        try:
            local_payment = Payment.objects.get(transaction_id=payment_id)
            order = local_payment.order

            local_payment.status = "completed"
            local_payment.paid_at = timezone.now()
            local_payment.save()

            order.status = "paid"
            order.payment_status = "paid"
            order.save()
            order.sub_orders.all().update(status='paid')

        except Payment.DoesNotExist:
            return DeepLinkRedirect("myapp://payment-return?status=error&message=PaymentNotFound")

        return DeepLinkRedirect(f"myapp://payment-return?status=success&order_id={order.order_id}")

    return DeepLinkRedirect("myapp://payment-return?status=failed")

@csrf_exempt
def paypal_cancel(request):
    return DeepLinkRedirect("myapp://payment-return?status=cancelled")


# ==============================================================================
# VNPAY VIEWS & HELPERS
# ==============================================================================

def _norm(v):
    return "" if v is None else str(v).strip()

def _get_vnpay_hash(data, secret_key):
    data_to_hash = {}
    for k, v in data.items():
        if k not in ["vnp_SecureHash", "vnp_SecureHashType"]:
            normalized_v = _norm(v)
            if normalized_v != "":
                data_to_hash[k] = normalized_v

    sorted_items = sorted(data_to_hash.items())
    hash_data_list = [f"{k}={urllib.parse.quote_plus(v)}" for k, v in sorted_items]
    hash_data = "&".join(hash_data_list)
    
    secure_hash = hmac.new(
        secret_key.encode('utf-8'),
        hash_data.encode('utf-8'),
        hashlib.sha512
    ).hexdigest().upper()
    
    return secure_hash

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def create_vnpay_payment(request, order_id):
    print(f"🚀 Đang xử lý VNPAY cho Order ID: {order_id}")
    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        return JsonResponse({"error": "Order not found"}, status=404)

    vnp_Amount = int(order.total_amount * 100)
    vnp_TxnRef = str(order.order_id)
    vnp_OrderInfo = f"Thanh toan don hang {order.order_id}"
    vnp_CreateDate = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    vnp_ExpireDate = (datetime.datetime.now() + datetime.timedelta(minutes=15)).strftime("%Y%m%d%H%M%S")
    
    # Lấy IP thực
    ip_addr = get_client_ip(request)

    inputData = {
        "vnp_Version": "2.1.0",
        "vnp_Command": "pay",
        "vnp_TmnCode": VNP_TMN,
        "vnp_Amount": vnp_Amount,
        "vnp_CurrCode": "VND",
        "vnp_TxnRef": vnp_TxnRef,
        "vnp_OrderInfo": vnp_OrderInfo,
        "vnp_OrderType": "other",
        "vnp_Locale": "vn",
        "vnp_ReturnUrl": VNP_RETURN,
        "vnp_IpAddr": ip_addr, 
        "vnp_CreateDate": vnp_CreateDate,
        "vnp_ExpireDate": vnp_ExpireDate,
    }

    # 1. Tạo Hash
    secure_hash = _get_vnpay_hash(inputData, VNP_SECRET)
    
    # 2. Sắp xếp dữ liệu để tạo Query String (Quan trọng: Phải sort giống lúc tạo Hash)
    # Nếu không sort, VNPAY sẽ báo lỗi sai chữ ký
    sorted_inputData = sorted(inputData.items())
    query_string = urllib.parse.urlencode(sorted_inputData, quote_via=urllib.parse.quote)
    
    # 3. Tạo Full URL
    payment_url = f"{VNP_URL}?{query_string}&vnp_SecureHashType=HMACSHA512&vnp_SecureHash={secure_hash}"

    print(f"🔗 Redirecting to: {payment_url}")

    # 4. Lưu Payment
    Payment.objects.update_or_create(
        order=order,
        defaults={
            "amount": order.total_amount,
            "payment_method": "vnpay",
            "transaction_id": vnp_TxnRef,
            "status": "pending"
        }
    )
    
    return redirect(payment_url)

@csrf_exempt
def vnpay_return(request):
    inputData = request.GET
    vnp_TxnRef = inputData.get("vnp_TxnRef")
    vnp_ResponseCode = inputData.get("vnp_ResponseCode")
    vnp_secure_recv = inputData.get("vnp_SecureHash", "").upper()

    secure_calc = _get_vnpay_hash(inputData, VNP_SECRET)
    
    if secure_calc != vnp_secure_recv:
        print("❌ VNPAY: Sai chữ ký!")
        return DeepLinkRedirect("myapp://payment-return?status=error&message=InvalidSignature")

    try:
        payment = Payment.objects.get(order__order_id=vnp_TxnRef)
        order = payment.order
    except Payment.DoesNotExist:
        return DeepLinkRedirect("myapp://payment-return?status=error&message=PaymentNotFound")

    if vnp_ResponseCode == "00":
        print(f"✅ VNPAY: Thanh toán thành công đơn {vnp_TxnRef}")
        payment.status = "completed"
        payment.paid_at = timezone.now()
        payment.save()
        
        order.status = "paid"
        order.payment_status = "paid"
        order.save()
        order.sub_orders.all().update(status='paid')
        
        return DeepLinkRedirect(f"myapp://payment-return?status=success&order_id={vnp_TxnRef}")
        
    elif vnp_ResponseCode == "24":
        print("⚠️ VNPAY: Người dùng hủy")
        payment.status = "failed"
        payment.save()
        return DeepLinkRedirect("myapp://payment-return?status=cancelled")
    else:
        print(f"❌ VNPAY: Lỗi {vnp_ResponseCode}")
        payment.status = "failed"
        payment.save()
        return DeepLinkRedirect(f"myapp://payment-return?status=failed&vnp_ResponseCode={vnp_ResponseCode}")

@csrf_exempt
def vnpay_ipn(request):
    inputData = request.GET
    vnp_TxnRef = inputData.get("vnp_TxnRef")
    vnp_ResponseCode = inputData.get("vnp_ResponseCode")
    vnp_TransactionNo = inputData.get("vnp_TransactionNo")
    vnp_Amount_recv = inputData.get("vnp_Amount")
    vnp_secure_recv = inputData.get("vnp_SecureHash", "").upper()

    secure_calc = _get_vnpay_hash(inputData, VNP_SECRET)
    
    if secure_calc != vnp_secure_recv:
        return JsonResponse({'RspCode': '97', 'Message': 'Invalid Signature'})

    try:
        local_payment = Payment.objects.get(order__order_id=vnp_TxnRef)
        local_order = local_payment.order
    except Payment.DoesNotExist:
        return JsonResponse({'RspCode': '01', 'Message': 'Order not found'})

    if local_payment.status == "completed":
        return JsonResponse({'RspCode': '02', 'Message': 'Order already confirmed'})

    # Chuyển Decimal thành string số nguyên để so sánh
    local_amount_vnd_str = str(int(local_order.total_amount * 100))

    if local_amount_vnd_str != vnp_Amount_recv:
        return JsonResponse({'RspCode': '04', 'Message': 'Invalid amount'})

    if vnp_ResponseCode == "00":
        local_payment.status = "completed"
        local_payment.paid_at = timezone.now()
        local_payment.transaction_id = vnp_TransactionNo
        local_payment.save()
        
        local_order.status = "paid"
        local_order.payment_status = "paid"
        local_order.save()
        local_order.sub_orders.all().update(status='paid')
    else:
        local_payment.status = "failed"
        local_payment.save()
        
    return JsonResponse({'RspCode': '00', 'Message': 'Confirm Success'})