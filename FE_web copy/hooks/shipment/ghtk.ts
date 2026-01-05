import { useState } from 'react';
import { createGhtkOrders as createGhtkOrdersService } from '../../services/shipment/ghtk';

export function useCreateGhtkOrders() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const createGhtkOrders = async (orderId: string | number) => {
    setLoading(true);
    setError(null);
    try {
      const res = await createGhtkOrdersService(orderId);
      return res;
    } catch (err) {
      const e = err instanceof Error ? err : new Error(String(err));
      setError(e);
      throw e;
    } finally {
      setLoading(false);
    }
  };

  return { createGhtkOrders, loading, error } as const;
}

export default useCreateGhtkOrders;
