import requests
import json

def get_all_data():
    # 1. Lấy tất cả tỉnh/thành phố
    provinces_url = "https://provinces.open-api.vn/api/v2/p/"
    provinces_resp = requests.get(provinces_url)
    provinces = provinces_resp.json()

    full_data = []

    for province in provinces:
        province_id = province['code']
        province_name = province['name']

        # 2. Lấy danh sách phường/xã của tỉnh (depth=2 để lấy cả wards)
        province_detail_url = f"https://provinces.open-api.vn/api/v2/p/{province_id}?depth=2"
        province_detail_resp = requests.get(province_detail_url)
        province_detail = province_detail_resp.json()
        
        # Lấy danh sách wards từ province
        wards = province_detail.get('wards', [])
        ward_list = [{'ward_code': w['code'], 'ward_name': w['name']} for w in wards]

        full_data.append({
            'province_code': province_id,
            'province_name': province_name,
            'wards': ward_list
        })

    return full_data

if __name__ == "__main__":
    print("Đang lấy dữ liệu tất cả tỉnh thành và phường xã Việt Nam...")
    print("Vui lòng đợi...")
    
    data = get_all_data()

    # Lưu vào file JSON
    filename = "vietnam_provinces_complete.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Thống kê
    total_provinces = len(data)
    total_wards = sum(len(province['wards']) for province in data)
    
    print(f"\n✅ Hoàn thành!")
    print(f"📊 Thống kê:")
    print(f"   - Tổng số tỉnh/thành phố: {total_provinces}")
    print(f"   - Tổng số phường/xã: {total_wards}")
    print(f"📁 Dữ liệu đã được lưu vào file: {filename}")
    
    # In vài tỉnh đầu tiên để kiểm tra
    print(f"\n📝 Một số tỉnh/thành phố đầu tiên:")
    for i, province in enumerate(data[:5]):
        print(f"   {i+1}. {province['province_name']} - {len(province['wards'])} phường/xã")
    
    if len(data) > 5:
        print(f"   ... và {len(data) - 5} tỉnh/thành phố khác")
