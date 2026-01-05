import { apiClient } from '../callAPI/apiClient';

interface GraphQLResponse<T = any> {
  data: T;
  errors?: any;
}

export async function createVnpayLink(orderId: string | number, amount: number, isStore?: boolean): Promise<string> {
  const query = `
    mutation CreateVnPayLink($orderId: ID!, $amount: Float!, $isStore: Boolean) {
      createVnpayLink(orderId: $orderId, amount: $amount, isStore: $isStore) {
        url
      }
    }
  `;

  const variables: any = { orderId: String(orderId), amount };
  if (typeof isStore !== 'undefined') variables.isStore = isStore;
  // Ensure amount is a number (GraphQL Float must be numeric, not a string)
  variables.amount = Number(variables.amount);

  const result: GraphQLResponse = await apiClient.authenticatedApiCall(query, variables);

  if (result.errors) {
    const message = Array.isArray(result.errors) && result.errors.length ? result.errors[0].message : 'GraphQL error';
    throw new Error(message);
  }

  const url = result.data?.createVnpayLink?.url;
  if (!url) throw new Error('No url returned from createVnpayLink');

  return url;
}

export default { createVnpayLink };
