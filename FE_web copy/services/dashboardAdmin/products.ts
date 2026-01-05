import { apiClient } from '../callAPI/apiClient';

/** Products service for admin */
export async function fetchAdminProducts(query: Record<string, any> = {}) {
  const gqlQuery = `
    query AdminProducts {
      adminProducts {
        id
        name
        store
        category
        price
        stock
        sold
        rating
        reviews
        status
        image
      }
    }
  `;

  try {
    const response = await apiClient.authenticatedApiCall(gqlQuery);
    if (response.errors) {
      throw new Error(response.errors[0]?.message || 'GraphQL Error');
    }
    return {
      items: response.data.adminProducts,
      total: response.data.adminProducts.length
    };
  } catch (err) {
    console.error("Failed to fetch admin products", err);
    throw err;
  }
}

export async function fetchAdminProductById(productId: number) {
  try {
    const res = await fetch(`/api/admin/products/${productId}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return { id: productId, name: 'Mock Product', stock: 10, status: 'draft' };
  }
}
