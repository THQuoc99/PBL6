import { ApiClient } from '../callAPI/apiClient';

const apiClient = ApiClient.getInstance();

interface GraphQLResponse<T = any> {
  data: T;
  errors?: any;
}

export async function createGhtkOrders(orderId: string | number): Promise<any> {
  const query = `
    mutation CreateGhtkOrders($orderId: ID!) {
      createGhtkOrders(orderId: $orderId) {
        success
        message
        results
      }
    }
  `;

  const variables = { orderId: String(orderId) };

  const result: GraphQLResponse = await apiClient.authenticatedApiCall(query, variables);

  if (result.errors) {
    const message = Array.isArray(result.errors) && result.errors.length ? result.errors[0].message : 'GraphQL error';
    throw new Error(message);
  }

  const payload = result.data?.createGhtkOrders;
  if (!payload) throw new Error('No response from createGhtkOrders');

  if (!payload.success) {
    throw new Error(payload.message || 'createGhtkOrders failed');
  }

  return payload.results;
}

export default { createGhtkOrders };
