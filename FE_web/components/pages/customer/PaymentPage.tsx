import React, { useState } from 'react';
import CustomerLayout from '../../layout/CustomerLayout';
import { 
  CreditCard, MapPin, Truck, Shield, ChevronDown, 
  Plus, Edit, Trash2, Check, Clock, Package
} from 'lucide-react';

interface PaymentPageProps {
  onNavigate?: (page: string) => void;
}

interface Address {
  id: string;
  name: string;
  phone: string;
  province: string;     // Tỉnh/TP
  ward: string;         // Phường/Xã
  street: string;       // Đường/Khu/Ấp
  specificAddress: string; // Địa chỉ đặc biệt (tự nhập)
  address: string;      // Địa chỉ đầy đủ (tổng hợp)
  isDefault: boolean;
}

interface PaymentMethod {
  id: string;
  type: 'card' | 'momo' | 'bank' | 'cod';
  name: string;
  icon: string;
  description: string;
}

interface OrderItem {
  id: string;
  name: string;
  image: string;
  price: number;
  quantity: number;
  variant: string;
}

export default function PaymentPage({ onNavigate }: PaymentPageProps) {
  const [selectedDeliveryAddress, setSelectedDeliveryAddress] = useState<string>('1'); // Địa chỉ giao hàng được chọn
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState<string>('card');
  const [selectedShipping, setSelectedShipping] = useState<string>('standard');
  const [showAddressList, setShowAddressList] = useState(false);
  const [showAddressForm, setShowAddressForm] = useState(false);
  const [editingAddress, setEditingAddress] = useState<Address | null>(null);
  const [cardDetails, setCardDetails] = useState({
    number: '',
    expiry: '',
    cvv: '',
    name: ''
  });
  const [isProcessing, setIsProcessing] = useState(false);
  const [newAddress, setNewAddress] = useState({
    name: '',
    phone: '',
    province: '',
    ward: '',
    street: '',
    specificAddress: ''
  });

  // Mock data
  const addresses: Address[] = [
    {
      id: '1',
      name: 'Nguyễn Văn A',
      phone: '0901234567',
      province: 'TP.Hồ Chí Minh',
      ward: 'Phường Bến Nghé',
      street: 'Đường Lê Lợi',
      specificAddress: 'Số 123, Tầng 2',
      address: 'TP.Hồ Chí Minh, Phường Bến Nghé, Đường Lê Lợi, Số 123, Tầng 2',
      isDefault: true
    },
    {
      id: '2',
      name: 'Nguyễn Văn A',
      phone: '0901234567',
      province: 'TP.Hồ Chí Minh',
      ward: 'Phường Bến Thành',
      street: 'Đường Nguyễn Huệ',
      specificAddress: 'Số 456, Chung cư ABC',
      address: 'TP.Hồ Chí Minh, Phường Bến Thành, Đường Nguyễn Huệ, Số 456, Chung cư ABC',
      isDefault: false
    },
    {
      id: '3',
      name: 'Nguyễn Văn A',
      phone: '0901234567',
      province: 'Hà Nội',
      ward: 'Phường Lê Đại Hành',
      street: 'Đường Bà Triệu',
      specificAddress: 'Số 789, Tòa nhà XYZ, Tầng 5',
      address: 'Hà Nội, Phường Lê Đại Hành, Đường Bà Triệu, Số 789, Tòa nhà XYZ, Tầng 5',
      isDefault: false
    }
  ];

  const defaultAddress = addresses.find(addr => addr.isDefault);
  const currentDeliveryAddress = addresses.find(addr => addr.id === selectedDeliveryAddress) || defaultAddress;
  
  const handleSelectAddress = (addressId: string) => {
    setSelectedDeliveryAddress(addressId);
    setShowAddressList(false);
  };

  const handleEditAddress = (address: Address) => {
    setEditingAddress(address);
    setNewAddress({
      name: address.name,
      phone: address.phone,
      province: address.province,
      ward: address.ward,
      street: address.street,
      specificAddress: address.specificAddress
    });
    setShowAddressForm(true);
    setShowAddressList(false);
  };

  const handleSaveAddress = () => {
    if (editingAddress) {
      // Update existing address logic here
      const fullAddress = `${newAddress.province}, ${newAddress.ward}, ${newAddress.street}, ${newAddress.specificAddress}`;
      console.log('Updating address:', { ...editingAddress, ...newAddress, address: fullAddress });
    } else {
      // Add new address logic here
      const fullAddress = `${newAddress.province}, ${newAddress.ward}, ${newAddress.street}, ${newAddress.specificAddress}`;
      console.log('Adding new address:', { ...newAddress, address: fullAddress });
    }
    setShowAddressForm(false);
    setEditingAddress(null);
    setNewAddress({ name: '', phone: '', province: '', ward: '', street: '', specificAddress: '' });
  };

  const handleCancelAddressForm = () => {
    setShowAddressForm(false);
    setEditingAddress(null);
    setNewAddress({ name: '', phone: '', province: '', ward: '', street: '', specificAddress: '' });
    if (showAddressList) {
      setShowAddressList(true);
    }
  };

  const paymentMethods: PaymentMethod[] = [
    {
      id: 'card',
      type: 'card',
      name: 'Thẻ tín dụng/ghi nợ',
      icon: '💳',
      description: 'Visa, Mastercard, JCB'
    },
    {
      id: 'momo',
      type: 'momo',
      name: 'Ví MoMo',
      icon: '🎯',
      description: 'Thanh toán qua ví điện tử MoMo'
    },
    {
      id: 'bank',
      type: 'bank',
      name: 'Chuyển khoản ngân hàng',
      icon: '🏦',
      description: 'Chuyển khoản trực tiếp'
    },
    {
      id: 'cod',
      type: 'cod',
      name: 'Thanh toán khi nhận hàng',
      icon: '💰',
      description: 'Thanh toán bằng tiền mặt'
    }
  ];

  const orderItems: OrderItem[] = [
    {
      id: '1',
      name: 'Nike Air Max 270 Premium',
      image: '/api/placeholder/80/80',
      price: 2500000,
      quantity: 1,
      variant: 'Đen - Size 42'
    },
    {
      id: '2',
      name: 'Adidas Ultraboost 22',
      image: '/api/placeholder/80/80',
      price: 2800000,
      quantity: 1,
      variant: 'Trắng - Size 42'
    }
  ];

  const shippingOptions = [
    { id: 'standard', name: 'Giao hàng tiêu chuẩn', time: '3-5 ngày', price: 30000 },
    { id: 'express', name: 'Giao hàng nhanh', time: '1-2 ngày', price: 50000 },
    { id: 'same-day', name: 'Giao hàng trong ngày', time: 'Trong ngày', price: 100000 }
  ];

  const subtotal = orderItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  const shippingCost = shippingOptions.find(s => s.id === selectedShipping)?.price || 0;
  const total = subtotal + shippingCost;

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(price);
  };

  const handlePayment = async () => {
    setIsProcessing(true);
    // Simulate payment processing
    await new Promise(resolve => setTimeout(resolve, 3000));
    setIsProcessing(false);
    // Redirect to success page or show success modal
    alert('Đặt hàng thành công!');
    onNavigate?.('home');
  };

  return (
    <CustomerLayout onNavigate={onNavigate}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumb */}
        <nav className="flex mb-6 text-sm">
          <button 
            onClick={() => onNavigate?.('home')}
            className="text-gray-500 hover:text-gray-700"
          >
            Trang chủ
          </button>
          <span className="mx-2 text-gray-500">/</span>
          <button 
            onClick={() => onNavigate?.('cart')}
            className="text-gray-500 hover:text-gray-700"
          >
            Giỏ hàng
          </button>
          <span className="mx-2 text-gray-500">/</span>
          <span className="text-gray-900">Thanh toán</span>
        </nav>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Payment Form */}
          <div className="lg:col-span-2 space-y-8">
            {/* Delivery Address */}
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                  <MapPin className="h-5 w-5 text-blue-600" />
                  Địa chỉ giao hàng
                </h2>
              </div>

              {!showAddressList && !showAddressForm && currentDeliveryAddress && (
                <div className="border border-gray-200 rounded-xl p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h4 className="font-medium">{currentDeliveryAddress.name}</h4>
                        <span className="text-gray-500">|</span>
                        <span className="text-gray-600">{currentDeliveryAddress.phone}</span>
                        {currentDeliveryAddress.isDefault && (
                          <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                            Mặc định
                          </span>
                        )}
                        {currentDeliveryAddress.id !== defaultAddress?.id && (
                          <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                            Địa chễ giao hàng
                          </span>
                        )}
                      </div>
                      <p className="text-gray-700">{currentDeliveryAddress.address}</p>
                    </div>
                    <button
                      onClick={() => setShowAddressList(true)}
                      className="text-blue-600 hover:text-blue-800 font-medium px-4 py-2 border border-blue-200 rounded-lg hover:bg-blue-50 transition-colors"
                    >
                      Thay đổi
                    </button>
                  </div>
                </div>
              )}

              {showAddressList && !showAddressForm && (
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-medium">Chọn địa chỉ giao hàng</h3>
                    <button
                      onClick={() => {
                        setShowAddressForm(true);
                        setShowAddressList(false);
                        setEditingAddress(null);
                      }}
                      className="text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1"
                    >
                      <Plus className="h-4 w-4" />
                      Thêm địa chỉ mới
                    </button>
                  </div>

                  <div className="space-y-3 mb-4">
                    {addresses.map((address) => (
                      <div
                        key={address.id}
                        className={`border rounded-xl p-4 cursor-pointer transition-colors ${
                          selectedDeliveryAddress === address.id 
                            ? 'border-blue-500 bg-blue-50' 
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                        onClick={() => handleSelectAddress(address.id)}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <h4 className="font-medium">{address.name}</h4>
                              <span className="text-gray-500">|</span>
                              <span className="text-gray-600">{address.phone}</span>
                              {address.isDefault && (
                                <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                                  Mặc định
                                </span>
                              )}
                              {selectedDeliveryAddress === address.id && (
                                <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                                  Đang chọn
                                </span>
                              )}
                            </div>
                            <p className="text-gray-700">{address.address}</p>
                          </div>
                          <div className="flex gap-2">
                            <button 
                              onClick={(e) => {
                                e.stopPropagation();
                                handleEditAddress(address);
                              }}
                              className="p-2 text-gray-400 hover:text-blue-600"
                            >
                              <Edit className="h-4 w-4" />
                            </button>
                            {!address.isDefault && (
                              <button 
                                onClick={(e) => {
                                  e.stopPropagation();
                                  // Delete address logic here
                                  console.log('Delete address:', address.id);
                                }}
                                className="p-2 text-gray-400 hover:text-red-600"
                              >
                                <Trash2 className="h-4 w-4" />
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  <button
                    onClick={() => setShowAddressList(false)}
                    className="w-full border border-gray-300 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Quay lại
                  </button>
                </div>
              )}

              {showAddressForm && (
                <div>
                  <h4 className="font-medium mb-4">
                    {editingAddress ? 'Chỉnh sửa địa chỉ' : 'Thêm địa chỉ mới'}
                  </h4>
                  <div className="space-y-4">
                    {/* Thông tin liên hệ */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <input
                        type="text"
                        placeholder="Họ và tên *"
                        value={newAddress.name}
                        onChange={(e) => setNewAddress({...newAddress, name: e.target.value})}
                        className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                      <input
                        type="tel"
                        placeholder="Số điện thoại *"
                        value={newAddress.phone}
                        onChange={(e) => setNewAddress({...newAddress, phone: e.target.value})}
                        className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    
                    {/* Địa chỉ hành chính theo thứ tự: Tỉnh/TP → Phường/Xã → Đường/Khu/Ấp → Địa chỉ đặc biệt */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <select
                        value={newAddress.province}
                        onChange={(e) => setNewAddress({...newAddress, province: e.target.value, ward: ''})}
                        className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="">Chọn Tỉnh/Thành phố *</option>
                        <option value="TP.Hồ Chí Minh">TP.Hồ Chí Minh</option>
                        <option value="Hà Nội">Hà Nội</option>
                        <option value="Đà Nẵng">Đà Nẵng</option>
                        <option value="Cần Thơ">Cần Thơ</option>
                        <option value="Hải Phòng">Hải Phòng</option>
                        <option value="An Giang">An Giang</option>
                        <option value="Bà Rịa - Vũng Tàu">Bà Rịa - Vũng Tàu</option>
                        <option value="Bắc Giang">Bắc Giang</option>
                        <option value="Bắc Ninh">Bắc Ninh</option>
                        <option value="Bình Dương">Bình Dương</option>
                        <option value="Đồng Nai">Đồng Nai</option>
                        <option value="Long An">Long An</option>
                      </select>
                      
                      <select
                        value={newAddress.ward}
                        onChange={(e) => setNewAddress({...newAddress, ward: e.target.value})}
                        className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        disabled={!newAddress.province}
                      >
                        <option value="">Chọn Phường/Xã *</option>
                        {newAddress.province === 'TP.Hồ Chí Minh' && (
                          <>
                            <option value="Phường Bến Nghé">Phường Bến Nghé</option>
                            <option value="Phường Bến Thành">Phường Bến Thành</option>
                            <option value="Phường Cô Giang">Phường Cô Giang</option>
                            <option value="Phường Nguyễn Thái Bình">Phường Nguyễn Thái Bình</option>
                            <option value="Phường Phạm Ngũ Lão">Phường Phạm Ngũ Lão</option>
                            <option value="Phường Cầu Ông Lãnh">Phường Cầu Ông Lãnh</option>
                            <option value="Phường Đa Kao">Phường Đa Kao</option>
                            <option value="Phường Tân Định">Phường Tân Định</option>
                          </>
                        )}
                        {newAddress.province === 'Hà Nội' && (
                          <>
                            <option value="Phường Lê Đại Hành">Phường Lê Đại Hành</option>
                            <option value="Phường Bách Khoa">Phường Bách Khoa</option>
                            <option value="Phường Đồng Nhân">Phường Đồng Nhân</option>
                            <option value="Phường Phố Huế">Phường Phố Huế</option>
                            <option value="Phường Hàng Bạc">Phường Hàng Bạc</option>
                            <option value="Phường Hàng Bài">Phường Hàng Bài</option>
                            <option value="Phường Hàng Trống">Phường Hàng Trống</option>
                          </>
                        )}
                        {newAddress.province === 'Đà Nẵng' && (
                          <>
                            <option value="Phường Thạch Thang">Phường Thạch Thang</option>
                            <option value="Phường Hải Châu I">Phường Hải Châu I</option>
                            <option value="Phường Hải Châu II">Phường Hải Châu II</option>
                            <option value="Phường Thuận Phước">Phường Thuận Phước</option>
                          </>
                        )}
                      </select>
                    </div>
                    
                    <select
                      value={newAddress.street}
                      onChange={(e) => setNewAddress({...newAddress, street: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      disabled={!newAddress.ward}
                    >
                      <option value="">Chọn Đường/Khu/Ấp *</option>
                      {newAddress.ward === 'Phường Bến Nghé' && (
                        <>
                          <option value="Đường Lê Lợi">Đường Lê Lợi</option>
                          <option value="Đường Nguyễn Huệ">Đường Nguyễn Huệ</option>
                          <option value="Đường Đồng Khởi">Đường Đồng Khởi</option>
                          <option value="Đường Nam Kỳ Khởi Nghĩa">Đường Nam Kỳ Khởi Nghĩa</option>
                        </>
                      )}
                      {newAddress.ward === 'Phường Bến Thành' && (
                        <>
                          <option value="Đường Lê Thị Riêng">Đường Lê Thị Riêng</option>
                          <option value="Đường Tôn Thất Đạm">Đường Tôn Thất Đạm</option>
                          <option value="Đường Phạm Ngũ Lão">Đường Phạm Ngũ Lão</option>
                        </>
                      )}
                      {newAddress.ward === 'Phường Cô Giang' && (
                        <>
                          <option value="Đường Cô Giang">Đường Cô Giang</option>
                          <option value="Đường Trần Quang Khải">Đường Trần Quang Khải</option>
                          <option value="Đường Nguyễn Cư Trinh">Đường Nguyễn Cư Trinh</option>
                        </>
                      )}
                      {newAddress.ward === 'Phường Lê Đại Hành' && (
                        <>
                          <option value="Đường Bà Triệu">Đường Bà Triệu</option>
                          <option value="Đường Lê Đại Hành">Đường Lê Đại Hành</option>
                          <option value="Đường Trần Khát Chân">Đường Trần Khát Chân</option>
                        </>
                      )}
                      {newAddress.ward === 'Phường Bách Khoa' && (
                        <>
                          <option value="Đường Tạ Quang Bữu">Đường Tạ Quang Bữu</option>
                          <option value="Đường Hai Bà Trưng">Đường Hai Bà Trưng</option>
                          <option value="Đường Trần Đại Nghĩa">Đường Trần Đại Nghĩa</option>
                        </>
                      )}
                      {newAddress.ward === 'Phường Hàng Bạc' && (
                        <>
                          <option value="Đường Hàng Bạc">Đường Hàng Bạc</option>
                          <option value="Đường Hàng Ngang">Đường Hàng Ngang</option>
                          <option value="Đường Hàng Đào">Đường Hàng Đào</option>
                        </>
                      )}
                      {newAddress.ward === 'Phường Thạch Thang' && (
                        <>
                          <option value="Đường 2 Tháng 9">Đường 2 Tháng 9</option>
                          <option value="Đường Lê Duẩn">Đường Lê Duẩn</option>
                          <option value="Đường Trần Phú">Đường Trần Phú</option>
                        </>
                      )}
                      {/* Thêm các khu vực, ấp cho các phường khác */}
                      {(newAddress.ward === 'Phường Nguyễn Thái Bình' || 
                        newAddress.ward === 'Phường Phạm Ngũ Lão' ||
                        newAddress.ward === 'Phường Cầu Ông Lãnh') && (
                        <>
                          <option value="Khu phố 1">Khu phố 1</option>
                          <option value="Khu phố 2">Khu phố 2</option>
                          <option value="Khu phố 3">Khu phố 3</option>
                        </>
                      )}
                      {(newAddress.ward === 'Phường Đồng Nhân' || 
                        newAddress.ward === 'Phường Phố Huế') && (
                        <>
                          <option value="Ngõ Quỳnh">Ngõ Quỳnh</option>
                          <option value="Ngõ Thái Hà">Ngõ Thái Hà</option>
                          <option value="Ngõ Láng Hạ">Ngõ Láng Hạ</option>
                        </>
                      )}
                      {(newAddress.ward === 'Phường Hải Châu I' || 
                        newAddress.ward === 'Phường Hải Châu II') && (
                        <>
                          <option value="Ấp 1">Ấp 1</option>
                          <option value="Ấp 2">Ấp 2</option>
                          <option value="Ấp Trung tâm">Ấp Trung tâm</option>
                        </>
                      )}
                    </select>
                    
                    {/* Địa chỉ cụ thể (tự nhập) */}
                    <textarea
                      placeholder="Địa chỉ đặc biệt (Số nhà, tầng, căn hộ, ghi chú thêm...) *"
                      rows={2}
                      value={newAddress.specificAddress}
                      onChange={(e) => setNewAddress({...newAddress, specificAddress: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    
                    <div className="flex gap-3">
                      <button 
                        onClick={handleSaveAddress}
                        className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        {editingAddress ? 'Cập nhật' : 'Thêm địa chỉ'}
                      </button>
                      <button
                        onClick={handleCancelAddressForm}
                        className="border border-gray-300 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors"
                      >
                        Hủy
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Payment Method */}
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
              <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                <CreditCard className="h-5 w-5 text-blue-600" />
                Phương thức thanh toán
              </h2>

              <div className="space-y-4">
                {paymentMethods.map((method) => (
                  <div
                    key={method.id}
                    className={`border rounded-xl p-4 cursor-pointer transition-colors ${
                      selectedPaymentMethod === method.id 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedPaymentMethod(method.id)}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{method.icon}</span>
                      <div className="flex-1">
                        <h4 className="font-medium">{method.name}</h4>
                        <p className="text-sm text-gray-600">{method.description}</p>
                      </div>
                      {selectedPaymentMethod === method.id && (
                        <Check className="h-5 w-5 text-blue-600" />
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* Card Details Form */}
              {selectedPaymentMethod === 'card' && (
                <div className="mt-6 p-4 border rounded-xl bg-gray-50">
                  <h4 className="font-medium mb-4">Chi tiết thẻ</h4>
                  <div className="space-y-4">
                    <input
                      type="text"
                      placeholder="Số thẻ"
                      value={cardDetails.number}
                      onChange={(e) => setCardDetails({...cardDetails, number: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <input
                      type="text"
                      placeholder="Tên trên thẻ"
                      value={cardDetails.name}
                      onChange={(e) => setCardDetails({...cardDetails, name: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <div className="grid grid-cols-2 gap-4">
                      <input
                        type="text"
                        placeholder="MM/YY"
                        value={cardDetails.expiry}
                        onChange={(e) => setCardDetails({...cardDetails, expiry: e.target.value})}
                        className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                      <input
                        type="text"
                        placeholder="CVV"
                        value={cardDetails.cvv}
                        onChange={(e) => setCardDetails({...cardDetails, cvv: e.target.value})}
                        className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Shipping Method */}
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
              <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                <Truck className="h-5 w-5 text-blue-600" />
                Phương thức vận chuyển
              </h2>

              <div className="space-y-4">
                {shippingOptions.map((option) => (
                  <div
                    key={option.id}
                    className={`border rounded-xl p-4 cursor-pointer transition-colors ${
                      selectedShipping === option.id 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedShipping(option.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="flex-1">
                          <h4 className="font-medium">{option.name}</h4>
                          <p className="text-sm text-gray-600 flex items-center gap-1">
                            <Clock className="h-4 w-4" />
                            {option.time}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">{formatPrice(option.price)}</p>
                        {selectedShipping === option.id && (
                          <Check className="h-5 w-5 text-blue-600 ml-auto" />
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Order Summary */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 h-fit">
            <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
              <Package className="h-5 w-5 text-blue-600" />
              Tóm tắt đơn hàng
            </h2>

            <div className="space-y-4 mb-6">
              {orderItems.map((item) => (
                <div key={item.id} className="flex gap-3">
                  <img 
                    src={item.image} 
                    alt={item.name}
                    className="w-16 h-16 object-cover rounded-lg"
                  />
                  <div className="flex-1">
                    <h4 className="font-medium text-sm line-clamp-2">{item.name}</h4>
                    <p className="text-xs text-gray-500">{item.variant}</p>
                    <div className="flex items-center justify-between mt-1">
                      <span className="text-sm text-gray-600">x{item.quantity}</span>
                      <span className="font-medium">{formatPrice(item.price)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="border-t pt-4 space-y-3">
              <div className="flex justify-between">
                <span>Tạm tính</span>
                <span>{formatPrice(subtotal)}</span>
              </div>
              <div className="flex justify-between">
                <span>Phí vận chuyển</span>
                <span>{formatPrice(shippingCost)}</span>
              </div>
              <div className="flex justify-between text-lg font-semibold border-t pt-3">
                <span>Tổng cộng</span>
                <span className="text-blue-600">{formatPrice(total)}</span>
              </div>
            </div>

            <button
              onClick={handlePayment}
              disabled={isProcessing}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white py-4 rounded-xl font-medium mt-6 transition-colors flex items-center justify-center gap-2"
            >
              {isProcessing ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                  Đang xử lý...
                </>
              ) : (
                <>
                  <Shield className="h-5 w-5" />
                  Đặt hàng ({formatPrice(total)})
                </>
              )}
            </button>

            <div className="mt-4 text-xs text-gray-500 text-center">
              Bằng cách đặt hàng, bạn đồng ý với{' '}
              <button className="text-blue-600 hover:underline">Điều khoản dịch vụ</button>
              {' '}và{' '}
              <button className="text-blue-600 hover:underline">Chính sách bảo mật</button>
            </div>
          </div>
        </div>
      </div>
    </CustomerLayout>
  );
}