import { apiClient } from '../callAPI/apiClient';

// Cart Item Interface
export interface CartItem {
  itemId: string;
  quantity: number;
  unitPrice: number;
  subtotal: number;
  variant: {
    variantId: string;
    colorName: string;
    sizeName: string;
    colorImageUrl: string; // <-- Thêm dòng này
    price: number;
    weight: number;
    finalPrice: number;
    stock: number;
    product: {
      productId: string;
      name: string;
      thumbnailImage: {
        imageUrl: string;
      };
      store:
          {
            storeId
            name
            avatar
          };
    };
  };
}

// Cart Interface
export interface Cart {
  cartId: string;
  totalItems: number;
  totalAmount: number;
  totalWeight: number;
  items: CartItem[];
  createdAt: string;
  updatedAt: string;
}

// API Response Interfaces
export interface CartResult {
  cart?: Cart;
  errors?: any;
}

export interface CartItemResult {
  cartItem?: CartItem;
  success: boolean;
  errors?: string[];
}

/**
 * Cart Service - Quản lý giỏ hàng
 */
class CartService {
  /**
   * Lấy giỏ hàng của user hiện tại
   */
  async getCart(): Promise<CartResult> {
    const query = `
      query GetMyCart {
        myCart {
          cartId
          totalItems
          totalAmount
          totalWeight
          createdAt
          updatedAt
          items {
            itemId
            quantity
            unitPrice
            subtotal
            variant {
              variantId
              colorName
              sizeName
              weight
              colorImageUrl
              price
              finalPrice
              stock
              product {
                productId
                name
                thumbnailImage {
                  imageUrl
                }
                store
                {
                  storeId
                  name
                  avatar
                }
              }
            }
          }
        }
      }
    `;

    try {
      const result = await apiClient.authenticatedApiCall(query);
      console.log('📦 CartService.getCart - API Response:', result);
      if (result.data?.myCart) {
        return { cart: result.data.myCart };
      }
      
      return { errors: result.errors || 'Lỗi lấy giỏ hàng' };
    } catch (error) {
      console.error('Get cart error:', error);
      return { errors: error };
    }
  }

  /**
   * Thêm sản phẩm vào giỏ hàng
   */
  async addToCart(variantId: string, quantity: number): Promise<CartItemResult> {
    const query = `
      mutation AddToCart($variantId: ID!, $quantity: Int!) {
        addToCart(input: {
          variantId: $variantId
          quantity: $quantity
        }) {
          success
          errors
          cart {
            cartId
            totalItems
            totalAmount
          }
          cartItem {
            itemId
            quantity
            unitPrice
            subtotal
            variant {
              variantId
              colorName
              sizeName
              stock
              product {
                productId
                name
                thumbnailImage {
                  imageUrl
                }
              }
            }
          }
        }
      }
    `;

    try {
      console.log('🛒 CartService.addToCart - Calling API with:', { variantId, quantity });
      console.log('🔑 Token exists:', !!localStorage.getItem('accessToken'));
      
      const result = await apiClient.authenticatedApiCall(query, { variantId, quantity });
      
      console.log('📦 CartService.addToCart - API Response:', result);
      
      if (result.data?.addToCart) {
        const data = result.data.addToCart;
        console.log('✅ addToCart data:', data);
        console.log('🎯 Success:', data.success);
        console.log('❌ Errors:', data.errors);
        console.log('🛍️ CartItem:', data.cartItem);
        
        return {
          success: data.success,
          cartItem: data.cartItem,
          errors: data.errors
        };
      }
      
      return { 
        success: false, 
        errors: result.errors || ['Lỗi thêm vào giỏ hàng'] 
      };
    } catch (error) {
      console.error('Add to cart error:', error);
      return { 
        success: false, 
        errors: [error instanceof Error ? error.message : 'Lỗi kết nối'] 
      };
    }
  }

  /**
   * Xóa sản phẩm khỏi giỏ hàng
   */
  async removeFromCart(itemId: string): Promise<{ success: boolean; errors?: string[] }> {
    const query = `
      mutation RemoveFromCart($itemId: ID!) {
        removeFromCart(input: {
          itemId: $itemId
        }) {
          success
          errors
          cart {
            cartId
            totalItems
            totalAmount
          }
        }
      }
    `;

    try {
      const result = await apiClient.authenticatedApiCall(query, { itemId });
      
      if (result.data?.removeFromCart) {
        const data = result.data.removeFromCart;
        return {
          success: data.success,
          errors: data.errors
        };
      }
      
      return { 
        success: false, 
        errors: result.errors || ['Lỗi xóa sản phẩm'] 
      };
    } catch (error) {
      console.error('Remove from cart error:', error);
      return { 
        success: false, 
        errors: [error instanceof Error ? error.message : 'Lỗi kết nối'] 
      };
    }
  }

  /**
   * Cập nhật số lượng sản phẩm trong giỏ hàng
   */
  async updateCartItemQuantity(itemId: string, quantity: number): Promise<CartItemResult> {
    const query = `
      mutation UpdateCartItemQuantity($itemId: ID!, $quantity: Int!) {
        updateCartItemQuantity(input: {
          itemId: $itemId
          quantity: $quantity
        }) {
          success
          errors
          cartItem {
            itemId
            quantity
            unitPrice
            subtotal
            variant {
              variantId
              colorName
              sizeName
              stock
              product {
                productId
                name
                thumbnailImage {
                  imageUrl
                }
              }
            }
          }
        }
      }
    `;

    try {
      const result = await apiClient.authenticatedApiCall(query, { itemId, quantity });
      
      if (result.data?.updateCartItemQuantity) {
        const data = result.data.updateCartItemQuantity;
        return {
          success: data.success,
          cartItem: data.cartItem,
          errors: data.errors
        };
      }
      
      return { 
        success: false, 
        errors: result.errors || ['Lỗi cập nhật số lượng'] 
      };
    } catch (error) {
      console.error('Update cart item error:', error);
      return { 
        success: false, 
        errors: [error instanceof Error ? error.message : 'Lỗi kết nối'] 
      };
    }
  }

  /**
   * Xóa tất cả sản phẩm trong giỏ hàng
   */
  async clearCart(): Promise<{ success: boolean; errors?: string[] }> {
    const query = `
      mutation ClearCart {
        clearCart(input: {}) {
          success
          errors
          cart {
            cartId
            totalItems
            totalAmount
          }
        }
      }
    `;

    try {
      const result = await apiClient.authenticatedApiCall(query);
      
      if (result.data?.clearCart) {
        const data = result.data.clearCart;
        return {
          success: data.success,
          errors: data.errors
        };
      }
      
      return { 
        success: false, 
        errors: result.errors || ['Lỗi xóa giỏ hàng'] 
      };
    } catch (error) {
      console.error('Clear cart error:', error);
      return { 
        success: false, 
        errors: [error instanceof Error ? error.message : 'Lỗi kết nối'] 
      };
    }
  }
}

export const cartService = new CartService();
