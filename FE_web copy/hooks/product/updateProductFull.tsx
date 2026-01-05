import { useState } from 'react';
import { productService } from '../../services/product/product';

export function useUpdateProductFull() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<any | null>(null);

  const update = async (productId: number, input: any) => {
    setLoading(true);
    setError(null);
    try {
      const res = await productService.updateProductFull(productId, input);
      setLoading(false);
      return res;
    } catch (e: any) {
      setLoading(false);
      setError(e);
      return { success: false, errors: [e?.message || 'Unknown error'] };
    }
  };

  return { update, loading, error } as const;
}

export default useUpdateProductFull;
