import { authService } from '../user/auth';

// Interface kết quả danh sách categories
export interface CategoriesResult {
	categories?: any;
	errors?: any;
}

// Hàm lấy categories theo filter/sort
export async function getCategoriesByFilter(
	filter?: any,
	sortBy?: string,
	paging?: { first?: number; after?: string; last?: number; before?: string }
): Promise<CategoriesResult> {
	const query = `
		query getCategoriesByFilter($filter: CategoryFilterInput, $sortBy: String, $first: Int, $after: String, $last: Int, $before: String) {
			categories(first: $first, after: $after, last: $last, before: $before, filter: $filter, sortBy: $sortBy) {
				edges {
					node {
						categoryId
						name
						productCount
						thumbnailImage
						subcategories {
							categoryId
							name
							productCount
						}
					}
				}
				pageInfo {
					hasNextPage
					hasPreviousPage
					startCursor
					endCursor
				}
			}
		}
	`;
	const variables: any = {};
	if (filter) variables.filter = filter;
	if (sortBy) variables.sortBy = sortBy;
	if (paging) {
		if (paging.first !== undefined) variables.first = paging.first;
		if (paging.after !== undefined) variables.after = paging.after;
		if (paging.last !== undefined) variables.last = paging.last;
		if (paging.before !== undefined) variables.before = paging.before;
	}
	const result = await authService.publicApiCall(query, Object.keys(variables).length ? variables : undefined);
	return {
		categories: result.data?.categories,
		errors: result.errors,
	};
}

// Singleton service để import nếu muốn
export class CategoryService {
	async getCategoriesByFilter(filter?: any, sortBy?: string, paging?: { first?: number; after?: string; last?: number; before?: string }) {
		return await getCategoriesByFilter(filter, sortBy, paging);
	}
}

export const categoryService = new CategoryService();
