import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation, useParams, useSearchParams } from 'react-router-dom';

// Component cho trang sản phẩm với search và filter
export function ProductsPageExample() {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();
  
  // Lấy query parameters
  const searchQuery = searchParams.get('search') || '';
  const category = searchParams.get('category') || '';
  const page = parseInt(searchParams.get('page') || '1');
  
  const handleSearch = (query: string) => {
    // Cập nhật URL với search params
    setSearchParams({ 
      search: query, 
      category, 
      page: '1' 
    });
  };
  
  const handleFilterByCategory = (cat: string) => {
    setSearchParams({ 
      search: searchQuery, 
      category: cat, 
      page: '1' 
    });
  };
  
  const goToProductDetail = (productId: string) => {
    navigate(`/product/${productId}`, {
      state: { 
        fromSearch: searchQuery,
        fromCategory: category,
        returnTo: location.pathname + location.search
      }
    });
  };

  return (
    <div className="p-4">
      <h1>Sản phẩm</h1>
      
      {/* Search */}
      <input 
        value={searchQuery}
        onChange={(e) => handleSearch(e.target.value)}
        placeholder="Tìm kiếm sản phẩm..."
        className="border p-2 mb-4"
      />
      
      {/* Category filter */}
      <div className="mb-4">
        <button 
          onClick={() => handleFilterByCategory('shoes')}
          className={`mr-2 px-4 py-2 ${category === 'shoes' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
        >
          Giày
        </button>
        <button 
          onClick={() => handleFilterByCategory('clothes')}
          className={`px-4 py-2 ${category === 'clothes' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
        >
          Quần áo
        </button>
      </div>
      
      {/* Products list */}
      <div className="grid grid-cols-4 gap-4">
        {[1,2,3,4].map(id => (
          <div key={id} className="border p-4">
            <h3>Sản phẩm {id}</h3>
            <button 
              onClick={() => goToProductDetail(id.toString())}
              className="bg-blue-500 text-white px-4 py-2 mt-2"
            >
              Xem chi tiết
            </button>
          </div>
        ))}
      </div>
      
      {/* Pagination */}
      <div className="mt-4">
        <button 
          onClick={() => setSearchParams({...Object.fromEntries(searchParams), page: (page - 1).toString()})}
          disabled={page <= 1}
          className="mr-2 px-4 py-2 bg-gray-200 disabled:opacity-50"
        >
          Trang trước
        </button>
        <span>Trang {page}</span>
        <button 
          onClick={() => setSearchParams({...Object.fromEntries(searchParams), page: (page + 1).toString()})}
          className="ml-2 px-4 py-2 bg-gray-200"
        >
          Trang sau
        </button>
      </div>
    </div>
  );
}

// Component cho trang chi tiết sản phẩm
export function ProductDetailExample() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  
  // Lấy data từ state (nếu có)
  const fromSearch = location.state?.fromSearch;
  const fromCategory = location.state?.fromCategory;
  const returnTo = location.state?.returnTo;
  
  const [product, setProduct] = useState(null);
  
  useEffect(() => {
    // Fetch product data based on ID
    console.log('Loading product:', id);
    // setProduct(fetchedProduct);
  }, [id]);
  
  const goBack = () => {
    if (returnTo) {
      // Quay về trang search với filters
      navigate(returnTo);
    } else {
      // Fallback: quay về trang trước
      navigate(-1);
    }
  };
  
  const addToCart = () => {
    // Add to cart logic
    navigate('/cart');
  };
  
  const buyNow = () => {
    navigate('/payment', {
      state: { 
        productId: id,
        fromPage: 'product-detail'
      }
    });
  };

  if (!id) {
    return <div>Không tìm thấy sản phẩm</div>;
  }

  return (
    <div className="p-4">
      {/* Breadcrumb/Back button */}
      <button 
        onClick={goBack}
        className="mb-4 text-blue-500 hover:underline"
      >
        ← Quay lại {fromSearch ? `kết quả "${fromSearch}"` : 'trang trước'}
      </button>
      
      <div className="grid grid-cols-2 gap-8">
        <div>
          <img src="/placeholder-image.jpg" alt="Product" className="w-full" />
        </div>
        
        <div>
          <h1 className="text-2xl font-bold mb-4">Sản phẩm {id}</h1>
          
          {fromSearch && (
            <p className="text-sm text-gray-600 mb-2">
              Tìm thấy từ tìm kiếm: "{fromSearch}"
            </p>
          )}
          
          {fromCategory && (
            <p className="text-sm text-gray-600 mb-4">
              Danh mục: {fromCategory}
            </p>
          )}
          
          <p className="text-xl font-bold text-red-500 mb-4">1.299.000 VNĐ</p>
          
          <div className="space-x-4">
            <button 
              onClick={addToCart}
              className="bg-yellow-500 text-white px-6 py-2 rounded"
            >
              Thêm vào giỏ
            </button>
            <button 
              onClick={buyNow}
              className="bg-red-500 text-white px-6 py-2 rounded"
            >
              Mua ngay
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Component cho user profile với nested routes
export function UserProfileExample() {
  const { userId, section } = useParams<{ userId: string; section?: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  
  const sections = ['profile', 'orders', 'wishlist', 'addresses'];
  const currentSection = section || 'profile';
  
  const navigateToSection = (sectionName: string) => {
    navigate(`/user/${userId}/${sectionName}`);
  };

  return (
    <div className="p-4">
      <h1>Tài khoản của User {userId}</h1>
      
      {/* Navigation tabs */}
      <div className="flex space-x-4 mb-6">
        {sections.map(sec => (
          <button
            key={sec}
            onClick={() => navigateToSection(sec)}
            className={`px-4 py-2 ${
              currentSection === sec 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-200 hover:bg-gray-300'
            }`}
          >
            {sec.charAt(0).toUpperCase() + sec.slice(1)}
          </button>
        ))}
      </div>
      
      {/* Content based on current section */}
      <div>
        {currentSection === 'profile' && <div>Thông tin cá nhân</div>}
        {currentSection === 'orders' && <div>Đơn hàng của bạn</div>}
        {currentSection === 'wishlist' && <div>Danh sách yêu thích</div>}
        {currentSection === 'addresses' && <div>Địa chỉ giao hàng</div>}
      </div>
    </div>
  );
}

// Hook tùy chỉnh để quản lý breadcrumb
export function useBreadcrumb() {
  const location = useLocation();
  
  const getBreadcrumb = () => {
    const paths = location.pathname.split('/').filter(Boolean);
    return paths.map((path, index) => ({
      name: path.charAt(0).toUpperCase() + path.slice(1),
      path: '/' + paths.slice(0, index + 1).join('/'),
      isLast: index === paths.length - 1
    }));
  };
  
  return getBreadcrumb();
}

// Component Breadcrumb
export function Breadcrumb() {
  const breadcrumb = useBreadcrumb();
  const navigate = useNavigate();
  
  return (
    <nav className="flex space-x-2 text-sm text-gray-600 mb-4">
      <button onClick={() => navigate('/home')} className="hover:text-blue-500">
        Trang chủ
      </button>
      {breadcrumb.map((item, index) => (
        <React.Fragment key={index}>
          <span>/</span>
          {item.isLast ? (
            <span className="text-gray-900 font-medium">{item.name}</span>
          ) : (
            <button 
              onClick={() => navigate(item.path)}
              className="hover:text-blue-500"
            >
              {item.name}
            </button>
          )}
        </React.Fragment>
      ))}
    </nav>
  );
}