import { useState, useEffect, useCallback } from 'react';
import { fetchAdminDashboard } from '../../services/dashboardAdmin/dashboard';

export function useAdminDashboard(params: Record<string, any> = {}){
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<any>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try{
      const res = await fetchAdminDashboard(params);
      setData(res);
      setError(null);
    }catch(err){
      setError(err);
    }finally{ setLoading(false); }
  }, [JSON.stringify(params)]);

  useEffect(()=>{ fetchData(); }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}
