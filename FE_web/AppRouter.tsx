import React, { useState, useEffect } from 'react';
import MainApp from './MainApp';
import { ShoppingBag, User, Home, Package, LogOut, Store } from 'lucide-react';
import { useAuth } from './hooks/uses/useAuth';
import LoginPage from './components/pages/auth/LoginPage';
import RegisterPage from './components/pages/auth/RegisterPage';
import { storeService } from './services/store'; // đảm bảo import đúng

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

  // Đồng bộ URL params khi load
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

  // Hàm navigate chuẩn
  const navigate = (path: string) => {
    let page: AppPage = 'customer-home';

    switch (path) {
      case '/home':
        page = 'customer-home';
        break;
      case '/products':
        page = 'customer-products';
        break;
      case '/product-detail':
        page = 'customer-product-detail';
        break;
      case '/store':
        page = 'customer-store';
        break;
      case '/payment':
        page = 'customer-payment';
        break;
      case '/promotions':
        page = 'customer-promotions';
        break;
      case '/contact':
        page = 'customer-contact';
        break;
      case '/cart':
        page = 'customer-cart';
        break;
      case '/wishlist':
        page = 'customer-wishlist';
        break;
      case '/account':
        page = 'customer-account';
        break;
      case '/collections':
        page = 'collections';
        break;
      case '/login':
        page = 'login';
        break;
      case '/register':
        page = 'register';
        break;
      case '/seller-login':
        page = 'seller-login';
        break;
      case '/seller-register':
        page = 'seller-register';
        break;
      case '/seller/dashboard':
        page = 'seller-dashboard';
        break;
      default:
        page = 'customer-home';
    }

    setCurrentPage(page);

    // Đồng bộ URL
    const url = new URL(window.location.href);
    url.searchParams.set('page', page);
    window.history.pushState({}, '', url.toString());
  };

  const handleLoginSuccess = () => navigate('/home');
  const handleRegisterSuccess = () => {
    navigate('/login');
    alert('Đăng ký thành công! Vui lòng đăng nhập.');
  };
  const handleLogout = () => {
    logout();
    navigate('/home');
  };

  // Seller auth
  const [showSellerAuth, setShowSellerAuth] = useState(false);
  const [sellerPass, setSellerPass] = useState('');
  const [sellerError, setSellerError] = useState('');
  const { getStoreInfo, checkStore } = require('./hooks/stores/storeAuth').useStoreAuth();

  const handleSellerClick = async () => {
    const store = await getStoreInfo();
    if (!store) {
      navigate('/seller-register');
      return;
    }
    setShowSellerAuth(true);
    setSellerPass('');
    setSellerError('');
  };

  const handleSellerAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSellerError('');
    const result = await checkStore(sellerPass);
    if (result.success) {
      setShowSellerAuth(false);
      navigate('/seller/dashboard');
    } else {
      setSellerError(result.message || 'Sai mật khẩu');
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
            <div className="flex items-center space-x-3">
              <ShoppingBag className="h-9 w-9 text-blue-600" />
              <span className="text-2xl font-bold text-gray-900">SHOEX</span>
            </div>

            <div className="flex items-center space-x-6">
              <button
                onClick={() => navigate('/home')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  currentPage === 'customer-home'
                    ? 'text-blue-600 bg-blue-50'
                    : 'text-gray-700 hover:text-blue-600 hover:bg-gray-100'
                }`}
              >
                <Home className="h-5 w-5" />
                <span>Trang chủ</span>
              </button>

              <button
                onClick={() => navigate('/products')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  currentPage === 'customer-products'
                    ? 'text-blue-600 bg-blue-50'
                    : 'text-gray-700 hover:text-blue-600 hover:bg-gray-100'
                }`}
              >
                <Package className="h-5 w-5" />
                <span>Sản phẩm</span>
              </button>

              <button
                onClick={handleSellerClick}
                className="flex items-center space-x-2 px-5 py-2.5 rounded-lg text-sm font-semibold bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700 transition-all shadow-md hover:shadow-lg transform hover:scale-105"
              >
                <Store className="h-5 w-5" />
                <span>Bán hàng trên SHOEX</span>
              </button>

              {!isAuthenticated ? (
                <>
                  <div className="w-px h-8 bg-gray-300 mx-2"></div>
                  <button
                    onClick={() => navigate('/login')}
                    className="flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-100"
                  >
                    <User className="h-5 w-5" />
                    <span>Đăng nhập</span>
                  </button>
                  <button
                    onClick={() => navigate('/register')}
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

      {showSellerAuth && (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
          <form
            className="bg-white rounded-lg shadow-lg p-8 w-full max-w-sm flex flex-col gap-4"
            onSubmit={handleSellerAuthSubmit}
          >
            <h2 className="text-xl font-bold mb-2 text-center">Xác thực cửa hàng</h2>
            <input
              type="password"
              className="border rounded px-3 py-2 w-full"
              placeholder="Nhập mật khẩu tài khoản"
              value={sellerPass}
              onChange={e => setSellerPass(e.target.value)}
              required
            />
            {sellerError && <div className="text-red-600 text-sm text-center">{sellerError}</div>}
            <button
              type="submit"
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 font-semibold"
            >
              Xác thực
            </button>
            <button
              type="button"
              className="mt-2 text-gray-500 hover:text-gray-700 text-sm"
              onClick={() => setShowSellerAuth(false)}
            >
              Hủy
            </button>
          </form>
        </div>
      )}

      <div className="app-content">
        {currentPage === 'login' ? (
          <LoginPage
            onLogin={handleLoginSuccess}
            onNavigateToRegister={() => navigate('/register')}
          />
        ) : currentPage === 'register' ? (
          <RegisterPage onRegister={handleRegisterSuccess} onNavigateToLogin={() => navigate('/login')} />
        ) : (
          <MainApp initialPage={mainAppPage} onNavigate={navigate} />
        )}
      </div>
    </div>
  );
}
