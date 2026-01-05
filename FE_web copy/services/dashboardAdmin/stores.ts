import { apiClient } from '../callAPI/apiClient';

/** Stores service for admin */
export async function fetchAdminStores(query: Record<string, any> = {}) {
  const gqlQuery = `
    query AdminStores {
      adminStores {
        id
        name
        ownerName
        email
        phone
        address
        status
        revenue
        orders
        products
        rating
        joinDate
        avatar
      }
    }
  `;

  try {
    const response = await apiClient.authenticatedApiCall(gqlQuery);
    if (response.errors) {
      throw new Error(response.errors[0]?.message || 'GraphQL Error');
    }

    // Transform data to match component expectation (though current component handles array directly)
    // The component expects { items: [], total: 0 } or just [] depending on hook usage?
    // Looking at useStores.ts: const [data, setData] = useState<any>({ items: [], total: 0 });
    // So we need to return { items: [...], total: ... }
    const items = response.data.adminStores || [];
    return {
      items,
      total: items.length
    };
  } catch (err) {
    console.error("Failed to fetch admin stores", err);
    throw err;
  }
}

export async function fetchAdminStoreById(storeId: number) {
  // TODO: implement single store fetching via GraphQL if needed later.
  // For now falling back to mock or unimplemented.
  try {
    const res = await fetch(`/api/admin/stores/${storeId}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return { id: storeId, name: 'Mock Store', status: 'pending', rating: 4.2 };
  }
}

export async function lockStore(storeId: any) {
  const mutation = `
        mutation LockStore($storeId: ID!) {
            lockStore(storeId: $storeId) {
                success
                message
                store {
                    id
                    status
                }
            }
        }
    `;

  try {
    const response = await apiClient.authenticatedApiCall(mutation, { storeId });
    if (response.errors) {
      throw new Error(response.errors[0]?.message || 'GraphQL Error');
    }
    return response.data.lockStore;
  } catch (err) {
    throw err;
  }
}
