import React, { useState, useEffect } from 'react';
import CustomerLayout from '../../layout/CustomerLayout';
import { 
  Star, Heart, ShoppingCart, Share2, ChevronLeft, ChevronRight, 
  Plus, Minus, Truck, Shield, RotateCcw, Award, MapPin, Clock,
  User, ThumbsUp, MessageCircle, Store, Eye
} from 'lucide-react';

interface ProductDetailPageProps {
  onNavigate?: (page: string) => void;
  productId?: string;
}

interface ProductColor {
  id: string;
  name: string;
  hex: string;
  image: string;
}

interface ProductSize {
  id: string;
  size: string;
  stock: number;
}

interface Review {
  id: string;
  user: string;
  avatar: string;
  rating: number;
  date: string;
  comment: string;
  images?: string[];
  helpful: number;
}

interface Store {
  id: string;
  name: string;
  avatar: string;
  rating: number;
  followers: number;
  products: number;
  responseTime: string;
  isVerified: boolean;
}

interface Product {
  id: string;
  name: string;
  price: number;
  originalPrice?: number;
  rating: number;
  reviews: number;
  sold: number;
  description: string;
  features: string[];
  images: string[];
  colors: ProductColor[];
  sizes: ProductSize[];
  status: 'in-stock' | 'low-stock' | 'out-of-stock';
  category: string;
  brand: string;
  store: Store;
  tags: string[];
}

