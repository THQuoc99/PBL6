import React, { useState } from 'react';
import CustomerLayout from '../../layout/CustomerLayout';
import { Filter, Grid, List, Star, Heart, ShoppingCart, ChevronDown } from 'lucide-react';

interface CustomerProductsPageProps {
  onNavigateToSeller?: () => void;
  onNavigate?: (page: string, data?: any) => void;
}

export default function CustomerProductsPage({ onNavigateToSeller, onNavigate }: CustomerProductsPageProps) {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState('popular');
  const [priceRange, setPriceRange] = useState([0, 5000000]);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedBrands, setSelectedBrands] = useState<string[]>([]);
  const [showFilters, setShowFilters] = useState(false);

  // Mock data
  const products = [
    {
      id: '1',
      name: 'Nike Air Max 270',
      brand: 'Nike',
      category: 'Giày thể thao',
      price: 2500000,
      originalPrice: 3000000,
      rating: 4.8,
      reviews: 124,
      image: 'https://static.fbshop.vn/wp-content/uploads/2023/12/Giay-Nike-Air-Max-270-Black-White-ad.gif',
      colors: ['Đen', 'Trắng', 'Xanh'],
      sizes: [39, 40, 41, 42, 43],
      isNew: true,
      discount: 17
    },
    {
      id: '2',
      name: 'Adidas Ultraboost 22',
      brand: 'Adidas',
      category: 'Giày chạy bộ',
      price: 2800000,
      rating: 4.9,
      reviews: 89,
      image: 'https://bizweb.dktcdn.net/thumb/small/100/347/092/products/gx5915-s1.jpg?v=1666974717997',
      colors: ['Trắng', 'Đen'],
      sizes: [40, 41, 42, 43, 44],
      isHot: true
    },
    {
      id: '3',
      name: 'Converse Chuck Taylor',
      brand: 'Converse',
      category: 'Giày thường',
      price: 1200000,
      rating: 4.6,
      reviews: 256,
      image: 'https://product.hstatic.net/1000387035/product/113_eea5f17eb29b4bd78c5c89e40f45da50_grande.png',
      colors: ['Đen', 'Trắng', 'Đỏ', 'Xanh'],
      sizes: [38, 39, 40, 41, 42]
    },
    {
      id: '4',
      name: 'Vans Old Skool',
      brand: 'Vans',
      category: 'Giày skate',
      price: 1500000,
      originalPrice: 1800000,
      rating: 4.7,
      reviews: 178,
      image: '/api/placeholder/300/300',
      colors: ['Đen/Trắng', 'Xanh navy'],
      sizes: [39, 40, 41, 42, 43],
      discount: 17
    }
  ];

  const categories = [
    { id: 'sport', name: 'Giày thể thao', count: 150 },
    { id: 'casual', name: 'Giày thường', count: 87 },
    { id: 'running', name: 'Giày chạy bộ', count: 64 },
    { id: 'skateboard', name: 'Giày skate', count: 42 },
    { id: 'boot', name: 'Giày boot', count: 35 }
  ];

  const brands = [
    { id: 'nike', name: 'Nike', count: 120 },
    { id: 'adidas', name: 'Adidas', count: 98 },
    { id: 'vans', name: 'Vans', count: 67 },
    { id: 'converse', name: 'Converse', count: 54 },
    { id: 'puma', name: 'Puma', count: 43 }
  ];

  const sortOptions = [
    { value: 'popular', label: 'Phổ biến nhất' },
    { value: 'newest', label: 'Mới nhất' },
    { value: 'price-low', label: 'Giá: Thấp đến Cao' },
    { value: 'price-high', label: 'Giá: Cao đến Thấp' },
    { value: 'rating', label: 'Đánh giá cao nhất' }
  ];

  const toggleCategory = (categoryId: string) => {
    setSelectedCategories(prev =>
      prev.includes(categoryId)
        ? prev.filter(id => id !== categoryId)
        : [...prev, categoryId]
    );
  };

  const toggleBrand = (brandId: string) => {
    setSelectedBrands(prev =>
      prev.includes(brandId)
        ? prev.filter(id => id !== brandId)
        : [...prev, brandId]
    );
  };

  const ProductCard = ({ product, isListView }: { product: any; isListView: boolean }) => (
    <div className={`group bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden hover:shadow-xl transition-all ${isListView ? 'flex' : ''}`}>
      {/* Product Image */}
      <div className={`relative bg-gray-50 ${isListView ? 'w-64 flex-shrink-0' : 'p-6'}`}>
        {product.isNew && (
          <span className="absolute top-3 left-3 bg-green-500 text-white text-xs font-medium px-2 py-1 rounded-full z-10">
            Mới
          </span>
        )}
        {product.isHot && (
          <span className="absolute top-3 left-3 bg-red-500 text-white text-xs font-medium px-2 py-1 rounded-full z-10">
            Hot
          </span>
        )}
        {product.discount && (
          <span className="absolute top-3 right-3 bg-orange-500 text-white text-xs font-medium px-2 py-1 rounded-full z-10">
            -{product.discount}%
          </span>
        )}
        <button className="absolute top-3 right-3 p-2 rounded-full bg-white shadow-md hover:bg-gray-50 transition-colors z-10">
          <Heart className="h-5 w-5 text-gray-400" />
        </button>
        
        <div className={`w-full bg-gray-200 rounded-lg ${isListView ? 'h-full' : 'h-48 mb-4'}`}></div>
      </div>

      {/* Product Info */}
      <div className={`p-6 ${isListView ? 'flex-1' : ''}`}>
        <div className="text-sm text-gray-500 mb-2">{product.category}</div>
        <h3 className="font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
          {product.name}
        </h3>
        <div className="text-sm text-gray-600 mb-3">{product.brand}</div>
        
        {/* Rating */}
        <div className="flex items-center space-x-2 mb-3">
          <div className="flex items-center">
            {[...Array(5)].map((_, i) => (
              <Star 
                key={i} 
                className={`h-4 w-4 ${
                  i < Math.floor(product.rating) 
                    ? 'text-yellow-400 fill-current' 
                    : 'text-gray-300'
                }`} 
              />
            ))}
          </div>
          <span className="text-sm text-gray-500">({product.reviews})</span>
        </div>

        {/* Colors & Sizes */}
        <div className="mb-4 space-y-2">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">Màu:</span>
            <div className="flex space-x-1">
              {product.colors.slice(0, 3).map((color: string, index: number) => (
                <span key={index} className="text-xs bg-gray-100 px-2 py-1 rounded">
                  {color}
                </span>
              ))}
              {product.colors.length > 3 && (
                <span className="text-xs text-gray-500">+{product.colors.length - 3}</span>
              )}
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">Size:</span>
            <span className="text-xs text-gray-500">
              {Math.min(...product.sizes)} - {Math.max(...product.sizes)}
            </span>
          </div>
        </div>

        {/* Price */}
        <div className="flex items-center space-x-2 mb-4">
          <span className="text-lg font-bold text-gray-900">
            {product.price.toLocaleString('vi-VN')}₫
          </span>
          {product.originalPrice && (
            <span className="text-sm text-gray-500 line-through">
              {product.originalPrice.toLocaleString('vi-VN')}₫
            </span>
          )}
        </div>

        {/* Add to Cart */}
        <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2">
          <ShoppingCart className="h-4 w-4" />
          <span>Thêm vào giỏ</span>
        </button>
      </div>
    </div>
  );

  return (
    <CustomerLayout currentPage="products" onNavigate={onNavigate}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Tất cả sản phẩm</h1>
          <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
            <p className="text-gray-600">Tìm thấy {products.length} sản phẩm</p>
            
            {/* Controls */}
            <div className="flex items-center space-x-4">
              {/* View Toggle */}
              <div className="flex bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded-md transition-colors ${
                    viewMode === 'grid' ? 'bg-white shadow-sm' : 'text-gray-500'
                  }`}
                >
                  <Grid className="h-5 w-5" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded-md transition-colors ${
                    viewMode === 'list' ? 'bg-white shadow-sm' : 'text-gray-500'
                  }`}
                >
                  <List className="h-5 w-5" />
                </button>
              </div>

              {/* Sort */}
              <div className="relative">
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {sortOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
                <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              </div>

              {/* Filter Toggle - Mobile */}
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="lg:hidden flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg"
              >
                <Filter className="h-5 w-5" />
                <span>Lọc</span>
              </button>
            </div>
          </div>
        </div>

        <div className="flex gap-8">
          {/* Filters Sidebar */}
          <div className={`w-80 flex-shrink-0 ${showFilters ? 'block' : 'hidden'} lg:block`}>
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 sticky top-8">
              <h3 className="font-semibold text-gray-900 mb-6 flex items-center">
                <Filter className="h-5 w-5 mr-2" />
                Bộ lọc
              </h3>

              {/* Price Range */}
              <div className="mb-8">
                <h4 className="font-medium text-gray-900 mb-4">Khoảng giá</h4>
                <div className="space-y-4">
                  <div className="flex gap-2">
                    <input
                      type="number"
                      min={0}
                      max={5000000}
                      placeholder="Từ"
                      className="w-1/2 border border-gray-300 rounded px-2 py-1 text-sm"
                      value={priceRange[0]}
                      onChange={e => setPriceRange([+e.target.value, priceRange[1]])}
                    />
                    <input
                      type="number"
                      min={0}
                      max={5000000}
                      placeholder="Đến"
                      className="w-1/2 border border-gray-300 rounded px-2 py-1 text-sm"
                      value={priceRange[1]}
                      onChange={e => setPriceRange([priceRange[0], +e.target.value])}
                    />
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="5000000"
                    step="100000"
                    value={priceRange[1]}
                    onChange={(e) => setPriceRange([priceRange[0], Number(e.target.value)])}
                    className="w-full accent-blue-600"
                  />
                  <div className="flex justify-between text-sm text-gray-500">
                    <span>0₫</span>
                    <span>5.000.000₫</span>
                  </div>
                </div>
              </div>

              {/* Categories */}
              <div className="mb-8">
                <h4 className="font-medium text-gray-900 mb-4">Danh mục</h4>
                <div className="space-y-3">
                  {categories.map(category => (
                    <label key={category.id} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={selectedCategories.includes(category.id)}
                        onChange={() => toggleCategory(category.id)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="ml-3 text-sm text-gray-700 flex-1">
                        {category.name}
                      </span>
                      <span className="text-xs text-gray-500">({category.count})</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Brands */}
              <div className="mb-8">
                <h4 className="font-medium text-gray-900 mb-4">Thương hiệu</h4>
                <div className="space-y-3">
                  {brands.map(brand => (
                    <label key={brand.id} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={selectedBrands.includes(brand.id)}
                        onChange={() => toggleBrand(brand.id)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="ml-3 text-sm text-gray-700 </div>flex-1">
                        {brand.name}
                      </span>
                      <span className="text-xs text-gray-500">({brand.count})</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Clear Filters */}
              <button className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition-colors">
                Xóa bộ lọc
              </button>
            </div>
          </div>

          {/* Products Grid/List */}
          <div className="flex-1">
            <div className={viewMode === 'grid' ? 'grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6' : 'space-y-6'}>
              {products.map(product => (
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
                    
                    {/* Badges */}
                    <div className="absolute top-4 left-4 flex flex-col space-y-2">
                      {product.isNew && (
                        <span className="bg-green-500 text-white text-xs font-medium px-2 py-1 rounded">
                          Mới
                        </span>
                      )}
                      {product.isHot && (
                        <span className="bg-red-500 text-white text-xs font-medium px-2 py-1 rounded">
                          Hot
                        </span>
                      )}
                      {product.discount && (
                        <span className="bg-red-500 text-white text-xs font-medium px-2 py-1 rounded">
                          -{product.discount}%
                        </span>
                      )}
                    </div>

                    {/* Wishlist Button */}
                    <button 
                      className="absolute top-4 right-4 bg-white/80 hover:bg-white p-2 rounded-full shadow-lg transition-colors"
                      onClick={(e) => {
                        e.stopPropagation();
                        // Handle wishlist toggle
                      }}
                    >
                      <Heart className="h-4 w-4 text-gray-600" />
                    </button>
                  </div>

                  <div className="p-6 flex-1">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <p className="text-sm text-gray-500 mb-1">{product.brand}</p>
                        <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">{product.name}</h3>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2 mb-3">
                      <div className="flex text-yellow-400">
                        {[...Array(5)].map((_, i) => (
                          <Star 
                            key={i} 
                            className={`h-4 w-4 ${i < Math.floor(product.rating) ? 'fill-current' : ''}`} 
                          />
                        ))}
                      </div>
                      <span className="text-sm text-gray-500">
                        {product.rating} ({product.reviews} đánh giá)
                      </span>
                    </div>

                    <div className="flex items-center space-x-2 mb-4">
                      <span className="text-2xl font-bold text-red-600">
                        {new Intl.NumberFormat('vi-VN', {
                          style: 'currency',
                          currency: 'VND'
                        }).format(product.price)}
                      </span>
                      {product.originalPrice && (
                        <span className="text-lg text-gray-500 line-through">
                          {new Intl.NumberFormat('vi-VN', {
                            style: 'currency',
                            currency: 'VND'
                          }).format(product.originalPrice)}
                        </span>
                      )}
                    </div>

                    {/* Colors */}
                    <div className="flex items-center space-x-2 mb-4">
                      <span className="text-sm text-gray-500">Màu:</span>
                      <div className="flex space-x-1">
                        {product.colors.slice(0, 3).map((color, index) => (
                          <div
                            key={index}
                            className="w-4 h-4 rounded-full bg-gray-300 border border-gray-400"
                            title={color}
                          />
                        ))}
                        {product.colors.length > 3 && (
                          <span className="text-xs text-gray-500">+{product.colors.length - 3}</span>
                        )}
                      </div>
                    </div>

                    {/* Sizes */}
                    <div className="flex items-center space-x-2 mb-6">
                      <span className="text-sm text-gray-500">Size:</span>
                      <div className="flex space-x-1">
                        {product.sizes.slice(0, 4).map((size, index) => (
                          <span key={index} className="text-xs bg-gray-100 px-2 py-1 rounded">
                            {size}
                          </span>
                        ))}
                        {product.sizes.length > 4 && (
                          <span className="text-xs text-gray-500">+{product.sizes.length - 4}</span>
                        )}
                      </div>
                    </div>

                    <button 
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-6 rounded-xl font-medium transition-colors flex items-center justify-center space-x-2"
                      onClick={(e) => {
                        e.stopPropagation();
                        // Handle add to cart
                      }}
                    >
                      <ShoppingCart className="h-5 w-5" />
                      <span>Thêm vào giỏ</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            <div className="mt-12 flex justify-center">
              <div className="flex space-x-2">
                <button className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50">
                  Trước
                </button>
                {[1, 2, 3, 4, 5].map(page => (
                  <button
                    key={page}
                    className={`px-4 py-2 rounded-lg ${
                      page === 1 
                        ? 'bg-blue-600 text-white' 
                        : 'border border-gray-300 text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    {page}
                  </button>
                ))}
                <button className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50">
                  Sau
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </CustomerLayout>
  );
}