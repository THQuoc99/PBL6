import requests
import json
from decimal import Decimal
import time # Dùng để tạm dừng giữa các lần chạy test

GRAPHQL_URL = "http://localhost:8000/graphql/"

# Giả sử USER_ID (cần thiết cho SaveVoucher) và ORDER_ID (cần thiết cho UseVoucher) đã có sẵn trong môi trường test
# Nếu bạn cần truyền USER_ID qua Header/Context/Authentication, bạn phải sửa hàm gql.
# Trong ví dụ này, tôi giả định hệ thống tự nhận dạng User qua Context/Session.
TEST_USER_ID = 6  # ID user giả định
TEST_STORE_ID = "b1e5f3e671fe"   # ID store giả định
TEST_PRODUCT_ID = 4 # ID product giả định
TEST_ORDER_ID = 1   # ID order giả định

def gql(query, variables=None):
    payload = {
        "query": query,
        "variables": variables or {}
    }
    # Thêm Header Auth nếu cần (giả định cần cho các hàm cần user)
    headers = {
        "Authorization": f"Bearer {TEST_USER_ID}" # Đây là ví dụ, thay bằng token/cơ chế Auth thực tế
    }
    
    res = requests.post(GRAPHQL_URL, json=payload, headers=headers)
    print("============================== REQUEST ==============================")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    try:
        response_data = res.json()
    except requests.JSONDecodeError:
        print("RESPONSE (Non-JSON):", res.text)
        response_data = {"error": "JSON Decode Error"}
        
    print("============================== RESPONSE ==============================")
    print(json.dumps(response_data, indent=2, ensure_ascii=False))
    print("======================================================================\n")
    return response_data

# ---------------------------------------------------------------------
# 1) Tạo voucher platform
# ---------------------------------------------------------------------
def test_create_platform_voucher():
    print("--- 1) TEST CREATE PLATFORM VOUCHER (PLT10) ---")
    query = """
    mutation CreatePlatformVoucher($data: VoucherInput!) {
      createPlatformVoucher(data: $data) {
        ok
        voucher { voucherId code type }
      }
    }
    """
    variables = {
        "data": {
          "code": f"PLT10_{int(time.time())}", # Dùng timestamp để tránh lỗi code trùng lặp
          "discountType": "percent", 
          "discountValue": 10.0, 
          "maxDiscount": 30000.0,
          "minOrderAmount": 100000.0,
          "startDate": "2025-12-12",
          "endDate": "2025-12-31",
          "perUserLimit": 1
        }
    }
    return gql(query, variables)

# ---------------------------------------------------------------------
# 2) Tạo voucher store
# ---------------------------------------------------------------------
def test_create_store_voucher(store_id):
    print(f"--- 2) TEST CREATE STORE VOUCHER (STORE50) cho Store ID: {store_id} ---")
    query = """
    mutation CreateStoreVoucher($storeId: ID!, $data: VoucherInput!) {
      createStoreVoucher(storeId: $storeId, data: $data) {
        ok
        voucher { voucherId code type } 
      }
    }
    """
    variables = {
        "storeId": str(store_id),
        "data": {
            "code": f"STORE50_{int(time.time())}", # Dùng timestamp để tránh lỗi code trùng lặp
            "discountType": "fixed", #Hoăc "percent"
            "discountValue": 50000.0,
            "maxDiscount": None, #Nếu là fixed thì phải để None
            "minOrderAmount": 200000.0,
            "startDate": "2025-01-01",
            "endDate": "2025-06-30",
            "perUserLimit": 1
        }
    }
    return gql(query, variables)

# ---------------------------------------------------------------------
# 3) Update voucher
# ---------------------------------------------------------------------
def test_update_voucher(voucher_id):
    print(f"--- 3) TEST UPDATE VOUCHER ID: {voucher_id} ---")
    query = """
    mutation UpdateVoucher($voucherId: ID!, $data: VoucherInput!) {
      updateVoucher(voucherId: $voucherId, data: $data) {
        ok
        voucher { voucherId code discountValue }
      }
    }
    """
    variables = {
        "voucherId": str(voucher_id),
        "data": {
            # Sửa: Thêm type, snake_case -> camelCase, thêm .0
            "type": "PLATFORM", 
            "code": "PLAT20_UPDATED",
            "discountType": "percent",
            "discountValue": 20.0,
            "minOrderAmount": 150000.0,
            "startDate": "2025-01-01",
            "endDate": "2025-12-31",
            "perUserLimit": 5
        }
    }
    return gql(query, variables)

