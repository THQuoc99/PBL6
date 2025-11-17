import React, { useState } from 'react';
import MainApp from './MainApp';
import { ShoppingBag, User, Home, Package } from 'lucide-react';

type AppPage = 'login' | 'register' | 'forgot-password' | 'customer-home' | 'customer-products' | 'customer-product-detail' | 'customer-store' | 'customer-payment' | 'seller-register' | 'seller-dashboard';

export default function AppRouter() {
  const [currentPage, setCurrentPage] = useState<AppPage>('customer-home');

  // Check URL params for direct navigation
  React.useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const page = params.get('page') as AppPage;
      if (page && ['login', 'register', 'forgot-password', 'customer-home', 'customer-products', 'customer-product-detail', 'customer-store', 'customer-payment', 'seller-register', 'seller-dashboard'].includes(page)) {
        setCurrentPage(page);
      }
    }
  }, []);

  // Update MainApp when currentPage changes
  const [mainAppPage, setMainAppPage] = useState<AppPage>(currentPage);
  
  React.useEffect(() => {
    setMainAppPage(currentPage);
  }, [currentPage]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Demo Navigation Bar */}
      <nav className="bg-white shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center space-x-2">
              <ShoppingBag className="h-8 w-8 text-blue-600" />
              <span className="text-xl font-bold text-gray-900">SHOEX</span>
            </div>

            {/* Demo Navigation */}
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setCurrentPage('customer-home')}
                className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentPage === 'customer-home'
                    ? 'text-blue-600 bg-blue-50'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <Home className="h-4 w-4" />
                <span>Trang chủ</span>
              </button>

              <button
                onClick={() => setCurrentPage('customer-products')}
                className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentPage === 'customer-products'
                    ? 'text-blue-600 bg-blue-50'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <Package className="h-4 w-4" />
                <span>Sản phẩm</span>
              </button>

              <div className="w-px h-6 bg-gray-300"></div>

              <button
                onClick={() => setCurrentPage('login')}
                className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentPage === 'login'
                    ? 'text-blue-600 bg-blue-50'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <User className="h-4 w-4" />
                <span>Đăng nhập</span>
              </button>

              <button
                onClick={() => setCurrentPage('register')}
                className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentPage === 'register'
                    ? 'text-blue-600 bg-blue-50'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <span>Đăng ký</span>
              </button>

              <button
                onClick={() => setCurrentPage('seller-register')}
                className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentPage === 'seller-register'
                    ? 'text-blue-600 bg-blue-50'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <span>Seller</span>
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* App Content */}
      <div className="app-content">
        <MainApp initialPage={mainAppPage} />
      </div>
    </div>
  );
}