import React, { useState } from "react";
import { Routes, Route, useNavigate, Navigate } from "react-router-dom";
import MainApp from "./MainApp";
import LoginPage from "./components/pages/auth/LoginPage";
import RegisterPage from "./components/pages/auth/RegisterPage";
import SellerLoginPage from "./components/pages/seller/SellerLoginPage";
import SellerRegistrationPage from "./components/pages/seller/SellerRegistrationPage";
import { useAuth } from "./hooks/user/useAuth";
import { ShoppingBag, User, Home, Package, LogOut, Store } from "lucide-react";
import { storeService } from "./services/store/store";

export default function AppRouter() {
  const { user, isAuthenticated, logout, loading } = useAuth();
  const navigate = useNavigate();
  const [showSellerAuth, setShowSellerAuth] = useState(false);
  const [sellerPass, setSellerPass] = useState('');
  const [sellerError, setSellerError] = useState('');
  const { getStoreInfo, checkStore } = require('./hooks/store/storeAuth').useStoreAuth();

  const handleLogout = () => {
    logout();
    navigate("/home");
  };

  const handleSellerClick = async () => {
      try {
        if(isAuthenticated) {
    const store = await getStoreInfo();
    if (!store) return navigate("/seller-register");

    // If seller was authenticated recently, skip re-auth
    try {
      const key = `seller_auth_${store.storeId}`;
      const raw = localStorage.getItem(key);
      if (raw) {
        const obj = JSON.parse(raw);
        if (obj && obj.expires && Date.now() < obj.expires) {
          return navigate('/seller/dashboard');
        }
      }
    } catch (e) {
      /* ignore localStorage parse errors */
    }

    setShowSellerAuth(true);
    setSellerPass('');
    setSellerError('');
        } else {
        navigate('/login');
        }
      } catch (err) {
        console.error('handleSellerClick error', err);
        // If an error occurs (e.g. auth issue), redirect to login
        navigate('/login');
      }
  };
  const handleSellerAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSellerError('');
    const result = await checkStore(sellerPass);
    if (result.success) {
      // remember successful seller auth for 7 days
      try {
        const store = await getStoreInfo();
        if (store) {
          const key = `seller_auth_${store.storeId}`;
          const payload = { ts: Date.now(), expires: Date.now() + 7 * 24 * 60 * 60 * 1000 };
          localStorage.setItem(key, JSON.stringify(payload));
        }
      } catch (e) {
        // ignore
      }
      setShowSellerAuth(false);
      navigate("/seller/dashboard");
    } else {
      setSellerError(result.message || "Sai mật khẩu");
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
                onClick={() => navigate("/home")}
                className="px-4 py-2 rounded-lg text-sm font-medium"
              >
                <Home className="h-5 w-5 inline" /> Trang chủ
              </button>
              <button
                onClick={() => navigate("/products")}
                className="px-4 py-2 rounded-lg text-sm font-medium"
              >
                <Package className="h-5 w-5 inline" /> Sản phẩm
              </button>
              <button
                onClick={handleSellerClick}
                className="px-5 py-2.5 rounded-lg text-sm font-semibold bg-gradient-to-r from-purple-600 to-blue-600 text-white"
              >
                <Store className="h-5 w-5 inline" /> Bán hàng trên SHOEX
              </button>

              {!isAuthenticated ? (
                <>
                  <button onClick={() => navigate("/login")}>
                    <User className="h-5 w-5 inline" /> Đăng nhập
                  </button>
                  <button onClick={() => navigate("/register")}>
                    Đăng ký
                  </button>
                </>
              ) : (
                <button onClick={handleLogout}>
                  <LogOut className="h-5 w-5 inline" /> Đăng xuất
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
              onChange={(e) => setSellerPass(e.target.value)}
              required
            />
            {sellerError && <div className="text-red-600 text-sm text-center">{sellerError}</div>}
            <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">
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

      {/* Routing */}
      <Routes>
        {/* Customer pages */}
        <Route path="/home" element={<MainApp initialPage="customer-home" />} />
        <Route path="/products" element={<MainApp initialPage="customer-products" />} />
        <Route path="/product/:id" element={<MainApp initialPage="customer-product-detail" />} />
        <Route path="/product-detail" element={<MainApp initialPage="customer-product-detail" />} />
        <Route path="/store/:storeId?" element={<MainApp initialPage="customer-store" />} />
        <Route path="/payment" element={<MainApp initialPage="customer-payment" />} />
        <Route path="/promotions" element={<MainApp initialPage="customer-promotions" />} />
        <Route path="/contact" element={<MainApp initialPage="customer-contact" />} />
        <Route path="/cart" element={<MainApp initialPage="customer-cart" />} />
        <Route path="/wishlist" element={<MainApp initialPage="customer-wishlist" />} />
        <Route path="/account/:section?" element={<MainApp initialPage="customer-account" />} />
        <Route path="/collections/:category?" element={<MainApp initialPage="collections" />} />

        {/* Auth pages */}
        <Route path="/login" element={<LoginPage onLogin={() => navigate("/home")} onNavigateToRegister={() => navigate("/register")} />} />
        <Route path="/register" element={<RegisterPage onRegister={() => navigate("/login")} onNavigateToLogin={() => navigate("/login")} />} />

        {/* Seller pages */}
        <Route path="/seller-login" element={<SellerLoginPage onLogin={() => navigate("/seller/dashboard")} onNavigateToRegister={() => navigate("/seller-register")} onBackToCustomer={() => navigate("/home")} />} />
        <Route path="/seller-register" element={<SellerRegistrationPage />} />
        <Route path="/seller/dashboard/*" element={<MainApp initialPage="seller-dashboard" />} />

        {/* Platform Admin pages */}
        <Route path="/admin/*" element={<MainApp initialPage="platform-admin" />} />

        {/* Default redirect */}
        <Route path="*" element={<Navigate to="/home" replace />} />
      </Routes>
    </div>
  );
}
