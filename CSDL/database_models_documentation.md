# Tài liệu Database Models - Dự án SHOEX với Store System

## Tổng quan hệ thống

Dự án SHOEX là một hệ thống thương mại điện tử đa cửa hàng (marketplace) bán giày dép với các module chính:

- **Users**: Quản lý người dùng (buyer, seller, admin)
- **Stores**: Quản lý cửa hàng và seller
- **Products**: Quản lý sản phẩm thuộc về Store
- **Collection**: Quản lý bộ sưu tập sản phẩm theo mùa/chủ đề
- **Orders**: Quản lý đơn hàng
- **Cart**: Quản lý giỏ hàng
- **Address**: Quản lý địa chỉ giao hàng
- **Payments**: Quản lý thanh toán
- **Reviews**: Quản lý đánh giá sản phẩm và cửa hàng
- **Shipments**: Quản lý vận chuyển
- **Discount**: Quản lý voucher và khuyến mại
- **Chatbot**: Hỗ trợ chatbot (chưa có models)

---

## 1. Module Users (users/models.py)

### User

Quản lý người dùng hệ thống, kế thừa từ Django AbstractUser.

**Các trường dữ liệu:**

- `id`: Primary key (tự động từ AbstractUser)
- `username`: Tên đăng nhập (từ AbstractUser)
- `email`: Email (từ AbstractUser)
- `password`: Mật khẩu (từ AbstractUser)
- `role`: CharField - Vai trò (choices: 'buyer', 'seller', 'admin')
- `full_name`: CharField - Họ và tên (max_length=100)
- `phone`: CharField - Số điện thoại (max_length=20)
- `created_at`: DateTimeField - Ngày tạo (auto_now_add=True)

**Relationships:**

- One-to-many với Store (qua StoreUser)
- One-to-many với Address
- One-to-many với Order (as buyer)
- One-to-one với Cart
- One-to-many với UserVoucher
- One-to-many với StoreFollower
- One-to-many với StoreReview

---

## 2. Module Stores (stores/models.py)

### Store

Quản lý thông tin cửa hàng.

**Các trường dữ liệu:**

- `store_id`: CharField - Primary key (max_length=50)
- `name`: CharField - Tên cửa hàng (max_length=255, NOT NULL)
- `slug`: CharField - URL thân thiện (max_length=255, UNIQUE)
- `description`: TextField - Mô tả chi tiết (optional)
- `email`: CharField - Email liên hệ (max_length=255, optional)
- `phone`: CharField - Số điện thoại (max_length=20, optional)
- `address`: TextField - Địa chỉ chi tiết (optional)
- `location`: CharField - Khu vực (max_length=255, optional)
- `avatar`: CharField - URL ảnh đại diện (max_length=500, optional)
- `cover_image`: CharField - URL ảnh bìa (max_length=500, optional)
- `logo`: CharField - URL logo (max_length=500, optional)
- `rating`: DecimalField - Điểm đánh giá (max_digits=2, decimal_places=1, default=0.0)
- `total_reviews`: IntegerField - Tổng số đánh giá (default=0)
- `followers_count`: IntegerField - Số người theo dõi (default=0)
- `products_count`: IntegerField - Số sản phẩm (default=0)
- `total_sales`: IntegerField - Tổng đơn hàng đã bán (default=0)
- `total_revenue`: DecimalField - Tổng doanh thu (max_digits=15, decimal_places=2, default=0)
- `is_verified`: BooleanField - Đã xác minh (default=False)
- `is_active`: BooleanField - Hoạt động (default=True)
- `status`: CharField - Trạng thái (choices: active, inactive, suspended, default=active)
- `response_time`: CharField - Thời gian phản hồi (max_length=20, optional)
- `response_rate`: DecimalField - Tỷ lệ phản hồi (max_digits=3, decimal_places=1, default=0)
- `cod_enabled`: BooleanField - Cho phép COD (default=True)
- `express_shipping`: BooleanField - Giao hàng nhanh (default=True)
- `standard_shipping`: BooleanField - Giao hàng thường (default=True)
- `free_shipping_min`: DecimalField - Miễn phí ship từ (max_digits=12, decimal_places=2, optional)
- `return_policy`: TextField - Chính sách đổi trả (optional)
- `shipping_policy`: TextField - Chính sách vận chuyển (optional)
- `warranty_policy`: TextField - Chính sách bảo hành (optional)
- `currency`: CharField - Đơn vị tiền tệ (max_length=5, default=VND)
- `timezone`: CharField - Múi giờ (max_length=50, default=Asia/Ho_Chi_Minh)
- `join_date`: DateTimeField - Ngày tham gia (NOT NULL)
- `created_at`: DateTimeField - Ngày tạo (auto_now_add=True)
- `updated_at`: DateTimeField - Ngày cập nhật (auto_now=True)

**Relationships:**

- Many-to-many với User qua StoreUser
- One-to-many với Product
- Many-to-many với Category qua StoreCategory
- One-to-many với StoreReview
- One-to-many với StoreFollower
- One-to-many với StoreAnalytics
- One-to-one với StoreSettings
- One-to-many với StoreImage
- One-to-many với StoreInvitation
- One-to-many với Voucher (seller vouchers)

### StoreUser

