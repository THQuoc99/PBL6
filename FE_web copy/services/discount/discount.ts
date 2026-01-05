/**
 * Discount Service - Voucher API calls
 * Handles all voucher-related GraphQL queries and mutations
 */

import { ApiClient } from '../callAPI/apiClient';

const apiClient = ApiClient.getInstance();

// ================================================
// TYPES & INTERFACES
// ================================================

export interface Voucher {
  voucherId: string;
  code: string;
  name?: string;
  discountType: 'PERCENT' | 'FIXED' | 'FREESHIP';
  discountValue: string;
  minOrderAmount: string;
  maxDiscount?: string;
  description?: string;
  startDate: string;
  endDate: string;
  isActive: boolean;
  perUserLimit: number;
}

export interface UserVoucher {
  id: string;
  usedCount: number;
  savedAt: string;
  voucher: Voucher;
}

export interface ApplyVoucherResult {
  discountAmount: number;
  message: string;
}

// ================================================
// QUERY: Lấy tất cả voucher phù hợp với đơn hàng
// ================================================
export async function getAllApplicableVouchers(orderTotal: number): Promise<Voucher[]> {
  const query = `
    query AllApplicableVouchers($orderTotal: Float!) {
      allApplicableVouchers(orderTotal: $orderTotal) {
        voucherId
        code
        name
        discountType # 'PERCENT' | 'FIXED' | 'FREESHIP'(cái này sẽ hiển thị ở Voucher Vận chuyển)
        discountValue
        minOrderAmount
        maxDiscount
        description
        startDate
        endDate
        isActive
        perUserLimit
      }
    }
  `;

  try {
    console.log('Fetching applicable vouchers for order total:', orderTotal);
    const response = await apiClient.authenticatedApiCall(query, { orderTotal });
    
    if (response.errors) {
      console.error('Error fetching applicable vouchers:', response.errors);
      throw new Error(response.errors[0]?.message || 'Failed to fetch vouchers');
    }

    return response.data?.allApplicableVouchers || [];
  } catch (error) {
    console.error('getAllApplicableVouchers error:', error);
    throw error;
  }
}

// ================================================
// QUERY: Lấy voucher đã lưu
// ================================================
export async function getSavedVouchers(): Promise<UserVoucher[]> {
  const query = `
    query SavedVouchers {
      savedVouchers {
        id
        usedCount
        savedAt
        voucher {
          voucherId
          code
          name
          discountType
          discountValue
          minOrderAmount
          maxDiscount
          description
          startDate
          endDate
          isActive
          perUserLimit
        }
      }
    }
  `;

  try {
    const response = await apiClient.authenticatedApiCall(query);
    
    if (response.errors) {
      console.error('Error fetching saved vouchers:', response.errors);
      throw new Error(response.errors[0]?.message || 'Failed to fetch saved vouchers');
    }

    return response.data?.savedVouchers || [];
  } catch (error) {
    console.error('getSavedVouchers error:', error);
    throw error;
  }
}

// ================================================
// QUERY: Lấy voucher platform chưa lưu
// ================================================
export async function getAvailablePlatformVouchers(): Promise<Voucher[]> {
  const query = `
    query AvailablePlatformVouchers {
      availablePlatformVouchers {
        voucherId
        code
        name
        discountType
        discountValue
        minOrderAmount
        maxDiscount
        description
        startDate
        endDate
        isActive
        perUserLimit
      }
    }
  `;

  try {
    const response = await apiClient.authenticatedApiCall(query);
    
    if (response.errors) {
      console.error('Error fetching platform vouchers:', response.errors);
      throw new Error(response.errors[0]?.message || 'Failed to fetch platform vouchers');
    }

    return response.data?.availablePlatformVouchers || [];
  } catch (error) {
    console.error('getAvailablePlatformVouchers error:', error);
    throw error;
  }
}

// ================================================
// QUERY: Lấy voucher cho product
// ================================================
export async function getVouchersForProduct(productId: string): Promise<Voucher[]> {
  const query = `
    query VouchersForProduct($productId: ID!) {
      vouchersForProduct(productId: $productId) {
        voucherId
        code
        name
        discountType
        discountValue
        minOrderAmount
        maxDiscount
        description
      }
    }
  `;

  try {
    const response = await apiClient.authenticatedApiCall(query, { productId });
    
    if (response.errors) {
      console.error('Error fetching vouchers for product:', response.errors);
      throw new Error(response.errors[0]?.message || 'Failed to fetch product vouchers');
    }

    return response.data?.vouchersForProduct || [];
  } catch (error) {
    console.error('getVouchersForProduct error:', error);
    throw error;
  }
}

