import React from 'react';
import CustomerLayout from '../../layout/CustomerLayout';
import { Tag, Clock, Gift, Percent, Star, ArrowRight } from 'lucide-react';

interface PromotionsPageProps {
  onNavigate?: (page: string) => void;
}

export default function PromotionsPage({ onNavigate }: PromotionsPageProps) {
  const promotions = [
    {
      id: 1,
      title: 'Flash Sale 50%',
      description: 'Giảm giá sốc cho tất cả giày thể thao',
      discount: '50%',
      endTime: '2024-12-31',
      image: '/api/placeholder/300/200',
      type: 'flash',
      minOrder: 500000
    },
    {
      id: 2,
      title: 'Mua 2 Tặng 1',
      description: 'Áp dụng cho dép sandal và phụ kiện',
      discount: 'Buy 2 Get 1',
      endTime: '2024-12-25',
      image: '/api/placeholder/300/200',
      type: 'bundle',
      minOrder: 300000
    },
    {
      id: 3,
      title: 'Miễn phí vận chuyển',
      description: 'Cho đơn hàng từ 299k trở lên',
      discount: 'Free Ship',
      endTime: '2024-12-20',
      image: '/api/placeholder/300/200',
      type: 'shipping',
      minOrder: 299000
    },
    {
      id: 4,
      title: 'Giảm 30% Giày Da',
      description: 'Chương trình đặc biệt cuối năm',
      discount: '30%',
      endTime: '2024-12-28',
      image: '/api/placeholder/300/200',
      type: 'category',
      minOrder: 400000
    }
  ];

  const voucherCodes = [
    { code: 'NEWYEAR2024', discount: '20%', minOrder: '500k', expires: '31/12/2024' },
    { code: 'FREESHIP50', discount: 'Free Ship', minOrder: '299k', expires: '25/12/2024' },
    { code: 'SHOEX30', discount: '30%', minOrder: '700k', expires: '28/12/2024' },
  ];

  return (
    <CustomerLayout currentPage="promotions" onNavigate={onNavigate}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">🎉 Khuyến Mãi Đặc Biệt</h1>
          <p className="text-xl text-gray-600">Cơ hội vàng để sở hữu những đôi giày yêu thích với giá tốt nhất!</p>
        </div>

        {/* Featured Promotion */}
        <div className="bg-gradient-to-r from-red-500 to-pink-500 rounded-2xl text-white p-8 mb-12">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="mb-6 md:mb-0">
              <div className="flex items-center mb-4">
                <Gift className="h-8 w-8 mr-3" />
                <span className="text-2xl font-bold">MEGA SALE CUỐI NĂM</span>
              </div>
              <h2 className="text-5xl font-extrabold mb-2">70% OFF</h2>
              <p className="text-xl mb-4">Cho tất cả sản phẩm trong cửa hàng</p>
              <div className="flex items-center text-lg">
                <Clock className="h-5 w-5 mr-2" />
                <span>Còn lại: 15 ngày 08 giờ 45 phút</span>
              </div>
            </div>
            <button className="bg-white text-red-500 px-8 py-4 rounded-lg font-bold text-lg hover:bg-gray-100 transition-colors">
              Mua Ngay
            </button>
          </div>
        </div>

        {/* Promotions Grid */}
        <div className="mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 flex items-center">
            <Tag className="h-8 w-8 mr-3 text-blue-600" />
            Chương Trình Khuyến Mãi
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {promotions.map((promo) => (
              <div key={promo.id} className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
                <div className="relative">
                  <div className="h-48 bg-gray-200 flex items-center justify-center">
                    <span className="text-gray-500">Image placeholder</span>
                  </div>
                  <div className="absolute top-4 right-4">
                    <span className="bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold">
                      {promo.discount}
                    </span>
                  </div>
                </div>
                <div className="p-6">
                  <h3 className="font-bold text-lg mb-2">{promo.title}</h3>
                  <p className="text-gray-600 mb-4">{promo.description}</p>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Đơn tối thiểu: {promo.minOrder.toLocaleString()}đ</span>
                    <span className="text-red-500 font-medium">Đến {promo.endTime}</span>
                  </div>
                  <button className="w-full mt-4 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors">
                    Áp Dụng Ngay
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Voucher Codes */}
        <div className="mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 flex items-center">
            <Percent className="h-8 w-8 mr-3 text-green-600" />
            Mã Giảm Giá
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {voucherCodes.map((voucher, index) => (
              <div key={index} className="bg-gradient-to-r from-green-400 to-blue-500 rounded-lg p-6 text-white">
                <div className="flex items-center justify-between mb-4">
                  <div className="bg-white text-gray-800 px-3 py-1 rounded font-mono font-bold">
                    {voucher.code}
                  </div>
                  <button className="text-white hover:text-gray-200">
                    Copy
                  </button>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center">
                    <Star className="h-4 w-4 mr-2" />
                    <span>Giảm {voucher.discount}</span>
                  </div>
                  <div className="flex items-center">
                    <ArrowRight className="h-4 w-4 mr-2" />
                    <span>Đơn tối thiểu {voucher.minOrder}</span>
                  </div>
                  <div className="flex items-center">
                    <Clock className="h-4 w-4 mr-2" />
                    <span>HSD: {voucher.expires}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Newsletter Signup */}
        <div className="bg-gray-50 rounded-2xl p-8 text-center">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            🔔 Đăng Ký Nhận Thông Báo Khuyến Mãi
          </h3>
          <p className="text-gray-600 mb-6">
            Không bỏ lỡ các ưu đãi đặc biệt và mã giảm giá độc quyền
          </p>
          <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
            <input
              type="email"
              placeholder="Nhập email của bạn"
              className="flex-1 px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
              Đăng Ký
            </button>
          </div>
        </div>
      </div>
    </CustomerLayout>
  );
}