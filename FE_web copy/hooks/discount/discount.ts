/**
 * Discount Hooks - Custom hooks for voucher management
 * Provides state management and API integration for vouchers
 */

import { useState, useEffect, useCallback } from 'react';
import {
  Voucher,
  UserVoucher,
  getAllApplicableVouchers,
  getSavedVouchers,
  getAvailablePlatformVouchers,
  getVouchersForProduct,
  getVouchersForStore,
  applyVoucher as applyVoucherService,
  saveVoucher as saveVoucherService,
  useVoucher as useVoucherService,
  createStoreVoucher as createStoreVoucherService,
  updateVoucher as updateVoucherService,
} from '../../services/discount/discount';

// ================================================
// Hook: Lấy tất cả voucher phù hợp với đơn hàng
// ================================================
export function useApplicableVouchers(orderTotal: number) {
  const [vouchers, setVouchers] = useState<Voucher[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchVouchers = useCallback(async () => {
    if (orderTotal <= 0) {
      setVouchers([]);
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const data = await getAllApplicableVouchers(orderTotal);
      setVouchers(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch vouchers');
      console.error('useApplicableVouchers error:', err);
    } finally {
      setLoading(false);
    }
  }, [orderTotal]);

  useEffect(() => {
    fetchVouchers();
  }, [fetchVouchers]);

  return {
    vouchers,
    loading,
    error,
    refetch: fetchVouchers,
  };
}

// ================================================
// Hook: Lấy voucher đã lưu
// ================================================
export function useSavedVouchers() {
  const [savedVouchers, setSavedVouchers] = useState<UserVoucher[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSavedVouchers = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await getSavedVouchers();
      setSavedVouchers(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch saved vouchers');
      console.error('useSavedVouchers error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSavedVouchers();
  }, [fetchSavedVouchers]);

  return {
    savedVouchers,
    loading,
    error,
    refetch: fetchSavedVouchers,
  };
}

// ================================================
// Hook: Lấy voucher platform
// ================================================
export function usePlatformVouchers() {
  const [platformVouchers, setPlatformVouchers] = useState<Voucher[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPlatformVouchers = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await getAvailablePlatformVouchers();
      setPlatformVouchers(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch platform vouchers');
      console.error('usePlatformVouchers error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPlatformVouchers();
  }, [fetchPlatformVouchers]);

  return {
    platformVouchers,
    loading,
    error,
    refetch: fetchPlatformVouchers,
  };
}

// ================================================
// Hook: Lấy voucher cho product
// ================================================
export function useProductVouchers(productId: string) {
  const [vouchers, setVouchers] = useState<Voucher[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchVouchers = useCallback(async () => {
    if (!productId) {
      setVouchers([]);
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const data = await getVouchersForProduct(productId);
      setVouchers(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch product vouchers');
      console.error('useProductVouchers error:', err);
    } finally {
      setLoading(false);
    }
  }, [productId]);

  useEffect(() => {
    fetchVouchers();
  }, [fetchVouchers]);

  return {
    vouchers,
    loading,
    error,
    refetch: fetchVouchers,
  };
}

// ================================================
// Hook: Lấy voucher cho cửa hàng
// Nếu storeId không truyền, server sẽ lấy theo membership của user
// ================================================
export function useStoreVouchers(storeId?: string) {
  const [vouchers, setVouchers] = useState<Voucher[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchVouchers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getVouchersForStore(storeId);
      setVouchers(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch store vouchers');
      console.error('useStoreVouchers error:', err);
    } finally {
      setLoading(false);
    }
  }, [storeId]);

  useEffect(() => {
    fetchVouchers();
  }, [fetchVouchers]);

  return {
    vouchers,
    loading,
    error,
    refetch: fetchVouchers,
  };
}

// ================================================
// Hook: Áp dụng voucher
// ================================================
export function useApplyVoucher() {
  const [applying, setApplying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const applyVoucher = useCallback(async (voucherCode: string, orderTotal: number) => {
    setApplying(true);
    setError(null);
    try {
      const result = await applyVoucherService(voucherCode, orderTotal);
      return result;
    } catch (err: any) {
      setError(err.message || 'Failed to apply voucher');
      console.error('useApplyVoucher error:', err);
      throw err;
    } finally {
      setApplying(false);
    }
  }, []);

  return {
    applyVoucher,
    applying,
    error,
  };
}

// ================================================
// Hook: Lưu voucher
// ================================================
export function useSaveVoucher() {
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const saveVoucher = useCallback(async (voucherId?: string, code?: string) => {
    setSaving(true);
    setError(null);
    
    try {
      const result = await saveVoucherService(voucherId, code);
      return result;
    } catch (err: any) {
      setError(err.message || 'Failed to save voucher');
      console.error('useSaveVoucher error:', err);
      throw err;
    } finally {
      setSaving(false);
    }
  }, []);

  return {
    saveVoucher,
    saving,
    error,
  };
}

// ================================================
// Hook: Sử dụng voucher
// ================================================
export function useUseVoucher() {
  const [using, setUsing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const useVoucher = useCallback(async (
    voucherId: string,
    discountAmount: number,
    orderId: string
  ) => {
    setUsing(true);
    setError(null);
    
    try {
      const result = await useVoucherService(voucherId, discountAmount, orderId);
      return result;
    } catch (err: any) {
      setError(err.message || 'Failed to use voucher');
      console.error('useUseVoucher error:', err);
      throw err;
    } finally {
      setUsing(false);
    }
  }, []);

  return {
    useVoucher,
    using,
    error,
  };
}

// ================================================
// Hook: Tạo voucher cho cửa hàng
// ================================================
export function useCreateStoreVoucher() {
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const create = useCallback(async (storeId: string, data: any) => {
    setCreating(true);
    setError(null);
    try {
      const res = await createStoreVoucherService(storeId, data);
      return res;
    } catch (err: any) {
      setError(err.message || 'Failed to create store voucher');
      console.error('useCreateStoreVoucher error:', err);
      throw err;
    } finally {
      setCreating(false);
    }
  }, []);

  return {
    createStoreVoucher: create,
    creating,
    error,
  };
}

// ================================================
// Hook: Cập nhật voucher
// ================================================
export function useUpdateVoucher() {
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const update = useCallback(async (voucherId: string, data: any) => {
    setUpdating(true);
    setError(null);
    try {
      const res = await updateVoucherService(voucherId, data);
      return res;
    } catch (err: any) {
      setError(err.message || 'Failed to update voucher');
      console.error('useUpdateVoucher error:', err);
      throw err;
    } finally {
      setUpdating(false);
    }
  }, []);

  return {
    updateVoucher: update,
    updating,
    error,
  };
}

// ================================================
// Hook: Quản lý voucher cho payment page
// ================================================
export function useVoucherManagement(orderTotal: number) {
  // Lấy tất cả voucher phù hợp
  const { 
    vouchers: applicableVouchers, 
    loading: loadingApplicable,
    refetch: refetchApplicable
  } = useApplicableVouchers(orderTotal);

  // Hook apply voucher
  const { applyVoucher, applying } = useApplyVoucher();

  // State cho voucher đã chọn
  const [selectedDiscountVoucher, setSelectedDiscountVoucher] = useState<Voucher | null>(null);
  const [selectedShippingVoucher, setSelectedShippingVoucher] = useState<Voucher | null>(null);
  const [discountAmount, setDiscountAmount] = useState(0);
  const [shippingDiscount, setShippingDiscount] = useState(0);

  // Phân loại voucher
  const discountVouchers = applicableVouchers.filter(
    v => v.discountType === 'PERCENT' || v.discountType === 'FIXED'
  );
  const shippingVouchers = applicableVouchers.filter(
    v => v.discountType === 'FREESHIP'
  );

  // Apply discount voucher
  const applyDiscountVoucher = useCallback(async (voucher: Voucher) => {
    try {
      const result = await applyVoucher(voucher.code, orderTotal);
      setSelectedDiscountVoucher(voucher);
      setDiscountAmount(result.discountAmount);
      return result;
    } catch (err) {
      console.error('Error applying discount voucher:', err);
      throw err;
    }
  }, [applyVoucher, orderTotal]);

  // Apply shipping voucher
  const applyShippingVoucher = useCallback(async (voucher: Voucher, shippingCost: number) => {
    try {
      const result = await applyVoucher(voucher.code, orderTotal);
      setSelectedShippingVoucher(voucher);
      // Shipping discount không được vượt quá shipping cost
      setShippingDiscount(Math.min(result.discountAmount, shippingCost));
      return result;
    } catch (err) {
      console.error('Error applying shipping voucher:', err);
      throw err;
    }
  }, [applyVoucher, orderTotal]);

  // Clear voucher
  const clearDiscountVoucher = useCallback(() => {
    setSelectedDiscountVoucher(null);
    setDiscountAmount(0);
  }, []);

  const clearShippingVoucher = useCallback(() => {
    setSelectedShippingVoucher(null);
    setShippingDiscount(0);
  }, []);

  const clearAllVouchers = useCallback(() => {
    clearDiscountVoucher();
    clearShippingVoucher();
  }, [clearDiscountVoucher, clearShippingVoucher]);

  return {
    // Vouchers
    discountVouchers,
    shippingVouchers,
    
    // Selected vouchers
    selectedDiscountVoucher,
    selectedShippingVoucher,
    
    // Discount amounts
    discountAmount,
    shippingDiscount,
    
    // Loading states
    loading: loadingApplicable || applying,
    
    // Actions
    applyDiscountVoucher,
    applyShippingVoucher,
    clearDiscountVoucher,
    clearShippingVoucher,
    clearAllVouchers,
    refetchVouchers: refetchApplicable,
  };
}
