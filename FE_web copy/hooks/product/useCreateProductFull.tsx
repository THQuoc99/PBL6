import { useState } from 'react';
import { createProductFull as svcCreateProductFull } from '../../services/product/product';

export function useCreateProductFull() {
  const [loading, setLoading] = useState(false);

  const createProductFull = async (input: any) => {
    setLoading(true);
    try {
      const res = await svcCreateProductFull(input);
      return res;
    } catch (err) {
      console.error('createProductFull error', err);
      return { success: false, errors: [err?.message || 'Unknown error'] };
    } finally {
      setLoading(false);
    }
  };

  return { createProductFull, loading } as const;
}

export default useCreateProductFull;