# ---------------------------------------------------------------------
# 4) Delete voucher
# ---------------------------------------------------------------------
def test_delete_voucher(voucher_id):
    print(f"--- 4) TEST DELETE VOUCHER ID: {voucher_id} ---")
    query = """
    mutation DeleteVoucher($voucherId: ID!) {
      deleteVoucher(voucherId: $voucherId) {
        ok
        message
      }
    }
    """
    return gql(query, {"voucherId": str(voucher_id)})

# ---------------------------------------------------------------------
# 5) Save voucher (Giả định user được xác định từ context)
# ---------------------------------------------------------------------
# SỬA trong file test.py (hàm test_save_voucher)
def test_save_voucher(voucher_id):
    print(f"--- 5) TEST SAVE VOUCHER ID: {voucher_id} ---")
    query = """
    mutation SaveVoucher($voucherId: ID!) {
      saveVoucher(voucherId: $voucherId) {
        ok
        userVoucher { 
          id # Hoặc pk, tùy thuộc vào cách bạn đặt tên trường ID của UserVoucher
          usedCount 
          voucher { voucherId code } 
        }
      }
    }
    """
    return gql(query, {"voucherId": str(voucher_id)})

# ---------------------------------------------------------------------
# 6) Apply voucher (Giả định orderTotal là Float)
# ---------------------------------------------------------------------
def test_apply_voucher(code, order_total):
    print(f"--- 6) TEST APPLY VOUCHER CODE: {code} (Total: {order_total}) ---")
    query = """
    mutation ApplyVoucher($code: String!, $orderTotal: Float!) {
      applyVoucher(voucherCode: $code, orderTotal: $orderTotal) {
        discountAmount
        message
      }
    }
    """
    variables = {
        "code": code,
        "orderTotal": float(order_total)
    }
    return gql(query, variables)

# ---------------------------------------------------------------------
# 7) Use voucher
# ---------------------------------------------------------------------
def test_use_voucher(voucher_id, discount_amount, order_id):
    print(f"--- 7) TEST USE VOUCHER ID: {voucher_id} for Order ID: {order_id} ---")
    query = """
    mutation UseVoucher($voucherId: ID!, $discountAmount: Float!, $orderId: ID!) {
      useVoucher(
        voucherId: $voucherId,
        discountAmount: $discountAmount,
        orderId: $orderId
      ) {
        ok
        message
      }
    }
    """
    variables = {
        "voucherId": str(voucher_id),
        "discountAmount": float(discount_amount),
        "orderId": str(order_id)
    }
    return gql(query, variables)

# ---------------------------------------------------------------------
# 8) Query danh sách voucher theo product
# ---------------------------------------------------------------------
def test_vouchers_for_product(product_id):
    print(f"--- 8) TEST VOUCHERS FOR PRODUCT ID: {product_id} ---")
    query = """
    query vouchersForProduct($productId: ID!) {
      vouchersForProduct(productId: $productId) {
        # Sửa: id -> voucherId
        voucherId code type discountValue
      }
    }
    """
    return gql(query, {"productId": str(product_id)})

# ---------------------------------------------------------------------
# 9) Query voucher user đã lưu
# ---------------------------------------------------------------------
def test_saved_vouchers():
    print("--- 9) TEST SAVED VOUCHERS ---")
    query = """
    query SavedVouchers {
      savedVouchers {
        id
        voucher { voucherId code }
      }
    }
    """
    return gql(query)

# ---------------------------------------------------------------------
# 10) Query voucher platform user chưa lưu
# ---------------------------------------------------------------------
# SỬA trong file test.py (hàm test_platform_vouchers_not_saved)
def test_platform_vouchers_not_saved():
    print("--- 10) TEST PLATFORM VOUCHERS NOT SAVED ---")
    query = """
    query PlatformNotSaved {
      availablePlatformVouchers { # ĐÃ SỬA: SỬ DỤNG TÊN CHÍNH XÁC
        voucherId
        code
        name
        discountType #vdf
        discountValue
        minOrderAmount
        description
      }
    }
    """
    return gql(query)
