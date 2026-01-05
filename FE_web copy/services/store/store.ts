// services/store.ts
import { apiClient } from '../callAPI/apiClient';

const CURRENT_STORE_KEY = 'currentStore';

interface StoreCreateInput {
  name: string;
  email?: string;
  description?: string;
  // Allow creating store with multiple addresses
  addresses?: Array<{
    province: string;
    ward: string;
    hamlet?: string;
    detail: string;
    phone?: string;
    // GraphQL expects camelCase `isDefault` (Graphene converts names)
    isDefault?: boolean;
  }>;
}

interface StoreResponse {
  success: boolean;
  message: string;
  store?: any;
  errors?: any;
}

export class StoreService {
  private static instance: StoreService;

  static getInstance(): StoreService {
    if (!StoreService.instance) {
      StoreService.instance = new StoreService();
    }
    return StoreService.instance;
  }

  // Lấy store từ localStorage
  private getStoredStore(): any | null {
    try {
      const stored = localStorage.getItem(CURRENT_STORE_KEY);
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  }

  // Lưu store vào localStorage
  // Lưu store vào localStorage
  // Nếu đã có store cũ, merge giữ lại các trường không có trong payload mới
  private saveStoreToStorage(store: any): void {
    try {
      const existing = this.getStoredStore() || {};
      // shallow merge: prefer new values, but keep existing keys when missing
      const merged = { ...existing, ...(store || {}) };
      localStorage.setItem(CURRENT_STORE_KEY, JSON.stringify(merged));
    } catch (e) {
      try { localStorage.setItem(CURRENT_STORE_KEY, JSON.stringify(store)); } catch (_) { /* ignore */ }
    }
  }

  // Xóa store khỏi localStorage (dùng khi logout hoặc xóa shop)
  clearCurrentStore(): void {
    localStorage.removeItem(CURRENT_STORE_KEY);
  }

  // Lấy store hiện tại.
  // Mặc định gọi API để đảm bảo đồng bộ server ↔ client; truyền forceRefresh=false để ưu tiên cache.
  async getCurrentStore(forceRefresh = true): Promise<any | null> {
    if (!forceRefresh) {
      const cached = this.getStoredStore();
      if (cached) {
        console.log('Store từ localStorage (cache):', cached.name);
        return cached;
      }
    }
    // Lấy tươi từ server
    return await this.loadMyOwnedStore();
  }

  // Lấy cửa hàng mà user là owner + tự động lưu vào localStorage
  async loadMyOwnedStore(): Promise<any | null> {
    console.log('Đang load myOwnedStore từ API');
    const query = `
      query  {
        myOwnedStore {
          storeId
          name
          slug
          email
          avatar
          coverImage
          logo
          currency
          joinDate
          isActive
          addresses
            {
              addressId
              province
              ward
              hamlet
              detail
              isDefault
              phone
              fullAddress
            }
        }
      }
    `;

    try {
      const result = await apiClient.authenticatedApiCall(query);
      const store = result.data?.myOwnedStore;
      console.log('Kết quả myOwnedStore từ API:', store);
      if (store) {
        this.saveStoreToStorage(store); // LƯU NGAY KHI LẤY ĐƯỢC
        console.log('Đã lưu store vào localStorage:', store.name);
        return store;
      }

      return null;
    } catch (error) {
      console.error('Lỗi lấy myOwnedStore:', error);
      return null;
    }
  }

  // Tạo cửa hàng mới → lưu luôn vào localStorage
  async createStore(input: StoreCreateInput): Promise<StoreResponse> {
    // legacy compatibility: keep signature but forward to multipart handler without files
    return this.createStoreWithFiles(input, {});
  }

  async createStoreWithFiles(input: StoreCreateInput, files: { avatar?: File; coverImage?: File; logo?: File } = {}): Promise<StoreResponse> {
    const query = `
      mutation CreateStore($input: StoreCreateInput!, $avatar: Upload, $coverImage: Upload, $logo: Upload) {
        createStore(input: $input, avatar: $avatar, coverImage: $coverImage, logo: $logo) {
          success
          message
          store {
          storeId
          name
          slug
          email
          avatar
          coverImage
          logo
          currency
          joinDate
          isActive
          addresses
            {
              addressId
              province
              ward
              hamlet
              detail
              isDefault
              phone
              fullAddress
            }
          }
        }
      }
    `;

    // Normalize input to match backend GraphQL field names (camelCase)
    const normalizedInput = { ...input } as any;
    if (Array.isArray(input.addresses)) {
      // Graphene exposes fields in camelCase; send `isDefault`.
      normalizedInput.addresses = input.addresses.map((a: any) => {
        const mapped: any = {
          province: a.province,
          ward: a.ward,
          hamlet: a.hamlet,
          detail: a.detail,
        };
        if (a.phone !== undefined) mapped.phone = a.phone;
        if (a.isDefault !== undefined) mapped.isDefault = a.isDefault;
        else if (a.is_default !== undefined) mapped.isDefault = a.is_default;
        return mapped;
      });
    }

    // Build variables placeholder; file vars must exist with null value per multipart spec
    const variables: any = { input: normalizedInput, avatar: null, coverImage: null, logo: null };

    // Map input file keys to variable names expected by mutation
    const fileMap: { [key: string]: File } = {};
    if (files.avatar) fileMap['avatar'] = files.avatar;
    if (files.coverImage) fileMap['coverImage'] = files.coverImage;
    if (files.logo) fileMap['logo'] = files.logo;

    try {
      const result = await apiClient.authenticatedMultipartCall(query, variables, fileMap);
      console.debug('createStore raw response:', result);

      // If GraphQL errors exist, return them for easier debugging
      if (result && (result as any).errors) {
        console.error('GraphQL errors when creating store:', (result as any).errors);
        return { success: false, message: JSON.stringify((result as any).errors) };
      }

      const response = result?.data?.createStore;

      if (response && response.success && response.store) {
        this.saveStoreToStorage(response.store); // LƯU NGAY SAU KHI TẠO
        console.log('Tạo store thành công & đã lưu:', response.store.name);
      }

      if (!response) {
        console.warn('CreateStore returned no data.createStore, full response logged above');
        return { success: false, message: 'No response from server', errors: result };
      }

      return response;
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Lỗi kết nối server',
      };
    }
  }

