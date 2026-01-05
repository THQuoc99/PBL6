import React, { useState, useEffect } from "react";
import { Save, Plus, MapPin, Check, Edit, Trash2 } from "lucide-react";
import { StoreSettings } from "../../../types";
import { TextField, SelectField, Toggle, ToolbarButton } from "../../index";
import { useStoreAuth } from '../../../hooks/store/storeAuth';
import { storeService } from '../../../services/store/store';
import useAddressStore from '../../../hooks/store/useAddressStore';
import { getProvinces, getWards, getHamlets } from '../../../services/callAPI/apiAddress';

// Normalize names for robust matching: remove diacritics, common prefixes and punctuation
function normalizeStr(input: any) {
  if (!input && input !== 0) return '';
  try {
    let s = String(input || '');
    // NFD + remove diacritics
    s = s.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    s = s.toLowerCase().trim();
    // remove common vietnamese administrative prefixes
    s = s.replace(/^(phuong|xa|thi tran|thi-tran|thon|khu|ap|am|tinh|huyen|quan)\s+/i, '');
    // remove punctuation
    s = s.replace(/[^a-z0-9\s]/g, '');
    s = s.replace(/\s+/g, ' ').trim();
    return s;
  } catch (e) {
    return String(input || '').toLowerCase();
  }
}

// Ensure media URL is absolute so CSS `url(...)` displays images.
function ensureAbsoluteMedia(url: any) {
  if (!url && url !== 0) return null;
  try {
    const s = String(url || '').trim();
    if (!s) return null;
    // keep data URLs and absolute HTTP(S)
    if (/^(https?:\/\/|data:)/i.test(s)) return s;
    const base = 'http://127.0.0.1:8000';
    if (s.startsWith('/media/')) return base + s;
    if (s.startsWith('media/')) return base + '/' + s;
    // e.g. 'store/covers/..' -> /media/store/...
    return base + '/media/' + s;
  } catch (e) {
    return String(url || null);
  }
}

interface SettingsPageProps {
  settings: StoreSettings;
  setSettings: (settings: StoreSettings) => void;
}

// AddressForm component copied from AccountPage to reuse the customer's address form
interface AddressFormProps {
  editingAddress: any | null;
  newAddress: any;
  setNewAddress: (v: any) => void;
  provinces: any[];
  wards: any[];
  hamlets: any[];
  loadingWards: boolean;
  loadingHamlets: boolean;
  setWards: (v: any[]) => void;
  setHamlets: (v: any[]) => void;
  addressLoading: boolean;
  handleUpdateAddress: () => void;
  handleAddAddress: () => void;
  handleCancelForm: () => void;
}

