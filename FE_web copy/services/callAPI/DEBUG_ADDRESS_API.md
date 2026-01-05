# Debug Address API

## 🔍 Cách kiểm tra API hoạt động

### 1. Mở Console trong Browser (F12)

Khi bạn mở form địa chỉ và chọn tỉnh/phường, bạn sẽ thấy các log sau:

```
🌍 Fetching provinces from: https://provinces.open-api.vn/api/v2/p/
✅ Provinces loaded: 63

🏘️ Fetching wards from: https://provinces.open-api.vn/api/v2/p/79?depth=2
✅ Wards loaded: 20 for province 79

🏠 Fetching hamlets from GHTK: https://services.giaohangtietkiem.vn/services/address/getAddressLevel4?province=...
✅ Hamlets loaded: {...}
```

### 2. Kiểm tra Network Tab

**Provinces API:**
- URL: `https://provinces.open-api.vn/api/v2/p/`
- Method: GET
- Status: 200 OK
- Response: Array of provinces

**Wards API:**
- URL: `https://provinces.open-api.vn/api/v2/p/{provinceId}?depth=2`
- Method: GET
- Status: 200 OK
- Response: Object with `wards` array

**Hamlets API (GHTK):**
- URL: `https://services.giaohangtietkiem.vn/services/address/getAddressLevel4`
- Method: GET
- Headers: `Token: [GHTK_TOKEN]`
- Status: 200 OK (hoặc CORS error)
- Response: Object with hamlet data

---

## ⚠️ Troubleshooting

### Lỗi 1: Provinces không load

**Triệu chứng:**
- Dropdown tỉnh trống
- Console: `❌ Error fetching provinces`

**Nguyên nhân:**
- API provinces.open-api.vn down hoặc bị rate limit
- Network issue

**Giải pháp:**
- Kiểm tra internet connection
- Thử truy cập `https://provinces.open-api.vn/api/v2/p/` trực tiếp trong browser
- Fallback: Cho phép nhập thủ công (đã implement)

---

### Lỗi 2: Wards không load

**Triệu chứng:**
- Chọn tỉnh xong nhưng phường/xã không hiện
- Console: `⚠️ getWards called without provinceId` hoặc `❌ Error fetching wards`

**Nguyên nhân:**
- `provinceId` không được set đúng
- API không trả về data cho tỉnh đó
- Network issue

**Debug:**
```javascript
// Check newAddress state
console.log('newAddress:', newAddress);
console.log('provinceId:', newAddress.provinceId);
```

**Giải pháp:**
- Đảm bảo `provinceId` được set khi chọn tỉnh
- Kiểm tra format data từ provinces API
- Fallback: Cho phép nhập thủ công

---

### Lỗi 3: Hamlets không load (CORS)

**Triệu chứng:**
- Console: `❌ GHTK API unavailable (CORS/Network)`
- Network tab: Request bị cancel hoặc status (failed)

**Nguyên nhân:**
- GHTK API không cho phép CORS từ browser
- Token không hợp lệ
- API rate limit

**Giải pháp HIỆN TẠI:**
- Cho phép nhập thủ công (optional field)
- User có thể bỏ qua hamlet

**Giải pháp DÀI HẠN:**
- Tạo proxy endpoint trên backend Django
- Backend gọi GHTK API, frontend gọi backend
- Ví dụ:
  ```python
  # Django view
  @api_view(['GET'])
  def get_hamlets(request):
      province = request.GET.get('province')
      ward = request.GET.get('ward')
      
      response = requests.get(
          'https://services.giaohangtietkiem.vn/services/address/getAddressLevel4',
          params={'province': province, 'district': '', 'ward_street': ward},
          headers={'Token': GHTK_TOKEN}
      )
      
      return Response(response.json())
  ```

---

## 🧪 Test với Python (như bạn đã làm)

```python
import requests

# Test Provinces
resp = requests.get('https://provinces.open-api.vn/api/v2/p/')
print(f"Provinces: {len(resp.json())} items")

# Test Wards
resp = requests.get('https://provinces.open-api.vn/api/v2/p/79?depth=2')
print(f"Wards: {len(resp.json()['wards'])} items")

# Test Hamlets (GHTK)
resp = requests.get(
    'https://services.giaohangtietkiem.vn/services/address/getAddressLevel4',
    params={'province': 'TP.Hồ Chí Minh', 'district': '', 'ward_street': 'Phường Bến Nghé'},
    headers={'Token': '2P8zJRNHjCwAoNCRzzUXDJMJgiJZzPnoZfQqZic'}
)
print(f"Hamlets: {resp.json()}")
```

**Kết quả Python vs Browser:**
- Python: ✅ Hoạt động → Không bị CORS
- Browser: ❌ CORS error → Bị chặn bởi browser security

---

## ✅ UX Flow Đã Implement

1. **Tỉnh/Thành phố:**
   - Auto load on mount
   - Nếu có data → Dropdown
   - Nếu không có → Text input thủ công
   - ⚠️ Message: "Không tải được danh sách tỉnh"

2. **Phường/Xã:**
   - **DISABLED** nếu chưa chọn tỉnh
   - Label hint: "(Chọn tỉnh trước)"
   - Loading spinner khi fetch data
   - Nếu có data → Dropdown
   - Nếu không có → Text input thủ công
   - ⚠️ Message: "Không tải được danh sách phường"

3. **Thôn/Khu/Ấp:**
   - **DISABLED** nếu chưa chọn phường
   - Label hint: "(Chọn phường/xã trước)"
   - Loading spinner khi fetch data
   - Nếu có data → Dropdown
   - Nếu không có → Text input thủ công (optional)
   - ℹ️ Message: "Không có dữ liệu. Bạn có thể nhập thủ công hoặc bỏ qua"

---

## 📝 Backend Recommendation

Tạo proxy endpoint để bypass CORS:

```python
# graphql_api/address/views.py
from django.http import JsonResponse
import requests
from django.views.decorators.http import require_GET

@require_GET
def get_hamlets_proxy(request):
    province = request.GET.get('province')
    ward = request.GET.get('ward')
    
    if not province or not ward:
        return JsonResponse({'success': False, 'message': 'Missing parameters'})
    
    try:
        response = requests.get(
            'https://services.giaohangtietkiem.vn/services/address/getAddressLevel4',
            params={'province': province, 'district': '', 'ward_street': ward},
            headers={'Token': '2P8zJRNHjCwAoNCRzzUXDJMJgiJZzPnoZfQqZic'},
            timeout=5
        )
        return JsonResponse(response.json())
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

# urls.py
urlpatterns = [
    path('api/hamlets/', get_hamlets_proxy, name='hamlets_proxy'),
]
```

Frontend sẽ call: `/api/hamlets/?province=...&ward=...`

---

## 🎯 Summary

- ✅ Provinces API: Hoạt động tốt
- ✅ Wards API: Hoạt động tốt
- ⚠️ Hamlets API: Bị CORS (cần backend proxy)
- ✅ UX: Disabled states, loading indicators, fallback inputs
- ✅ Error handling: Graceful degradation
- ✅ User friendly: Hint messages, manual input option
