import React, { useState, useEffect } from 'react';
import MainApp from './MainApp';
import { ShoppingBag, User, Home, Package, LogOut, Store } from 'lucide-react';
import { useAuth } from './hooks/useAuth';
import LoginPage from './components/pages/auth/LoginPage';
import RegisterPage from './components/pages/auth/RegisterPage';
import { storeService } from './services/store'; // ← Đảm bảo import đúng

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

export default function AppRouter() {
  const [currentPage, setCurrentPage] = useState<AppPage>('customer-home');
  const [mainAppPage, setMainAppPage] = useState<AppPage>('customer-home');
  const { user, isAuthenticated, logout, loading } = useAuth();

  // Đồng bộ URL params
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const page = params.get('page') as AppPage;
      if (page) setCurrentPage(page);
    }
  }, []);

  useEffect(() => {
    setMainAppPage(currentPage);
  }, [currentPage]);

  const handleLoginSuccess = () => setCurrentPage('customer-home');
  const handleRegisterSuccess = () => {
    setCurrentPage('login');
    alert('Đăng ký thành công! Vui lòng đăng nhập.');
  };
  const handleLogout = () => {
    logout();
    storeService.clearCurrentStore(); // Xóa store khi logout
    setCurrentPage('customer-home');
  };

  // XỬ LÝ NÚT "SELLER" – KIỂM TRA CÓ SHOP CHƯA
  const handleSellerClick = async () => {
    const myStore = await storeService.getCurrentStore();

    if (myStore) {
      console.log('Đã có shop → Chuyển đến Seller Dashboard:', myStore.name);
      setCurrentPage('seller-dashboard');
    } else {
      console.log('Chưa có shop → Chuyển đến tạo shop');
      setCurrentPage('seller-register');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-32 w-32 border-b-4 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Bar */}
      <nav className="bg-white shadow-md border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center space-x-3">
              <ShoppingBag className="h-9 w-9 text-blue-600" />
              <span className="text-2xl font-bold text-gray-900">SHOEX</span>
            </div>

            {/* Navigation Links */}
            <div className="flex items-center space-x-6">
              <button
                onClick={() => setCurrentPage('customer-home')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  currentPage.startsWith('customer-') && currentPage !== 'customer-store'
                    ? 'text-blue-600 bg-blue-50'
                    : 'text-gray-700 hover:text-blue-600 hover:bg-gray-100'
                }`}
              >
                <Home className="h-5 w-5" />
                <span>Trang chủ</span>
              </button>

              <button
                onClick={() => setCurrentPage('customer-products')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  currentPage === 'customer-products'
                    ? 'text-blue-600 bg-blue-50'
                    : 'text-gray-700 hover:text-blue-600 hover:bg-gray-100'
                }`}
              >
                <Package className="h-5 w-5" />
                <span>Sản phẩm</span>
              </button>

              {/* NÚT SELLER - ĐÃ ĐƯỢC XỬ LÝ THÔNG MINH */}
              <button
                onClick={handleSellerClick}
                className="flex items-center space-x-2 px-5 py-2.5 rounded-lg text-sm font-semibold bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700 transition-all shadow-md hover:shadow-lg transform hover:scale-105"
              >
                <Store className="h-5 w-5" />
                <span>Bán hàng trên SHOEX</span>
              </button>

              {/* Auth Buttons */}
              {!isAuthenticated ? (
                <>
                  <div className="w-px h-8 bg-gray-300 mx-2"></div>
                  <button
                    onClick={() => setCurrentPage('login')}
                    className="flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-100"
                  >
                    <User className="h-5 w-5" />
                    <span>Đăng nhập</span>
                  </button>
                  <button
                    onClick={() => setCurrentPage('register')}
                    className="px-5 py-2.5 rounded-lg text-sm font-semibold bg-blue-600 text-white hover:bg-blue-700 transition-all"
                  >
                    Đăng ký
                  </button>
                </>
              ) : (
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50"
                >
                  <LogOut className="h-5 w-5" />
                  <span>Đăng xuất</span>
                </button>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Nội dung chính */}
      <div className="app-content">
        {currentPage === 'login' ? (
          <LoginPage
            onLogin={handleLoginSuccess}
            onNavigateToRegister={() => setCurrentPage('register')}
          />
        ) : currentPage === 'register' ? (
          <RegisterPage onRegister={handleRegisterSuccess} onNavigateToLogin={() => setCurrentPage('login')} />
        ) : (
          <MainApp initialPage={mainAppPage} onNavigate={(page) => setCurrentPage(page as AppPage)} />
        )}
      </div>
    </div>
  );
}