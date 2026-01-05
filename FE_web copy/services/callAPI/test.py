import requests
import time

# ================================================
# CẤU HÌNH API
# ================================================
# API Open-API.vn (dùng cho Tỉnh/Thành phố, Quận/Huyện, Phường/Xã)
PROVINCES_API = "https://provinces.open-api.vn/api/v2/p/"

# API GHTK (dùng cho Thôn/Khu ấp)
GHTK_TOKEN = "2P8zJRNHjCwAoNCRzzUXDJMJgiJZzPnoZfQqZic"  # Token GHTK
GHTK_BASE_URL = "https://services.giaohangtietkiem.vn/services/address/getAddressLevel4"
GHTK_HEADERS = {"Token": GHTK_TOKEN}

# ================================================
# 1. LẤY PHƯỜNG/XÃ (Giữ nguyên)
# ================================================
def get_wards(province_id):
    """
    Lấy danh sách phường/xã theo ID tỉnh.
    Trả về list wards hoặc [] nếu lỗi.
    """
    url = f"{PROVINCES_API}{province_id}?depth=2"

    try:
        print(f"Fetching wards for province ID = {province_id}...")
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        data = response.json()
        wards = data.get("wards", [])

        print(f"Found {len(wards)} wards.")
        return wards

    except Exception as e:
        print("Error fetching wards:", e)
        return []

# ================================================
# 2. LẤY THÔN/KHU ẤP TỪ GHTK (Hàm mới)
# ================================================
def get_hamlets(province_name, ward_name, retries=3, delay=1):
    """
    Lấy địa chỉ cấp 4 (hamlet) từ API GHTK.
    Sử dụng tên Tỉnh và tên Phường/Xã.
    """
    params = {
        "province": province_name,
        "district": "",  # Bỏ qua cấp huyện
        "ward_street": ward_name
    }
    
    print(f"\n🏠 Fetching hamlets for {province_name} - {ward_name}...")

    for attempt in range(retries):
        try:
            # Gửi yêu cầu với Token GHTK
            r = requests.get(GHTK_BASE_URL, headers=GHTK_HEADERS, params=params, timeout=10)
            r.raise_for_status() # Báo lỗi nếu status code là 4xx hoặc 5xx

            response_data = r.json()
            
            if response_data.get("success"):
                hamlets = response_data.get("data", [])
                print(f"✅ GHTK Success. Found {len(hamlets)} hamlets.")
                return hamlets
            else:
                # GHTK API trả về success: False
                message = response_data.get("message", "Unknown error from GHTK API")
                print(f"⚠️ GHTK API returned failure: {message}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching GHTK API (Attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(delay)  # Chờ trước khi thử lại
                continue
            return []
            
    return []

# ================================================
# CHẠY THỬ
# ================================================
if __name__ == "__main__":
    # --- PHẦN 1: TEST get_wards (Giữ nguyên ID 44) ---
    print("--- TESTING get_wards (API Open-API.vn) ---")
    
    # ID tỉnh: 44 (Đà Nẵng)
    province_id_test = 44 
    
    wards_data = get_wards(province_id_test)
    
    # --- PHẦN 2: TEST get_hamlets ---
    print("\n--- TESTING get_hamlets (API GHTK) ---")
    
    if wards_data:
        # Lấy Tên Tỉnh (Giả sử ID 44 là Đà Nẵng, cần phải gọi API Tỉnh để lấy tên chính xác)
        # Giả lập tên tỉnh và phường đầu tiên để test:
        province_name_test = "Quảng Trị" 
        ward_name_test = "Vĩnh Chấp"

        print(f"Using Province: {province_name_test}")
        print(f"Using Ward: {ward_name_test}")

        hamlets_data = get_hamlets(province_name_test, ward_name_test)

        print("\n=== HAMLETS RESULT ===")
        if hamlets_data:
            for i, h in enumerate(hamlets_data[:5]):
                print(f"- Hamlet {i+1}: {h}")
            if len(hamlets_data) > 5:
                print(f"... và {len(hamlets_data) - 5} thôn/xóm khác")
        else:
            print("Không tìm thấy thôn/xóm nào hoặc xảy ra lỗi.")
    else:
        print("Không có dữ liệu Phường/Xã để tiếp tục test GHTK API.")