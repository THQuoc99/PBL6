from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import hmac, hashlib, urllib.parse
from django.conf import settings
VNP_HASH_SECRET = settings.VNP_HASH_SECRET
@csrf_exempt
def vnpay_ipn(request):
    params = request.GET.dict()
    vnp_secure_hash = params.pop("vnp_SecureHash", None)
    params.pop("vnp_SecureHashType", None)
    sorted_items = sorted(params.items())
    raw = "&".join(f"{k}={v}" for k, v in sorted_items)
    my_hash = hmac.new(VNP_HASH_SECRET.encode(), raw.encode(), hashlib.sha512).hexdigest()
    if my_hash != vnp_secure_hash:
        return JsonResponse({"RspCode": "97", "Message": "Checksum invalid"})
    txn_ref = params.get("vnp_TxnRef")
    response_code = params.get("vnp_ResponseCode")
    # TODO: load order by txn_ref, verify amount, update status
    if response_code == "00":
        # mark order paid
        pass
    return JsonResponse({"RspCode": "00", "Message": "Confirm Success"})