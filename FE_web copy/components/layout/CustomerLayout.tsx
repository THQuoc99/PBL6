import React, { useState, useEffect } from 'react';
import { Search, Menu, X, Heart, ShoppingCart, User, Home, Package, Store, Tag, Truck, Star, LogOut, Phone, Bot, MessageSquare, Sparkles } from 'lucide-react';
import { useAuth } from '../../hooks/user/useAuth';
import { authService } from '../../services/user/auth';
import { useNavigate } from 'react-router-dom';

interface CustomerLayoutProps {
  children: React.ReactNode;
  currentPage?: string;
  onNavigate?: (page: string) => void;
  onSearch?: (searchText: string) => void;
  searchValue?: string;
  onSearchSubmit?: (searchText: string) => void;
}

export default function CustomerLayout({ children, currentPage, onNavigate, onSearch, searchValue = '', onSearchSubmit }: CustomerLayoutProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [showUserDropdown, setShowUserDropdown] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([
    { role: 'assistant', content: 'Xin chào! Tôi là trợ lý AI của Shoex. Tôi có thể giúp gì cho bạn hôm nay?' },
    { role: 'assistant', content: 'Bạn có muốn tìm kiếm bộ sưu tập giày mới nhất không?', isSuggestion: true },
  ]);
  const [localSearch, setLocalSearch] = useState(searchValue);
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

  // Sync localSearch với searchValue từ props
  useEffect(() => {
    setLocalSearch(searchValue);
  }, [searchValue]);

  const handleLogout = () => {
    logout();
    onNavigate?.('login');
  };

  const handleSearchSubmit = () => {
    if (localSearch.trim()) {
      // Navigate to products page with search query
      navigate(`/products?search=${encodeURIComponent(localSearch.trim())}`);
      // Also call the prop callback if exists
      onSearchSubmit?.(localSearch.trim());
    }
  };

  const navigationItems = [
    { icon: Tag, label: 'Khuyến mãi', href: '/promotions', value: 'promotions' },
    { icon: Phone, label: 'Liên hệ', href: '/contact', value: 'contact' },
  ];

  const handleSendChat = () => {
    if (!chatMessage.trim()) return;

    // Add user message to history
    setChatHistory(prev => [...prev, { role: 'user', content: chatMessage }]);
    const currentMsg = chatMessage;
    setChatMessage('');

    // Placeholder for AI thinking logic
    setTimeout(() => {
      setChatHistory(prev => [...prev, {
        role: 'assistant',
        content: `Cảm ơn bạn đã hỏi "${currentMsg}". Đây là chức năng AI Chatbot đang được phát triển, chúng tôi sẽ sớm tích hợp bộ não thông minh nhất vào đây!`
      }]);
    }, 800);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-[2560px] mx-auto px-2 sm:px-3 lg:px-4">
          <div className="flex justify-between items-center h-16">
            {/* Mobile menu button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="lg:hidden p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
            >
              <Menu className="h-6 w-6" />
            </button>

            {/* Navigation - Desktop */}
            <nav className="hidden lg:flex space-x-6">
              {navigationItems.map((item) => (
                <button
                  key={item.value}
                  onClick={() => navigate(item.href)}
                  className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${currentPage === item.value
                    ? 'text-blue-600 bg-blue-50'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                >
                  <item.icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </button>
              ))}
            </nav>

            {/* Search */}
            <div className="hidden md:flex flex-1 max-w-md mx-6">
              <div className="relative w-full">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Search className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  placeholder="Tìm kiếm sản phẩm..."
                  value={localSearch}
                  onChange={(e) => {
                    setLocalSearch(e.target.value);
                    onSearch?.(e.target.value);
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      handleSearchSubmit();
                    }
                  }}
                  className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            {/* User actions */}
            <div className="flex items-center space-x-3">
              <button
                onClick={() => navigate('/wishlist')}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md relative"
              >
                <Heart className="h-6 w-6" />
                <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                  2
                </span>
              </button>

              <button
                onClick={() => navigate('/cart')}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md relative"
              >
                <ShoppingCart className="h-6 w-6" />
                <span className="absolute -top-1 -right-1 h-4 w-4 bg-blue-500 text-white text-xs rounded-full flex items-center justify-center">
                  3
                </span>
              </button>

              {isAuthenticated && user ? (
                // User is logged in - Show user info with dropdown
                <div className="relative">
                  <button
                    onClick={() => navigate('/account')}
                    onMouseEnter={() => setShowUserDropdown(true)}
                    onMouseLeave={() => setShowUserDropdown(false)}
                    className="flex items-center space-x-2 p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md"
                  >
                    <div className="w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center text-sm font-medium">
                      {user.fullName?.charAt(0) || user.username?.charAt(0) || 'U'}
                    </div>
                    <div className="text-left hidden sm:block">
                      <div className="text-sm font-medium">{user.fullName || user.username}</div>
                      <div className="text-xs text-gray-500 uppercase">{user.role}</div>
                    </div>
                  </button>

                  {/* Dropdown Menu */}
                  {showUserDropdown && (
                    <div
                      className="absolute right-0 top-full mt-0.1 w-48 bg-white rounded-md shadow-lg border border-gray-200 py-1 z-50"
                      onMouseEnter={() => setShowUserDropdown(true)}
                      onMouseLeave={() => setShowUserDropdown(false)}
                    >
                      <button
                        onClick={() => {
                          setShowUserDropdown(false);
                          navigate('/account');
                        }}
                        className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
                      >
                        <User className="h-4 w-4" />
                        <span>Tài khoản của tôi</span>
                      </button>
                      <hr className="my-1" />
                      <button
                        onClick={() => {
                          setShowUserDropdown(false);
                          handleLogout();
                        }}
                        className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center space-x-2"
                      >
                        <LogOut className="h-4 w-4" />
                        <span>Đăng xuất</span>
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                // User is not logged in
                <button
                  onClick={() => navigate('/account')}
                  className="flex items-center space-x-2 p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md"
                >
                  <User className="h-6 w-6" />
                  <span className="hidden sm:block text-sm">Tài khoản</span>
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="lg:hidden border-t bg-white">
            <div className="px-4 py-3 space-y-2">
              {navigationItems.map((item) => (
                <button
                  key={item.value}
                  onClick={() => navigate(item.href)}
                  className={`w-full flex items-center space-x-3 px-3 py-2 rounded-md text-sm font-medium ${currentPage === item.value
                    ? 'text-blue-600 bg-blue-50'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                >
                  <item.icon className="h-5 w-5" />
                  <span>{item.label}</span>
                </button>
              ))}

              {/* Mobile Search */}
              <div className="pt-4">
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Search className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    type="text"
                    placeholder="Tìm kiếm sản phẩm..."
                    value={localSearch}
                    onChange={(e) => {
                      setLocalSearch(e.target.value);
                      onSearch?.(e.target.value);
                    }}
                    className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
            </div>
          </div>
        )}
      </header>

      {/* Main Content - use same container as header so content aligns with menu */}
      <main>
        <div className="max-w-[2560px] mx-auto px-2 sm:px-3 lg:px-4 py-6">
          {children}
        </div>
      </main>

      {/* AI Chatbot Floating Button & Window */}
      <div className="fixed bottom-6 right-6 z-[100] flex flex-col items-end">
        {/* Chat Window */}
        {isChatOpen && (
          <div className="mb-4 w-[350px] sm:w-[400px] h-[500px] bg-white rounded-2xl shadow-2xl border border-gray-100 flex flex-col overflow-hidden animate-in slide-in-from-bottom-5 duration-300">
            {/* Header */}
            <div className="p-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white flex items-center justify-between shadow-md">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                  <Bot className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="font-bold">AI Assistant</h3>
                  <div className="flex items-center space-x-1 text-[10px] opacity-90">
                    <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></span>
                    <span>Sẵn sàng hỗ trợ</span>
                  </div>
                </div>
              </div>
              <button
                onClick={() => setIsChatOpen(false)}
                className="p-1 hover:bg-white/10 rounded-lg transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50/50">
              {chatHistory.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`p-3 rounded-2xl shadow-sm max-w-[85%] ${msg.role === 'user'
                      ? 'bg-blue-600 text-white rounded-tr-none'
                      : 'bg-white border border-gray-100 text-gray-800 rounded-tl-none'
                    }`}>
                    {msg.role === 'assistant' && (msg as any).isSuggestion && (
                      <div className="flex items-center space-x-2 text-blue-600 mb-1">
                        <Sparkles className="h-3 w-3" />
                        <span className="text-[10px] font-bold uppercase tracking-wider">AI Suggestion</span>
                      </div>
                    )}
                    <p className="text-sm">{msg.content}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* Input */}
            <form
              onSubmit={(e) => { e.preventDefault(); handleSendChat(); }}
              className="p-4 bg-white border-t border-gray-100"
            >
              <div className="relative">
                <input
                  type="text"
                  value={chatMessage}
                  onChange={(e) => setChatMessage(e.target.value)}
                  placeholder="Nhập tin nhắn..."
                  className="w-full pl-4 pr-12 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                />
                <button
                  type="submit"
                  className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-md shadow-blue-200"
                >
                  <MessageSquare className="h-4 w-4" />
                </button>
              </div>
              <p className="text-[10px] text-gray-400 text-center mt-2">Powered by Shoex AI Experience</p>
            </form>
          </div>
        )}

        {/* Toggle Button */}
        <button
          onClick={() => setIsChatOpen(!isChatOpen)}
          className={`group flex items-center justify-center w-14 h-14 rounded-full shadow-2xl transition-all duration-300 transform hover:scale-110 active:scale-95 ${isChatOpen
            ? 'bg-red-500 text-white rotate-90 hover:bg-red-600'
            : 'bg-gradient-to-tr from-blue-600 to-indigo-600 text-white shadow-blue-300'
            }`}
        >
          {isChatOpen ? <X className="h-7 w-7" /> : <Bot className="h-7 w-7 group-hover:animate-bounce" />}

          {/* Badge/Pulse */}
          {!isChatOpen && (
            <span className="absolute top-0 right-0 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500 border-2 border-white"></span>
            </span>
          )}
        </button>
      </div>
    </div>
  );
}