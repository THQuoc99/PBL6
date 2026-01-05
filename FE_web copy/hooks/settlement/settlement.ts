import { useState, useCallback } from 'react';
import { createSettlementService, CreateSettlementResult, fetchSettlementsService, Settlement } from '../../services/settlement/settlement';

export function useCreateSettlement() {
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<any>(null);
	const [lastResult, setLastResult] = useState<CreateSettlementResult | null>(null);

	const createSettlement = useCallback(async (storeId: string | number) => {
		setLoading(true);
		setError(null);
		try {
			const { settlement, raw } = await createSettlementService(storeId);
			if (!settlement) {
				// Ưu tiên hiển thị message lỗi thực từ GraphQL server (nếu có)
				const firstError = (raw as any)?.errors?.[0];
				const message =
					(firstError && (firstError.message || String(firstError))) ||
					'Không nhận được dữ liệu settlement từ server';
				throw new Error(message);
			}
			setLastResult(settlement);
			return settlement;
		} catch (e) {
			setError(e);
			throw e;
		} finally {
			setLoading(false);
		}
	}, []);

	return {
		createSettlement,
		loading,
		error,
		lastResult,
	} as const;
}

export function useSettlements(storeId?: string | number) {
	const [data, setData] = useState<Settlement[]>([]);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<any>(null);

	const fetchSettlements = useCallback(async (id?: string | number) => {
		setLoading(true);
		setError(null);
		try {
			const { settlements, raw } = await fetchSettlementsService(id);
			if (raw.errors) {
				setError(raw.errors);
				setData([]);
			} else {
				setData(settlements);
			}
		} catch (e) {
			setError(e);
			setData([]);
		} finally {
			setLoading(false);
		}
	}, []);

	return {
		data,
		loading,
		error,
		fetchSettlements,
		refetch: () => fetchSettlements(storeId),
	} as const;
}

export default useCreateSettlement;

