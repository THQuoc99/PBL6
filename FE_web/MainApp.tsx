import React, { useState, useEffect } from 'react';
import {
  LoginPage,
  RegisterPage,
  ForgotPasswordPage,
  SellerLoginPage,
  SellerRegisterPage,
  SellerRegistrationPage,
  CustomerHomePage,
  CustomerProductsPage,
  CustomerProductDetailPage,
  CustomerStorePage,
  CustomerPaymentPage,
  CustomerPromotionsPage,
  CustomerContactPage,
  CustomerCartPage,
  CustomerWishlistPage,
  CustomerAccountPage,
  AdminLayout,
  SellerProductsPage,
  OrdersPage,
  SettingsPage,
  ListingsPage,
  PromotionsPage,
  ChatbotAIPage,
  PaymentsPage,
  MetricCard,
  SalesChart,
  OrderChart
} from './components';
import { MenuItems, Product, Order, StoreSettings } from './types';
import { 
  TrendingUp, 
  Package, 
  ShoppingCart, 
  DollarSign,
  Users,
  Eye,
  Calendar,
  BarChart3
} from 'lucide-react';

type AppPage = 'login' | 'register' | 'forgot-password' | 'customer-home' | 'customer-products' | 'customer-product-detail' | 'customer-store' | 'customer-payment' | 'customer-promotions' | 'customer-contact' | 'customer-cart' | 'customer-wishlist' | 'customer-account' | 'seller-login' | 'seller-register' | 'seller-dashboard';

interface MainAppProps {
  initialPage?: AppPage;
}