export default function ProductDetailPage({ onNavigate, productId = '1' }: ProductDetailPageProps) {
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [selectedColor, setSelectedColor] = useState<string>('');
  const [selectedSize, setSelectedSize] = useState<string>('');
  const [quantity, setQuantity] = useState(1);
  const [isWishlisted, setIsWishlisted] = useState(false);
  const [activeTab, setActiveTab] = useState<'description' | 'reviews' | 'shipping'>('description');

  // Scroll to top when component mounts
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  // Mock product data
  const product: Product = {
    id: '1',
    name: 'Nike Air Max 270 Premium',
    price: 2500000,
    originalPrice: 3000000,
    rating: 4.8,
    reviews: 124,
    sold: 1200,
    description: `Nike Air Max 270 Premium mang đến sự thoải mái tối ưu với công nghệ đệm khí Max Air đặt ở gót chân. 
    
Thiết kế hiện đại kết hợp với chất liệu cao cấp, mang lại trải nghiệm tuyệt vời cho mọi hoạt động hàng ngày.

Đặc điểm nổi bật:
• Công nghệ Max Air cushioning
• Upper mesh thoáng khí
• Đế ngoài cao su bền bỉ
• Phù hợp cho chạy bộ và tập gym`,
    features: [
      'Công nghệ Max Air đệm khí',
      'Chất liệu mesh thoáng khí',
      'Đế cao su chống mài mòn',
      'Thiết kế thời trang',
      'Phù hợp mọi hoạt động'
    ],
    images: [
      'https://static.fbshop.vn/wp-content/uploads/2023/12/Giay-Nike-Air-Max-270-Black-White-ad.gif',
      'https://static.fbshop.vn/wp-content/uploads/2023/12/Giay-Nike-Air-Max-270-Black-White-ds.gif',
      'https://cdn-images.farfetch-contents.com/12/83/31/75/12833175_21352546_1000.jpg',
      'https://cdn-images.farfetch-contents.com/12/83/31/75/12833175_21352546_1000.jpg',
      'https://cdn-images.farfetch-contents.com/12/83/31/75/12833175_21352546_1000.jpg'
    ],
    colors: [
      { id: 'black', name: 'Đen', hex: '#000000', image: '' },
      { id: 'white', name: 'Trắng', hex: '#FFFFFF', image: 'https://cdn-images.farfetch-contents.com/12/83/31/75/12833175_21352546_1000.jpg' },
      { id: 'red', name: 'Đỏ', hex: '#FF0000', image: 'https://static.fbshop.vn/wp-content/uploads/2023/12/Giay-Nike-Air-Max-270-Red-White-ds.gif' },
      { id: 'blue', name: 'Xanh', hex: '#0074D9', image: 'https://static.fbshop.vn/wp-content/uploads/2023/12/Giay-Nike-Air-Max-270-Blue-White-ds.gif' }
    ],
    sizes: [
      { id: '38', size: '38', stock: 5 },
      { id: '39', size: '39', stock: 12 },
      { id: '40', size: '40', stock: 8 },
      { id: '41', size: '41', stock: 15 },
      { id: '42', size: '42', stock: 3 },
      { id: '43', size: '43', stock: 0 },
      { id: '44', size: '44', stock: 7 }
    ],
    status: 'in-stock',
    category: 'Giày thể thao',
    brand: 'Nike',
    store: {
      id: 'store1',
      name: 'SHOEX Official Store',
      avatar: 'https://static.fbshop.vn/wp-content/uploads/2023/12/Giay-Nike-Air-Max-270-Black-White-ad.gif',
      rating: 4.9,
      followers: 125000,
      products: 1250,
      responseTime: '1 giờ',
      isVerified: true
    },
    tags: ['Nike', 'Air Max', 'Thể thao', 'Sneakers', 'Nam', 'Nữ']
  };

  // Mock reviews
  const reviews: Review[] = [
    {
      id: '1',
      user: 'Nguyễn Văn A',
      avatar: '/api/placeholder/40/40',
      rating: 5,
      date: '2024-11-10',
      comment: 'Giày rất đẹp và thoải mái! Chất lượng tuyệt vời, đáng tiền. Mình đã mua 3 đôi rồi.',
      images: ['/api/placeholder/100/100', '/api/placeholder/100/100'],
      helpful: 23
    },
    {
      id: '2',
      user: 'Trần Thị B',
      avatar: '/api/placeholder/40/40',
      rating: 4,
      date: '2024-11-08',
      comment: 'Giày đẹp nhưng hơi chật. Nên chọn size lớn hơn 1 size.',
      helpful: 15
    },
    {
      id: '3',
      user: 'Lê Minh C',
      avatar: '/api/placeholder/40/40',
      rating: 5,
      date: '2024-11-05',
      comment: 'Perfect! Đúng như mô tả, giao hàng nhanh.',
      helpful: 8
    }
  ];

  // Mock related products
  const relatedProducts = [
    {
      id: '2',
      name: 'Adidas Ultraboost 22',
      price: 2800000,
      rating: 4.9,
      image: '/api/placeholder/200/200'
    },
    {
      id: '3',
      name: 'Puma RS-X',
      price: 2200000,
      rating: 4.7,
      image: '/api/placeholder/200/200'
    },
    {
      id: '4',
      name: 'Vans Old Skool',
      price: 1800000,
      rating: 4.6,
      image: '/api/placeholder/200/200'
    },
    {
      id: '5',
      name: 'Converse Chuck Taylor',
      price: 1200000,
      rating: 4.5,
      image: '/api/placeholder/200/200'
    }
  ];

  React.useEffect(() => {
    if (product.colors.length > 0) {
      setSelectedColor(product.colors[0].id);
    }
  }, []);

  const getStatusBadge = () => {
    switch (product.status) {
      case 'in-stock':
        return <span className="bg-green-100 text-green-800 text-sm font-medium px-2 py-1 rounded">Còn hàng</span>;
      case 'low-stock':
        return <span className="bg-yellow-100 text-yellow-800 text-sm font-medium px-2 py-1 rounded">Sắp hết</span>;
      case 'out-of-stock':
        return <span className="bg-red-100 text-red-800 text-sm font-medium px-2 py-1 rounded">Hết hàng</span>;
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(price);
  };

  const handleAddToCart = () => {
    if (!selectedSize) {
      alert('Vui lòng chọn size!');
      return;
    }
    alert(`Đã thêm ${quantity} sản phẩm vào giỏ hàng!`);
  };

  const handleBuyNow = () => {
    if (!selectedSize) {
      alert('Vui lòng chọn size!');
      return;
    }
    alert('Chuyển đến trang thanh toán!');
  };

  return (
    <CustomerLayout onNavigate={onNavigate}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumb */}
        <nav className="flex mb-6 text-sm">
          <button 
            onClick={() => onNavigate?.('home')}
            className="text-gray-500 hover:text-gray-700 transition-colors"
          >
            Trang chủ
          </button>
          <span className="mx-2 text-gray-500">/</span>
          <button 
            onClick={() => onNavigate?.('products')}
            className="text-gray-500 hover:text-gray-700 transition-colors"
          >
            {product.category}
          </button>
          <span className="mx-2 text-gray-500">/</span>
          <span className="text-gray-900">{product.name}</span>
        </nav>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-12">
          {/* Product Images */}
          <div className="space-y-4">
            {/* Main Image */}
            <div className="relative bg-gray-100 rounded-lg overflow-hidden aspect-square">
              <img 
                src={selectedColor && product.colors.find(c => c.id === selectedColor)?.image || product.images[selectedImageIndex]}
                alt={product.name}
                className="w-full h-full object-cover"
              />
              {/* Navigation Arrows */}
              <button 
                onClick={() => {
                  setSelectedImageIndex(Math.max(0, selectedImageIndex - 1));
                  if (selectedColor) setSelectedColor('');
                }}
                className="absolute left-4 top-1/2 -translate-y-1/2 bg-white/80 hover:bg-white p-2 rounded-full shadow-lg transition-colors"
                disabled={selectedImageIndex === 0}
              >
                <ChevronLeft className="h-5 w-5" />
              </button>
              <button 
                onClick={() => {
                  setSelectedImageIndex(Math.min(product.images.length - 1, selectedImageIndex + 1));
                  if (selectedColor) setSelectedColor('');
                }}
                className="absolute right-4 top-1/2 -translate-y-1/2 bg-white/80 hover:bg-white p-2 rounded-full shadow-lg transition-colors"
                disabled={selectedImageIndex === product.images.length - 1}
              >
                <ChevronRight className="h-5 w-5" />
              </button>
              {/* Wishlist Button */}
              <button 
                onClick={() => setIsWishlisted(!isWishlisted)}
                className="absolute top-4 right-4 bg-white/80 hover:bg-white p-2 rounded-full shadow-lg transition-colors"
              >
                <Heart className={`h-5 w-5 ${isWishlisted ? 'fill-red-500 text-red-500' : 'text-gray-600'}`} />
              </button>
            </div>

            {/* Thumbnail Images */}
            <div className="flex space-x-3 overflow-x-auto pb-2">
              {product.images.map((image, index) => (
                <button
                  key={index}
                  onClick={() => {
                    setSelectedImageIndex(index);
                    if (selectedColor) setSelectedColor('');
                  }}
                  className={`flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden border-2 transition-colors ${
                    selectedImageIndex === index ? 'border-blue-500' : 'border-gray-200'
                  }`}
                >
                  <img src={image} alt="" className="w-full h-full object-cover" />
                </button>
              ))}
            </div>
          </div>

          {/* Product Info */}
          <div className="space-y-6">
            {/* Title & Rating */}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-sm text-gray-500">{product.brand}</span>
                {getStatusBadge()}
              </div>
              <h1 className="text-3xl font-bold text-gray-900 mb-3">{product.name}</h1>
              
              <div className="flex items-center gap-4 mb-2">
                <div className="flex items-center">
                  <div className="flex text-yellow-400">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className={`h-5 w-5 ${i < Math.floor(product.rating) ? 'fill-current' : ''}`} />
                    ))}
                  </div>
                  <span className="ml-2 text-sm text-gray-600">
                    {product.rating} ({product.reviews} đánh giá)
                  </span>
                </div>
                <span className="text-sm text-gray-500">|</span>
                <span className="text-sm text-gray-600">Đã bán {product.sold}</span>
              </div>
            </div>

            {/* Price */}
            <div className="flex items-baseline gap-3">
              <span className="text-3xl font-bold text-red-600">{formatPrice(product.price)}</span>
              {product.originalPrice && (
                <span className="text-xl text-gray-500 line-through">{formatPrice(product.originalPrice)}</span>
              )}
              {product.originalPrice && (
                <span className="text-sm bg-red-100 text-red-800 px-2 py-1 rounded">
                  -{Math.round((1 - product.price / product.originalPrice) * 100)}%
                </span>
              )}
            </div>

            {/* Colors */}
            <div>
              <h3 className="text-sm font-medium text-gray-900 mb-3">Màu sắc: {product.colors.find(c => c.id === selectedColor)?.name}</h3>
              <div className="flex flex-wrap gap-3">
                {product.colors.map((color) => {
                  // Lấy ảnh đại diện cho màu
                  let colorImage = '';
                  if (Array.isArray((color as any).images) && (color as any).images.length > 0) {
                    colorImage = (color as any).images[0];
                  } else if (color.image) {
                    colorImage = color.image;
                  }
                  return (
                    <button
                      key={color.id}
                      onClick={() => setSelectedColor(color.id)}
                      className={`relative flex items-center justify-center w-12 h-12 rounded-lg border-2 transition-colors ${
                        selectedColor === color.id ? 'border-blue-500' : 'border-gray-200'
                      }`}
                    >
                      {colorImage ? (
                        <img src={colorImage} alt={color.name} className="w-10 h-10 object-cover rounded-lg" />
                      ) : (
                        <div className="w-10 h-10 bg-gray-200 rounded-lg"></div>
                      )}
                      {selectedColor === color.id && (
                        <div className="absolute -top-1 -right-1 w-4 h-4 bg-blue-500 rounded-full flex items-center justify-center">
                          <div className="w-2 h-2 bg-white rounded-full"></div>
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Sizes */}
            <div>
              <h3 className="text-sm font-medium text-gray-900 mb-3">Kích thước</h3>
              <div className="grid grid-cols-4 gap-3">
                {product.sizes.map((size) => (
                  <button
                    key={size.id}
                    onClick={() => size.stock > 0 && setSelectedSize(size.id)}
                    disabled={size.stock === 0}
                    className={`relative px-2 py-1 text-center border rounded-md transition-colors text-sm min-w-[36px] h-9 flex flex-col items-center justify-center ${
                      selectedSize === size.id 
                        ? 'border-blue-500 bg-blue-50 text-blue-700' 
                        : size.stock === 0 
                          ? 'border-gray-200 bg-gray-100 text-gray-400 cursor-not-allowed'
                          : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="font-medium leading-none">{size.size}</div>
                    {size.stock <= 5 && size.stock > 0 && (
                      <div className="text-[10px] text-orange-500 leading-none">Còn {size.stock}</div>
                    )}
                    {size.stock === 0 && (
                      <div className="absolute inset-0 flex items-center justify-center bg-gray-100/75 rounded-md">
                        <span className="text-[10px] text-gray-500">Hết hàng</span>
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Quantity */}
            <div>
              <h3 className="text-sm font-medium text-gray-900 mb-3">Số lượng</h3>
              <div className="flex items-center gap-4">
                <div className="flex items-center border rounded-lg">
                  <button 
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                    className="p-2 hover:bg-gray-50 transition-colors"
                  >
                    <Minus className="h-4 w-4" />
                  </button>
                  <span className="px-4 py-2 min-w-[60px] text-center">{quantity}</span>
                  <button 
                    onClick={() => setQuantity(quantity + 1)}
                    className="p-2 hover:bg-gray-50 transition-colors"
                  >
                    <Plus className="h-4 w-4" />
                  </button>
                </div>
                <span className="text-sm text-gray-500">
                  {selectedSize && product.sizes.find(s => s.id === selectedSize)?.stock} sản phẩm có sẵn
                </span>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4">
              <button 
                onClick={handleAddToCart}
                className="flex-1 bg-orange-500 hover:bg-orange-600 text-white py-3 px-6 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
              >
                <ShoppingCart className="h-5 w-5" />
                Thêm vào giỏ hàng
              </button>
              <button 
                onClick={handleBuyNow}
                className="flex-1 bg-red-600 hover:bg-red-700 text-white py-3 px-6 rounded-lg font-medium transition-colors"
              >
                Mua ngay
              </button>
            </div>

            {/* Store Info */}
            <div className="border rounded-lg p-4 bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <img 
                    src={product.store.avatar} 
                    alt={product.store.name}
                    className="w-12 h-12 rounded-full object-cover"
                  />
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 
                        className="font-medium text-gray-900 cursor-pointer hover:text-blue-600 transition-colors"
                        onClick={() => onNavigate?.('store')}
                      >
                        {product.store.name}
                      </h4>
                      {product.store.isVerified && (
                        <Award className="h-4 w-4 text-blue-500" />
                      )}
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <span className="flex items-center gap-1">
                        <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                        {product.store.rating}
                      </span>
                      <span>{product.store.followers.toLocaleString()} người theo dõi</span>
                    </div>
                  </div>
                </div>
                <button 
                  onClick={() => onNavigate?.('store')}
                  className="flex items-center gap-2 px-4 py-2 border border-orange-500 text-orange-500 rounded-lg hover:bg-orange-50 transition-colors"
                >
                  <Store className="h-4 w-4" />
                  Xem shop
                </button>
              </div>
              
              <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t">
                <div className="text-center">
                  <div className="text-sm text-gray-500">Sản phẩm</div>
                  <div className="font-medium">{product.store.products}</div>
                </div>
                <div className="text-center">
                  <div className="text-sm text-gray-500">Tỷ lệ phản hồi</div>
                  <div className="font-medium">98%</div>
                </div>
                <div className="text-center">
                  <div className="text-sm text-gray-500">Thời gian phản hồi</div>
                  <div className="font-medium">{product.store.responseTime}</div>
                </div>
              </div>
            </div>

            {/* Features */}
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
                <Truck className="h-5 w-5 text-blue-600" />
                <span className="text-sm text-blue-700">Miễn phí vận chuyển</span>
              </div>
              <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
                <Shield className="h-5 w-5 text-green-600" />
                <span className="text-sm text-green-700">Bảo hành chính hãng</span>
              </div>
              <div className="flex items-center gap-3 p-3 bg-purple-50 rounded-lg">
                <RotateCcw className="h-5 w-5 text-purple-600" />
                <span className="text-sm text-purple-700">Đổi trả 30 ngày</span>
              </div>
              <div className="flex items-center gap-3 p-3 bg-orange-50 rounded-lg">
                <Award className="h-5 w-5 text-orange-600" />
                <span className="text-sm text-orange-700">Chính hãng 100%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Product Details Tabs */}
        <div className="bg-white rounded-lg shadow-sm border mb-12">
          {/* Tab Headers */}
          <div className="flex border-b">
            {[
              { key: 'description', label: 'Mô tả sản phẩm' },
              { key: 'reviews', label: `Đánh giá (${product.reviews})` },
              { key: 'shipping', label: 'Vận chuyển' }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`px-6 py-4 text-sm font-medium transition-colors ${
                  activeTab === tab.key 
                    ? 'text-blue-600 border-b-2 border-blue-600' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'description' && (
              <div className="prose max-w-none">
                <div className="whitespace-pre-line text-gray-700 mb-6">{product.description}</div>
                
                <h4 className="text-lg font-semibold mb-4">Tính năng nổi bật</h4>
                <ul className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {product.features.map((feature, index) => (
                    <li key={index} className="flex items-center gap-3">
                      <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {activeTab === 'reviews' && (
              <div className="space-y-6">
                {/* Review Summary */}
                <div className="flex items-center gap-8 p-6 bg-gray-50 rounded-lg">
                  <div className="text-center">
                    <div className="text-4xl font-bold text-gray-900">{product.rating}</div>
                    <div className="flex text-yellow-400 justify-center mb-1">
                      {[...Array(5)].map((_, i) => (
                        <Star key={i} className={`h-5 w-5 ${i < Math.floor(product.rating) ? 'fill-current' : ''}`} />
                      ))}
                    </div>
                    <div className="text-sm text-gray-500">{product.reviews} đánh giá</div>
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

                {/* Individual Reviews */}
                <div className="space-y-6">
                  {reviews.map((review) => (
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
                          
                          {review.images && (
                            <div className="flex gap-2 mb-3">
                              {review.images.map((image, index) => (
                                <img 
                                  key={index}
                                  src={image} 
                                  alt=""
                                  className="w-20 h-20 rounded-lg object-cover"
                                />
                              ))}
                            </div>
                          )}
                          
                          <div className="flex items-center gap-4 text-sm">
                            <button className="flex items-center gap-1 text-gray-500 hover:text-blue-600 transition-colors">
                              <ThumbsUp className="h-4 w-4" />
                              Hữu ích ({review.helpful})
                            </button>
                            <button className="flex items-center gap-1 text-gray-500 hover:text-blue-600 transition-colors">
                              <MessageCircle className="h-4 w-4" />
                              Trả lời
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'shipping' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h4 className="text-lg font-semibold">Thông tin vận chuyển</h4>
                    <div className="space-y-3">
                      <div className="flex items-center gap-3">
                        <Truck className="h-5 w-5 text-blue-600" />
                        <div>
                          <div className="font-medium">Giao hàng tiêu chuẩn</div>
                          <div className="text-sm text-gray-500">2-3 ngày làm việc</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Clock className="h-5 w-5 text-green-600" />
                        <div>
                          <div className="font-medium">Giao hàng nhanh</div>
                          <div className="text-sm text-gray-500">1-2 ngày làm việc (+30,000₫)</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <MapPin className="h-5 w-5 text-purple-600" />
                        <div>
                          <div className="font-medium">Nhận tại cửa hàng</div>
                          <div className="text-sm text-gray-500">Miễn phí</div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <h4 className="text-lg font-semibold">Chính sách đổi trả</h4>
                    <div className="space-y-3 text-sm text-gray-700">
                      <p>• Đổi trả miễn phí trong 30 ngày</p>
                      <p>• Sản phẩm còn nguyên tem, mác</p>
                      <p>• Không sử dụng hoặc có dấu hiệu sử dụng</p>
                      <p>• Đầy đủ phụ kiện và hộp đựng</p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Related Products */}
        <div>
          <h3 className="text-2xl font-bold text-gray-900 mb-6">Sản phẩm liên quan</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {relatedProducts.map((relatedProduct) => (
              <div key={relatedProduct.id} className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow cursor-pointer">
                <div className="aspect-square bg-gray-100 rounded-t-lg overflow-hidden">
                  <img 
                    src={relatedProduct.image} 
                    alt={relatedProduct.name}
                    className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                  />
                </div>
                <div className="p-4">
                  <h4 className="font-medium text-gray-900 mb-2 line-clamp-2">{relatedProduct.name}</h4>
                  <div className="flex items-center gap-2 mb-2">
                    <div className="flex text-yellow-400">
                      {[...Array(5)].map((_, i) => (
                        <Star key={i} className={`h-3 w-3 ${i < Math.floor(relatedProduct.rating) ? 'fill-current' : ''}`} />
                      ))}
                    </div>
                    <span className="text-xs text-gray-500">({relatedProduct.rating})</span>
                  </div>
                  <div className="text-lg font-bold text-red-600">{formatPrice(relatedProduct.price)}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </CustomerLayout>
  );
}