// services/store.ts
import { AuthService } from './auth';

const authService = AuthService.getInstance();

// Key lưu trữ trong localStorage
const CURRENT_STORE_KEY = 'currentStore';

interface StoreCreateInput {
  name: string;
  email?: string;
  phone?: string;
  province: string;
  ward: string;
  hamlet?: string;
  detail: string;
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
  private saveStoreToStorage(store: any): void {
    localStorage.setItem(CURRENT_STORE_KEY, JSON.stringify(store));
  }

  // Xóa store khỏi localStorage (dùng khi logout hoặc xóa shop)
  clearCurrentStore(): void {
    localStorage.removeItem(CURRENT_STORE_KEY);
  }

  // Lấy store hiện tại (ưu t iên localStorage → mới gọi API nếu chưa có)
  async getCurrentStore(): Promise<any | null> {
    // 1. Ưu tiên lấy từ localStorage
    const cached = this.getStoredStore();
    if (cached) {
      console.log('Store từ localStorage:', cached.name);
      return cached;
    }
    const userId = authService.getCurrentUser()?.id;
    if (!userId) {
      console.log('Không có userId, không thể lấy store');
      return null;
    }
    console.log('userId:', userId);
    // 2. Nếu chưa có thì gọi API
    return await this.loadMyOwnedStore(userId);
  }

  // Lấy cửa hàng mà user là owner + tự động lưu vào localStorage
  async loadMyOwnedStore(userId?: string): Promise<any | null> {
    console.log('Đang load myOwnedStore từ API với userId:', userId);
    const query = `
      query  {
        myOwnedStore(userId: ${userId}) {
          storeId
          name
          slug
          email
          phone
          avatar
          coverImage
          currency
          joinDate
          isActive
        }
      }
    `;

    try {
      const variables = userId ? { userId } : {};
      const result = await authService.apiCall(query, variables);
      const store = result.data?.myOwnedStore;

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
    const query = `
      mutation CreateStore($input: StoreCreateInput!) {
        createStore(input: $input) {
          success
          message
          store {
            storeId
            name
            slug
            email
            phone
            avatar
            coverImage
            currency
            joinDate
            isActive
          }
        }
      }
    `;

    try {
      const result = await authService.apiCall(query, { input });
      const response = result.data.createStore;

      if (response.success && response.store) {
        this.saveStoreToStorage(response.store); // LƯU NGAY SAU KHI TẠO
        console.log('Tạo store thành công & đã lưu:', response.store.name);
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
          phone
          avatar
          coverImage
          description
          currency
          joinDate
          rating
          totalReviews
          followersCount
          productsCount
          isVerified
          isActive
        }
      }
    `;

    try {
      const result = await authService.apiCall(query, { storeId });
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
            phone
            currency
          }
        }
      }
    `;

    try {
      const result = await authService.apiCall(query, { storeId, input });
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
    const query = `query($storeId: String) { addressStores(storeId: $storeId) { addressId province ward hamlet detail isDefault } }`;
    const variables = storeId ? { storeId } : {};
    const result = await authService.apiCall(query, variables);
    return result.data?.addressStores || [];
  }

  async getStoreMembers(storeId: string): Promise<any[]> {
    const query = `query($storeId: String!) { storeUsers(storeId: $storeId) { id role status user { id username fullName } } }`;
    const result = await authService.apiCall(query, { storeId });
    return result.data?.storeUsers || [];
  }

  async addStoreMember(input: { storeId: string; userId: string; role: string }): Promise<any> {
    const query = `mutation($input: StoreUserInput!) { createStoreUser(input: $input) { success message } }`;
    const result = await authService.apiCall(query, { input });
    return result.data?.createStoreUser || { success: false };
  }
}

// Export singleton
export const storeService = StoreService.getInstance();