export default function MainApp({ initialPage = 'customer-home' }: MainAppProps) {
  const [currentAppPage, setCurrentAppPage] = useState<AppPage>(initialPage);
  const [currentSellerPage, setCurrentSellerPage] = useState<MenuItems>('dashboard');
  
  // Update currentAppPage when initialPage changes
  useEffect(() => {
    setCurrentAppPage(initialPage);
  }, [initialPage]);
  
  // Mock data
  const [products, setProducts] = useState<Product[]>([
    {
      id: '1',
      name: 'Nike Air Max 270',
      sku: 'NIKE-AM270-001',
      category: 'Giày thể thao',
      stock: 45,
      price: 2500000,
      images: [],
      createdAt: new Date().toISOString(),
      active: true
    }
  ]);

  const [orders, setOrders] = useState<Order[]>([
    {
      id: '1',
      customer: 'Nguyễn Văn A',
      status: 'Processing',
      date: new Date().toISOString(),
      amount: 2500000,
      items: [{ productId: '1', qty: 1, price: 2500000 }]
    }
  ]);

  const [settings, setSettings] = useState<StoreSettings>({
    storeName: 'SHOEX Store',
    email: 'info@shoex.com',
    phone: '0123456789',
    address: '123 Đường ABC, TP.HCM',
    currency: 'VND',
    shipping: {
      cod: true,
      express: true,
      standard: true
    }
  });

  // Mock chart data
  const salesData = [
    { name: 'T2', value: 4000000 },
    { name: 'T3', value: 3000000 },
    { name: 'T4', value: 5000000 },
    { name: 'T5', value: 4500000 },
    { name: 'T6', value: 6000000 },
    { name: 'T7', value: 7000000 },
    { name: 'CN', value: 5500000 }
  ];

  const orderData = [
    { name: 'Đang xử lý', value: 12, color: '#3B82F6' },
    { name: 'Đã giao', value: 19, color: '#10B981' },
    { name: 'Đã hủy', value: 3, color: '#EF4444' },
    { name: 'Đang giao', value: 8, color: '#F59E0B' }
  ];

  const storeData = {
    name: settings.storeName,
    totalProducts: products.length,
    totalOrders: orders.length,
    totalRevenue: orders.reduce((sum, order) => sum + order.amount, 0),
    totalCustomers: 892
  };

  // Event handlers
  const handleLogin = (email: string, password: string) => {
    console.log('Login:', { email, password });
    setCurrentAppPage('seller-dashboard');
  };

  const handleRegister = (data: any) => {
    console.log('Register:', data);
    setCurrentAppPage('seller-dashboard');
  };

  const handleSellerLogin = async (username: string, password: string) => {
    console.log('Seller Login:', { username, password });
    // Simulate async authentication (replace with real API call)
    await new Promise((r) => setTimeout(r, 600));

    if (username === 'seller' && password === 'seller') {
      setCurrentAppPage('seller-dashboard');
      return;
    }

    // On failure, throw so the caller (SellerLoginPage) can show an error
    throw new Error('Tên đăng nhập hoặc mật khẩu không đúng');
  };

  const handleSellerRegister = (data: any) => {
    console.log('Seller Register:', data);
    // Registration logic would go here
    alert('Đăng ký thành công! Vui lòng đăng nhập.');
    setCurrentAppPage('seller-login');
  };

  const handleSellerMenuChange = (menu: MenuItems) => {
    setCurrentSellerPage(menu);
  };

  const handleCustomerNavigate = (page: string) => {
    switch (page) {
      case 'home':
        setCurrentAppPage('customer-home');
        break;
      case 'products':
        setCurrentAppPage('customer-products');
        break;
      case 'product-detail':
        setCurrentAppPage('customer-product-detail');
        break;
      case 'store':
        setCurrentAppPage('customer-store');
        break;
      case 'payment':
        setCurrentAppPage('customer-payment');
        break;
      case 'promotions':
        setCurrentAppPage('customer-promotions');
        break;
      case 'contact':
        setCurrentAppPage('customer-contact');
        break;
      case 'cart':
        setCurrentAppPage('customer-cart');
        break;
      case 'wishlist':
        setCurrentAppPage('customer-wishlist');
        break;
      case 'account':
        setCurrentAppPage('customer-account');
        break;
      case 'login':
        setCurrentAppPage('login');
        break;
      case 'seller-login':
        setCurrentAppPage('seller-login');
        break;
      default:
        setCurrentAppPage('customer-home');
        break;
    }
  };

  // Render seller dashboard content
  const renderSellerDashboardContent = () => {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600 mt-2">Tổng quan về cửa hàng của bạn</p>
          </div>
          <div className="flex items-center space-x-3 text-sm text-gray-600">
            <Calendar className="h-4 w-4" />
            <span>7 ngày qua</span>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            title="Doanh thu"
            value={`${(storeData.totalRevenue / 1000000).toFixed(1)}M₫`}
            sub="+12.5% so với tuần trước"
            icon={<DollarSign className="h-6 w-6 text-green-600" />}
          />
          <MetricCard
            title="Đơn hàng"
            value={storeData.totalOrders.toString()}
            sub="+8.2% so với tuần trước"
            icon={<ShoppingCart className="h-6 w-6 text-blue-600" />}
          />
          <MetricCard
            title="Sản phẩm"
            value={storeData.totalProducts.toString()}
            sub="5 sản phẩm mới"
            icon={<Package className="h-6 w-6 text-purple-600" />}
          />
          <MetricCard
            title="Khách hàng"
            value={storeData.totalCustomers.toString()}
            sub="+15.3% so với tuần trước"
            icon={<Users className="h-6 w-6 text-orange-600" />}
          />
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900">Doanh thu 7 ngày</h3>
              <TrendingUp className="h-5 w-5 text-green-600" />
            </div>
            <SalesChart data={salesData} />
          </div>
          
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900">Đơn hàng theo trạng thái</h3>
              <BarChart3 className="h-5 w-5 text-blue-600" />
            </div>
            <OrderChart data={orderData} />
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Hành động nhanh</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button 
              onClick={() => setCurrentSellerPage('products')}
              className="p-4 bg-blue-50 rounded-xl hover:bg-blue-100 transition-colors text-left"
            >
              <Package className="h-6 w-6 text-blue-600 mb-2" />
              <div className="font-medium text-gray-900">Thêm sản phẩm</div>
              <div className="text-sm text-gray-600">Tạo sản phẩm mới</div>
            </button>
            
            <button 
              onClick={() => setCurrentSellerPage('orders')}
              className="p-4 bg-green-50 rounded-xl hover:bg-green-100 transition-colors text-left"
            >
              <ShoppingCart className="h-6 w-6 text-green-600 mb-2" />
              <div className="font-medium text-gray-900">Xem đơn hàng</div>
              <div className="text-sm text-gray-600">Quản lý đơn hàng</div>
            </button>
            
            <button 
              onClick={() => setCurrentSellerPage('settings')}
              className="p-4 bg-purple-50 rounded-xl hover:bg-purple-100 transition-colors text-left"
            >
              <Eye className="h-6 w-6 text-purple-600 mb-2" />
              <div className="font-medium text-gray-900">Xem cửa hàng</div>
              <div className="text-sm text-gray-600">Cài đặt giao diện</div>
            </button>
          </div>
        </div>
      </div>
    );
  };

  const renderSellerPageContent = () => {
    switch (currentSellerPage) {
      case 'dashboard':
        return renderSellerDashboardContent();
      case 'products':
        return <SellerProductsPage products={products} setProducts={setProducts} />;
      case 'orders':
        return <OrdersPage orders={orders} setOrders={setOrders} query="" />;
      case 'listings':
        return <ListingsPage />;
      case 'promotions':
        return <PromotionsPage />;
      case 'chatbot':
        return <ChatbotAIPage />;
      case 'payments':
        return <PaymentsPage />;
      case 'settings':
        return <SettingsPage settings={settings} setSettings={setSettings} />;
      default:
        return renderSellerDashboardContent();
    }
  };

  // Main app routing
  switch (currentAppPage) {
    case 'login':
      return (
        <LoginPage 
          onLogin={handleLogin}
          onNavigateToRegister={() => setCurrentAppPage('register')}
          onNavigateToForgot={() => setCurrentAppPage('forgot-password')}
        />
      );

    case 'register':
      return (
        <RegisterPage 
          onRegister={handleRegister}
          onNavigateToLogin={() => setCurrentAppPage('login')}
        />
      );

    case 'forgot-password':
      return (
        <ForgotPasswordPage 
          onNavigateToLogin={() => setCurrentAppPage('login')}
          onSendResetEmail={(email) => {
            console.log('Sending reset email to:', email);
            // TODO: Implement actual email sending logic
          }}
        />
      );

    case 'customer-home':
      return <CustomerHomePage onNavigate={handleCustomerNavigate} />;

    case 'customer-products':
      return <CustomerProductsPage onNavigate={handleCustomerNavigate} />;

    case 'customer-product-detail':
      return <CustomerProductDetailPage onNavigate={handleCustomerNavigate} />;

    case 'customer-store':
      return <CustomerStorePage onNavigate={handleCustomerNavigate} />;

    case 'customer-payment':
      return <CustomerPaymentPage onNavigate={handleCustomerNavigate} />;

    case 'customer-promotions':
      return <CustomerPromotionsPage onNavigate={handleCustomerNavigate} />;

    case 'customer-contact':
      return <CustomerContactPage onNavigate={handleCustomerNavigate} />;

    case 'customer-cart':
      return <CustomerCartPage onNavigate={handleCustomerNavigate} />;

    case 'customer-wishlist':
      return <CustomerWishlistPage onNavigate={handleCustomerNavigate} />;

    case 'customer-account':
      return <CustomerAccountPage onNavigate={handleCustomerNavigate} />;

    case 'seller-login':
      return (
        <SellerLoginPage 
          onLogin={handleSellerLogin}
          onNavigateToRegister={() => setCurrentAppPage('seller-register')}
          onBackToCustomer={() => setCurrentAppPage('customer-home')}
        />
      );

    case 'seller-register':
      return (
        <SellerRegistrationPage 
          onComplete={() => setCurrentAppPage('seller-login')}
          onBackToCustomer={() => setCurrentAppPage('customer-home')}
        />
      );

    case 'seller-dashboard':
      return (
        <AdminLayout 
          currentPage={currentSellerPage} 
          onMenuChange={handleSellerMenuChange}
          storeData={storeData}
        >
          {renderSellerPageContent()}
        </AdminLayout>
      );

    default:
      return <CustomerHomePage />;
  }
}