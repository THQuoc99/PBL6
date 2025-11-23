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
				brand
				basePrice
				priceRange
				hasDiscount
				discountPercentage
				isActive
				isFeatured
				availabilityStatus
				ratingCount
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
	const query = `
		query getProducts {
			products {
				edges {
					node {
						productId
						category { name }
						name
						brand
						minPrice
						maxPrice
						basePrice
						discountPercentage
						hasDiscount
						isHot
						isFeatured
						thumbnailImage { imageUrl }
						ratingAverage
						ratingCount
						colorOptions { value valueCode imageUrl }
						sizeOptions { value }
						totalStock
					}
				}
			}
		}
	`;
	const result = await authService.apiCall(query);
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
}

export const productService = new ProductService();
