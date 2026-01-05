import requests
import json

# ======================================================
# GHTK CONFIG (lấy trực tiếp như bạn yêu cầu)
# ======================================================
GHTK_API_TOKEN = "2P8zJRNHjCwAoNCRzzUXDJMJgiJZzPnoZfQqZic"
GHTK_PARTNER_CODE = "S22995688"
GHTK_BASE_URL = "https://services.giaohangtietkiem.vn"

# ======================================================
# TRACKING CODE (label / partner_id đều dùng được)
# ======================================================
TRACKING_CODE = "S22995688.BO.MB1-06-F6.1396494756"


def get_ghtk_order_status(tracking_code: str):
    """
    Gọi API GHTK lấy trạng thái đơn hàng
    Endpoint:
    GET /services/shipment/v2/{TRACKING_ORDER}
    """

    url = f"{GHTK_BASE_URL}/services/shipment/v2/{tracking_code}"

    headers = {
        "Token": GHTK_API_TOKEN,
        "X-Client-Source": GHTK_PARTNER_CODE,
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers, timeout=15)

    print("HTTP STATUS:", response.status_code)

    try:
        data = response.json()
    except Exception:
        print("Response is not JSON")
        print(response.text)
        return

    print("========== GHTK RESPONSE ==========")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    if data.get("success"):
        order = data.get("order", {})
        print("\n====== PARSED DATA ======")
        print("Label ID        :", order.get("label_id"))
        print("Partner ID      :", order.get("partner_id"))
        print("Status          :", order.get("status"))
        print("Status Text     :", order.get("status_text"))
        print("Pick Date       :", order.get("pick_date"))
        print("Deliver Date    :", order.get("deliver_date"))
        print("COD (pick_money):", order.get("pick_money"))
        print("Ship Fee        :", order.get("ship_money"))
        print("Insurance Fee   :", order.get("insurance"))
    else:
        print("GHTK ERROR:", data.get("message"))


if __name__ == "__main__":
    get_ghtk_order_status(TRACKING_CODE)
