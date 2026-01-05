import { apiClient } from '../callAPI/apiClient';

/** Vouchers service for admin */
export async function fetchAdminVouchers(query: Record<string, any> = {}) {
  const gqlQuery = `
    query AdminVouchers {
      adminVouchers {
        voucherId
        code
        name
        type
        discountType
        discountValue
        description
        minOrderAmount
        maxDiscount
        startDate
        endDate
        usageLimit
        perUserLimit
        timesUsed
        isActive
        createdAt
      }
    }
  `;

  try {
    const response = await apiClient.authenticatedApiCall(gqlQuery);
    if (response.errors) {
      throw new Error(response.errors[0]?.message || 'GraphQL Error');
    }
    return {
      items: response.data.adminVouchers,
      total: response.data.adminVouchers.length
    };
  } catch (err) {
    console.error("Failed to fetch admin vouchers", err);
    throw err;
  }
}

export async function toggleVoucher(voucherId: number) {
  const mutation = `
    mutation ToggleVoucher($voucherId: ID!) {
      toggleVoucher(voucherId: $voucherId) {
        success
        message
      }
    }
  `;

  try {
    const response = await apiClient.authenticatedApiCall(mutation, { voucherId: voucherId.toString() });
    if (response.errors) {
      throw new Error(response.errors[0]?.message || 'GraphQL Error');
    }
    return response.data.toggleVoucher;
  } catch (err) {
    console.error("Failed to toggle voucher", err);
    throw err;
  }
}

export async function deleteVoucher(voucherId: number) {
  const mutation = `
    mutation DeleteVoucher($voucherId: ID!) {
      deleteVoucher(voucherId: $voucherId) {
        success
        message
      }
    }
  `;

  try {
    const response = await apiClient.authenticatedApiCall(mutation, { voucherId: voucherId.toString() });
    if (response.errors) {
      throw new Error(response.errors[0]?.message || 'GraphQL Error');
    }
    return response.data.deleteVoucher;
  } catch (err) {
    console.error("Failed to delete voucher", err);
    throw err;
  }
}

export async function createVoucher(payload: any) {
  const mutation = `
    mutation CreateAdminVoucher(
      $code: String!
      $name: String!
      $type: String!
      $discountType: String!
      $discountValue: Decimal!
      $description: String
      $minOrderAmount: Decimal!
      $maxDiscount: Decimal
      $startDate: Date!
      $endDate: Date!
      $usageLimit: Int
      $perUserLimit: Int!
      $isActive: Boolean
    ) {
      createAdminVoucher(
        code: $code
        name: $name
        type: $type
        discountType: $discountType
        discountValue: $discountValue
        description: $description
        minOrderAmount: $minOrderAmount
        maxDiscount: $maxDiscount
        startDate: $startDate
        endDate: $endDate
        usageLimit: $usageLimit
        perUserLimit: $perUserLimit
        isActive: $isActive
      ) {
        success
        message
        voucher {
          voucherId
          code
        }
      }
    }
  `;

  try {
    const response = await apiClient.authenticatedApiCall(mutation, payload);
    if (response.errors) {
      throw new Error(response.errors[0]?.message || 'GraphQL Error');
    }
    return response.data.createAdminVoucher;
  } catch (err) {
    console.error("Failed to create voucher", err);
    throw err;
  }
}

export async function updateVoucher(voucherId: number, payload: any) {
  const mutation = `
    mutation UpdateAdminVoucher(
      $voucherId: ID!
      $code: String
      $name: String
      $type: String
      $discountType: String
      $discountValue: Decimal
      $description: String
      $minOrderAmount: Decimal
      $maxDiscount: Decimal
      $startDate: Date
      $endDate: Date
      $usageLimit: Int
      $perUserLimit: Int
      $isActive: Boolean
    ) {
      updateAdminVoucher(
        voucherId: $voucherId
        code: $code
        name: $name
        type: $type
        discountType: $discountType
        discountValue: $discountValue
        description: $description
        minOrderAmount: $minOrderAmount
        maxDiscount: $maxDiscount
        startDate: $startDate
        endDate: $endDate
        usageLimit: $usageLimit
        perUserLimit: $perUserLimit
        isActive: $isActive
      ) {
        success
        message
        voucher {
          voucherId
          code
        }
      }
    }
  `;

  try {
    const response = await apiClient.authenticatedApiCall(mutation, { voucherId: voucherId.toString(), ...payload });
    if (response.errors) {
      throw new Error(response.errors[0]?.message || 'GraphQL Error');
    }
    return response.data.updateAdminVoucher;
  } catch (err) {
    console.error("Failed to update voucher", err);
    throw err;
  }
}

export async function fetchAdminVoucherById(id: number) {
  const gqlQuery = `
    query AdminVoucherById($voucherId: ID!) {
      adminVoucherById(voucherId: $voucherId) {
        voucherId
        code
        name
        type
        discountType
        discountValue
        description
        minOrderAmount
        maxDiscount
        startDate
        endDate
        usageLimit
        perUserLimit
        timesUsed
        isActive
        createdAt
      }
    }
  `;

  try {
    const response = await apiClient.authenticatedApiCall(gqlQuery, { voucherId: id.toString() });
    if (response.errors) {
      throw new Error(response.errors[0]?.message || 'GraphQL Error');
    }
    return response.data.adminVoucherById;
  } catch (err) {
    console.error(`Failed to fetch voucher ${id}`, err);
    return null;
  }
}