Quản lý thành viên cửa hàng và phân quyền.

**Các trường dữ liệu:**

- `id`: AutoField - Primary key
- `store`: ForeignKey - Store
- `user`: ForeignKey - User
- `role`: CharField - Vai trò (choices: owner, admin, manager, employee)
- `status`: CharField - Trạng thái (choices: active, inactive, pending, default=pending)
- `granted_permissions`: JSONField - Quyền bổ sung được cấp (optional)
- `revoked_permissions`: JSONField - Quyền bị thu hồi (optional)
- `invited_by`: ForeignKey - Người mời (User, optional)
- `invited_at`: DateTimeField - Thời gian được mời (optional)
- `joined_at`: DateTimeField - Thời gian tham gia (optional)
- `last_login`: DateTimeField - Lần đăng nhập cuối (optional)
- `notes`: TextField - Ghi chú (optional)
- `created_at`: DateTimeField - Ngày tạo (auto_now_add=True)
- `updated_at`: DateTimeField - Ngày cập nhật (auto_now=True)

**Constraints:**

- Unique constraint trên (store, user)

### StoreCategory

Liên kết Store với Category.

**Các trường dữ liệu:**

- `id`: AutoField - Primary key
- `store`: ForeignKey - Store
- `category`: ForeignKey - Category
- `is_primary`: BooleanField - Danh mục chính (default=False)
- `created_at`: DateTimeField - Ngày tạo (auto_now_add=True)

**Constraints:**

- Unique constraint trên (store, category)

### StoreReview

Đánh giá cửa hàng.

**Các trường dữ liệu:**

- `id`: AutoField - Primary key
- `store`: ForeignKey - Store
- `user`: ForeignKey - User (người đánh giá)
- `order`: ForeignKey - Order liên quan (optional)
- `rating`: IntegerField - Điểm đánh giá (1-5)
- `title`: CharField - Tiêu đề (max_length=255, optional)
- `comment`: TextField - Nội dung đánh giá (optional)
- `images`: JSONField - Ảnh đính kèm (optional)
- `helpful_count`: IntegerField - Số lượt hữu ích (default=0)
- `is_verified`: BooleanField - Đánh giá đã xác thực (default=False)
- `created_at`: DateTimeField - Ngày tạo (auto_now_add=True)
- `updated_at`: DateTimeField - Ngày cập nhật (auto_now=True)

### StoreFollower

Người theo dõi cửa hàng.

**Các trường dữ liệu:**

- `store`: ForeignKey - Store (Primary key)
- `user`: ForeignKey - User (Primary key)
- `followed_at`: DateTimeField - Thời gian theo dõi (auto_now_add=True)
- `is_active`: BooleanField - Còn theo dõi (default=True)

**Constraints:**

- Composite primary key (store, user)

### StoreAnalytics

Thống kê cửa hàng.

**Các trường dữ liệu:**

- `id`: AutoField - Primary key
- `store`: ForeignKey - Store
- `date`: DateField - Ngày thống kê
- `views`: IntegerField - Lượt xem (default=0)
- `visitors`: IntegerField - Khách truy cập (default=0)
- `orders`: IntegerField - Đơn hàng (default=0)
- `revenue`: DecimalField - Doanh thu (max_digits=15, decimal_places=2, default=0)
- `new_followers`: IntegerField - Người theo dõi mới (default=0)
- `products_added`: IntegerField - Sản phẩm thêm mới (default=0)

**Constraints:**

- Unique constraint trên (store, date)

### StoreSettings

Cài đặt cửa hàng.

**Các trường dữ liệu:**

- `store`: OneToOneField - Store (Primary key)
- `auto_confirm_orders`: BooleanField - Tự động xác nhận đơn (default=False)
- `notification_email`: BooleanField - Thông báo email (default=True)
- `notification_sms`: BooleanField - Thông báo SMS (default=False)
- `working_hours_start`: TimeField - Giờ làm việc bắt đầu (optional)
- `working_hours_end`: TimeField - Giờ làm việc kết thúc (optional)
- `working_days`: JSONField - Ngày làm việc (optional)
- `vacation_mode`: BooleanField - Chế độ nghỉ phép (default=False)
- `vacation_message`: TextField - Thông báo nghỉ phép (optional)
- `auto_reply_message`: TextField - Tin nhắn tự động (optional)

### StoreImage

Hình ảnh cửa hàng.

**Các trường dữ liệu:**

- `id`: AutoField - Primary key
- `store`: ForeignKey - Store
- `image_url`: CharField - URL hình ảnh (max_length=500)
- `image_type`: CharField - Loại hình ảnh (choices: cover, gallery, logo, banner)
- `title`: CharField - Tiêu đề (max_length=255, optional)
- `alt_text`: CharField - Mô tả (max_length=255, optional)
- `sort_order`: IntegerField - Thứ tự sắp xếp (default=0)
- `is_active`: BooleanField - Đang sử dụng (default=True)
- `created_at`: DateTimeField - Ngày tạo (auto_now_add=True)

### StoreRole

Vai trò cửa hàng.

**Các trường dữ liệu:**

