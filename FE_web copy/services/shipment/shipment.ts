import { ApiClient } from '../callAPI/apiClient';

const apiClient = ApiClient.getInstance();

export interface ShippingFeeInput {
  storeId: string;
  weight: number;
  value?: number;
  transport?: string;
}

export interface ExtraFee {
  title: string;
  amount: number;
  type: string;
}

export interface ShippingFeeResult {
  totalFee: number;
  baseFee?: number;
  insuranceFee?: number;
  name?: string;
  deliverySupported?: boolean;
  extraFees?: ExtraFee[];
}

export async function calculateShippingFee(input: ShippingFeeInput): Promise<ShippingFeeResult | null> {
  const query = `
    query CalculateShippingFee($input: ShippingFeeInput!) {
      calculateShippingFee(input: $input) {
        totalFee
        baseFee
        insuranceFee
        name
        deliverySupported
        extraFees {
          title
          amount
          type
        }
      }
    }
  `;

  try {
    console.log('Calculating shipping fee with input:', input);
    // Remove undefined fields before sending to API
    const cleanInput = Object.fromEntries(Object.entries(input).filter(([_, v]) => v !== undefined));
    console.log('Cleaned input for API call:', cleanInput);
    const response = await apiClient.authenticatedApiCall(query, { input: cleanInput });
    if (response.errors) {
      console.error('Error calculating shipping fee:', response.errors);
      throw new Error(response.errors[0]?.message || 'Failed to calculate shipping fee');
    }
    return response.data?.calculateShippingFee || null;
  } catch (error) {
    console.error('calculateShippingFee error:', error);
    throw error;
  }
}