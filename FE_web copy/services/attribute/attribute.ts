
import { apiClient } from '../callAPI/apiClient';

export interface ProductAttribute {
	attributeId: number;
	name: string; // DB value, e.g. 'color'
	nameDisplay?: string; // human label, e.g. 'Màu Sắc'
	type?: string;
	hasImage?: boolean;
}

/**
 * Fetch product attributes from backend GraphQL
 */
export async function fetchProductAttributes(): Promise<ProductAttribute[]> {
	const query = `query { productAttributes { attributeId name nameDisplay type hasImage } }`;
	const res = await apiClient.publicApiCall(query);

	if (!res) throw new Error('No response from API');
	if (res.errors) throw res.errors;

	return res.data?.productAttributes || [];
}

export default { fetchProductAttributes };

