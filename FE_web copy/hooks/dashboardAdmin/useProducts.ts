import { useState, useEffect, useCallback } from 'react';
import { fetchAdminProducts, fetchAdminProductById } from '../../services/dashboardAdmin/products';

export function useAdminProducts(query: Record<string, any> = {}){
  const [data, setData] = useState<any>({ items: [], total: 0 });
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<any>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try{
      const res = await fetchAdminProducts(query);
      setData(res);
      setError(null);
    }catch(err){ setError(err); }
    finally{ setLoading(false); }
  }, [JSON.stringify(query)]);

  useEffect(()=>{ fetchData(); }, [fetchData]);

  return { data, loading, error, refetch: fetchData, getById: fetchAdminProductById };
}
