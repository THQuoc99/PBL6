import { useState, useEffect, useRef } from 'react';
import { productService } from '../../services/product/product';

export function useProducts(filter?: any, sortBy?: any, paging?: { first?: number; after?: string; last?: number; before?: string }) {
  const [products, setProducts] = useState<any[]>([]);
  const [pageInfo, setPageInfo] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Sử dụng ref để so sánh giá trị thực sự thay vì reference
  const prevParamsRef = useRef<string>('');

  useEffect(() => {
    const currentParams = JSON.stringify({ filter, sortBy, paging });
    
    // Chỉ fetch khi params thực sự thay đổi
    if (currentParams === prevParamsRef.current) {
      return;
    }
    
    prevParamsRef.current = currentParams;
    console.log('useProducts - fetching with params:', { filter, sortBy, paging });
    
    setLoading(true);
    productService.getProductByFilter_Sort(filter, sortBy, paging)
      .then(res => {
        console.log('useProducts - response:', res);
        const newProducts = res.products?.edges?.map((e: any) => e.node) || [];
        setProducts(newProducts);
        setPageInfo(res.products?.pageInfo || null);
        setError(res.errors ? 'Lỗi lấy danh sách sản phẩm' : null);
      })
      .catch((err) => {
        console.error('useProducts - error:', err);
        setError('Lỗi lấy danh sách sản phẩm');
      })
      .finally(() => setLoading(false));
  }, [filter, sortBy, paging]);
  
  // load more (cursor-based)
  const loadMore = async () => {
    if (!pageInfo?.hasNextPage) return { success: false, reason: 'no_more' };
    try {
      setLoading(true);
      const nextPaging = { ...(paging || {}), after: pageInfo.endCursor };
      const res = await productService.getProductByFilter_Sort(filter, sortBy, nextPaging);
      const more = res.products?.edges?.map((e: any) => e.node) || [];
      setProducts(prev => [...prev, ...more]);
      setPageInfo(res.products?.pageInfo || null);
      return { success: true };
    } catch (err) {
      console.error('useProducts.loadMore error', err);
      return { success: false, reason: 'error' };
    } finally {
      setLoading(false);
    }
  };

  return { products, pageInfo, loading, error, loadMore };
}