def test_all_applicable_vouchers(order_total):
    print(f"--- TEST ALL APPLICABLE VOUCHERS (order_total={order_total}) ---")
    query = """
    query AllApplicableVouchers($orderTotal: Float!) {
      allApplicableVouchers(orderTotal: $orderTotal) {
        voucherId
        code
        name
        discountType # sẽ trả về 'PERCENT', 'FIXED', 'FREESHIP' -nếu là voucher freeship thì giá trị này sẽ là 'FREESHIP',còn voucher giảm giá tiền mặt hoặc phần trăm sẽ trả về 'FIXED' hoặc 'PERCENT'
        discountValue
        minOrderAmount
        description
      }
    }
    """
    variables = {
        "orderTotal": float(order_total)
    }
    return gql(query, variables)
# ---------------------------------------------------------------------
# CHẠY TEST (Test Flow Logic)
# ---------------------------------------------------------------------
if __name__ == "__main__":
    # --- 1. SETUP ---
    
    # 1. Tạo Voucher Platform (PLT10)
    result_platform = test_create_platform_voucher()
    platform_voucher_id = result_platform.get('data', {}).get('createPlatformVoucher', {}).get('voucher', {}).get('voucherId')
    platform_voucher_code = result_platform.get('data', {}).get('createPlatformVoucher', {}).get('voucher', {}).get('code')
    print(f"\nCREATED PLATFORM VOUCHER ID: {platform_voucher_id}, CODE: {platform_voucher_code}\n")
    
    # 2. Tạo Voucher Store (STORE50)
    result_store = test_create_store_voucher(TEST_STORE_ID)
    store_voucher_id = result_store.get('data', {}).get('createStoreVoucher', {}).get('voucher', {}).get('voucherId')
    store_voucher_code = result_store.get('data', {}).get('createStoreVoucher', {}).get('voucher', {}).get('code')
    print(f"\nCREATED STORE VOUCHER ID: {store_voucher_id}, CODE: {store_voucher_code}\n")
    
    time.sleep(1) # Đợi 1 giây để đảm bảo mã code duy nhất

    # --- 2. VOUCHER LIFECYCLE TESTS ---

    if platform_voucher_id:
        # 3. Update Voucher Platform
        test_update_voucher(platform_voucher_id)

        # 5. Save Voucher Platform (Cần userId trong context/auth)
        test_save_voucher(platform_voucher_id)

    # 6. Apply Voucher (Dùng code Platform vừa tạo)
    if platform_voucher_code:
        # Giả định tổng đơn hàng đủ điều kiện áp dụng (vd: 200,000 > minOrderAmount 100,000)
        apply_result = test_apply_voucher(platform_voucher_code, 200000.0)
        
        # 7. Use Voucher (Chỉ chạy nếu Apply thành công)
        if apply_result and not apply_result.get('errors'):
            discount = apply_result.get('data', {}).get('applyVoucher', {}).get('discountAmount')
            if platform_voucher_id and TEST_ORDER_ID and discount:
                test_use_voucher(platform_voucher_id, discount, TEST_ORDER_ID)
    
    # --- 3. QUERY TESTS ---
    
    # 8. Query voucher áp dụng cho Product (Cần setup liên kết VoucherProduct/VoucherCategory/VoucherStore)
    test_vouchers_for_product(TEST_PRODUCT_ID)

    # 9. Query voucher user đã lưu (Dựa trên test_save_voucher ở bước 5)
    test_saved_vouchers()

    # 10. Query voucher platform user chưa lưu
    test_platform_vouchers_not_saved()

    # --- 4. CLEANUP ---
    if platform_voucher_id:
        # 4. Delete Voucher Platform
        test_delete_voucher(platform_voucher_id)
        
    if store_voucher_id:
        # 4. Delete Voucher Store
        test_delete_voucher(store_voucher_id)