- `id`: AutoField - Primary key
- `role_name`: CharField - Tên vai trò (max_length=50, unique)
- `role_display_name`: CharField - Tên hiển thị (max_length=100, optional)
- `description`: TextField - Mô tả vai trò (optional)
- `default_permissions`: JSONField - Quyền mặc định (optional)
- `is_system_role`: BooleanField - Vai trò hệ thống (default=True)
- `created_at`: DateTimeField - Ngày tạo (auto_now_add=True)

### StorePermission

Quyền hạn cửa hàng.

**Các trường dữ liệu:**

- `id`: AutoField - Primary key
- `permission_name`: CharField - Tên quyền (max_length=100, unique)
- `permission_group`: CharField - Nhóm quyền (max_length=50, optional)
- `display_name`: CharField - Tên hiển thị (max_length=100, optional)
- `description`: TextField - Mô tả quyền (optional)
- `is_active`: BooleanField - Còn sử dụng (default=True)
- `created_at`: DateTimeField - Ngày tạo (auto_now_add=True)

### StoreInvitation

Lời mời tham gia cửa hàng.

**Các trường dữ liệu:**

- `id`: AutoField - Primary key
- `store`: ForeignKey - Store
- `email`: CharField - Email được mời (max_length=255)
- `role`: CharField - Vai trò được mời (max_length=50)
- `invitation_token`: CharField - Token xác thực (max_length=255, unique)
- `invited_by`: ForeignKey - Người gửi lời mời (User)
- `invited_at`: DateTimeField - Thời gian gửi (auto_now_add=True)
- `expires_at`: DateTimeField - Thời gian hết hạn
- `accepted_at`: DateTimeField - Thời gian chấp nhận (optional)
- `status`: CharField - Trạng thái (choices: pending, accepted, expired, revoked, default=pending)
- `message`: TextField - Tin nhắn mời (optional)
- `created_at`: DateTimeField - Ngày tạo (auto_now_add=True)

---

## 3. Module Products (products/models.py)

### Category

Quản lý danh mục sản phẩm với cấu trúc cây phân cấp.

**Các trường dữ liệu:**

- `category_id`: AutoField - Primary key
- `name`: CharField - Tên danh mục (max_length=100)
- `description`: TextField - Mô tả (optional)
- `parent`: ForeignKey - Danh mục cha (self-reference, optional)
- `thumbnail_image`: ImageField - Ảnh đại diện (upload_to='categories/thumbnails/')
- `is_active`: BooleanField - Trạng thái hoạt động
- `created_at`: DateTimeField - Ngày tạo

**Relationships:**

- Parent-child với chính nó (self-reference)
- Many-to-many với Store qua StoreCategory
- One-to-many với Product
- Many-to-many với Voucher qua VoucherCategory

### Product

Sản phẩm chính - Thuộc về Store thay vì User.

**Các trường dữ liệu:**

- `product_id`: AutoField - Primary key
- `slug`: SlugField - URL slug (unique)
- `store`: ForeignKey - Store (thay vì seller/user)
- `category`: ForeignKey - Danh mục
- `name`: CharField - Tên sản phẩm (max_length=200)
- `description`: TextField - Mô tả sản phẩm
- `base_price`: DecimalField - Giá cơ bản (max_digits=12, decimal_places=2)
- `brand`: CharField - Thương hiệu (optional, max_length=100)
- `model_code`: CharField - Mã model (unique, max_length=100)
- `size_guide_image`: ImageField - Ảnh hướng dẫn chọn size (upload_to='products/size_guides/', optional)
- `is_active`: BooleanField - Trạng thái hoạt động
- `is_featured`: BooleanField - Sản phẩm nổi bật
- `is_hot`: BooleanField - Sản phẩm hot/trending (default=False)
- `collections`: ManyToManyField - Bộ sưu tập (qua ProductCollection)
- `created_at`: DateTimeField - Ngày tạo
- `updated_at`: DateTimeField - Ngày cập nhật

**Properties:**

- `min_price`: Giá thấp nhất từ variants
- `max_price`: Giá cao nhất từ variants
- `total_stock`: Tổng tồn kho
- `available_colors`: Các màu có sẵn

**Relationships:**

- Thuộc về Store (thay vì User)
- Thuộc về Category
- Many-to-many với Collection qua ProductCollection
- One-to-many với ProductVariant
- One-to-many với ProductAttributeOption
- One-to-many với ProductImage

### ProductAttribute

Định nghĩa các thuộc tính sản phẩm (Size, Color, Material, Style...).

**Các trường dữ liệu:**

- `attribute_id`: AutoField - Primary key
- `name`: CharField - Tên thuộc tính (unique, max_length=50)
- `type`: CharField - Loại thuộc tính (choices: 'select', 'color', 'text', 'number')
- `is_required`: BooleanField - Bắt buộc
- `has_image`: BooleanField - Có ảnh riêng
- `display_order`: IntegerField - Thứ tự hiển thị
- `created_at`: DateTimeField - Ngày tạo

**Relationships:**

- One-to-many với ProductAttributeOption

### ProductAttributeOption

Các tùy chọn cụ thể cho từng thuộc tính của sản phẩm.

**Các trường dữ liệu:**

