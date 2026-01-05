# 📊 **CẤU TRÚC CÁC BẢNG CHO HỆ THỐNG STORE**

## **1. BẢNG CHÍNH - STORES**

| **Trường**    | **Kiểu dữ liệu** | **Ràng buộc**       | **Mô tả**            |
| --------------------- | ------------------------- | --------------------------- | ---------------------------- |
| `id`                | VARCHAR(50)               | PRIMARY KEY                 | ID cửa hàng                |
|                       |                           |                             |                              |
| `name`              | VARCHAR(255)              | NOT NULL                    | Tên cửa hàng              |
| `slug`              | VARCHAR(255)              | UNIQUE                      | URL thân thiện             |
| `description`       | TE                        | NULL                        | Mô tả chi tiết            |
| `email`             | VARCHAR(255)              | NULL                        | Email liên hệ              |
| `phone`             | VARCHAR(20)               | NULL                        | Số điện thoại            |
| `address`           | TEXT                      | NULL                        | Địa chỉ chi tiết         |
| `location`          | VARCHAR(255)              | NULL                        | Khu vực (TP.HCM, HN...)     |
| `avatar`            | VARCHAR(500)              | NULL                        | URL ảnh đại diện         |
| `cover_image`       | VARCHAR(500)              | NULL                        | URL ảnh bìa                |
| `logo`              | VARCHAR(500)              | NULL                        | URL logo chính thức        |
| `rating`            | DECIMAL(2,1)              | DEFAULT 0.0                 | Điểm đánh giá (0.0-5.0) |
| `total_reviews`     | INT                       | DEFAULT 0                   | Tổng số đánh giá        |
| `followers_count`   | INT                       | DEFAULT 0                   | Số người theo dõi        |
| `products_count`    | INT                       | DEFAULT 0                   | Số sản phẩm               |
| `total_sales`       | INT                       | DEFAULT 0                   | Tổng đơn hàng đã bán  |
| `total_revenue`     | DECIMAL(15,2)             | DEFAULT 0                   | Tổng doanh thu              |
| `is_verified`       | BOOLEAN                   | DEFAULT FALSE               | Đã xác minh               |
| `is_active`         | BOOLEAN                   | DEFAULT TRUE                | Hoạt động                 |
| `status`            | ENUM                      | DEFAULT 'active'            | active/inactive/suspended    |
| `response_time`     | VARCHAR(20)               | NULL                        | Thời gian phản hồi        |
| `response_rate`     | DECIMAL(3,1)              | DEFAULT 0                   | Tỷ lệ phản hồi (%)       |
| `cod_enabled`       | BOOLEAN                   | DEFAULT TRUE                | Cho phép COD                |
| `express_shipping`  | BOOLEAN                   | DEFAULT TRUE                | Giao hàng nhanh             |
| `standard_shipping` | BOOLEAN                   | DEFAULT TRUE                | Giao hàng thường          |
| `free_shipping_min` | DECIMAL(12,2)             | NULL                        | Miễn phí ship từ          |
| `return_policy`     | TEXT                      | NULL                        | Chính sách đổi trả      |
| `shipping_policy`   | TEXT                      | NULL                        | Chính sách vận chuyển    |
| `warranty_policy`   | TEXT                      | NULL                        | Chính sách bảo hành      |
| `currency`          | VARCHAR(5)                | DEFAULT 'VND'               | Đơn vị tiền tệ          |
| `timezone`          | VARCHAR(50)               | DEFAULT 'Asia/Ho_Chi_Minh'  | Múi giờ                    |
| `join_date`         | DATETIME                  | NOT NULL                    | Ngày tham gia               |
| `created_at`        | DATETIME                  | DEFAULT CURRENT_TIMESTAMP   | Ngày tạo                   |
| `updated_at`        | DATETIME                  | ON UPDATE CURRENT_TIMESTAMP | Ngày cập nhật             |

## **2. BẢNG DANH MỤC CỬA HÀNG - STORE_CATEGORIES**

