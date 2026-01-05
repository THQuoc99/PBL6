import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import CustomerLayout from '../../layout/CustomerLayout';
import { ShoppingCart, Trash2, Plus, Minus, Gift, Truck, Shield, ArrowRight, Loader2 } from 'lucide-react';
import { useCart } from '../../../hooks/cart/cart';
import { useAuth } from '../../../hooks/user/useAuth';

interface CartPageProps {
  onNavigate?: (page: string, data?: any) => void;
}

export default function CartPage({ onNavigate }: CartPageProps) {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { cart, loading, error, removeFromCart, updateQuantity, clearCart, fetchCart } = useCart();
  const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
  const [promoCode, setPromoCode] = useState('');
  const [discount, setDiscount] = useState(0);
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [processingItems, setProcessingItems] = useState<Set<string>>(new Set());

  const cartItems = cart?.items || [];
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(price);
  };
  // Selectable items (only in-stock)
  const selectableItems = cartItems.filter(item => (item.variant?.stock ?? 0) > 0);
  const selectableItemIds = selectableItems.map(i => i.itemId);

  // Select all checkbox state (only counts selectable items)
  const isAllSelected = selectableItemIds.length > 0 && selectedItems.length === selectableItemIds.length;
  const isPartiallySelected = selectedItems.length > 0 && selectedItems.length < selectableItemIds.length;

  // Calculate selected items total
  const selectedItemsData = cartItems.filter(item => selectedItems.includes(item.itemId));
  const selectedSubtotal = selectedItemsData.reduce(
    (sum, item) => sum + Number(item.subtotal), 0
  );

  const selectedTotalItems = selectedItemsData.reduce((sum, item) => sum + item.quantity, 0);

  // Handle individual item selection
  const handleItemSelect = (itemId: string) => {
    setSelectedItems(prev => 
      prev.includes(itemId) 
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  // Handle select all (only toggle selectable items)
  const handleSelectAll = () => {
    if (isAllSelected) {
      setSelectedItems([]);
    } else {
      setSelectedItems(selectableItemIds);
    }
  };

  // Auto-select all in-stock items on mount
  useEffect(() => {
    if (selectableItemIds.length > 0 && selectedItems.length === 0) {
      setSelectedItems(selectableItemIds);
    }
  }, [selectableItemIds.length]);

  // Handle quantity update
  const handleUpdateQuantity = async (itemId: string, newQuantity: number) => {
    if (newQuantity < 1) return;
    
    setProcessingItems(prev => new Set(prev).add(itemId));
    try {
      const result = await updateQuantity(itemId, newQuantity);
      if (!result.success) {
        alert(result.errors?.[0] || 'Lỗi cập nhật số lượng');
      }
    } finally {
      setProcessingItems(prev => {
        const newSet = new Set(prev);
        newSet.delete(itemId);
        return newSet;
      });
    }
  };

  // Handle remove item
  const handleRemoveItem = async (itemId: string) => {
    if (!confirm('Bạn có chắc muốn xóa sản phẩm này?')) return;
    
    setProcessingItems(prev => new Set(prev).add(itemId));
    try {
      const result = await removeFromCart(itemId);
      if (result.success) {
        setSelectedItems(prev => prev.filter(id => id !== itemId));
      } else {
        alert(result.errors?.[0] || 'Lỗi xóa sản phẩm');
      }
    } finally {
      setProcessingItems(prev => {
        const newSet = new Set(prev);
        newSet.delete(itemId);
        return newSet;
      });
    }
  };

  // Handle clear cart
  const handleClearCart = async () => {
    if (!confirm('Bạn có chắc muốn xóa tất cả sản phẩm trong giỏ hàng?')) return;
    
    const result = await clearCart();
    if (result.success) {
      setSelectedItems([]);
      alert('Đã xóa tất cả sản phẩm');
    } else {
      alert(result.errors?.[0] || 'Lỗi xóa giỏ hàng');
    }
  };

  // Apply promo code
  const applyPromoCode = () => {
    const codes: Record<string, number> = {
      'SHOEX20': 20,
      'WELCOME10': 10,
      'FREESHIP': 0
    };
    
    if (codes[promoCode.toUpperCase()]) {
      setDiscount(codes[promoCode.toUpperCase()]);
      alert(`Áp dụng mã giảm giá ${promoCode} thành công!`);
    } else {
      alert('Mã giảm giá không hợp lệ');
    }
  };

  // Calculate totals
  const discountAmount = (selectedSubtotal * discount) / 100;
  const shippingFee = selectedSubtotal >= 299000 ? 0 : 30000;
  const total = selectedSubtotal - discountAmount + shippingFee;

  // Redirect if not authenticated
  if (!isAuthenticated) {
    return (
      <CustomerLayout currentPage="cart" onNavigate={onNavigate}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <ShoppingCart className="h-24 w-24 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-medium text-gray-900 mb-2">Vui lòng đăng nhập</h3>
            <p className="text-gray-500 mb-6">Bạn cần đăng nhập để xem giỏ hàng</p>
            <button 
              onClick={() => navigate('/auth/login')}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Đăng Nhập
            </button>
          </div>
        </div>
      </CustomerLayout>
    );
  }

  // Show loading
  if (loading && !cart) {
    return (
      <CustomerLayout currentPage="cart" onNavigate={onNavigate}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-center min-h-[400px]">
            <Loader2 className="h-12 w-12 text-blue-600 animate-spin" />
          </div>
        </div>
      </CustomerLayout>
    );
  }

  // Show error
  if (error) {
    return (
      <CustomerLayout currentPage="cart" onNavigate={onNavigate}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
            <p className="text-red-800">{error}</p>
            <button 
              onClick={fetchCart}
              className="mt-4 bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700"
            >
              Thử Lại
            </button>
          </div>
        </div>
      </CustomerLayout>
    );
  }

  return (
    <CustomerLayout currentPage="cart" onNavigate={onNavigate}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center">
            <ShoppingCart className="h-8 w-8 text-blue-600 mr-3" />
            <h1 className="text-3xl font-bold text-gray-900">
              Giỏ Hàng ({cart?.totalItems || 0})
            </h1>
          </div>
          {cartItems.length > 0 && (
            <button
              onClick={handleClearCart}
              className="text-red-600 hover:text-red-700 font-medium flex items-center gap-2"
            >
              <Trash2 className="h-5 w-5" />
              Xóa tất cả
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Cart Items */}
          <div className="lg:col-span-2">
            {cartItems.length === 0 ? (
              <div className="bg-white rounded-xl shadow-lg p-12 text-center">
                <ShoppingCart className="h-24 w-24 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-medium text-gray-500 mb-2">Giỏ hàng trống</h3>
                <p className="text-gray-400 mb-6">Hãy thêm sản phẩm yêu thích vào giỏ hàng</p>
                <button 
                  onClick={() => onNavigate?.('customer-products')}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Tiếp Tục Mua Sắm
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Select All Checkbox */}
                <div className="bg-white rounded-xl shadow-lg p-4">
                  <div className="flex items-center gap-3">
                    <div className="relative">
                      <input
                        type="checkbox"
                        checked={isAllSelected}
                        ref={el => {
                          if (el) el.indeterminate = isPartiallySelected;
                        }}
                        onChange={handleSelectAll}
                        className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      />
                    </div>
                    <span className="font-medium text-gray-700">
                      Chọn tất cả ({selectableItems.length} sản phẩm khả dụng)
                    </span>
                  </div>
                </div>

                {cartItems.map((item) => {
                  const isProcessing = processingItems.has(item.itemId);
                  const inStock = item.variant.stock > 0;
                  
                  return (
                    <div key={item.itemId} className={`bg-white rounded-xl shadow-lg p-6 ${(isProcessing || !inStock) ? 'opacity-50' : ''}`}>
                      <div className="flex items-start space-x-4">
                        {/* Checkbox */}
                        <div className="pt-2">
                          <input
                            type="checkbox"
                            checked={selectedItems.includes(item.itemId)}
                            onChange={() => handleItemSelect(item.itemId)}
                            disabled={!inStock || isProcessing}
                            className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                          />
                        </div>
                    
                        {/* Product Image */}
                        <div className="w-24 h-24 rounded-lg overflow-hidden flex-shrink-0 cursor-pointer relative group">
                          <img 
                            src={item.variant.colorImageUrl} 
                            alt={item.variant.product.name}
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                            onClick={() => navigate(`/product/${item.variant.product.productId}`)}
                          />
                          <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                        </div>

                        {/* Product Info */}
                        <div className="flex-1">
                          <div className="flex justify-between items-start mb-2">
                            <h3 
                              className="font-bold text-lg text-gray-900 cursor-pointer hover:text-blue-600 transition-colors"
                              onClick={() => navigate(`/product/${item.variant.product.productId}`)}
                            >
                              {item.variant.product.name}
                            </h3>
                            <button
                              onClick={() => handleRemoveItem(item.itemId)}
                              disabled={isProcessing}
                              className="text-red-500 hover:text-red-700 p-1 disabled:opacity-50"
                            >
                              {isProcessing ? (
                                <Loader2 className="h-5 w-5 animate-spin" />
                              ) : (
                                <Trash2 className="h-5 w-5" />
                              )}
                            </button>
                          </div>
                          
                          <div className="text-sm text-gray-600 mb-3">
                            <p>Size: {item.variant.sizeName} | Màu: {item.variant.colorName}</p>
                            {!inStock && (
                              <p className="text-red-500 font-medium">Tạm hết hàng</p>
                            )}
                            {inStock && item.variant.stock < 10 && (
                              <p className="text-orange-500 font-medium">Chỉ còn {item.variant.stock} sản phẩm</p>
                            )}
                          </div>

                          <div className="flex items-center justify-between">
                            {/* Price */}
                            <div className="flex flex-col">
                              <div className="flex items-center space-x-2">
                                <span className="text-xl font-bold text-gray-900">
                                  {formatPrice(item.unitPrice )}
                                </span>
                                {item.variant.finalPrice < item.variant.price && (
                                  <span className="text-sm text-gray-500 line-through">
                                    {formatPrice(item.variant.price)}
                                  </span>
                                )}
                              </div>
                              <span className="text-sm text-gray-500">
                                Tổng: {item.subtotal.toLocaleString()}đ
                              </span>
                            </div>

                            {/* Quantity Controls */}
                            <div className="flex items-center space-x-3">
                              <button
                                onClick={() => handleUpdateQuantity(item.itemId, item.quantity - 1)}
                                disabled={!inStock || isProcessing || item.quantity <= 1}
                                className="w-8 h-8 rounded-full border border-gray-300 flex items-center justify-center hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                              >
                                <Minus className="h-4 w-4" />
                              </button>
                              <span className="w-8 text-center font-medium">
                                {isProcessing ? (
                                  <Loader2 className="h-4 w-4 animate-spin mx-auto" />
                                ) : (
                                  item.quantity
                                )}
                              </span>
                              <button
                                onClick={() => handleUpdateQuantity(item.itemId, item.quantity + 1)}
                                disabled={!inStock || isProcessing || item.quantity >= item.variant.stock}
                                className="w-8 h-8 rounded-full border border-gray-300 flex items-center justify-center hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                              >
                                <Plus className="h-4 w-4" />
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Order Summary */}
          {cartItems.length > 0 && (
            <div className="lg:col-span-1">
              <div className="bg-white rounded-xl shadow-lg p-6 sticky top-8">
                <h2 className="text-xl font-bold text-gray-900 mb-6">
                  Tóm Tắt Đơn Hàng 
                  {selectedItems.length > 0 && (
                    <span className="text-sm font-normal text-gray-500">
                      ({selectedItems.length} sản phẩm đã chọn)
                    </span>
                  )}
                </h2>

                {/* Selected Items Preview */}
                {selectedItems.length > 0 && (
                  <div className="space-y-4 mb-6">
                    {selectedItemsData.map((item) => (
                      <div key={item.itemId} className="flex gap-3">
                        <img
                          src={item.variant.colorImageUrl} 
                          alt={item.variant.product.name}
                          className="w-16 h-16 object-cover rounded-lg"
                        />

                        <div className="flex-1">
                          <h4 className="font-medium text-sm line-clamp-2">
                            {item.variant.product.name}
                          </h4>

                          <p className="text-xs text-gray-500">
                            {item.variant.colorName} | Size: {item.variant.sizeName}
                          </p>

                          <div className="flex items-center justify-between mt-1">
                            <span className="text-sm text-gray-600">
                              x{item.quantity}
                            </span>

                            <span className="font-medium">
                              {formatPrice(item.subtotal)}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                {/* Order Details */}
                <div className="space-y-3 mb-6">
                  <div className="flex justify-between">
                    <span>Tạm tính:</span>
                   <span>{selectedSubtotal.toLocaleString('vi-VN', { maximumFractionDigits: 2 })}đ</span>
                  </div>
                  {discount > 0 && (
                    <div className="flex justify-between text-green-600">
                      <span>Giảm giá ({discount}%):</span>
                      <span>-{discountAmount.toLocaleString()}đ</span>
                    </div>
                  )}
                  <div className="border-t pt-3 flex justify-between font-bold text-lg">
                    <span>Tổng cộng:</span>
                    <span className="text-blue-600">{total.toLocaleString()}đ</span>
                  </div>
                </div>

                {/* Benefits */}
                <div className="space-y-3 mb-6">
                  <div className="flex items-center space-x-2 text-sm text-green-600">
                    <Truck className="h-4 w-4" />
                    <span>Miễn phí vận chuyển cho đơn từ 299k</span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-blue-600">
                    <Shield className="h-4 w-4" />
                    <span>Đổi trả miễn phí trong 7 ngày</span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-purple-600">
                    <Gift className="h-4 w-4" />
                    <span>Tích điểm thành viên</span>
                  </div>
                </div>
                {/* Checkout Button */}
                <button 
                  onClick={() => {
                    if (selectedItems.length > 0) {
                      // Lấy dữ liệu các item đã chọn
                      const selectedItemsData = cartItems.filter(item => selectedItems.includes(item.itemId));
                      navigate('/payment', { state: { orderItems: selectedItemsData } });
                    }
                  }}
                  disabled={selectedItems.length === 0}
                  className={`w-full py-3 rounded-lg transition-colors flex items-center justify-center font-medium ${
                    selectedItems.length > 0 
                      ? 'bg-blue-600 text-white hover:bg-blue-700' 
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  <span>
                    {selectedItems.length > 0 
                      ? `Thanh Toán (${selectedItems.length} sản phẩm)` 
                      : 'Chọn sản phẩm để thanh toán'
                    }
                  </span>
                  {selectedItems.length > 0 && <ArrowRight className="h-5 w-5 ml-2" />}
                </button>

                <button 
                  onClick={() => onNavigate?.('customer-products')}
                  className="w-full mt-3 border border-gray-300 text-gray-700 py-3 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Tiếp Tục Mua Sắm
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </CustomerLayout>
  );
}