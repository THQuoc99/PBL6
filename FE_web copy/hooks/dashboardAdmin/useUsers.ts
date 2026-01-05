import { useState, useEffect, useCallback } from 'react';
import { fetchAdminUsers, fetchAdminUserById } from '../../services/dashboardAdmin/users';

export function useAdminUsers(query: Record<string, any> = {}) {
  const [data, setData] = useState<any>({ items: [], total: 0 });
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<any>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetchAdminUsers(query);
      setData(res);
      setError(null);
    } catch (err) { setError(err); }
    finally { setLoading(false); }
  }, [JSON.stringify(query)]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleBanUser = async (userId: any) => {
    try {
      const { banUser } = await import('../../services/dashboardAdmin/users');
      await banUser(userId);
      fetchData();
      return true;
    } catch (err) {
      console.error("Ban user error:", err);
      return false;
    }
  };

  return { data, loading, error, refetch: fetchData, getById: fetchAdminUserById, banUser: handleBanUser };
}