| **Trường** | **Kiểu dữ liệu** | **Ràng buộc**      | **Mô tả**       |
| ------------------ | ------------------------- | -------------------------- | ----------------------- |
| `id`             | INT                       | PRIMARY KEY AUTO_INCREMENT | ID danh mục            |
| `store_id`       | VARCHAR(50)               | NOT NULL, FK               | ID cửa hàng           |
| `category_id`    | INT                       | NOT NULL, FK               | ID danh mục sản phẩm |
|                    |                           |                            |                         |
| `created_at`     | DATETIME                  | DEFAULT CURRENT_TIMESTAMP  | Ngày tạo              |

## **3. BẢNG ĐÁNH GIÁ CỬA HÀNG - STORE_REVIEWS**

| **Trường** | **Kiểu dữ liệu** | **Ràng buộc**       | **Mô tả**           |
| ------------------ | ------------------------- | --------------------------- | --------------------------- |
| `id`             | INT                       | PRIMARY KEY AUTO_INCREMENT  | ID đánh giá              |
| `store_id`       | VARCHAR(50)               | NOT NULL, FK                | ID cửa hàng               |
| `user_id`        | VARCHAR(50)               | NOT NULL, FK                | ID người đánh giá      |
| `order_id`       | VARCHAR(50)               | NULL, FK                    | ID đơn hàng liên quan   |
| `rating`         | INT                       | CHECK (1-5)                 | Điểm đánh giá          |
| `title`          | VARCHAR(255)              | NULL                        | Tiêu đề đánh giá      |
| `comment`        | TEXT                      | NULL                        | Nội dung đánh giá       |
| `images`         | JSON                      | NULL                        | Ảnh đính kèm            |
| `helpful_count`  | INT                       | DEFAULT 0                   | Số lượt hữu ích        |
| `is_verified`    | BOOLEAN                   | DEFAULT FALSE               | Đánh giá đã xác thực |
| `created_at`     | DATETIME                  | DEFAULT CURRENT_TIMESTAMP   | Ngày tạo                  |
| `updated_at`     | DATETIME                  | ON UPDATE CURRENT_TIMESTAMP | Ngày cập nhật            |

## **4. BẢNG NGƯỜI THEO DÕI - STORE_FOLLOWERS**

| **Trường** | **Kiểu dữ liệu** | **Ràng buộc**     | **Mô tả**    |
| ------------------ | ------------------------- | ------------------------- | -------------------- |
| `store_id`       | VARCHAR(50)               | PRIMARY KEY               | ID cửa hàng        |
| `user_id`        | VARCHAR(50)               | PRIMARY KEY               | ID người theo dõi |
| `followed_at`    | DATETIME                  | DEFAULT CURRENT_TIMESTAMP | Thời gian theo dõi |
| `is_active`      | BOOLEAN                   | DEFAULT TRUE              | Còn theo dõi       |

## **5. BẢNG THỐNG KÊ CỬA HÀNG - STORE_ANALYTICS**

| **Trường** | **Kiểu dữ liệu** | **Ràng buộc**      | **Mô tả**      |
| ------------------ | ------------------------- | -------------------------- | ---------------------- |
| `id`             | INT                       | PRIMARY KEY AUTO_INCREMENT | ID thống kê          |
| `store_id`       | VARCHAR(50)               | NOT NULL, FK               | ID cửa hàng          |
| `date`           | DATE                      | NOT NULL                   | Ngày thống kê       |
| `views`          | INT                       | DEFAULT 0                  | Lượt xem             |
| `visitors`       | INT                       | DEFAULT 0                  | Khách truy cập       |
| `orders`         | INT                       | DEFAULT 0                  | Đơn hàng            |
| `revenue`        | DECIMAL(15,2)             | DEFAULT 0                  | Doanh thu              |
| `new_followers`  | INT                       | DEFAULT 0                  | Người theo dõi mới |
| `products_added` | INT                       | DEFAULT 0                  | Sản phẩm thêm mới  |

## **6. BẢNG CÀI ĐẶT CỬA HÀNG - STORE_SETTINGS**

