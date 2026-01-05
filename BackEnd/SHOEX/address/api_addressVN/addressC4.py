import requests
import time
import json # Chỉ cần cho in kết quả đẹp hơn

# ================================================
# CẤU HÌNH API GHTK
# ================================================
# Đặt các hằng số API ra ngoài để dễ quản lý
API_TOKEN = "2P8zJRNHjCwAoNCRzzUXDJMJgiJZzPnoZfQqZic"
BASE_URL = "https://services.giaohangtietkiem.vn/services/address/getAddressLevel4"
HEADERS = {"Token": API_TOKEN}

# ================================================
# HÀM LẤY THÔN/KHU ẤP TỪ GHTK (HAMLET)
# Tương tự như get_address_level4 đã hoạt động
# ================================================
def get_hamlets(province_name: str, ward_name: str, retries=3, delay=1):
    """
    Lấy địa chỉ cấp 4 (hamlet) từ API GHTK.
    Sử dụng tên Tỉnh và tên Phường/Xã.
    """
    params = {
        "province": province_name,
        "district": "",  # GHTK API chỉ cần Tỉnh và Phường/Xã
        "ward_street": ward_name
    }
    
    print(f"🏠 Đang tìm kiếm thôn/xóm cho: {province_name} - {ward_name}")

    for attempt in range(retries):
        try:
            # 1. Gửi yêu cầu với Token GHTK từ môi trường Server-side
            r = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=10)
            r.raise_for_status() # Báo lỗi nếu status code là 4xx hoặc 5xx

            response_data = r.json()
            
            # 2. Xử lý phản hồi JSON của GHTK
            if response_data.get("success"):
                hamlets = response_data.get("data", [])
                print(f"✅ Thành công! Tìm thấy {len(hamlets)} thôn/xóm (Thử lại lần {attempt + 1}).")
                return hamlets
            else:
                message = response_data.get("message", "Lỗi không xác định từ GHTK API")
                print(f"⚠️ GHTK API trả về success: False. Message: {message}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"❌ Lỗi mạng hoặc HTTP (Thử lại lần {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(delay)  # Chờ trước khi thử lại
                continue
            return [] # Trả về rỗng sau khi hết số lần thử lại
            
    return []

# ================================================
# KIỂM TRA HÀM
# ================================================
if __name__ == "__main__":
    # Dùng các tên thật để kiểm tra
    PROVINCE_TEST = "Thành phố Đà Nẵng"
    WARD_TEST = "Phường Liên Chiểu"

    print("--- BẮT ĐẦU KIỂM TRA HÀM get_hamlets ---")

    hamlets_result = get_hamlets(PROVINCE_TEST, WARD_TEST)

    print("\n=== KẾT QUẢ THÔN/XÓM ===")
    if hamlets_result:
        # In tối đa 5 kết quả để kiểm tra
        print(f"Tìm thấy tổng cộng {len(hamlets_result)} thôn/xóm.")
        print(f"Các thôn/xóm đầu tiên:")
        for i, h in enumerate(hamlets_result[:5]):
            print(f" - {h}")
        if len(hamlets_result) > 5:
            print(f" ... và {len(hamlets_result) - 5} thôn/xóm khác.")
    else:
        print("Không tìm thấy dữ liệu thôn/xóm nào hoặc xảy ra lỗi trong quá trình lấy dữ liệu.")