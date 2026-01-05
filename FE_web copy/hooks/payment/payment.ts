import { useState } from 'react';
import { createVnpayLink as createVnpayLinkService } from '../../services/payment/payment';

export function useCreateVnPayLink() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const createVnpayLink = async (orderId: string | number, amount: number, isStore?: boolean): Promise<string> => {
    setLoading(true);
    setError(null);
    try {
      const url = await createVnpayLinkService(orderId, amount, isStore);
      return url;
    } catch (err) {
      const e = err instanceof Error ? err : new Error(String(err));
      setError(e);
      throw e;
    } finally {
      setLoading(false);
    }
  };

  return { createVnpayLink, loading, error } as const;
}

export default useCreateVnPayLink;
