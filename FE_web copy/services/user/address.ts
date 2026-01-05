import { apiClient } from '../callAPI/apiClient';

// =====================
// Address Interface
// =====================
export interface Address {
  addressId: string;
  name: string;               // NEW
  phoneNumber?: string;
  province: string;
  ward: string;
  hamlet?: string;
  detail: string;
  fullAddress: string;
  isDefault: boolean;
}

// =====================
// API Response Interfaces
// =====================
export interface AddressResult {
  success: boolean;
  errors?: string[];
  address?: Address;
}

export interface AddressListResult {
  myAddresses: Address[];
}

// =====================
// Address Service
// =====================
export class AddressService {
  private static instance: AddressService;

  private constructor() {}

  static getInstance(): AddressService {
    if (!AddressService.instance) {
      AddressService.instance = new AddressService();
    }
    return AddressService.instance;
  }

  // ============================================================
  // Lấy danh sách địa chỉ của user
  // ============================================================
  async getAddresses(): Promise<Address[]> {
    const query = `
      query {
        myAddresses {
          addressId
          name
          phoneNumber
          province
          ward
          hamlet
          detail
          fullAddress
          isDefault
        }
      }
    `;

    const result = await apiClient.authenticatedApiCall(query);
    return (result.data as AddressListResult)?.myAddresses || [];
  }

  // ============================================================
  // Lấy địa chỉ mặc định
  // ============================================================
  async getDefaultAddress(): Promise<Address | null> {
    const query = `
      query {
        myDefaultAddress {
          addressId
          name
          phoneNumber
          province
          ward
          hamlet
          detail
          fullAddress
          isDefault
        }
      }
    `;

    const result = await apiClient.authenticatedApiCall(query);
    return (result.data as { myDefaultAddress: Address })?.myDefaultAddress || null;
  }

  // ============================================================
  // Thêm địa chỉ mới
  // ============================================================
  async addAddress(input: {
    name: string;
    phoneNumber?: string;
    province: string;
    ward: string;
    hamlet?: string;
    detail: string;
    isDefault?: boolean;
  }): Promise<AddressResult> {

    const mutation = `
      mutation AddAddress($input: AddAddressMutationInput!) {
        addAddress(input: $input) {
          success
          errors
          address {
            addressId
            name
            phoneNumber
            province
            ward
            hamlet
            detail
            fullAddress
            isDefault
          }
        }
      }
    `;

    const result = await apiClient.authenticatedApiCall(mutation, { input });

    return (
      (result.data as { addAddress: AddressResult })?.addAddress ||
      { success: false, errors: ['Unknown error'] }
    );
  }

  // ============================================================
  // Cập nhật địa chỉ
  // ============================================================
  async updateAddress(input: {
    addressId: number;
    name?: string;
    phoneNumber?: string;
    province?: string;
    ward?: string;
    hamlet?: string;
    detail?: string;
    isDefault?: boolean;
  }): Promise<AddressResult> {

    const mutation = `
      mutation UpdateAddress($input: UpdateAddressMutationInput!) {
        updateAddress(input: $input) {
          success
          errors
          address {
            addressId
            name
            phoneNumber
            province
            ward
            hamlet
            detail
            fullAddress
            isDefault
          }
        }
      }
    `;

    const result = await apiClient.authenticatedApiCall(mutation, { input });

    return (
      (result.data as { updateAddress: AddressResult })?.updateAddress ||
      { success: false, errors: ['Unknown error'] }
    );
  }

  // ============================================================
  // Xóa địa chỉ
  // ============================================================
  async deleteAddress(addressId: number): Promise<{ success: boolean; errors?: string[] }> {
    const mutation = `
      mutation DeleteAddress($input: DeleteAddressMutationInput!) {
        deleteAddress(input: $input) {
          success
          errors
        }
      }
    `;

    const result = await apiClient.authenticatedApiCall(mutation, {
      input: { addressId }
    });

    return (
      (result.data as { deleteAddress: { success: boolean; errors?: string[] } })?.deleteAddress ||
      { success: false, errors: ['Unknown error'] }
    );
  }

  // ============================================================
  // Đặt địa chỉ làm mặc định
  // ============================================================
  async setDefaultAddress(addressId: number): Promise<AddressResult> {
    const mutation = `
      mutation SetDefaultAddress($input: SetDefaultAddressMutationInput!) {
        setDefaultAddress(input: $input) {
          success
          errors
          address {
            addressId
            name
            fullAddress
            isDefault
          }
        }
      }
    `;

    const result = await apiClient.authenticatedApiCall(mutation, {
      input: { addressId }
    });

    return (
      (result.data as { setDefaultAddress: AddressResult })?.setDefaultAddress ||
      { success: false, errors: ['Unknown error'] }
    );
  }
}

export const addressService = AddressService.getInstance();
