import { useState, useCallback } from 'react';
import { createOrder as createOrderService } from '../../services/order/order';

export function useCreateOrder() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<any>(null);
  const [data, setData] = useState<any>(null);

  const createOrder = useCallback(async (input: any) => {
    setLoading(true);
    setError(null);
    try {
      const res = await createOrderService(input);
      const payload = res?.data?.createOrder ?? null;
      setData(payload);
      if (res?.errors) setError(res.errors);
      setLoading(false);
      return res;
    } catch (err) {
      setError(err);
      setLoading(false);
      throw err;
    }
  }, []);

  return { createOrder, loading, error, data };
}