| **Trường**      | **Kiểu dữ liệu** | **Ràng buộc** | **Mô tả**           |
| ----------------------- | ------------------------- | --------------------- | --------------------------- |
| `store_id`            | VARCHAR(50)               | PRIMARY KEY, FK       | ID cửa hàng               |
| `auto_confirm_orders` | BOOLEAN                   | DEFAULT FALSE         | Tự động xác nhận đơn |
| `notification_email`  | BOOLEAN                   | DEFAULT TRUE          | Thông báo email           |
| `notification_sms`    | BOOLEAN                   | DEFAULT FALSE         | Thông báo SMS             |
| `working_hours_start` | TIME                      | NULL                  | Giờ làm việc bắt đầu  |
| `working_hours_end`   | TIME                      | NULL                  | Giờ làm việc kết thúc  |
| `working_days`        | JSON                      | NULL                  | Ngày làm việc            |
| `vacation_mode`       | BOOLEAN                   | DEFAULT FALSE         | Chế độ nghỉ phép       |
| `vacation_message`    | TEXT                      | NULL                  | Thông báo nghỉ phép     |
| `auto_reply_message`  | TEXT                      | NULL                  | Tin nhắn tự động        |

## **7. BẢNG HÌNH ẢNH CỬA HÀNG - STORE_IMAGES**

| **Trường** | **Kiểu dữ liệu** | **Ràng buộc**      | **Mô tả**         |
| ------------------ | ------------------------- | -------------------------- | ------------------------- |
| `id`             | INT                       | PRIMARY KEY AUTO_INCREMENT | ID hình ảnh             |
| `store_id`       | VARCHAR(50)               | NOT NULL, FK               | ID cửa hàng             |
| `image_url`      | VARCHAR(500)              | NOT NULL                   | URL hình ảnh            |
| `image_type`     | ENUM                      | NOT NULL                   | cover/gallery/logo/banner |
| `title`          | VARCHAR(255)              | NULL                       | Tiêu đề hình ảnh     |
| `alt_text`       | VARCHAR(255)              | NULL                       | Mô tả hình ảnh        |
| `sort_order`     | INT                       | DEFAULT 0                  | Thứ tự sắp xếp        |
| `is_active`      | BOOLEAN                   | DEFAULT TRUE               | Đang sử dụng           |
| `created_at`     | DATETIME                  | DEFAULT CURRENT_TIMESTAMP  | Ngày tạo                |

## **8. BẢNG NGƯỜI DÙNG CỬA HÀNG - STORE_USERS**

| **Trường**      | **Kiểu dữ liệu**                  | **Ràng buộc**       | **Mô tả**                  |
| ----------------------- | ------------------------------------------ | --------------------------- | ---------------------------------- |
| `id`                  | INT                                        | PRIMARY KEY AUTO_INCREMENT  | ID bản ghi                        |
| `store_id`            | VARCHAR(50)                                | NOT NULL, FK                | ID cửa hàng                      |
| `user_id`             | VARCHAR(50)                                | NOT NULL, FK                | ID người dùng (từ bảng users) |
| `role`                | ENUM('owner','admin','manager','employee') | NOT NULL                    | Vai trò trong cửa hàng          |
| `status`              | ENUM('active','inactive','pending')        | DEFAULT 'pending'           | Trạng thái thành viên          |
| `granted_permissions` | JSON                                       | NULL                        | Quyền bổ sung được cấp       |
| `revoked_permissions` | JSON                                       | NULL                        | Quyền bị thu hồi                |
| `invited_by`          | VARCHAR(50)                                | NULL, FK                    | Người mời (user_id)             |
| `invited_at`          | DATETIME                                   | NULL                        | Thời gian được mời            |
| `joined_at`           | DATETIME                                   | NULL                        | Thời gian tham gia                |
| `last_login`          | DATETIME                                   | NULL                        | Lần đăng nhập cuối            |
| `notes`               | TEXT                                       | NULL                        | Ghi chú về thành viên          |
| `created_at`          | DATETIME                                   | DEFAULT CURRENT_TIMESTAMP   | Ngày tạo                         |
| `updated_at`          | DATETIME                                   | ON UPDATE CURRENT_TIMESTAMP | Ngày cập nhật                   |

