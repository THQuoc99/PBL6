import React, { useState } from 'react';
import { 
  LayoutDashboard, Store, Users, ShoppingCart, Package, 
  BarChart3, Menu, X, Bell, Search, LogOut,
  FileText, TrendingUp, Shield, Tag
} from 'lucide-react';

export type AdminMenuItem = 
  | 'dashboard' 
  | 'stores' 
  | 'users' 
  | 'orders' 
  | 'products' 
  | 'analytics'
  | 'reports'
  | 'vouchers';

interface PlatformAdminLayoutProps {
  children: React.ReactNode;
  currentPage: AdminMenuItem;
  onMenuChange: (menu: AdminMenuItem) => void;
}

export default function PlatformAdminLayout({ 
  children, 
  currentPage, 
  onMenuChange 
}: PlatformAdminLayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [showNotifications, setShowNotifications] = useState(false);

  const menuItems = [
    { id: 'dashboard' as AdminMenuItem, label: 'Tổng quan', icon: LayoutDashboard },
    { id: 'stores' as AdminMenuItem, label: 'Quản lý cửa hàng', icon: Store },
    { id: 'users' as AdminMenuItem, label: 'Quản lý người dùng', icon: Users },
    { id: 'orders' as AdminMenuItem, label: 'Đơn hàng', icon: ShoppingCart },
    { id: 'products' as AdminMenuItem, label: 'Sản phẩm', icon: Package },
    { id: 'analytics' as AdminMenuItem, label: 'Phân tích', icon: TrendingUp },
    { id: 'reports' as AdminMenuItem, label: 'Báo cáo', icon: FileText },
    { id: 'vouchers' as AdminMenuItem, label: 'Quản lý Voucher', icon: Tag },
  ];

  const notifications = [
    { id: 1, text: 'Cửa hàng mới đăng ký chờ duyệt', time: '5 phút trước', unread: true },
    { id: 2, text: 'Sản phẩm vi phạm cần xem xét', time: '1 giờ trước', unread: true },
    { id: 3, text: 'Doanh thu hôm nay đạt 50M', time: '2 giờ trước', unread: false },
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside
        className={`${
          isSidebarOpen ? 'w-64' : 'w-20'
        } bg-gradient-to-b from-indigo-900 to-indigo-800 text-white transition-all duration-300 flex flex-col shadow-xl`}
      >
        {/* Logo */}
        <div className="p-6 flex items-center justify-between border-b border-indigo-700">
          {isSidebarOpen && (
            <div className="flex items-center space-x-2">
              <Shield className="h-8 w-8 text-yellow-400" />
              <span className="text-xl font-bold">SHOEX Admin</span>
            </div>
          )}
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="p-2 hover:bg-indigo-700 rounded-lg transition-colors"
          >
            {isSidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>

        {/* Menu Items */}
        <nav className="flex-1 py-6 px-3 space-y-2 overflow-y-auto">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onMenuChange(item.id)}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${
                  isActive
                    ? 'bg-white text-indigo-900 shadow-lg'
                    : 'text-indigo-100 hover:bg-indigo-700'
                }`}
              >
                <Icon className="h-5 w-5" />
                {isSidebarOpen && <span className="font-medium">{item.label}</span>}
              </button>
            );
          })}
        </nav>

        {/* Logout */}
        <div className="p-4 border-t border-indigo-700">
          <button className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-indigo-100 hover:bg-indigo-700 transition-colors">
            <LogOut className="h-5 w-5" />
            {isSidebarOpen && <span className="font-medium">Đăng xuất</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Top Header */}
        <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-40">
          <div className="px-6 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-4 flex-1 max-w-2xl">
              <Search className="h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Tìm kiếm cửa hàng, người dùng, đơn hàng..."
                className="flex-1 outline-none text-gray-700 placeholder-gray-400"
              />
            </div>

            <div className="flex items-center space-x-4">
              {/* Notifications */}
              <div className="relative">
                <button
                  onClick={() => setShowNotifications(!showNotifications)}
                  className="relative p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <Bell className="h-5 w-5 text-gray-600" />
                  <span className="absolute top-1 right-1 h-2 w-2 bg-red-500 rounded-full"></span>
                </button>

                {showNotifications && (
                  <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-xl border border-gray-200 py-2">
                    <div className="px-4 py-2 border-b border-gray-100">
                      <h3 className="font-semibold text-gray-900">Thông báo</h3>
                    </div>
                    {notifications.map((notif) => (
                      <div
                        key={notif.id}
                        className={`px-4 py-3 hover:bg-gray-50 cursor-pointer ${
                          notif.unread ? 'bg-blue-50' : ''
                        }`}
                      >
                        <p className="text-sm text-gray-900">{notif.text}</p>
                        <p className="text-xs text-gray-500 mt-1">{notif.time}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Admin Profile */}
              <div className="flex items-center space-x-3">
                <div className="h-10 w-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold">
                  A
                </div>
                <div>
                  <p className="text-sm font-semibold text-gray-900">Admin User</p>
                  <p className="text-xs text-gray-500">Quản trị viên</p>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 p-6 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
