import requests

# =========================
# CẤU HÌNH GHTK
# =========================
GHTK_API_TOKEN = "2P8zJRNHjCwAoNCRzzUXDJMJgiJZzPnoZfQqZic"
GHTK_PARTNER_CODE = "S22995688"
GHTK_BASE_URL = "https://services.giaohangtietkiem.vn"

TRACKING_CODE = "S22995688.BO.MB1-06-F6.1396494756"


def cancel_ghtk_order(tracking_code: str):
    """
    Gọi API huỷ đơn hàng GHTK
    """

    url = f"{GHTK_BASE_URL}/services/shipment/cancel/{tracking_code}"

    headers = {
        "Token": GHTK_API_TOKEN,
        "X-Client-Source": GHTK_PARTNER_CODE,
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        print("response:", data)
        if data.get("success"):
            print("✅ Huỷ đơn hàng thành công")
        else:
            print("❌ Không thể huỷ đơn hàng")
            print("Lý do:", data.get("message"))

        print("Log ID:", data.get("log_id"))

    except requests.exceptions.RequestException as e:
        print("❌ Lỗi khi gọi API GHTK:", str(e))


# =========================
# CHẠY CHƯƠNG TRÌNH
# =========================
if __name__ == "__main__":
    cancel_ghtk_order(TRACKING_CODE)