## **9. BẢNG VAI TRÒ CỬA HÀNG - STORE_ROLES**

| **Trường**      | **Kiểu dữ liệu** | **Ràng buộc**      | **Mô tả**               |
| ----------------------- | ------------------------- | -------------------------- | ------------------------------- |
| `id`                  | INT                       | PRIMARY KEY AUTO_INCREMENT | ID vai trò                     |
| `role_name`           | VARCHAR(50)               | NOT NULL UNIQUE            | Tên vai trò (owner, admin...) |
| `role_display_name`   | VARCHAR(100)              | NULL                       | Tên hiển thị                 |
| `description`         | TEXT                      | NULL                       | Mô tả vai trò                |
| `default_permissions` | JSON                      | NULL                       | Quyền mặc định              |
| `is_system_role`      | BOOLEAN                   | DEFAULT TRUE               | Vai trò hệ thống             |
| `created_at`          | DATETIME                  | DEFAULT CURRENT_TIMESTAMP  | Ngày tạo                      |

## **10. BẢNG QUYỀN HẠN - STORE_PERMISSIONS**

| **Trường**   | **Kiểu dữ liệu** | **Ràng buộc**      | **Mô tả**                  |
| -------------------- | ------------------------- | -------------------------- | ---------------------------------- |
| `id`               | INT                       | PRIMARY KEY AUTO_INCREMENT | ID quyền                          |
| `permission_name`  | VARCHAR(100)              | NOT NULL UNIQUE            | Tên quyền (products.create)      |
| `permission_group` | VARCHAR(50)               | NULL                       | Nhóm quyền (products, orders...) |
| `display_name`     | VARCHAR(100)              | NULL                       | Tên hiển thị                    |
| `description`      | TEXT                      | NULL                       | Mô tả quyền                     |
| `is_active`        | BOOLEAN                   | DEFAULT TRUE               | Còn sử dụng                     |
| `created_at`       | DATETIME                  | DEFAULT CURRENT_TIMESTAMP  | Ngày tạo                         |

## **11. BẢNG LỜI MỜI THAM GIA - STORE_INVITATIONS**

| **Trường**   | **Kiểu dữ liệu**                      | **Ràng buộc**      | **Mô tả**      |
| -------------------- | ---------------------------------------------- | -------------------------- | ---------------------- |
| `id`               | INT                                            | PRIMARY KEY AUTO_INCREMENT | ID lời mời           |
| `store_id`         | VARCHAR(50)                                    | NOT NULL, FK               | ID cửa hàng          |
| `email`            | VARCHAR(255)                                   | NOT NULL                   | Email được mời     |
| `role`             | VARCHAR(50)                                    | NOT NULL                   | Vai trò được mời  |
| `invitation_token` | VARCHAR(255)                                   | UNIQUE                     | Token xác thực       |
| `invited_by`       | VARCHAR(50)                                    | NOT NULL, FK               | Người gửi lời mời |
| `invited_at`       | DATETIME                                       | DEFAULT CURRENT_TIMESTAMP  | Thời gian gửi        |
| `expires_at`       | DATETIME                                       | NOT NULL                   | Thời gian hết hạn   |
| `accepted_at`      | DATETIME                                       | NULL                       | Thời gian chấp nhận |
| `status`           | ENUM('pending','accepted','expired','revoked') | DEFAULT 'pending'          | Trạng thái           |
| `message`          | TEXT                                           | NULL                       | Tin nhắn mời         |
| `created_at`       | DATETIME                                       | DEFAULT CURRENT_TIMESTAMP  | Ngày tạo             |

---

## **🔗 QUAN HỆ GIỮA CÁC BẢNG:**

```
USERS (1) ←→ (N) STORE_USERS ←→ (1) STORES
STORES (1) ←→ (N) STORE_CATEGORIES
STORES (1) ←→ (N) STORE_REVIEWS  
STORES (1) ←→ (N) STORE_FOLLOWERS
STORES (1) ←→ (N) STORE_ANALYTICS
STORES (1) ←→ (1) STORE_SETTINGS
STORES (1) ←→ (N) STORE_IMAGES
STORES (1) ←→ (N) STORE_INVITATIONS
STORE_ROLES (1) ←→ (N) STORE_USERS
```## **📈 TỔNG KẾT:**

