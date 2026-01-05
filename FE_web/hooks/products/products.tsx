import { useState, useEffect } from 'react';
import { productService } from '../../services/product';

export function useProducts(filter?: any, sortBy?: any, paging?: { first?: number; after?: string; last?: number; before?: string }) {
  const [products, setProducts] = useState<any[]>([]);
  const [pageInfo, setPageInfo] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    productService.getProductByFilter_Sort(filter, sortBy, paging)
      .then(res => {
        setProducts(res.products?.edges?.map((e: any) => e.node) || []);
        setPageInfo(res.products?.pageInfo || null);
        setError(res.errors ? 'Lỗi lấy danh sách sản phẩm' : null);
      })
      .catch(() => setError('Lỗi lấy danh sách sản phẩm'))
      .finally(() => setLoading(false));
  }, [filter, sortBy, paging]);
  console.log('useProducts - products:', products);
  return { products, pageInfo, loading, error };
}
