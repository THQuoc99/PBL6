import React, { useState } from 'react';
import CustomerLayout from '../../layout/CustomerLayout';
import { 
  Star, Heart, ShoppingCart, MessageCircle, Award, MapPin, 
  Clock, Phone, Mail, Shield, Users, Package, Eye, Filter,
  Grid, List, ChevronDown
} from 'lucide-react';

interface StorePageProps {
  onNavigate?: (page: string) => void;
  storeId?: string;
}

interface Store {
  id: string;
  name: string;
  avatar: string;
  cover: string;
  rating: number;
  reviews: number;
  followers: number;
  products: number;
  responseTime: string;
  joinDate: string;
  isVerified: boolean;
  description: string;
  location: string;
  phone: string;
  email: string;
  policies: {
    return: string;
    shipping: string;
    warranty: string;
  };
}

export default function StorePage({ onNavigate, storeId = 'store1' }: StorePageProps) {
  const [activeTab, setActiveTab] = useState<'products' | 'about' | 'reviews'>('products');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState('popular');

  // Mock store data
  const store: Store = {
    id: 'store1',
    name: 'SHOEX Official Store',
    avatar: '/api/placeholder/100/100',
    cover: '/api/placeholder/1200/400',
    rating: 4.9,
    reviews: 15420,
    followers: 125000,
    products: 1250,
    responseTime: '1 giờ',
    joinDate: '2020-01-15',
    isVerified: true,
    description: `SHOEX Official Store là cửa hàng chính hãng chuyên cung cấp giày thể thao, giày thời trang từ các thương hiệu hàng đầu thế giới như Nike, Adidas, Puma, Vans, Converse...

Với hơn 5 năm kinh nghiệm trong ngành, chúng tôi cam kết:
• 100% sản phẩm chính hãng
• Bảo hành đầy đủ theo chính sách nhà sản xuất
• Giao hàng nhanh toàn quốc
• Đổi trả miễn phí trong 30 ngày`,
    location: 'TP.Hồ Chí Minh, Việt Nam',
    phone: '+84 901 234 567',
    email: 'contact@shoex.vn',
    policies: {
      return: 'Đổi trả miễn phí trong 30 ngày',
      shipping: 'Giao hàng toàn quốc, miễn phí với đơn từ 500k',
      warranty: 'Bảo hành chính hãng 6-12 tháng'
    }
  };

  // Mock store products
  const storeProducts = [
    {
      id: '1',
      name: 'Nike Air Max 270 Premium',
      price: 2500000,
      originalPrice: 3000000,
      rating: 4.8,
      reviews: 124,
      image: '/api/placeholder/300/300',
      sold: 1200,
      category: 'Giày thể thao'
    },
    {
      id: '2',
      name: 'Adidas Ultraboost 22',
      price: 2800000,
      rating: 4.9,
      reviews: 89,
      image: '/api/placeholder/300/300',
      sold: 800,
      category: 'Giày chạy bộ'
    },
    {
      id: '3',
      name: 'Puma RS-X Sneakers',
      price: 2200000,
      rating: 4.7,
      reviews: 156,
      image: '/api/placeholder/300/300',
      sold: 650,
      category: 'Giày thể thao'
    },
    {
      id: '4',
      name: 'Vans Old Skool Classic',
      price: 1800000,
      rating: 4.6,
      reviews: 203,
      image: '/api/placeholder/300/300',
      sold: 950,
      category: 'Giày thường'
    },
    {
      id: '5',
      name: 'Converse Chuck Taylor All Star',
      price: 1200000,
      rating: 4.5,
      reviews: 180,
      image: '/api/placeholder/300/300',
      sold: 1100,
      category: 'Giày thường'
    },
    {
      id: '6',
      name: 'New Balance 574 Core',
      price: 2000000,
      rating: 4.7,
      reviews: 95,
      image: '/api/placeholder/300/300',
      sold: 420,
      category: 'Giày thể thao'
    }
  ];

  // Mock store reviews
  const storeReviews = [
    {
      id: '1',
      user: 'Nguyễn Văn A',
      avatar: '/api/placeholder/40/40',
      rating: 5,
      date: '2024-11-10',
      comment: 'Shop uy tín, giao hàng nhanh. Sản phẩm chất lượng, đúng như mô tả.',
      helpful: 23
    },
    {
      id: '2',
      user: 'Trần Thị B',
      avatar: '/api/placeholder/40/40',
      rating: 5,
      date: '2024-11-08',
      comment: 'Đã mua nhiều lần ở shop này, luôn hài lòng. Nhân viên tư vấn nhiệt tình.',
      helpful: 15
    },
    {
      id: '3',
      user: 'Lê Minh C',
      avatar: '/api/placeholder/40/40',
      rating: 4,
      date: '2024-11-05',
      comment: 'Sản phẩm tốt, đóng gói cẩn thận. Sẽ tiếp tục ủng hộ shop.',
      helpful: 8
    }
  ];

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(price);
  };

  const sortOptions = [
    { value: 'popular', label: 'Phổ biến nhất' },
    { value: 'newest', label: 'Mới nhất' },
    { value: 'price-low', label: 'Giá: Thấp đến Cao' },
    { value: 'price-high', label: 'Giá: Cao đến Thấp' },
    { value: 'rating', label: 'Đánh giá cao nhất' },
    { value: 'sold', label: 'Bán chạy nhất' }
  ];

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
          <span className="text-gray-900">Cửa hàng</span>
        </nav>

        {/* Store Header */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden mb-8">
          {/* Cover Image */}
          <div className="relative h-64 bg-gradient-to-r from-blue-600 to-purple-600">
            <img 
              src={store.cover}
              alt="Store cover"
              className="w-full h-full object-cover mix-blend-overlay"
            />
          </div>

          {/* Store Info */}
          <div className="p-8">
            <div className="flex items-start gap-6 mb-6">
              <img 
                src={store.avatar}
                alt={store.name}
                className="w-24 h-24 rounded-full object-cover border-4 border-white shadow-lg -mt-16"
              />
              
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h1 className="text-3xl font-bold text-gray-900">{store.name}</h1>
                  {store.isVerified && (
                    <Award className="h-6 w-6 text-blue-500" aria-label="Cửa hàng đã xác minh" role="img" />
                  )}
                </div>
                
                <div className="flex items-center gap-6 text-gray-600 mb-4">
                  <div className="flex items-center gap-1">
                    <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                    <span className="font-medium">{store.rating}</span>
                    <span>({store.reviews.toLocaleString()} đánh giá)</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Users className="h-4 w-4" />
                    <span>{store.followers.toLocaleString()} người theo dõi</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Package className="h-4 w-4" />
                    <span>{store.products} sản phẩm</span>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <button className="bg-orange-500 hover:bg-orange-600 text-white px-6 py-2 rounded-lg font-medium transition-colors flex items-center gap-2">
                    <Users className="h-4 w-4" />
                    Theo dõi
                  </button>
                  <button className="border border-gray-300 text-gray-700 px-6 py-2 rounded-lg font-medium hover:bg-gray-50 transition-colors flex items-center gap-2">
                    <MessageCircle className="h-4 w-4" />
                    Chat ngay
                  </button>
                </div>
              </div>
            </div>

            {/* Store Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 p-6 bg-gray-50 rounded-xl">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">{store.products}</div>
                <div className="text-sm text-gray-600">Sản phẩm</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">{store.responseTime}</div>
                <div className="text-sm text-gray-600">Thời gian phản hồi</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">98%</div>
                <div className="text-sm text-gray-600">Tỷ lệ phản hồi</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">4.9★</div>
                <div className="text-sm text-gray-600">Đánh giá shop</div>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 mb-8">
          <div className="flex border-b">
            {[
              { key: 'products', label: `Sản phẩm (${store.products})`, icon: Package },
              { key: 'about', label: 'Giới thiệu', icon: Eye },
              { key: 'reviews', label: `Đánh giá (${store.reviews})`, icon: Star }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key as any)}
                  className={`flex items-center gap-2 px-6 py-4 text-sm font-medium transition-colors ${
                    activeTab === tab.key 
                      ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50' 
                      : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>

          <div className="p-6">
            {activeTab === 'products' && (
              <div>
                {/* Products Header */}
                <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
                  <div className="flex items-center gap-4">
                    <div className="relative">
                      <select
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value)}
                        className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-2 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        {sortOptions.map((option) => (
                          <option key={option.value} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>
                      <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setViewMode('grid')}
                      className={`p-2 rounded-lg ${viewMode === 'grid' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'}`}
                    >
                      <Grid className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => setViewMode('list')}
                      className={`p-2 rounded-lg ${viewMode === 'list' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'}`}
                    >
                      <List className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                {/* Products Grid */}
                <div className={viewMode === 'grid' ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6' : 'space-y-4'}>
                  {storeProducts.map((product) => (
                    <div 
                      key={product.id}
                      className={`bg-white border border-gray-200 rounded-xl hover:shadow-md transition-shadow cursor-pointer ${
                        viewMode === 'list' ? 'flex gap-4 p-4' : 'overflow-hidden'
                      }`}
                      onClick={() => onNavigate?.('product-detail')}
                    >
                      <div className={viewMode === 'list' ? 'w-32 h-32 flex-shrink-0' : 'aspect-square'}>
                        <img 
                          src={product.image}
                          alt={product.name}
                          className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                        />
                      </div>

                      <div className="p-4 flex-1">
                        <h3 className="font-medium text-gray-900 mb-2 line-clamp-2">{product.name}</h3>
                        
                        <div className="flex items-center gap-2 mb-2">
                          <div className="flex text-yellow-400">
                            {[...Array(5)].map((_, i) => (
                              <Star key={i} className={`h-3 w-3 ${i < Math.floor(product.rating) ? 'fill-current' : ''}`} />
                            ))}
                          </div>
                          <span className="text-xs text-gray-500">({product.reviews})</span>
                        </div>

                        <div className="flex items-baseline gap-2 mb-3">
                          <span className="text-lg font-bold text-red-600">{formatPrice(product.price)}</span>
                          {product.originalPrice && (
                            <span className="text-sm text-gray-500 line-through">{formatPrice(product.originalPrice)}</span>
                          )}
                        </div>

                        <div className="text-xs text-gray-500 mb-3">Đã bán {product.sold}</div>

                        <button 
                          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <ShoppingCart className="h-4 w-4" />
                          Thêm vào giỏ
                        </button>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Load More */}
                <div className="text-center mt-8">
                  <button className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-8 py-3 rounded-lg font-medium transition-colors">
                    Xem thêm sản phẩm
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'about' && (
              <div className="space-y-8">
                {/* Store Description */}
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-4">Giới thiệu cửa hàng</h3>
                  <div className="prose max-w-none text-gray-700 whitespace-pre-line">
                    {store.description}
                  </div>
                </div>

                {/* Contact Info */}
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-4">Thông tin liên hệ</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div className="flex items-center gap-3">
                        <MapPin className="h-5 w-5 text-gray-500" />
                        <span>{store.location}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <Phone className="h-5 w-5 text-gray-500" />
                        <span>{store.phone}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <Mail className="h-5 w-5 text-gray-500" />
                        <span>{store.email}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <Clock className="h-5 w-5 text-gray-500" />
                        <span>Tham gia từ {new Date(store.joinDate).getFullYear()}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Policies */}
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-4">Chính sách cửa hàng</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <Shield className="h-6 w-6 text-blue-600 mb-2" />
                      <h4 className="font-medium text-gray-900 mb-2">Đổi trả</h4>
                      <p className="text-sm text-gray-700">{store.policies.return}</p>
                    </div>
                    <div className="bg-green-50 p-4 rounded-lg">
                      <Package className="h-6 w-6 text-green-600 mb-2" />
                      <h4 className="font-medium text-gray-900 mb-2">Vận chuyển</h4>
                      <p className="text-sm text-gray-700">{store.policies.shipping}</p>
                    </div>
                    <div className="bg-purple-50 p-4 rounded-lg">
                      <Award className="h-6 w-6 text-purple-600 mb-2" />
                      <h4 className="font-medium text-gray-900 mb-2">Bảo hành</h4>
                      <p className="text-sm text-gray-700">{store.policies.warranty}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'reviews' && (
              <div className="space-y-6">
                {/* Review Summary */}
                <div className="bg-gray-50 rounded-xl p-6">
                  <div className="flex items-center gap-8">
                    <div className="text-center">
                      <div className="text-4xl font-bold text-gray-900">{store.rating}</div>
                      <div className="flex text-yellow-400 justify-center mb-1">
                        {[...Array(5)].map((_, i) => (
                          <Star key={i} className={`h-5 w-5 ${i < Math.floor(store.rating) ? 'fill-current' : ''}`} />
                        ))}
                      </div>
                      <div className="text-sm text-gray-500">{store.reviews.toLocaleString()} đánh giá</div>
                    </div>
                    
                    <div className="flex-1">
                      {[5, 4, 3, 2, 1].map((stars) => {
                        const percentage = Math.random() * 100; // Mock data
                        return (
                          <div key={stars} className="flex items-center gap-3 mb-2">
                            <span className="text-sm w-8">{stars}★</span>
                            <div className="flex-1 bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-yellow-400 h-2 rounded-full"
                                style={{ width: `${percentage}%` }}
                              ></div>
                            </div>
                            <span className="text-sm text-gray-500 w-12">{Math.round(percentage)}%</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>

                {/* Individual Reviews */}
                <div className="space-y-6">
                  {storeReviews.map((review) => (
                    <div key={review.id} className="border-b pb-6">
                      <div className="flex items-start gap-4">
                        <img 
                          src={review.avatar} 
                          alt={review.user}
                          className="w-10 h-10 rounded-full object-cover"
                        />
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h5 className="font-medium">{review.user}</h5>
                            <div className="flex text-yellow-400">
                              {[...Array(5)].map((_, i) => (
                                <Star key={i} className={`h-4 w-4 ${i < review.rating ? 'fill-current' : ''}`} />
                              ))}
                            </div>
                            <span className="text-sm text-gray-500">{review.date}</span>
                          </div>
                          <p className="text-gray-700 mb-3">{review.comment}</p>
                          
                          <button className="flex items-center gap-1 text-sm text-gray-500 hover:text-blue-600 transition-colors">
                            <span>Hữu ích ({review.helpful})</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </CustomerLayout>
  );
}