import { useState, useEffect, useCallback } from 'react';
import { fetchSubOrdersByStore, confirmSubOrderShipmentService } from '../../services/order/order';

// isPayment: nếu true sẽ chỉ lấy các suborder chưa thuộc SettlementItem (dùng cho màn Payments)
export function useSubOrdersByStore(storeId?: string, isPayment?: boolean) {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<any>(null);

  const fetchData = useCallback(async (id?: string) => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetchSubOrdersByStore(id, isPayment);
      // Debug log the full GraphQL response to help diagnose empty results
      // eslint-disable-next-line no-console
      console.debug('fetchSubOrdersByStore - graphql result:', res);

      if (res.errors) {
        setError(res.errors);
        setData([]);
      } else {
        // Accept either camelCase or snake_case field names depending on server schema
        const payload = res.data?.subOrdersByStore ?? res.data?.sub_orders_by_store ?? [];
        setData(payload);
      }
    } catch (e) {
      setError(e);
      setData([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (storeId) fetchData(storeId);
  }, [storeId, isPayment, fetchData]);

  const confirmSubOrder = useCallback(async (subOrderId?: string | number) => {
    if (!storeId || !subOrderId) throw new Error('storeId and subOrderId required');
    try {
      const res = await confirmSubOrderShipmentService(subOrderId);
      // Expect res to be { success, message, result } — surface server message on failure
      if (!res) throw new Error('No response from server');
      const success = res.success ?? false;
      const message = res.message ?? (res.errors ? JSON.stringify(res.errors) : 'Unknown response');
      // after confirming on server, refresh the list to get updated shipment info
      await fetchData(storeId);
      if (!success) {
        throw new Error(message);
      }
      return { success, message, result: res.result };
    } catch (e) {
      // rethrow so caller can handle UI fallback
      throw e;
    }
  }, [storeId, fetchData]);

  return {
    data,
    loading,
    error,
    refetch: () => fetchData(storeId),
    confirmSubOrder,
  } as const;
}

export default useSubOrdersByStore;
