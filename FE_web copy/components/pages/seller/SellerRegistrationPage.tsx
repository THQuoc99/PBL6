import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import AuthLayout from '../../layout/AuthLayout';
import { useCreateStore } from '../../../hooks/store/useCreateStore';
import CustomerLayout from '../../layout/CustomerLayout';
import { 
  Store, 
  Mail, 
  Phone, 
  MapPin, 
  Plus, 
  ArrowRight, 
  ArrowLeft,
  Upload,
  Camera,
  IdCard,
  Building,
  FileText,
  CheckCircle,
  User,
  Globe,
  Edit,
  Trash2,
  Check
} from 'lucide-react';
import { storeService } from '../../../services/store/store';
import { getProvinces, getWards, getHamlets } from '../../../services/callAPI/apiAddress';

interface SellerRegistrationPageProps {}

type RegistrationStep = 'store-info' | 'complete';

interface Address {
  id: string;
  phone: string;
  province: string;
  ward: string;
  street: string;
  specificAddress: string;
  address: string;
  isDefault: boolean;
}

interface StoreInfo {
  shopName: string;
  selectedAddressId: string;
  email: string;
  phone: string;
  description?: string;
  avatarFile?: File | null;
  logoFile?: File | null;
  coverImageFile?: File | null;
}



export default function SellerRegistrationPage(_: SellerRegistrationPageProps) {
  const [currentStep, setCurrentStep] = useState<RegistrationStep>('store-info');
  const navigate = useNavigate();
  const [storeInfo, setStoreInfo] = useState<StoreInfo>({
    shopName: '',
    selectedAddressId: '',
    email: '',
    phone: '',
    description: '',
    avatarFile: null,
    logoFile: null,
    coverImageFile: null
  });
  const [shopNameTaken, setShopNameTaken] = useState(false);
  const [showAddressList, setShowAddressList] = useState(false);
  const [showAddressForm, setShowAddressForm] = useState(false);
  const [editingAddress, setEditingAddress] = useState<Address | null>(null);
  const [newAddress, setNewAddress] = useState({
    
    phone: '',
    province: '',
    ward: '',
    street: '',
    specificAddress: '',
    isDefault: false
  });

  // Address selection data (reuse API helpers like in AccountPage)
  const [provinces, setProvinces] = useState<any[]>([]);
  const [wards, setWards] = useState<any[]>([]);
  const [hamlets, setHamlets] = useState<any[]>([]);
  const [loadingWards, setLoadingWards] = useState(false);
  const [loadingHamlets, setLoadingHamlets] = useState(false);
  

  // Local addresses saved during this session
  const [addresses, setAddresses] = useState<Address[]>([]);

  const { createStore, loading: creating, error: createError } = useCreateStore();

  // Load provinces on mount
  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const provs = await getProvinces();
        if (!mounted) return;
        setProvinces(Array.isArray(provs) ? provs : []);
      } catch (e) {
        if (!mounted) return;
        setProvinces([]);
      }
    })();

    return () => { mounted = false; };
  }, []);

  // When province changes, load wards
  useEffect(() => {
    let mounted = true;
    const loadWards = async () => {
      if (!newAddress.province) {
        setWards([]);
        setHamlets([]);
        return;
      }
      setLoadingWards(true);
      try {
        const res = await getWards(newAddress.province);
        if (!mounted) return;
        setWards(Array.isArray(res) ? res : []);
        setHamlets([]);
      } catch (e) {
        if (!mounted) return;
        setWards([]);
        setHamlets([]);
      }
      setLoadingWards(false);
    };
    loadWards();
    return () => { mounted = false; };
  }, [newAddress.province]);

  // When ward changes, load hamlets
  useEffect(() => {
    let mounted = true;
    const loadHamlets = async () => {
      if (!newAddress.province || !newAddress.ward) {
        setHamlets([]);
        return;
      }
      setLoadingHamlets(true);
      try {
        // newAddress.province/ward now store codes; map them to human-readable names for GHTK
        const prov = provinces.find((p: any) => String(p.province_code ?? p.code) === String(newAddress.province));
        const wardObj = wards.find((w: any) => String(w.ward_code ?? w.code) === String(newAddress.ward));
        const provinceName = prov ? (prov.province_name ?? prov.name ?? String(prov.province_code ?? prov.code)) : String(newAddress.province);
        const wardName = wardObj ? (wardObj.ward_name ?? wardObj.name ?? String(wardObj.ward_code ?? wardObj.code)) : String(newAddress.ward);

        const res = await getHamlets(provinceName, wardName);
        if (!mounted) return;
        setHamlets(Array.isArray(res) ? res : []);
      } catch (e) {
        if (!mounted) return;
        setHamlets([]);
      }
      setLoadingHamlets(false);
    };
    loadHamlets();
    return () => { mounted = false; };
  }, [newAddress.province, newAddress.ward]);

  const defaultAddress = addresses.find(addr => addr.isDefault);
  const currentAddress = addresses.find(addr => addr.id === storeInfo.selectedAddressId) || defaultAddress;

  const handleSelectAddress = (addressId: string) => {
    setStoreInfo(prev => ({ ...prev, selectedAddressId: addressId }));
    setShowAddressList(false);
  };

  const handleEditAddress = (address: Address) => {
    setEditingAddress(address);
    setNewAddress({
      phone: address.phone,
      province: address.province,
      ward: address.ward,
      street: address.street,
      specificAddress: address.specificAddress,
      isDefault: address.isDefault
    });
    setShowAddressForm(true);
    setShowAddressList(false);
  };

  const handleDeleteAddress = (addressId: string) => {
    const filtered = addresses.filter(a => a.id !== addressId);
    setAddresses(filtered);
    // if deleted was selected, clear selection or pick first
    if (storeInfo.selectedAddressId === addressId) {
      const first = filtered[0];
      if (first) {
        // make first default if none
        const updated = filtered.map((f, idx) => ({ ...f, isDefault: idx === 0 }));
        setAddresses(updated);
        setStoreInfo(prev => ({ ...prev, selectedAddressId: first.id }));
      } else {
        setStoreInfo(prev => ({ ...prev, selectedAddressId: '' }));
      }
    }
  };

  const handleSetDefaultAddress = (addressId: string) => {
    const updated = addresses.map(a => ({ ...a, isDefault: a.id === addressId }));
    setAddresses(updated);
    setStoreInfo(prev => ({ ...prev, selectedAddressId: addressId }));
  };

  const handleSaveAddress = () => {
    // Resolve province and ward codes to readable names for display
    const provObj = provinces.find((p: any) => String(p.province_code ?? p.code) === String(newAddress.province));
    const wardObj = wards.find((w: any) => String(w.ward_code ?? w.code) === String(newAddress.ward));
    const provinceDisplay = provObj ? (provObj.province_name ?? provObj.name ?? String(provObj.province_code ?? provObj.code)) : newAddress.province;
    const wardDisplay = wardObj ? (wardObj.ward_name ?? wardObj.name ?? String(wardObj.ward_code ?? wardObj.code)) : newAddress.ward;
    const fullAddress = `${provinceDisplay}, ${wardDisplay}, ${newAddress.street}, ${newAddress.specificAddress}`;
    if (editingAddress) {
      const updated = addresses.map(a => a.id === editingAddress.id ? ({ ...a, ...newAddress, address: fullAddress }) : a);
      // If this edited address is set as default, ensure others are unset
      if (newAddress.isDefault) {
        const norm = updated.map(u => ({ ...u, isDefault: u.id === editingAddress.id }));
        setAddresses(norm);
      } else {
        setAddresses(updated);
      }
    } else {
      const newEntry: Address = {
        id: String(Date.now()),
        phone: newAddress.phone || '',
        province: newAddress.province,
        ward: newAddress.ward,
        street: newAddress.street,
        specificAddress: newAddress.specificAddress,
        address: fullAddress,
        isDefault: newAddress.isDefault || addresses.length === 0
      };
      // If new entry is default, unset others
      if (newEntry.isDefault) {
        const rest = addresses.map(a => ({ ...a, isDefault: false }));
        setAddresses([newEntry, ...rest]);
      } else {
        setAddresses(prev => [newEntry, ...prev]);
      }
      // if this is the first address, select it
      if (addresses.length === 0) {
        setStoreInfo(prev => ({ ...prev, selectedAddressId: newEntry.id }));
      }
    }
    setShowAddressForm(false);
    setEditingAddress(null);
    setNewAddress({ phone: '', province: '', ward: '', street: '', specificAddress: '', isDefault: false });
  };

  const handleCancelAddressForm = () => {
    setShowAddressForm(false);
    setEditingAddress(null);
    setNewAddress({ phone: '', province: '', ward: '', street: '', specificAddress: '', isDefault: false });
    if (showAddressList) {
      setShowAddressList(true);
    }
  };

  const steps = [
    { key: 'complete', title: 'Hoàn tất', icon: CheckCircle }
  ];

  const getCurrentStepIndex = () => steps.findIndex(step => step.key === currentStep);

  const handleNext = () => {
    const currentIndex = getCurrentStepIndex();
    if (currentIndex < steps.length - 1) {
      setCurrentStep(steps[currentIndex + 1].key as RegistrationStep);
    }
  };

  const handlePrevious = () => {
    const currentIndex = getCurrentStepIndex();
    if (currentIndex > 0) {
      setCurrentStep(steps[currentIndex - 1].key as RegistrationStep);
    }
  };

  const handleStoreFileChange = (field: 'avatarFile' | 'logoFile' | 'coverImageFile') => (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] || null;
    setStoreInfo(prev => ({ ...prev, [field]: file }));
  };

  const handleCreateStore = async () => {
    if (!storeInfo.shopName || !currentAddress) return;

    const input = {
      name: storeInfo.shopName,
      email: storeInfo.email,
      description: storeInfo.description,
      addresses: addresses.map((addr) => ({
        province: addr.province,
        ward: addr.ward,
        hamlet: addr.street,
        detail: addr.specificAddress,
        phone: addr.phone, // Phone comes from addresses
        is_default: addr.isDefault,
      })),
    };

    const files: any = {
      avatar: storeInfo.avatarFile || undefined,
      coverImage: storeInfo.coverImageFile || undefined,
      logo: storeInfo.logoFile || undefined
    };

    try {
      const result = await createStore(input as any, files as any);
      if (result?.success) {
        // Redirect straight to seller dashboard on success
        navigate('/seller/dashboard');
      } else {
        alert(result?.message || 'Tạo cửa hàng thất bại');
      }
    } catch (err) {
      alert('Đăng ký cửa hàng thất bại');
    }
  };

  const renderStoreInfoStep = () => {
    const currentWardName = ((): string => {
      const w = wards.find((x: any) => String(x.ward_code ?? x.code ?? x.id ?? x.name) === String(newAddress.ward));
      return w ? (w.ward_name ?? w.name ?? String(w.ward_code ?? w.code)) : String(newAddress.ward);
    })();

    return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900">Thông tin Shop</h2>
        <p className="text-gray-600 mt-2">Cung cấp thông tin cơ bản về cửa hàng của bạn</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="space-y-4 lg:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <span className="text-red-500">*</span> Tên Shop
          </label>
          <input
            type="text"
            value={storeInfo.shopName}
            onChange={(e) => setStoreInfo(prev => ({ ...prev, shopName: e.target.value }))}
            className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="shopIT"
            maxLength={30}
          />
          <div className="text-right text-sm text-gray-500 mt-1">
            {storeInfo.shopName.length}/30
          </div>
          {shopNameTaken && (
            <p className="text-sm text-red-500 mt-1">Tên Shop đã được sử dụng</p>
          )}
        </div>

        <div className="space-y-4 lg:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <span className="text-red-500">*</span> Địa chỉ lấy hàng
          </label>

          {/* No demo address list shown by default. User must click to add an address. */}
          {!showAddressForm && (
            <button 
              onClick={() => { setShowAddressForm(true); setShowAddressList(false); }}
              className="w-full px-3 py-3 border border-gray-300 rounded-lg text-left text-gray-500 hover:bg-gray-50"
            >
              <Plus className="inline h-4 w-4 mr-2" />
              Thêm địa chỉ lấy hàng
            </button>
          )}

          {showAddressForm && (
            <div>
              <h4 className="font-medium mb-4">
                {editingAddress ? 'Chỉnh sửa địa chỉ' : 'Thêm địa chỉ mới'}
              </h4>
              <div className="space-y-4">
                <div className="grid grid-cols-1 gap-4">
                  <input
                    type="tel"
                    placeholder="Số điện thoại *"
                    value={newAddress.phone}
                    onChange={(e) => setNewAddress({...newAddress, phone: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <select
                    value={newAddress.province}
                    onChange={(e) => setNewAddress({...newAddress, province: e.target.value, ward: '', street: ''})}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Chọn Tỉnh/Thành phố *</option>
                    {provinces && provinces.length > 0 ? (
                      provinces.map((p: any) => {
                        const code = p.province_code ?? p.code ?? String(p.province_code ?? p.code ?? '');
                        const name = p.province_name ?? p.name ?? String(p.province_name ?? p.name ?? code);
                        return (
                          <option key={code} value={code}>
                            {name}
                          </option>
                        );
                      })
                    ) : (
                      <>
                        <option value="79">TP.Hồ Chí Minh</option>
                        <option value="01">Hà Nội</option>
                        <option value="48">Đà Nẵng</option>
                        <option value="92">Cần Thơ</option>
                        <option value="31">Hải Phòng</option>
                      </>
                    )}
                  </select>

                  <select
                    value={newAddress.ward}
                    onChange={(e) => setNewAddress({...newAddress, ward: e.target.value})}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={!newAddress.province || loadingWards}
                  >
                    <option value="">Chọn Phường/Xã *</option>
                    {loadingWards && (
                      <option value="">Đang tải...</option>
                    )}
                    {!loadingWards && wards && wards.length > 0 && (
                      wards.map((w: any) => {
                        const wcode = w.ward_code ?? w.code ?? String(w.ward_code ?? w.code ?? '');
                        const wname = w.ward_name ?? w.name ?? String(w.ward_name ?? w.name ?? wcode);
                        return (
                          <option key={wcode} value={wcode}>
                            {wname}
                          </option>
                        );
                      })
                    )}
                  </select>
                </div>

                <select
                  value={newAddress.street}
                  onChange={(e) => setNewAddress({...newAddress, street: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={!newAddress.ward || loadingHamlets}
                >
                  <option value="">Chọn Đường/Khu vực *</option>
                  {loadingHamlets && (
                    <option value="">Đang tải...</option>
                  )}
                  {!loadingHamlets && hamlets && hamlets.length > 0 ? (
                    hamlets.map((h: any, idx: number) => (
                      <option key={String(h) + idx} value={h}>{h}</option>
                    ))
                  ) : (
                    // Keep some sensible defaults for a better UX if no hamlets
                    currentWardName === 'Phường Bến Nghé' ? (
                      <>
                        <option value="Đường Lê Lợi">Đường Lê Lợi</option>
                        <option value="Đường Nguyễn Huệ">Đường Nguyễn Huệ</option>
                        <option value="Đường Đồng Khởi">Đường Đồng Khởi</option>
                      </>
                    ) : currentWardName === 'Phường Bến Thành' ? (
                      <>
                        <option value="Đường Lê Thị Riêng">Đường Lê Thị Riêng</option>
                        <option value="Đường Tôn Thất Đạm">Đường Tôn Thất Đạm</option>
                        <option value="Đường Phạm Ngũ Lão">Đường Phạm Ngũ Lão</option>
                      </>
                    ) : null
                  )}
                </select>

                <input
                  type="text"
                  placeholder="Địa chỉ cụ thể (số nhà, tòa nhà) *"
                  value={newAddress.specificAddress}
                  onChange={(e) => setNewAddress({...newAddress, specificAddress: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />

                <label className="inline-flex items-center gap-2 mt-2">
                  <input
                    type="checkbox"
                    checked={!!newAddress.isDefault}
                    onChange={(e) => setNewAddress({...newAddress, isDefault: e.target.checked})}
                    className="h-4 w-4"
                  />
                  <span className="text-sm text-gray-700">Đặt làm địa chỉ mặc định</span>
                </label>

                <div className="flex gap-3 pt-4">
                  <button
                    onClick={handleSaveAddress}
                    className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    {editingAddress ? 'Cập nhật' : 'Thêm địa chỉ'}
                  </button>
                  <button
                    onClick={handleCancelAddressForm}
                    className="flex-1 border border-gray-300 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Hủy
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Show saved addresses as fulladdress lines for easy review */}
          {!showAddressForm && addresses.length > 0 && (
            <div className="space-y-4 mb-6">
              {addresses.map((addr) => (
                <div key={addr.id}>
                  <div className="border border-gray-200 rounded-lg p-6 relative">
                    <div className="pr-16">
                      <div className="flex items-center gap-3 mb-2">
                        <h4 className="font-semibold">{addr.address}</h4>
                        <span className="text-gray-400">|</span>
                        <span className="text-gray-600">{addr.phone}</span>
                        {addr.isDefault && (
                          <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full flex items-center gap-1">
                            <Check className="h-3 w-3" />
                            Mặc định
                          </span>
                        )}
                      </div>
                      <p className="text-gray-700 mb-3">{addr.address}</p>

                      {!addr.isDefault && (
                        <button
                          onClick={() => handleSetDefaultAddress(addr.id)}
                          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                        >
                          Đặt làm mặc định
                        </button>
                      )}
                    </div>

                            <div className="absolute bottom-4 right-4 flex gap-2">
                              <button
                                onClick={() => handleEditAddress(addr)}
                                className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                title="Chỉnh sửa"
                              >
                                <Edit className="h-4 w-4" />
                              </button>
                              <button
                                onClick={() => {
                                  if (!confirm('Bạn có chắc chắn muốn xóa địa chỉ này?')) return;
                                  handleDeleteAddress(addr.id);
                                }}
                                className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                title="Xóa"
                              >
                                <Trash2 className="h-4 w-4" />
                              </button>
                            </div>
                  </div>

                  {showAddressForm && editingAddress?.id === addr.id && (
                    <div className="mt-4">
                      {/* Existing inline form is reused when editing */}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="lg:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <span className="text-red-500">*</span> Email
          </label>
          <input
            type="email"
            value={storeInfo.email}
            onChange={(e) => setStoreInfo(prev => ({ ...prev, email: e.target.value }))}
            className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="tranhuuquoc12a10@gmail.com"
          />
        </div>

        <div className="lg:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">Mô tả Shop</label>
          <textarea
            value={storeInfo.description}
            onChange={(e) => setStoreInfo(prev => ({ ...prev, description: e.target.value }))}
            className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Mô tả ngắn về cửa hàng của bạn"
            rows={4}
          />

        </div>

        {/* Right column: compact image card */}
        <div className="grid grid-rows-[auto,1fr] gap-8 h-full">
          <label className="block text-sm font-medium text-gray-700 mb-2">Ảnh cửa hàng</label>

          <div className="bg-gray-50 border border-gray-200 rounded-lg overflow-hidden w-full">
            <div className="relative w-full h-40 md:h-48 bg-gray-100 z-0">
              {storeInfo.coverImageFile ? (
                <img src={URL.createObjectURL(storeInfo.coverImageFile)} alt="cover-preview" className="w-full h-full object-cover z-0" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-400">Ảnh bìa</div>
              )}
              <label className="absolute right-3 top-3 z-10 bg-white/90 px-2 py-1 rounded-md cursor-pointer text-xs text-gray-700 border border-gray-200 hover:bg-white">
                Thay
                <input type="file" accept="image/*" onChange={handleStoreFileChange('coverImageFile')} className="hidden" />
              </label>
            </div>
            
            <div className="px-4 py-4 -mt-24 flex items-center gap-4 justify-center md:justify-start">
              <div className="relative z-30">
                <div className="w-28 h-28 rounded-full bg-white border-4 border-white shadow-sm overflow-hidden flex items-center justify-center">
                  {storeInfo.avatarFile ? (
                    <img src={URL.createObjectURL(storeInfo.avatarFile)} alt="avatar" className="w-full h-full object-cover" />
                  ) : (
                    <div className="text-gray-400">Avatar</div>
                  )}
                </div>
                <label className="absolute -right-1 -bottom-1 bg-white border rounded-full p-1 cursor-pointer text-xs z-40" title="Thay ảnh đại diện">
                  <input type="file" accept="image/*" onChange={handleStoreFileChange('avatarFile')} className="hidden" />
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536M9 11l6-6m2 8v6a2 2 0 01-2 2H7a2 2 0 01-2-2V7a2 2 0 012-2h6" /></svg>
                </label>
              </div>

              <div className="flex flex-col z-30">
                <div className="text-sm font-medium text-gray-700">Logo</div>
                <div className="mt-2 w-20 h-20 rounded-md bg-white border overflow-hidden flex items-center justify-center">
                  {storeInfo.logoFile ? (
                    <img src={URL.createObjectURL(storeInfo.logoFile)} alt="logo" className="w-full h-full object-contain p-1" />
                  ) : (
                    <div className="text-gray-400 text-xs">Chưa có logo</div>
                  )}
                </div>
                <label className="mt-2 text-xs text-blue-600 cursor-pointer" title="Thay logo">
                  Thay
                  <input type="file" accept="image/*" onChange={handleStoreFileChange('logoFile')} className="hidden" />
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
  };

  const renderCompleteStep = () => (
    <div className="text-center space-y-6">
      <div className="mx-auto w-24 h-24 bg-green-100 rounded-full flex items-center justify-center">
        <CheckCircle className="h-12 w-12 text-green-600" />
      </div>
      
      <div>
        <h2 className="text-3xl font-bold text-gray-900 mb-4">Đăng ký thành công!</h2>
        <p className="text-gray-600 text-lg">
          Cảm ơn bạn đã đăng ký làm seller trên SHOEX. 
          Chúng tôi sẽ xem xét hồ sơ của bạn trong vòng 1-2 ngày làm việc.
        </p>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-left">
        <h3 className="font-semibold text-blue-900 mb-3">Các bước tiếp theo:</h3>
        <ul className="space-y-2 text-sm text-blue-800">
          <li className="flex items-center space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span>Xem xét hồ sơ và xác minh thông tin</span>
          </li>
          <li className="flex items-center space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span>Gửi email xác nhận khi được duyệt</span>
          </li>
          <li className="flex items-center space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span>Hướng dẫn sử dụng tài khoản seller</span>
          </li>
        </ul>
      </div>

      <button
        onClick={() => {
          navigate('/seller/dashboard');
        }}
        className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors font-medium"
      >
        Hoàn tất
      </button>
    </div>
  );

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 'store-info':
        return renderStoreInfoStep();
      case 'complete':
        return renderCompleteStep();
      default:
        return renderStoreInfoStep();
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 'store-info':
        // Allow proceed when shopName and email provided, and either a top-level phone
        // or a selected/current address that includes a phone number.
        const addressPhone = currentAddress?.phone;
        return !!(storeInfo.shopName && storeInfo.email && (storeInfo.phone || addressPhone));
      default:
        return true;
    }
  };

  if (currentStep === 'complete') {
    return (
      <AuthLayout title="Hoàn tất đăng ký">
        <div className="w-full max-w-2xl mx-auto">
          {renderCompleteStep()}
        </div>
      </AuthLayout>
    );
  }

  return (
    <CustomerLayout >
      <div className="w-full max-w-4xl mx-auto">
        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {steps.slice(0, -1).map((step, index) => {
              const isActive = step.key === currentStep;
              const isCompleted = getCurrentStepIndex() > index;
              const StepIcon = step.icon;
              
              return (
                <div key={step.key} className="flex flex-col items-center">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center mb-2 ${
                    isCompleted 
                      ? 'bg-green-500 text-white' 
                      : isActive 
                        ? 'bg-blue-500 text-white' 
                        : 'bg-gray-200 text-gray-400'
                  }`}>
                    {isCompleted ? (
                      <CheckCircle className="h-6 w-6" />
                    ) : (
                      <StepIcon className="h-6 w-6" />
                    )}
                  </div>
                  <span className={`text-sm font-medium ${
                    isActive ? 'text-blue-600' : isCompleted ? 'text-green-600' : 'text-gray-500'
                  }`}>
                    {step.title}
                  </span>
                </div>
              );
            })}
          </div>
          
          {/* Progress Bar */}
          <div className="mt-4 bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(getCurrentStepIndex() / (steps.length - 1)) * 100}%` }}
            />
          </div>
        </div>

        {/* Step Content */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          {renderCurrentStep()}

          {/* Navigation Buttons */}
          {currentStep === 'store-info' && (
            <div className="flex justify-between mt-8 pt-6 border-t">
              <div className="flex space-x-3">
                {getCurrentStepIndex() > 0 && (
                  <button
                    onClick={handlePrevious}
                    className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    <ArrowLeft className="h-4 w-4" />
                    <span>Quay lại</span>
                  </button>
                )}

                <button
                   onClick={() => {
                navigate('/home');
              }}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
                >
                  Quay lại trang khách hàng
                </button>
              </div>

              <div className="flex items-center space-x-3">
                <button
                  onClick={handleCreateStore}
                  disabled={!canProceed()}
                  className="flex items-center space-x-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <span>Tạo cửa hàng</span>
                  <ArrowRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </CustomerLayout>
  );
}