import requests

# Token thật của bạn (do Viettel Post cung cấp)
API_TOKEN = "your_token_here"

BASE_URL = "https://partner.viettelpost.vn/v2/categories/listProvince"
HEADERS = {
    "Token": API_TOKEN
}

def get_provinces():
    try:
        response = requests.get(BASE_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()  # nếu lỗi sẽ raise exception
        data = response.json()
        
        if data.get("status") == 200:
            provinces = data.get("data", [])
            print(f"Tìm thấy {len(provinces)} tỉnh/thành:")
            for p in provinces:
                print(f"- {p['PROVINCE_ID']}: {p['PROVINCE_NAME']}")
        else:
            print("API trả về lỗi:", data)
    except Exception as e:
        print("Có lỗi khi gọi API:", e)

if __name__ == "__main__":
    get_provinces()
