import { apiClient } from '../callAPI/apiClient';

/** Users service for admin */
export async function fetchAdminUsers(query: Record<string, any> = {}) {
  const gqlQuery = `
    query AdminUsers {
      adminUsers {
        id
        name
        email
        phone
        role
        status
        orders
        spending
        joinDate
        address
        storeName
      }
    }
  `;

  try {
    const response = await apiClient.authenticatedApiCall(gqlQuery);
    if (response.errors) {
      throw new Error(response.errors[0]?.message || 'GraphQL Error');
    }
    // Transform to expected shape { items: [], total: ... }
    return {
      items: response.data.adminUsers,
      total: response.data.adminUsers.length
    };
  } catch (err) {
    console.error("Failed to fetch admin users", err);
    throw err;
  }
}

export async function fetchAdminUserById(userId: number) {
  // TODO: Implement detail query if needed, for now mock or simple finding from list
  return { id: userId, name: 'Mock User', email: 'mock@example.com', role: 'customer', status: 'active' };
}

export async function banUser(userId: any) {
  const mutation = `
        mutation BanUser($userId: ID!) {
            banUser(userId: $userId) {
                success
                message
                user {
                    id
                    status
                }
            }
        }
    `;

  try {
    const response = await apiClient.authenticatedApiCall(mutation, { userId });
    if (response.errors) {
      throw new Error(response.errors[0]?.message || 'GraphQL Error');
    }
    return response.data.banUser;
  } catch (err) {
    throw err;
  }
}
