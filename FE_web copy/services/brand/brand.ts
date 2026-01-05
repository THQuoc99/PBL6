import { apiClient } from '../callAPI/apiClient';

export const getBrandById = async (brandId: number) => {
  const query = `query GetBrand($brandId: Int){ brand(brandId: $brandId){ brandId name slug description logo country isActive createdAt updatedAt } }`;
  const vars = { brandId };
  const res = await apiClient.publicApiCall(query, vars);
  return res;
};

export const getBrandBySlug = async (slug: string) => {
  const query = `query GetBrandBySlug($slug: String){ brand(slug: $slug){ brandId name slug description logo country isActive createdAt updatedAt } }`;
  const vars = { slug };
  const res = await apiClient.publicApiCall(query, vars);
  return res;
};

export const listBrands = async (isActive?: boolean) => {
  const query = `query ListBrands($isActive: Boolean){ brands(isActive: $isActive){ brandId name slug logo country isActive } }`;
  const vars = { isActive };
  const res = await apiClient.publicApiCall(query, vars);
  return res;
};

export const createBrand = async (input: { name: string; slug?: string; description?: string; country?: string; isActive?: boolean }) => {
  const mutation = `mutation CreateBrand($name: String!, $slug: String, $description: String, $country: String, $isActive: Boolean){ createBrand(name: $name, slug: $slug, description: $description, country: $country, isActive: $isActive){ success brand{ brandId name slug } errors } }`;
  const vars = input;
  const res = await apiClient.authenticatedApiCall(mutation, vars);
  return res;
};

export const updateBrand = async (brandId: number, input: { name?: string; slug?: string; description?: string; country?: string; isActive?: boolean }) => {
  const mutation = `mutation UpdateBrand($brandId: Int!, $name: String, $slug: String, $description: String, $country: String, $isActive: Boolean){ updateBrand(brandId: $brandId, name: $name, slug: $slug, description: $description, country: $country, isActive: $isActive){ success brand{ brandId name slug } errors } }`;
  const vars = { brandId, ...input };
  const res = await apiClient.authenticatedApiCall(mutation, vars);
  return res;
};

export const deleteBrand = async (brandId: number) => {
  const mutation = `mutation DeleteBrand($brandId: Int!){ deleteBrand(brandId: $brandId){ success errors } }`;
  const vars = { brandId };
  const res = await apiClient.authenticatedApiCall(mutation, vars);
  return res;
};

export default {
  getBrandById,
  getBrandBySlug,
  listBrands,
  createBrand,
  updateBrand,
  deleteBrand,
};
