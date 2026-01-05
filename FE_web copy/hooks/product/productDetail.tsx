import { useState, useEffect } from 'react';
import { productService } from '../../services/product/product';

export function useProductDetail(productId: string) {
  const [product, setProduct] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!productId) {
      setProduct(null);
      return;
    }
    setLoading(true);
    productService.getProductDetail(productId)
      .then(res => {
        setProduct(res.product || null);
        setError(res.errors ? 'Lỗi lấy chi tiết sản phẩm' : null);
      })
      .catch(() => setError('Lỗi lấy chi tiết sản phẩm'))
      .finally(() => setLoading(false));
  }, [productId]);

  return { product, loading, error };
}
