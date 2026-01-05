import { useState, useEffect, useCallback } from 'react';
import { fetchProductAttributes, ProductAttribute } from '../../services/attribute/attribute';

interface UseProductAttributesResult {
	data: ProductAttribute[] | null;
	loading: boolean;
	error: any;
	refetch: () => Promise<void>;
}

export function useProductAttributes(): UseProductAttributesResult {
	const [data, setData] = useState<ProductAttribute[] | null>(null);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<any>(null);

	const fetch = useCallback(async () => {
		setLoading(true);
		setError(null);
		try {
			const attrs = await fetchProductAttributes();
			setData(attrs);
		} catch (e) {
			setError(e);
		} finally {
			setLoading(false);
		}
	}, []);

	useEffect(() => {
		fetch();
	}, [fetch]);

	return { data, loading, error, refetch: fetch };
}

export default useProductAttributes;

