import { useState, useCallback } from 'react';
import { fetchMyOrders, fetchOrdersByUser, cancelOrderService, cancelSubOrderService } from '../../services/order/order';

export function useMyOrders() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<any>(null);
  const [data, setData] = useState<any>(null);

  const getMyOrders = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchMyOrders();
      const payload = res?.data?.myOrders ?? null;
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

  return { getMyOrders, loading, error, data };
}

export function useOrdersByUser() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<any>(null);
  const [data, setData] = useState<any>(null);

  const getOrdersByUser = useCallback(async (userId: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchOrdersByUser(userId);
      const payload = res?.data?.ordersByUser ?? null;
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

  return { getOrdersByUser, loading, error, data };
}

export function useCancelOrder() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<any>(null);

  const cancelOrder = useCallback(async (orderId: string | number) => {
    setLoading(true);
    setError(null);
    try {
      const res = await cancelOrderService(orderId);
      setLoading(false);
      return res;
    } catch (err) {
      setError(err);
      setLoading(false);
      throw err;
    }
  }, []);

  return { cancelOrder, loading, error };
}

export function useCancelSubOrder() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<any>(null);

  const cancelSubOrder = useCallback(async (subOrderId: string | number) => {
    setLoading(true);
    setError(null);
    try {
      const res = await cancelSubOrderService(subOrderId);
      setLoading(false);
      return res;
    } catch (err) {
      setError(err);
      setLoading(false);
      throw err;
    }
  }, []);

  return { cancelSubOrder, loading, error };
}

export default useMyOrders;