- `option_id`: AutoField - Primary key
- `product`: ForeignKey - Sản phẩm
- `attribute`: ForeignKey - Thuộc tính
- `value`: CharField - Giá trị (max_length=100)
- `value_code`: CharField - Mã giá trị (optional, max_length=50)
- `image`: ImageField - Ảnh (optional, upload_to='products/attributes/%Y/%m/')
- `display_order`: IntegerField - Thứ tự hiển thị
- `is_available`: BooleanField - Còn hàng
- `created_at`: DateTimeField - Ngày tạo

**Methods:**

- `get_variants()`: Lấy tất cả variants có tùy chọn này
- `get_available_combinations()`: Lấy các kết hợp khác có sẵn

**Relationships:**

- Thuộc về Product
- Thuộc về ProductAttribute

### ProductVariant

Biến thể sản phẩm - SKU thực tế (Size + Color + ...).

**Các trường dữ liệu:**

- `variant_id`: AutoField - Primary key
- `product`: ForeignKey - Sản phẩm
- `sku`: CharField - Mã SKU (unique, max_length=100)
- `price`: DecimalField - Giá bán (max_digits=12, decimal_places=2)
- `stock`: IntegerField - Tồn kho
- `weight`: DecimalField - Khối lượng kg (max_digits=8, decimal_places=2)
- `option_combinations`: JSONField - Kết hợp thuộc tính {"Size": "39", "Color": "Đen"}
- `is_active`: BooleanField - Trạng thái hoạt động
- `created_at`: DateTimeField - Ngày tạo
- `updated_at`: DateTimeField - Ngày cập nhật

**Properties:**

- `color_name`: Lấy tên màu từ option_combinations
- `size_name`: Lấy size từ option_combinations
- `is_in_stock`: Kiểm tra còn hàng
- `color_image`: Lấy ảnh màu tương ứng

**Relationships:**

- Thuộc về Product
- One-to-many với CartItem
- One-to-many với OrderItem

### ProductImage

Bảng lưu trữ ảnh cho Product (ảnh đại diện + ảnh chính).

**Các trường dữ liệu:**

- `image_id`: AutoField - Primary key
- `product`: ForeignKey - Sản phẩm
- `image`: ImageField - Ảnh sản phẩm (upload_to='products/gallery/%Y/%m/')
- `is_thumbnail`: BooleanField - Ảnh đại diện (chỉ được 1 ảnh)
- `alt_text`: CharField - Alt text cho SEO (optional, max_length=200)
- `display_order`: IntegerField - Thứ tự hiển thị
- `created_at`: DateTimeField - Ngày tạo

**Properties:**

- `image_url`: Trả về URL của ảnh

**Constraints:**

- Mỗi product chỉ có 1 ảnh đại diện

**Relationships:**

- Thuộc về Product

---

## 5. Module Address (address/models.py)

### Address

Quản lý địa chỉ của người dùng với thông tin địa chỉ lưu trực tiếp dưới dạng text.

**Các trường dữ liệu:**

- `address_id`: AutoField - Primary key
- `user`: ForeignKey - Người dùng
- `province`: CharField - Tỉnh/Thành phố (text, max_length=100)
- `ward`: CharField - Xã/Phường (text, max_length=100)
- `hamlet`: CharField - Thôn/Xóm (text, optional, max_length=100)
- `detail`: CharField - Địa chỉ chi tiết (max_length=255)
- `is_default`: BooleanField - Địa chỉ mặc định

**Properties:**

- `full_address`: Trả về địa chỉ đầy đủ

**Methods:**

- `set_as_default()`: Đặt làm địa chỉ mặc định

**Constraints:**

- Mỗi user chỉ có 1 địa chỉ mặc định

**Relationships:**

- Thuộc về User
- One-to-many với Order

---

## 6. Module Cart (cart/models.py)

### Cart

Quản lý giỏ hàng - Hỗ trợ cả user đã đăng nhập và guest user.

**Các trường dữ liệu:**

- `cart_id`: AutoField - Primary key
- `user`: OneToOneField - Người dùng (optional cho guest)
- `session_key`: CharField - Session ID cho guest user (optional, max_length=40)
- `created_at`: DateTimeField - Ngày tạo
- `updated_at`: DateTimeField - Ngày cập nhật
- `expires_at`: DateTimeField - Ngày hết hạn cho guest cart (optional)

**Properties:**

- `total_items`: Tổng số sản phẩm khác nhau
- `total_amount`: Tổng giá trị giỏ hàng
- `total_weight`: Tổng khối lượng

**Methods:**

- `clear()`: Xóa tất cả sản phẩm
- `merge_cart(other_cart)`: Gộp giỏ hàng khác vào

**Constraints:**

- Mỗi cart phải có user HOẶC session_key

**Relationships:**

- Thuộc về User (optional)
- One-to-many với CartItem

### CartItem

Sản phẩm trong giỏ hàng.

**Các trường dữ liệu:**

- `item_id`: AutoField - Primary key
- `cart`: ForeignKey - Giỏ hàng
- `variant`: ForeignKey - Biến thể sản phẩm
- `quantity`: PositiveIntegerField - Số lượng
- `unit_price`: DecimalField - Đơn giá tại thời điểm thêm vào giỏ
- `created_at`: DateTimeField - Ngày thêm vào giỏ
- `updated_at`: DateTimeField - Ngày cập nhật

