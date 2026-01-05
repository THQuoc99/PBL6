/**
 * React Hook cho Store Authentication
 */
import { useState, useEffect } from 'react';
import { useAuth } from '../user/useAuth';
import { storeService } from '../../services/store/store';
import { authService } from '../../services/user/auth';
interface StoreAddress {
  addressId: string;
  province: string;
  ward: string;
  hamlet?: string;
  detail: string;
  isDefault: boolean;
  phone?: string;
  fullAddress: string;
}

interface Store {
  storeId: string;
  name: string;
  slug: string;
  email?: string;
  avatar?: string;
  coverImage?: string;
  logo?: string;

  currency?: string;
  joinDate?: string;
  isActive?: boolean;

  addresses: StoreAddress[];
}


interface StoreAuthHook {
  store: Store | null;
  loading: boolean;
  error: string | null;
  getStoreInfo: () => Promise<Store | null>;
  checkStore: (password: string) => Promise<{ success: boolean; message: string }>;
}

export function useStoreAuth(): StoreAuthHook {
  const { user, loading: userLoading } = useAuth();
  const [store, setStore] = useState<Store | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Lấy thông tin store khi user thay đổi
  useEffect(() => {
    if (!user) {
      setStore(null);
      return;
    }
    setLoading(true);
    storeService.getCurrentStore()
      .then((result) => {
        setStore(result);
        setError(null);
      })
      .catch((err) => {
        setError('Lỗi lấy thông tin store');
        setStore(null);
      })
      .finally(() => setLoading(false));
  }, [user]);

  // Hàm lấy lại thông tin store (có thể gọi lại thủ công)
  const getStoreInfo = async (): Promise<Store | null> => {
    setLoading(true);
    setError(null);
    try {
      const result = await storeService.getCurrentStore();
      setStore(result);
      return result;
    } catch (err) {
      setError('Lỗi lấy thông tin store');
      setStore(null);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Hàm checkStore: xác thực lại bằng password
  // Sử dụng login phía user, username lấy từ user đã đăng nhập
  const checkStore = async (password: string): Promise<{ success: boolean; message: string }> => {
    if (!user?.username) {
      return { success: false, message: 'Chưa đăng nhập user' };
    }
    setLoading(true);
    setError(null);
    try {
      const result = await authService.login(user.username, password);
      if (result.success) {
        return { success: true, message: 'Xác thực thành công' };
      } else {
        return { success: false, message: result.message || 'Xác thực thất bại' };
      }
    } catch (err) {
      return { success: false, message: 'Lỗi xác thực store' };
    } finally {
      setLoading(false);
    }
  };

  return {
    store,
    loading: loading || userLoading,
    error,
    getStoreInfo,
    checkStore,
  };
}
