import requests
import json
import urllib.parse

# --- 1. THIẾT LẬP THÔNG TIN CẦN THIẾT ---
# Thay thế {API_TOKEN} và {PARTNER_CODE} bằng thông tin thực tế của bạn
API_TOKEN = "2P8zJRNHjCwAoNCRzzUXDJMJgiJZzPnoZfQqZic" 
PARTNER_CODE = "S22995688" 
BASE_URL = "https://services.giaohangtietkiem.vn" 

# --- 2. ĐỊNH NGHĨA THAM SỐ GỬI ĐI (QUERY PARAMETERS) ---
# SỬ DỤNG 2 ĐỊA CHỈ NỘI THÀNH KHÁC NHAU ĐỂ ĐẢM BẢO delivery: true
# SỬ DỤNG LẠI HÀ NỘI
params = {
    # --- ĐỊA CHỈ GỬI (PICK-UP) ---
    "pick_province": "Hà Nội",
    "pick_district": "Quận Hai Bà Trưng", 
    "pick_ward": "Phường Vĩnh Tuy", 
    "pick_address": "Số 20 Vĩnh Tuy",

    # --- ĐỊA CHỈ NHẬN (DELIVERY) ---
    "province": "Hà Nội",
    "district": "Quận Đống Đa",         
    "ward": "Phường Láng Hạ",          
    "address": "Số 100 Láng Hạ",
    
    "weight": 1000, "value": 3000, "transport": "road", 
}

# --- 3. ĐỊNH NGHĨA HEADERS ---
headers = {
    "Token": API_TOKEN,
    "X-Client-Source": PARTNER_CODE,
}

# --- 4. THỰC HIỆN YÊU CẦU API ---
endpoint = "/services/shipment/fee"
url = f"{BASE_URL}{endpoint}"

print(f"✅ Đang gửi yêu cầu GET đến: {url}")
print(f"ℹ️ Với tham số (URL encoded): {urllib.parse.urlencode(params)}")

try:
    # Gửi yêu cầu GET
    response = requests.get(url, headers=headers, params=params)

    # Kiểm tra mã trạng thái HTTP
    response.raise_for_status() 

    # Phân tích phản hồi JSON
    data = response.json()

    # --- 5. HIỂN THỊ KẾT QUẢ ---
    print("\n\n--- PHẢN HỒI TỪ API ---")
    print(json.dumps(data, indent=4, ensure_ascii=False))
    print("--------------------------\n")
    
    if data.get("success") == True:
        fee_info = data.get("fee", {})
        print("🚀 KẾT QUẢ TÍNH PHÍ VẬN CHUYỂN THÀNH CÔNG:")
        print(f"* Tên gói cước: **{fee_info.get('name')}**")
        print(f"* Cước vận chuyển: **{fee_info.get('fee'):,} VNĐ**")
        print(f"* Phí khai giá (Bảo hiểm): **{fee_info.get('insurance_fee'):,} VNĐ**")
        
        # In kết quả kiểm tra hỗ trợ giao hàng
        trang_thai_giao = 'Có' if fee_info.get('delivery') else 'Không'
        print(f"* Khu vực này có hỗ trợ giao hàng: **{trang_thai_giao}**")

        ext_fees = fee_info.get('extFees', [])
        if ext_fees:
            print("\n* Phụ phí bổ sung:")
            for ext in ext_fees:
                print(f"  - {ext.get('title')}: {ext.get('amount'):,} VNĐ")

    else:
        print(f"❌ LỖI TRẢ VỀ TỪ API: {data.get('message', 'Không rõ lỗi.')}")

except requests.exceptions.HTTPError as err:
    print(f"❌ LỖI HTTP: {err}")
    print(f"Nội dung phản hồi lỗi: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"❌ LỖI KẾT NỐI/YÊU CẦU: {e}")
except Exception as e:
    print(f"❌ LỖI KHÔNG XÁC ĐỊNH: {e}")