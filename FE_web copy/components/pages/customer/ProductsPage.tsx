import React, { useState, useMemo, useCallback, useEffect, useRef } from 'react';
import CustomerLayout from '../../layout/CustomerLayout';
import { Filter, Grid, List, Star, Heart, ShoppingCart, ChevronDown } from 'lucide-react';
import { useProducts } from '../../../hooks/product/products';
import { useCategories } from '../../../hooks/category/categorys';
import { useBrands } from '../../../hooks/brand/useBrand';
import { useLocation, useNavigate } from 'react-router-dom';
import { useCart } from '../../../hooks/cart/cart';
import { useAuth } from '../../../hooks/user/useAuth';

interface CustomerProductsPageProps {
  onNavigateToSeller?: () => void;
  onNavigate?: (page: string, data?: any) => void;
}

export default function CustomerProductsPage({ onNavigateToSeller, onNavigate }: CustomerProductsPageProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const { addToCart, loading: cartLoading } = useCart();
  const { isAuthenticated } = useAuth();
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState('popular');
  const [searchText, setSearchText] = useState('');
  const [activeSearch, setActiveSearch] = useState(''); // Search text được active khi nhấn Enter
  
  // Read search from URL on mount
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const searchParam = params.get('search');
    if (searchParam) {
      setActiveSearch(searchParam);
      setSearchText(searchParam);
    }
  }, [location.search]);
  
  // Filter states phù hợp với backend
  const [selectedCategories, setSelectedCategories] = useState<number[]>([]);
  const [includeSubcategories, setIncludeSubcategories] = useState(true);
  const [selectedBrandId, setSelectedBrandId] = useState<number | null>(null);
  const [priceMin, setPriceMin] = useState<number>(0);
  const [priceMax, setPriceMax] = useState<number>(5000000);
  const [hasStock, setHasStock] = useState<boolean | null>(null);
  const [hasDiscount, setHasDiscount] = useState<boolean | null>(null);
  const [minRating, setMinRating] = useState<number | null>(null);
  
  const [showFilters, setShowFilters] = useState(false);
  const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
  const formatPrice = (price: number) => {

    
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(price);
  };
  // Xây dựng filter object cho API
  const filter = useMemo(() => {
    const filterObj: any = {};
    
    if (activeSearch) filterObj.search = activeSearch;
    if (selectedCategories.length > 0) {
      filterObj.categoryIds = selectedCategories;
      filterObj.includeSubcategories = includeSubcategories;
    }
    if (selectedBrandId !== null) filterObj.brandId = selectedBrandId;
    if (priceMin > 0 || priceMax < 5000000) {
      filterObj.priceRange = { minPrice: priceMin, maxPrice: priceMax };
    }
    if (hasStock !== null) filterObj.hasStock = hasStock;
    if (hasDiscount !== null) filterObj.hasDiscount = hasDiscount;
    if (minRating !== null) filterObj.minRating = minRating;
    
    return Object.keys(filterObj).length > 0 ? filterObj : undefined;
  }, [activeSearch, selectedCategories, includeSubcategories, selectedBrandId, priceMin, priceMax, hasStock, hasDiscount, minRating]);

  // Xây dựng sort string cho API
  const sortByValue = useMemo(() => {
    switch (sortBy) {
      case 'newest':
        return 'NEWEST';
      case 'price-low':
        return 'PRICE_ASC';
      case 'price-high':
        return 'PRICE_DESC';
      case 'popular':
      default:
        return 'SALES_DESC';
    }
  }, [sortBy]);

  // Paging
  const paging = useMemo(() => ({ first: 16 }), []);

  // Gọi API với useProducts
  const { products, pageInfo, loading, error, loadMore } = useProducts(filter, sortByValue, paging as any);

  const containerRef = useRef<HTMLDivElement | null>(null);
  const isLoadingMoreRef = useRef(false);

  // Infinite scroll on the products container: load next page when near bottom
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const onScroll = () => {
      try {
        if (isLoadingMoreRef.current) return;
        const threshold = 300; // px from bottom to trigger
        const { scrollTop, scrollHeight, clientHeight } = el;
        if (scrollTop + clientHeight >= scrollHeight - threshold) {
          if (pageInfo?.hasNextPage && loadMore) {
            isLoadingMoreRef.current = true;
            loadMore().finally(() => {
              isLoadingMoreRef.current = false;
            });
          }
        }
      } catch (e) {
        // swallow
      }
    };

    el.addEventListener('scroll', onScroll);
    return () => el.removeEventListener('scroll', onScroll);
  }, [pageInfo, loadMore]);

  // Gọi API lấy categories
  const { categories: categoriesData, loading: categoriesLoading } = useCategories(
    { hasProducts: true },
    'product_count_desc'
  );

  // Chuyển đổi categories data sang format cho UI
  const categories = useMemo(() => {
    if (!categoriesData || categoriesData.length === 0) return [];
    return categoriesData.map((cat: any) => ({
      id: parseInt(cat.categoryId, 10), // Convert to number
      name: cat.name,
      count: cat.productCount || 0
    }));
  }, [categoriesData]);

  // Handle search khi nhấn Enter
  const handleSearchSubmit = useCallback((search: string) => {
    setActiveSearch(search);
  }, []);

  // Brands loaded from backend
  const { fetchBrands } = useBrands();
  const [brands, setBrands] = useState<{ id: number; name: string; count: number }[]>([]);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const data: any[] = await fetchBrands?.(true) || [];
        if (!mounted) return;
        const mapped = (data || []).map((b: any) => ({
          id: Number(b.brandId ?? b.brand_id ?? b.id) || 0,
          name: b.name || '',
          count: Number(b.productCount ?? 0) || 0,
        }));
        setBrands(mapped);
      } catch (e) {
        // ignore - keep brands empty on error
      }
    })();
    return () => {
      mounted = false;
    };
  }, [fetchBrands]);

  const sortOptions = [
    { value: 'popular', label: 'Phổ biến nhất' },
    { value: 'newest', label: 'Mới nhất' },
    { value: 'price-low', label: 'Giá: Thấp đến Cao' },
    { value: 'price-high', label: 'Giá: Cao đến Thấp' }
  ];

  const toggleCategory = (categoryId: number) => {
    setSelectedCategories(prev =>
      prev.includes(categoryId)
        ? prev.filter(id => id !== categoryId)
        : [...prev, categoryId]
    );
  };

  const handleRatingSelect = (rating: number) => {
    setMinRating(minRating === rating ? null : rating);
  };

  const handleClearFilters = () => {
    setSelectedCategories([]);
    setIncludeSubcategories(true);
    setSelectedBrandId(null);
    setPriceMin(0);
    setPriceMax(5000000);
    setHasStock(null);
    setHasDiscount(null);
    setMinRating(null);
    setSearchText('');
    setActiveSearch('');
  };

  // Quick add to cart handler
  const handleQuickAddToCart = async (e: React.MouseEvent, product: any) => {
    e.stopPropagation(); // Prevent navigation to product detail
    
    if (!isAuthenticated) {
      alert('Vui lòng đăng nhập để thêm vào giỏ hàng!');
      navigate('/login');
      return;
    }

    // Get first available variant (first color + first size)
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

  const ProductCard = ({ product, isListView }: { product: any; isListView: boolean }) => (
    <div className={`group bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-all ${isListView ? 'flex' : ''}`}>
      {/* Product Image */}
      <div className={`relative bg-gray-50 ${isListView ? 'w-56 flex-shrink-0' : 'p-4'}`}>
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
        
        <div className={`w-full bg-gray-200 rounded-lg ${isListView ? 'h-full' : 'h-36 mb-3'}`}></div>
      </div>

      {/* Product Info */}
      <div className={`p-4 ${isListView ? 'flex-1' : ''}`}>
        <div className="text-sm text-gray-500 mb-2">{product.category.name}</div>
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
          
          {/* Giá chính: finalPrice nếu có giảm, ngược lại basePrice */}
          <span className="text-lg font-bold text-gray-900">
            {formatPrice(product.finalPrice ?? product.basePrice)}
          </span>

          {/* Nếu có giảm giá thì mới hiển thị giá gốc gạch ngang */}
          {product.finalPrice && product.finalPrice < product.basePrice && (
            <span className="text-sm text-gray-500 line-through">
              {formatPrice(product.basePrice)}
            </span>
          )}

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
  );

  return (
    <CustomerLayout 
      currentPage="products" 
      onNavigate={onNavigate}
      onSearch={setSearchText}
      searchValue={searchText}
      onSearchSubmit={handleSearchSubmit}
    >
      {/* Sticky Header Bar */}
      <div className="sticky top-0 bg-white border-b shadow-sm z-40">
        <div className="max-w-[2560px] mx-auto px-2 sm:px-3 lg:px-4 py-4">
          <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Tất cả sản phẩm</h1>
              <p className="text-sm text-gray-600 mt-1">
                {loading ? 'Đang tải...' : error ? error : `Tìm thấy ${products.length} sản phẩm`}
              </p>
            </div>
            
            {/* Controls */}
            <div className="flex items-center space-x-3">
              {/* View Toggle */}
              <div className="flex bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded-md transition-colors ${
                    viewMode === 'grid' ? 'bg-white shadow-sm' : 'text-gray-500'
                  }`}
                  title="Lưới"
                >
                  <Grid className="h-5 w-5" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded-md transition-colors ${
                    viewMode === 'list' ? 'bg-white shadow-sm' : 'text-gray-500'
                  }`}
                  title="Danh sách"
                >
                  <List className="h-5 w-5" />
                </button>
              </div>

              {/* Sort */}
              <div className="relative">
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-2.5 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  {sortOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
                <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
              </div>

              {/* Filter Toggle - Mobile */}
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="lg:hidden flex items-center space-x-2 bg-blue-600 text-white px-4 py-2.5 rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Filter className="h-5 w-5" />
                <span className="text-sm font-medium">Lọc</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-[2560px] mx-auto px-2 sm:px-3 lg:px-4 py-6">
        <div className="flex gap-6">
          {/* Filters Sidebar - Fixed with scroll */}
          <aside className={`w-72 flex-shrink-0 ${showFilters ? 'block' : 'hidden'} lg:block`}>
            <div className="sticky top-24 bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div className="max-h-[calc(100vh-120px)] overflow-y-auto custom-scrollbar">
                {/* Filter Header - Sticky inside scroll */}
                <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 z-10">
                  <h3 className="font-semibold text-gray-900 flex items-center">
                    <Filter className="h-5 w-5 mr-2 text-blue-600" />
                    Bộ lọc
                  </h3>
                </div>

                <div className="p-6 space-y-6">
                  {/* Price Range */}
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3 text-sm">Khoảng giá</h4>
                    <div className="space-y-3">
                      <div className="flex gap-2">
                        <input
                          type="number"
                          min={0}
                          placeholder="Từ"
                          className="w-1/2 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          value={priceMin}
                          onChange={e => setPriceMin(+e.target.value)}
                        />
                        <input
                          type="number"
                          min={0}
                          placeholder="Đến"
                          className="w-1/2 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          value={priceMax}
                          onChange={e => setPriceMax(+e.target.value)}
                        />
                      </div>
                      <input
                        type="range"
                        min="0"
                        max="5000000"
                        step="100000"
                        value={priceMax}
                        onChange={(e) => setPriceMax(Number(e.target.value))}
                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                      />
                      <div className="flex justify-between text-xs text-gray-500">
                        <span>{priceMin.toLocaleString('vi-VN')}₫</span>
                        <span>{priceMax.toLocaleString('vi-VN')}₫</span>
                      </div>
                    </div>
                  </div>

                  {/* Categories */}
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3 text-sm">Danh mục</h4>
                    <div className="space-y-3">
                      <div className="space-y-2">
                        {categories.map(category => (
                          <label key={category.id} className="flex items-center cursor-pointer group">
                            <input
                              type="checkbox"
                              checked={selectedCategories.includes(category.id)}
                              onChange={() => toggleCategory(category.id)}
                              className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                            />
                            <span className="ml-3 text-sm text-gray-700 flex-1 group-hover:text-gray-900">
                              {category.name}
                            </span>
                            <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">{category.count}</span>
                          </label>
                        ))}
                      </div>
                      
                      {/* Include Subcategories */}
                      {selectedCategories.length > 0 && (
                        <label className="flex items-center cursor-pointer mt-3 pt-3 border-t border-gray-200">
                          <input
                            type="checkbox"
                            checked={includeSubcategories}
                            onChange={(e) => setIncludeSubcategories(e.target.checked)}
                            className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                          />
                          <span className="ml-3 text-sm text-gray-600">
                            Bao gồm danh mục con
                          </span>
                        </label>
                      )}
                    </div>
                  </div>

                  {/* Brands */}
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3 text-sm">Thương hiệu</h4>
                    <div className="space-y-2">
                      {brands.map(brand => (
                        <label key={brand.id} className="flex items-center cursor-pointer group">
                          <input
                            type="radio"
                            name="brand"
                            checked={selectedBrandId === brand.id}
                            onChange={() => setSelectedBrandId(selectedBrandId === brand.id ? null : brand.id)}
                            className="w-4 h-4 border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                          />
                          <span className="ml-3 text-sm text-gray-700 flex-1 group-hover:text-gray-900">
                            {brand.name}
                          </span>
                          <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">{brand.count}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Rating Filter */}
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3 text-sm">Đánh giá tối thiểu</h4>
                    <div className="space-y-2">
                      {[5, 4, 3, 2, 1].map(rating => (
                        <label 
                          key={rating} 
                          className="flex items-center cursor-pointer group hover:bg-gray-50 rounded-lg p-2 transition-colors"
                        >
                          <input
                            type="radio"
                            name="rating"
                            checked={minRating === rating}
                            onChange={() => handleRatingSelect(rating)}
                            className="w-4 h-4 border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                          />
                          <div className="ml-3 flex items-center flex-1">
                            <div className="flex">
                              {[...Array(5)].map((_, i) => (
                                <Star
                                  key={i}
                                  className={`h-4 w-4 ${
                                    i < rating
                                      ? 'text-yellow-400 fill-current'
                                      : 'text-gray-300'
                                  }`}
                                />
                              ))}
                            </div>
                            <span className="ml-2 text-sm text-gray-600">trở lên</span>
                          </div>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Stock & Discount Filters */}
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3 text-sm">Trạng thái</h4>
                    <div className="space-y-2">
                      <label className="flex items-center cursor-pointer group hover:bg-gray-50 rounded-lg p-2 transition-colors">
                        <input
                          type="checkbox"
                          checked={hasStock === true}
                          onChange={(e) => setHasStock(e.target.checked ? true : null)}
                          className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                        />
                        <span className="ml-3 text-sm text-gray-700 group-hover:text-gray-900">
                          Còn hàng
                        </span>
                      </label>
                      
                      <label className="flex items-center cursor-pointer group hover:bg-gray-50 rounded-lg p-2 transition-colors">
                        <input
                          type="checkbox"
                          checked={hasDiscount === true}
                          onChange={(e) => setHasDiscount(e.target.checked ? true : null)}
                          className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                        />
                        <span className="ml-3 text-sm text-gray-700 group-hover:text-gray-900">
                          Đang giảm giá
                        </span>
                      </label>
                    </div>
                  </div>
                </div>

                {/* Clear Filters - Sticky at bottom */}
                <div className="sticky bottom-0 bg-white border-t border-gray-200 p-4">
                  <button 
                    onClick={handleClearFilters}
                    className="w-full bg-gray-100 text-gray-700 py-2.5 px-4 rounded-lg hover:bg-gray-200 transition-colors font-medium text-sm"
                  >
                    Xóa bộ lọc
                  </button>
                </div>
              </div>
            </div>
          </aside>

          {/* Products Grid/List */}
          <main ref={containerRef} className="flex-1 min-w-0" style={{ maxHeight: 'calc(100vh - 96px)', overflowY: 'auto' }}>
            {loading ? (
              <div className="flex items-center justify-center py-20">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
                  <p className="text-gray-600">Đang tải sản phẩm...</p>
                </div>
              </div>
            ) : error ? (
              <div className="flex items-center justify-center py-20">
                <div className="text-center">
                  <p className="text-red-600 mb-4">{error}</p>
                  <button 
                    onClick={() => window.location.reload()}
                    className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
                  >
                    Thử lại
                  </button>
                </div>
              </div>
            ) : products.length === 0 ? (
              <div className="flex items-center justify-center py-20">
                <div className="text-center">
                  <div className="text-6xl mb-4">🔍</div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Không tìm thấy sản phẩm</h3>
                  <p className="text-gray-600 mb-6">Thử thay đổi bộ lọc hoặc từ khóa tìm kiếm</p>
                  <button 
                    onClick={handleClearFilters}
                    className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
                  >
                    Xóa bộ lọc
                  </button>
                </div>
              </div>
            ) : (
              <>
              <div className={viewMode === 'grid' ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6' : 'space-y-6'}>
                {products.map(product => (
                        <div 
                  key={product.productId} 
                  className={`bg-white rounded-2xl shadow-lg border border-gray-100 hover:shadow-xl transition-shadow duration-300 overflow-hidden cursor-pointer group ${
                    viewMode === 'list' ? 'flex' : ''
                  }`}
                  onClick={() => navigate(`/product/${product.productId}`)}
                >
                          <div className={`relative ${viewMode === 'list' ? 'w-56 flex-shrink-0' : 'aspect-square'}`}>
                    {product.thumbnailImage?.imageUrl ? (
                      <img 
                        src={product.thumbnailImage.imageUrl}
                        alt={product.name}
                                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                    ) : (
                      <div className="w-full h-full bg-gray-200 flex items-center justify-center">
                        <span className="text-gray-400">{product.id}</span>
                      </div>
                    )}
                    
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
                      {product.discountPercentage && (
                        <span className="bg-red-500 text-white text-xs font-medium px-2 py-1 rounded">
                          -{product.discountPercentage}%
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

                  <div className="p-3 flex-1">
                    {/* Brand */}
                    <p className="text-xs text-gray-500 mb-1">{product.brand?.name || 'N/A'}</p>
                    
                    {/* Product Name - Fixed 2 lines */}
                    <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2 h-10 text-sm">
                      {product.name}
                    </h3>

                    {/* Rating & Reviews */}
                    <div className="flex items-center space-x-2 mb-2">
                      <div className="flex text-yellow-400">
                        {[...Array(5)].map((_, i) => (
                          <Star 
                            key={i} 
                            className={`h-3 w-3 ${i < Math.floor(product.ratingAverage || 0) ? 'fill-current' : ''}`} 
                          />
                        ))}
                      </div>
                      <span className="text-xs text-gray-500">
                        ({product.reviewCount || 0})
                      </span>
                    </div>

                    {/* Sold Count */}
                    <div className="text-xs text-gray-600 mb-3">
                      Đã bán: <span className="font-medium">{product.totalSold || 0}</span>
                    </div>

                    {/* Price */}
                    <div className="flex items-baseline space-x-2 mb-3">
                      <span className="text-lg font-bold text-red-600">
                        {formatPrice(product.finalPrice || product.basePrice || 0)}
                      </span>
                      {product.hasDiscount && product.basePrice && (
                        <span className="text-sm text-gray-500 line-through">
                          {formatPrice(product.basePrice)}
                        </span>
                      )}
                    </div>

                    {/* Colors & Sizes - Compact */}
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      {product.colorOptions && product.colorOptions.length > 0 && (
                        <span>{product.colorOptions.length} màu</span>
                      )}
                      {product.sizeOptions && product.sizeOptions.length > 0 && (
                        <span>{product.sizeOptions.length} size</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination removed - infinite scroll/loadMore used instead */}
          </>
          )}
          </main>
        </div>
      </div>
    </CustomerLayout>
  );
}