- **11 bảng** chính cho hệ thống Store với phân quyền
- **Stores**: 32 trường (bảng chính)
- **Store_Users**: 13 trường (map user-store với roles)
- **Multi-user support**: Owner, Admin, Manager, Employee
- **Tổng cộng**: ~80 trường trên tất cả các bảng
- **Đầy đủ** cho StorePage, SettingsPage, Team Management và Analytics

---

## **💾 SQL TẠO BẢNG:**

### **1. Tạo bảng STORES:**

```sql
CREATE TABLE stores (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE,
    description TEXT,
    email VARCHAR(255),
    phone VARCHAR(20),
    address TEXT,
    location VARCHAR(255),
    avatar VARCHAR(500),
    cover_image VARCHAR(500),
    logo VARCHAR(500),
    rating DECIMAL(2,1) DEFAULT 0.0,
    total_reviews INT DEFAULT 0,
    followers_count INT DEFAULT 0,
    products_count INT DEFAULT 0,
    total_sales INT DEFAULT 0,
    total_revenue DECIMAL(15,2) DEFAULT 0,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    status ENUM('active', 'inactive', 'suspended') DEFAULT 'active',
    response_time VARCHAR(20),
    response_rate DECIMAL(3,1) DEFAULT 0,
    cod_enabled BOOLEAN DEFAULT TRUE,
    express_shipping BOOLEAN DEFAULT TRUE,
    standard_shipping BOOLEAN DEFAULT TRUE,
    free_shipping_min DECIMAL(12,2),
    return_policy TEXT,
    shipping_policy TEXT,
    warranty_policy TEXT,
    currency VARCHAR(5) DEFAULT 'VND',
    timezone VARCHAR(50) DEFAULT 'Asia/Ho_Chi_Minh',
    join_date DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_stores_name (name),
    INDEX idx_stores_rating (rating),
    INDEX idx_stores_status (is_active, status),
    INDEX idx_stores_location (location)
);
```

### **2. Tạo bảng STORE_CATEGORIES:**

```sql
CREATE TABLE store_categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    store_id VARCHAR(50) NOT NULL,
    category_id INT NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE,
    UNIQUE KEY unique_store_category (store_id, category_id)
);
```

### **3. Tạo bảng STORE_REVIEWS:**

```sql
CREATE TABLE store_reviews (
    id INT PRIMARY KEY AUTO_INCREMENT,
    store_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    order_id VARCHAR(50),
    rating INT CHECK (rating BETWEEN 1 AND 5),
    title VARCHAR(255),
    comment TEXT,
    images JSON,
    helpful_count INT DEFAULT 0,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE,
    INDEX idx_reviews_store (store_id),
    INDEX idx_reviews_rating (rating),
    INDEX idx_reviews_date (created_at)
);
```

### **4. Tạo bảng STORE_FOLLOWERS:**

```sql
CREATE TABLE store_followers (
    store_id VARCHAR(50),
    user_id VARCHAR(50),
    followed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,

    PRIMARY KEY (store_id, user_id),
    FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE
);
```

### **5. Tạo bảng STORE_ANALYTICS:**

```sql
CREATE TABLE store_analytics (
    id INT PRIMARY KEY AUTO_INCREMENT,
    store_id VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    views INT DEFAULT 0,
    visitors INT DEFAULT 0,
    orders INT DEFAULT 0,
    revenue DECIMAL(15,2) DEFAULT 0,
    new_followers INT DEFAULT 0,
    products_added INT DEFAULT 0,

    FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE,
    UNIQUE KEY unique_store_date (store_id, date)
);
```

### **6. Tạo bảng STORE_SETTINGS:**

