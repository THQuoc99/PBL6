// MainApp.tsx
import React, { useState, useEffect } from 'react';
import {
  LoginPage,
  RegisterPage,
  ForgotPasswordPage,
  SellerLoginPage,
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
  CollectionsPage,
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
import DashboardPage from './components/pages/seller/DashboardPage';
import { MenuItems, Product, Order, StoreSettings } from './types';
type AppPage = 
  | 'login'
  | 'register'
  | 'forgot-password'
  | 'customer-home'
  | 'customer-products'
  | 'customer-product-detail'
  | 'customer-store'
  | 'customer-payment'
  | 'customer-promotions'
  | 'customer-contact'
  | 'customer-cart'
  | 'customer-wishlist'
  | 'customer-account'
  | 'collections'
  | 'seller-login'
  | 'seller-register'
  | 'seller-dashboard';

interface MainAppProps {
  initialPage?: AppPage;
  onNavigate?: (page: AppPage) => void;
}

export default function MainApp({ initialPage = 'customer-home', onNavigate }: MainAppProps) {
  const [currentAppPage, setCurrentAppPage] = useState<AppPage>(initialPage);
  const [currentSellerPage, setCurrentSellerPage] = useState<MenuItems>('dashboard');

  // Update internal state when initialPage changes
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
    shipping: { cod: true, express: true, standard: true }
  });

  const storeData = {
    name: settings.storeName,
    totalProducts: products.length,
    totalOrders: orders.length,
    totalRevenue: orders.reduce((sum, order) => sum + order.amount, 0),
    totalCustomers: 892
  };

  // --- Event handlers ---
  const handleLogin = (result: any) => {
    console.log('Login:', result);
    if (result.success) onNavigate?.('seller-dashboard');
  };

  const handleRegister = (data: any) => {
    console.log('Register:', data);
    onNavigate?.('seller-dashboard');
  };

  const handleSellerLogin = async (username: string, password: string) => {
    console.log('Seller Login:', { username, password });
    await new Promise((r) => setTimeout(r, 600));
    if (username === 'seller' && password === 'seller') {
      onNavigate?.('seller-dashboard');
      return;
    }
    throw new Error('Tên đăng nhập hoặc mật khẩu không đúng');
  };

  const handleSellerRegister = (data: any) => {
    console.log('Seller Register:', data);
    alert('Đăng ký thành công! Vui lòng đăng nhập.');
    onNavigate?.('seller-login');
  };

  const handleSellerMenuChange = (menu: MenuItems) => {
    setCurrentSellerPage(menu);
  };

  const pageMap: Record<string, AppPage> = {
    home: 'customer-home',
    products: 'customer-products',
    'product-detail': 'customer-product-detail',
    store: 'customer-store',
    payment: 'customer-payment',
    promotions: 'customer-promotions',
    contact: 'customer-contact',
    cart: 'customer-cart',
    wishlist: 'customer-wishlist',
    account: 'customer-account',
    collections: 'collections',
    'login': 'login',
    'register': 'register',
    'seller-login': 'seller-login',
    'seller-register': 'seller-register'
  };

  const handleCustomerNavigate = (page: string, data?: any) => {
    setCurrentAppPage(pageMap[page] || 'customer-home');
    onNavigate?.(pageMap[page] || 'customer-home');
  };

  // --- Seller dashboard render ---

  const renderSellerPageContent = () => {
    switch (currentSellerPage) {
      case 'dashboard':
        return (
          <DashboardPage
            onNavigate={(menu) => setCurrentSellerPage(menu as MenuItems)}
          />
        );
      case 'products': return <SellerProductsPage products={products} setProducts={setProducts} />;
      case 'orders': return <OrdersPage orders={orders} setOrders={setOrders} query="" />;
      case 'listings': return <ListingsPage />;
      case 'promotions': return <PromotionsPage />;
      case 'chatbot': return <ChatbotAIPage />;
      case 'payments': return <PaymentsPage />;
      case 'settings': return <SettingsPage settings={settings} setSettings={setSettings} />;
      default:
        return (
          <DashboardPage
            onNavigate={(menu) => setCurrentSellerPage(menu as MenuItems)}
          />
        );
    }
  };

  // --- Main routing ---
  switch (currentAppPage) {
    case 'login':
      return (
        <LoginPage 
          onLogin={handleLogin}
          onNavigateToRegister={() => onNavigate?.('register')}
          onNavigateToForgot={() => onNavigate?.('forgot-password')}
        />
      );

    case 'register':
      return (
        <RegisterPage 
          onRegister={handleRegister}
          onNavigateToLogin={() => onNavigate?.('login')}
        />
      );

    case 'forgot-password':
      return (
        <ForgotPasswordPage 
          onNavigateToLogin={() => onNavigate?.('login')}
          onSendResetEmail={(email) => console.log('Sending reset email to:', email)}
        />
      );

    case 'customer-home': return <CustomerHomePage onNavigate={handleCustomerNavigate} />;
    case 'customer-products': return <CustomerProductsPage onNavigate={handleCustomerNavigate} />;
    case 'customer-product-detail': return <CustomerProductDetailPage onNavigate={handleCustomerNavigate} />;
    case 'customer-store': return <CustomerStorePage onNavigate={handleCustomerNavigate} />;
    case 'customer-payment': return <CustomerPaymentPage onNavigate={handleCustomerNavigate} />;
    case 'customer-promotions': return <CustomerPromotionsPage onNavigate={handleCustomerNavigate} />;
    case 'customer-contact': return <CustomerContactPage onNavigate={handleCustomerNavigate} />;
    case 'customer-cart': return <CustomerCartPage onNavigate={handleCustomerNavigate} />;
    case 'customer-wishlist': return <CustomerWishlistPage onNavigate={handleCustomerNavigate} />;
    case 'customer-account': return <CustomerAccountPage onNavigate={handleCustomerNavigate} />;
    case 'collections': return <CollectionsPage onNavigate={handleCustomerNavigate} />;

    case 'seller-login':
      return (
        <SellerLoginPage 
          onLogin={handleSellerLogin}
          onNavigateToRegister={() => onNavigate?.('seller-register')}
          onBackToCustomer={() => onNavigate?.('customer-home')}
        />
      );

    case 'seller-register':
      return (
        <SellerRegistrationPage 
          onComplete={() => onNavigate?.('seller-login')}
          onBackToCustomer={() => onNavigate?.('customer-home')}
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
      return <CustomerHomePage onNavigate={handleCustomerNavigate} />;
  }
}
