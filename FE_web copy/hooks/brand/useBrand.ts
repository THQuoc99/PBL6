import { useState, useCallback } from 'react';
import * as brandService from '../../services/brand/brand';

export const useBrands = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<any>(null);

  const fetch = useCallback(async (isActive?: boolean) => {
    setLoading(true);
    setError(null);
    try {
      const res = await brandService.listBrands(isActive);
      const payload = res?.data?.brands || [];
      return payload;
    } catch (err) {
      setError(err);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  return { fetchBrands: fetch, loading, error };
};

export const useBrand = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<any>(null);

  const fetchById = useCallback(async (brandId: number) => {
    setLoading(true);
    setError(null);
    try {
      const res = await brandService.getBrandById(brandId);
      return res?.data?.brand ?? null;
    } catch (err) {
      setError(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchBySlug = useCallback(async (slug: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await brandService.getBrandBySlug(slug);
      return res?.data?.brand ?? null;
    } catch (err) {
      setError(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { fetchById, fetchBySlug, loading, error };
};

export const useCreateBrand = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<any>(null);

  const create = useCallback(async (input: any) => {
    setLoading(true);
    setError(null);
    try {
      const res = await brandService.createBrand(input);
      return res?.data?.createBrand ?? res?.data?.create_brand ?? res;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { createBrand: create, loading, error };
};

export const useUpdateBrand = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<any>(null);

  const update = useCallback(async (brandId: number, input: any) => {
    setLoading(true);
    setError(null);
    try {
      const res = await brandService.updateBrand(brandId, input);
      return res?.data?.updateBrand ?? res?.data?.update_brand ?? res;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { updateBrand: update, loading, error };
};

export const useDeleteBrand = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<any>(null);

  const remove = useCallback(async (brandId: number) => {
    setLoading(true);
    setError(null);
    try {
      const res = await brandService.deleteBrand(brandId);
      return res?.data?.deleteBrand ?? res?.data?.delete_brand ?? res;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { deleteBrand: remove, loading, error };
};

export default {
  useBrands,
  useBrand,
  useCreateBrand,
  useUpdateBrand,
  useDeleteBrand,
};
