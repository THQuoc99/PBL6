import { authService } from '../user/auth';
import { apiClient } from '../callAPI/apiClient';

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
				brand { brandId }
				basePrice
				finalPrice
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
							finalPrice
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
	const result = await authService.publicApiCall(query, Object.keys(variables).length ? variables : undefined);
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
	// Debug: show the filter payload being sent to the API
	if (filter) console.log('getProductByFilter_Sort - outgoing filter:', JSON.parse(JSON.stringify(filter)));
	if (sortBy) variables.sortBy = sortBy;
	if (paging) {
		if (paging.first !== undefined) variables.first = paging.first;
		if (paging.after !== undefined) variables.after = paging.after;
		if (paging.last !== undefined) variables.last = paging.last;
		if (paging.before !== undefined) variables.before = paging.before;
	}
	const result = await authService.publicApiCall(query, Object.keys(variables).length ? variables : undefined);
	console.log('getProductByFilter_Sort - result:', result);
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

	// Create full product (wrapper)
	async createProductFull(input: any) {
		return await createProductFull(input);
	}

	// Update full product (wrapper)
	async updateProductFull(productId: number, input: any) {
		return await updateProductFull(productId, input);
	}

	async deleteProduct(productId: number) {
		return await deleteProduct(productId);
	}
}

export const productService = new ProductService();

// Create full product (minimal support: no file uploads in this helper)
export async function createProductFull(input: any) {
	const mutation = `
		mutation CreateProductFull($input: CreateProductFullInput!) {
			createProductFull(input: $input) {
				success
				product {
					productId
					name
					slug
				}
				errors
			}
		}
	`;
	// Detect files inside input and perform multipart/form-data upload if any
	try {
		// Deep clone input to avoid mutating caller
		const cleanedInput: any = JSON.parse(JSON.stringify(input || {}));
		const files: Array<{ path: string; file: File }> = [];

		// Helper to collect file at path and set null placeholder in cleanedInput
		const pushFile = (path: string, file: File) => {
			files.push({ path, file });
			// set placeholder null at path inside cleanedInput
			const parts = path.replace(/^variables\./, '').split('.');
			let cur: any = { input: cleanedInput };
			for (let i = 0; i < parts.length - 1; i++) {
				const p = parts[i];
				if (p.endsWith(']')) {
					// not expected here
				}
				if (!(p in cur)) cur[p] = {};
				cur = cur[p];
			}
			cur[parts[parts.length - 1]] = null;
		};

		// sizeGuideImage
		if (input.sizeGuideImage instanceof File) {
			pushFile('variables.input.sizeGuideImage', input.sizeGuideImage);
		} else if (input.sizeGuideImage) {
			cleanedInput.sizeGuideImage = input.sizeGuideImage;
		}

		// images: array of { image, isThumbnail, altText, displayOrder }
		if (Array.isArray(input.images)) {
			cleanedInput.images = cleanedInput.images || [];
			for (let i = 0; i < input.images.length; i++) {
				const img = input.images[i];
				cleanedInput.images[i] = { ...(img || {}) };
				if (img && img.image instanceof File) {
					pushFile(`variables.input.images.${i}.image`, img.image);
				} else {
					cleanedInput.images[i].image = img?.image;
				}
			}
		}

		// attributeOptions: [{ attributeId, value, valueCode, image, displayOrder }]
		if (Array.isArray(input.attributeOptions)) {
			cleanedInput.attributeOptions = cleanedInput.attributeOptions || [];
			for (let i = 0; i < input.attributeOptions.length; i++) {
				const ao = input.attributeOptions[i];
				cleanedInput.attributeOptions[i] = { ...(ao || {}) };
				if (ao && ao.image instanceof File) {
					pushFile(`variables.input.attributeOptions.${i}.image`, ao.image);
				} else {
					cleanedInput.attributeOptions[i].image = ao?.image;
				}
			}
		}

		// Variants: ensure optionCombinations is string if object
		if (Array.isArray(input.variants)) {
			cleanedInput.variants = cleanedInput.variants || [];
			for (let i = 0; i < input.variants.length; i++) {
				const v = input.variants[i];
				cleanedInput.variants[i] = { ...(v || {}) };
				if (v && v.optionCombinations && typeof v.optionCombinations === 'object') {
					cleanedInput.variants[i].optionCombinations = JSON.stringify(v.optionCombinations);
				}
			}
		}

		// If no files detected, use regular authenticated JSON call
		if (files.length === 0) {
			const variables = { input: cleanedInput };
			const result = await authService.apiCall(mutation, Object.keys(variables).length ? variables : undefined);
			// normalize GraphQL errors to strings
			const apiErrors = (result.errors || []).map((e: any) => e?.message || JSON.stringify(e));
			if (result.data?.createProductFull) return result.data.createProductFull;
			return { success: false, errors: apiErrors.length ? apiErrors : ["Unknown error"] };
		}

		// Build multipart/form-data per GraphQL multipart spec
		const operations = { query: mutation, variables: { input: cleanedInput } };
		const map: any = {};
		const form = new FormData();
		files.forEach((f, idx) => {
			map[String(idx)] = [f.path.replace(/^variables\./, 'variables.')];
			form.append(String(idx), f.file);
		});
		form.append('operations', JSON.stringify(operations));
		form.append('map', JSON.stringify(map));

		// Build files mapping expected by apiClient.authenticatedMultipartCall
		const filesMap: { [key: string]: File | null } = {};
		files.forEach((f, idx) => {
			// f.path uses 'variables.input....' format earlier; convert to 'input....'
			const key = f.path.replace(/^variables\./, '');
			filesMap[key] = f.file;
		});

		// Use centralized apiClient to handle auth + multipart upload
		const mpResult = await apiClient.authenticatedMultipartCall(mutation, { input: cleanedInput }, filesMap as any);
		if (mpResult.errors) {
			const errs = (mpResult.errors || []).map((e: any) => e?.message || JSON.stringify(e));
			return { success: false, errors: errs };
		}
		if (mpResult.data?.createProductFull) return mpResult.data.createProductFull;
		return { success: false, errors: ['Unknown error'] };
	} catch (err: any) {
		console.error('createProductFull error', err);
		return { success: false, errors: [err?.message || 'Unknown error'] };
	}
}

