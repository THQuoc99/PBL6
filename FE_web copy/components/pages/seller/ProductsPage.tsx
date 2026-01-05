import { useState, useEffect, useMemo } from "react";
import { Search, Plus, ChevronDown, ChevronUp, Edit, Trash2, Save } from "lucide-react";
import { Product } from "../../../types";
import { Modal, Toggle, TextField, SelectField, ImageUploader, ToolbarButton } from "../../index";
import { useStoreAuth } from '../../../hooks/store/storeAuth';
import { useProducts } from '../../../hooks/product/productSeller';
import { useCategories } from '../../../hooks/category/categorys';
import { useBrands, useCreateBrand } from '../../../hooks/brand/useBrand';
import useCreateProductFull from '../../../hooks/product/useCreateProductFull';
import useUpdateProductFull from '../../../hooks/product/updateProductFull';
import { useProductDetail } from '../../../hooks/product/productDetail';

interface ProductsPageProps {
  products: Product[];
  setProducts: (products: Product[]) => void;
}

// Local attribute shape for seller page (kept local to avoid depending on external types)
type AttributeValue = string | { value: string; image?: string };
type AttributeLocal = {
  attributeId?: string; // 'color' | 'size' | ...
  label?: string; // human label shown in select
  name?: string;
  values: AttributeValue[];
};

type LocalProduct = {
  id: string;
  name: string;
  slug?: string;
  sku?: string;
  price?: number;
  stock?: number;
  images?: Array<string | { preview?: string; file?: File }>;
  active?: boolean;
  attributes?: AttributeLocal[];
  variants?: any[];
  description?: string;
  createdAt?: string;
  category?: any;
  // brand can be a simple string or numeric id, or a richer object returned from brand APIs
  brand?: string | number | { brandId?: number };
};

// Helpers to convert local shapes into Product-compatible shapes
const mapAttributeLocalToProductAttr = (a: AttributeLocal) => {
  return {
    name: a.label || a.attributeId || 'attr',
    // keep values as-is (strings or {value,image}), backend can digest as needed
    values: a.values || [],
  };
};

const localToProduct = (l: LocalProduct): Product => {
  return {
    id: l.id,
    name: l.name,
    // product type expects `sku` present; prefer slug then sku then id
    sku: l.slug || l.sku || l.id,
    category: l.category as any,
    price: l.price || 0,
    stock: l.stock || 0,
    images: (l.images || []).map((it: any) => (typeof it === 'string' ? it : (it?.preview || ''))),
    attributes: (l.attributes || []).map(mapAttributeLocalToProductAttr) as any,
    variants: l.variants || [],
    active: l.active !== false,
    createdAt: l.createdAt,
  } as Product;
};

