import { apiClient } from '../callAPI/apiClient';

export interface CreateSettlementResult {
	settlementId: string | number;
	totalAmount: string;
	status: string;
}

export async function createSettlementService(storeId: string | number) {
	const mutation = `mutation CreateSettlement($storeId: ID!) {
		createSettlement(storeId: $storeId) {
			settlementId
			totalAmount
			status
		}
	}`;

	const variables = { storeId: String(storeId) };
	const res = await apiClient.authenticatedApiCall(mutation, variables);

	// Chuẩn hoá payload phòng trường hợp server dùng snake_case
	const payload =
		(res.data as any)?.createSettlement ??
		(res.data as any)?.create_settlement ??
		null;

	return {
		raw: res,
		settlement: payload as CreateSettlementResult | null,
	};
}

export interface Settlement {
	settlementId: string | number;
	totalAmount: string;
	status: string;
	paidAt?: string;
	createdAt?: string;
	note?: string;
	store?: any;
}

export async function fetchSettlementsService(storeId?: string | number) {
	const query = `query Settlements($storeId: ID) {
		settlements(storeId: $storeId) {
			settlementId
			totalAmount
			status
			paidAt
			createdAt
			note
			store {
				storeId
				name
			}
		}
	}`;

	const variables = storeId ? { storeId: String(storeId) } : {};
	const res = await apiClient.authenticatedApiCall(query, variables);

	const payload =
		(res.data as any)?.settlements ??
		[];

	return {
		raw: res,
		settlements: payload as Settlement[],
	};
}

export default {
	createSettlementService,
	fetchSettlementsService,
};