**Properties:**

- `subtotal`: Tính tổng tiền cho item này
- `current_price`: Giá hiện tại của sản phẩm
- `price_changed`: Kiểm tra giá có thay đổi không

**Constraints:**

- Unique constraint trên (cart, variant)

**Relationships:**

- Thuộc về Cart
- Thuộc về ProductVariant

---

## 4. Module Collection (collection/models.py)

### Collection

Quản lý bộ sưu tập sản phẩm theo mùa hoặc chủ đề.

**Các trường dữ liệu:**

- `collection_id`: AutoField - Primary key
- `title`: CharField - Tiêu đề bộ sưu tập (max_length=200)
- `subtitle`: CharField - Phụ đề (max_length=255, optional)
- `description`: TextField - Mô tả chi tiết (optional)
- `image_url`: URLField - URL hình ảnh chính (optional)
- `banner_image`: URLField - URL hình ảnh banner (optional)
- `season`: CharField - Mùa (choices: spring, summer, autumn, winter, all, max_length=20, default=all)
- `is_featured`: BooleanField - Bộ sưu tập nổi bật (default=False)
- `is_active`: BooleanField - Trạng thái hoạt động (default=True)
- `sort_order`: IntegerField - Thứ tự sắp xếp (default=0)
- `meta_title`: CharField - SEO title (max_length=255, optional)
- `meta_description`: CharField - SEO description (max_length=255, optional)
- `created_at`: DateTimeField - Ngày tạo (auto_now_add=True)
- `updated_at`: DateTimeField - Ngày cập nhật (auto_now=True)

**Properties:**

- `product_count`: Số lượng sản phẩm trong bộ sưu tập
- `featured_products`: Sản phẩm nổi bật trong bộ sưu tập

**Relationships:**

- Many-to-many với Product qua ProductCollection

### ProductCollection

Bảng trung gian quản lý mối quan hệ giữa Product và Collection.

**Các trường dữ liệu:**

- `id`: AutoField - Primary key
- `product`: ForeignKey - Sản phẩm
- `collection`: ForeignKey - Bộ sưu tập
- `is_featured_in_collection`: BooleanField - Nổi bật trong bộ sưu tập (default=False)
- `sort_order`: IntegerField - Thứ tự trong bộ sưu tập (default=0)
- `added_at`: DateTimeField - Ngày thêm vào bộ sưu tập (auto_now_add=True)

**Relationships:**

- Thuộc về Product
- Thuộc về Collection

---

## 7. Module Orders (orders/models.py)

### Order

Đơn hàng chính.

**Các trường dữ liệu:**

- `order_id`: AutoField - Primary key
- `buyer`: ForeignKey - Người mua
- `address`: ForeignKey - Địa chỉ giao hàng
- `total_amount`: DecimalField - Tổng tiền (max_digits=10, decimal_places=2)
- `status`: CharField - Trạng thái đơn hàng (choices: pending, confirmed, shipped, delivered, cancelled)
- `shipment_status`: CharField - Trạng thái vận chuyển
- `created_at`: DateTimeField - Ngày tạo

**Relationships:**

- Thuộc về User (buyer)
- Thuộc về Address
- One-to-many với SubOrder
- One-to-many với OrderItem
- One-to-one với Payment
- Many-to-many với Voucher qua OrderVoucher

### SubOrder

Đơn hàng con (theo store).

**Các trường dữ liệu:**

- `sub_order_id`: AutoField - Primary key
- `order`: ForeignKey - Đơn hàng chính
- `store`: ForeignKey - Store (thay vì seller)
- `total_amount`: DecimalField - Tổng tiền đơn hàng con
- `status`: CharField - Trạng thái đơn hàng con
- `created_at`: DateTimeField - Ngày tạo

**Relationships:**

- Thuộc về Order
- Thuộc về Store (thay vì User)
- One-to-many với OrderItem
- One-to-one với Shipment

### OrderItem

Mục trong đơn hàng.

**Các trường dữ liệu:**

- `order_item_id`: AutoField - Primary key
- `order`: ForeignKey - Đơn hàng
- `sub_order`: ForeignKey - Đơn hàng con
- `variant`: ForeignKey - Biến thể sản phẩm
- `quantity`: IntegerField - Số lượng
- `price_at_order`: DecimalField - Giá tại thời điểm đặt hàng

**Relationships:**

- Thuộc về Order
- Thuộc về SubOrder
- Thuộc về ProductVariant
- One-to-many với Review

---

## 8. Module Payments (payments/models.py)

### Payment

Quản lý thanh toán.

**Các trường dữ liệu:**

- `payment_id`: AutoField - Primary key
- `order`: OneToOneField - Đơn hàng
- `amount`: DecimalField - Số tiền (max_digits=10, decimal_places=2)
- `payment_method`: CharField - Phương thức thanh toán (choices: credit_card, bank_transfer, cod)
- `status`: CharField - Trạng thái (choices: pending, completed, failed)
- `transaction_id`: CharField - Mã giao dịch (optional, max_length=100)
- `paid_at`: DateTimeField - Thời gian thanh toán (optional)

**Relationships:**

- Thuộc về Order (one-to-one)

---

## 9. Module Reviews (reviews/models.py)

