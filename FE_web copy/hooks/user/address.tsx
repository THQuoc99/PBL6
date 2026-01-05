import { useState, useEffect, useCallback } from 'react';
import { addressService, Address } from '../../services/user/address';
import { useAuth } from './useAuth';

export function useAddresses() {
  const { isAuthenticated } = useAuth();
  const [addresses, setAddresses] = useState<Address[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ======================================================
  // Load danh sách địa chỉ
  // ======================================================
  const fetchAddresses = useCallback(async () => {
    if (!isAuthenticated) {
      setAddresses([]);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const data = await addressService.getAddresses();
      setAddresses(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Lỗi khi tải địa chỉ');
      setAddresses([]);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  // ======================================================
  // Helper để chạy mutation rồi refresh
  // ======================================================
  const runMutation = useCallback(
    async <T,>(handler: () => Promise<T>): Promise<T> => {
      try {
        setLoading(true);
        const result = await handler();

        if ((result as any)?.success) {
          await fetchAddresses();
        }

        return result;
      } catch (err) {
        return {
          success: false,
          errors: [err instanceof Error ? err.message : 'Lỗi hệ thống'],
        } as any;
      } finally {
        setLoading(false);
      }
    },
    [fetchAddresses]
  );

  // ======================================================
  // ADD ADDRESS
  // Service yêu cầu: { name, phoneNumber, province, ward... }
  // ======================================================
  const addAddress = useCallback(
    async (input: {
      name: string;
      phoneNumber?: string;
      province: string;
      ward: string;
      hamlet?: string;
      detail: string;
      isDefault?: boolean;
    }) => {
      return runMutation(() => addressService.addAddress(input));
    },
    [runMutation]
  );

  // ======================================================
  // UPDATE ADDRESS
  // Service yêu cầu: addressId: number
  // Hook nhận string → convert sang number
  // ======================================================
  const updateAddress = useCallback(
    async (input: {
      addressId: string;
      name?: string;
      phoneNumber?: string;
      province?: string;
      ward?: string;
      hamlet?: string;
      detail?: string;
      isDefault?: boolean;
    }) => {
      return runMutation(() =>
        addressService.updateAddress({
          ...input,
          addressId: Number(input.addressId),
        })
      );
    },
    [runMutation]
  );

  // ======================================================
  // DELETE
  // ======================================================
  const deleteAddress = useCallback(
    async (addressId: string) => {
      return runMutation(() =>
        addressService.deleteAddress(Number(addressId))
      );
    },
    [runMutation]
  );

  // ======================================================
  // SET DEFAULT
  // ======================================================
  const setDefaultAddress = useCallback(
    async (addressId: string) => {
      return runMutation(() =>
        addressService.setDefaultAddress(Number(addressId))
      );
    },
    [runMutation]
  );

  // ======================================================
  // Auto fetch
  // ======================================================
  useEffect(() => {
    fetchAddresses();
  }, [fetchAddresses]);

  return {
    addresses,
    loading,
    error,  
    fetchAddresses,
    addAddress,
    updateAddress,
    deleteAddress,
    setDefaultAddress,
    defaultAddress: addresses.find(a => a.isDefault) || null,
  };
}
