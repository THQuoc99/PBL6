import { useState } from 'react';
import { storeService } from '../../services/store/store';

export function useAddressStore() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<any>(null);

  const addAddress = async (storeId: string, input: any) => {
    setLoading(true);
    setError(null);
    try {
      const res = await storeService.addAddressStore(storeId, input);
      return res;
    } catch (e: any) {
      setError(e);
      return { success: false, message: e?.message || String(e) };
    } finally {
      setLoading(false);
    }
  };

  const updateAddress = async (storeId: string, input: any) => {
    setLoading(true);
    setError(null);
    try {
      const res = await storeService.updateAddressStore(storeId, input);
      return res;
    } catch (e: any) {
      setError(e);
      return { success: false, message: e?.message || String(e) };
    } finally {
      setLoading(false);
    }
  };

  const setDefaultAddress = async (addressId: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await storeService.setDefaultAddress(addressId);
      console.debug('useAddressStore.setDefaultAddress response:', res);
      return res;
    } catch (e: any) {
      setError(e);
      return { success: false, message: e?.message || String(e) };
    } finally {
      setLoading(false);
    }
  };

  const deleteAddress = async (addressId: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await storeService.deleteAddressStore(addressId);
      return res;
    } catch (e: any) {
      setError(e);
      return { success: false, message: e?.message || String(e) };
    } finally {
      setLoading(false);
    }
  };

  return { addAddress, updateAddress, setDefaultAddress, deleteAddress, loading, error } as const;
}

export default useAddressStore;