### Review

Quản lý đánh giá sản phẩm chi tiết.

**Choices:**

- `ACCURACY_CHOICES`: ['smaller', 'accurate', 'larger'] - Đánh giá độ chính xác so với mô tả
- `QUALITY_CHOICES`: ['poor', 'average', 'good', 'excellent'] - Đánh giá chất lượng

**Các trường dữ liệu:**

- `review_id`: AutoField - Primary key
- `order_item`: ForeignKey - Mục đơn hàng (xác thực đã mua)
- `rating`: IntegerField - Xếp hạng tổng thể (1-5, có validator)
- `size_accuracy`: CharField - Độ chính xác size (choices: ACCURACY_CHOICES, optional)
- `color_accuracy`: CharField - Độ chính xác màu sắc (choices: ACCURACY_CHOICES, optional)
- `material_quality`: CharField - Chất lượng chất liệu (choices: QUALITY_CHOICES, optional)
- `comment`: TextField - Bình luận chi tiết (optional)
- `created_at`: DateTimeField - Ngày tạo

**Properties:**

- `reviewer_name`: Tên người đánh giá (ẩn một phần để bảo mật)
- `rating_stars`: Chuỗi sao hiển thị rating (⭐⭐⭐⭐⭐)
- `short_comment`: Comment rút gọn (150 ký tự đầu)
- `variant_display`: Thông tin phân loại đã mua từ order_item.variant

**Constraints:**

- Unique constraint: Mỗi order_item chỉ có 1 review

**Relationships:**

- Thuộc về OrderItem
- Thông qua OrderItem có thể truy cập Product, ProductVariant, User (buyer)

**Cách lấy thông tin liên quan:**

```python
# Lấy sản phẩm từ review
product = review.order_item.variant.product

# Lấy store từ review
store = review.order_item.variant.product.store

# Lấy người đánh giá từ review
reviewer = review.order_item.order.buyer

# Lấy thông tin variant đã mua
variant_info = review.variant_display
```

### ReviewImage

Bảng lưu trữ ảnh đính kèm trong review.

**Các trường dữ liệu:**

- `image_id`: AutoField - Primary key
- `review`: ForeignKey - Review
- `image`: ImageField - Ảnh đánh giá (upload_to='reviews/images/%Y/%m/')
- `caption`: CharField - Mô tả ảnh (max_length=200, optional)
- `display_order`: IntegerField - Thứ tự hiển thị (default=0)
- `created_at`: DateTimeField - Ngày tạo

### ReviewVideo

Bảng lưu trữ video đính kèm trong review.

**Các trường dữ liệu:**

- `video_id`: AutoField - Primary key
- `review`: ForeignKey - Review
- `video`: FileField - Video đánh giá (upload_to='reviews/videos/%Y/%m/')
- `thumbnail`: ImageField - Ảnh thumbnail (upload_to='reviews/video_thumbnails/%Y/%m/', optional)
- `duration`: CharField - Thời lượng (max_length=10, optional)
- `caption`: CharField - Mô tả video (max_length=200, optional)
- `display_order`: IntegerField - Thứ tự hiển thị (default=0)
- `created_at`: DateTimeField - Ngày tạo

### ReviewHelpful

Bảng lưu trữ thông tin người dùng đánh giá review hữu ích.

**Các trường dữ liệu:**

- `review`: ForeignKey - Review
- `user`: ForeignKey - User
- `is_helpful`: BooleanField - Hữu ích (default=True)
- `created_at`: DateTimeField - Ngày vote

**Constraints:**

- Unique constraint trên (review, user)

---

## 10. Module Shipments (shipments/models.py)

### Shipment

Quản lý vận chuyển.

**Các trường dữ liệu:**

- `shipment_id`: AutoField - Primary key
- `sub_order`: OneToOneField - Đơn hàng con
- `tracking_code`: CharField - Mã theo dõi (optional, max_length=100)
- **Thông tin người gửi:**
  - `pick_name`: CharField - Tên người gửi (max_length=100)
  - `pick_address`: CharField - Địa chỉ người gửi (max_length=255)
  - `pick_province`: CharField - Tỉnh người gửi (max_length=50)
  - `pick_ward`: CharField - Phường/Xã người gửi (max_length=50)
  - `pick_tel`: CharField - Số điện thoại người gửi (max_length=20)
- **Thông tin người nhận:**
  - `name`: CharField - Tên người nhận (max_length=100)
  - `address`: CharField - Địa chỉ người nhận (max_length=255)
  - `province`: CharField - Tỉnh người nhận (max_length=50)
  - `ward`: CharField - Phường/Xã người nhận (max_length=50)
  - `hamlet`: CharField - Thôn/Ấp người nhận (optional, max_length=50)
  - `tel`: CharField - Số điện thoại người nhận (max_length=20)
- **Thông tin vận chuyển:**
  - `is_freeship`: BooleanField - Miễn phí vận chuyển
  - `pick_date`: DateField - Ngày lấy hàng
  - `pick_money`: DecimalField - Tiền thu hộ
  - `note`: TextField - Ghi chú (optional)
  - `value`: DecimalField - Giá trị hàng hóa
  - `transport`: CharField - Phương tiện vận chuyển (max_length=50)
  - `pick_option`: CharField - Tùy chọn lấy hàng (choices: cod, non_cod)
  - `deliver_option`: CharField - Tùy chọn giao hàng (choices: xteam, standard)
  - `status`: CharField - Trạng thái vận chuyển (choices: pending, picked, shipped, delivered, failed)
  - `total_weight`: DecimalField - Tổng khối lượng (optional)
