# Hướng dẫn sử dụng tính năng Vận chuyển (Shipping) trong Checkout

## Tổng quan

Tính năng vận chuyển đã được tích hợp vào màn hình checkout, cho phép người dùng:
- Chọn phương thức vận chuyển (Giao hàng tiết kiệm / Giao hàng nhanh)
- Xem phí vận chuyển thực tế từ GHTK API
- Tự động tính tổng tiền bao gồm phí ship

## Các file đã tạo/sửa đổi

### 1. Model - ShippingMethodModel
**File:** `lib/shop/models/shipping_method_model.dart`

```dart
class ShippingMethodModel {
  final String id;
  final String name;
  final String description;
  final double fee;
  final String estimatedDays;
  final String icon;
  final bool isFreeShip;
}
```

### 2. Controller - ShippingController
**File:** `lib/shop/controllers/shipping_controller.dart`

**Chức năng chính:**
- `loadDefaultShippingMethods()` - Load 2 phương thức mặc định (standard, express)
- `calculateShippingFee()` - Gọi API GHTK để tính phí ship thực tế
- `selectShippingMethod(context)` - Hiển thị bottom sheet để chọn phương thức
- `totalWithShipping` - Getter tính tổng tiền bao gồm ship
- `shippingFee` - Getter lấy phí ship hiện tại

**Cách hoạt động:**
1. Khi user chọn địa chỉ → Controller tự động gọi GHTK API
2. Tính toán dựa trên:
   - Tỉnh/quận đích (từ AddressController)
   - Trọng lượng hàng (500g/sản phẩm)
   - Địa điểm lấy hàng: Hà Nội, Hoàn Kiếm
3. Cập nhật fee cho 2 phương thức:
   - Standard: Fee từ GHTK
   - Express: Fee x 1.5

### 3. Widget - BillingShippingSection
**File:** `lib/features/shop/screens/checkout/widgets/billing_shipping_section.dart`

**Giao diện:**
- Hiển thị phương thức đã chọn với icon, tên, mô tả, phí
- Button "Thay đổi" mở bottom sheet
- Badge "FREESHIP" nếu miễn phí
- Thời gian dự kiến giao hàng

**States:**
- `isLoading` - Đang tính phí
- `selectedMethod == null` - Chưa chọn → Hiện nút "Chọn phương thức"
- `selectedMethod != null` - Đã chọn → Hiện thông tin chi tiết

### 4. Checkout Screen
**File:** `lib/features/shop/screens/checkout/checkout.dart`

**Cập nhật:**
- Import `ShippingController` và `BillingShippingSection`
- Thêm shipping section vào UI (giữa Payment và Address)
- Bottom button hiển thị tổng tiền bao gồm shipping:
  ```dart
  final total = cartController.totalAmount.value + shippingController.shippingFee;
  ```

### 5. Billing Amount Section
**File:** `lib/features/shop/screens/checkout/widgets/billing_amount_section.dart`

**Cập nhật:**
- Hiển thị `Shipping Fee` động từ ShippingController
- Nếu chưa chọn → "Chọn phương thức"
- Nếu đã chọn → Hiển thị số tiền
- Total = Subtotal + Shipping Fee + Tax

## Luồng hoạt động (User Flow)

```
1. User vào CheckoutScreen
   ↓
2. Chọn địa chỉ giao hàng (BillingAddressSection)
   ↓
3. Nhấn "Chọn phương thức vận chuyển"
   ↓
4. ShippingController gọi GHTK API calculate-fee
   ↓
5. Bottom sheet hiện 2 options với fee thực tế:
   - Giao hàng tiết kiệm (3-5 ngày) - $X
   - Giao hàng nhanh (1-2 ngày) - $X*1.5
   ↓
6. User chọn phương thức
   ↓
7. UI cập nhật:
   - BillingShippingSection: Hiển thị phương thức đã chọn
   - BillingAmountSection: Cập nhật Shipping Fee
   - Bottom button: Cập nhật Total
   ↓
8. User nhấn "Checkout $Total"
```

## API Integration

### GHTK Calculate Fee Endpoint

**Request:**
```http
POST http://10.0.2.2:8000/api/shipments/calculate-fee/
Content-Type: application/json

{
  "pick_province": "Hà Nội",
  "pick_district": "Hoàn Kiếm",
  "province": "Hồ Chí Minh",
  "district": "Quận 1",
  "weight": 1500,
  "deliver_option": "none"
}
```

**Response:**
```json
{
  "fee": {
    "fee": 25000,
    "insurance_fee": 1000,
    "ship_fee_only": 25000
  }
}
```

### Code Example (trong ShippingController):

```dart
final response = await http.post(
  Uri.parse('$baseUrl/api/shipments/calculate-fee/'),
  headers: {'Content-Type': 'application/json'},
  body: json.encode(requestBody),
);

if (response.statusCode == 200) {
  final data = json.decode(utf8.decode(response.bodyBytes));
  final fee = (data['fee']['fee'] ?? 0).toDouble();
  final insurance = (data['fee']['insurance_fee'] ?? 0).toDouble();
  
  // Update shipping methods
  shippingMethods[standardIndex] = ShippingMethodModel(
    fee: fee + insurance,
    ...
  );
}
```

## Customization

### Thay đổi địa điểm lấy hàng

