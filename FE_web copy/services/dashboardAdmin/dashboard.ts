import { apiClient } from '../callAPI/apiClient';

/**
 * Admin dashboard service helpers
 * Fetches data from the backend GraphQL API
 */

export async function fetchAdminDashboard(params: Record<string, any> = {}) {
  const query = `
    query AdminDashboard {
      adminDashboard {
        totalRevenue
        totalOrders
        totalStores
        totalUsers
        revenueByDay {
          day
          revenue
          orders
        }
        topStores {
          name
          revenue
          orders
          rating
        }
        productByCategory {
          name
          value
          color
        }
        recentActivities {
          id
          type
          text
          time
          status
        }
      }
    }
  `;

  try {
    const response = await apiClient.authenticatedApiCall(query);

    if (response.errors) {
      throw new Error(response.errors[0]?.message || 'GraphQL Error');
    }

    return response.data.adminDashboard;
  } catch (err) {
    console.error("Failed to fetch admin dashboard", err);
    // Return null or rethrow, user handle error.
    // Preserving fallback logic if needed, but plan implies we replace mock.
    // If backend fails, returning null so UI shows error state or empty.
    throw err;
  }
}
