import { useState, useEffect } from "react";
import {
  fetchStoreDashboard,
  StoreDashboard,
} from "../../services/dashboard/dashboard";

export const useDashboard = (storeId: string | null, days: number = 7) => {
  const [data, setData] = useState<StoreDashboard | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboard = async () => {
    if (!storeId) {
      setData(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await fetchStoreDashboard(storeId, days);
      setData(result);
    } catch (err: any) {
      console.error("Error in useDashboard:", err);
      setError(err.message || "Failed to fetch dashboard data");
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, [storeId, days]);

  const refetch = () => {
    fetchDashboard();
  };

  return {
    data,
    loading,
    error,
    refetch,
  };
};
