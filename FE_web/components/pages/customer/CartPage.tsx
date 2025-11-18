import React, { useState, useEffect } from 'react';
import CustomerLayout from '../../layout/CustomerLayout';
import { ShoppingCart, Trash2, Plus, Minus, Gift, Truck, Shield, ArrowRight, Check } from 'lucide-react';

interface CartPageProps {
  onNavigate?: (page: string, data?: any) => void;
}

interface CartItem {
  id: number;
  name: string;
  price: number;
  originalPrice?: number;
  quantity: number;
  size: string;
  color: string;
  image: string;
  inStock: boolean;
}

export default function CartPage({ onNavigate }: CartPageProps) {
  const [cartItems, setCartItems] = useState<CartItem[]>([
    {
      id: 1,
      name: 'Nike Air Max 270',
      price: 2490000,
      originalPrice: 2890000,
      quantity: 1,
      size: '42',
      color: 'Đen/Trắng',
      image: '/api/placeholder/150/150',
      inStock: true
    },
    {
      id: 2,
      name: 'Adidas Ultraboost 22',
      price: 3200000,
      quantity: 2,
      size: '41',
      color: 'Xanh Navy',
      image: '/api/placeholder/150/150',
      inStock: true
    },
    {
      id: 3,
      name: 'Converse Chuck Taylor',
      price: 1200000,
      originalPrice: 1500000,
      quantity: 1,
      size: '40',
      color: 'Trắng',
      image: '/api/placeholder/150/150',
      inStock: false
    }
  ]);

  const [promoCode, setPromoCode] = useState('');
  const [discount, setDiscount] = useState(0);
  const [selectedItems, setSelectedItems] = useState<number[]>([]);

  // Select all checkbox state
  const isAllSelected = cartItems.length > 0 && selectedItems.length === cartItems.length;
  const isPartiallySelected = selectedItems.length > 0 && selectedItems.length < cartItems.length;

  // Calculate selected items total
  const selectedItemsData = cartItems.filter(item => selectedItems.includes(item.id));
  const selectedSubtotal = selectedItemsData.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  const selectedTotalItems = selectedItemsData.reduce((sum, item) => sum + item.quantity, 0);

  // Handle individual item selection
  const handleItemSelect = (id: number) => {
    setSelectedItems(prev => 
      prev.includes(id) 
        ? prev.filter(itemId => itemId !== id)
        : [...prev, id]
    );
  };

  // Handle select all
  const handleSelectAll = () => {
    if (isAllSelected) {
      setSelectedItems([]);
    } else {
      setSelectedItems(cartItems.map(item => item.id));
    }
  };

  // Auto-select first item on mount
  useEffect(() => {
    if (cartItems.length > 0 && selectedItems.length === 0) {
      setSelectedItems([cartItems[0].id]);
    }
  }, [cartItems.length]);

  const updateQuantity = (id: number, newQuantity: number) => {
    if (newQuantity < 1) return;
    setCartItems(items =>
      items.map(item =>
        item.id === id ? { ...item, quantity: newQuantity } : item
      )
    );
  };

  const removeItem = (id: number) => {
    setCartItems(items => items.filter(item => item.id !== id));
    setSelectedItems(prev => prev.filter(itemId => itemId !== id));
  };

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

  const subtotal = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  const discountAmount = (selectedSubtotal * discount) / 100;
  const shippingFee = selectedSubtotal >= 299000 ? 0 : 30000;
  const total = selectedSubtotal - discountAmount + shippingFee;

  return (
    <CustomerLayout currentPage="cart" onNavigate={onNavigate}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center mb-8">
          <ShoppingCart className="h-8 w-8 text-blue-600 mr-3" />
          <h1 className="text-3xl font-bold text-gray-900">Giỏ Hàng ({cartItems.length})</h1>
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
                      Chọn tất cả ({cartItems.length} sản phẩm)
                    </span>
                  </div>
                </div>

                {cartItems.map((item) => (
                  <div key={item.id} className="bg-white rounded-xl shadow-lg p-6">
                    <div className="flex items-start space-x-4">
                      {/* Checkbox */}
                      <div className="pt-2">
                        <input
                          type="checkbox"
                          checked={selectedItems.includes(item.id)}
                          onChange={() => handleItemSelect(item.id)}
                          className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                      </div>

                      {/* Product Image */}
                      <div 
                        className="w-24 h-24 bg-gray-200 rounded-lg flex items-center justify-center flex-shrink-0 cursor-pointer hover:bg-gray-300 transition-colors"
                        onClick={() => onNavigate?.('product-detail', { productId: item.id })}
                      >
                        <span className="text-gray-500 text-xs">Image</span>
                      </div>

                      {/* Product Info */}
                      <div className="flex-1">
                        <div className="flex justify-between items-start mb-2">
                          <h3 
                            className="font-bold text-lg text-gray-900 cursor-pointer hover:text-blue-600 transition-colors"
                            onClick={() => onNavigate?.('product-detail', { productId: item.id })}
                          >
                            {item.name}
                          </h3>
                          <button
                            onClick={() => removeItem(item.id)}
                            className="text-red-500 hover:text-red-700 p-1"
                          >
                            <Trash2 className="h-5 w-5" />
                          </button>
                        </div>
                        
                        <div className="text-sm text-gray-600 mb-3">
                          <p>Size: {item.size} | Màu: {item.color}</p>
                          {!item.inStock && (
                            <p className="text-red-500 font-medium">Tạm hết hàng</p>
                          )}
                        </div>

                        <div className="flex items-center justify-between">
                          {/* Price */}
                          <div className="flex items-center space-x-2">
                            <span className="text-xl font-bold text-gray-900">
                              {item.price.toLocaleString()}đ
                            </span>
                            {item.originalPrice && (
                              <span className="text-sm text-gray-500 line-through">
                                {item.originalPrice.toLocaleString()}đ
                              </span>
                            )}
                          </div>

                          {/* Quantity Controls */}
                          <div className="flex items-center space-x-3">
                            <button
                              onClick={() => updateQuantity(item.id, item.quantity - 1)}
                              disabled={!item.inStock}
                              className="w-8 h-8 rounded-full border border-gray-300 flex items-center justify-center hover:bg-gray-100 disabled:opacity-50"
                            >
                              <Minus className="h-4 w-4" />
                            </button>
                            <span className="w-8 text-center font-medium">{item.quantity}</span>
                            <button
                              onClick={() => updateQuantity(item.id, item.quantity + 1)}
                              disabled={!item.inStock}
                              className="w-8 h-8 rounded-full border border-gray-300 flex items-center justify-center hover:bg-gray-100 disabled:opacity-50"
                            >
                              <Plus className="h-4 w-4" />
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
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
                  <div className="mb-4 p-3 bg-blue-50 rounded-lg">
                    <h4 className="font-medium text-blue-900 mb-2">Sản phẩm đã chọn:</h4>
                    <div className="space-y-2">
                      {selectedItemsData.map((item) => (
                        <div key={item.id} className="flex justify-between items-center text-sm">
                          <span className="text-gray-700">
                            {item.name} x{item.quantity}
                          </span>
                          <span className="font-medium text-blue-900">
                            {(item.price * item.quantity).toLocaleString()}đ
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Promo Code */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Mã giảm giá
                  </label>
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={promoCode}
                      onChange={(e) => setPromoCode(e.target.value)}
                      placeholder="Nhập mã giảm giá"
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                      onClick={applyPromoCode}
                      className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors"
                    >
                      Áp dụng
                    </button>
                  </div>
                </div>

                {/* Order Details */}
                <div className="space-y-3 mb-6">
                  <div className="flex justify-between">
                    <span>Tạm tính:</span>
                    <span>{selectedSubtotal.toLocaleString()}đ</span>
                  </div>
                  {discount > 0 && (
                    <div className="flex justify-between text-green-600">
                      <span>Giảm giá ({discount}%):</span>
                      <span>-{discountAmount.toLocaleString()}đ</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span>Phí vận chuyển:</span>
                    <span>
                      {shippingFee === 0 ? (
                        <span className="text-green-600">Miễn phí</span>
                      ) : (
                        `${shippingFee.toLocaleString()}đ`
                      )}
                    </span>
                  </div>
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
                  onClick={() => selectedItems.length > 0 && onNavigate?.('payment')}
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