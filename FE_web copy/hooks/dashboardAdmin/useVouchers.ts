import { useState, useEffect, useCallback } from 'react';
import { fetchAdminVouchers, toggleVoucher, deleteVoucher, createVoucher, updateVoucher, fetchAdminVoucherById } from '../../services/dashboardAdmin/vouchers';

export function useAdminVouchers(query: Record<string, any> = {}) {
  const [data, setData] = useState<any>({ items: [], total: 0 });
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<any>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetchAdminVouchers(query);
      setData(res);
      setError(null);
    } catch (err) { setError(err); }
    finally { setLoading(false); }
  }, [JSON.stringify(query)]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleToggleVoucher = async (voucherId: number) => {
    try {
      await toggleVoucher(voucherId);
      await fetchData();
    } catch (err) {
      console.error('Failed to toggle voucher:', err);
      throw err;
    }
  };

  const handleDeleteVoucher = async (voucherId: number) => {
    try {
      await deleteVoucher(voucherId);
      await fetchData();
    } catch (err) {
      console.error('Failed to delete voucher:', err);
      throw err;
    }
  };

  const handleCreateVoucher = async (payload: any) => {
    try {
      const result = await createVoucher(payload);
      await fetchData();
      return result;
    } catch (err) {
      console.error('Failed to create voucher:', err);
      throw err;
    }
  };

  const handleUpdateVoucher = async (voucherId: number, payload: any) => {
    try {
      const result = await updateVoucher(voucherId, payload);
      await fetchData();
      return result;
    } catch (err) {
      console.error('Failed to update voucher:', err);
      throw err;
    }
  };

  return {
    data,
    loading,
    error,
    refetch: fetchData,
    toggleVoucher: handleToggleVoucher,
    deleteVoucher: handleDeleteVoucher,
    createVoucher: handleCreateVoucher,
    updateVoucher: handleUpdateVoucher,
    getById: fetchAdminVoucherById
  };
}