// ================================================
// QUERY: Lấy voucher cho store
// Nếu truyền storeId sẽ lấy voucher của store đó;
// nếu không truyền sẽ lấy voucher cho store(s) của user trên server
// ================================================
export async function getVouchersForStore(storeId?: string): Promise<Voucher[]> {
  const query = `
    query VouchersForStore($storeId: ID) {
      vouchersForStore(storeId: $storeId) {
        voucherId
        code
        name
        discountType
        discountValue
        minOrderAmount
        maxDiscount
        description
        startDate
        endDate
        isActive
        perUserLimit
      }
    }
  `;

  try {
    const variables = storeId ? { storeId } : {};
    const response = await apiClient.authenticatedApiCall(query, variables);

    if (response.errors) {
      console.error('Error fetching store vouchers:', response.errors);
      throw new Error(response.errors[0]?.message || 'Failed to fetch store vouchers');
    }

    return response.data?.vouchersForStore || [];
  } catch (error) {
    console.error('getVouchersForStore error:', error);
    throw error;
  }
}

// ================================================
// MUTATION: Áp dụng voucher
// ================================================
export async function applyVoucher(
  voucherCode: string, 
  orderTotal: number
): Promise<ApplyVoucherResult> {
  const mutation = `
    mutation ApplyVoucher($code: String!, $orderTotal: Float!) {
      applyVoucher(voucherCode: $code, orderTotal: $orderTotal) {
        discountAmount
        message
      }
    }
  `;

  try {
    const response = await apiClient.authenticatedApiCall(mutation, {
      code: voucherCode,
      orderTotal
    });
    
    if (response.errors) {
      console.error('Error applying voucher:', response.errors);
      throw new Error(response.errors[0]?.message || 'Failed to apply voucher');
    }

    return response.data?.applyVoucher || { discountAmount: 0, message: 'Error' };
  } catch (error) {
    console.error('applyVoucher error:', error);
    throw error;
  }
}

// ================================================
// MUTATION: Lưu voucher
// ================================================
export async function saveVoucher(voucherId?: string, code?: string): Promise<{ ok: boolean; userVoucher?: UserVoucher }> {
  const mutation = `
    mutation SaveVoucher($voucherId: ID, $code: String) {
      saveVoucher(voucherId: $voucherId, code: $code) {
        ok
        userVoucher {
          id
          usedCount
          savedAt
          voucher {
            voucherId
            code
            name
            discountType
            discountValue
          }
        }
      }
    }
  `;

  try {
    const response = await apiClient.authenticatedApiCall(mutation, { voucherId, code });

    if (response.errors) {
      console.error('Error saving voucher:', response.errors);
      throw new Error(response.errors[0]?.message || 'Failed to save voucher');
    }

    return response.data?.saveVoucher || { ok: false };
  } catch (error) {
    console.error('saveVoucher error:', error);
    throw error;
  }
}

// ================================================
// MUTATION: Sử dụng voucher
// ================================================
export async function useVoucher(
  voucherId: string,
  discountAmount: number,
  orderId: string
): Promise<{ ok: boolean; message: string }> {
  const mutation = `
    mutation UseVoucher($voucherId: ID!, $discountAmount: Float!, $orderId: ID!) {
      useVoucher(
        voucherId: $voucherId,
        discountAmount: $discountAmount,
        orderId: $orderId
      ) {
        ok
        message
      }
    }
  `;

  try {
    const response = await apiClient.authenticatedApiCall(mutation, {
      voucherId,
      discountAmount,
      orderId
    });
    
    if (response.errors) {
      console.error('Error using voucher:', response.errors);
      throw new Error(response.errors[0]?.message || 'Failed to use voucher');
    }

    return response.data?.useVoucher || { ok: false, message: 'Error' };
  } catch (error) {
    console.error('useVoucher error:', error);
    throw error;
  }
}

// ================================================
// MUTATION: Tạo voucher cho cửa hàng
// ================================================
export async function createStoreVoucher(storeId: string, data: any): Promise<{ ok: boolean; voucher?: any }> {
  const mutation = `
    mutation CreateStoreVoucher($storeId: ID!, $data: VoucherInput!) {
      createStoreVoucher(storeId: $storeId, data: $data) {
        ok
        voucher { voucherId code type }
      }
    }
  `;

  try {
    const response = await apiClient.authenticatedApiCall(mutation, { storeId, data });

    if (response.errors) {
      console.error('Error creating store voucher:', response.errors);
      throw new Error(response.errors[0]?.message || 'Failed to create store voucher');
    }

    return response.data?.createStoreVoucher || { ok: false };
  } catch (error) {
    console.error('createStoreVoucher error:', error);
    throw error;
  }
}

// ================================================
// MUTATION: Cập nhật voucher
// ================================================
export async function updateVoucher(voucherId: string, data: any): Promise<{ ok: boolean; voucher?: any }> {
  const mutation = `
    mutation UpdateVoucher($voucherId: ID!, $data: UpdateVoucherInput!) {
      updateVoucher(voucherId: $voucherId, data: $data) {
        ok
        voucher { voucherId code discountValue }
      }
    }
  `;

  try {
    const response = await apiClient.authenticatedApiCall(mutation, { voucherId, data });

    if (response.errors) {
      console.error('Error updating voucher:', response.errors);
      throw new Error(response.errors[0]?.message || 'Failed to update voucher');
    }

    return response.data?.updateVoucher || { ok: false };
  } catch (error) {
    console.error('updateVoucher error:', error);
    throw error;
  }
}