Trong `shipping_controller.dart`, dòng 70-71:
```dart
'pick_province': 'Hà Nội', // Thay đổi tỉnh kho
'pick_district': 'Hoàn Kiếm', // Thay đổi quận kho
```

### Thay đổi trọng lượng mặc định

Dòng 68:
```dart
final weight = totalItems * 500; // 500g/item → Có thể thay đổi
```

### Thay đổi hệ số phí express

Dòng 106:
```dart
fee: (fee + insurance) * 1.5, // Express = 1.5x Standard
```

### Thêm phương thức mới

Trong `loadDefaultShippingMethods()`:
```dart
shippingMethods.value = [
  ShippingMethodModel(...), // Standard
  ShippingMethodModel(...), // Express
  ShippingMethodModel(      // NEW
    id: 'ghtk_super_fast',
    name: 'Siêu tốc',
    description: 'Giao trong 2 giờ',
    fee: 0,
    estimatedDays: 'Trong ngày',
    icon: 'rocket',
  ),
];
```

## Testing

### Test Flow

1. **Chọn địa chỉ trước:**
   - Vào checkout
   - Chọn địa chỉ ở `BillingAddressSection`
   - Kiểm tra địa chỉ có province và ward

2. **Chọn phương thức vận chuyển:**
   - Nhấn "Chọn phương thức vận chuyển"
   - Chờ loading (đang gọi API)
   - Kiểm tra 2 options hiển thị với fee khác nhau
   - Chọn 1 option

3. **Kiểm tra UI cập nhật:**
   - BillingShippingSection: Hiển thị phương thức đã chọn
   - BillingAmountSection: Shipping Fee != 0
   - Bottom button: Total = Subtotal + Shipping Fee

4. **Thay đổi phương thức:**
   - Nhấn "Thay đổi"
   - Chọn phương thức khác
   - Kiểm tra UI cập nhật

### Test Cases

| Test Case | Input | Expected Output |
|-----------|-------|-----------------|
| Chưa chọn địa chỉ | Nhấn "Chọn phương thức" | Snackbar: "Vui lòng chọn địa chỉ giao hàng" |
| Đã chọn địa chỉ | Nhấn "Chọn phương thức" | Bottom sheet với 2 options + loading |
| API thành công | Chọn địa chỉ HCM | Fee > 0 cho cả 2 phương thức |
| API lỗi | Network error | Giữ nguyên fee mặc định = 0 |
| Chọn Standard | Tap vào Standard | UI cập nhật, bottom sheet đóng |
| Chọn Express | Tap vào Express | Fee = 1.5x Standard |
| Total tính đúng | Chọn bất kỳ | Total = Subtotal + Shipping Fee |

## Troubleshooting

### Lỗi thường gặp

1. **"Vui lòng chọn địa chỉ giao hàng"**
   - Nguyên nhân: addressController.selectedAddress == null
   - Giải pháp: Chọn địa chỉ trước khi chọn phương thức vận chuyển

2. **Shipping fee = 0 mãi**
   - Nguyên nhân: API GHTK lỗi hoặc chưa cấu hình token
   - Kiểm tra: Backend settings.py có GHTK_API_TOKEN chưa
   - Log: Check console "Error calculating shipping fee: ..."

3. **Bottom sheet không hiện**
   - Nguyên nhân: Context null hoặc Get routing issues
   - Kiểm tra: ShippingController đã được Get.put() chưa

4. **Total không cập nhật**
   - Nguyên nhân: Không dùng Obx() wrapper
   - Kiểm tra: checkout.dart bottomNavigationBar có Obx()

## Tích hợp với Order Processing

Khi user nhấn "Checkout", cần gửi shipping method ID lên backend:

```dart
// Trong OrderController.processOrder()
final shippingController = Get.find<ShippingController>();

final orderData = {
  'items': [...],
  'address_id': addressId,
  'payment_method': paymentMethod,
  'shipping_method_id': shippingController.selectedShippingMethod.value?.id,
  'shipping_fee': shippingController.shippingFee,
  'total_amount': cartController.totalAmount.value + shippingController.shippingFee,
};
```

Backend sẽ tạo Shipment record với:
- `method = shipping_method_id` (ghtk_standard/ghtk_express)
- `fee = shipping_fee`
- Gọi GHTK create_order API

## Tính năng mở rộng

### Sắp tới có thể thêm:

1. **Freeship voucher:**
   - Kiểm tra điều kiện freeship trong CouponCode
   - Set `isFreeShip = true` cho shipping method

2. **Ước tính thời gian chính xác:**
   - GHTK API trả về `estimated_pick_time`, `estimated_deliver_time`
   - Hiển thị: "Nhận hàng dự kiến: 25/12/2024"

3. **Tracking realtime:**
   - Sau khi đặt hàng → Tạo TrackingScreen
   - Gọi GHTK webhook để cập nhật trạng thái

4. **Multiple addresses:**
   - Cho phép chọn địa chỉ khác
   - Tự động recalculate shipping fee

## Kết luận

Tính năng shipping đã được tích hợp hoàn chỉnh vào checkout flow với:
- ✅ UI/UX trực quan, dễ sử dụng
- ✅ Tính phí ship thực tế từ GHTK API
- ✅ Reactive state management với GetX
- ✅ Error handling đầy đủ
- ✅ Sẵn sàng cho production

Để test, chạy app và vào checkout screen!