  // Lấy chi tiết 1 cửa hàng bất kỳ
  async getStore(storeId: string): Promise<any | null> {
    const query = `
      query GetStore($storeId: ID!) {
        store(storeId: $storeId) {
          storeId
          name
          slug
          email
          avatar
          coverImage
          logo
          currency
          joinDate
          isActive
          addresses
            {
              addressId
              province
              ward
              hamlet
              detail
              isDefault
              phone
              fullAddress
            }
        }
      }
    `;

    try {
      const result = await apiClient.authenticatedApiCall(query, { storeId });
      return result.data?.store || null;
    } catch (error) {
      console.error('Lỗi lấy store:', error);
      return null;
    }
  }

  // Cập nhật store (nếu là owner thì cập nhật luôn localStorage)
  async updateStore(storeId: string, input: any): Promise<StoreResponse> {
    const query = `
      mutation UpdateStore($storeId: ID!, $input: StoreUpdateInput!) {
        updateStore(storeId: $storeId, input: $input) {
          success
          message
          store {
          storeId
          name
          slug
          email
          avatar
          coverImage
          logo
          currency
          joinDate
          isActive
          addresses
            {
              addressId
              province
              ward
              hamlet
              detail
              isDefault
              phone
              fullAddress
            }
          }
        }
      }
    `;

    try {
      const result = await apiClient.authenticatedApiCall(query, { storeId, input });
      const response = result.data.updateStore;

      if (response.success && response.store) {
        // Nếu là cửa hàng hiện tại → cập nhật luôn localStorage
        const current = this.getStoredStore();
        if (current && current.storeId === storeId) {
          this.saveStoreToStorage(response.store);
        }
      }

      return response;
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Lỗi cập nhật',
      };
    }
  }

  // Các hàm khác giữ nguyên (getAddressStores, getStoreMembers, addStoreMember, ...)
  async getAddressStores(storeId?: string): Promise<any[]> {
    const query = `query($storeId: String) { addressStores(storeId: $storeId) { addressId province ward hamlet detail isDefault phone fullAddress } }`;
    const variables = storeId ? { storeId } : {};
    const result = await apiClient.authenticatedApiCall(query, variables);
    return result.data?.addressStores || [];
  }

  async addAddressStore(storeId: string, input: any): Promise<any> {
    const query = `
      mutation CreateAddressStore($storeId: String!, $input: AddressStoreInput!) {
        createAddressStore(storeId: $storeId, input: $input) {
          success
          message
          address { addressId province ward hamlet detail isDefault phone fullAddress }
        }
      }
    `;
    try {
      const res = await apiClient.authenticatedApiCall(query, { storeId, input });
      return res.data?.createAddressStore || { success: false, message: 'No response' };
    } catch (e) {
      return { success: false, message: e instanceof Error ? e.message : String(e) };
    }
  }

  async updateAddressStore(storeId: string, input: any): Promise<any> {
    const query = `
      mutation UpdateAddressStore($input: AddressStoreInput!, $storeId: ID) {
        updateAddressStore(input: $input, storeId: $storeId) {
          success
          message
          address { addressId province ward hamlet detail isDefault phone fullAddress }
        }
      }
    `;
    // normalize input to camelCase and ensure addressId is present inside input
    console.debug('updateAddressStore - original input:', input);
    const normalizedInput: any = { ...(input || {}) };
    // support legacy snake_case coming from other code paths
    if (!normalizedInput.addressId && normalizedInput.address_id) normalizedInput.addressId = String(normalizedInput.address_id);
    // default false when undefined
    if (typeof normalizedInput.isDefault === 'undefined') normalizedInput.isDefault = false;

    try {
      const variables = { input: normalizedInput, storeId };
      const result = await apiClient.authenticatedApiCall(query, variables);
      if (result && result.errors) return { success: false, message: result.errors };
      return result.data?.updateAddressStore || { success: false, message: 'No response' };
    } catch (e) {
      return { success: false, message: e instanceof Error ? e.message : String(e) };
    }
  }

  async deleteAddressStore(addressId: string): Promise<any> {
    const query = `
      mutation DeleteAddressStore($addressId: ID!) {
        deleteAddressStore(addressId: $addressId) {
          success
          message
        }
      }
    `;
    try {
      const res = await apiClient.authenticatedApiCall(query, { addressId });
      return res.data?.deleteAddressStore || { success: false, message: 'No response' };
    } catch (e) {
      return { success: false, message: e instanceof Error ? e.message : String(e) };
    }
  }

  async setDefaultAddress(addressId: string): Promise<any> {
    const query = `
      mutation SetDefaultAddress($addressId: ID!) {
        setDefaultAddress(addressId: $addressId) {
          success
          message
          address {
            addressId
            isDefault
            fullAddress
            province
            ward
            hamlet
            phone
          }
        }
      }
    `;
    const variables = { addressId };
    try {
      const res = await apiClient.authenticatedApiCall(query, variables);
      console.debug('setDefaultAddress raw response:', res);
      if (res && res.errors) {
        console.error('GraphQL errors when calling setDefaultAddress:', res.errors);
        return { success: false, message: JSON.stringify(res.errors) };
      }
      return res?.data?.setDefaultAddress || { success: false, message: 'No response' };
    } catch (e) {
      console.error('Exception in setDefaultAddress:', e);
      return { success: false, message: e instanceof Error ? e.message : String(e) };
    }
  }

  async getStoreMembers(storeId: string): Promise<any[]> {
    const query = `query($storeId: String!) { storeUsers(storeId: $storeId) { id role status user { id username fullName } } }`;
    const result = await apiClient.authenticatedApiCall(query, { storeId });
    return result.data?.storeUsers || [];
  }

  async addStoreMember(input: { storeId: string; userId: string; role: string }): Promise<any> {
    const query = `mutation($input: StoreUserInput!) { createStoreUser(input: $input) { success message } }`;
    const result = await apiClient.authenticatedApiCall(query, { input });
    return result.data?.createStoreUser || { success: false };
  }
}

// Export singleton
export const storeService = StoreService.getInstance();