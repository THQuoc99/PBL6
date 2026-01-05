import { useState, useEffect, useCallback } from 'react';
import { cartService, Cart, CartItem } from '../../services/carts/cart';
import { useAuth } from '../user/useAuth';

/**
 * Hook quản lý giỏ hàng
 */
export function useCart() {
  const { isAuthenticated, user } = useAuth();
  const [cart, setCart] = useState<Cart | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Lấy giỏ hàng từ API
   */
  const fetchCart = useCallback(async () => {
    if (!isAuthenticated || !user) {
      setCart(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await cartService.getCart();
      
      if (result.cart) {
        setCart(result.cart);
      } else {
        setError(result.errors || 'Lỗi lấy giỏ hàng');
      }
    } catch (err) {
      console.error('Fetch cart error:', err);
      setError(err instanceof Error ? err.message : 'Lỗi kết nối');
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, user]);

  /**
   * Thêm sản phẩm vào giỏ hàng
   */
  const addToCart = useCallback(async (variantId: string, quantity: number = 1) => {
    setLoading(true);
    setError(null);

    try {
      const result = await cartService.addToCart(variantId, quantity);
      
      if (result.success) {
        // Refresh cart after adding
        await fetchCart();
        return { success: true };
      } else {
        const errorMsg = result.errors?.[0] || 'Lỗi thêm vào giỏ hàng';
        setError(errorMsg);
        return { success: false, errors: result.errors };
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Lỗi kết nối';
      setError(errorMsg);
      return { success: false, errors: [errorMsg] };
    } finally {
      setLoading(false);
    }
  }, [fetchCart]);

  /**
   * Xóa sản phẩm khỏi giỏ hàng
   */
  const removeFromCart = useCallback(async (itemId: string) => {
    if (!isAuthenticated || !user) {
      setError('Vui lòng đăng nhập');
      return { success: false };
    }

    setLoading(true);
    setError(null);

    try {
      const result = await cartService.removeFromCart(itemId);
      
      if (result.success) {
        // Refresh cart after removing
        await fetchCart();
        return { success: true };
      } else {
        const errorMsg = result.errors?.[0] || 'Lỗi xóa sản phẩm';
        setError(errorMsg);
        return { success: false, errors: result.errors };
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Lỗi kết nối';
      setError(errorMsg);
      return { success: false, errors: [errorMsg] };
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, user, fetchCart]);

  /**
   * Cập nhật số lượng sản phẩm
   */
  const updateQuantity = useCallback(async (itemId: string, quantity: number) => {
    if (!isAuthenticated || !user) {
      setError('Vui lòng đăng nhập');
      return { success: false };
    }

    if (quantity <= 0) {
      setError('Số lượng phải lớn hơn 0');
      return { success: false };
    }

    setLoading(true);
    setError(null);

    try {
      const result = await cartService.updateCartItemQuantity(itemId, quantity);
      
      if (result.success) {
        // Refresh cart after updating
        await fetchCart();
        return { success: true };
      } else {
        const errorMsg = result.errors?.[0] || 'Lỗi cập nhật số lượng';
        setError(errorMsg);
        return { success: false, errors: result.errors };
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Lỗi kết nối';
      setError(errorMsg);
      return { success: false, errors: [errorMsg] };
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, user, fetchCart]);

  /**
   * Xóa tất cả sản phẩm trong giỏ hàng
   */
  const clearCart = useCallback(async () => {
    if (!isAuthenticated || !user) {
      setError('Vui lòng đăng nhập');
      return { success: false };
    }

    setLoading(true);
    setError(null);

    try {
      const result = await cartService.clearCart();
      
      if (result.success) {
        // Refresh cart after clearing
        await fetchCart();
        return { success: true };
      } else {
        const errorMsg = result.errors?.[0] || 'Lỗi xóa giỏ hàng';
        setError(errorMsg);
        return { success: false, errors: result.errors };
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Lỗi kết nối';
      setError(errorMsg);
      return { success: false, errors: [errorMsg] };
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, user, fetchCart]);

  // Tự động lấy giỏ hàng khi user đăng nhập
  useEffect(() => {
    if (isAuthenticated && user) {
      fetchCart();
    } else {
      setCart(null);
    }
  }, [isAuthenticated, user, fetchCart]);

  return {
    cart,
    loading,
    error,
    // Methods
    fetchCart,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    // Computed values
    totalItems: cart?.totalItems || 0,
    totalAmount: cart?.totalAmount || 0,
    items: cart?.items || [],
  };
}