// Delete product
export async function deleteProduct(productId: number) {
	const mutation = `
		mutation DeleteProduct($id: Int!) {
			productDelete(id: $id) {
				success
				errors
			}
		}
	`;
	try {
		const variables = { id: productId };
		const result = await authService.apiCall(mutation, Object.keys(variables).length ? variables : undefined);
		console.debug('deleteProduct - graphql result:', result);
		// Support both camelCase and snake_case mutation field names
		const payload = result.data?.productDelete ?? result.data?.product_delete;
		if (result.errors) {
			const errs = (result.errors || []).map((e: any) => e?.message || JSON.stringify(e));
			return { success: false, errors: errs };
		}
		if (payload) return payload;
		// If we reach here, return any hints from the raw result
		const hint = result.data ? JSON.stringify(result.data) : undefined;
		return { success: false, errors: ['Unknown error', hint].filter(Boolean) };
	} catch (err: any) {
		console.error('deleteProduct error', err);
		return { success: false, errors: [err?.message || 'Unknown error'] };
	}
}

// Update full product (supports file uploads similar to createProductFull)
export async function updateProductFull(productId: number, input: any) {
	const mutation = `
		mutation UpdateProductFull($productId: Int!, $input: CreateProductFullInput!) {
			updateProductFull(productId: $productId, input: $input) {
				success
				product { productId name slug }
				errors
			}
		}
	`;

	try {
		const cleanedInput: any = JSON.parse(JSON.stringify(input || {}));
		const files: Array<{ path: string; file: File }> = [];

		const pushFile = (path: string, file: File) => {
			files.push({ path, file });
			const parts = path.replace(/^variables\./, '').split('.');
			let cur: any = { input: cleanedInput };
			for (let i = 0; i < parts.length - 1; i++) {
				const p = parts[i];
				if (!(p in cur)) cur[p] = {};
				cur = cur[p];
			}
			cur[parts[parts.length - 1]] = null;
		};

		if (input.sizeGuideImage instanceof File) {
			pushFile('variables.input.sizeGuideImage', input.sizeGuideImage);
		} else if (input.sizeGuideImage) {
			cleanedInput.sizeGuideImage = input.sizeGuideImage;
		}

		if (Array.isArray(input.images)) {
			cleanedInput.images = cleanedInput.images || [];
			for (let i = 0; i < input.images.length; i++) {
				const img = input.images[i];
				cleanedInput.images[i] = { ...(img || {}) };
				if (img && img.image instanceof File) {
					pushFile(`variables.input.images.${i}.image`, img.image);
				} else {
					cleanedInput.images[i].image = img?.image;
				}
			}
		}

		if (Array.isArray(input.attributeOptions)) {
			cleanedInput.attributeOptions = cleanedInput.attributeOptions || [];
			for (let i = 0; i < input.attributeOptions.length; i++) {
				const ao = input.attributeOptions[i];
				cleanedInput.attributeOptions[i] = { ...(ao || {}) };
				if (ao && ao.image instanceof File) {
					pushFile(`variables.input.attributeOptions.${i}.image`, ao.image);
				} else {
					cleanedInput.attributeOptions[i].image = ao?.image;
				}
			}
		}

		if (Array.isArray(input.variants)) {
			cleanedInput.variants = cleanedInput.variants || [];
			for (let i = 0; i < input.variants.length; i++) {
				const v = input.variants[i];
				cleanedInput.variants[i] = { ...(v || {}) };
				if (v && v.optionCombinations && typeof v.optionCombinations === 'object') {
					cleanedInput.variants[i].optionCombinations = JSON.stringify(v.optionCombinations);
				}
			}
		}

		if (files.length === 0) {
			const variables = { productId, input: cleanedInput };
			const result = await authService.apiCall(mutation, Object.keys(variables).length ? variables : undefined);
			const apiErrors = (result.errors || []).map((e: any) => e?.message || JSON.stringify(e));
			if (result.data?.updateProductFull) return result.data.updateProductFull;
			return { success: false, errors: apiErrors.length ? apiErrors : ["Unknown error"] };
		}

		const filesMap: { [key: string]: File | null } = {};
		files.forEach((f, idx) => {
			const key = f.path.replace(/^variables\./, '');
			filesMap[key] = f.file;
		});

		const mpResult = await apiClient.authenticatedMultipartCall(mutation, { productId, input: cleanedInput }, filesMap as any);
		if (mpResult.errors) {
			const errs = (mpResult.errors || []).map((e: any) => e?.message || JSON.stringify(e));
			return { success: false, errors: errs };
		}
		if (mpResult.data?.updateProductFull) return mpResult.data.updateProductFull;
		return { success: false, errors: ['Unknown error'] };
	} catch (err: any) {
		console.error('updateProductFull error', err);
		return { success: false, errors: [err?.message || 'Unknown error'] };
	}
}

// (createProductFull is exposed as a class method above)
