# SHOEX - E-commerce Platform

## 🏗️ Cấu Trúc Dự Án Mới

Dự án đã được tái cấu trúc hoàn toàn với hệ thống multi-page và tổ chức code theo từng module riêng biệt.

### 📁 Cấu Trúc Thư Mục

```
FE/
├── components/
│   ├── layout/                 # Layout components
│   │   ├── CustomerLayout.tsx  # Layout cho khách hàng
│   │   ├── AdminLayout.tsx     # Layout cho admin/seller
│   │   └── AuthLayout.tsx      # Layout cho trang đăng nhập
│   │
│   ├── pages/                  # Page components
│   │   ├── auth/               # Trang xác thực
│   │   │   ├── LoginPage.tsx
│   │   │   └── RegisterPage.tsx
│   │   │
│   │   ├── customer/           # Trang dành cho khách hàng
│   │   │   ├── HomePage.tsx
│   │   │   └── ProductsPage.tsx
│   │   │
│   │   ├── seller/             # Trang dành cho seller (dashboard)
│   │   │   ├── Sidebar.tsx
│   │   │   ├── ProductsPage.tsx
│   │   │   ├── OrdersPage.tsx
│   │   │   ├── SettingsPage.tsx
│   │   │   └── ...
│   │   │
│   │   └── admin/              # Trang dành cho admin (future)
│   │
│   ├── ui/                     # UI Components
│   │   ├── Modal.tsx
│   │   ├── TextField.tsx
│   │   └── ...
│   │
│   ├── charts/                 # Chart Components
│   └── shared/                 # Shared Components
│
├── AppRouter.tsx              # Main router với demo navigation
├── MainApp.tsx                # Main application logic
├── SellerDashboard.tsx        # Seller dashboard (legacy)
└── types/                     # TypeScript types
```

## 🎯 Các Trang Chính

### 1. **Customer Pages** (Khách Hàng)

- **HomePage**: Trang chủ bán hàng với featured products, categories, services
- **ProductsPage**: Trang sản phẩm với filters, search, grid/list view

### 2. **Auth Pages** (Xác Thực)

- **LoginPage**: Đăng nhập với validation và UI đẹp
- **RegisterPage**: Đăng ký tài khoản với form validation

### 3. **Seller Dashboard** (Bán Hàng)

- **Dashboard**: Tổng quan doanh thu, charts, quick actions
- **ProductsPage**: Quản lý sản phẩm với multi-step form
- **OrdersPage**: Quản lý đơn hàng
- **SettingsPage**: Cài đặt cửa hàng

## 🚀 Cách Chạy Dự Án

```bash
# Cài đặt dependencies
npm install

# Chạy development server
npm run dev

# Build production
npm run build

# Start production
npm start
```

## 🔧 Tính Năng Chính

### ✅ Đã Hoàn Thành:

- **Multi-layout System**: CustomerLayout, AdminLayout, AuthLayout
- **Customer E-commerce**: Homepage với products, categories, search
- **Auth System**: Login/Register với validation
- **Seller Dashboard**: Products management, charts, metrics
- **Voice Input**: AskAI với Speech-to-Text tiếng Việt
- **Responsive Design**: Mobile-first approach

### 🔄 Đang Phát Triển:

- **Shopping Cart**: Giỏ hàng và checkout
- **Product Details**: Trang chi tiết sản phẩm
- **Order Tracking**: Theo dõi đơn hàng
- **Payment Integration**: Tích hợp thanh toán

## 🎨 UI/UX Features

### **Customer Experience:**

- **Hero Banner**: Gradient background với call-to-action
- **Product Grid**: Card layout với heart wishlist, rating stars
- **Category Navigation**: Icon-based categories
- **Service Features**: Shipping, warranty, support badges
- **Newsletter Signup**: Email subscription form

### **Seller Experience:**

- **Metrics Dashboard**: Revenue, orders, products, customers
- **Charts Integration**: Sales trends, order status distribution
- **Multi-step Product Form**: 5 steps với image upload
- **Quick Actions**: Fast navigation buttons
- **AskAI Assistant**: Context-aware AI help với voice input

### **Authentication:**

- **Modern Auth UI**: Gradient backgrounds, glass morphism
- **Form Validation**: Real-time validation với error states
- **Password Visibility**: Toggle password visibility
- **Remember Me**: Persistent login option

## 🛠️ Technical Stack

- **Framework**: Next.js 15 + React 19
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Charts**: Recharts
- **Animation**: Framer Motion
- **Speech Recognition**: Web Speech API

## 📱 Demo Navigation

Trong development, có navigation bar ở trên cùng để dễ dàng test các trang:

- **Trang chủ**: Customer homepage
- **Sản phẩm**: Customer products listing
- **Đăng nhập**: Auth login page
- **Đăng ký**: Auth register page
- **Seller**: Seller dashboard

## 🎯 Next Steps

1. **Implement Shopping Cart**
2. **Add Product Details Page**
3. **Integrate Backend API**
4. **Add Payment System**
5. **Implement Real Authentication**
6. **Add Admin Panel**
7. **Add More Customer Pages** (Profile, Wishlist, Order History)

## 👥 Team Structure

- **Frontend**: React/Next.js components
- **Backend**: Django REST API (existing)
- **Database**: PostgreSQL/SQLite
- **Deployment**: Vercel/Netlify (Frontend) + Railway/Heroku (Backend)

---

**Lưu ý**: Dự án hiện đang ở giai đoạn development với mock data. Cần tích hợp với backend API để có dữ liệu thực.
