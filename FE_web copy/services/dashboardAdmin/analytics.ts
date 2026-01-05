/** 
 * Analytics service for admin - Platform-wide analytics
 * Calls backend GraphQL query: adminAnalytics
 */
import { apiClient } from '../callAPI/apiClient';

export async function fetchAdminAnalytics(params: Record<string, any> = {}){
  // Call backend GraphQL API (authenticated)
  try{
    const query = `
      query AdminAnalytics($range: String, $limit: Int) {
        adminAnalytics(range: $range, limit: $limit) {
          revenueTrend { 
            month 
            revenue 
            orders 
            growth 
          }
          categoryPerformance { 
            name 
            sales 
            orders 
          }
          regionalDistribution { 
            region 
            value 
          }
          userGrowth { 
            month 
            customers 
            sellers 
          }
          keyMetrics {
            revenueGrowth
            averageOrderValue
            retentionRate
          }
        }
      }
    `;
    const variables = { 
      range: params.range || '30d', 
      limit: params.limit || 12 
    };
    
    const resp = await apiClient.authenticatedApiCall(query, variables);
    
    // Check for GraphQL errors
    if (resp.errors && resp.errors.length > 0) {
      console.error('GraphQL errors:', resp.errors);
      throw new Error(`GraphQL Error: ${resp.errors[0].message}`);
    }
    
    if (resp && resp.data && resp.data.adminAnalytics) {
      console.log('✅ Admin analytics loaded from backend:', resp.data.adminAnalytics);
      return resp.data.adminAnalytics;
    }
    
    throw new Error('No data returned from adminAnalytics query');
  }catch(graphQLErr){
    console.error('❌ GraphQL adminAnalytics call failed:', graphQLErr);
    // Re-throw to let hook handle error state
    throw graphQLErr;
  }
}