- `created_at`: DateTimeField - Ngày tạo
- `updated_at`: DateTimeField - Ngày cập nhật (optional)

**Relationships:**

- Thuộc về SubOrder (one-to-one)
- One-to-many với ShipmentTracking

### ShipmentTracking

Lưu chi tiết lộ trình vận chuyển.

**Các trường dữ liệu:**

- `tracking_id`: AutoField - Primary key
- `shipment`: ForeignKey - Vận chuyển
- `status`: CharField - Trạng thái lộ trình (choices: created, picked_up, in_transit, out_for_delivery, delivered, failed_delivery, returned, cancelled, exception)
- `location`: CharField - Vị trí hiện tại (max_length=255)
- `details`: TextField - Chi tiết trạng thái (optional)
- `timestamp`: DateTimeField - Thời gian sự kiện
- **Thông tin từ API:**
  - `carrier_status_code`: CharField - Mã trạng thái nhà vận chuyển (optional, max_length=50)
  - `carrier_status_description`: TextField - Mô tả trạng thái nhà vận chuyển (optional)
  - `latitude`: DecimalField - Vĩ độ (optional, max_digits=10, decimal_places=8)
  - `longitude`: DecimalField - Kinh độ (optional, max_digits=11, decimal_places=8)
  - `estimated_delivery`: DateTimeField - Thời gian giao hàng dự kiến (optional)
- **Metadata:**
  - `created_at`: DateTimeField - Thời gian lưu bản ghi
  - `updated_at`: DateTimeField - Thời gian cập nhật
  - `api_response`: JSONField - Raw API Response (optional)
  - `sync_at`: DateTimeField - Thời gian đồng bộ (optional)

**Properties:**

- `status_display_vietnamese`: Hiển thị trạng thái bằng tiếng Việt
- `has_location_coordinates`: Kiểm tra có tọa độ vị trí không
- `is_final_status`: Kiểm tra có phải trạng thái cuối cùng không
- `is_in_progress`: Kiểm tra có đang trong quá trình vận chuyển không

**Constraints:**

- Unique constraint trên (shipment, timestamp, status)

**Relationships:**

- Thuộc về Shipment

---

## 11. Module Discount (discount/models.py)

### Voucher

Quản lý voucher chung.

**Các trường dữ liệu:**

- `voucher_id`: AutoField - Primary key
- `code`: CharField - Mã voucher (unique, max_length=50)
- `type`: CharField - Loại voucher (choices: platform, store)
- `store`: ForeignKey - Store (optional cho platform voucher, required cho store voucher)
- `discount_type`: CharField - Loại giảm giá (choices: percent, fixed)
- `discount_value`: DecimalField - Giá trị giảm giá
- `min_order_amount`: DecimalField - Đơn tối thiểu
- `max_discount`: DecimalField - Giảm tối đa (optional)
- `start_date`: DateField - Ngày bắt đầu
- `end_date`: DateField - Ngày hết hạn
- `usage_limit`: IntegerField - Giới hạn sử dụng toàn hệ thống (optional)
- `per_user_limit`: IntegerField - Giới hạn mỗi user
- `is_active`: BooleanField - Trạng thái
- `is_auto`: BooleanField - Tự động áp dụng
- `created_at`: DateTimeField - Ngày tạo
- `updated_at`: DateTimeField - Ngày cập nhật

**Validation Rules:**

- Store voucher phải có store_id
- Platform voucher không được có store_id
- Ngày kết thúc phải sau ngày bắt đầu
- max_discount chỉ áp dụng cho discount_type = percent

**Relationships:**

- Thuộc về Store (optional)
- Many-to-many với Product qua VoucherProduct
- Many-to-many với Category qua VoucherCategory
- Many-to-many với Store qua VoucherStore
- One-to-many với UserVoucher
- One-to-many với OrderVoucher

### VoucherProduct

Liên kết voucher với sản phẩm cụ thể.

**Các trường dữ liệu:**

- `voucher`: ForeignKey - Voucher
- `product`: ForeignKey - Sản phẩm
- `created_at`: DateTimeField - Ngày tạo

**Constraints:**

- Unique constraint trên (voucher, product)

### VoucherCategory

Liên kết voucher với danh mục sản phẩm.

**Các trường dữ liệu:**

- `voucher`: ForeignKey - Voucher
- `category`: ForeignKey - Danh mục
- `created_at`: DateTimeField - Ngày tạo

**Constraints:**

- Unique constraint trên (voucher, category)

### VoucherStore

Liên kết voucher với nhiều store (cho platform voucher áp dụng một số store cụ thể).

**Các trường dữ liệu:**

- `voucher`: ForeignKey - Voucher
- `store`: ForeignKey - Store
- `created_at`: DateTimeField - Ngày tạo

**Constraints:**

- Unique constraint trên (voucher, store)

### UserVoucher

