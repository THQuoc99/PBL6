import requests
import time

# ===============================
# CONFIG
# ===============================
GHTK_TOKEN = "2P8zJRNHjCwAoNCRzzUXDJMJgiJZzPnoZfQqZic"

BASE_URL = "https://services.ghtk.vn/services/shipment/address/getAddressLevel4"
PROVINCES_API = "https://provinces.open-api.vn/api/p/"


# ================================================
# 1. LẤY DANH SÁCH TỈNH
# ================================================
def get_provinces():
    try:
        print("🌍 Fetching provinces from:", PROVINCES_API)
        resp = requests.get(PROVINCES_API, timeout=10)

        if resp.status_code != 200:
            print(f"⚠️ Provinces API returned {resp.status_code}")
            return []

        data = resp.json()
        print(f"✅ Provinces loaded: {len(data)}")
        return data

    except Exception as e:
        print("❌ Error fetching provinces:", str(e))
        return []


# ================================================
# 2. LẤY DANH SÁCH PHƯỜNG/XÃ THEO TỈNH
# ================================================
def get_wards(province_id, retries=2):
    if not province_id:
        print("⚠️ get_wards called without province_id")
        return []

    url = f"{PROVINCES_API}{province_id}?depth=2"

    for attempt in range(retries + 1):
        try:
            if attempt > 0:
                print(f"🔄 Retry {attempt}/{retries} - Fetching wards from:", url)
            else:
                print("🏘️ Fetching wards from:", url)

            resp = requests.get(
                url,
                headers={"Accept": "application/json"},
                timeout=10
            )

            if resp.status_code != 200:
                print(f"⚠️ Wards API returned {resp.status_code}")
                if attempt < retries:
                    time.sleep(1)
                    continue
                return []

            data = resp.json()
            wards = data.get("wards", [])
            print(f"✅ Wards loaded: {len(wards)} for province {province_id}")
            return wards

        except requests.exceptions.Timeout:
            print(f"⏱️ Timeout fetching wards (attempt {attempt + 1})")
        except Exception as e:
            print(f"❌ Error fetching wards (attempt {attempt + 1}):", str(e))

        if attempt < retries:
            time.sleep(1)

    return []


# ================================================
# 3. LẤY THÔN/KHU ẤP TỪ GHTK
# ================================================
def get_hamlets(province_name, ward_name):
    if not province_name or not ward_name:
        print("⚠️ get_hamlets called without province or ward")
        return []

    print(f'🏘️ Fetching hamlets for Province="{province_name}", Ward="{ward_name}"')

    params = {
        "province": province_name,
        "district": "",
        "ward_street": ward_name
    }

    try:
        print("🏠 Fetching hamlets from GHTK:", BASE_URL)
        resp = requests.get(
            BASE_URL,
            headers={"Token": GHTK_TOKEN},
            params=params,
            timeout=10
        )

        if resp.status_code != 200:
            print(f"⚠️ GHTK API returned {resp.status_code}")
            return []

        result = resp.json()
        print("✅ GHTK Response:", result)

        if result.get("success") and isinstance(result.get("data"), list):
            hamlets = result["data"]

            if len(hamlets) == 1 and hamlets[0] == "Khác":
                print('⚠️ No real hamlets found (only "Khác")')
                return []

            print(f"✅ Found {len(hamlets)} hamlets")
            return hamlets

        print("⚠️ GHTK API returned invalid format")
        return []

    except requests.exceptions.RequestException as e:
        print("❌ GHTK API unavailable (Network/CORS-like issue):", str(e))
        return []


# ================================================
# MAIN TEST
# ================================================
def main():
    # 1. Test provinces
    provinces = get_provinces()
    if not provinces:
        print("❌ No provinces loaded")
        return

    first_province = provinces[0]
    province_id = first_province["code"]
    province_name = first_province["name"]

    print("\n📍 Selected province:", province_name)

    # 2. Test wards
    wards = get_wards(province_id)
    if not wards:
        print("❌ No wards found")
        return

    first_ward = wards[0]
    ward_name = first_ward["name"]

    print("\n📍 Selected ward:", ward_name)

    # 3. Test hamlets
    hamlets = get_hamlets(province_name, ward_name)

    print("\n📌 FINAL RESULT")
    print("Province:", province_name)
    print("Ward:", ward_name)
    print("Hamlets:", hamlets)


if __name__ == "__main__":
    main()
