import React, { useState } from 'react';
import CustomerLayout from '../../layout/CustomerLayout';
import { Star, Heart, ShoppingCart, ArrowRight, Truck, Shield, Headphones, RotateCcw } from 'lucide-react';
import { useProducts } from '../../../hooks/product/products';
import { useCart } from '../../../hooks/cart/cart';
import { useAuth } from '../../../hooks/user/useAuth';
import { useNavigate } from 'react-router-dom';

interface CustomerHomePageProps {
  onNavigateToSeller?: () => void;
  onNavigate?: (page: string, data?: any) => void;
}

export default function CustomerHomePage({ onNavigateToSeller, onNavigate }: CustomerHomePageProps) {
    const navigate = useNavigate();
    const { addToCart, loading: cartLoading } = useCart();
    const { isAuthenticated } = useAuth();
    const [categoryScroll, setCategoryScroll] = useState(0);
    const categoryRef = React.useRef<HTMLDivElement>(null);
    const visibleCount = 4; // số lượng hiển thị trên màn hình

    const handleScrollCategory = (direction: 'left' | 'right') => {
      if (!categoryRef.current) return;
      const cardWidth = categoryRef.current.firstChild instanceof HTMLElement ? categoryRef.current.firstChild.offsetWidth : 0;
      const scrollAmount = cardWidth * visibleCount;
      if (direction === 'left') {
        categoryRef.current.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
        setCategoryScroll((prev) => Math.max(prev - visibleCount, 0));
      } else {
        categoryRef.current.scrollBy({ left: scrollAmount, behavior: 'smooth' });
        setCategoryScroll((prev) => prev + visibleCount);
      }
    };
  const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
  const [wishlist, setWishlist] = useState<string[]>([]);

  const toggleWishlist = (productId: string) => {
    setWishlist(prev => 
      prev.includes(productId) 
        ? prev.filter(id => id !== productId)
        : [...prev, productId]
    );
  };

  // Quick add to cart handler
  const handleQuickAddToCart = async (e: React.MouseEvent, product: any) => {
    e.stopPropagation(); // Prevent navigation to product detail
    
    if (!isAuthenticated) {
      alert('Vui lòng đăng nhập để thêm vào giỏ hàng!');
      navigate('/login');
      return;
    }

    // Get first available variant
    if (!product.variants?.edges || product.variants.edges.length === 0) {
      alert('Sản phẩm này hiện không có sẵn!');
      return;
    }

    const firstVariant = product.variants.edges[0].node;
    
    if (!firstVariant.isInStock || firstVariant.stock === 0) {
      alert('Sản phẩm này đã hết hàng!');
      return;
    }

    const result = await addToCart(firstVariant.variantId, 1);
    
    if (result.success) {
      alert('Đã thêm vào giỏ hàng!');
    } else {
      alert(result.errors?.[0] || 'Có lỗi xảy ra!');
    }
  };

  // Lấy 4 sản phẩm nổi bật
  const { products: featuredProducts, loading: loadingFeatured } = useProducts(
    { isNew: true  },
    undefined,
    { first: 4 }
  );

  const categories = [
    { id: '1', name: 'Giày thể thao', icon: '👟', count: 150 },
    { id: '2', name: 'Giày da', icon: '👞', count: 87 },
    { id: '3', name: 'Dép sandal', icon: '👡', count: 64 },
    { id: '4', name: 'Giày boot', icon: '🥾', count: 42 },
    { id: '5', name: 'Giày thể thao', icon: '👟', count: 150 },
    { id: '6', name: 'Giày da', icon: '👞', count: 87 },
    { id: '7', name: 'Dép sandal', icon: '👡', count: 64 },
    { id: '8', name: 'Giày boot', icon: '🥾', count: 42 }
  ];

  const services = [
    {
      icon: <Truck className="h-8 w-8 text-blue-600" />,
      title: 'Miễn phí vận chuyển',
      description: 'Đơn hàng từ 500k'
    },
    {
      icon: <Shield className="h-8 w-8 text-green-600" />,
      title: 'Bảo hành 1 năm',
      description: 'Đổi trả trong 30 ngày'
    },
    {
      icon: <Headphones className="h-8 w-8 text-purple-600" />,
      title: 'Hỗ trợ 24/7',
      description: 'Tư vấn miễn phí'
    },
    {
      icon: <RotateCcw className="h-8 w-8 text-orange-600" />,
      title: 'Đổi trả dễ dàng',
      description: 'Không cần lý do'
    }
  ];

  return (
    <CustomerLayout currentPage="home" onNavigate={onNavigate}>
      {/* Hero Banner */}
      <section className="relative bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-4xl lg:text-6xl font-bold mb-6">
                Khám phá<br />
                <span className="text-yellow-300">Bộ sưu tập</span><br />
                mới nhất
              </h1>
              <p className="text-xl text-blue-100 mb-8">
                Hơn 1000+ mẫu giày chính hãng từ các thương hiệu hàng đầu thế giới
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <button 
                  onClick={() => onNavigate?.('customer-products')}
                  className="bg-white text-blue-600 font-semibold py-3 px-8 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  Mua ngay
                </button>
                <button 
                  onClick={() => onNavigate?.('collections')}
                  className="border-2 border-white text-white font-semibold py-3 px-8 rounded-lg hover:bg-white hover:text-blue-600 transition-colors"
                >
                  Xem bộ sưu tập
                </button>
              </div>
            </div>
            <div className="relative">
              <div className="w-full h-96 bg-white/10 rounded-3xl backdrop-blur-sm border border-white/20"></div>
            </div>
          </div>
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Services */}
        <section className="py-16">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {services.map((service, index) => (
              <div key={index} className="text-center p-6 bg-white rounded-2xl shadow-lg border border-gray-100">
                <div className="flex justify-center mb-4">
                  {service.icon}
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">{service.title}</h3>
                <p className="text-gray-600 text-sm">{service.description}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Categories - Horizontal scroll with arrows */}
        <section className="py-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Danh mục sản phẩm</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Tìm kiếm theo từng danh mục để dễ dàng tìm được sản phẩm phù hợp
            </p>
          </div>
          <div className="relative">
            {categories.length > visibleCount && (
              <button
                className="absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-white border border-gray-300 rounded-full shadow p-2 hover:bg-blue-100"
                style={{ marginLeft: '-32px' }}
                onClick={() => handleScrollCategory('left')}
                aria-label="Xem trái"
              >
                <ArrowRight className="h-5 w-5 rotate-180 text-blue-600" />
              </button>
            )}
            <div
              ref={categoryRef}
              className="flex gap-6 overflow-x-auto scrollbar-hide px-1"
              style={{ scrollBehavior: 'smooth' }}
            >
              {categories.map((category) => (
                <div
                  key={category.id}
                  className="group min-w-[220px] p-8 bg-white rounded-2xl shadow-lg border border-gray-100 hover:shadow-xl hover:border-blue-200 transition-all cursor-pointer"
                >
                  <div className="text-center">
                    <div className="text-4xl mb-4">{category.icon}</div>
                    <h3 className="font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
                      {category.name}
                    </h3>
                    <p className="text-gray-500 text-sm">{category.count} sản phẩm</p>
                  </div>
                </div>
              ))}
            </div>
            {categories.length > visibleCount && (
              <button
                className="absolute right-0 top-1/2 -translate-y-1/2 z-10 bg-white border border-gray-300 rounded-full shadow p-2 hover:bg-blue-100"
                style={{ marginRight: '-32px' }}
                onClick={() => handleScrollCategory('right')}
                aria-label="Xem phải"
              >
                <ArrowRight className="h-5 w-5 text-blue-600" />
              </button>
            )}
          </div>
        </section>

        {/* Featured Products */}
        <section className="py-16">
          <div className="flex justify-between items-center mb-12">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Sản phẩm nổi bật</h2>
              <p className="text-gray-600">Những sản phẩm được yêu thích nhất</p>
            </div>
            <button className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 font-medium">
              <span>Xem tất cả</span>
              <ArrowRight className="h-5 w-5" />
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {loadingFeatured ? (
              <div className="col-span-4 text-center py-12 text-gray-500">Đang tải sản phẩm nổi bật...</div>
            ) : featuredProducts.length === 0 ? (
              <div className="col-span-4 text-center py-12 text-gray-500">Không có sản phẩm nổi bật.</div>
            ) : (
              featuredProducts.map((product: any) => (
                <div
                  key={product.productId}
                  className="group bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden hover:shadow-xl transition-all cursor-pointer flex flex-col"
                  style={{ minHeight: '420px' }}
                  onClick={() => onNavigate?.('product-detail', { id: product.productId })}
                >
                  {/* Product Image */}
                  <div className="relative p-6 bg-gray-50" style={{ minHeight: '220px' }}>
                    {product.isNew && (
                      <span className="absolute top-3 left-3 bg-green-500 text-white text-xs font-medium px-2 py-1 rounded-full">
                        Mới
                      </span>
                    )}
                    {product.isHot && (
                      <span className="absolute top-3 left-3 bg-red-500 text-white text-xs font-medium px-2 py-1 rounded-full">
                        Hot
                      </span>
                    )}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleWishlist(product.productId);
                      }}
                      className="absolute top-3 right-3 p-2 rounded-full bg-white shadow-md hover:bg-gray-50 transition-colors"
                    >
                      <Heart
                        className={`h-5 w-5 ${
                          wishlist.includes(product.productId)
                            ? 'text-red-500 fill-current'
                            : 'text-gray-400'
                        }`}
                      />
                    </button>
                    <div className="w-full h-48 bg-gray-200 rounded-lg mb-4 flex items-center justify-center">
                      {product.thumbnailImage?.imageUrl ? (
                        <img src={product.thumbnailImage.imageUrl} alt={product.name} />
                      ) : null}
                    </div>
                  </div>

                  {/* Product Info */}
                  <div className="p-6 flex flex-col flex-1 justify-between" style={{ minHeight: '180px' }}>
                    <div>
                      <div className="text-sm text-gray-500 mb-2">{product.category?.name}</div>
                      <h3
                        className="font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors line-clamp-2"
                        style={{
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden',
                          minHeight: '2.5em',
                        }}
                      >
                        {product.name}
                      </h3>
                      {/* Rating */}
                      <div className="flex items-center space-x-2 mb-3">
                        <div className="flex items-center">
                          {[...Array(5)].map((_, i) => (
                            <Star
                              key={i}
                              className={`h-4 w-4 ${
                                i < Math.floor(product.ratingAverage || 0)
                                  ? 'text-yellow-400 fill-current'
                                  : 'text-gray-300'
                              }`}
                            />
                          ))}
                        </div>
                        <span className="text-sm text-gray-500">({product.reviewCount || 0})</span>
                      </div>
                      {/* Price */}
                      <div className="flex items-center space-x-2 mb-4">
                        <span className="text-lg font-bold text-gray-900">
                          {(product.finalPrice || product.basePrice || 0).toLocaleString('vi-VN')}₫
                        </span>
                        {product.hasDiscount && product.basePrice && (
                          <span className="text-sm text-gray-500 line-through">
                            {product.basePrice.toLocaleString('vi-VN')}₫
                          </span>
                        )}
                      </div>
                    </div>
                    {/* Add to Cart */}
                    <button
                      onClick={(e) => handleQuickAddToCart(e, product)}
                      disabled={cartLoading}
                      className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2 disabled:bg-gray-300 disabled:cursor-not-allowed"
                    >
                      <ShoppingCart className="h-4 w-4" />
                      <span>{cartLoading ? 'Đang thêm...' : 'Thêm vào giỏ'}</span>
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </section>

        {/* Newsletter */}
        <section className="py-16">
          <div className="bg-gray-900 rounded-3xl p-12 text-center text-white">
            <h2 className="text-3xl font-bold mb-4">Đăng ký nhận tin</h2>
            <p className="text-gray-300 mb-8 max-w-2xl mx-auto">
              Nhận thông tin về sản phẩm mới, khuyến mãi đặc biệt và các xu hướng thời trang mới nhất
            </p>
            <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
              <input
                type="email"
                placeholder="Nhập email của bạn"
                className="flex-1 px-4 py-3 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium">
                Đăng ký
              </button>
            </div>
          </div>
        </section>
      </div>
    </CustomerLayout>
  );
}