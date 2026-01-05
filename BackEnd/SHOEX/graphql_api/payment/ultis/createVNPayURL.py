import hmac
import hashlib
import urllib.parse
from datetime import datetime, timedelta
from django.conf import settings

DEFAULT_VNP_URL = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"

VNP_TMN_CODE = settings.VNP_TMN_CODE
HASH_SECRET_KEY = settings.VNP_HASH_SECRET
PAYMENT_URL = getattr(settings, "VNP_URL", DEFAULT_VNP_URL)
RETURN_URL = settings.VNP_RETURN_URL
RETURN_URL_STORE = settings.VNP_RETURN_URL_STORE


def hmac_sha512(key: str, data: str) -> str:
    return hmac.new(
        key.encode("utf-8"),
        data.encode("utf-8"),
        hashlib.sha512
    ).hexdigest()


def create_payment_url(
    order_id: str,
    amount: int,
    ip_addr: str = "127.0.0.1",
    bank_code: str = None,
    locale: str = "vn",
    expire_minutes: int = 15,
    isStore: bool | None = None,
) -> str:
    """
    amount: số tiền VND (VD: 100000)
    """

    create_date = datetime.now()
    expire_date = create_date + timedelta(minutes=expire_minutes)
    params = {
        "vnp_Version": "2.1.0",
        "vnp_Command": "pay",
        "vnp_TmnCode": VNP_TMN_CODE,
        "vnp_Amount": str(int(amount) * 100),
        "vnp_CurrCode": "VND",
        "vnp_TxnRef": str(order_id),
        "vnp_OrderInfo": f"Thanh toan don hang {order_id}",
        "vnp_OrderType": "other",
        "vnp_Locale": locale,
        "vnp_ReturnUrl": RETURN_URL,
        "vnp_IpAddr": ip_addr,
        "vnp_CreateDate": create_date.strftime("%Y%m%d%H%M%S"),
        "vnp_ExpireDate": expire_date.strftime("%Y%m%d%H%M%S"),
    }

    if bank_code:
        params["vnp_BankCode"] = bank_code
    # choose return url depending on isStore flag
    if isStore is True:
        params["vnp_ReturnUrl"] = RETURN_URL_STORE
    else:
        params["vnp_ReturnUrl"] = RETURN_URL

    # === SORT + BUILD QUERY STRING (GIỐNG vnpay.py) ===
    sorted_items = sorted(params.items())

    query_parts = []
    for key, value in sorted_items:
        query_parts.append(
            f"{key}={urllib.parse.quote_plus(str(value))}"
        )

    query_string = "&".join(query_parts)

    # === HASH ===
    secure_hash = hmac_sha512(HASH_SECRET_KEY, query_string)

    return f"{PAYMENT_URL}?{query_string}&vnp_SecureHash={secure_hash}"
