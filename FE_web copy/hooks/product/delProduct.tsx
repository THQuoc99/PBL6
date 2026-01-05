import { useState } from 'react';
import { deleteProduct as apiDeleteProduct } from '../../services/product/product';

export function useDeleteProduct() {
  const [loading, setLoading] = useState(false);

  const deleteProduct = async (productId: number) => {
    setLoading(true);
    try {
      const res = await apiDeleteProduct(productId);
      return res;
    } finally {
      setLoading(false);
    }
  };

  return { deleteProduct, loading } as const;
}

export default useDeleteProduct;
