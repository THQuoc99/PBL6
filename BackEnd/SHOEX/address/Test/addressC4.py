import requests
import json
import sqlite3
from urllib.parse import quote_plus
import time

# API configuration for GHTK
API_TOKEN = "2P8zJRNHjCwAoNCRzzUXDJMJgiJZzPnoZfQqZic"
BASE_URL = "https://services.giaohangtietkiem.vn/services/address/getAddressLevel4"
HEADERS = {"Token": API_TOKEN}

# Initialize SQLite database
conn = sqlite3.connect("vietnam_addresses.db")
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS address_level4 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    province TEXT,
    ward TEXT,
    hamlet TEXT,
    UNIQUE(province, ward, hamlet)
)
""")
conn.commit()

def get_address_level4(province, ward, retries=3, delay=1):
    """
    Lấy địa chỉ cấp 4 (hamlet) từ API GHTK
    """
    params = {
        "province": province,
        "district": "",  # Bỏ qua cấp huyện
        "ward_street": ward
    }
    for attempt in range(retries):
        try:
            r = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=15)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching GHTK API for {province} - {ward}: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
                continue
            return {"success": False, "message": str(e)}
    return {"success": False, "message": "Max retries reached"}

def save_to_db(province, ward, hamlets):
    """
    Lưu dữ liệu địa chỉ cấp 4 vào SQLite
    """
    for hamlet in hamlets:
        try:
            cur.execute(
                "INSERT OR IGNORE INTO address_level4 (province, ward, hamlet) VALUES (?, ?, ?)",
                (province, ward, hamlet)
            )
        except Exception as e:
            print(f"DB insert error for {province} - {ward} - {hamlet}: {e}")
    conn.commit()

def get_all_data():
    """
    Lấy tất cả dữ liệu tỉnh/thành phố, phường/xã từ API provinces.open-api.vn
    và địa chỉ cấp 4 (hamlet) từ API GHTK
    """
    # Lấy danh sách tỉnh/thành phố
    provinces_url = "https://provinces.open-api.vn/api/v2/p/"
    try:
        provinces_resp = requests.get(provinces_url, timeout=15)
        provinces_resp.raise_for_status()
        provinces = provinces_resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching provinces: {e}")
        return []

    full_data = []

    for province in provinces:
        province_id = province['code']
        province_name = province['name']
        print(f"Processing province: {province_name}")

        # Lấy danh sách phường/xã
        province_detail_url = f"https://provinces.open-api.vn/api/v2/p/{province_id}?depth=2"
        try:
            province_detail_resp = requests.get(province_detail_url, timeout=15)
            province_detail_resp.raise_for_status()
            province_detail = province_detail_resp.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching details for {province_name}: {e}")
            continue

        wards = province_detail.get('wards', [])
        ward_list = []

        for ward in wards:
            ward_code = ward['code']
            ward_name = ward['name']

            # Lấy địa chỉ cấp 4 từ GHTK API
            ghtk_response = get_address_level4(province_name, ward_name)
            hamlets = []
            if ghtk_response.get("success"):
                hamlets = ghtk_response.get("data", [])
                print(hamlets)
                print(f"Found {len(hamlets)} hamlets for {province_name} - {ward_name}")
                # Lưu vào SQLite
                save_to_db(province_name, ward_name, hamlets)
            else:
                print(f"No hamlet data for {province_name} - {ward_name}: {ghtk_response.get('message')}")

            ward_list.append({
                'ward_code': ward_code,
                'ward_name': ward_name,
                'hamlets': hamlets
            })

            # Thêm thời gian nghỉ để tránh bị chặn API
            time.sleep(0.5)

        full_data.append({
            'province_code': province_id,
            'province_name': province_name,
            'wards': ward_list
        })

    return full_data

if __name__ == "__main__":
    print("Đang lấy dữ liệu tất cả tỉnh/thành phố, phường/xã và thôn/xóm Việt Nam...")
    print("Vui lòng đợi...")

    # Lấy dữ liệu
    data = get_all_data()

    # Lưu vào file JSON
    filename = "vietnam_addresses.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Thống kê
    total_provinces = len(data)
    total_wards = sum(len(province['wards']) for province in data)
    total_hamlets = sum(
        len(ward['hamlets'])
        for province in data
        for ward in province['wards']
    )

    print(f"\n✅ Hoàn thành!")
    print(f"📊 Thống kê:")
    print(f"   - Tổng số tỉnh/thành phố: {total_provinces}")
    print(f"   - Tổng số phường/xã: {total_wards}")
    print(f"   - Tổng số thôn/xóm: {total_hamlets}")
    print(f"📁 Dữ liệu đã được lưu vào file: {filename}")
    print(f"📁 Dữ liệu cũng được lưu vào cơ sở dữ liệu: vietnam_addresses.db")

    # In một số dữ liệu mẫu để kiểm tra
    print(f"\n📝 Một số tỉnh/thành phố đầu tiên:")
    for i, province in enumerate(data[:3]):
        print(f"   {i+1}. {province['province_name']} - {len(province['wards'])} phường/xã")
        for j, ward in enumerate(province['wards'][:2]):
            print(f"      - {ward['ward_name']} ({len(ward['hamlets'])} thôn/xóm)")
            for hamlet in ward['hamlets'][:2]:  # In tối đa 2 thôn/xóm
                print(f"        + {hamlet}")
            if len(ward['hamlets']) > 2:
                print(f"        ... và {len(ward['hamlets']) - 2} thôn/xóm khác")

    if len(data) > 3:
        print(f"   ... và {len(data) - 3} tỉnh/thành phố khác")

    # Đóng kết nối database
    conn.close()