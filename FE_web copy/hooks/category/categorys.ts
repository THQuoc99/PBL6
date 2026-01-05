import { useState, useEffect, useRef } from 'react';
import { getCategoriesByFilter } from '../../services/category/category';

interface UseCategoriesParams {
	filter?: any;
	sortBy?: string;
	paging?: { first?: number; after?: string; last?: number; before?: string };
}

export function useCategories(
	filter?: any,
	sortBy?: string,
	paging?: { first?: number; after?: string; last?: number; before?: string }
) {
	const [categories, setCategories] = useState<any[]>([]);
	const [pageInfo, setPageInfo] = useState<any>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<any>(null);
	const prevParamsRef = useRef<string>('');

	useEffect(() => {
		const currentParams = JSON.stringify({ filter, sortBy, paging });
		
		// Chỉ fetch khi params thay đổi
		if (prevParamsRef.current === currentParams) {
			return;
		}
		
		prevParamsRef.current = currentParams;

		const fetchCategories = async () => {
			setLoading(true);
			setError(null);
			try {
				const result = await getCategoriesByFilter(filter, sortBy, paging);
				if (result.errors) {
					setError(result.errors);
					setCategories([]);
					setPageInfo(null);
				} else {
					const edges = result.categories?.edges || [];
					setCategories(edges.map((edge: any) => edge.node));
					setPageInfo(result.categories?.pageInfo || null);
				}
			} catch (err) {
				setError(err);
				setCategories([]);
				setPageInfo(null);
			} finally {
				setLoading(false);
			}
		};

		fetchCategories();
	}, [filter, sortBy, paging]);

	return { categories, pageInfo, loading, error };
}
