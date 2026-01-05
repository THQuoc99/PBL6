import { useState, useEffect, useCallback } from 'react';
import { fetchAdminStores, fetchAdminStoreById } from '../../services/dashboardAdmin/stores';

export function useAdminStores(query: Record<string, any> = {}) {
  const [data, setData] = useState<any>({ items: [], total: 0 });
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<any>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetchAdminStores(query);
      setData(res);
      setError(null);
    } catch (err) { setError(err); }
    finally { setLoading(false); }
  }, [JSON.stringify(query)]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleLockStore = async (storeId: any) => {
    try {
      const { lockStore } = await import('../../services/dashboardAdmin/stores');
      await lockStore(storeId);
      // Refetch to update UI
      fetchData();
      return true;
    } catch (err) {
      console.error("Lock store error:", err);
      return false;
    }
  };

  return { data, loading, error, refetch: fetchData, getById: fetchAdminStoreById, lockStore: handleLockStore };
}