// Helper function to generate unique ID
const uid = (prefix: string) => `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
import { useDeleteProduct } from '../../../hooks/product/delProduct';

export default function ProductsPage({ products, setProducts }: ProductsPageProps) {
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<LocalProduct | null>(null);
  const [detailId, setDetailId] = useState<string | null>(null);
  const { product: detailProduct, loading: loadingDetail } = useProductDetail(detailId || '');
  const [query, setQuery] = useState("");
  const [sortType, setSortType] = useState<'popular' | 'newest' | 'price-low' | 'price-high'>('popular');
  const [sortAsc, setSortAsc] = useState(false);
  const [dateFilter, setDateFilter] = useState<"all" | "today" | "week" | "month" | "range">("all");
  const [createdFrom, setCreatedFrom] = useState<string | null>(null);
  const [createdTo, setCreatedTo] = useState<string | null>(null);

  // fetch products from backend for this seller
  const { store } = useStoreAuth();
  // Add createdAt to products if not exists
  const productsWithDate = products.map(p => ({
    ...p,
    createdAt: p.createdAt || new Date().toISOString()
  }));

  // Build backend filter (includes fixed storeId and date flags)
  const filterForApi = useMemo(() => {
    const f: any = {};
    if (store?.storeId) f.storeId = store.storeId;
    if (dateFilter === 'today') f.createdToday = true;
    if (dateFilter === 'week') f.createdThisWeek = true;
    if (dateFilter === 'month') f.createdThisMonth = true;
    // 'all' -> don't include any convenience flags (leave filter unspecified)
    if (dateFilter === 'range') {
      if (createdFrom) f.createdFrom = createdFrom;
      if (createdTo) f.createdTo = createdTo;
    }
    return Object.keys(f).length ? f : undefined;
  }, [store?.storeId, dateFilter, createdFrom, createdTo]);

  const sortByValue = useMemo(() => {
    switch (sortType) {
      case 'price-low':
        return 'PRICE_ASC';
      case 'price-high':
        return 'PRICE_DESC';
      case 'newest':
        return 'NEWEST';
      case 'popular':
      default:
        return 'SALES_DESC';
    }
  }, [sortType, sortAsc]);

  const paging = useMemo(() => ({ first: 50 }), []);

  // load full categories for the add-product form
  const { categories: categoriesData, loading: categoriesLoading } = useCategories(undefined, undefined);
  const categoryOptions = useMemo(() => {
    if (!categoriesData || categoriesData.length === 0) return ["Chung"];
    return categoriesData.map((c: any) => c.name);
  }, [categoriesData]);

  // load brands for the add-product form (seller chooses brand)
  const { fetchBrands, loading: brandsLoading } = useBrands();
  const [brandOptions, setBrandOptions] = useState<string[]>([]);
  const [fetchedBrandsList, setFetchedBrandsList] = useState<any[]>([]);
  const { createBrand, loading: creatingBrand } = useCreateBrand();
  // hooks to create / update full product (call services)
  const { createProductFull, loading: creatingProduct } = useCreateProductFull();
  const { update: updateProductFull, loading: updatingProduct } = useUpdateProductFull();
  const [showNewBrandInput, setShowNewBrandInput] = useState(false);
  const [newBrandName, setNewBrandName] = useState('');
  const ADD_BRAND_LABEL = 'Thêm thương hiệu...';

  useEffect(() => {
    // fetch active brands when modal opens
    if (!open) return;
    let mounted = true;
    (async () => {
      try {
        const data = await fetchBrands(true);
        setFetchedBrandsList(data || []);
        if (!mounted) return;
        const opts = (data || []).map((b: any) => b.name || b.title || '');
        // ensure we include the special add option at the end
        const final = opts.length ? opts : ["Không có thương hiệu"];
        if (!final.includes(ADD_BRAND_LABEL)) final.push(ADD_BRAND_LABEL);
        setBrandOptions(final);
      } catch (e) {
        // ignore
      }
    })();
    return () => { mounted = false; };
  }, [open, fetchBrands]);

  // Don't fetch until we have the seller storeId to avoid querying all products
  const { products: fetchedProducts, loading: fetchingProducts } = useProducts(
    store?.storeId ? filterForApi : undefined,
    sortByValue,
    paging
  );

  useEffect(() => {
    if (fetchedProducts !== undefined) {
      // always update products when we receive a response (allow empty result)
      setProducts(fetchedProducts || []);
    }
  }, [fetchedProducts]);

  // Filter by date range
  const filterByDate = (products: any[]) => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
    const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);

    switch (dateFilter) {
      case "today":
        return products.filter(p => new Date(p.createdAt) >= today);
      case "week":
        return products.filter(p => new Date(p.createdAt) >= weekAgo);
      case "month":
        return products.filter(p => new Date(p.createdAt) >= monthAgo);
      default:
        return products;
    }
  };

  const filtered = filterByDate(productsWithDate)
    .filter((p) => 
      p.name.toLowerCase().includes(query.toLowerCase()) || 
      ((p as any).sku || (p as any).slug || '').toLowerCase().includes(query.toLowerCase())
    )
    .sort((a, b) => {
      let comparison = 0;
      switch (sortType) {
        case 'price-low':
          comparison = a.price - b.price;
          break;
        case 'price-high':
          comparison = b.price - a.price;
          break;
        case 'newest':
          comparison = new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
          break;
        case 'popular':
        default:
          // best-effort: try sold_count or soldCount, else fallback to name
          const sa = (a as any).sold_count ?? (a as any).soldCount ?? 0;
          const sb = (b as any).sold_count ?? (b as any).soldCount ?? 0;
          comparison = sb - sa;
      }
      return comparison;
    });

  const startCreate = () => {
    setEditing({ 
      id: uid("P"), 
      name: "", 
      slug: "", 
      stock: 0, 
      price: 0, 
      images: [], 
      active: true,
      // attribute objects will use { attributeId, label, values }
      attributes: [{ attributeId: '', label: '', values: [''] }],
      variants: [],
      description: '',
      createdAt: new Date().toISOString(),
    });
    setOpen(true);
  };

  const startEdit = (p: Product) => {
    // Request full product detail and open modal; mapping will occur when detail loads
    // Some product objects from list use `productId` while others use `id` — prefer `productId`.
    const pid = (p as any).productId ?? (p as any).id ?? '';
    setDetailId(String(pid));
    setEditing(null);
    setOpen(true);
  };

  // When detailed product loads, map its fields into our LocalProduct shape
  useEffect(() => {
    if (!detailProduct) return;
    try {
      const dp: any = detailProduct;
      const mappedAttrs: AttributeLocal[] = [];
      if (Array.isArray(dp.colorOptions) && dp.colorOptions.length) {
        mappedAttrs.push({
          attributeId: 'color',
          label: 'Màu Sắc',
          values: dp.colorOptions.map((c: any) => ({ value: c.value, image: c.imageUrl || undefined })),
        });
      }
      if (Array.isArray(dp.sizeOptions) && dp.sizeOptions.length) {
        mappedAttrs.push({
          attributeId: 'size',
          label: 'Size',
          values: dp.sizeOptions.map((s: any) => (s.value)),
        });
      }

      const gallery = Array.isArray(dp.galleryImages) ? dp.galleryImages.map((g: any) => g.imageUrl).filter(Boolean) : [];

            const variants = Array.isArray(dp.variants?.edges)
        ? dp.variants.edges.map((e: any) => {
            const n = e?.node || {};
            const vid = n.variantId ?? n.id ?? uid('V');
            const sku = n.sku || String(vid);
            const price = Number(n.finalPrice ?? n.price ?? dp.basePrice ?? 0);
            const stock = Number(n.stock ?? 0);
            const attrs: any[] = [];

            // Primary common fields (older schema)
            if (n.colorName) attrs.push({ name: 'color', value: n.colorName });
            if (n.sizeName) attrs.push({ name: 'size', value: n.sizeName });

            // Fallback: some APIs return an object of option combinations
            const ocCandidate = n.optionCombinations ?? n.option_combinations ?? n.option_combinations_json ?? n.option_combinations_text;
            if (ocCandidate && Object.keys(attrs).length === 0) {
              let oc: any = ocCandidate;
              if (typeof ocCandidate === 'string') {
                try { oc = JSON.parse(ocCandidate); } catch (err) { oc = null; }
              }
              if (oc && typeof oc === 'object') {
                for (const [k, v] of Object.entries(oc)) {
                  // prefer short keys (color/size) when available, else use key as-is
                  attrs.push({ name: String(k), value: String(v) });
                }
              }
            }

            // Another fallback: some nodes include an array of option objects
            if ((attrs.length === 0) && Array.isArray(n.options)) {
              for (const opt of n.options) {
                const name = opt.name || opt.optionName || opt.attribute || opt.attributeName;
                const value = opt.value || opt.optionValue || opt.valueName;
                if (name && value) attrs.push({ name, value });
              }
            }

            return {
              id: String(vid),
              sku,
              price,
              stock,
              attributes: attrs,
              // keep original node for any extra fields
              raw: n,
            };
          })
        : [];

      // If no explicit color/size option lists were provided, derive attributes from variants
      if (mappedAttrs.length === 0 && Array.isArray(variants) && variants.length) {
        const attrMap = new Map<string, Set<string>>();
        const attrImageMap = new Map<string, Map<string, string>>();

        variants.forEach((v: any) => {
          const raw = v.raw || {};
          // prefer already-parsed attributes array on variant
          if (Array.isArray(v.attributes) && v.attributes.length) {
            v.attributes.forEach((a: any) => {
              const name = (a.name || a.label || String(a.attribute || '')).toString();
              const value = a.value ?? a.optionValue ?? a.valueName ?? '';
              if (!attrMap.has(name)) attrMap.set(name, new Set());
              attrMap.get(name)!.add(String(value));
              if (name.toLowerCase() === 'color') {
                const img = raw.colorImageUrl || raw.colorImage || raw.color_image_url || raw.color_image;
                if (img) {
                  if (!attrImageMap.has(name)) attrImageMap.set(name, new Map());
                  attrImageMap.get(name)!.set(String(value), img);
                }
              }
            });
            return;
          }

          // fallback: parse option combinations object/string
          let oc: any = raw.optionCombinations ?? raw.option_combinations ?? raw.option_combinations_json ?? raw.option_combinations_text ?? raw.option_combinations;
          if (typeof oc === 'string') {
            try { oc = JSON.parse(oc); } catch (e) { oc = null; }
          }
          if (oc && typeof oc === 'object') {
            for (const [k, v] of Object.entries(oc)) {
              const name = String(k);
              const value = v as any;
              if (!attrMap.has(name)) attrMap.set(name, new Set());
              attrMap.get(name)!.add(String(value));
            }
          }
        });

        // Build mappedAttrs from collected attribute map
        const labelFor = (id: string) => {
          if (!id) return id;
          const low = id.toLowerCase();
          if (low === 'color') return 'Màu Sắc';
          if (low === 'size') return 'Size';
          return id;
        };

        for (const [name, vals] of attrMap.entries()) {
          const arr = Array.from(vals).map((val) => {
            if (name.toLowerCase() === 'color') {
              const img = attrImageMap.get(name)?.get(val);
              return { value: val, image: img || undefined };
            }
            return val;
          });
          mappedAttrs.push({ attributeId: name.toLowerCase(), label: labelFor(name), values: arr as any });
        }
      }

      // determine category and brand values for the selects
      const categoryVal = dp.category ? (dp.category.name || dp.category.title || dp.category.categoryId || undefined) : undefined;
      let brandVal: any = undefined;
      if (dp.brand && (dp.brand.brandId || dp.brand.id || dp.brand.brand_id)) {
        const bid = dp.brand.brandId || dp.brand.id || dp.brand.brand_id;
        const found = (fetchedBrandsList || []).find((b: any) => (b.brandId == bid || b.id == bid || b.brand_id == bid));
        brandVal = found ? (found.name || found.title) : String(bid);
      }

      const local: LocalProduct = {
        id: String(dp.productId || dp.id || ''),
        name: dp.name || '',
        slug: dp.slug || undefined,
        sku: dp.slug || String(dp.productId || dp.id || ''),
        price: Number(dp.basePrice || 0),
        stock: 0,
        images: gallery,
        active: dp.isActive !== false,
        attributes: mappedAttrs,
        variants,
        description: dp.description || '',
        createdAt: dp.createdAt || undefined,
        category: categoryVal,
        brand: brandVal,
      };

      setEditing(local);
    } catch (err) {
      // ignore mapping errors
      console.error('Failed to map detailProduct to editing:', err);
    }
  }, [detailProduct]);

  const { deleteProduct: deleteProductApi, loading: deleting } = useDeleteProduct();

  const remove = async (id: string) => {
    if (!confirm("Xóa sản phẩm này?")) return;
    try {
      // attempt to parse numeric productId, fallback to local removal
      const pid = Number(id);
      if (!Number.isNaN(pid) && pid > 0) {
        const res = await deleteProductApi(pid);
        if (res && res.success) {
          setProducts(products.filter((p) => p.id !== id));
          return;
        }
        alert('Xóa sản phẩm thất bại: ' + (res?.errors ? res.errors.join(', ') : 'Unknown'));
        return;
      }
      // fallback local removal for unsaved items
      setProducts(products.filter((p) => p.id !== id));
    } catch (err: any) {
      console.error('remove error', err);
      alert('Lỗi khi xóa sản phẩm: ' + (err?.message || err));
    }
  };

  const save = () => {
    if (!editing) return;
    if (!editing.name || !((editing as any).slug || (editing as any).sku)) {
      alert("Tên và Mã model là bắt buộc");
      return;
    }

    // Prepare minimal CreateProductFullInput and call backend
    (async () => {
      try {
        // find categoryId: prefer numeric id on editing.category, else match by name
        let categoryId: any = undefined;
        if (editing.category && typeof editing.category === 'object') {
          categoryId = editing.category.categoryId || editing.category.id || editing.category.category_id;
        } else if (typeof editing.category === 'string') {
          const found = (categoriesData || []).find((c: any) => c.name === editing.category);
          categoryId = found ? found.categoryId || found.category_id : undefined;
        }

        if (!categoryId && categoriesData && categoriesData.length) {
          // fallback to first category
          categoryId = categoriesData[0].categoryId || categoriesData[0].category_id;
        }

        if (!store || !store.storeId) {
          console.error('No store context; cannot create product on backend. store:', store);
          alert('Không có thông tin cửa hàng. Vui lòng đăng nhập/thiết lập cửa hàng để tạo sản phẩm.');
          return;
        }

        // Map variants and normalize optionCombinations to object (backend expects optionCombinations)
        const variants = (editing.variants || []).map((v: any) => {
          const sku = v.sku || v.id || `${editing.slug || editing.sku || 'NEW'}-${Math.random().toString(36).slice(2,6)}`;
          const price = Number(v.price ?? editing.price ?? 0);
          const stock = Number(v.stock ?? editing.stock ?? 0);

          let optionCombinations: any = {};
          if (v.optionCombinations) optionCombinations = v.optionCombinations;
          else if (v.option_combinations) optionCombinations = v.option_combinations;
          else if (v.attributes && Array.isArray(v.attributes)) {
            optionCombinations = v.attributes.reduce((acc: any, a: any) => {
              const key = a.name || a.label || a.attributeId || 'attr';
              acc[key] = a.value;
              return acc;
            }, {} as Record<string, any>);
          }

          return {
            sku,
            price,
            stock,
            optionCombinations,
          };
        });

        // normalize categoryId to primitive (backend expects ID)
        const normalizedCategoryId = Number(categoryId);
        // compute brandId safely with runtime type checks
        let brandId: number | undefined = undefined;
        if (typeof editing.brand === 'number') {
          brandId = editing.brand;
        } else if (editing.brand && typeof editing.brand === 'object') {
          brandId = (editing.brand as any).brandId || (editing.brand as any).id || (editing.brand as any).brand_id;
        } else if (typeof editing.brand === 'string') {
          // map selected brand name to id if possible
          const found = (fetchedBrandsList || []).find((b: any) => (b.name || b.title) === editing.brand);
          brandId = found ? (found.brandId || found.id || found.brand_id) : undefined;
        } else {
          brandId = undefined;
        }

        const input: any = {
          storeId: store.storeId,
          categoryId: normalizedCategoryId,
          name: editing.name,
          slug: editing.slug || undefined,
          description: editing.description || '',
          basePrice: Number(editing.price || 0),
          brandId: brandId,
          isFeatured: (editing as any).isFeatured || false,
          isActive: editing.active !== false,
          variants,
        };

    // helper: convert data-URL (base64) to File
    const dataURLtoFile = (dataurl: string, filename = 'image') => {
      try {
        const arr = dataurl.split(',');
        const mime = arr[0].match(/:(.*?);/)?.[1] || 'image/png';
        const bstr = atob(arr[1]);
        let n = bstr.length;
        const u8arr = new Uint8Array(n);
        while (n--) {
          u8arr[n] = bstr.charCodeAt(n);
        }
        // Ensure filename has an extension matching mime
        const ext = (mime.split('/')[1] || 'png').split('+')[0];
        const finalName = filename && filename.includes('.') ? filename : `${filename}.${ext}`;
        return new File([u8arr], finalName, { type: mime });
      } catch (e) {
        return null;
      }
    };

    // Attach images: convert data-URL strings to File objects for upload
    if (Array.isArray(editing.images) && editing.images.length) {
      const imgs: any[] = [];
      for (let i = 0; i < editing.images.length; i++) {
        const raw = (editing.images as any)[i];
        // If it's already a File
        if (raw instanceof File) {
          const resized = await resizeImageFile(raw);
          imgs.push({ image: resized, isThumbnail: i === 0, altText: '', displayOrder: i });
          continue;
        }

        // If it's an object with a `file` property
        if (raw && typeof raw === 'object' && 'file' in raw && raw.file instanceof File) {
          const resized = await resizeImageFile(raw.file);
          imgs.push({ image: resized, isThumbnail: i === 0, altText: '', displayOrder: i });
          continue;
        }

        // If it's a data-URL string
        if (typeof raw === 'string' && raw.startsWith('data:')) {
          const file = dataURLtoFile(raw, `${editing.id || 'img'}_${i}.png`);
          if (file) {
            const resized = await resizeImageFile(file);
            imgs.push({ image: resized, isThumbnail: i === 0, altText: '', displayOrder: i });
          }
          continue;
        }

        // If it's an object with a preview data-URL
        if (raw && typeof raw === 'object' && typeof raw.preview === 'string' && raw.preview.startsWith('data:')) {
          const file = dataURLtoFile(raw.preview, `${editing.id || 'img'}_${i}.png`);
          if (file) {
            const resized = await resizeImageFile(file);
            imgs.push({ image: resized, isThumbnail: i === 0, altText: '', displayOrder: i });
          }
          continue;
        }
      }
      if (imgs.length) input.images = imgs;
    }

    // Build attributeOptions from editing.attributes (convert image data-URLs to File)
    if (Array.isArray(editing.attributes) && editing.attributes.length) {
      const attrOpts: any[] = [];
      for (const attr of editing.attributes) {
        const attributeId = attr.attributeId || attr.label || attr.name;
        if (!attributeId) continue;
        for (let vi = 0; vi < (attr.values || []).length; vi++) {
          const val = attr.values[vi];
          if (typeof val === 'string') {
            attrOpts.push({ attributeId, value: val });
          } else if (val && typeof val === 'object') {
            const ao: any = { attributeId, value: val.value || '', displayOrder: vi };
            const imgVal = (val as any).image;
            if (imgVal instanceof File) {
              ao.image = await resizeImageFile(imgVal);
            } else if (imgVal && typeof imgVal === 'object' && imgVal.file instanceof File) {
              ao.image = await resizeImageFile(imgVal.file);
            } else if (typeof imgVal === 'string' && imgVal.startsWith('data:')) {
              const f = dataURLtoFile(imgVal, `${editing.id || 'attr'}_${attributeId}_${vi}.png`);
              if (f) ao.image = await resizeImageFile(f);
              else ao.image = imgVal;
            } else if (imgVal && typeof imgVal === 'object' && typeof imgVal.preview === 'string' && imgVal.preview.startsWith('data:')) {
              const f = dataURLtoFile(imgVal.preview, `${editing.id || 'attr'}_${attributeId}_${vi}.png`);
              if (f) ao.image = await resizeImageFile(f);
              else ao.image = imgVal.preview;
            }
            attrOpts.push(ao);
          }
        }
      }
      if (attrOpts.length) input.attributeOptions = attrOpts;
    }

    // sizeGuideImage if present as File, object with file, or data-URL/preview (resize before upload)
    const sizeGuide = (editing as any).sizeGuideImage;
    if (sizeGuide instanceof File) {
      input.sizeGuideImage = await resizeImageFile(sizeGuide);
    } else if (sizeGuide && typeof sizeGuide === 'object' && sizeGuide.file instanceof File) {
      input.sizeGuideImage = await resizeImageFile(sizeGuide.file);
    } else if (typeof sizeGuide === 'string' && sizeGuide.startsWith('data:')) {
      const f = dataURLtoFile(sizeGuide, `${editing.id || 'sizeguide'}.png`);
      if (f) input.sizeGuideImage = await resizeImageFile(f);
    } else if (sizeGuide && typeof sizeGuide === 'object' && typeof sizeGuide.preview === 'string' && sizeGuide.preview.startsWith('data:')) {
      const f = dataURLtoFile(sizeGuide.preview, `${editing.id || 'sizeguide'}.png`);
      if (f) input.sizeGuideImage = await resizeImageFile(f);
    }

        // call hook/service to create or update product
        const isLocalNew = typeof editing.id === 'string' && editing.id.startsWith('P_');
        if (!isLocalNew) {
          // attempt update using numeric productId
          const productId = Number(editing.id);
          if (!Number.isNaN(productId)) {
            console.log('Calling updateProductFull with productId:', productId, 'input:', input);
            const res = await updateProductFull(productId, input);
            console.log('updateProductFull response:', res);
            if (res && res.success) {
              // update local list (replace existing)
              const updated = (products || []).map((p: Product) => (String(p.id) === String(editing.id) ? (res.product || p) : p));
              setProducts(updated);
              setOpen(false);
              setEditing(null);
              return;
            }
            alert('Cập nhật sản phẩm thất bại: ' + (res.errors ? res.errors.join(', ') : 'Unknown'));
            return;
          }
        }

        // fallback: create new product
        console.log('Calling createProductFull with input:', input);
        const res = await createProductFull(input);
        console.log('createProductFull response:', res);

        if (res && res.success) {
          // map returned product to local shape and insert
          const created = res.product || null;
          const out = localToProduct({
            id: created ? created.productId : editing.id,
            name: editing.name,
            slug: created ? created.slug || editing.slug : editing.slug,
            sku: editing.sku,
            price: editing.price,
            stock: editing.stock,
            images: editing.images,
            active: editing.active,
            attributes: editing.attributes,
            variants: editing.variants,
            description: editing.description,
            createdAt: new Date().toISOString(),
            category: editing.category,
          });

          const exists = products.some((p) => p.id === out.id);
          const next = exists ? products.map((p) => (p.id === out.id ? out : p)) : [out, ...products];
          setProducts(next);
          setOpen(false);
          alert('Tạo sản phẩm thành công');
          return;
        }

        alert('Tạo sản phẩm thất bại: ' + (res.errors ? res.errors.join(', ') : 'Unknown'));
      } catch (err: any) {
        console.error('save createProductFull error', err);
        alert('Lỗi khi tạo sản phẩm: ' + (err?.message || err));
      }
    })();
  };

  // ---- Multi-step product creation (demo-only) ----
  const [step, setStep] = useState(0);

  // The editing object will be enriched for multi-step flow
  const editingAttributes = (editing?.attributes || []) as AttributeLocal[];
  const editingVariants = editing?.variants || [];

  const setEditingAttributes = (attrs: any[]) => {
    if (!editing) return;
    setEditing({ ...editing, attributes: attrs });
  };

  const setEditingVariants = (vars: any[]) => {
    if (!editing) return;
    setEditing({ ...editing, variants: vars });
  };

  // Helper: Cartesian product to auto-generate variants from attributes
  const cartesianVariants = (attrs: any[]) => {
    if (!attrs.length) return [];
    const pools = attrs.map((a: any) => a.values.map((v: any) => ({ name: a.label || a.attributeId, value: typeof v === 'string' ? v : v?.value })));
    const results: any[] = [];
    const helper = (i: number, acc: any[]) => {
      if (i === pools.length) {
        results.push(acc);
        return;
      }
      for (const val of pools[i]) helper(i + 1, [...acc, val]);
    };
    helper(0, []);
    
    // Generate SKUs: SKU-màu-size format
    return results.map((attrsSet, idx) => {
      const baseSku = editing?.slug || editing?.sku || "NEW";
      let variantSku = baseSku;

      // Add attribute values to SKU, taking first letters for longer values
      attrsSet.forEach((attr: any) => {
        let attrValue = attr.value;
        // If value is longer than 2 characters, take first letters of each word
        if (attrValue && attrValue.length > 2) {
          attrValue = attrValue.split(' ').map((word: string) => word.charAt(0).toUpperCase()).join('');
        }
        variantSku += `-${attrValue}`;
      });

      // Build option_combinations object expected by backend
      const option_combinations = attrsSet.reduce((acc: any, a: any) => {
        const key = a.name || a.label || a.attributeId || 'attr';
        acc[key] = a.value;
        return acc;
      }, {} as Record<string, any>);

      return {
        id: uid("V"),
        sku: variantSku,
        price: editing?.price || 0,
        stock: editing?.stock || 0,
        attributes: attrsSet,
        option_combinations, // add object so backend JSONField receives it
      };
    });
  };

  // Normalize various image-like values to a string/Blob acceptable for <img src>
  const getImageSrc = (it: any): string | Blob => {
    if (!it) return '';
    if (typeof it === 'string') return it;
    // If it's a File use an object URL for preview
    try {
      if ((it as any) instanceof File) return URL.createObjectURL(it as File);
    } catch (e) {
      // ignore
    }
    if (typeof it === 'object') {
      if (typeof it.preview === 'string') return it.preview;
      if (typeof it.image === 'string') return it.image;
    }
    return '';
  };

  // Resize image File to max dimensions (preserve aspect ratio). If image is within limits, returns original file.
  const resizeImageFile = (file: File, maxDim = 2000, quality = 0.9): Promise<File> => {
    return new Promise((resolve) => {
      try {
        const img = new Image();
        const url = URL.createObjectURL(file);
        img.onload = () => {
          const width = img.width || 0;
          const height = img.height || 0;
          // If already within limits, return original
          if (width <= maxDim && height <= maxDim) {
            URL.revokeObjectURL(url);
            resolve(file);
            return;
          }
          const ratio = Math.min(maxDim / width, maxDim / height);
          const newW = Math.max(1, Math.round(width * ratio));
          const newH = Math.max(1, Math.round(height * ratio));
          const canvas = document.createElement('canvas');
          canvas.width = newW;
          canvas.height = newH;
          const ctx = canvas.getContext('2d');
          if (!ctx) {
            URL.revokeObjectURL(url);
            resolve(file);
            return;
          }
          ctx.drawImage(img, 0, 0, newW, newH);
          const outType = file.type === 'image/png' ? 'image/png' : 'image/jpeg';
          // toBlob quality param ignored for PNG
          canvas.toBlob((blob) => {
            if (!blob) {
              URL.revokeObjectURL(url);
              resolve(file);
              return;
            }
            // Ensure the new File has a valid name (fallback to extension from blob type)
            const blobType = blob.type || outType || 'image/png';
            const ext = (blobType.split('/')[1] || 'png').split('+')[0];
            const baseName = (file && file.name) ? file.name : `image`;
            const hasExt = baseName.includes('.');
            const finalName = hasExt ? baseName : `${baseName}.${ext}`;
            const newFile = new File([blob], finalName, { type: blobType });
            URL.revokeObjectURL(url);
            resolve(newFile);
          }, outType, outType === 'image/png' ? undefined : quality);
        };
        img.onerror = () => {
          try { URL.revokeObjectURL(url); } catch (e) {}
          resolve(file);
        };
        img.src = url;
      } catch (e) {
        resolve(file);
      }
    });
  };


  // Format currency
  const fmt = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });

  const ATTRIBUTE_OPTIONS = [
    { id: 'color', label: 'Màu Sắc' },
    { id: 'size', label: 'Size' },
    { id: 'material', label: 'Chất Liệu' },
    { id: 'style', label: 'Kiểu dáng' },
    { id: 'custom', label: 'Khác' },
  ];

  return (
    <section className="space-y-4 w-full pl-0">
      <div className="flex flex-col gap-3">
        <div className="flex flex-col items-start justify-between gap-3 sm:flex-row sm:items-center">
          <div className="flex w-full items-center gap-2 sm:w-auto">
            <div className="relative w-full sm:w-80">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Tìm sản phẩm theo tên hoặc SKU…"
                className="w-full rounded-xl border border-gray-200 bg-white py-2.5 pl-10 pr-3 text-sm outline-none ring-0 placeholder:text-gray-400 focus:border-gray-300 focus:shadow-sm"
              />
            </div>
          </div>
          <ToolbarButton onClick={startCreate}>
            <Plus className="h-4 w-4" /> Thêm sản phẩm
          </ToolbarButton>
        </div>
        
        {/* Filters and Sort */}
        <div className="flex flex-wrap items-center gap-2 text-sm">
          <span className="text-gray-500 font-medium">Lọc theo ngày:</span>
          <select
            value={dateFilter}
            onChange={(e) => {
              const v = e.target.value as any;
              setDateFilter(v);
              // when switching away from range, clear explicit range values
              if (v !== 'range') {
                setCreatedFrom(null);
                setCreatedTo(null);
              }
              // fetching is handled by the hook via `filterForApi`
            }}
            className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm bg-white hover:bg-gray-50"
          >
            <option value="all">Tất cả thời gian</option>
            <option value="today">Hôm nay</option>
            <option value="week">Tuần này</option>
            <option value="month">Tháng này</option>
            <option value="range">Khoảng ngày</option>
          </select>

          {dateFilter === 'range' && (
            <div className="flex items-center gap-2 ml-2">
              <input
                type="date"
                value={createdFrom ? createdFrom.split('T')[0] : ''}
                onChange={(e) => {
                  const val = e.target.value;
                  const iso = val ? new Date(val + 'T00:00:00').toISOString() : null;
                  setCreatedFrom(iso);
                  // fetching handled by hook via filterForApi
                }}
                className="rounded-lg border border-gray-200 px-2 py-1 text-sm bg-white"
              />
              <span className="text-gray-400">→</span>
              <input
                type="date"
                value={createdTo ? createdTo.split('T')[0] : ''}
                onChange={(e) => {
                  const val = e.target.value;
                  const iso = val ? new Date(val + 'T23:59:59.999').toISOString() : null;
                  setCreatedTo(iso);
                  // fetching handled by hook via filterForApi
                }}
                className="rounded-lg border border-gray-200 px-2 py-1 text-sm bg-white"
              />
            </div>
          )}

          <span className="text-gray-500 font-medium ml-4">Lọc theo:</span>
          <select
            value={sortType}
            onChange={(e) => setSortType(e.target.value as any)}
            className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm bg-white hover:bg-gray-50"
          >
            <option value="popular">Phổ biến nhất</option>
            <option value="newest">Mới nhất</option>
            <option value="price-low">Giá tăng dần</option>
            <option value="price-high">Giá giảm dần</option>
          </select>


            <div className="text-gray-500 ml-4">
            Hiển thị {filtered.length} trên {products.length} sản phẩm
          </div>
        </div>
      </div>

      <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="text-left text-gray-500">
                <th className="px-3 py-2 font-medium">Sản phẩm</th>
                <th className="px-3 py-2 font-medium">Danh mục</th>
                <th className="px-3 py-2 font-medium">Mã model</th>
                <th className="px-3 py-2 font-medium">Kho</th>
                <th className="px-3 py-2 font-medium">Giá</th>
                <th className="px-3 py-2 font-medium">Ngày tạo</th>
                <th className="px-3 py-2 font-medium">Trạng thái</th>
                <th className="px-3 py-2 font-medium">Hành động</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((p) => (
                <tr key={p.id} className="border-t border-gray-100 hover:bg-gray-50">
                  <td className="px-3 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-lg overflow-hidden bg-gray-100 flex-shrink-0">
                        {p.images && p.images.length > 0 ? (
                          <img 
                            src={getImageSrc(p.images[0])} 
                            alt={p.name}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full bg-gray-200 flex items-center justify-center text-gray-400 text-xs">
                            Không có ảnh
                          </div>
                        )}
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="font-medium text-gray-900 truncate">{p.name}</div>
                        {p.variants && p.variants.length > 0 && (
                          <div className="text-xs text-gray-500">{p.variants.length} biến thể</div>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-3 py-3">
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gray-100 text-gray-600">
                      {typeof p.category === 'object' ? p.category?.name || 'Chung' : p.category || 'Chung'}
                    </span>
                  </td>
                  <td className="px-3 py-3 font-mono text-xs">{(p as any).slug || p.sku}</td>
                  <td className="px-3 py-3">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs ${
                      p.totalStock > 10 ? 'bg-green-100 text-green-700' :
                      p.totalStock > 0 ? 'bg-yellow-100 text-yellow-700' :
                      'bg-red-100 text-red-700'
                    }`}>
                      {p.totalStock} sp
                    </span>
                  </td>
                  <td className="px-3 py-3 font-medium">{fmt.format(p.price)}</td>
                  <td className="px-3 py-3 text-xs text-gray-500">
                    {p.createdAt ? new Date(p.createdAt).toLocaleDateString('vi-VN', {
                      day: '2-digit',
                      month: '2-digit',
                      year: 'numeric'
                    }) : 'Không rõ'}
                  </td>
                  <td className="px-3 py-3">
                    <Toggle
                      checked={p.active !== false}
                      onChange={(v) => setProducts(products.map((x) => (x.id === p.id ? { ...x, active: v } : x)))}
                    />
                  </td>
                  <td className="px-3 py-3">
                    <div className="flex gap-1">
                      <button 
                          className="rounded-lg border border-gray-200 p-1.5 hover:bg-gray-50 transition-colors" 
                          onClick={() => startEdit(p)}
                          title="Chỉnh sửa sản phẩm"
                        >
                        <Edit className="h-4 w-4 text-gray-600" />
                      </button>
                      <button 
                          className="rounded-lg border border-gray-200 p-1.5 hover:bg-gray-50 transition-colors" 
                          onClick={() => remove(p.id)}
                          title="Xóa sản phẩm"
                        >
                        <Trash2 className="h-4 w-4 text-rose-600" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title={
          <div className="flex flex-col gap-3">
            <div>{editing?.id ? (products.some((p) => p.id === editing.id) ? "Chỉnh sửa sản phẩm" : "Thêm sản phẩm") : "Thêm sản phẩm"}</div>
            {editing && (
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <button 
                  onClick={() => setStep(0)}
                  className={`px-2 py-1 ${step===0?"bg-gray-900 text-white":"bg-gray-100 hover:bg-gray-200"} rounded cursor-pointer transition-colors`}
                >
                  1
                </button>
                <div>Cơ bản</div>
                <button 
                  onClick={() => setStep(1)}
                  className={`px-2 py-1 ${step===1?"bg-gray-900 text-white":"bg-gray-100 hover:bg-gray-200"} rounded ml-4 cursor-pointer transition-colors`}
                >
                  2
                </button>
                <div>Thuộc tính</div>
                <button 
                  onClick={() => setStep(2)}
                  className={`px-2 py-1 ${step===2?"bg-gray-900 text-white":"bg-gray-100 hover:bg-gray-200"} rounded ml-4 cursor-pointer transition-colors`}
                >
                  3
                </button>
                <div>Biến thể</div>
                <button 
                  onClick={() => setStep(3)}
                  className={`px-2 py-1 ${step===3?"bg-gray-900 text-white":"bg-gray-100 hover:bg-gray-200"} rounded ml-4 cursor-pointer transition-colors`}
                >
                  4
                </button>
                <div>Ảnh</div>
                <button 
                  onClick={() => setStep(4)}
                  className={`px-2 py-1 ${step===4?"bg-gray-900 text-white":"bg-gray-100 hover:bg-gray-200"} rounded ml-4 cursor-pointer transition-colors`}
                >
                  5
                </button>
                <div>Xem lại</div>
              </div>
            )}
          </div>
        }
        footer={
          <div className="flex items-center justify-end gap-2">
            <button
              onClick={() => { setOpen(false); setStep(0); }}
              className="rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm hover:bg-gray-50"
            >
              Hủy
            </button>
            <div className="flex gap-2">
              {step > 0 && (
                <button
                  onClick={() => setStep((s) => Math.max(0, s - 1))}
                  className="rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm hover:bg-gray-50"
                >
                  Trước
                </button>
              )}
              {step < 4 && (
                <button
                  onClick={() => setStep((s) => Math.min(4, s + 1))}
                  className="rounded-xl bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-black"
                >
                  Tiếp
                </button>
              )}
                {step === 4 && (
                  (() => {
                    const isLocalNew = editing && typeof editing.id === 'string' && editing.id.startsWith('P_');
                    const loading = isLocalNew ? creatingProduct : updatingProduct;
                    const label = isLocalNew ? 'Tạo sản phẩm' : 'Cập nhật sản phẩm';
                    const bgClass = loading ? 'bg-gray-400' : (isLocalNew ? 'bg-green-600 hover:bg-green-700' : 'bg-blue-600 hover:bg-blue-700');
                    return (
                      <button
                        onClick={() => save()}
                        disabled={!!loading}
                        className={`inline-flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium text-white ${bgClass}`}
                      >
                        <Save className="h-4 w-4" /> {label}
                      </button>
                    );
                  })()
                )}
            </div>
          </div>
        }
      >
        {editing && (
          <div>

            {/* Step content */}
            {step === 0 && (
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <TextField 
                    label="Tên" 
                    value={editing.name} 
                    onChange={(v) => setEditing({ ...editing, name: v })}
                    onBlur={() => {
                      // Auto-generate slug when name field loses focus and slug is empty
                      if (editing && !editing.slug && editing.name) {
                        const generateSlug = (name: string) => {
                          return name
                            .trim()
                            .toLowerCase()
                            .replace(/[^a-z0-9\s-]/g, '')
                            .replace(/\s+/g, '-')
                            .replace(/-+/g, '-');
                        };
                        const newSlug = generateSlug(editing.name);
                        setEditing({ ...editing, slug: newSlug });
                      }
                    }}
                  />
                </div>
                <TextField label="Mã model" value={(editing as any).slug || ''} onChange={(v) => setEditing({ ...editing, slug: v })} />
                <SelectField label="Danh mục" value={editing.category || categoryOptions[0] || "Chung"} onChange={(v) => setEditing({ ...editing, category: v })} options={categoryOptions} />
                <div>
                  {showNewBrandInput ? (
                    <div>
                      <TextField
                        label="Thương hiệu (Nhập và nhấn Enter để tạo)"
                        value={newBrandName}
                        onChange={(v) => setNewBrandName(v)}
                        onKeyDown={async (e: any) => {
                          if (e.key === 'Enter' && newBrandName.trim()) {
                            try {
                              const created = await createBrand({ name: newBrandName.trim() });
                              // created should be the GraphQL payload like { success, brand, errors }
                              const success = created?.success ?? false;
                              const brandObj = created?.brand ?? null;
                              if (success && brandObj) {
                                const createdName = brandObj.name || newBrandName.trim();
                                const beforeAdd = brandOptions.filter(x => x !== ADD_BRAND_LABEL);
                                const nextOpts = [createdName, ...beforeAdd];
                                if (!nextOpts.includes(ADD_BRAND_LABEL)) nextOpts.push(ADD_BRAND_LABEL);
                                setBrandOptions(nextOpts);
                                setEditing({ ...editing, brand: createdName });
                                setShowNewBrandInput(false);
                                setNewBrandName('');
                              } else {
                                const errs = (created && (created.errors || created.error || created.message)) || 'Không thể tạo thương hiệu';
                                alert('Tạo thương hiệu thất bại: ' + (Array.isArray(errs) ? errs.join(', ') : String(errs)));
                              }
                            } catch (err) {
                              alert('Không thể tạo thương hiệu: ' + (err?.message || String(err)));
                            }
                          }
                          // allow other handlers to run
                        }}
                      />
                      <div className="mt-2 flex gap-2">
                        <button className="rounded-xl border px-3 py-1 text-sm" onClick={() => { setShowNewBrandInput(false); setNewBrandName(''); }}>
                          Hủy
                        </button>
                      </div>
                    </div>
                  ) : (
                    <SelectField
                      label="Thương hiệu"
                      value={(editing as any).brand || (brandOptions[0] || '')}
                      onChange={(v) => {
                        if (v === ADD_BRAND_LABEL) {
                          setShowNewBrandInput(true);
                          setNewBrandName('');
                          setEditing({ ...editing, brand: undefined });
                          return;
                        }
                        setEditing({ ...editing, brand: v });
                      }}
                      options={brandOptions.length ? brandOptions : ["Không có thương hiệu"]}
                    />
                  )}
                </div>
                <TextField label="Giá mặc định" type="number" value={editing.price} onChange={(v) => setEditing({ ...editing, price: Number(v) })} />
                <TextField label="Kho (mặc định)" type="number" value={editing.stock} onChange={(v) => setEditing({ ...editing, stock: Number(v) })} />
                <label className="grid gap-1 text-sm">
                  <span className="text-gray-600">Kích hoạt</span>
                  <div>
                    <Toggle checked={editing.active !== false} onChange={(v) => setEditing({ ...editing, active: v })} />
                  </div>
                </label>
                <div className="sm:col-span-2">
                  <TextField label="Mô tả ngắn (demo)" value={(editing as any).description || ""} onChange={(v) => setEditing({ ...editing, description: v })} />
                </div>
              </div>
            )}
            {step === 1 && (
              <div className="space-y-3">
                <div className="text-sm text-gray-600">Định nghĩa thuộc tính sản phẩm (ví dụ: Màu, Kích thước). Thuộc tính dùng để tạo biến thể.</div>
                {(editingAttributes.length ? editingAttributes : [{ attributeId: '', label: '', values: [''] }]).map((attr, idx) => (
                  <div key={idx} className="grid gap-2 sm:grid-cols-2 items-start">
                    <div>
                      <SelectField label="Tên thuộc tính" value={(attr as any).label || ''} onChange={(v: string) => {
                        const next = [...editingAttributes];
                        const existing = next[idx] || { attributeId: '', label: '', values: [''] };
                        const opt = ATTRIBUTE_OPTIONS.find(o => o.label === v);
                        const aid = opt ? opt.id : '';
                        next[idx] = { ...existing, attributeId: aid, label: v, values: existing.values || [''] };
                        // If switching to color ensure values are objects
                        if (aid === 'color') {
                          next[idx].values = (next[idx].values || []).map((x: any) => (typeof x === 'string' ? { value: x, image: undefined } : x));
                        } else {
                          next[idx].values = (next[idx].values || []).map((x: any) => (typeof x === 'string' ? x : x.value || ''));
                        }
                        setEditingAttributes(next);
                      }} options={ATTRIBUTE_OPTIONS.map(o => o.label)} />
                    </div>
                    <div className="sm:col-span-2">
                      <div className="space-y-3">
                        {/* Values section - scrollable if needed */}
                        <div className="flex flex-wrap gap-2">
                          {(attr.values || []).map((val: any, vi: number) => {
                            const valueStr = typeof val === 'string' ? val : val?.value || '';
                            return (
                              <div key={vi} className="flex flex-col gap-1 min-w-[120px]">
                                  <TextField label={`Giá trị ${vi+1}`} value={valueStr} onChange={(v) => {
                                  const next = [...editingAttributes];
                                  const arr = [...(next[idx]?.values || [])];
                                  const existing = arr[vi];
                                  const item = next[idx] || { attributeId: (attr as any).attributeId || '', label: attr.label, values: [] };
                                  if ((item as any).attributeId === 'color') {
                                    const image = typeof existing === 'string' ? undefined : (existing ? (existing as any).image : undefined);
                                    arr[vi] = { value: v, image };
                                  } else {
                                    arr[vi] = v;
                                  }
                                  next[idx] = { ...item, values: arr };
                                  setEditingAttributes(next);
                                }} />
                                {/* If attribute is Color, show small uploader for this value */}
                                {(attr as any).attributeId === 'color' && (
                                  <div className="flex flex-col gap-1">
                                    <label className="inline-flex cursor-pointer items-center gap-1 rounded-xl border border-dashed border-gray-300 px-2 py-1 text-xs text-gray-600 hover:bg-gray-50">
                                      Tải lên
                                      <input type="file" accept="image/*" className="hidden" onChange={(e) => {
                                        const f = e.target.files && e.target.files[0];
                                        if (!f) return;
                                        const fr = new FileReader();
                                        fr.onload = () => {
                                          const data = String(fr.result);
                                          const next = [...editingAttributes];
                                          const arr = [...(next[idx]?.values || [])];
                                          const item = next[idx] || { attributeId: (attr as any).attributeId || '', label: attr.label, values: [] };
                                          const existing = arr[vi] || { value: valueStr, image: undefined };
                                          arr[vi] = { ...(typeof existing === 'string' ? { value: existing, image: data } : { ...existing, image: data }) };
                                          next[idx] = { ...item, values: arr };
                                          setEditingAttributes(next);
                                        };
                                        fr.readAsDataURL(f);
                                      }} />
                                    </label>
                                    {typeof val !== 'string' && val?.image && (
                                      <img src={getImageSrc((val as any).image)} className="h-8 w-8 rounded object-cover mx-auto" />
                                    )}
                                  </div>
                                )}
                                {/* Remove value button - only show if more than 1 value */}
                                {(attr.values || []).length > 1 && (
                                  <button className="rounded border px-1 py-0.5 text-xs text-rose-600 hover:bg-rose-50" onClick={() => {
                                    const next = [...editingAttributes];
                                    const arr = [...(next[idx]?.values || [])];
                                    arr.splice(vi, 1);
                                    next[idx] = { ...(next[idx] || { label: attr.label, values: [] }), values: arr };
                                    setEditingAttributes(next);
                                  }}>×</button>
                                )}
                              </div>
                            );
                          })}
                        </div>
                        
                        {/* Fixed control buttons */}
                        <div className="flex gap-2 pt-2 border-t border-gray-100">
                          <button className="rounded-xl border border-gray-300 px-3 py-2 text-sm hover:bg-gray-50 flex-shrink-0" onClick={() => {
                            const next = [...editingAttributes]; 
                            if (!next[idx]) next[idx] = { label: attr.label || '', attributeId: attr.attributeId || '', values: [''] };
                            next[idx].values = next[idx].values || [];
                            if ((next[idx] as any).attributeId === 'color') next[idx].values.push({ value: '', image: undefined }); 
                            else next[idx].values.push('');
                            setEditingAttributes(next);
                            }}>+ Thêm giá trị</button>
                          <button className="rounded-xl border border-rose-200 px-3 py-2 text-sm text-rose-600 hover:bg-rose-50 flex-shrink-0" onClick={() => {
                            const next = [...editingAttributes]; 
                            next.splice(idx,1); 
                            setEditingAttributes(next);
                            }}>Xóa thuộc tính</button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                <div>
                          <button className="rounded-xl border px-3 py-2 text-sm" onClick={() => {
                    setEditingAttributes([...(editingAttributes || []), { attributeId: '', label: '', values: [''] }]);
                  }}>+ Thêm thuộc tính</button>
                  <button className="ml-2 rounded-xl bg-gray-900 px-3 py-2 text-sm text-white" onClick={() => {
                    // tự động tạo xem trước biến thể
                    const vs = cartesianVariants(editingAttributes);
                    setEditingVariants(vs);
                    setStep(2);
                  }}>Tự tạo biến thể</button>
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="space-y-3">
                <div className="text-sm text-gray-600">Tạo biến thể. Bạn có thể chỉnh SKU, giá và kho cho mỗi biến thể. Thuộc tính hiển thị cho từng biến thể.</div>
                <div className="space-y-2">
                  {(editingVariants.length ? editingVariants : [{ id: uid('V'), sku: `${editing?.slug||editing?.sku||'NEW'}-1`, price: editing?.price||0, stock: editing?.stock||0, attributes: [] }]).map((v, i) => (
                    <div key={v.id} className="grid gap-2 sm:grid-cols-4 items-center border rounded p-2">
                      <div className="sm:col-span-2">
                          <TextField label="SKU" value={v.sku} onChange={(val) => {
                          const nx = [...editingVariants]; nx[i] = { ...nx[i], sku: val }; setEditingVariants(nx);
                        }} />
                        <div className="flex gap-2 mt-2">
                          <TextField label="Giá" type="number" value={v.price} onChange={(val) => { const nx = [...editingVariants]; nx[i] = { ...nx[i], price: Number(val) }; setEditingVariants(nx); }} />
                          <TextField label="Kho" type="number" value={v.stock} onChange={(val) => { const nx = [...editingVariants]; nx[i] = { ...nx[i], stock: Number(val) }; setEditingVariants(nx); }} />
                        </div>
                      </div>
                      <div className="sm:col-span-2">
                        <div className="text-xs text-gray-500">Thuộc tính</div>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {(v.attributes || []).map((a: any, ai: number) => (
                            <div key={ai} className="rounded border px-2 py-1 text-sm">{a.name}: {a.value}</div>
                          ))}
                        </div>
                      </div>
                      <div className="col-span-full text-right">
                        <button className="rounded-xl border px-3 py-1 text-sm text-rose-600" onClick={() => { const nx = [...editingVariants]; nx.splice(i,1); setEditingVariants(nx); }}>Xóa</button>
                      </div>
                    </div>
                  ))}
                </div>
                  <div>
                        <button className="rounded-xl border px-3 py-2 text-sm" onClick={() => {
                    const firstAttr = editingAttributes[0];
                    const firstValue = firstAttr?.values?.[0];
                    const valueStr = typeof firstValue === 'string' ? firstValue : firstValue?.value || '';
                    const nx = [...(editingVariants || [])]; 
                    nx.push({ 
                      id: uid('V'), 
                      sku: `${editing?.slug||editing?.sku||'NEW'}-${nx.length+1}`, 
                      price: editing?.price||0, 
                      stock: editing?.stock||0, 
                      attributes: (firstAttr?.values?.length ? [{ name: firstAttr.label || firstAttr.attributeId || 'attr', value: valueStr }] : []) 
                    }); 
                    setEditingVariants(nx);
                  }}>+ Thêm biến thể</button>
                </div>
              </div>
            )}

            {step === 3 && (
              <div>
                <ImageUploader label="Ảnh (thứ tự tải lên được giữ)." images={editing.images || []} setImages={(imgs) => setEditing({ ...editing, images: imgs })} />
                <div className="text-sm text-gray-500 mt-2">Đánh dấu một ảnh làm chính bằng cách chọn 'Đặt làm ảnh chính' (demo).</div>
                <div className="flex flex-wrap gap-2 mt-2">
                  {(editing.images || []).map((src, i) => (
                    <div key={i} className="relative">
                      <img 
                        src={getImageSrc(src)} 
                        className={`h-24 w-24 rounded-lg object-cover ${i === 0 ? 'border-3 border-black' : 'border border-gray-200'}`} 
                      />
                      {i === 0 && (
                        <div className="absolute -top-2 -right-2 bg-black text-white text-xs px-1.5 py-0.5 rounded-full">
                          Ảnh chính
                        </div>
                      )}
                      <div className="flex gap-1 mt-1">
                        <button className="rounded border px-2 py-1 text-xs" onClick={() => {
                          // move to front
                          const imgs = [...(editing.images || [])]; imgs.splice(i,1); imgs.unshift(src); setEditing({ ...editing, images: imgs });
                        }}>Đặt làm ảnh chính</button>
                        <button className="rounded border px-2 py-1 text-xs text-rose-600" onClick={() => {
                          const imgs = [...(editing.images || [])]; imgs.splice(i,1); setEditing({ ...editing, images: imgs });
                        }}>Xóa</button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {step === 4 && (
              <div className="space-y-3">
                <div className="text-sm text-gray-600">Xem lại và chỉnh sửa trước khi tạo sản phẩm (demo).</div>
                <div className="grid gap-4 sm:grid-cols-3">
                  <div className="sm:col-span-1">
                    <div className="space-y-2">
                      <div className="text-sm font-medium">Ảnh</div>
                      {(editing.images || []).length === 0 && <div className="text-xs text-gray-500">Chưa tải ảnh lên</div>}
                      <div className="flex flex-col gap-2">
                        {(editing.images || []).map((src, i) => (
                            <div key={i} className="flex items-center gap-2">
                              <img src={getImageSrc(src)} className="h-28 w-28 rounded object-cover" />
                              <div className="flex flex-col">
                              <button className="rounded border px-2 py-1 text-xs" onClick={() => { const imgs = [...(editing.images||[])]; imgs.splice(i,1); setEditing({ ...editing, images: imgs }); }}>Xóa</button>
                              <button className="rounded border px-2 py-1 text-xs" onClick={() => { const imgs = [...(editing.images||[])]; imgs.splice(i,1); imgs.unshift(src); setEditing({ ...editing, images: imgs }); }}>Đặt làm ảnh chính</button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="sm:col-span-2 space-y-3">
                    <div className="grid gap-3">
                      <TextField label="Tên" value={editing.name} onChange={(v) => setEditing({ ...editing, name: v })} />
                      <TextField label="Mã model" value={(editing as any).slug || ''} onChange={(v) => setEditing({ ...editing, slug: v })} />
                      <SelectField label="Danh mục" value={editing.category || categoryOptions[0] || "Chung"} onChange={(v) => setEditing({ ...editing, category: v })} options={categoryOptions} />
                      <SelectField
                        label="Thương hiệu"
                        value={(editing as any).brand || (brandOptions[0] || '')}
                        onChange={(v) => {
                          if (v === ADD_BRAND_LABEL) {
                            setShowNewBrandInput(true);
                            setNewBrandName('');
                            setEditing({ ...editing, brand: undefined });
                            return;
                          }
                          setEditing({ ...editing, brand: v });
                        }}
                        options={brandOptions.length ? brandOptions : ["Không có thương hiệu"]}
                      />
                      <TextField label="Mô tả ngắn" value={(editing as any).description || ""} onChange={(v) => setEditing({ ...editing, description: v })} />
                      <div className="grid gap-2 sm:grid-cols-2">
                        <TextField label="Giá mặc định" type="number" value={editing.price} onChange={(v) => setEditing({ ...editing, price: Number(v) })} />
                        <TextField label="Kho mặc định" type="number" value={editing.stock} onChange={(v) => setEditing({ ...editing, stock: Number(v) })} />
                      </div>
                    </div>

                    <div className="pt-2">
                      <div className="text-sm font-medium">Thuộc tính</div>
                      <div className="space-y-2 mt-2">
                        {(editing.attributes || []).map((attr: any, ai: number) => (
                          <div key={ai} className="border rounded p-2">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <div className="text-sm font-medium">{attr.label || <em className="text-xs text-gray-400">Chưa đặt tên</em>}</div>
                                <div className="text-xs text-gray-500">{attr.attributeId}</div>
                              </div>
                              <div className="flex gap-2">
                                <button className="rounded border px-2 py-1 text-xs" onClick={() => { const next = [...(editing.attributes||[])]; next.splice(ai,1); setEditing({ ...editing, attributes: next }); }}>Xóa</button>
                              </div>
                            </div>
                            <div className="mt-2 grid gap-2 sm:grid-cols-2">
                              {(attr.values || []).map((val: any, vi: number) => (
                                <div key={vi} className="flex items-center gap-2">
                                  <TextField label={`Giá trị ${vi+1}`} value={typeof val === 'string' ? val : val?.value || ''} onChange={(v) => {
                                    const next = [...(editing.attributes||[])]; 
                                    const arr = [...(next[ai].values||[])]; 
                                    const existing = arr[vi]; 
                                    if (next[ai].attributeId === 'color') {
                                      const existingImage = typeof existing === 'string' ? undefined : (existing as any)?.image;
                                      arr[vi] = { value: v, image: existingImage };
                                    } else {
                                      arr[vi] = v;
                                    }
                                    next[ai].values = arr; 
                                    setEditing({ ...editing, attributes: next });
                                  }} />
                                  {attr.attributeId === 'color' && (
                                    <div>
                                      <label className="inline-flex cursor-pointer items-center gap-1 rounded-xl border border-dashed border-gray-300 px-2 py-1 text-xs text-gray-600 hover:bg-gray-50">
                                      Tải lên
                                        <input type="file" accept="image/*" className="hidden" onChange={(e) => { const f = e.target.files && e.target.files[0]; if (!f) return; const fr = new FileReader(); fr.onload = () => { const data = String(fr.result); const next = [...(editing.attributes||[])]; const arr = [...(next[ai].values||[])]; const existing = arr[vi]; arr[vi] = { ...(typeof existing === 'string' ? { value: existing, image: data } : { ...existing, image: data }) }; next[ai].values = arr; setEditing({ ...editing, attributes: next }); }; fr.readAsDataURL(f); }} />
                                      </label>
                                      {typeof val !== 'string' && val?.image && (<img src={val.image} className="h-12 w-12 rounded object-cover" />)}
                                    </div>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <div className="text-sm font-medium">Variants</div>
                      <div className="overflow-x-auto mt-2">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="text-left text-gray-500"><th className="px-2 py-1">SKU</th><th className="px-2 py-1">Giá</th><th className="px-2 py-1">Kho</th><th className="px-2 py-1">Thuộc tính</th></tr>
                          </thead>
                          <tbody>
                            {(editing.variants || []).map((v: any, vi: number) => (
                              <tr key={v.id || vi} className="border-t">
                                <td className="px-2 py-1"><TextField label="" value={v.sku} onChange={(s) => { const nx = [...(editing.variants||[])]; nx[vi] = { ...nx[vi], sku: s }; setEditing({ ...editing, variants: nx }); }} /></td>
                                <td className="px-2 py-1"><TextField label="" type="number" value={v.price} onChange={(s) => { const nx = [...(editing.variants||[])]; nx[vi] = { ...nx[vi], price: Number(s) }; setEditing({ ...editing, variants: nx }); }} /></td>
                                <td className="px-2 py-1"><TextField label="" type="number" value={v.stock} onChange={(s) => { const nx = [...(editing.variants||[])]; nx[vi] = { ...nx[vi], stock: Number(s) }; setEditing({ ...editing, variants: nx }); }} /></td>
                                <td className="px-2 py-1 text-xs">{(v.attributes || []).map((a: any) => `${a.name}: ${a.value}`).join(', ')}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </Modal>
    </section>
  );
}