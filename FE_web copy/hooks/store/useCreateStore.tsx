import { useState } from 'react';
import { storeService } from '../../services/store/store';

interface CreateStoreInput {
  name: string;
  email?: string;
  description?: string;
  // allow addresses list for new API
  addresses?: Array<{
    province: string;
    ward: string;
    hamlet?: string;
    detail: string;
    phone?: string;
    // GraphQL expects camelCase `isDefault`
    isDefault?: boolean;
  }>;
}

export function useCreateStore() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function createStore(input: CreateStoreInput, files?: { avatar?: File; coverImage?: File; logo?: File }) {
    setLoading(true);
    setError(null);
    try {
      // Normalize address keys to match GraphQL camelCase (isDefault)
      const normalizedInput: any = { ...input };
      if (Array.isArray(input.addresses)) {
        // Normalize address flags to GraphQL camelCase `isDefault`
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

      const response = await storeService.createStoreWithFiles(normalizedInput as any, files as any);
      if (!response || !response.success) {
        setError(response?.message || 'Tạo cửa hàng thất bại');
      }
      return response;
    } catch (e: any) {
      setError(e?.message || String(e));
      return { success: false, message: e?.message || 'Lỗi'};
    } finally {
      setLoading(false);
    }
  }

  return {
    createStore,
    loading,
    error,
  } as const;
}

export default useCreateStore;
