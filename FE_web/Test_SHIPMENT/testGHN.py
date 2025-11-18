import requests

TOKEN = "b0dcb80e-8c91-11f0-9186-726dc10c3f58"  # thay bằng token thật
BASE_URL = "https://online-gateway.ghn.vn/shiip/public-api/master-data/province"

headers = {
    "token": TOKEN
}

def get_provinces():
    response = requests.get(BASE_URL, headers=headers)
    return response.json()

if __name__ == "__main__":
    provinces = get_provinces()
    print("Danh sách Tỉnh/Thành GHN:")
    for p in provinces["data"]:
        print(p["ProvinceID"], p["ProvinceName"], p["Code"])
