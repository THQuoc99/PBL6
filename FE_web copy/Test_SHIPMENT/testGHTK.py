import requests
import sqlite3
from urllib.parse import quote_plus

API_TOKEN = "2P8zJRNHjCwAoNCRzzUXDJMJgiJZzPnoZfQqZic"
BASE_URL = "https://services.giaohangtietkiem.vn/services/address/getAddressLevel4"
HEADERS = {"Token": API_TOKEN}

# --- DB init (sqlite demo) ---
conn = sqlite3.connect("ghtk_addresses.db")
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS address_level4 (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  province TEXT,
  district TEXT,
  ward_street TEXT,
  address_level4 TEXT,
  UNIQUE(province, district, ward_street, address_level4)
)
""")
conn.commit()

def get_address_level4(province, district, ward_street, address=None):
    params = {
        "province": province,
        "district": district,
        "ward_street": ward_street
    }
    if address:
        params["address"] = address
    r = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=15)
    r.raise_for_status()
    return r.json()

def save_results(province, district, ward_street, address_list):
    for a in address_list:
        try:
            cur.execute(
                "INSERT OR IGNORE INTO address_level4 (province, district, ward_street, address_level4) VALUES (?, ?, ?, ?)",
                (province, district, ward_street, a)
            )
        except Exception as e:
            print("DB insert error:", e)
    conn.commit()

if __name__ == "__main__":
    province = "Đà Nẵng"
    district = ""
    ward_street = "Phường Liên Chiểu"

    res = get_address_level4(province, district, ward_street)
    if res.get("success"):
        addresses = res.get("data", [])
        print("Found", len(addresses), "items")
        for item in addresses:
            print("-", item)
        save_results(province, district, ward_street, addresses)
    else:
        print("API failed:", res)
