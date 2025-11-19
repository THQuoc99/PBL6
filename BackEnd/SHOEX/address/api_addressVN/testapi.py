import json

# Đường dẫn tới file JSON
json_file_path = r'D:\PBL6\BackEnd\SHOEX\address\api_addressVN\vietnam_addresses.json'

# Load file JSON một lần khi chạy chương trình
with open(json_file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 1. Lấy danh sách tỉnh
def get_provinces():
    return [province['province_name'] for province in data]

# 2. Lấy danh sách xã/ward theo tỉnh
def get_wards_by_province(province_name):
    for province in data:
        if province['province_name'].strip().lower() == province_name.strip().lower():
            return [ward['ward_name'] for ward in province['wards']]
    return []  # Nếu không tìm thấy tỉnh

# 3. Lấy danh sách hamlet theo tỉnh và xã
def get_hamlets(province_name, ward_name):
    for province in data:
        if province['province_name'].strip().lower() == province_name.strip().lower():
            for ward in province['wards']:
                if ward['ward_name'].strip().lower() == ward_name.strip().lower():
                    return ward['hamlets']
    return []  # Nếu không tìm thấy

# =========================
# Ví dụ sử dụng
print("Danh sách tỉnh:")
print(len(get_provinces()))  # ✅ Số lượng tỉnh

# print(get_provinces())

# print("\nDanh sách xã của 'Thành phố Hà Nội':")
# print(get_wards_by_province("Thành phố Hà Nội"))

# print("\nDanh sách hamlet của 'Thành phố Hà Nội' - 'Phường Ba Đình':")
# print(get_hamlets("Thành phố Hà Nội", "Phường Ba Đình"))