```sql
CREATE TABLE store_settings (
    store_id VARCHAR(50) PRIMARY KEY,
    auto_confirm_orders BOOLEAN DEFAULT FALSE,
    notification_email BOOLEAN DEFAULT TRUE,
    notification_sms BOOLEAN DEFAULT FALSE,
    working_hours_start TIME,
    working_hours_end TIME,
    working_days JSON,
    vacation_mode BOOLEAN DEFAULT FALSE,
    vacation_message TEXT,
    auto_reply_message TEXT,

    FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE
);
```

### **7. Tạo bảng STORE_IMAGES:**

```sql
CREATE TABLE store_images (
    id INT PRIMARY KEY AUTO_INCREMENT,
    store_id VARCHAR(50) NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    image_type ENUM('cover', 'gallery', 'logo', 'banner') NOT NULL,
    title VARCHAR(255),
    alt_text VARCHAR(255),
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE,
    INDEX idx_images_store_type (store_id, image_type)
);
```

### **8. Tạo bảng STORE_USERS:**

```sql
CREATE TABLE store_users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    store_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    role ENUM('owner', 'admin', 'manager', 'employee') NOT NULL,
    status ENUM('active', 'inactive', 'pending') DEFAULT 'pending',
    granted_permissions JSON,
    revoked_permissions JSON,
    invited_by VARCHAR(50),
    invited_at DATETIME,
    joined_at DATETIME,
    last_login DATETIME,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
    FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (invited_by) REFERENCES users(id) ON DELETE SET NULL,
    UNIQUE KEY unique_store_user (store_id, user_id),
    INDEX idx_store_users_role (store_id, role),
    INDEX idx_store_users_status (status)
);
```

### **9. Tạo bảng STORE_ROLES:**

```sql
CREATE TABLE store_roles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    role_display_name VARCHAR(100),
    description TEXT,
    default_permissions JSON,
    is_system_role BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert default roles
INSERT INTO store_roles (role_name, role_display_name, description, default_permissions, is_system_role) VALUES
('owner', 'Chủ cửa hàng', 'Quyền cao nhất, quản lý toàn bộ cửa hàng', 
 '["store.*", "users.*", "products.*", "orders.*", "analytics.*", "billing.*"]', TRUE),
('admin', 'Quản trị viên', 'Quản lý sản phẩm, đơn hàng và team', 
 '["users.invite", "products.*", "orders.*", "analytics.view"]', TRUE),
('manager', 'Quản lý', 'Quản lý sản phẩm và đơn hàng', 
 '["products.create", "products.edit", "orders.manage", "analytics.basic"]', TRUE),
('employee', 'Nhân viên', 'Xử lý đơn hàng và hỗ trợ khách hàng', 
 '["products.view", "orders.view", "orders.update_status"]', TRUE);
```

### **10. Tạo bảng STORE_PERMISSIONS:**

```sql
CREATE TABLE store_permissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    permission_name VARCHAR(100) NOT NULL UNIQUE,
    permission_group VARCHAR(50),
    display_name VARCHAR(100),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert default permissions
INSERT INTO store_permissions (permission_name, permission_group, display_name, description) VALUES
-- Store management
('store.settings', 'store', 'Cài đặt cửa hàng', 'Quản lý thông tin và cài đặt cửa hàng'),
('store.delete', 'store', 'Xóa cửa hàng', 'Xóa hoàn toàn cửa hàng'),

-- User management
('users.invite', 'users', 'Mời thành viên', 'Mời người dùng tham gia team'),
('users.remove', 'users', 'Xóa thành viên', 'Xóa thành viên khỏi team'),
('users.manage', 'users', 'Quản lý thành viên', 'Thay đổi role và quyền của thành viên'),

-- Products
('products.view', 'products', 'Xem sản phẩm', 'Xem danh sách sản phẩm'),
('products.create', 'products', 'Tạo sản phẩm', 'Thêm sản phẩm mới'),
('products.edit', 'products', 'Sửa sản phẩm', 'Chỉnh sửa thông tin sản phẩm'),
('products.delete', 'products', 'Xóa sản phẩm', 'Xóa sản phẩm'),

-- Orders
('orders.view', 'orders', 'Xem đơn hàng', 'Xem danh sách đơn hàng'),
('orders.manage', 'orders', 'Quản lý đơn hàng', 'Cập nhật trạng thái đơn hàng'),
('orders.update_status', 'orders', 'Cập nhật trạng thái', 'Thay đổi trạng thái đơn hàng'),
('orders.refund', 'orders', 'Hoàn tiền', 'Xử lý hoàn tiền cho đơn hàng'),

-- Analytics
('analytics.view', 'analytics', 'Xem thống kê', 'Xem báo cáo và thống kê'),
('analytics.basic', 'analytics', 'Thống kê cơ bản', 'Xem thống kê cơ bản'),
('analytics.export', 'analytics', 'Xuất dữ liệu', 'Xuất báo cáo dưới dạng file'),

-- Billing
('billing.view', 'billing', 'Xem hóa đơn', 'Xem thông tin thanh toán'),
('billing.manage', 'billing', 'Quản lý hóa đơn', 'Quản lý thanh toán và hóa đơn');
```

