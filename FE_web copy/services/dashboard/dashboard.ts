import { apiClient } from "../callAPI/apiClient";

export interface DailyRevenue {
  date: string;
  label: string;
  value: number;
}

export interface OrderStatusCount {
  status: string;
  label: string;
  count: number;
  color: string;
}

export interface DashboardMetrics {
  totalRevenue7d: number;
  totalOrders7d: number;
  totalProducts: number;
  totalCustomers7d: number;
}

export interface DashboardCharts {
  revenueByDay7d: DailyRevenue[];
  ordersByStatus: OrderStatusCount[];
}

export interface StoreDashboard {
  storeId: string;
  storeName: string;
  metrics: DashboardMetrics;
  charts: DashboardCharts;
}

const STORE_DASHBOARD_QUERY = `
  query StoreDashboard($storeId: ID!, $days: Int) {
    storeDashboard(storeId: $storeId, days: $days) {
      storeId
      storeName
      metrics {
        totalRevenue7d
        totalOrders7d
        totalProducts
        totalCustomers7d
      }
      charts {
        revenueByDay7d {
          date
          label
          value
        }
        ordersByStatus {
          status
          label
          count
          color
        }
      }
    }
  }
`;

export const fetchStoreDashboard = async (
  storeId: string,
  days: number = 7
): Promise<StoreDashboard | null> => {
  try {
    const response = await apiClient.authenticatedApiCall(
      STORE_DASHBOARD_QUERY,
      { storeId, days }
    );

    if (response.errors) {
      console.error("GraphQL Errors:", response.errors);
      throw new Error(response.errors[0].message);
    }

    return response.data.storeDashboard;
  } catch (error) {
    console.error("Error fetching store dashboard:", error);
    throw error;
  }
};
