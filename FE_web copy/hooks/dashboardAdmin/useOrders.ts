import { useState, useEffect, useCallback } from 'react';
import { fetchAdminOrders, fetchAdminOrderById } from '../../services/dashboardAdmin/orders';

export function useAdminOrders(query: Record<string, any> = {}){
  const [data, setData] = useState<any>({ items: [], total: 0 });
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<any>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try{
      const res = await fetchAdminOrders(query);
      setData(res);
      setError(null);
    }catch(err){ setError(err); }
    finally{ setLoading(false); }
  }, [JSON.stringify(query)]);

  useEffect(()=>{ fetchData(); }, [fetchData]);

  return { data, loading, error, refetch: fetchData, getById: fetchAdminOrderById };
}
