# Hệ thống Trả hàng & Hoàn tiền

## 📋 Flow trả hàng chuẩn TMDT

### 1. Buyer tạo yêu cầu trả hàng
```
POST /api/returns/create_return/

Body:
{
  "order_id": 123,
  "sub_order_id": 456,  // optional
  "return_type": "refund",  // refund hoặc exchange
  "reason": "damaged",  // wrong_item, damaged, not_as_described, size_issue, changed_mind, quality_issue, other
  "description": "Sản phẩm bị rách góc trái...",
  "items": [
    {"order_item_id": 1, "quantity": 2}
  ],
  "images": [file1, file2]  // multipart/form-data
}
```

**Điều kiện:**
- Order status = 'completed'
- Trong vòng 7 ngày kể từ khi nhận hàng
- Chưa có return request đang xử lý

### 2. Shop duyệt/từ chối (Admin)
- Shop vào Django Admin → Returns → Approve/Reject
- Hoặc API riêng cho shop (có thể thêm sau)

Status chuyển: `pending` → `approved` hoặc `rejected`

### 3. Buyer gửi hàng về
```
POST /api/returns/{id}/update_tracking/

Body:
{
  "tracking_code": "GHTK123456"
}
```

Status chuyển: `approved` → `shipping_back`

### 4. Shop nhận hàng & kiểm tra (Admin)
- Kiểm tra hàng trả có đúng điều kiện không
- Cập nhật status: `shipping_back` → `received`

### 5. Hoàn tiền/Đổi hàng (Admin)
- Xử lý refund hoặc gửi hàng mới
- Cập nhật status: `received` → `completed`

## 🔄 Status Flow

```
pending (Chờ duyệt)
    ↓
approved (Đã duyệt - Chờ gửi hàng)
    ↓
shipping_back (Đang gửi hàng về)
    ↓
received (Shop đã nhận hàng)
    ↓
completed (Hoàn thành)

Có thể: cancelled (Buyer hủy) hoặc rejected (Shop từ chối)
```

## 📡 API Endpoints

### Buyer APIs
- `GET /api/returns/` - Danh sách yêu cầu của mình
- `POST /api/returns/create_return/` - Tạo yêu cầu mới
- `GET /api/returns/{id}/` - Chi tiết yêu cầu
- `POST /api/returns/{id}/cancel/` - Hủy yêu cầu (chỉ khi pending)
- `POST /api/returns/{id}/update_tracking/` - Cập nhật mã vận đơn trả

### Shop APIs
- `POST /api/returns/{id}/shop/approve/` - Duyệt yêu cầu trả hàng
- `POST /api/returns/{id}/shop/reject/` - Từ chối yêu cầu
- `POST /api/returns/{id}/shop/mark_received/` - Đánh dấu đã nhận hàng trả về
- `POST /api/returns/{id}/shop/complete/` - Hoàn thành (tự động refund hoặc tạo order mới nếu exchange)
- `GET /api/returns/shop/list/?status=pending` - Danh sách returns của shop

## 🗃️ Database Models

### ReturnRequest
- Thông tin yêu cầu trả hàng
- Link tới Order, SubOrder, Buyer
- **exchange_order**: Link tới Order mới được tạo khi type='exchange'
- Status tracking
- Refund amount

### ReturnItem
- Chi tiết sản phẩm trả (có thể trả 1 phần)
- Quantity trả

### ReturnImage
- Ảnh chứng minh (hàng hỏng, không đúng mô tả...)

### ReturnTracking
- Lịch sử xử lý (audit log)
- Ghi lại mỗi lần status thay đổi

## 🔧 Advanced Features (Implemented)

**Note**: Hiện tại chỉ admin (is_staff) mới access được shop APIs. 
Để enable cho shop owner thật:
1. Thêm `owner` field vào Store model
2. Uncomment code trong `returns/permissions.py` và `returns/views.py shop_list()`

## 💡 Best Practices

1. **Thời gian trả hàng**: 7-15 ngày (hiện tại: 7 ngày)
2. **Upload ảnh**: Bắt buộc với lý do "damaged", "not_as_described"
3. **Phí ship trả**: 
   - Lỗi shop: shop chịu
   - Đổi ý: buyer chịu
4. **Refund**: Hoàn về ví hoặc tài khoản ngân hàng (3-7 ngày)

## 🚀 Next Steps

### ✅ Completed
- ✅ Exchange flow with auto order creation
- ✅ Shop permission system (IsShopOwner)
- ✅ Shop APIs (approve, reject, mark_received, complete, list)

### Phase 2 - Store Owner Integration
- Add `owner` field to Store model: `owner = models.ForeignKey(User, ...)`
- Enable IsShopOwner permission filtering in production
- Create shop dashboard for return management

### Phase 3 - Notifications
- Notification khi có return request (to shop)
- Notification khi approve/reject (to buyer)
- Notification khi completed (to buyer with refund/exchange info)

### Phase 4 - Production Deployment
- Add VNPay refund integration for production merchant account
- Add shipment creation for exchange orders
- Add photo validation (require photos for damaged/not_as_described)
- Rate limiting for return requests

## 📱 Flutter Integration

```dart
// Model
class ReturnRequest {
  final int returnId;
  final int orderId;
  final String returnType;
  final String reason;
  final String description;
  final double refundAmount;
  final String status;
  final List<ReturnItem> items;
  final List<String> images;
}

// Create return request
Future<void> createReturnRequest({
  required int orderId,
  required String reason,
  required String description,
  required List<Map<String, int>> items,
  List<File>? images,
}) async {
  var request = http.MultipartRequest(
    'POST',
    Uri.parse('$baseUrl/api/returns/create_return/'),
  );
  
  request.headers['Authorization'] = 'Bearer $token';
  request.fields['order_id'] = orderId.toString();
  request.fields['return_type'] = 'refund';
  request.fields['reason'] = reason;
  request.fields['description'] = description;
  request.fields['items'] = jsonEncode(items);
  
  // Add images
  if (images != null) {
    for (var img in images) {
      request.files.add(await http.MultipartFile.fromPath('images', img.path));
    }
  }
  
  var response = await request.send();
  // Handle response...
}
```

## ⚠️ Notes

- **Refund**: Hiện tại shop cần manual refund (VNPay sandbox không hỗ trợ refund API)
- **Shop APIs**: Đã implement đầy đủ, hiện tại chỉ admin access (cần thêm Store.owner để enable shop owners)
- **Notification**: Chưa tích hợp notification real-time
- **Exchange flow**: Đã hoàn thành - tự động tạo order mới khi đổi hàng