const AddressFormComponent = React.memo(function AddressFormComponent({
  editingAddress,
  newAddress,
  setNewAddress,
  provinces,
  wards,
  hamlets,
  loadingWards,
  loadingHamlets,
  setWards,
  setHamlets,
  addressLoading,
  handleUpdateAddress,
  handleAddAddress,
  handleCancelForm
}: AddressFormProps) {
  return (
    <div className="border border-gray-300 rounded-lg p-6 bg-gray-50">
      <h3 className="font-semibold mb-4">
        {editingAddress ? 'Chỉnh sửa địa chỉ' : 'Thêm địa chỉ mới'}
      </h3>
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Name removed as requested */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Số điện thoại *</label>
            <input
              type="tel"
              value={newAddress.phoneNumber}
              onChange={(e) => setNewAddress((prev: any) => ({ ...prev, phoneNumber: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Nhập số điện thoại"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tỉnh/Thành phố *</label>
            {provinces.length > 0 ? (
              <select
                value={newAddress.provinceId}
                onChange={(e) => {
                  const selected = provinces.find((p: any) => String(p.code) === String(e.target.value));
                  const newState = { ...newAddress, provinceId: e.target.value, province: selected?.name || '', wardId: '', ward: '', hamlet: '' };
                  setNewAddress(newState);
                  setWards([]);
                  setHamlets([]);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="">Chọn Tỉnh/Thành phố</option>
                {provinces.map((p: any) => <option key={p.code} value={p.code}>{p.name}</option>)}
              </select>
            ) : (
              <input type="text" value={newAddress.province} onChange={(e) => setNewAddress((prev: any) => ({ ...prev, province: e.target.value, provinceId: '' }))} className="w-full px-3 py-2 border border-gray-300 rounded-lg" />
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Phường/Xã *</label>
            {loadingWards ? (
              <div className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500 flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                Đang tải danh sách phường/xã...
              </div>
            ) : wards.length > 0 && newAddress.provinceId ? (
              <select value={newAddress.wardId} onChange={(e) => {
                const selected = wards.find((w: any) => String(w.code) === String(e.target.value));
                const newState = { ...newAddress, wardId: e.target.value, ward: selected?.name || '', hamlet: '' };
                setNewAddress(newState);
                setHamlets([]);
              }} className="w-full px-3 py-2 border border-gray-300 rounded-lg">
                <option value="">Chọn Phường/Xã</option>
                {wards.map((w: any) => <option key={w.code} value={w.code}>{w.name}</option>)}
              </select>
            ) : (
              <input type="text" value={newAddress.ward} onChange={(e) => setNewAddress((prev: any) => ({ ...prev, ward: e.target.value, wardId: '' }))} className="w-full px-3 py-2 border rounded-lg" />
            )}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Thôn/Khu/Ấp (tùy chọn)</label>
          {loadingHamlets ? (
            <div className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500 flex items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
              Đang tải danh sách thôn/khu/ấp...
            </div>
          ) : hamlets.length > 0 && (newAddress.ward || newAddress.wardId) ? (
            <select value={newAddress.hamletId} onChange={(e) => {
              const idx = e.target.value;
              const selected = hamlets[parseInt(idx)];
              const hamletName = selected?.name || selected || '';
              setNewAddress((prev: any) => ({ ...prev, hamletId: idx, hamlet: hamletName }));
            }} className="w-full px-3 py-2 border border-gray-300 rounded-lg">
              <option value="">Chọn Thôn/Khu/Ấp</option>
              {hamlets.map((h: any, i: number) => <option key={`h-${i}`} value={String(i)}>{h.name || h}</option>)}
            </select>
          ) : (
            <input type="text" value={newAddress.hamlet} onChange={(e) => setNewAddress((prev: any) => ({ ...prev, hamlet: e.target.value }))} className="w-full px-3 py-2 border rounded-lg" />
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Địa chỉ chi tiết *</label>
          <textarea value={newAddress.detail} onChange={(e) => setNewAddress((prev: any) => ({ ...prev, detail: e.target.value }))} rows={2} className="w-full px-3 py-2 border border-gray-300 rounded-lg" />
        </div>

        <div className="flex gap-3">
          <button onClick={editingAddress ? handleUpdateAddress : handleAddAddress} disabled={addressLoading} className="bg-blue-600 text-white px-6 py-2 rounded-lg">
            {addressLoading ? 'Đang xử lý...' : (editingAddress ? 'Cập nhật' : 'Thêm địa chỉ')}
          </button>
          <button onClick={handleCancelForm} className="border border-gray-300 px-6 py-2 rounded-lg">Hủy</button>
        </div>
      </div>
    </div>
  );
}) as React.FC<AddressFormProps>;

export default function SettingsPage({ settings, setSettings }: SettingsPageProps) {
  const [localSettings, setLocalSettings] = useState<StoreSettings>(settings);
  const { store } = useStoreAuth()
  const [addresses, setAddresses] = useState<any[]>([]);
  const [loadingAddresses, setLoadingAddresses] = useState(false);
  const [editingAddress, setEditingAddress] = useState<any | null>(null);
  const [provinces, setProvinces] = useState<any[]>([]);
  const [wards, setWards] = useState<any[]>([]);
  const [hamlets, setHamlets] = useState<any[]>([]);
  const [showAddressForm, setShowAddressForm] = useState(false);
  const [formPosition, setFormPosition] = useState<'top' | 'bottom' | null>('top');
  const [newAddress, setNewAddress] = useState<any>({ name: '', phoneNumber: '', province: '', provinceId: '', ward: '', wardId: '', hamlet: '', hamletId: '', detail: '' });
  const [loadingWards, setLoadingWards] = useState(false);
  const [loadingHamlets, setLoadingHamlets] = useState(false);
  const [addressLoading, setAddressLoading] = useState(false);

  // When `store` from auth changes, populate local settings and addresses
  useEffect(() => {
    if (!store) return;
    try {
      // Populate basic store-level fields into localSettings (preserve existing fields)
      setLocalSettings((prev: any) => ({
        ...prev,
        storeName: store.name ?? prev.storeName,
        email: store.email ?? prev.email,
        avatar: ensureAbsoluteMedia(store.avatar) || prev.avatar,
        coverImage: ensureAbsoluteMedia(store.coverImage) || prev.coverImage,
        currency: store.currency ?? prev.currency,
        address: prev.address || ''
      }));
      // state updates are async; show server value normalized and previous local value
      // // If the store object already contains addresses, use them
      // if (Array.isArray(store.addresses) && store.addresses.length > 0) {
      //   setAddresses(store.addresses);
      // }
    } catch (e) {
      console.error('Error populating settings from store:', e);
    }
  }, [store]);

  // Format various error/message payloads into a readable string
  const fmtMsg = (m: any) => {
    if (!m && m !== 0) return '';
    if (typeof m === 'string') return m;
    if (typeof m === 'number' || typeof m === 'boolean') return String(m);
    try {
      if (Array.isArray(m)) {
        // try to extract common GraphQL error shapes
        const parts = m.map((it: any) => (it?.message ? it.message : (typeof it === 'string' ? it : JSON.stringify(it))));
        return parts.join('; ');
      }
      if (m?.message) return typeof m.message === 'string' ? m.message : JSON.stringify(m.message);
      return JSON.stringify(m);
    } catch (e) {
      return String(m);
    }
  };

  // Load wards when newAddress.provinceId changes
  useEffect(() => {
    const loadWards = async () => {
      if (newAddress.provinceId) {
        setLoadingWards(true);
        try {
          const provinceIdNum = parseInt(newAddress.provinceId, 10);
          const data = await getWards(provinceIdNum);
          setWards(data || []);
        } catch (err) { setWards([]); }
        finally { setLoadingWards(false); }
      } else {
        setWards([]);
      }
      setHamlets([]);
    };
    loadWards();
  }, [newAddress.provinceId]);

  // When provinces load (or change) and an editingAddress exists, try to map province name -> provinceId
  useEffect(() => {
    if (!editingAddress || !editingAddress.province) return;
    if (!provinces || provinces.length === 0) return;
    const target = normalizeStr(editingAddress.province);
    const match = provinces.find((p: any) => {
      const name = normalizeStr(p.name || p.province_name || p.province || p.label || '');
      const code = String(p.code ?? p.province_code ?? p.id ?? '');
      return name === target || name.includes(target) || target.includes(name) || String(code) === String(editingAddress.provinceId || editingAddress.province);
    });
    if (match) {
      const code = String(match.code ?? match.province_code ?? match.id ?? '');
      if (code && newAddress.provinceId !== code) {
        setNewAddress((prev: any) => ({ ...prev, provinceId: code }));
      }
    }
  }, [provinces, editingAddress]);

  // When wards load and editingAddress exists, map ward name -> wardId and load hamlets & select hamlet
  useEffect(() => {
    if (!editingAddress || !editingAddress.ward) return;
    if (!wards || wards.length === 0) return;
    const targetWard = normalizeStr(editingAddress.ward);
    const match = wards.find((w: any) => {
      const name = normalizeStr(w.name || w.ward_name || w.label || '');
      const code = String(w.code ?? w.ward_code ?? w.id ?? '');
      return name === targetWard || name.includes(targetWard) || targetWard.includes(name) || code === String(editingAddress.wardId || editingAddress.ward);
    });
    if (match) {
      const wardCode = String(match.code ?? match.ward_code ?? match.id ?? '');
      if (wardCode && newAddress.wardId !== wardCode) {
        setNewAddress((prev: any) => ({ ...prev, wardId: wardCode, ward: match.name || match.ward_name || prev.ward }));
      }

      // attempt to load hamlets from match if present (match.hamlets may be array of strings)
      const localHamlets = match.hamlets || match.hamlet || [];
      const targetHamletRaw = editingAddress.hamlet || '';
      const targetHamlet = normalizeStr(targetHamletRaw);
      if (Array.isArray(localHamlets) && localHamlets.length > 0) {
        // normalize and find exact/substring match
        setHamlets(localHamlets as any[]);
        const foundIndex = localHamlets.findIndex((h: any) => normalizeStr(h) === targetHamlet || normalizeStr(h).includes(targetHamlet) || targetHamlet.includes(normalizeStr(h)));
        if (foundIndex >= 0) {
          const hamletValue = typeof localHamlets[foundIndex] === 'string' ? localHamlets[foundIndex] : (localHamlets[foundIndex].name || String(localHamlets[foundIndex]));
          setNewAddress((prev: any) => ({ ...prev, hamletId: String(foundIndex), hamlet: hamletValue }));
        }
      } else {
        // otherwise, try to fetch hamlets via API and then select
        (async () => {
          try {
            const hs = await getHamlets(newAddress.province || editingAddress.province, match.name || match.ward_name || editingAddress.ward);
            setHamlets(hs || []);
            const foundIndex = (hs || []).findIndex((h: any) => normalizeStr(h) === targetHamlet || normalizeStr(h).includes(targetHamlet) || targetHamlet.includes(normalizeStr(h)));
            if (foundIndex >= 0) {
              const hamletValue = typeof hs[foundIndex] === 'string' ? hs[foundIndex] : (hs[foundIndex].name || String(hs[foundIndex]));
              setNewAddress((prev: any) => ({ ...prev, hamletId: String(foundIndex), hamlet: hamletValue }));
            }
          } catch (e) { }
        })();
      }
    }
  }, [wards, editingAddress]);

  // Load hamlets when ward changes
  useEffect(() => {
    const loadHamlets = async () => {
      setNewAddress((prev: any) => ({ ...prev, hamlet: '' }));
      if (newAddress.province && newAddress.ward) {
        setLoadingHamlets(true);
        try {
          const hs = await getHamlets(newAddress.province, newAddress.ward);
          setHamlets(hs || []);
        } catch (err) { setHamlets([]); }
        finally { setLoadingHamlets(false); }
      } else {
        setHamlets([]);
      }
    };
    loadHamlets();
  }, [newAddress.ward]);

  const { addAddress, updateAddress, setDefaultAddress, deleteAddress } = useAddressStore();

  const refreshAddresses = async () => {
    if (!store?.storeId) return;
    setLoadingAddresses(true);
    try {
      const res = await storeService.getAddressStores(store.storeId);
      setAddresses(Array.isArray(res) ? res : []);
    } catch (e) { setAddresses([]); }
    setLoadingAddresses(false);
  };

  const handleAddAddress = async () => {
    if (!store?.storeId) return alert('Store missing');
    setAddressLoading(true);
    const provinceName = newAddress.province || (provinces.find((p:any) => String(p.code) === String(newAddress.provinceId))?.name || '');
    const wardName = newAddress.ward || (wards.find((w:any) => String(w.code) === String(newAddress.wardId))?.name || '');
    const payload = {
      phone: newAddress.phoneNumber,
      province: provinceName,
      ward: wardName,
      hamlet: newAddress.hamlet,
      detail: newAddress.detail,
      isDefault: !!newAddress.isDefault
    };
    try {
      const resp = await addAddress(store.storeId, payload);
      console.debug('addAddress response:', resp);
      if (resp && resp.success) {
        alert(fmtMsg(resp?.message) || 'Đã thêm địa chỉ thành công');
        await refreshAddresses();
        setShowAddressForm(false);
        setNewAddress({ name: '', phoneNumber: '', province: '', provinceId: '', ward: '', wardId: '', hamlet: '', hamletId: '', detail: '' });
      } else {
        alert(fmtMsg(resp?.message) || fmtMsg(resp) || 'Đã thêm địa chỉ thất bại');
      }
    } catch (e: any) { alert(e?.message || 'Lỗi khi thêm địa chỉ'); }
    setAddressLoading(false);
  };

  const handleUpdateAddress = async () => {
    if (!store?.storeId || !editingAddress?.addressId) return alert('Missing data');
    setAddressLoading(true);
    const provinceName = newAddress.province || (provinces.find((p:any) => String(p.code) === String(newAddress.provinceId))?.name || '');
    const wardName = newAddress.ward || (wards.find((w:any) => String(w.code) === String(newAddress.wardId))?.name || '');
    const payload = {
      phone: newAddress.phoneNumber,
      province: provinceName,
      ward: wardName,
      hamlet: newAddress.hamlet,
      detail: newAddress.detail,
      isDefault: !!newAddress.isDefault
    };
    try {
      const addrId = String(editingAddress.addressId || editingAddress.address_id || editingAddress.id);
      const resp = await updateAddress(store.storeId, { ...payload, addressId: addrId });
      console.debug('updateAddress response:', resp);
      if (resp && resp.success) {
        alert(fmtMsg(resp?.message) || 'Cập nhật địa chỉ thành công');
        await refreshAddresses();
        setShowAddressForm(false);
        setEditingAddress(null);
        setNewAddress({ name: '', phoneNumber: '', province: '', provinceId: '', ward: '', wardId: '', hamlet: '', hamletId: '', detail: '' });
      } else {
        alert(fmtMsg(resp?.message) || fmtMsg(resp) || 'Cập nhật địa chỉ thất bại');
      }
    } catch (e: any) { alert(fmtMsg(e?.message) || fmtMsg(e) || 'Lỗi khi cập nhật địa chỉ'); }
    setAddressLoading(false);
  };

  const handleCancelForm = () => {
    setShowAddressForm(false);
    setEditingAddress(null);
    setNewAddress({ name: '', phoneNumber: '', province: '', provinceId: '', ward: '', wardId: '', hamlet: '', hamletId: '', detail: '' });
  };

  const handleSetDefaultAddress = async (addressId: string) => {
    try {
      const resp = await setDefaultAddress(addressId);
      console.debug('handleSetDefaultAddress response:', resp);
      alert(fmtMsg(resp?.message) || fmtMsg(resp) || 'Đã đặt mặc định');
      await refreshAddresses();
    } catch (e) { alert(fmtMsg(e) || 'Lỗi'); }
  };

  const handleEditAddress = (address: any) => {
    setEditingAddress(address);
    // Pre-fill textual fields
    const pref = {
      name: address.name || '',
      phoneNumber: address.phone || address.phoneNumber || '',
      province: address.province || '',
      provinceId: address.provinceId || '',
      ward: address.ward || '',
      wardId: address.wardId || '',
      hamlet: address.hamlet || '',
      hamletId: address.hamletId || '',
      detail: address.detail || ''
    } as any;

    // Try to resolve provinceId by matching province name in loaded provinces
    if (pref.province && provinces && provinces.length > 0) {
      const match = provinces.find((p: any) => {
        const name = (p.name || '').toString().toLowerCase().trim();
        return name === pref.province.toString().toLowerCase().trim() || name.includes(pref.province.toString().toLowerCase().trim());
      });
      if (match) pref.provinceId = String(match.code ?? match.province_code ?? match.id ?? '');
    }

    setNewAddress(pref);
    setFormPosition('bottom');
    setShowAddressForm(true);
  };

  const handleDeleteAddress = async (addressId: string) => {
    if (!confirm('Bạn có chắc chắn muốn xóa địa chỉ này?')) return;
    try {
      const resp = await deleteAddress(addressId);
      alert(fmtMsg(resp?.message) || fmtMsg(resp) || 'Đã xóa');
      await refreshAddresses();
    } catch (e) { alert(fmtMsg(e) || 'Lỗi khi xóa'); }
  };

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      if (!store?.storeId) return;
      setLoadingAddresses(true);
      try {
        const res = await storeService.getAddressStores(store.storeId);
        if (!mounted) return;
        setAddresses(Array.isArray(res) ? res : []);
      } catch (e) {
        if (!mounted) return;
        setAddresses([]);
      } finally {
        if (mounted) setLoadingAddresses(false);
      }
    };
    load();
    return () => { mounted = false; };
  }, [store?.storeId]);

  useEffect(() => {
    (async () => {
      try {
        const ps = await getProvinces();
        setProvinces(ps || []);
      } catch (e) {
        setProvinces([]);
      }
    })();
  }, []);

  const handleSave = () => {
    setSettings(localSettings);
    alert("Settings saved successfully!");
  };

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Store Settings</h1>
        <ToolbarButton onClick={handleSave}>
          <Save className="h-4 w-4" /> Save Settings
        </ToolbarButton>
      </div>

      {/* Store Visual Identity */}
      <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">  
        {/* Cover Image */}
        <div className="mb-6">
          <div className="relative">
            <div 
              className="w-full h-80 bg-gray-100 rounded-lg overflow-hidden border-2 border-dashed border-gray-300 hover:border-gray-400 transition-colors"
              style={{
                backgroundImage: localSettings.coverImage 
                  ? `url(${localSettings.coverImage})` 
                  : 'url(https://aobongda.net/pic/Images/Module/News/images/giay-dep-nhat-10.jpg)',
                backgroundSize: 'cover',
                backgroundPosition: 'center'
              }}
            >
              <div className="absolute inset-0 bg-black bg-opacity-30 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                <label className="cursor-pointer bg-white px-4 py-2 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50">
                  Change Cover
                  <input
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) {
                        const reader = new FileReader();
                        reader.onload = () => {
                          setLocalSettings({ ...localSettings, coverImage: reader.result as string });
                        };
                        reader.readAsDataURL(file);
                      }
                    }}
                  />
                </label>
              </div>
            </div>
          </div>
        </div>

        {/* Avatar */}
        <div className="mb-6">
          <div className="flex items-center gap-4">
            <div className="relative">
              <div 
                className="w-32 h-32 bg-gray-100 rounded-full overflow-hidden border-4 border-white shadow-md"
                style={{
                  backgroundImage: localSettings.avatar 
                    ? `url(${store?.avatar || localSettings.avatar})` 
                    : 'url(https://nganhquangcao.vn/upload/filemanager/files/adidas-logo-lich-su-y-nghia-bieu-tuong-adidas-5.jpg)',
                  backgroundSize: 'cover',
                  backgroundPosition: 'center'
                }}
              >
                <div className="absolute inset-0 bg-black bg-opacity-30 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity rounded-full">
                  <label className="cursor-pointer text-white text-xs font-medium">
                    Change
                    <input
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) {
                          const reader = new FileReader();
                          reader.onload = () => {
                            setLocalSettings({ ...localSettings, avatar: reader.result as string });
                          };
                          reader.readAsDataURL(file);
                        }
                      }}
                    />
                  </label>
                </div>
              </div>
            </div>
            <div>  <div className="text-xl font-bold">{localSettings.storeName}</div>
            
            </div>
          </div>
        </div>
      </div>

      <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4">Store Information</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <TextField
            label="Store Name"
            value={localSettings.storeName}
            onChange={(v) => setLocalSettings({ ...localSettings, storeName: v })}
          />
          <TextField
            label="Email"
            type="email"
            value={localSettings.email}
            onChange={(v) => setLocalSettings({ ...localSettings, email: v })}
          />
        </div>
      </div>

      <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4">Store Addresses</h2>
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold">Địa chỉ giao hàng</h3>
          <button
            onClick={() => {
              setEditingAddress(null);
              setNewAddress({ name: '', phoneNumber: '', province: '', provinceId: '', ward: '', wardId: '', hamlet: '', hamletId: '', detail: '' });
              setShowAddressForm(true);
              setFormPosition('top');
            }}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Thêm địa chỉ mới
          </button>
        </div>

        {/* Add Form at Top */}
        {showAddressForm && formPosition === 'top' && (
          <AddressFormComponent
            editingAddress={editingAddress}
            newAddress={newAddress}
            setNewAddress={setNewAddress}
            provinces={provinces}
            wards={wards}
            hamlets={hamlets}
            loadingWards={loadingWards}
            loadingHamlets={loadingHamlets}
            setWards={setWards}
            setHamlets={setHamlets}
            addressLoading={addressLoading}
            handleUpdateAddress={handleUpdateAddress}
            handleAddAddress={handleAddAddress}
            handleCancelForm={handleCancelForm}
          />
        )}

        {loadingAddresses ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-600 mt-4">Đang tải địa chỉ...</p>
          </div>
        ) : addresses.length === 0 ? (
          <div className="text-center py-12 bg-gray-50 rounded-lg">
            <MapPin className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 mb-2">Chưa có địa chỉ giao hàng</p>
            <p className="text-sm text-gray-500">Thêm địa chỉ để tiện cho việc đặt hàng</p>
          </div>
        ) : (
          <div className="space-y-4 mb-6">
            {addresses.map((address: any) => (
              <div key={address.addressId ?? address.address_id}>
                <div className="border border-gray-200 rounded-lg p-6 relative">
                  <div className="pr-16">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="font-semibold">{address.name || address.fullName || ''}</h4>
                      <span className="text-gray-400">|</span>
                      <span className="text-gray-600">{address.phone || address.phoneNumber || '-'}</span>
                      {address.isDefault && (
                        <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full flex items-center gap-1">
                          <Check className="h-3 w-3" />
                          Mặc định
                        </span>
                      )}
                    </div>
                    <p className="text-gray-700 mb-3">{address.fullAddress ?? `${address.province}, ${address.ward}, ${address.hamlet ?? ''}, ${address.detail}`}</p>
                    {!address.isDefault && (
                      <button onClick={() => handleSetDefaultAddress(address.addressId ?? address.address_id)} className="text-blue-600 hover:text-blue-800 text-sm font-medium">Đặt làm mặc định</button>
                    )}
                  </div>

                  <div className="absolute bottom-4 right-4 flex gap-2">
                    <button onClick={() => handleEditAddress(address)} className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg" title="Chỉnh sửa"><Edit className="h-4 w-4" /></button>
                    <button onClick={() => handleDeleteAddress(address.addressId ?? address.address_id)} className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg" title="Xóa"><Trash2 className="h-4 w-4" /></button>
                  </div>
                </div>

                {/* Edit Form Below Address */}
                {showAddressForm && formPosition === 'bottom' && editingAddress?.addressId === (address.addressId ?? address.address_id) && (
                  <div className="mt-4">
                    <AddressFormComponent
                      editingAddress={editingAddress}
                      newAddress={newAddress}
                      setNewAddress={setNewAddress}
                      provinces={provinces}
                      wards={wards}
                      hamlets={hamlets}
                      loadingWards={loadingWards}
                      loadingHamlets={loadingHamlets}
                      setWards={setWards}
                      setHamlets={setHamlets}
                      addressLoading={addressLoading}
                      handleUpdateAddress={handleUpdateAddress}
                      handleAddAddress={handleAddAddress}
                      handleCancelForm={handleCancelForm}
                    />
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4">Shipping Options</h2>
        <div className="grid gap-4">
          <div className="flex items-center justify-between">
            <div>
              <span className="font-medium">Cash on Delivery</span>
              <div className="text-sm text-gray-500">Allow COD payments</div>
            </div>
            <Toggle
              checked={localSettings.shipping.cod}
              onChange={(v) => setLocalSettings({
                ...localSettings,
                shipping: { ...localSettings.shipping, cod: v }
              })}
            />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <span className="font-medium">Express Shipping</span>
              <div className="text-sm text-gray-500">Fast shipping options</div>
            </div>
            <Toggle
              checked={localSettings.shipping.express}
              onChange={(v) => setLocalSettings({
                ...localSettings,
                shipping: { ...localSettings.shipping, express: v }
              })}
            />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <span className="font-medium">Standard Shipping</span>
              <div className="text-sm text-gray-500">Economy shipping options</div>
            </div>
            <Toggle
              checked={localSettings.shipping.standard}
              onChange={(v) => setLocalSettings({
                ...localSettings,
                shipping: { ...localSettings.shipping, standard: v }
              })}
            />
          </div>
        </div>
      </div>
    </section>
  );
}