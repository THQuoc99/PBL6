import React, { useState } from 'react';
import CustomerLayout from '../../layout/CustomerLayout';
import { Heart, ShoppingCart, Share2, Star, Filter, Grid, List } from 'lucide-react';

interface WishlistPageProps {
  onNavigate?: (page: string, data?: any) => void;
}

interface WishlistItem {
  id: number;
  name: string;
  price: number;
  originalPrice?: number;
  brand: string;
  rating: number;
  reviews: number;
  image: string;
  inStock: boolean;
  discount?: number;
}

export default function WishlistPage({ onNavigate }: WishlistPageProps) {
  const [wishlistItems, setWishlistItems] = useState<WishlistItem[]>([
    {
      id: 1,
      name: 'Nike Air Max 270',
      price: 2490000,
      originalPrice: 2890000,
      brand: 'Nike',
      rating: 4.5,
      reviews: 128,
      image: '/api/placeholder/300/300',
      inStock: true,
      discount: 14
    },
    {
      id: 2,
      name: 'Adidas Ultraboost 22',
      price: 3200000,
      brand: 'Adidas',
      rating: 4.8,
      reviews: 95,
      image: '/api/placeholder/300/300',
      inStock: true
    },
    {
      id: 3,
      name: 'Converse Chuck Taylor All Star',
      price: 1200000,
      originalPrice: 1500000,
      brand: 'Converse',
      rating: 4.2,
      reviews: 67,
      image: '/api/placeholder/300/300',
      inStock: false,
      discount: 20
    },
    {
      id: 4,
      name: 'Vans Old Skool',
      price: 1800000,
      brand: 'Vans',
      rating: 4.6,
      reviews: 89,
      image: '/api/placeholder/300/300',
      inStock: true
    },
    {
      id: 5,
      name: 'Puma RS-X',
      price: 2200000,
      originalPrice: 2800000,
      brand: 'Puma',
      rating: 4.3,
      reviews: 45,
      image: '/api/placeholder/300/300',
      inStock: true,
      discount: 21
    }
  ]);

  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState('newest');

  const removeFromWishlist = (id: number) => {
    setWishlistItems(items => items.filter(item => item.id !== id));
  };

  const addToCart = (item: WishlistItem) => {
    alert(`Đã thêm "${item.name}" vào giỏ hàng!`);
  };

  const moveAllToCart = () => {
    const inStockItems = wishlistItems.filter(item => item.inStock);
    if (inStockItems.length > 0) {
      alert(`Đã thêm ${inStockItems.length} sản phẩm vào giỏ hàng!`);
    }
  };

  const shareWishlist = () => {
    alert('Đã sao chép link danh sách yêu thích!');
  };

  return (
    <CustomerLayout currentPage="wishlist" onNavigate={onNavigate}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
          <div className="flex items-center mb-4 sm:mb-0">
            <Heart className="h-8 w-8 text-red-500 mr-3" />
            <h1 className="text-3xl font-bold text-gray-900">
              Danh Sách Yêu Thích ({wishlistItems.length})
            </h1>
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={shareWishlist}
              className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Share2 className="h-4 w-4" />
              <span>Chia sẻ</span>
            </button>
            
            {wishlistItems.filter(item => item.inStock).length > 0 && (
              <button
                onClick={moveAllToCart}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Thêm tất cả vào giỏ
              </button>
            )}
          </div>
        </div>

        {wishlistItems.length === 0 ? (
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <Heart className="h-24 w-24 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-medium text-gray-500 mb-2">Danh sách yêu thích trống</h3>
            <p className="text-gray-400 mb-6">Lưu những sản phẩm yêu thích để mua sau</p>
            <button 
              onClick={() => onNavigate?.('customer-products')}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Khám Phá Sản Phẩm
            </button>
          </div>
        ) : (
          <>
            {/* Controls */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 bg-white rounded-lg shadow-sm p-4">
              <div className="flex items-center space-x-4 mb-4 sm:mb-0">
                <div className="flex items-center space-x-2">
                  <Filter className="h-4 w-4 text-gray-500" />
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="newest">Mới nhất</option>
                    <option value="price-low">Giá thấp → cao</option>
                    <option value="price-high">Giá cao → thấp</option>
                    <option value="rating">Đánh giá cao nhất</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded-md ${viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:text-gray-600'}`}
                >
                  <Grid className="h-4 w-4" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded-md ${viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:text-gray-600'}`}
                >
                  <List className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* Products Grid/List */}
            <div className={viewMode === 'grid' ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6' : 'space-y-4'}>
              {wishlistItems.map((item) => (
                <div key={item.id} className={`bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow ${viewMode === 'list' ? 'flex' : ''}`}>
                  {/* Product Image */}
                  <div className={`relative ${viewMode === 'list' ? 'w-48 flex-shrink-0' : 'aspect-square'}`}>
                    <div className="w-full h-full bg-gray-200 flex items-center justify-center">
                      <span className="text-gray-500">Image</span>
                    </div>
                    
                    {/* Discount Badge */}
                    {item.discount && (
                      <div className="absolute top-3 left-3 bg-red-500 text-white px-2 py-1 rounded-md text-sm font-bold">
                        -{item.discount}%
                      </div>
                    )}
                    
                    {/* Stock Status */}
                    {!item.inStock && (
                      <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                        <span className="text-white font-bold">Hết hàng</span>
                      </div>
                    )}
                    
                    {/* Remove from Wishlist */}
                    <button
                      onClick={() => removeFromWishlist(item.id)}
                      className="absolute top-3 right-3 w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-md hover:bg-gray-100 transition-colors"
                    >
                      <Heart className="h-4 w-4 text-red-500 fill-current" />
                    </button>
                  </div>

                  {/* Product Info */}
                  <div className="p-4 flex-1">
                    <div className="mb-2">
                      <p className="text-sm text-gray-500">{item.brand}</p>
                      <h3 className="font-bold text-lg text-gray-900 line-clamp-2">{item.name}</h3>
                    </div>

                    {/* Rating */}
                    <div className="flex items-center mb-3">
                      <div className="flex items-center">
                        {[...Array(5)].map((_, i) => (
                          <Star
                            key={i}
                            className={`h-4 w-4 ${i < Math.floor(item.rating) ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
                          />
                        ))}
                      </div>
                      <span className="text-sm text-gray-500 ml-2">
                        {item.rating} ({item.reviews} đánh giá)
                      </span>
                    </div>

                    {/* Price */}
                    <div className="flex items-center space-x-2 mb-4">
                      <span className="text-xl font-bold text-gray-900">
                        {item.price.toLocaleString()}đ
                      </span>
                      {item.originalPrice && (
                        <span className="text-sm text-gray-500 line-through">
                          {item.originalPrice.toLocaleString()}đ
                        </span>
                      )}
                    </div>

                    {/* Actions */}
                    <div className={`${viewMode === 'list' ? 'flex space-x-3' : 'space-y-2'}`}>
                      <button
                        onClick={() => addToCart(item)}
                        disabled={!item.inStock}
                        className={`${viewMode === 'list' ? 'flex-1' : 'w-full'} bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center`}
                      >
                        <ShoppingCart className="h-4 w-4 mr-2" />
                        {item.inStock ? 'Thêm vào giỏ' : 'Hết hàng'}
                      </button>
                      
                      <button className={`${viewMode === 'list' ? 'px-4' : 'w-full'} border border-gray-300 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-50 transition-colors`}>
                        Xem chi tiết
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Recommendations */}
            <div className="mt-12 bg-gray-50 rounded-2xl p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
                💡 Có thể bạn cũng thích
              </h2>
              <div className="text-center">
                <p className="text-gray-600 mb-4">
                  Khám phá thêm những sản phẩm tương tự dành cho bạn
                </p>
                <button 
                  onClick={() => onNavigate?.('customer-products')}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Xem Thêm Sản Phẩm
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </CustomerLayout>
  );
}