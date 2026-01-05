import { authService } from './auth';

// Interface kết quả chi tiết sản phẩm
export interface ProductDetailResult {
	product?: any;
	errors?: any;
}

// Interface kết quả danh sách sản phẩm
export interface ProductsResult {
	products?: any;
	errors?: any;
}

// Lấy chi tiết sản phẩm

export async function getProductDetail(id: string): Promise<ProductDetailResult> {
	const query = `
		query GetProductDetail($id: ID!) {
			product(id: $id) {
				productId
				name
				slug
				description
				brand { id }
				basePrice
				priceRange
				hasDiscount
				discountPercentage
				isActive
				isFeatured
				availabilityStatus
				reviewCount
				totalSold
				createdAt
				store {
					storeId
					name
					avatar
				}
				category {
					categoryId
					name
					fullPath { id name }
					parent { name }
				}
				colorOptions { value imageUrl variantCount }
				sizeOptions { value variantCount }
				galleryImages { imageId imageUrl isThumbnail altText displayOrder }
				thumbnailImage { imageUrl altText }
				variants {
					edges {
						node {
							variantId
							price
							stock
							colorName
							sizeName
							isInStock
							stockStatus
							discountPercentage
							colorImageUrl
							isActive
						}
					}
				}
			}
		}
	`;
	const variables = { id };
	const result = await authService.apiCall(query, variables);
	return {
		product: result.data?.product,
		errors: result.errors,
	};
}

// Lấy danh sách sản phẩm

export async function getProducts(): Promise<ProductsResult> {
	// Dùng getProductByFilter_Sort với biến null để lấy tất cả sản phẩm
	return await getProductByFilter_Sort();
}

// Hàm lấy sản phẩm theo filter/sort
export async function getProductByFilter_Sort(
	filter?: any,
	sortBy?: any,
	paging?: { first?: number; after?: string; last?: number; before?: string }
): Promise<ProductsResult> {
	const query = `
		query getProductByFilter_Sort($filter: ProductFilterInput, $sortBy: ProductSortInput, $first: Int, $after: String, $last: Int, $before: String) {
			products(first: $first, after: $after, last: $last, before: $before, filter: $filter, sortBy: $sortBy) {
				edges {
					node {
						productId
						category { name }
						brand { name }
						ratingAverage
						reviewCount
						totalSold
						totalStock
						name
						store { name }
						minPrice
						maxPrice
						priceRange
						basePrice
						discountPercentage
						hasDiscount
						finalPrice
						isFeatured
						isHot
						isNew
						thumbnailImage { imageUrl }
						colorOptions { value valueCode imageUrl }
						sizeOptions { value }
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
	const result = await authService.apiCall(query, Object.keys(variables).length ? variables : undefined);
	return {
		products: result.data?.products,
		errors: result.errors,
	};
}

// Singleton service để import nếu muốn
export class ProductService {
	async getProductDetail(id: string) {
		return await getProductDetail(id);
	}
	async getProducts() {
		return await getProducts();
	}
	async getProductByFilter_Sort(filter?: any, sortBy?: any, paging?: { first?: number; after?: string; last?: number; before?: string }) {
		return await getProductByFilter_Sort(filter, sortBy, paging);
	}
}

export const productService = new ProductService();
