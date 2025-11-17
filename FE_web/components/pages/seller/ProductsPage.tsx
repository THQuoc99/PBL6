import { useState } from "react";
import { Search, Plus, ChevronDown, ChevronUp, Edit, Trash2, Save } from "lucide-react";
import { Product } from "../../../types";
import { Modal, Toggle, TextField, SelectField, ImageUploader, ToolbarButton } from "../../index";

interface ProductsPageProps {
  products: Product[];
  setProducts: (products: Product[]) => void;
}

// Helper function to generate unique ID
const uid = (prefix: string) => `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

export default function ProductsPage({ products, setProducts }: ProductsPageProps) {
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<(Product & { description?: string, createdAt?: string }) | null>(null);
  const [query, setQuery] = useState("");
  const [sortType, setSortType] = useState<"price" | "name" | "date">("date");
  const [sortAsc, setSortAsc] = useState(false);
  const [dateFilter, setDateFilter] = useState<"all" | "today" | "week" | "month">("all");

  // Add createdAt to products if not exists
  const productsWithDate = products.map(p => ({
    ...p,
    createdAt: p.createdAt || new Date().toISOString()
  }));

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
      p.sku.toLowerCase().includes(query.toLowerCase())
    )
    .sort((a, b) => {
      let comparison = 0;
      switch (sortType) {
        case "price":
          comparison = a.price - b.price;
          break;
        case "name":
          comparison = a.name.localeCompare(b.name);
          break;
        case "date":
          comparison = new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime();
          break;
      }
      return sortAsc ? comparison : -comparison;
    });

  const startCreate = () => {
    setEditing({ 
      id: uid("P"), 
      name: "", 
      sku: "", 
      stock: 0, 
      price: 0, 
      images: [], 
      active: true,
      attributes: [{ name: '', values: [''], type: 'Size' }],
      variants: [],
      description: '',
      createdAt: new Date().toISOString(),
    });
    setOpen(true);
  };

  const startEdit = (p: Product) => {
    setEditing({ ...p, attributes: p.attributes || [], variants: p.variants || [] });
    setOpen(true);
  };

  const remove = (id: string) => {
    if (confirm("Delete this product?")) {
      setProducts(products.filter((p) => p.id !== id));
    }
  };

  const save = () => {
    if (!editing) return;
    if (!editing.name || !editing.sku) {
      alert("Name and SKU are required");
      return;
    }

    const exists = products.some((p) => p.id === editing.id);
    const next = exists 
      ? products.map((p) => (p.id === editing.id ? editing : p)) 
      : [editing, ...products];
    setProducts(next);
    setOpen(false);
  };

  // ---- Multi-step product creation (demo-only) ----
  const [step, setStep] = useState(0);

  // The editing object will be enriched for multi-step flow
  const editingAttributes = editing?.attributes || [];
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
    const pools = attrs.map((a: any) => a.values.map((v: any) => ({ name: a.name, value: typeof v === 'string' ? v : v?.value })));
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
      const baseSku = editing?.sku || "NEW";
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
      
      return { 
        id: uid("V"), 
        sku: variantSku, 
        price: editing?.price || 0, 
        stock: editing?.stock || 0, 
        attributes: attrsSet 
      };
    });
  };


  // Format currency
  const fmt = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });

  return (
    <section className="space-y-4">
      <div className="flex flex-col gap-3">
        <div className="flex flex-col items-start justify-between gap-3 sm:flex-row sm:items-center">
          <div className="flex w-full items-center gap-2 sm:w-auto">
            <div className="relative w-full sm:w-80">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search products by name or SKU…"
                className="w-full rounded-xl border border-gray-200 bg-white py-2.5 pl-10 pr-3 text-sm outline-none ring-0 placeholder:text-gray-400 focus:border-gray-300 focus:shadow-sm"
              />
            </div>
          </div>
          <ToolbarButton onClick={startCreate}>
            <Plus className="h-4 w-4" /> Add Product
          </ToolbarButton>
        </div>
        
        {/* Filters and Sort */}
        <div className="flex flex-wrap items-center gap-2 text-sm">
          <span className="text-gray-500 font-medium">Filter by date:</span>
          <select
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value as any)}
            className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm bg-white hover:bg-gray-50"
          >
            <option value="all">All time</option>
            <option value="today">Today</option>
            <option value="week">This week</option>
            <option value="month">This month</option>
          </select>

          <span className="text-gray-500 font-medium ml-4">Sort by:</span>
          <select
            value={sortType}
            onChange={(e) => setSortType(e.target.value as any)}
            className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm bg-white hover:bg-gray-50"
          >
            <option value="date">Date created</option>
            <option value="name">Name</option>
            <option value="price">Price</option>
          </select>

          <ToolbarButton onClick={() => setSortAsc((v) => !v)}>
            {sortAsc ? <ChevronDown className="h-4 w-4" /> : <ChevronUp className="h-4 w-4" />}
            {sortAsc ? "Ascending" : "Descending"}
          </ToolbarButton>

          <div className="text-gray-500 ml-4">
            Showing {filtered.length} of {products.length} products
          </div>
        </div>
      </div>

      <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="text-left text-gray-500">
                <th className="px-3 py-2 font-medium">Product</th>
                <th className="px-3 py-2 font-medium">Category</th>
                <th className="px-3 py-2 font-medium">SKU</th>
                <th className="px-3 py-2 font-medium">Stock</th>
                <th className="px-3 py-2 font-medium">Price</th>
                <th className="px-3 py-2 font-medium">Created</th>
                <th className="px-3 py-2 font-medium">Active</th>
                <th className="px-3 py-2 font-medium">Actions</th>
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
                            src={p.images[0]} 
                            alt={p.name}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full bg-gray-200 flex items-center justify-center text-gray-400 text-xs">
                            No Image
                          </div>
                        )}
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="font-medium text-gray-900 truncate">{p.name}</div>
                        {p.variants && p.variants.length > 0 && (
                          <div className="text-xs text-gray-500">{p.variants.length} variants</div>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-3 py-3">
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gray-100 text-gray-600">
                      {p.category || 'General'}
                    </span>
                  </td>
                  <td className="px-3 py-3 font-mono text-xs">{p.sku}</td>
                  <td className="px-3 py-3">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs ${
                      p.stock > 10 ? 'bg-green-100 text-green-700' :
                      p.stock > 0 ? 'bg-yellow-100 text-yellow-700' :
                      'bg-red-100 text-red-700'
                    }`}>
                      {p.stock} units
                    </span>
                  </td>
                  <td className="px-3 py-3 font-medium">{fmt.format(p.price)}</td>
                  <td className="px-3 py-3 text-xs text-gray-500">
                    {p.createdAt ? new Date(p.createdAt).toLocaleDateString('vi-VN', {
                      day: '2-digit',
                      month: '2-digit',
                      year: 'numeric'
                    }) : 'Unknown'}
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
                        title="Edit product"
                      >
                        <Edit className="h-4 w-4 text-gray-600" />
                      </button>
                      <button 
                        className="rounded-lg border border-gray-200 p-1.5 hover:bg-gray-50 transition-colors" 
                        onClick={() => remove(p.id)}
                        title="Delete product"
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
            <div>{editing?.id ? (products.some((p) => p.id === editing.id) ? "Edit Product" : "Add Product") : "Add Product"}</div>
            {editing && (
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <button 
                  onClick={() => setStep(0)}
                  className={`px-2 py-1 ${step===0?"bg-gray-900 text-white":"bg-gray-100 hover:bg-gray-200"} rounded cursor-pointer transition-colors`}
                >
                  1
                </button>
                <div>Basic</div>
                <button 
                  onClick={() => setStep(1)}
                  className={`px-2 py-1 ${step===1?"bg-gray-900 text-white":"bg-gray-100 hover:bg-gray-200"} rounded ml-4 cursor-pointer transition-colors`}
                >
                  2
                </button>
                <div>Attributes</div>
                <button 
                  onClick={() => setStep(2)}
                  className={`px-2 py-1 ${step===2?"bg-gray-900 text-white":"bg-gray-100 hover:bg-gray-200"} rounded ml-4 cursor-pointer transition-colors`}
                >
                  3
                </button>
                <div>Variants</div>
                <button 
                  onClick={() => setStep(3)}
                  className={`px-2 py-1 ${step===3?"bg-gray-900 text-white":"bg-gray-100 hover:bg-gray-200"} rounded ml-4 cursor-pointer transition-colors`}
                >
                  4
                </button>
                <div>Images</div>
                <button 
                  onClick={() => setStep(4)}
                  className={`px-2 py-1 ${step===4?"bg-gray-900 text-white":"bg-gray-100 hover:bg-gray-200"} rounded ml-4 cursor-pointer transition-colors`}
                >
                  5
                </button>
                <div>Review</div>
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
              Cancel
            </button>
            <div className="flex gap-2">
              {step > 0 && (
                <button
                  onClick={() => setStep((s) => Math.max(0, s - 1))}
                  className="rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm hover:bg-gray-50"
                >
                  Back
                </button>
              )}
              {step < 4 && (
                <button
                  onClick={() => setStep((s) => Math.min(4, s + 1))}
                  className="rounded-xl bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-black"
                >
                  Next
                </button>
              )}
              {step === 4 && (
                <button
                  onClick={() => {
                    // Finalize demo payload into product list
                    if (!editing) return;
                    const payload = {
                      id: editing.id,
                      name: editing.name,
                      sku: editing.sku,
                      category: editing.category,
                      active: editing.active,
                      attributes: editing.attributes || [],
                      variants: editing.variants || [],
                      images: editing.images || [],
                      price: editing.price,
                      stock: editing.stock,
                    };
                    // For demo, map payload to Product shape (simple fallback)
                    const primaryPrice = payload.variants?.[0]?.price ?? payload.price ?? 0;
                    const totalStock = payload.variants?.reduce((a: number, v: any) => a + (v.stock || 0), 0) || payload.stock || 0;
                    const out: Product = {
                      id: payload.id,
                      name: payload.name,
                      sku: payload.sku || `${payload.id}`,
                      category: payload.category,
                      price: primaryPrice,
                      stock: totalStock,
                      images: payload.images,
                      attributes: payload.attributes,
                      variants: payload.variants,
                      active: payload.active,
                      createdAt: editing.createdAt || new Date().toISOString(),
                    };
                    const exists = products.some((p) => p.id === out.id);
                    const next = exists ? products.map((p) => (p.id === out.id ? out : p)) : [out, ...products];
                    setProducts(next);
                    setOpen(false);
                    setStep(0);
                  }}
                  className="inline-flex items-center gap-2 rounded-xl bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700"
                >
                  <Save className="h-4 w-4" /> Create Product (demo)
                </button>
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
                    label="Name" 
                    value={editing.name} 
                    onChange={(v) => setEditing({ ...editing, name: v })}
                    onBlur={() => {
                      // Auto-generate SKU when name field loses focus and SKU is empty
                      if (editing && !editing.sku && editing.name) {
                        const generateSKU = (name: string) => {
                          return name
                            .split(' ')
                            .map(word => word.charAt(0).toUpperCase())
                            .join('-');
                        };
                        const newSKU = generateSKU(editing.name);
                        setEditing({ ...editing, sku: newSKU });
                      }
                    }}
                  />
                </div>
                <TextField label="SKU" value={editing.sku} onChange={(v) => setEditing({ ...editing, sku: v })} />
                <SelectField label="Category" value={editing.category || "General"} onChange={(v) => setEditing({ ...editing, category: v })} options={["General", "Electronics", "Accessories", "Apparel"]} />
                <TextField label="Price (default)" type="number" value={editing.price} onChange={(v) => setEditing({ ...editing, price: Number(v) })} />
                <TextField label="Stock (default)" type="number" value={editing.stock} onChange={(v) => setEditing({ ...editing, stock: Number(v) })} />
                <label className="grid gap-1 text-sm">
                  <span className="text-gray-600">Active</span>
                  <div>
                    <Toggle checked={editing.active !== false} onChange={(v) => setEditing({ ...editing, active: v })} />
                  </div>
                </label>
                <div className="sm:col-span-2">
                  <TextField label="Short description (demo)" value={(editing as any).description || ""} onChange={(v) => setEditing({ ...editing, description: v })} />
                </div>
              </div>
            )}
            {step === 1 && (
              <div className="space-y-3">
                <div className="text-sm text-gray-600">Define product attributes (e.g. Color, Size). Attributes are used to create variants.</div>
                {(editingAttributes.length ? editingAttributes : [{ name: '', values: [''], type: 'Size' }]).map((attr, idx) => (
                  <div key={idx} className="grid gap-2 sm:grid-cols-3 items-start">
                    <div>
                      <TextField label="Attribute name" value={attr.name} onChange={(v) => {
                        const next = [...editingAttributes];
                        const existing = next[idx] || { name: '', values: [''], type: 'Size' };
                        next[idx] = { ...existing, name: v, values: existing.values || [''] };
                        setEditingAttributes(next);
                      }} />
                    </div>
                    <div>
                      <SelectField label="Type" value={(attr as any).type || 'Size'} onChange={(v: string) => {
                        const next = [...editingAttributes];
                        const existing = next[idx] || { name: '', values: [''], type: 'Size' };
                        next[idx] = { ...existing, type: v as "Size" | "Color" | "Custom" };
                        // if switching to Color ensure values are objects
                        if (v === 'Color') {
                          next[idx].values = (next[idx].values || []).map((x: any) => (typeof x === 'string' ? { value: x, image: undefined } : x));
                        } else {
                          next[idx].values = (next[idx].values || []).map((x: any) => (typeof x === 'string' ? x : x.value || ''));
                        }
                        setEditingAttributes(next);
                      }} options={["Size","Color","Custom"]} />
                    </div>
                    <div className="sm:col-span-2">
                      <div className="space-y-3">
                        {/* Values section - scrollable if needed */}
                        <div className="flex flex-wrap gap-2">
                          {(attr.values || []).map((val: any, vi: number) => {
                            const valueStr = typeof val === 'string' ? val : val?.value || '';
                            return (
                              <div key={vi} className="flex flex-col gap-1 min-w-[120px]">
                                <TextField label={`Value ${vi+1}`} value={valueStr} onChange={(v) => {
                                  const next = [...editingAttributes];
                                  const arr = [...(next[idx]?.values || [])];
                                  const existing = arr[vi];
                                  if ((next[idx] as any).type === 'Color') {
                                    const image = typeof existing === 'string' ? undefined : (existing ? (existing as any).image : undefined);
                                    arr[vi] = { value: v, image };
                                  } else {
                                    arr[vi] = v;
                                  }
                                  next[idx] = { ...(next[idx] || { name: attr.name, values: [] }), values: arr };
                                  setEditingAttributes(next);
                                }} />
                                {/* If attribute is Color, show small uploader for this value */}
                                {(attr as any).type === 'Color' && (
                                  <div className="flex flex-col gap-1">
                                    <label className="inline-flex cursor-pointer items-center gap-1 rounded-xl border border-dashed border-gray-300 px-2 py-1 text-xs text-gray-600 hover:bg-gray-50">
                                      Upload
                                      <input type="file" accept="image/*" className="hidden" onChange={(e) => {
                                        const f = e.target.files && e.target.files[0];
                                        if (!f) return;
                                        const fr = new FileReader();
                                        fr.onload = () => {
                                          const data = String(fr.result);
                                          const next = [...editingAttributes];
                                          const arr = [...(next[idx]?.values || [])];
                                          const existing = arr[vi] || { value: valueStr, image: undefined };
                                          arr[vi] = { ...(typeof existing === 'string' ? { value: existing, image: data } : { ...existing, image: data }) };
                                          next[idx] = { ...(next[idx] || { name: attr.name, values: [] }), values: arr };
                                          setEditingAttributes(next);
                                        };
                                        fr.readAsDataURL(f);
                                      }} />
                                    </label>
                                    {typeof val !== 'string' && val?.image && (
                                      <img src={val.image} className="h-8 w-8 rounded object-cover mx-auto" />
                                    )}
                                  </div>
                                )}
                                {/* Remove value button - only show if more than 1 value */}
                                {(attr.values || []).length > 1 && (
                                  <button className="rounded border px-1 py-0.5 text-xs text-rose-600 hover:bg-rose-50" onClick={() => {
                                    const next = [...editingAttributes];
                                    const arr = [...(next[idx]?.values || [])];
                                    arr.splice(vi, 1);
                                    next[idx] = { ...(next[idx] || { name: attr.name, values: [] }), values: arr };
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
                            if (!next[idx]) next[idx] = { name: attr.name || '', values: [''], type: (attr as any).type || 'Size' };
                            next[idx].values = next[idx].values || [];
                            if ((next[idx] as any).type === 'Color') next[idx].values.push({ value: '', image: undefined }); 
                            else next[idx].values.push('');
                            setEditingAttributes(next);
                          }}>+ Add value</button>
                          <button className="rounded-xl border border-rose-200 px-3 py-2 text-sm text-rose-600 hover:bg-rose-50 flex-shrink-0" onClick={() => {
                            const next = [...editingAttributes]; 
                            next.splice(idx,1); 
                            setEditingAttributes(next);
                          }}>Remove attribute</button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                <div>
                  <button className="rounded-xl border px-3 py-2 text-sm" onClick={() => {
                    setEditingAttributes([...(editingAttributes || []), { name: '', values: [''], type: 'Size' }]);
                  }}>+ Add attribute</button>
                  <button className="ml-2 rounded-xl bg-gray-900 px-3 py-2 text-sm text-white" onClick={() => {
                    // auto-generate small preview of variants
                    const vs = cartesianVariants(editingAttributes);
                    setEditingVariants(vs);
                    setStep(2);
                  }}>Auto-generate variants</button>
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="space-y-3">
                <div className="text-sm text-gray-600">Create variants. You can edit SKU, price, and stock for each variant. Attributes shown per variant.</div>
                <div className="space-y-2">
                  {(editingVariants.length ? editingVariants : [{ id: uid('V'), sku: `${editing?.sku||'NEW'}-1`, price: editing?.price||0, stock: editing?.stock||0, attributes: [] }]).map((v, i) => (
                    <div key={v.id} className="grid gap-2 sm:grid-cols-4 items-center border rounded p-2">
                      <div className="sm:col-span-2">
                        <TextField label="SKU" value={v.sku} onChange={(val) => {
                          const nx = [...editingVariants]; nx[i] = { ...nx[i], sku: val }; setEditingVariants(nx);
                        }} />
                        <div className="flex gap-2 mt-2">
                          <TextField label="Price" type="number" value={v.price} onChange={(val) => { const nx = [...editingVariants]; nx[i] = { ...nx[i], price: Number(val) }; setEditingVariants(nx); }} />
                          <TextField label="Stock" type="number" value={v.stock} onChange={(val) => { const nx = [...editingVariants]; nx[i] = { ...nx[i], stock: Number(val) }; setEditingVariants(nx); }} />
                        </div>
                      </div>
                      <div className="sm:col-span-2">
                        <div className="text-xs text-gray-500">Attributes</div>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {(v.attributes || []).map((a: any, ai: number) => (
                            <div key={ai} className="rounded border px-2 py-1 text-sm">{a.name}: {a.value}</div>
                          ))}
                        </div>
                      </div>
                      <div className="col-span-full text-right">
                        <button className="rounded-xl border px-3 py-1 text-sm text-rose-600" onClick={() => { const nx = [...editingVariants]; nx.splice(i,1); setEditingVariants(nx); }}>Remove</button>
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
                      sku: `${editing?.sku||'NEW'}-${nx.length+1}`, 
                      price: editing?.price||0, 
                      stock: editing?.stock||0, 
                      attributes: (firstAttr?.values?.length ? [{ name: firstAttr.name, value: valueStr }] : []) 
                    }); 
                    setEditingVariants(nx);
                  }}>+ Add variant</button>
                </div>
              </div>
            )}

            {step === 3 && (
              <div>
                <ImageUploader label="Images (upload order will be kept)." images={editing.images || []} setImages={(imgs) => setEditing({ ...editing, images: imgs })} />
                <div className="text-sm text-gray-500 mt-2">Mark one image as primary by clicking 'Make primary' (demo only).</div>
                <div className="flex flex-wrap gap-2 mt-2">
                  {(editing.images || []).map((src, i) => (
                    <div key={i} className="relative">
                      <img 
                        src={src} 
                        className={`h-24 w-24 rounded-lg object-cover ${i === 0 ? 'border-3 border-black' : 'border border-gray-200'}`} 
                      />
                      {i === 0 && (
                        <div className="absolute -top-2 -right-2 bg-black text-white text-xs px-1.5 py-0.5 rounded-full">
                          Primary
                        </div>
                      )}
                      <div className="flex gap-1 mt-1">
                        <button className="rounded border px-2 py-1 text-xs" onClick={() => {
                          // move to front
                          const imgs = [...(editing.images || [])]; imgs.splice(i,1); imgs.unshift(src); setEditing({ ...editing, images: imgs });
                        }}>Make primary</button>
                        <button className="rounded border px-2 py-1 text-xs text-rose-600" onClick={() => {
                          const imgs = [...(editing.images || [])]; imgs.splice(i,1); setEditing({ ...editing, images: imgs });
                        }}>Remove</button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {step === 4 && (
              <div className="space-y-3">
                <div className="text-sm text-gray-600">Review and edit the full product preview before creating (demo-only).</div>
                <div className="grid gap-4 sm:grid-cols-3">
                  <div className="sm:col-span-1">
                    <div className="space-y-2">
                      <div className="text-sm font-medium">Images</div>
                      {(editing.images || []).length === 0 && <div className="text-xs text-gray-500">No images uploaded</div>}
                      <div className="flex flex-col gap-2">
                        {(editing.images || []).map((src, i) => (
                          <div key={i} className="flex items-center gap-2">
                            <img src={src} className="h-28 w-28 rounded object-cover" />
                            <div className="flex flex-col">
                              <button className="rounded border px-2 py-1 text-xs" onClick={() => { const imgs = [...(editing.images||[])]; imgs.splice(i,1); setEditing({ ...editing, images: imgs }); }}>Remove</button>
                              <button className="rounded border px-2 py-1 text-xs" onClick={() => { const imgs = [...(editing.images||[])]; imgs.splice(i,1); imgs.unshift(src); setEditing({ ...editing, images: imgs }); }}>Make primary</button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="sm:col-span-2 space-y-3">
                    <div className="grid gap-3">
                      <TextField label="Name" value={editing.name} onChange={(v) => setEditing({ ...editing, name: v })} />
                      <TextField label="SKU" value={editing.sku} onChange={(v) => setEditing({ ...editing, sku: v })} />
                      <SelectField label="Category" value={editing.category || "General"} onChange={(v) => setEditing({ ...editing, category: v })} options={["General","Electronics","Accessories","Apparel"]} />
                      <TextField label="Short description" value={(editing as any).description || ""} onChange={(v) => setEditing({ ...editing, description: v })} />
                      <div className="grid gap-2 sm:grid-cols-2">
                        <TextField label="Default price" type="number" value={editing.price} onChange={(v) => setEditing({ ...editing, price: Number(v) })} />
                        <TextField label="Default stock" type="number" value={editing.stock} onChange={(v) => setEditing({ ...editing, stock: Number(v) })} />
                      </div>
                    </div>

                    <div className="pt-2">
                      <div className="text-sm font-medium">Attributes</div>
                      <div className="space-y-2 mt-2">
                        {(editing.attributes || []).map((attr: any, ai: number) => (
                          <div key={ai} className="border rounded p-2">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <div className="text-sm font-medium">{attr.name || <em className="text-xs text-gray-400">Unnamed</em>}</div>
                                <div className="text-xs text-gray-500">{attr.type}</div>
                              </div>
                              <div className="flex gap-2">
                                <button className="rounded border px-2 py-1 text-xs" onClick={() => { const next = [...(editing.attributes||[])]; next.splice(ai,1); setEditing({ ...editing, attributes: next }); }}>Remove</button>
                              </div>
                            </div>
                            <div className="mt-2 grid gap-2 sm:grid-cols-2">
                              {(attr.values || []).map((val: any, vi: number) => (
                                <div key={vi} className="flex items-center gap-2">
                                  <TextField label={`Value ${vi+1}`} value={typeof val === 'string' ? val : val?.value || ''} onChange={(v) => {
                                    const next = [...(editing.attributes||[])]; 
                                    const arr = [...(next[ai].values||[])]; 
                                    const existing = arr[vi]; 
                                    if (next[ai].type === 'Color') {
                                      const existingImage = typeof existing === 'string' ? undefined : (existing as any)?.image;
                                      arr[vi] = { value: v, image: existingImage };
                                    } else {
                                      arr[vi] = v;
                                    }
                                    next[ai].values = arr; 
                                    setEditing({ ...editing, attributes: next });
                                  }} />
                                  {attr.type === 'Color' && (
                                    <div>
                                      <label className="inline-flex cursor-pointer items-center gap-2 rounded-xl border border-dashed border-gray-300 px-2 py-1 text-xs text-gray-600 hover:bg-gray-50">
                                        Upload
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
                            <tr className="text-left text-gray-500"><th className="px-2 py-1">SKU</th><th className="px-2 py-1">Price</th><th className="px-2 py-1">Stock</th><th className="px-2 py-1">Attributes</th></tr>
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