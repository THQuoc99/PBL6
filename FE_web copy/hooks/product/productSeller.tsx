import { useState, useEffect, useRef } from 'react';
import { productService } from '../../services/product/product';

export function useProducts(
  filter?: any,
  sortBy?: any,
  paging?: { first?: number; after?: string; last?: number; before?: string },
  options?: { allowAll?: boolean }
) {
  const [products, setProducts] = useState<any[]>([]);
  const [pageInfo, setPageInfo] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Sử dụng ref để so sánh giá trị thực sự thay vì reference
  const prevParamsRef = useRef<string>('');

  useEffect(() => {
    // For seller hook, default to NOT allowing a global fetch when no filter provided.
    // Caller should pass { allowAll: true } only when they explicitly want global results.
    const allowAll = options?.allowAll ?? false;

    const currentParams = JSON.stringify({ filter, sortBy, paging, allowAll });
    
    // Chỉ fetch khi params thực sự thay đổi
    if (currentParams === prevParamsRef.current) {
      return;
    }
    
    prevParamsRef.current = currentParams;
    console.log('useProducts (seller) - fetching with params:', { filter, sortBy, paging, allowAll });

    // If caller requested not to fetch when no filter provided, skip.
    if (!allowAll && !filter) {
      console.log('useProducts (seller) - skipping fetch because allowAll=false and filter is empty (prevents global fetch)');
      setProducts([]);
      setPageInfo(null);
      setError(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    productService.getProductByFilter_Sort(filter, sortBy, paging)
      .then(res => {
        console.log('useProducts - response:', res);
        const nodes = res.products?.edges || [];
        const normalized = nodes.map((e: any) => {
          const n = e.node || {};
          return {
            id: n.productId ?? n.id,
            name: n.name,
            sku: n.sku ?? n.productId ?? n.id,
            price: n.finalPrice ?? n.minPrice ?? n.basePrice ?? 0,
            minPrice: n.minPrice,
            maxPrice: n.maxPrice,
            priceRange: n.priceRange,
            basePrice: n.basePrice,
            discountPercentage: n.discountPercentage,
            hasDiscount: n.hasDiscount,
            finalPrice: n.finalPrice,
            isFeatured: n.isFeatured,
            isHot: n.isHot,
            isNew: n.isNew,
            images: n.thumbnailImage ? [n.thumbnailImage.imageUrl] : (n.images || []),
            colorOptions: n.colorOptions || [],
            sizeOptions: n.sizeOptions || [],
            category: n.category ? { name: n.category.name } : n.category || null,
            brand: n.brand ? { brandId: n.brand.brandId, name: n.brand.name } : n.brand || null,
            rating: n.ratingAverage ?? null,
            reviews: n.reviewCount ?? null,
            sold_count: n.totalSold ?? n.total_sold ?? 0,
            totalStock: n.totalStock ?? n.total_stock ?? 0,
            createdAt: n.createdAt,
            store: n.store ? { name: n.store.name } : n.store || null,
          };
        });
        setProducts(normalized || []);
        setPageInfo(res.products?.pageInfo || null);
        setError(res.errors ? 'Lỗi lấy danh sách sản phẩm' : null);
      })
      .catch((err) => {
        console.error('useProducts - error:', err);
        setError('Lỗi lấy danh sách sản phẩm');
      })
      .finally(() => setLoading(false));
  }, [filter, sortBy, paging, options?.allowAll]);
  
  return { products, pageInfo, loading, error };
}
