import React, { useState } from 'react';
import CustomerLayout from '../../layout/CustomerLayout';
import { Filter, Grid, List, Star, Heart, ShoppingCart, ChevronDown, Tag, Sparkles, Package } from 'lucide-react';

interface CollectionsPageProps {
  onNavigate?: (page: string, data?: any) => void;
}

interface Collection {
  id: string;
  name: string;
  description: string;
  image: string;
  productCount: number;
  featured: boolean;
  season: string;
}

interface Product {
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
  collection: string;
}

export default function CollectionsPage({ onNavigate }: CollectionsPageProps) {
  const [selectedCollection, setSelectedCollection] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState('featured');

  // Mock collections data
  const collections: Collection[] = [
    {
      id: 'summer-2024',
      name: 'Summer Collection 2024',
      description: 'Bộ sưu tập mùa hè với những mẫu giày thoáng khí và năng động',
      image: '/api/placeholder/400/250',
      productCount: 24,
      featured: true,
      season: 'Hè 2024'
    },
    {
      id: 'sport-elite',
      name: 'Sport Elite Series',
      description: 'Dành cho những vận động viên chuyên nghiệp và người yêu thể thao',
      image: '/api/placeholder/400/250',
      productCount: 18,
      featured: true,
      season: 'Thường niên'
    },
    {
      id: 'classic-luxury',
      name: 'Classic Luxury',
      description: 'Những mẫu giày cổ điển sang trọng cho các dịp đặc biệt',
      image: '/api/placeholder/400/250',
      productCount: 15,
      featured: false,
      season: 'Thường niên'
    },
    {
      id: 'street-fashion',
      name: 'Street Fashion',
      description: 'Phong cách đường phố hiện đại và cá tính',
      image: '/api/placeholder/400/250',
      productCount: 32,
      featured: true,
      season: 'Thu Đông 2024'
    },
    {
      id: 'running-pro',
      name: 'Running Pro',
      description: 'Chuyên dụng cho chạy bộ với công nghệ đệm tiên tiến',
      image: '/api/placeholder/400/250',
      productCount: 20,
      featured: false,
      season: 'Thường niên'
    },
    {
      id: 'limited-edition',
      name: 'Limited Edition',
      description: 'Những mẫu giới hạn độc quyền chỉ có tại SHOEX',
      image: '/api/placeholder/400/250',
      productCount: 8,
      featured: true,
      season: 'Đặc biệt'
    }
  ];

  // Mock products data for selected collection
  const collectionProducts: Product[] = [
    {
      id: 1,
      name: 'Nike Air Max 270 Summer',
      price: 2490000,
      originalPrice: 2890000,
      brand: 'Nike',
      rating: 4.8,
      reviews: 124,
      image: '/api/placeholder/300/300',
      inStock: true,
      discount: 14,
      collection: 'summer-2024'
    },
    {
      id: 2,
      name: 'Adidas Ultraboost Elite',
      price: 3200000,
      brand: 'Adidas',
      rating: 4.9,
      reviews: 89,
      image: '/api/placeholder/300/300',
      inStock: true,
      collection: 'sport-elite'
    },
    {
      id: 3,
      name: 'Converse Limited Gold',
      price: 2800000,
      originalPrice: 3200000,
      brand: 'Converse',
      rating: 4.7,
      reviews: 67,
      image: '/api/placeholder/300/300',
      inStock: false,
      discount: 13,
      collection: 'limited-edition'
    }
  ];

  const filteredProducts = selectedCollection 
    ? collectionProducts.filter(product => product.collection === selectedCollection)
    : [];

  const handleCollectionSelect = (collectionId: string) => {
    setSelectedCollection(collectionId);
  };

  const handleBackToCollections = () => {
    setSelectedCollection(null);
  };

  // Render collection grid view
  const renderCollectionsGrid = () => (
    <div className="space-y-8">
      {/* Featured Collections */}
      <section>
        <div className="flex items-center mb-6">
          <Sparkles className="h-6 w-6 text-yellow-500 mr-2" />
          <h2 className="text-2xl font-bold text-gray-900">Bộ sưu tập nổi bật</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {collections.filter(collection => collection.featured).map((collection) => (
            <div 
              key={collection.id}
              className="bg-white rounded-2xl shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 overflow-hidden cursor-pointer group"
              onClick={() => handleCollectionSelect(collection.id)}
            >
              <div className="relative h-48">
                <img 
                  src={collection.image}
                  alt={collection.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
                <div className="absolute top-4 right-4">
                  <span className="bg-blue-600 text-white text-xs px-2 py-1 rounded-full">
                    {collection.productCount} sản phẩm
                  </span>
                </div>
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                <div className="absolute bottom-4 left-4 right-4 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <h3 className="font-bold text-lg mb-1">{collection.name}</h3>
                  <p className="text-sm text-gray-200 line-clamp-2">{collection.description}</p>
                </div>
              </div>
              <div className="p-6">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-bold text-lg text-gray-900 group-hover:text-blue-600 transition-colors">
                    {collection.name}
                  </h3>
                  <Tag className="h-4 w-4 text-gray-400" />
                </div>
                <p className="text-gray-600 text-sm mb-4 line-clamp-2">{collection.description}</p>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">{collection.season}</span>
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      handleCollectionSelect(collection.id);
                    }}
                    className="text-blue-600 hover:text-blue-800 font-medium text-sm"
                  >
                    Khám phá →
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* All Collections */}
      <section>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Tất cả bộ sưu tập</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
          {collections.map((collection) => (
            <div 
              key={collection.id}
              className="bg-white rounded-xl shadow-md border border-gray-100 hover:shadow-lg transition-all duration-300 overflow-hidden cursor-pointer group"
              onClick={() => handleCollectionSelect(collection.id)}
            >
              <div className="relative h-32">
                <img 
                  src={collection.image}
                  alt={collection.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
                <div className="absolute top-2 right-2">
                  <span className="bg-white/90 text-gray-700 text-xs px-2 py-1 rounded-full">
                    {collection.productCount}
                  </span>
                </div>
              </div>
              <div className="p-4">
                <h3 className="font-semibold text-gray-900 mb-1 line-clamp-1 group-hover:text-blue-600 transition-colors">
                  {collection.name}
                </h3>
                <p className="text-gray-500 text-xs mb-2">{collection.season}</p>
                <p className="text-gray-600 text-sm line-clamp-2">{collection.description}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );

  // Render products in selected collection
  const renderCollectionProducts = () => {
    const collection = collections.find(c => c.id === selectedCollection);
    
    return (
      <div className="space-y-6">
        {/* Collection Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white">
          <button 
            onClick={handleBackToCollections}
            className="text-white/80 hover:text-white mb-4 flex items-center"
          >
            ← Quay lại bộ sưu tập
          </button>
          <h1 className="text-3xl font-bold mb-2">{collection?.name}</h1>
          <p className="text-blue-100 mb-4">{collection?.description}</p>
          <div className="flex items-center gap-4 text-sm">
            <span className="bg-white/20 px-3 py-1 rounded-full">{collection?.season}</span>
            <span className="bg-white/20 px-3 py-1 rounded-full">{collection?.productCount} sản phẩm</span>
          </div>
        </div>

        {/* Controls */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="flex items-center gap-4">
            <span className="text-gray-600 font-medium">
              {filteredProducts.length} sản phẩm
            </span>
          </div>

          <div className="flex items-center gap-4">
            <select 
              value={sortBy} 
              onChange={(e) => setSortBy(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="featured">Nổi bật</option>
              <option value="price-low">Giá thấp đến cao</option>
              <option value="price-high">Giá cao đến thấp</option>
              <option value="rating">Đánh giá cao nhất</option>
            </select>

            <div className="flex border border-gray-300 rounded-lg overflow-hidden">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 ${viewMode === 'grid' ? 'bg-blue-50 text-blue-600' : 'text-gray-600'}`}
              >
                <Grid className="h-4 w-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 ${viewMode === 'list' ? 'bg-blue-50 text-blue-600' : 'text-gray-600'}`}
              >
                <List className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Products Grid */}
        {filteredProducts.length > 0 ? (
          <div className={viewMode === 'grid' ? 'grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6' : 'space-y-6'}>
            {filteredProducts.map(product => (
              <div 
                key={product.id} 
                className={`bg-white rounded-2xl shadow-lg border border-gray-100 hover:shadow-xl transition-shadow duration-300 overflow-hidden cursor-pointer group ${
                  viewMode === 'list' ? 'flex' : ''
                }`}
                onClick={() => onNavigate?.('product-detail', { productId: product.id })}
              >
                <div className={`relative ${viewMode === 'list' ? 'w-64 flex-shrink-0' : 'aspect-square'}`}>
                  <img 
                    src={product.image}
                    alt={product.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  {product.discount && (
                    <div className="absolute top-3 left-3">
                      <span className="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                        -{product.discount}%
                      </span>
                    </div>
                  )}
                  {!product.inStock && (
                    <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                      <span className="text-white font-medium">Hết hàng</span>
                    </div>
                  )}
                </div>

                <div className="p-6 flex-1">
                  <div className="mb-2">
                    <span className="text-xs text-gray-500 uppercase tracking-wide">{product.brand}</span>
                  </div>
                  <h3 className="font-bold text-lg text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
                    {product.name}
                  </h3>
                  
                  <div className="flex items-center mb-3">
                    <div className="flex items-center">
                      {[...Array(5)].map((_, i) => (
                        <Star 
                          key={i} 
                          className={`h-4 w-4 ${i < Math.floor(product.rating) ? 'text-yellow-400 fill-current' : 'text-gray-300'}`} 
                        />
                      ))}
                    </div>
                    <span className="text-sm text-gray-600 ml-2">({product.reviews})</span>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="text-xl font-bold text-gray-900">
                        {product.price.toLocaleString()}đ
                      </span>
                      {product.originalPrice && (
                        <span className="text-sm text-gray-500 line-through">
                          {product.originalPrice.toLocaleString()}đ
                        </span>
                      )}
                    </div>

                    <div className="flex items-center space-x-2">
                      <button className="p-2 rounded-full text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors">
                        <Heart className="h-4 w-4" />
                      </button>
                      <button 
                        className="p-2 rounded-full text-gray-400 hover:text-blue-500 hover:bg-blue-50 transition-colors"
                        disabled={!product.inStock}
                      >
                        <ShoppingCart className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Package className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-500 mb-2">Chưa có sản phẩm</h3>
            <p className="text-gray-400">Bộ sưu tập này đang được cập nhật</p>
          </div>
        )}
      </div>
    );
  };

  return (
    <CustomerLayout currentPage="collections" onNavigate={onNavigate}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        {!selectedCollection && (
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">Bộ Sưu Tập</h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Khám phá những bộ sưu tập đặc biệt được tuyển chọn kỹ lưỡng từ các thương hiệu hàng đầu thế giới
            </p>
          </div>
        )}

        {/* Content */}
        {selectedCollection ? renderCollectionProducts() : renderCollectionsGrid()}
      </div>
    </CustomerLayout>
  );
}