### **11. Tạo bảng STORE_INVITATIONS:**

```sql
CREATE TABLE store_invitations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    store_id VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    invitation_token VARCHAR(255) UNIQUE,
    invited_by VARCHAR(50) NOT NULL,
    invited_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    accepted_at DATETIME,
    status ENUM('pending', 'accepted', 'expired', 'revoked') DEFAULT 'pending',
    message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  
    FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE,
    FOREIGN KEY (invited_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_invitations_token (invitation_token),
    INDEX idx_invitations_email (email),
    INDEX idx_invitations_status (status)
);
```

---

## **⚡ TRIGGERS & PROCEDURES:**

### **1. Trigger cập nhật số followers:**

```sql
DELIMITER //
CREATE TRIGGER update_followers_count
AFTER INSERT ON store_followers
FOR EACH ROW
BEGIN
    UPDATE stores
    SET followers_count = (
        SELECT COUNT(*)
        FROM store_followers
        WHERE store_id = NEW.store_id AND is_active = TRUE
    )
    WHERE id = NEW.store_id;
END//

CREATE TRIGGER update_followers_count_delete
AFTER UPDATE ON store_followers
FOR EACH ROW
BEGIN
    IF NEW.is_active != OLD.is_active THEN
        UPDATE stores
        SET followers_count = (
            SELECT COUNT(*)
            FROM store_followers
            WHERE store_id = NEW.store_id AND is_active = TRUE
        )
        WHERE id = NEW.store_id;
    END IF;
END//
DELIMITER ;
```

### **2. Trigger cập nhật rating:**

```sql
DELIMITER //
CREATE TRIGGER update_store_rating
AFTER INSERT ON store_reviews
FOR EACH ROW
BEGIN
    UPDATE stores
    SET
        rating = (
            SELECT AVG(rating)
            FROM store_reviews
            WHERE store_id = NEW.store_id
        ),
        total_reviews = (
            SELECT COUNT(*)
            FROM store_reviews
            WHERE store_id = NEW.store_id
        )
    WHERE id = NEW.store_id;
END//
DELIMITER ;
```

### **3. Trigger quản lý Store Users:**

```sql
DELIMITER //
-- Trigger đảm bảo chỉ có 1 owner per store
CREATE TRIGGER check_store_owner_limit
BEFORE INSERT ON store_users
FOR EACH ROW
BEGIN
    DECLARE owner_count INT DEFAULT 0;
  
    IF NEW.role = 'owner' THEN
        SELECT COUNT(*) INTO owner_count 
        FROM store_users 
        WHERE store_id = NEW.store_id AND role = 'owner' AND status = 'active';
    
        IF owner_count >= 1 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Một cửa hàng chỉ có thể có 1 owner';
        END IF;
    END IF;
END//

-- Trigger tự động set joined_at khi status = active
CREATE TRIGGER set_joined_date
BEFORE UPDATE ON store_users
FOR EACH ROW
BEGIN
    IF OLD.status != 'active' AND NEW.status = 'active' AND OLD.joined_at IS NULL THEN
        SET NEW.joined_at = NOW();
    END IF;
END//
DELIMITER ;
```