Quản lý user đã lưu voucher nào và số lần sử dụng.

**Các trường dữ liệu:**

- `user`: ForeignKey - Người dùng
- `voucher`: ForeignKey - Voucher
- `saved_at`: DateTimeField - Thời điểm lưu
- `used_count`: IntegerField - Số lần đã sử dụng

**Properties:**

- `can_use`: Kiểm tra user có thể sử dụng voucher này không

**Constraints:**

- Unique constraint trên (user, voucher)

### OrderVoucher

Lưu voucher được áp dụng cho đơn hàng.

**Các trường dữ liệu:**

- `order`: ForeignKey - Đơn hàng
- `voucher`: ForeignKey - Voucher
- `discount_amount`: DecimalField - Số tiền được giảm thực tế
- `applied_at`: DateTimeField - Thời điểm áp dụng

---

## 12. Module Chatbot (chatbot/models.py)

**Chưa có models nào được định nghĩa.**

---

## TỔNG KẾT TẤT CẢ CÁC BẢNG

### **Nhóm User & Authentication:**

1. **User** - Người dùng hệ thống
2. **Address** - Địa chỉ người dùng (lưu text trực tiếp)

### **Nhóm Store Management:**

3. **Store** - Thông tin cửa hàng
4. **StoreUser** - Thành viên cửa hàng và phân quyền
5. **StoreCategory** - Danh mục của cửa hàng
6. **StoreReview** - Đánh giá cửa hàng
7. **StoreFollower** - Người theo dõi cửa hàng
8. **StoreAnalytics** - Thống kê cửa hàng
9. **StoreSettings** - Cài đặt cửa hàng
10. **StoreImage** - Hình ảnh cửa hàng
11. **StoreRole** - Vai trò trong cửa hàng
12. **StorePermission** - Quyền hạn cửa hàng
13. **StoreInvitation** - Lời mời tham gia cửa hàng

### **Nhóm Product Management:**

14. **Category** - Danh mục sản phẩm
15. **Product** - Sản phẩm (thuộc Store)
16. **ProductAttribute** - Thuộc tính sản phẩm
17. **ProductAttributeOption** - Tùy chọn thuộc tính
18. **ProductVariant** - Biến thể sản phẩm (SKU)
19. **ProductImage** - Ảnh sản phẩm
20. **Collection** - Bộ sưu tập sản phẩm
21. **ProductCollection** - Sản phẩm trong bộ sưu tập

### **Nhóm Shopping & Cart:**

22. **Cart** - Giỏ hàng
23. **CartItem** - Sản phẩm trong giỏ hàng

### **Nhóm Order Management:**

24. **Order** - Đơn hàng chính
25. **SubOrder** - Đơn hàng con (theo Store)
26. **OrderItem** - Mục đơn hàng
27. **Payment** - Thanh toán

### **Nhóm Review & Rating:**

28. **Review** - Đánh giá sản phẩm
29. **ReviewImage** - Ảnh đánh giá
30. **ReviewVideo** - Video đánh giá
31. **ReviewHelpful** - Vote review hữu ích

### **Nhóm Shipping & Logistics:**

32. **Shipment** - Vận chuyển
33. **ShipmentTracking** - Theo dõi vận chuyển

### **Nhóm Discount & Promotion:**

34. **Voucher** - Voucher/Mã giảm giá
35. **VoucherProduct** - Voucher cho sản phẩm
36. **VoucherCategory** - Voucher cho danh mục
37. **VoucherStore** - Voucher cho cửa hàng
38. **UserVoucher** - Voucher đã lưu của user
39. **OrderVoucher** - Voucher đã áp dụng

---

## **TỔNG CỘNG: 39 BẢNG**

**Các thay đổi chính so với phiên bản trước:**

1. ✅ **Product được quản lý bởi Store** thay vì User
2. ✅ **SubOrder liên kết với Store** thay vì User
3. ✅ **Voucher có thể thuộc Store** (store voucher) hoặc platform (platform voucher)
4. ✅ **Thêm đầy đủ hệ thống Store** với phân quyền, analytics, settings
5. ✅ **Thêm models cho Review multimedia** (ReviewImage, ReviewVideo)
6. ✅ **Đơn giản hóa hệ thống địa chỉ** - Lưu text trực tiếp (bỏ Province, Ward, Hamlet)
7. ✅ **Thêm hệ thống Collection** - Bộ sưu tập sản phẩm theo mùa/chủ đề
8. ✅ **Thêm thuộc tính is_hot** cho Product - Đánh dấu sản phẩm hot/trending

**Ưu điểm của cấu trúc mới:**

- 🏪 **Multi-store marketplace** hoàn chỉnh
- 👥 **Phân quyền store** linh hoạt (owner, admin, manager, employee)
- 📊 **Analytics và thống kê** chi tiết cho từng store
- 🎯 **Voucher system** đa dạng (platform + store)
- ⭐ **Review system** phong phú với media
- 🚚 **Shipping tracking** chi tiết
- 📚 **Collection system** quản lý bộ sưu tập theo mùa
- 🔥 **Hot products** đánh dấu sản phẩm trending

---

_Tài liệu được cập nhật ngày: 19/11/2025_
_Phiên bản: 2.1 - Collection System Integration_

---
