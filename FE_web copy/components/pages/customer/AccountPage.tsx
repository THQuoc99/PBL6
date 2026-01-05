import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import CustomerLayout from '../../layout/CustomerLayout';
import { authService } from '../../../services/user/auth';
import { useAddresses } from '../../../hooks/user/address';
import { getProvinces, getWards, getHamlets } from '../../../services/callAPI/apiAddress';
import { 
  User, ShoppingBag, Heart, Settings, LogOut, Edit, Camera, MapPin, 
  Phone, Mail, Gift, Calendar, Plus, Trash2, Check, Star, Upload, Store,
  Truck, Clock, MapPinIcon, X, Package, CheckCircle, Ticket, Tag
} from 'lucide-react';
import useMyOrders, { useCancelOrder, useCancelSubOrder } from '../../../hooks/order/useOrders';
import { useCreateVnPayLink } from '../../../hooks/payment/payment';
import { useSaveVoucher, useSavedVouchers } from '../../../hooks/discount/discount';

interface AccountPageProps {
  // onNavigate nhận URL string, có thể kèm data tùy chọn
  onNavigate?: (url: string, data?: any) => void;
}


interface Address {
  addressId: string;
  name: string;
  phoneNumber?: string;
  province: string;
  ward: string;
  hamlet?: string;
  detail: string;
  fullAddress: string;
  isDefault: boolean;
}

interface Voucher {
  voucher_id: number;
  code: string;
  type: 'platform' | 'seller';
  seller?: {
    id: number;
    name: string;
    logo?: string;
  };
  discount_type: 'percent' | 'fixed';
  discount_value: number;
  min_order_amount: number;
  max_discount?: number;
  start_date: string;
  end_date: string;
  usage_limit?: number;
  per_user_limit: number;
  is_active: boolean;
  is_auto: boolean;
  description?: string;
  // User voucher specific fields
  saved_at: string;
  used_count: number;
  can_use: boolean;
}

// AddressForm component - tách ra ngoài để tránh re-create
const AddressFormComponent = React.memo<{
  editingAddress: Address | null;
  newAddress: any;
  setNewAddress: (value: any) => void;
  provinces: any[];
  wards: any[];
  hamlets: any[];
  loadingWards: boolean;
  loadingHamlets: boolean;
  setWards: (value: any[]) => void;
  setHamlets: (value: any[]) => void;
  addressLoading: boolean;
  handleUpdateAddress: () => void;
  handleAddAddress: () => void;
  handleCancelForm: () => void;
}>(({ 
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
}) => (
  <div className="border border-gray-300 rounded-lg p-6 bg-gray-50">
    <h3 className="font-semibold mb-4">
      {editingAddress ? 'Chỉnh sửa địa chỉ' : 'Thêm địa chỉ mới'}
    </h3>
    <div className="space-y-4">
      {/* Thông tin liên hệ */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Họ và tên *
          </label>
          <input
            type="text"
            value={newAddress.name}
            onChange={(e) => {
              const value = e.target.value;
              setNewAddress((prev: any) => ({...prev, name: value}));
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Nhập họ và tên"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Số điện thoại *
          </label>
          <input
            type="tel"
            value={newAddress.phoneNumber}
            onChange={(e) => {
              const value = e.target.value;
              setNewAddress((prev: any) => ({...prev, phoneNumber: value}));
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Nhập số điện thoại"
          />
        </div>
      </div>
      
      {/* Địa chỉ từ API */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Tỉnh/Thành phố *
          </label>
          {provinces.length > 0 ? (
            <select
              value={newAddress.provinceId}
              onChange={(e) => {
                const selectedProvince = provinces.find((p: any) => p.code === parseInt(e.target.value));
                const newState = {
                  ...newAddress,
                  provinceId: e.target.value,
                  province: selectedProvince?.name || '',
                  wardId: '',
                  ward: '',
                  hamlet: ''
                };
                setNewAddress(newState);
                setWards([]);
                setHamlets([]);
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Chọn Tỉnh/Thành phố</option>
              {provinces.map((province: any) => (
                <option key={province.code} value={province.code}>
                  {province.name}
                </option>
              ))}
            </select>
          ) : (
            <input
              type="text"
              value={newAddress.province}
              onChange={(e) => {
                const value = e.target.value;
                setNewAddress((prev: any) => ({...prev, province: value, provinceId: ''}));
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Nhập tên tỉnh/thành phố"
            />
          )}
          {provinces.length === 0 && (
            <p className="text-xs text-red-500 mt-1">Không tải được danh sách tỉnh. Vui lòng nhập thủ công.</p>
          )}
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Phường/Xã * {!newAddress.provinceId && !newAddress.province && <span className="text-gray-400 text-xs">(Chọn tỉnh trước)</span>}
            {loadingWards && <span className="text-blue-600 text-xs ml-2">⏳ Đang tải...</span>}
          </label>
          {loadingWards ? (
            <div className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500 flex items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
              Đang tải danh sách phường/xã...
            </div>
          ) : wards.length > 0 && newAddress.provinceId ? (
            <select
              value={newAddress.wardId}
    
              onChange={(e) => {
                console.log('❤️❤️❤️❤️❤️❤️',e.target.value);
                const selectedWard = wards.find((w: any) => w.code === parseInt(e.target.value));
                const newState = {
                  ...newAddress,
                  wardId: e.target.value,
                  ward: selectedWard?.name || '',
                  hamlet: ''
                };
                console.log('❤️❤️❤️❤️❤️❤️ newState',newState);
                setNewAddress(newState);
                setHamlets([]);
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Chọn Phường/Xã</option>
              {wards.map((ward: any) => (
                <option key={ward.code} value={ward.code}>
                  {ward.name}
                </option>
              ))}
            </select>
          ) : (
            <input
              type="text"
              value={newAddress.ward}
              onChange={(e) => {
                const value = e.target.value;
                setNewAddress((prev: any) => ({...prev, ward: value, wardId: '', hamlet: ''}));
              }}
              className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                (!newAddress.province && !newAddress.provinceId) 
                  ? 'border-gray-200 bg-gray-50 text-gray-400 cursor-not-allowed' 
                  : 'border-gray-300 bg-white'
              }`}
              placeholder={(!newAddress.province && !newAddress.provinceId) ? "Chọn tỉnh trước" : "Nhập tên phường/xã"}
              disabled={!newAddress.province && !newAddress.provinceId}
            />
          )}
          {newAddress.provinceId && wards.length === 0 && !loadingWards && (
            <p className="text-xs text-amber-600 mt-1">Không tải được danh sách. Vui lòng nhập thủ công.</p>
          )}
        </div>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Thôn/Khu/Ấp (tùy chọn) {!newAddress.ward && !newAddress.wardId && <span className="text-gray-400 text-xs">(Chọn phường/xã trước)</span>}
          {loadingHamlets && <span className="text-blue-600 text-xs ml-2">⏳ Đang tải...</span>}
        </label>
        {loadingHamlets ? (
          <div className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500 flex items-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
            Đang tải danh sách thôn/khu/ấp...
          </div>
        ) : hamlets.length > 0 && (newAddress.ward || newAddress.wardId) ? (
          <select
            value={newAddress.hamletId}
            onChange={(e) => {
              const selectedIndex = e.target.value;
              const selectedHamlet = hamlets[parseInt(selectedIndex)];
              const hamletName = selectedHamlet?.name || selectedHamlet || '';
              setNewAddress((prev: any) => ({
                ...prev, 
                hamletId: selectedIndex,
                hamlet: hamletName
              }));
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Chọn Thôn/Khu/Ấp</option>
            {hamlets.map((hamlet: any, index: number) => {
              const hamletName = hamlet.name || hamlet;
              return (
                <option key={`hamlet-${hamletName}-${index}`} value={index.toString()}>
                  {hamletName}
                </option>
              );
            })}
          </select>
        ) : (
          <input
            type="text"
            value={newAddress.hamlet}
            onChange={(e) => {
              const value = e.target.value;
              setNewAddress((prev: any) => ({...prev, hamlet: value}));
            }}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              (!newAddress.ward && !newAddress.wardId) 
                ? 'border-gray-200 bg-gray-50 text-gray-400 cursor-not-allowed' 
                : 'border-gray-300 bg-white'
            }`}
            placeholder={(!newAddress.ward && !newAddress.wardId) ? "Chọn phường/xã trước" : "Nhập thôn/khu/ấp (nếu có)"}
            disabled={!newAddress.ward && !newAddress.wardId}
          />
        )}
        {(newAddress.ward || newAddress.wardId) && hamlets.length === 0 && !loadingHamlets && (
          <p className="text-xs text-gray-500 mt-1">
            Không có dữ liệu thôn/khu/ấp. Bạn có thể nhập thủ công hoặc bỏ qua.
          </p>
        )}
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Địa chỉ chi tiết *
        </label>
        <textarea
          value={newAddress.detail}
          onChange={(e) => {
            const value = e.target.value;
            setNewAddress((prev: any) => ({...prev, detail: value}));
          }}
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="Số nhà, tầng, căn hộ, ghi chú thêm..."
        />
      </div>
      
      <div className="flex gap-3">
        <button
          onClick={editingAddress ? handleUpdateAddress : handleAddAddress}
          disabled={addressLoading}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          {addressLoading ? 'Đang xử lý...' : (editingAddress ? 'Cập nhật' : 'Thêm địa chỉ')}
        </button>
        <button
          onClick={handleCancelForm}
          className="border border-gray-300 px-6 py-2 rounded-lg hover:bg-gray-50 transition-colors"
        >
          Hủy
        </button>
      </div>
    </div>
  </div>
));

export default function AccountPage({ onNavigate }: AccountPageProps) {
  const [activeTab, setActiveTab] = useState('profile');
  const [userInfo, setUserInfo] = useState({
    name: '',
    email: '',
    phone: '',
    address: '',
    birthday: '',
    gender: 'male',
    memberSince: '',
    avatar: ''
  });

  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [showAddressForm, setShowAddressForm] = useState(false);

  const navigate = useNavigate();

useEffect(() => {
  if (typeof window === 'undefined') return; // Chỉ chạy trên client

  if (authService.isAuthenticated()) {
    loadUserProfile();
  } else {
    const currentUser = authService.getCurrentUser(); // có thể dùng localStorage
    if (currentUser) {
      setUserInfo({
        name: currentUser.fullName || currentUser.username || 'Người dùng',
        email: currentUser.email || '',
        phone: currentUser.phone || '',
        address: '',
        birthday: '',
        gender: 'male',
        memberSince: currentUser.dateJoined || '',
        avatar: currentUser.avatarUrl || ''
      });
    }
    setLoading(false);
  }
}, []);


  const loadUserProfile = async () => {
    try {
      setLoading(true);
      const response = await authService.getUserProfile();
      
      if (response.success && response.user) {
        const user = response.user;
        setUserInfo({
          name: user.fullName || `${user.firstName || ''} ${user.lastName || ''}`.trim() || user.username || 'Người dùng',
          email: user.email || '',
          phone: user.phone || '',
          address: '', // Có thể lấy từ address API riêng
          birthday: user.birthDate || '', // ✅ Load birthDate từ backend
          gender: 'male', // Có thể thêm field này vào backend
          memberSince: user.dateJoined || '',
          avatar: user.avatarUrl || ''
        });
      } else {
        // Fallback: Lấy thông tin từ localStorage
        const currentUser = authService.getCurrentUser();
        if (currentUser) {
          setUserInfo({
            name: currentUser.fullName || currentUser.username || 'Người dùng',
            email: currentUser.email || '',
            phone: currentUser.phone || '',
            address: '',
            birthday: '',
            gender: 'male',
            memberSince: currentUser.dateJoined || '',
            avatar: currentUser.avatarUrl || ''
          });
        }
      }
    } catch (error) {
      console.error('Error loading user profile:', error);
      // Fallback: Lấy thông tin từ localStorage
      const currentUser = authService.getCurrentUser();
      if (currentUser) {
        setUserInfo({
          name: currentUser.fullName || currentUser.username || 'Người dùng',
          email: currentUser.email || '',
          phone: currentUser.phone || '',
          address: '',
          birthday: '',
          gender: 'male',
          memberSince: currentUser.dateJoined || '',
          avatar: currentUser.avatarUrl || ''
        });
      }
    } finally {
      setLoading(false);
    }
  };
  const [editingAddress, setEditingAddress] = useState<Address | null>(null);
  const [orderTab, setOrderTab] = useState('all');
  const [formPosition, setFormPosition] = useState<'top' | 'bottom' | null>(null);
  const [showTrackingModal, setShowTrackingModal] = useState(false);
  const [selectedOrderTracking, setSelectedOrderTracking] = useState<string | null>(null);
  const [voucherTab, setVoucherTab] = useState('available');
  
  // Use real Address API
  const { 
    addresses, 
    loading: addressLoading, 
    addAddress, 
    updateAddress, 
    deleteAddress, 
    setDefaultAddress 
  } = useAddresses();
  
  // Address form state
  const [provinces, setProvinces] = useState<any[]>([]);
  const [wards, setWards] = useState<any[]>([]);
  const [hamlets, setHamlets] = useState<any[]>([]);
  const [loadingWards, setLoadingWards] = useState(false);
  const [loadingHamlets, setLoadingHamlets] = useState(false);

  const [newAddress, setNewAddress] = useState({
    name: '',
    phoneNumber: '',
    province: '',
    provinceId: '',
    ward: '',
    wardId: '',
    hamlet: '',
    hamletId: '',
    detail: ''
  });
  
  // Load provinces on mount
  useEffect(() => {
    const loadProvinces = async () => {
      try {
        const data = await getProvinces();
        if (data && data.length > 0) {
          setProvinces(data);
        } else {
          console.warn('No provinces data returned');
          setProvinces([]);
        }
      } catch (err) {
        console.error('Failed to load provinces:', err);
        setProvinces([]);
      }
    };
    loadProvinces();
  }, []);
  
  // Load wards when province changes
  useEffect(() => {
    const loadWards = async () => {
      if (newAddress.provinceId) {
        console.warn('❤️❤️❤️❤️❤️❤️',newAddress);
        setLoadingWards(true);
        try {
          const provinceIdNum = parseInt(newAddress.provinceId, 10);
          const data = await getWards(provinceIdNum);
          setWards(data || []);
        } catch (err) {
          console.error('Failed to load wards:', err);
          setWards([]);
        } finally {
          setLoadingWards(false);
        }
      } else {
        setWards([]);
      }
      setHamlets([]);
    };
    loadWards();
  }, [newAddress.provinceId]);
  
  // Load hamlets when ward changes
  // Load hamlets when ward changes
  useEffect(() => {
    const loadHamlets = async () => {
      // Reset hamlet khi đổi ward
      setNewAddress(prev => ({ ...prev, hamlet: '' }));
      
      // Chỉ load khi có đủ province VÀ ward (không rỗng)
      if (newAddress.province && newAddress.ward && newAddress.province.trim() && newAddress.ward.trim()) {
        setLoadingHamlets(true);
        try {
          const hamlets = await getHamlets(newAddress.province, newAddress.ward);
          setHamlets(hamlets || []);
        } catch (err) {
          console.warn('Error loading hamlets:', err);
          setHamlets([]);
        } finally {
          setLoadingHamlets(false);
        }
      } else {
        setHamlets([]);
        setLoadingHamlets(false);
      }
    };
    loadHamlets();
  }, [newAddress.ward]); // Chỉ depend vào ward

  // Orders loaded from backend via GraphQL
  const { getMyOrders, loading: ordersLoading, error: ordersError, data: ordersData } = useMyOrders();
  const { cancelOrder, loading: cancellingOrder } = useCancelOrder();
  const { cancelSubOrder, loading: cancellingSubOrder } = useCancelSubOrder();
  const [orders, setOrders] = useState<any[]>([]);

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        const res = await getMyOrders();
        const payload = res?.data?.myOrders ?? res?.data?.my_orders ?? ordersData ?? [];
        if (mounted && Array.isArray(payload)) setOrders(payload);
      } catch (err) {
        console.warn('Failed to load orders', err);
      }
    };
    load();
    return () => { mounted = false; };
  }, [getMyOrders]);

  // Mock voucher data mapping với backend
  const userVouchers: Voucher[] = [
    {
      voucher_id: 1,
      code: 'WELCOME10',
      type: 'platform',
      discount_type: 'percent',
      discount_value: 10,
      min_order_amount: 500000,
      max_discount: 100000,
      start_date: '2024-11-01',
      end_date: '2024-12-31',
      per_user_limit: 1,
      is_active: true,
      is_auto: false,
      description: 'Voucher chào mừng thành viên mới',
      saved_at: '2024-11-10T09:00:00Z',
      used_count: 0,
      can_use: true
    },
    {
      voucher_id: 2,
      code: 'SHOEX50K',
      type: 'seller',
      seller: {
        id: 1,
        name: 'SHOEX Official Store',
        logo: '/api/placeholder/32/32'
      },
      discount_type: 'fixed',
      discount_value: 50000,
      min_order_amount: 1000000,
      start_date: '2024-11-01',
      end_date: '2024-11-30',
      per_user_limit: 2,
      is_active: true,
      is_auto: false,
      description: 'Giảm 50K cho đơn hàng từ 1 triệu',
      saved_at: '2024-11-12T14:30:00Z',
      used_count: 1,
      can_use: true
    },
    {
      voucher_id: 3,
      code: 'FREESHIP',
      type: 'platform',
      discount_type: 'fixed',
      discount_value: 25000,
      min_order_amount: 300000,
      start_date: '2024-11-15',
      end_date: '2024-11-20',
      per_user_limit: 1,
      is_active: true,
      is_auto: false,
      description: 'Miễn phí vận chuyển cho đơn từ 300K',
      saved_at: '2024-11-15T10:00:00Z',
      used_count: 1,
      can_use: false
    },
    {
      voucher_id: 4,
      code: 'EXPIRED20',
      type: 'platform',
      discount_type: 'percent',
      discount_value: 20,
      min_order_amount: 800000,
      max_discount: 200000,
      start_date: '2024-10-01',
      end_date: '2024-10-31',
      per_user_limit: 1,
      is_active: false,
      is_auto: false,
      description: 'Voucher đã hết hạn',
      saved_at: '2024-10-15T08:00:00Z',
      used_count: 0,
      can_use: false
    }
  ];

  // Local state for saved vouchers (will be loaded from backend)
  const [savedVouchers, setSavedVouchers] = useState<Voucher[]>([]);

  // Hook to save a voucher
  const { saveVoucher, saving: savingVoucher, error: saveVoucherError } = useSaveVoucher();

  // VNPay link creation hook
  const { createVnpayLink, loading: creatingVnpay, error: createVnpayError } = useCreateVnPayLink();

  const [voucherToSaveCode, setVoucherToSaveCode] = useState<string>('');

  // Load saved vouchers from backend (hook)
  const { savedVouchers: fetchedUserVouchers, loading: loadingSavedVouchers, error: savedVouchersError, refetch: refetchSavedVouchers } = useSavedVouchers();

  // Map backend saved vouchers into UI shape when fetched
  useEffect(() => {
    if (Array.isArray(fetchedUserVouchers) && fetchedUserVouchers.length > 0) {
      const mapped = (fetchedUserVouchers as any[]).map((uv: any) => {
        const v = uv.voucher || {};
        const usedCount = Number(uv.usedCount ?? uv.used_count ?? 0);
        const perUserLimit = Number(v.perUserLimit ?? v.per_user_limit ?? 1);
        const isActive = v.isActive ?? true;
        const endDate = v.endDate || v.end_date || '';
        const notExpired = !endDate || new Date(endDate) > new Date();
        const canUse = usedCount < perUserLimit && isActive && notExpired;

        return {
          voucher_id: Number(v.voucherId || v.voucher_id || Date.now()),
          code: v.code || '',
          type: v.seller ? 'seller' : 'platform',
          seller: v.seller ? { id: v.seller.id, name: v.seller.name, logo: v.seller.logo } : undefined,
          discount_type: (v.discountType || v.discount_type || 'PERCENT').toString().toLowerCase() === 'percent' ? 'percent' : 'fixed',
          discount_value: Number(v.discountValue || v.discount_value || 0),
          min_order_amount: Number(v.minOrderAmount || v.min_order_amount || 0),
          max_discount: v.maxDiscount || v.max_discount,
          start_date: v.startDate || v.start_date || '',
          end_date: v.endDate || v.end_date || '',
          per_user_limit: perUserLimit,
          is_active: isActive,
          description: v.description || '',
          saved_at: uv.savedAt || uv.saved_at || new Date().toISOString(),
          used_count: usedCount,
          can_use: canUse
        } as Voucher;
      });

      setSavedVouchers(mapped);
    } else {
      // fallback to demo mock
      setSavedVouchers(userVouchers);
    }
  }, [fetchedUserVouchers]);

  const handleSaveVoucher = async (voucherCode: string) => {
    if (!voucherCode) return alert('Vui lòng nhập mã voucher để lưu');
    try {
      const res: any = await saveVoucher(undefined, voucherCode);
      if (res?.ok) {
        const uv: any = res.userVoucher || {};
        const v: any = uv.voucher || {};
        const usedCount = Number(uv.usedCount ?? uv.used_count ?? 0);
        const perUserLimit = Number(v.perUserLimit ?? v.per_user_limit ?? 1);
        const isActive = v.isActive ?? true;
        const endDate = v.endDate || v.end_date || '';
        const notExpired = !endDate || new Date(endDate) > new Date();
        const canUse = usedCount < perUserLimit && isActive && notExpired;

        const mapped = {
          voucher_id: Number(v.voucherId || v.voucher_id || Date.now()),
          code: v.code || '',
          type: v.seller ? 'seller' : 'platform',
          seller: v.seller ? { id: v.seller.id, name: v.seller.name, logo: v.seller.logo } : undefined,
          discount_type: (v.discountType || v.discount_type || 'PERCENT').toString().toLowerCase() === 'percent' ? 'percent' : 'fixed',
          discount_value: Number(v.discountValue || v.discount_value || 0),
          min_order_amount: Number(v.minOrderAmount || v.min_order_amount || 0),
          max_discount: v.maxDiscount || v.max_discount,
          start_date: v.startDate || v.start_date || '',
          end_date: v.endDate || v.end_date || '',
          per_user_limit: perUserLimit,
          is_active: isActive,
          description: v.description || '',
          saved_at: uv.savedAt || uv.saved_at || new Date().toISOString(),
          used_count: usedCount,
          can_use: canUse
        } as Voucher;

        setSavedVouchers(prev => [mapped, ...prev]);
        setVoucherToSaveCode('');
        alert('Lưu voucher thành công');
      } else {
        alert(res?.message || 'Lưu voucher thất bại');
      }
    } catch (err: any) {
      console.error('handleSaveVoucher error', err);
      alert(err?.message || 'Lỗi khi lưu voucher');
    }
  };

  const stats = {
    totalOrders: 15,
    totalSpent: 12500000,
    savedItems: 8,
    loyaltyPoints: 2450
  };

  // Map backend payment/shipment statuses to UI statuses used in this page
  const getOrderStatus = (order: any) => {
    // Prefer shipment statuses derived from subOrders.shipment.status when available.
    // If no shipment exists, fall back to payment status (only PENDING means waiting for payment).
    const payStatus = (order?.payment?.status || order?.payment_status || '').toString().toUpperCase();

    // Collect shipment statuses from subOrders (if any)
    const shipStatuses: string[] = [];
    if (Array.isArray(order?.subOrders)) {
      order.subOrders.forEach((s: any) => {
        const st = (s?.shipment?.status || s?.shipment_status || '').toString();
        if (st) shipStatuses.push(st.toUpperCase());
      });
    }

    if (shipStatuses.length > 0) {
      // priority: RETURNED -> CANCELLED -> OUT_FOR_DELIVERY -> SHIPPING -> PENDING -> COMPLETED
      if (shipStatuses.includes('RETURNED')) return 'refund';
      if (shipStatuses.includes('CANCELLED')) return 'cancelled';
      if (shipStatuses.includes('OUT_FOR_DELIVERY')) return 'delivering';
      if (shipStatuses.includes('SHIPPING')) return 'shipping';
      if (shipStatuses.includes('PENDING')) return 'pending';
      if (shipStatuses.includes('COMPLETED') || shipStatuses.includes('DELIVERED') || shipStatuses.includes('DELIVERED_SUCCESS') || shipStatuses.includes('IN_TRANSIT')) return 'completed';
      // fallback to the first available shipment status
      return shipStatuses[0].toLowerCase();
    }

    // No shipments: use payment status mapping (only PENDING means waiting for payment)
    if (payStatus === 'PENDING') return 'pending';
    if (payStatus === 'FAILED' || payStatus === 'CANCELLED') return 'cancelled';
    if (payStatus === 'REFUNDED') return 'refund';
    if (payStatus === 'COMPLETED') return 'completed';

    // Fallback: use raw order.status or pending
    const raw = (order?.status || '').toString().toLowerCase();
    return raw || 'pending';
  };

  // Order management functions
  const ordersWithUiStatus = orders.map(o => ({ ...o, uiStatus: getOrderStatus(o) }));

  const orderTabs = [
    { id: 'all', label: 'Tất cả', count: ordersWithUiStatus.length },
    { id: 'pending', label: 'Chờ xác nhận', count: ordersWithUiStatus.filter(o => o.uiStatus === 'pending').length },
    { id: 'shipping', label: 'Vận chuyển', count: ordersWithUiStatus.filter(o => o.uiStatus === 'shipping').length },
    { id: 'delivering', label: 'Chờ giao hàng', count: ordersWithUiStatus.filter(o => o.uiStatus === 'delivering').length },
    { id: 'completed', label: 'Hoàn thành', count: ordersWithUiStatus.filter(o => o.uiStatus === 'completed').length },
    { id: 'cancelled', label: 'Đã hủy', count: ordersWithUiStatus.filter(o => o.uiStatus === 'cancelled').length },
    { id: 'refund', label: 'Trả hàng/Hoàn tiền', count: ordersWithUiStatus.filter(o => o.uiStatus === 'refund').length }
  ];

  const filteredOrders = orderTab === 'all'
    ? ordersWithUiStatus
    : ordersWithUiStatus.filter(order => order.uiStatus === orderTab);

  // Dữ liệu tracking cho đơn hàng
  const trackingData: { [key: string]: any } = {
    'ORD005': {
      currentStatus: 'Chờ giao hàng',
      estimatedDelivery: '2024-11-16 14:00',
      carrier: 'Giao Hàng Nhanh',
      trackingNumber: 'GHN123456789',
      timeline: [
        {
          id: 5,
          status: 'Giao thành công',
          location: 'Địa chỉ nhận hàng',
          time: 'Dự kiến 2024-11-16 14:00',
          description: 'Hàng sẽ được giao đến tay người nhận',
          completed: false,
          needsConfirmation: true,
          deliveryProof: {
            receiverName: 'Nguyễn Văn A',
            receiverPhone: '0901234567',
            deliveryImages: [
              '/api/placeholder/300/200?text=H%C3%ACnh+giao+h%C3%A0ng+1',
              '/api/placeholder/300/200?text=H%C3%ACnh+x%C3%A1c+nh%E1%BA%ADn+2'
            ],
            signature: '/api/placeholder/200/100?text=Ch%E1%BB%AF+k%C3%BD',
            note: 'Hàng đã được giao thành công. Vui lòng xác nhận đã nhận hàng.'
          }
        },
        {
          id: 4,
          status: 'Đang giao hàng',
          location: 'Đang trên đường giao',
          time: 'Dự kiến 2024-11-15 16:00',
          description: 'Shipper đang trên đường giao hàng đến bạn',
          completed: true,
          current: true,
          detailedRoute: [
            {
              location: 'Địa chỉ giao hàng - 123 Lê Lợi, Q.1',
              time: 'Dự kiến 2024-11-16 14:00',
              status: 'Sắp tới',
              description: 'Shipper sẽ giao hàng đến địa chỉ của bạn'
            },
            {
              location: 'Đang di chuyển trên đường Nguyễn Huệ',
              time: '2024-11-15 15:30',
              status: 'Hiện tại',
              description: 'Shipper đang di chuyển và sẽ liên hệ với bạn trước khi đến'
            },
            {
              location: 'Xuất phát từ Hub GHN Quận 7',
              time: '2024-11-15 14:45',
              status: 'Đã qua',
              description: 'Shipper đã nhận hàng và bắt đầu quá trình giao hàng'
            },
            {
              location: 'Chuẩn bị giao hàng tại Hub',
              time: '2024-11-15 14:20',
              status: 'Đã qua',
              description: 'Hàng đã được chuẩn bị và phân công cho shipper'
            }
          ]
        },
        {
          id: 3,
          status: 'Đang vận chuyển',
          location: 'Trung tâm phân loại - TP.HCM',
          time: '2024-11-14 08:20',
          description: 'Hàng đã hoàn thành vận chuyển',
          completed: true
        },
        {
          id: 2,
          status: 'Đã giao cho đơn vị vận chuyển',
          location: 'Kho SHOEX Official Store - Quận 1',
          time: '2024-11-13 15:45',
          description: 'Hàng đã được chuyển đến kho vận chuyển',
          completed: true
        },
        {
          id: 1,
          status: 'Đã xác nhận đơn hàng',
          location: 'SHOEX Official Store - TP.HCM',
          time: '2024-11-13 09:30',
          description: 'Đơn hàng đã được xác nhận và chuẩn bị hàng',
          completed: true
        }
      ]
    },
    'ORD001': {
      currentStatus: 'Hoàn thành',
      estimatedDelivery: '2024-11-10 15:30',
      carrier: 'Giao Hàng Nhanh',
      trackingNumber: 'GHN987654321',
      timeline: [
        {
          id: 5,
          status: 'Giao thành công',
          location: 'Địa chỉ nhận hàng - 123 Lê Lợi, Q.1',
          time: '2024-11-10 15:30',
          description: 'Hàng đã được giao thành công và khách hàng đã xác nhận nhận hàng',
          completed: true,
          current: false
        },
        {
          id: 4,
          status: 'Đang giao hàng',
          location: 'Shipper đang giao hàng',
          time: '2024-11-10 14:45',
          description: 'Shipper đã liên hệ và đang trên đường giao hàng',
          completed: true
        },
        {
          id: 3,
          status: 'Đang vận chuyển',
          location: 'Trung tâm phân loại - TP.HCM',
          time: '2024-11-09 16:20',
          description: 'Hàng đã hoàn thành vận chuyển',
          completed: true
        },
        {
          id: 2,
          status: 'Đã giao cho đơn vị vận chuyển',
          location: 'Kho SHOEX Official Store - Quận 1',
          time: '2024-11-08 10:15',
          description: 'Hàng đã được chuyển đến đơn vị vận chuyển',
          completed: true
        },
        {
          id: 1,
          status: 'Đã xác nhận đơn hàng',
          location: 'SHOEX Official Store - TP.HCM',
          time: '2024-11-08 09:00',
          description: 'Đơn hàng đã được xác nhận và chuẩn bị hàng',
          completed: true
        }
      ]
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(price);
  };

  // Avatar upload handler
  const handleAvatarUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      try {
        setLoading(true);
        
        // Validate file size (5MB max)
        if (file.size > 5 * 1024 * 1024) {
          alert('Kích thước file không được vượt quá 5MB!');
          return;
        }
        
        // Validate file type
        if (!file.type.startsWith('image/')) {
          alert('Vui lòng chọn file hình ảnh!');
          return;
        }
        
        const response = await authService.uploadAvatar(file);
        
        if (response.success) {
          // Update local state immediately for better UX
          setUserInfo({
            ...userInfo,
            avatar: response.avatarUrl || ''
          });
          alert('Tải lên avatar thành công!');
          // Reload user profile to get updated data
          await loadUserProfile();
        } else {
          alert(`Tải lên thất bại: ${response.message}`);
        }
      } catch (error) {
        console.error('Error uploading avatar:', error);
        alert('Có lỗi xảy ra khi tải lên avatar!');
      } finally {
        setLoading(false);
      }
    }
  };

  // Avatar delete handler
  const handleAvatarDelete = async () => {
    if (!userInfo.avatar) {
      alert('Không có avatar để xóa!');
      return;
    }

    if (confirm('Bạn có chắc chắn muốn xóa avatar?')) {
      try {
        setLoading(true);
        
        const response = await authService.deleteAvatar();
        
        if (response.success) {
          // Update local state immediately for better UX
          setUserInfo({
            ...userInfo,
            avatar: ''
          });
          alert('Xóa avatar thành công!');
          // Reload user profile to get updated data
          await loadUserProfile();
        } else {
          alert(`Xóa avatar thất bại: ${response.message}`);
        }
      } catch (error) {
        console.error('Error deleting avatar:', error);
        alert('Có lỗi xảy ra khi xóa avatar!');
      } finally {
        setLoading(false);
      }
    }
  };

  // Address management functions
  const handleAddAddress = async () => {
    // Validation: Kiểm tra các field bắt buộc
    if (!newAddress.name || !newAddress.phoneNumber || !newAddress.province || !newAddress.ward || !newAddress.detail) {
      alert('Vui lòng điền đầy đủ thông tin bắt buộc (Tên, SĐT, Tỉnh, Phường, Địa chỉ)!');
      return;
    }
    
    const result = await addAddress({
      name: newAddress.name,
      phoneNumber: newAddress.phoneNumber,
      province: newAddress.province,
      ward: newAddress.ward,
      hamlet: newAddress.hamlet || '',
      detail: newAddress.detail,
      isDefault: addresses.length === 0
    });
    
    if (result.success) {
      setNewAddress({ name: '', phoneNumber: '', province: '', provinceId: '', ward: '', wardId: '', hamlet: '',hamletId:'', detail: '' });
      setShowAddressForm(false);
      setFormPosition(null);
      setWards([]);
      setHamlets([]);
      alert('Thêm địa chỉ thành công!');
    } else {
      alert(result.errors?.join(', ') || 'Lỗi khi thêm địa chỉ');
    }
  };

  const handleEditAddress = async (address: Address) => {
    setEditingAddress(address);
    
    // Tìm provinceId từ tên tỉnh
    const foundProvince = provinces.find(p => p.name === address.province);
    console.warn('🏵️🏵️🏵️🏵️🏵️ Found province for edit:', foundProvince);
    console.warn('🏵️🏵️🏵️🏵️🏵️ Address to edit:', address);
    
    // Load wards ngay khi có provinceId
    let loadedWards: any[] = [];
    let foundWardId = '';
    if (foundProvince?.code) {
      setLoadingWards(true);
      try {
        const wardsData = await getWards(foundProvince.code);
        if (wardsData && wardsData.length > 0) {
          loadedWards = wardsData;
          setWards(wardsData);
          // Tìm wardId từ tên ward
          const foundWard = wardsData.find((w: any) => w.name === address.ward);
          if (foundWard) {
            foundWardId = foundWard.code.toString();
            console.warn('🏵️ Found ward for edit:', foundWard);
          }
        }
      } catch (err) {
        console.error('Failed to load wards for edit:', err);
      } finally {
        setLoadingWards(false);
      }
    }
    
    // Load hamlets ngay khi có province và ward
    let foundHamletId = '';
    if (address.province && address.ward && address.province.trim() && address.ward.trim()) {
      setLoadingHamlets(true);
      try {
        const hamletsData = await getHamlets(address.province, address.ward);
        if (hamletsData && hamletsData.length > 0) {
          setHamlets(hamletsData);
          // Tìm hamletId/index từ tên hamlet
          const hamletIndex = hamletsData.findIndex((h: any) => {
            const hamletName = h.name || h;
            return hamletName === address.hamlet;
          });
          if (hamletIndex !== -1) {
            foundHamletId = hamletIndex.toString();
            console.warn('🏵️ Found hamlet for edit:', address.hamlet, 'at index:', hamletIndex);
          }
        }
      } catch (err) {
        console.error('Failed to load hamlets for edit:', err);
      } finally {
        setLoadingHamlets(false);
      }
    }
    
    // Set state với đầy đủ thông tin bao gồm wardId và hamletId
    setNewAddress({
      name: address.name,
      phoneNumber: address.phoneNumber || '',
      province: address.province,
      provinceId: foundProvince?.code?.toString() || '',
      ward: address.ward,
      wardId: foundWardId,
      hamlet: address.hamlet || '',
      hamletId: foundHamletId,
      detail: address.detail
    });
    
    setShowAddressForm(true);
    setFormPosition('bottom');
  };

  const handleUpdateAddress = async () => {
    if (editingAddress && newAddress.name && newAddress.phoneNumber && newAddress.province && newAddress.ward && newAddress.detail) {
      const result = await updateAddress({
        addressId: editingAddress.addressId,
        name: newAddress.name,
        phoneNumber: newAddress.phoneNumber,
        province: newAddress.province,
        ward: newAddress.ward,
        hamlet: newAddress.hamlet,
        detail: newAddress.detail
      });
      
      if (result.success) {
        setEditingAddress(null);
        setNewAddress({ name: '', phoneNumber: '', province: '', provinceId: '', ward: '', wardId: '', hamlet: '',hamletId: '', detail: '' });
        setShowAddressForm(false);
        setFormPosition(null);
        alert('Cập nhật địa chỉ thành công!');
      } else {
        alert(result.errors?.join(', ') || 'Lỗi khi cập nhật địa chỉ');
      }
    } else {
      alert('Vui lòng điền đầy đủ thông tin!');
    }
  };

  const handleCancelForm = () => {
    setShowAddressForm(false);
    setEditingAddress(null);
    setNewAddress({ name: '', phoneNumber: '', province: '', provinceId: '', ward: '', wardId: '', hamlet: '',hamletId: '', detail: '' });
    setFormPosition(null);
  };

  const handleShowTracking = (orderId: string) => {
    setSelectedOrderTracking(orderId);
    setShowTrackingModal(true);
  };

  const handleCloseTracking = () => {
    setShowTrackingModal(false);
    setSelectedOrderTracking(null);
  };

  const handleConfirmDelivery = (orderId: string) => {
    // Cập nhật trạng thái đơn hàng thành completed
    alert('Xác nhận nhận hàng thành công! Đơn hàng đã hoàn thành.');
    setShowTrackingModal(false);
    setSelectedOrderTracking(null);
    // Thực tế sẽ cập nhật database và refresh data
  };

  const handleDeleteAddress = async (addressId: string) => {
    if (confirm('Bạn có chắc muốn xóa địa chỉ này?')) {
      const result = await deleteAddress(addressId);
      if (result.success) {
        alert('Xóa địa chỉ thành công!');
      } else {
        alert(result.errors?.join(', ') || 'Lỗi khi xóa địa chỉ');
      }
    }
  };

  const handleSetDefaultAddress = async (addressId: string) => {
    const result = await setDefaultAddress(addressId);
    if (result.success) {
      alert('Đã đặt làm địa chỉ mặc định!');
    } else {
      alert(result.errors?.join(', ') || 'Lỗi khi đặt địa chỉ mặc định');
    }
  };

  const tabs = [
    { id: 'profile', label: 'Thông tin cá nhân', icon: User },
    { id: 'orders', label: 'Đơn hàng', icon: ShoppingBag },
    { id: 'addresses', label: 'Địa chỉ', icon: MapPin },
    { id: 'vouchers', label: 'Voucher', icon: Ticket },
    { id: 'settings', label: 'Cài đặt', icon: Settings }
  ];

  const handleSave = async () => {
    try {
      setLoading(true);
      
      // Parse fullName into firstName and lastName
      const nameParts = userInfo.name.trim().split(' ');
      const firstName = nameParts[0] || '';
      const lastName = nameParts.slice(1).join(' ') || '';
      
      // Format birthDate để đảm bảo format YYYY-MM-DD
      const formatBirthDate = (dateValue: string) => {
        if (!dateValue || !dateValue.trim()) return undefined;
        
        // Nếu đã là format YYYY-MM-DD thì giữ nguyên
        if (/^\d{4}-\d{2}-\d{2}$/.test(dateValue)) {
          return dateValue;
        }
        
        // Nếu là format DD/MM/YYYY, convert thành YYYY-MM-DD
        if (/^\d{2}\/\d{2}\/\d{4}$/.test(dateValue)) {
          const [day, month, year] = dateValue.split('/');
          return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
        }
        
        // Nếu là Date object hoặc các format khác
        try {
          const date = new Date(dateValue);
          if (isNaN(date.getTime())) return undefined;
          return date.toISOString().split('T')[0];
        } catch {
          return undefined;
        }
      };
      
      const birthDate = formatBirthDate(userInfo.birthday);
      
      console.log('📝 Preparing update data:', {
        originalBirthday: userInfo.birthday,
        formattedBirthDate: birthDate,
        fullName: userInfo.name,
        phone: userInfo.phone,
        email: userInfo.email
      });
      
      const updateData = {
        fullName: userInfo.name,
        firstName: firstName,
        lastName: lastName,
        phone: userInfo.phone,
        email: userInfo.email,
        ...(birthDate && { birthDate: birthDate }) // Chỉ thêm nếu có giá trị
      };
      
      console.log('📤 Final updateData being sent:', updateData);
      
      const response = await authService.updateUserProfile(updateData);
      
      if (response.success) {
        setIsEditing(false);
        alert('Cập nhật thông tin thành công!');
        // Reload user profile to get updated data
        await loadUserProfile();
      } else {
        alert(`Cập nhật thất bại: ${response.message}`);
      }
    } catch (error) {
      console.error('Error updating user profile:', error);
      alert('Có lỗi xảy ra khi cập nhật thông tin!');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    if (confirm('Bạn có chắc chắn muốn đăng xuất?')) {
      onNavigate?.('home');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'shipping': return 'text-blue-600 bg-blue-100';
      case 'delivering': return 'text-purple-600 bg-purple-100';
      case 'pending': return 'text-orange-600 bg-orange-100';
      case 'cancelled': return 'text-red-600 bg-red-100';
      case 'refund': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  // TrackingModal component
  const TrackingModal = ({ orderId }: { orderId: string }) => {
    // Try to build tracking info from real order data (subOrder.shipment.trackings)
    const order = orders.find(o => o.orderId === orderId);

    let tracking: any = null;

    if (order) {
      // Collect all trackings from subOrders
      const rawTrackings: any[] = (order.subOrders || []).flatMap((s: any) => (s.shipment && Array.isArray(s.shipment.trackings)) ? s.shipment.trackings : []);

      if (rawTrackings.length > 0) {
        // Sort by eventTime descending (latest first)
        rawTrackings.sort((a: any, b: any) => {
          const ta = new Date(a.eventTime || a.timestamp || a.time || 0).getTime();
          const tb = new Date(b.eventTime || b.timestamp || b.time || 0).getTime();
          return tb - ta;
        });

        const latest = rawTrackings[0];
        tracking = {
          currentStatus: latest.carrierStatusText || latest.status || order.subOrders?.[0]?.shipment?.status || 'Đang vận chuyển',
          estimatedDelivery: latest.estimatedDeliverTime || latest.estimatedDeliverAt || order.subOrders?.[0]?.shipment?.estimatedDeliverTime || '',
          carrier: order.subOrders?.[0]?.shipment?.carrier || 'Đơn vị vận chuyển',
          trackingNumber: order.subOrders?.[0]?.shipment?.trackingCode || '',
          // syncedAt: time when tracking was last synced from carrier (prefer per-tracking event, then per-shipment)
          syncedAt: latest.syncedAt || latest.synced_at || order.subOrders?.[0]?.shipment?.syncedAt || order.subOrders?.[0]?.shipment?.synced_at || '',
          timeline: rawTrackings.map((t: any, idx: number) => ({
            id: idx + 1,
            status: t.carrierStatusText || t.status || '...',
            location: t.location || t.place || '',
            time: t.eventTime || t.timestamp || t.time || '',
            description: t.description || t.note || '',
            completed: (t.status || '').toString().toUpperCase() === 'COMPLETED' || /giao thành công|delivered/i.test((t.carrierStatusText || '') as string),
            current: idx === 0,
            syncedAt: t.syncedAt || t.synced_at || ''
          }))
        };
      }
    }

    // Fallback to mock trackingData if no real tracking found
    if (!tracking) {
      tracking = trackingData[orderId];
    }

    if (!tracking) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-xl font-bold mb-2">Chi tiết vận chuyển</h3>
                <p className="text-blue-100">Đơn hàng #{orderId}</p>
                <p className="text-sm text-blue-100">Mã vận đơn: {tracking.trackingNumber}</p>
                {/* Removed header syncedAt to avoid confusion with per-event timestamps */}
              </div>
              <button
                onClick={handleCloseTracking}
                className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white bg-opacity-20 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-1">
                  <Truck className="h-4 w-4" />
                  <span className="text-sm font-medium">Đơn vị vận chuyển</span>
                </div>
                <p className="text-white font-semibold">{tracking.carrier}</p>
              </div>
              <div className="bg-white bg-opacity-20 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-1">
                  <Clock className="h-4 w-4" />
                  <span className="text-sm font-medium">Dự kiến giao hàng</span>
                </div>
                <p className="text-white font-semibold">{tracking.estimatedDelivery}</p>
              </div>
            </div>
          </div>

          {/* Timeline */}
          <div className="p-6 overflow-y-auto max-h-96">
            <div className="space-y-4">
              {tracking.timeline.map((step: any, index: number) => (
                <div key={step.id} className="relative">
                  {/* Connector Line */}
                  {index > 0 && (
                    <div className={`absolute left-4 top-0 w-0.5 h-4 ${
                      tracking.timeline[index - 1].completed ? 'bg-green-300' : 'bg-gray-200'
                    }`} />
                  )}
                  
                  <div className="flex items-start gap-4">
                    {/* Status Icon */}
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                      step.current 
                        ? 'bg-blue-500 text-white animate-pulse' 
                        : step.completed 
                        ? 'bg-green-500 text-white' 
                        : 'bg-gray-200 text-gray-400'
                    }`}>
                      {step.completed ? (
                        <CheckCircle className="h-4 w-4" />
                      ) : step.current ? (
                        <Truck className="h-4 w-4" />
                      ) : (
                        <Package className="h-4 w-4" />
                      )}
                    </div>
                    
                    {/* Content */}
                    <div className="flex-1 pb-4">
                      <div className="bg-gray-50 rounded-lg p-4">
                        <div className="flex justify-between items-start mb-2">
                          <h4 className={`font-semibold ${
                            step.current ? 'text-blue-600' : step.completed ? 'text-green-600' : 'text-gray-600'
                          }`}>
                            {step.status}
                            {step.current && (
                              <span className="ml-2 bg-blue-100 text-blue-600 text-xs px-2 py-1 rounded-full">
                                Hiện tại
                              </span>
                            )}
                          </h4>
                          <span className={`text-sm ${
                            step.completed || step.current ? 'text-gray-700' : 'text-gray-400'
                          }`}>
                            {(() => {
                              // Prefer syncedAt (carrier sync time) then event time
                              const rawTime = step.syncedAt || step.time || '';
                              let timeStr = '';
                              if (rawTime) {
                                try {
                                  const d = new Date(rawTime);
                                  if (!isNaN(d.getTime())) timeStr = d.toLocaleString();
                                  else timeStr = rawTime;
                                } catch {
                                  timeStr = rawTime;
                                }
                              }
                              const statusText = (step.status || '').toString();
                              return timeStr ? `${timeStr} - ${statusText}` : statusText;
                            })()}
                          </span>
                        </div>
                        
                        <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                          <MapPinIcon className="h-4 w-4" />
                          <span>{step.location}</span>
                        </div>
                        
                        <p className={`text-sm ${
                          step.completed || step.current ? 'text-gray-700' : 'text-gray-400'
                        }`}>
                          {step.description}
                        </p>
                        
                        {/* Detailed Route for shipping status */}
                        {step.detailedRoute && (
                          <div className="mt-4 border-l-2 border-blue-200 pl-4">
                            <h5 className="text-sm font-semibold text-blue-600 mb-3 flex items-center">
                              <MapPinIcon className="h-4 w-4 mr-1" />
                              Chi tiết lộ trình vận chuyển
                            </h5>
                            <div className="space-y-3">
                              {step.detailedRoute.map((route: any, routeIndex: number) => (
                                <div key={routeIndex} className="relative">
                                  {routeIndex > 0 && (
                                    <div className="absolute left-3 top-0 w-0.5 h-4 bg-blue-200" />
                                  )}
                                  
                                  <div className="flex items-start gap-3">
                                    <div className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                                      route.status === 'Hiện tại'
                                        ? 'bg-blue-500 text-white animate-pulse'
                                        : route.status === 'Đã qua'
                                        ? 'bg-green-400 text-white'
                                        : 'bg-gray-300 text-gray-600'
                                    }`}>
                                      {route.status === 'Đã qua' ? '✓' : route.status === 'Hiện tại' ? '●' : '○'}
                                    </div>
                                    
                                    <div className="flex-1">
                                      <div className="flex justify-between items-start">
                                        <h6 className={`text-sm font-medium ${
                                          route.status === 'Hiện tại' ? 'text-blue-600' :
                                          route.status === 'Đã qua' ? 'text-green-600' : 'text-gray-500'
                                        }`}>
                                          {route.location}
                                          {route.status === 'Hiện tại' && (
                                            <span className="ml-2 bg-blue-100 text-blue-600 text-xs px-1.5 py-0.5 rounded">
                                              Hiện tại
                                            </span>
                                          )}
                                        </h6>
                                        <span className={`text-xs ${
                                          route.status === 'Sắp tới' ? 'text-gray-400' : 'text-gray-600'
                                        }`}>
                                          {route.time}
                                        </span>
                                      </div>
                                      <p className={`text-xs mt-1 ${
                                        route.status === 'Sắp tới' ? 'text-gray-400' : 'text-gray-600'
                                      }`}>
                                        {route.description}
                                      </p>
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {/* Delivery Proof for completed orders */}
                        {step.deliveryProof && (
                          <div className="mt-4 border border-green-200 rounded-lg p-4 bg-green-50">
                            <h5 className="text-sm font-semibold text-green-700 mb-3 flex items-center">
                              <CheckCircle className="h-4 w-4 mr-1" />
                              {step.needsConfirmation ? 'Xác nhận nhận hàng' : 'Xác nhận giao hàng thành công'}
                            </h5>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              {/* Receiver Info */}
                              <div>
                                <div className="mb-3">
                                  <p className="text-sm text-green-700">
                                    <strong>Người nhận:</strong> {step.deliveryProof.receiverName}
                                  </p>
                                  <p className="text-sm text-green-700">
                                    <strong>SĐT:</strong> {step.deliveryProof.receiverPhone}
                                  </p>
                                </div>
                                
                                {step.deliveryProof.note && (
                                  <div className="bg-white rounded-lg p-3">
                                    <p className="text-xs text-gray-600 mb-1"><strong>Ghi chú:</strong></p>
                                    <p className="text-sm text-gray-800">{step.deliveryProof.note}</p>
                                  </div>
                                )}
                              </div>
                              
                              {/* Delivery Images */}
                              <div>
                                <p className="text-sm font-medium text-green-700 mb-2">Hình ảnh xác nhận:</p>
                                <div className="grid grid-cols-2 gap-2">
                                  {step.deliveryProof.deliveryImages.map((image: string, imgIndex: number) => (
                                    <div key={imgIndex} className="relative group cursor-pointer">
                                      <img 
                                        src={image} 
                                        alt={`Hình giao hàng ${imgIndex + 1}`}
                                        className="w-full h-20 object-cover rounded border border-green-300 hover:border-green-500 transition-colors"
                                      />
                                      <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-opacity rounded" />
                                    </div>
                                  ))}
                                </div>
                              </div>
                            </div>
                            
                            {/* Signature */}
                            {step.deliveryProof.signature && (
                              <div className="mt-4 pt-3 border-t border-green-200">
                                <p className="text-sm font-medium text-green-700 mb-2">Chữ ký xác nhẫn:</p>
                                <div className="bg-white rounded border border-green-300 p-2 inline-block">
                                  <img 
                                    src={step.deliveryProof.signature}
                                    alt="Chữ ký người nhận" 
                                    className="h-12 w-auto"
                                  />
                                </div>
                              </div>
                            )}
                            
                            {/* Confirmation Button */}
                            {step.needsConfirmation && (
                              <div className="mt-4 pt-3 border-t border-green-200">
                                <div className="flex justify-between items-center">
                                  <p className="text-sm text-green-700">
                                    Vui lòng xác nhận bạn đã nhận hàng thành công
                                  </p>
                                  <button
                                    onClick={() => handleConfirmDelivery(orderId)}
                                    className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
                                  >
                                    <Check className="h-4 w-4" />
                                    Xác nhận nhận hàng
                                  </button>
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Footer */}
          <div className="border-t border-gray-200 p-6">
            <div className="flex justify-between items-center">
              <div className="text-sm text-gray-600">
                <p>Có thắc mắc? Liên hệ hotline: <span className="font-semibold text-blue-600">1900-1234</span></p>
              </div>
              <button
                onClick={handleCloseTracking}
                className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // AddressForm component với API thực - dùng useMemo để tránh re-render
  const AddressForm = useMemo(() => (
    <div className="border border-gray-300 rounded-lg p-6 bg-gray-50">
      <h3 className="font-semibold mb-4">
        {editingAddress ? 'Chỉnh sửa địa chỉ' : 'Thêm địa chỉ mới'}
      </h3>
      <div className="space-y-4">
        {/* Thông tin liên hệ */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Họ và tên *
            </label>
            <input
              type="text"
              value={newAddress.name}
              onChange={(e) => {
                const value = e.target.value;
                setNewAddress(prev => ({...prev, name: value}));
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Nhập họ và tên"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Số điện thoại *
            </label>
            <input
              type="tel"
              value={newAddress.phoneNumber}
              onChange={(e) => {
                const value = e.target.value;
                setNewAddress(prev => ({...prev, phoneNumber: value}));
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Nhập số điện thoại"
            />
          </div>
        </div>
        
        {/* Địa chỉ từ API */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tỉnh/Thành phố *
            </label>
            {provinces.length > 0 ? (
              <select
                value={newAddress.provinceId}
                onChange={(e) => {
                  const selectedProvince = provinces.find(p => p.code === parseInt(e.target.value));
                  const newState = {
                    ...newAddress,
                    provinceId: e.target.value,
                    province: selectedProvince?.name || '',
                    wardId: '',
                    ward: '',
                    hamlet: ''
                  };
                  setNewAddress(newState);
                  // Reset wards và hamlets
                  setWards([]);
                  setHamlets([]);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Chọn Tỉnh/Thành phố</option>
                {provinces.map((province) => (
                  <option key={province.code} value={province.code}>
                    {province.name}
                  </option>
                ))}
              </select>
            ) : (
              <input
                type="text"
                value={newAddress.province}
                onChange={(e) => {
                  const value = e.target.value;
                  setNewAddress(prev => ({...prev, province: value, provinceId: ''}));
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Nhập tên tỉnh/thành phố"
              />
            )}
            {provinces.length === 0 && (
              <p className="text-xs text-red-500 mt-1">Không tải được danh sách tỉnh. Vui lòng nhập thủ công.</p>
            )}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Phường/Xã * {!newAddress.provinceId && !newAddress.province && <span className="text-gray-400 text-xs">(Chọn tỉnh trước)</span>}
              {loadingWards && <span className="text-blue-600 text-xs ml-2">⏳ Đang tải...</span>}
            </label>
            {loadingWards ? (
              <div className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500 flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                Đang tải danh sách phường/xã...
              </div>
            ) : wards.length > 0 && newAddress.provinceId ? (
              <select
                value={newAddress.wardId}
                onChange={(e) => {
                  const selectedWard = wards.find(w => w.code === parseInt(e.target.value));
                  const newState = {
                    ...newAddress,
                    wardId: e.target.value,
                    ward: selectedWard?.name || '',
                    hamlet: ''
                  };
                  setNewAddress(newState);
                  // Reset hamlets sẽ được load lại bởi useEffect
                  setHamlets([]);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Chọn Phường/Xã</option>
                {wards.map((ward) => (
                  <option key={ward.code} value={ward.code}>
                    {ward.name}
                  </option>
                ))}
              </select>
            ) : (
              <input
                type="text"
                value={newAddress.ward}
                onChange={(e) => {
                  const value = e.target.value;
                  setNewAddress(prev => ({...prev, ward: value, wardId: '', hamlet: ''}));
                }}
                className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  (!newAddress.province && !newAddress.provinceId) 
                    ? 'border-gray-200 bg-gray-50 text-gray-400 cursor-not-allowed' 
                    : 'border-gray-300 bg-white'
                }`}
                placeholder={(!newAddress.province && !newAddress.provinceId) ? "Chọn tỉnh trước" : "Nhập tên phường/xã"}
                disabled={!newAddress.province && !newAddress.provinceId}
              />
            )}
            {newAddress.provinceId && wards.length === 0 && !loadingWards && (
              <p className="text-xs text-amber-600 mt-1">Không tải được danh sách. Vui lòng nhập thủ công.</p>
            )}
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Thôn/Khu/Ấp (tùy chọn) {!newAddress.ward && !newAddress.wardId && <span className="text-gray-400 text-xs">(Chọn phường/xã trước)</span>}
            {loadingHamlets && <span className="text-blue-600 text-xs ml-2">⏳ Đang tải...</span>}
          </label>
          {loadingHamlets ? (
            <div className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500 flex items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
              Đang tải danh sách thôn/khu/ấp...
            </div>
          ) : hamlets.length > 0 && (newAddress.ward || newAddress.wardId) ? (
            <select
              value={newAddress.hamlet}
              onChange={(e) => {
                const value = e.target.value;
                setNewAddress(prev => ({...prev, hamlet: value}));
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Chọn Thôn/Khu/Ấp</option>
              {hamlets.map((hamlet: any, index: number) => {
                const hamletName = hamlet.name || hamlet;
                return (
                  <option key={`hamlet-${hamletName}-${index}`} value={hamletName}>
                    {hamletName}
                  </option>
                );
              })}
            </select>
          ) : (
            <input
              type="text"
              value={newAddress.hamlet}
              onChange={(e) => {
                const value = e.target.value;
                setNewAddress(prev => ({...prev, hamlet: value}));
              }}
              className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                (!newAddress.ward && !newAddress.wardId) 
                  ? 'border-gray-200 bg-gray-50 text-gray-400 cursor-not-allowed' 
                  : 'border-gray-300 bg-white'
              }`}
              placeholder={(!newAddress.ward && !newAddress.wardId) ? "Chọn phường/xã trước" : "Nhập thôn/khu/ấp (nếu có)"}
              disabled={!newAddress.ward && !newAddress.wardId}
            />
          )}
          {(newAddress.ward || newAddress.wardId) && hamlets.length === 0 && !loadingHamlets && (
            <p className="text-xs text-gray-500 mt-1">
              Không có dữ liệu thôn/khu/ấp. Bạn có thể nhập thủ công hoặc bỏ qua.
            </p>
          )}
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Địa chỉ chi tiết *
          </label>
          <textarea
            value={newAddress.detail}
            onChange={(e) => {
              const value = e.target.value;
              setNewAddress(prev => ({...prev, detail: value}));
            }}
            rows={2}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Số nhà, tầng, căn hộ, ghi chú thêm..."
          />
        </div>
        
        <div className="flex gap-3">
          <button
            onClick={editingAddress ? handleUpdateAddress : handleAddAddress}
            disabled={addressLoading}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {addressLoading ? 'Đang xử lý...' : (editingAddress ? 'Cập nhật' : 'Thêm địa chỉ')}
          </button>
          <button
            onClick={handleCancelForm}
            className="border border-gray-300 px-6 py-2 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Hủy
          </button>
        </div>
      </div>
    </div>
  ), [editingAddress, loadingWards, loadingHamlets, wards, hamlets, provinces, addressLoading]);

  return (
    <CustomerLayout currentPage="account" onNavigate={onNavigate}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl text-white p-8 mb-8">
          <div className="flex flex-col md:flex-row items-center">
            <div className="relative mb-4 md:mb-0 md:mr-6">
              <div className="w-24 h-24 bg-white bg-opacity-20 rounded-full overflow-hidden">
                {userInfo.avatar ? (
                  <img 
                    src={userInfo.avatar} 
                    alt="Avatar" 
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <User className="h-12 w-12" />
                  </div>
                )}
              </div>
              <label className="absolute -bottom-1 -right-1 w-8 h-8 bg-white text-blue-600 rounded-full flex items-center justify-center cursor-pointer hover:bg-gray-100 transition-colors">
                <Camera className="h-4 w-4" />
                <input 
                  type="file" 
                  accept="image/*" 
                  onChange={handleAvatarUpload}
                  className="hidden"
                />
              </label>
              
              {/* Nút xóa avatar - chỉ hiển thị khi có avatar */}
              {userInfo.avatar && (
                <button
                  onClick={handleAvatarDelete}
                  className="absolute -top-1 -right-1 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center cursor-pointer hover:bg-red-600 transition-colors"
                  title="Xóa avatar"
                >
                  <X className="h-3 w-3" />
                </button>
              )}
            </div>
            
            <div className="text-center md:text-left flex-1">
              <h1 className="text-3xl font-bold mb-2">{userInfo.name || 'Người dùng'}</h1>
              <p className="text-blue-100 mb-4">
                Thành viên từ {userInfo.memberSince ? new Date(userInfo.memberSince).getFullYear() : 'N/A'}
              </p>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold">{stats.totalOrders}</div>
                  <div className="text-sm text-blue-100">Đơn hàng</div>
                </div>
                <div>
                  <div className="text-2xl font-bold">{(stats.totalSpent / 1000000).toFixed(1)}M</div>
                  <div className="text-sm text-blue-100">Đã mua</div>
                </div>
                <div>
                  <div className="text-2xl font-bold">{stats.savedItems}</div>
                  <div className="text-sm text-blue-100">Yêu thích</div>
                </div>
                <div>
                  <div className="text-2xl font-bold">{stats.loyaltyPoints}</div>
                  <div className="text-sm text-blue-100">Điểm tích lũy</div>
                </div>
              </div>
            </div>

            <button
              onClick={handleLogout}
              className="mt-4 md:mt-0 bg-white bg-opacity-20 hover:bg-opacity-30 px-4 py-2 rounded-lg transition-colors flex items-center"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Đăng xuất
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar Navigation */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <nav className="space-y-2">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors ${
                      activeTab === tab.id
                        ? 'bg-blue-50 text-blue-600'
                        : 'text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <tab.icon className="h-5 w-5" />
                    <span>{tab.label}</span>
                  </button>
                ))}
              </nav>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-xl shadow-lg p-8">
              {activeTab === 'profile' && (
                <div>
                  <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold text-gray-900">Thông tin cá nhân</h2>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => loadUserProfile()}
                        disabled={loading}
                        className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                        <span>Tải lại</span>
                      </button>
                      <button
                        onClick={() => setIsEditing(!isEditing)}
                        disabled={loading}
                        className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <Edit className="h-4 w-4" />
                        <span>{loading ? 'Đang tải...' : isEditing ? 'Hủy' : 'Chỉnh sửa'}</span>
                      </button>
                    </div>
                  </div>

                  {loading ? (
                    <div className="flex justify-center items-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                      <span className="ml-2 text-gray-600">Đang tải thông tin...</span>
                    </div>
                  ) : (
                    <>


                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Họ tên</label>
                      <div className="flex items-center space-x-3">
                        <User className="h-5 w-5 text-gray-400" />
                        <input
                          type="text"
                          value={userInfo.name}
                          disabled={!isEditing || loading}
                          onChange={(e) => setUserInfo({...userInfo, name: e.target.value})}
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg disabled:bg-gray-50"
                          placeholder="Nhập họ tên"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                      <div className="flex items-center space-x-3">
                        <Mail className="h-5 w-5 text-gray-400" />
                        <input
                          type="email"
                          value={userInfo.email}
                          disabled={!isEditing || loading}
                          onChange={(e) => setUserInfo({...userInfo, email: e.target.value})}
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg disabled:bg-gray-50"
                          placeholder="Nhập email"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Số điện thoại</label>
                      <div className="flex items-center space-x-3">
                        <Phone className="h-5 w-5 text-gray-400" />
                        <input
                          type="tel"
                          value={userInfo.phone}
                          disabled={!isEditing || loading}
                          onChange={(e) => setUserInfo({...userInfo, phone: e.target.value})}
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg disabled:bg-gray-50"
                          placeholder="Nhập số điện thoại"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Ngày sinh</label>
                      <div className="flex items-center space-x-3">
                        <Calendar className="h-5 w-5 text-gray-400" />
                        <input
                          type="date"
                          value={userInfo.birthday}
                          disabled={!isEditing}
                          onChange={(e) => setUserInfo({...userInfo, birthday: e.target.value})}
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg disabled:bg-gray-50"
                        />
                      </div>
                    </div>

                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-2">Địa chỉ</label>
                      <div className="flex items-center space-x-3">
                        <MapPin className="h-5 w-5 text-gray-400" />
                        <input
                          type="text"
                          value={userInfo.address}
                          disabled={!isEditing}
                          onChange={(e) => setUserInfo({...userInfo, address: e.target.value})}
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg disabled:bg-gray-50"
                        />
                      </div>
                    </div>
                  </div>

                  {isEditing && (
                    <div className="mt-8 flex space-x-4">
                      <button
                        onClick={handleSave}
                        disabled={loading}
                        className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {loading ? 'Đang lưu...' : 'Lưu thay đổi'}
                      </button>
                      <button
                        onClick={() => setIsEditing(false)}
                        className="border border-gray-300 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-50 transition-colors"
                      >
                        Hủy bỏ
                      </button>
                    </div>
                  )}
                  </>
                  )}
                </div>
              )}

              {activeTab === 'orders' && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">Lịch sử đơn hàng</h2>
                  
                  {/* Order Tabs */}
                  <div className="border-b border-gray-200 mb-6">
                    <div className="flex space-x-8 overflow-x-auto">
                      {orderTabs.map((tab) => (
                        <button
                          key={tab.id}
                          onClick={() => setOrderTab(tab.id)}
                          className={`py-2 px-1 border-b-2 font-medium text-sm whitespace-nowrap transition-colors ${
                            orderTab === tab.id
                              ? 'border-blue-500 text-blue-600'
                              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                          }`}
                        >
                          {tab.label}
                          {tab.count > 0 && (
                            <span className={`ml-2 px-2 py-1 text-xs rounded-full ${
                              orderTab === tab.id
                                ? 'bg-blue-100 text-blue-600'
                                : 'bg-gray-100 text-gray-600'
                            }`}>
                              {tab.count}
                            </span>
                          )}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Orders List */}
                  {filteredOrders.length === 0 ? (
                    <div className="text-center py-12">
                      <div className="text-gray-400 mb-4">
                        <ShoppingBag className="h-16 w-16 mx-auto" />
                      </div>
                      <h3 className="text-lg font-medium text-gray-900 mb-2">Không có đơn hàng nào</h3>
                      <p className="text-gray-500 mb-6">
                        {orderTab === 'all' 
                          ? 'Bạn chưa có đơn hàng nào. Hãy bắt đầu mua sắm ngay!' 
                          : `Bạn không có đơn hàng nào ở trạng thái "${orderTabs.find(t => t.id === orderTab)?.label}".`
                        }
                      </p>
                      <button 
                        onClick={() => onNavigate?.('home')}
                        className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        Tiếp tục mua sắm
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-6">
                      {filteredOrders.map((order) => (
                        <div key={order.orderId} className="border border-gray-200 rounded-lg overflow-hidden">
                          {/* Order Header */}
                          <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
                            <div className="flex justify-between items-center">
                              <div className="flex items-center gap-4">
                                <div>
                                  <h3 className="font-bold text-lg">Đơn hàng #{order.orderId}</h3>
                                  <p className="text-sm text-gray-600">Ngày đặt: {new Date(order.createdAt || order.updatedAt || '').toLocaleString()}</p>
                                </div>
          
                              </div>
                              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(order.uiStatus || order.status)}`}>
                                {order.uiStatus || order.status}
                              </span>
                            </div>
                          </div>

                          {/* Per-store SubOrders */}
                          <div className="p-6 space-y-4">
                            {Array.isArray(order.subOrders) && order.subOrders.map((sub: any) => (
                              <div key={sub.subOrderId} className="border rounded-lg p-4 bg-gray-50">
                                <div className="flex justify-between items-center mb-3">
                                  <div
                                    className="flex items-center gap-3 cursor-pointer"
                                    onClick={() => navigate(`/store/${sub.store?.storeId ?? ''}`)}
                                  >
                                    <img src={sub.store?.avatar || '/api/placeholder/32/32'} alt={sub.store?.name} className="w-8 h-8 rounded-full object-cover" />
                                    <div>
                                      <div className="text-sm font-medium">{sub.store?.name || 'Cửa hàng'}</div>
                                      <div className="text-xs text-gray-500">{sub.items?.length ?? 0} sản phẩm</div>
                                    </div>
                                  </div>
                                  <div className="text-right">
                                    <div className="text-sm text-gray-600">Tổng: {formatPrice(sub.subtotal || 0)}</div>
                                    <div className="text-xs text-gray-500">Phí ship: {formatPrice(sub.shippingFee || 0)}</div>
                                  </div>
                                </div>

                                <div className="space-y-3">
                                  {Array.isArray(sub.items) && sub.items.map((item: any) => (
                                    <div key={item.itemId} className="flex items-center gap-4 p-3 bg-white rounded-lg border border-gray-100">
                                      <img src={item.variant?.colorImageUrl || '/api/placeholder/80/80'} alt={item.variant?.product?.name} className="w-20 h-20 object-cover rounded-lg" />
                                      <div className="flex-1">
                                        <h4 className="font-medium text-gray-900">{item.variant?.product?.name}</h4>
                                        <p className="text-sm text-gray-600">{item.variant?.colorName || ''} • {item.variant?.sizeName || ''}</p>
                                        <div className="flex items-center justify-between mt-2">
                                          <span className="text-sm text-gray-600">Số lượng: x{item.quantity}</span>
                                          <span className="font-bold text-lg text-blue-600">{formatPrice(item.priceAtOrder || item.variant?.price || 0)}</span>
                                        </div>

                                        {/* Nếu đơn đã bị hủy: hiển thị nút Mua lại trên từng sản phẩm */}
                                        {order.uiStatus === 'cancelled' && (
                                          <div className="mt-3">
                                            <button
                                              onClick={() => navigate(`/product/${item.variant?.product?.productId}`)}
                                              className="px-3 py-2 text-sm border border-blue-300 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
                                            >
                                              Mua lại
                                            </button>
                                          </div>
                                        )}
                                      </div>
                                    </div>
                                  ))}
                                </div>

                                {/* Shipment summary for sub-order */}
                                {sub.shipment && (
                                  <div className="mt-3 p-3 bg-white rounded border border-gray-100">
                                    <div className="flex justify-between items-center">
                                      <div className="text-sm text-gray-700">Mã vận đơn: {sub.shipment.trackingCode || '-'}</div>
                                      <div className="text-sm text-gray-600">Trạng thái: {sub.shipment.status || '-'}</div>
                                    </div>
                                  </div>
                                )}

                                {/* Nếu đơn đang ở trạng thái chờ và thanh toán COD: hiển thị nút Hủy cho từng sub-order */}
                                {order.uiStatus === 'pending' && ((order.payment?.paymentMethod || order.payment?.method || order.payment?.payment_method || '').toString().toUpperCase() === 'COD') && (
                                  <div className="mt-3 flex justify-end">
                                    <button
                                      onClick={async () => {
                                        if (!confirm('Bạn có chắc chắn muốn hủy sub-order này?')) return;
                                        try {
                                          await cancelSubOrder(sub.subOrderId);
                                          await getMyOrders();
                                        } catch (err: any) {
                                          console.error('cancelSubOrder error', err);
                                          alert(err?.message || 'Lỗi khi hủy sub-order');
                                        }
                                      }}
                                      disabled={cancellingSubOrder}
                                      className="px-4 py-2 text-sm border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                                    >
                                      {cancellingSubOrder ? 'Đang hủy...' : 'Hủy đơn'}
                                    </button>
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>

                          {/* Order Footer */}
                          <div className="p-6 border-t border-gray-200 bg-white">
                            <div className="flex justify-between items-center">
                              <div className="text-sm text-gray-600">
                                Tổng cộng: {order.subOrders?.reduce((acc:any, s:any)=> acc + (s.items?.reduce((a:any,i:any)=> a + (i.quantity||0),0)||0),0) || 0} sản phẩm
                              </div>
                              <div className="flex items-center gap-4">
                                <div className="text-right">
                                  <p className="text-sm text-gray-600">Thành tiền:</p>
                                  <p className="font-bold text-xl text-red-600">{formatPrice(order.totalAmount || 0)}</p>
                                </div>
                                <div className="flex gap-2">
                                  {(
                                    (order.payment?.status || '').toString().toUpperCase() === 'PENDING' &&
                                    ((order.payment?.paymentMethod || order.payment?.method || order.payment?.payment_method || '').toString().toUpperCase() !== 'COD')
                                  ) && (
                                    <button
                                      onClick={async () => {
                                        try {
                                          const amount = Number(order.totalAmount) || 0;
                                          const url = await createVnpayLink(order.orderId, amount);
                                          if (url) {
                                            window.location.href = url;
                                          } else {
                                            alert('Không nhận được liên kết thanh toán');
                                          }
                                        } catch (err: any) {
                                          console.error('createVnpayLink error', err);
                                          alert(err?.message || 'Lỗi khi tạo liên kết VNPay');
                                        }
                                      }}
                                      disabled={creatingVnpay}
                                      className="px-4 py-2 text-sm bg-yellow-50 border border-yellow-300 text-yellow-700 rounded-lg hover:bg-yellow-100 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                                    >
                                      {creatingVnpay ? 'Đang chuyển...' : 'Chờ thanh toán'}
                                    </button>
                                  )}
                                  {order.uiStatus === 'pending' && !((order.payment?.paymentMethod || order.payment?.method || order.payment?.payment_method || '').toString().toUpperCase() === 'COD') && (
                                    <button
                                      onClick={async () => {
                                        if (!confirm('Bạn có chắc chắn muốn hủy đơn này?')) return;
                                        try {
                                          await cancelOrder(order.orderId);
                                          await getMyOrders();
                                        } catch (err: any) {
                                          console.error('cancelOrder error', err);
                                          alert(err?.message || 'Lỗi khi hủy đơn');
                                        }
                                      }}
                                      disabled={cancellingOrder}
                                      className="px-4 py-2 text-sm border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                                    >
                                      {cancellingOrder ? 'Đang hủy...' : 'Hủy đơn'}
                                    </button>
                                  )}
                                  {['shipping', 'delivering', 'completed'].includes(order.uiStatus) && (
                                    <button onClick={() => handleShowTracking(order.orderId)} className="px-4 py-2 text-sm border border-blue-300 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors">Theo dõi</button>
                                  )}
                                  {order.uiStatus === 'completed' && (
                                    <>
                                      <button
                                        onClick={() => {
                                          const pid = order.subOrders?.[0]?.items?.[0]?.variant?.product?.productId;
                                          if (pid) navigate(`/product/${pid}`);
                                        }}
                                        className="px-4 py-2 text-sm border border-blue-300 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
                                      >
                                        Mua lại
                                      </button>
                                      <button className="px-4 py-2 text-sm border border-yellow-300 text-yellow-600 rounded-lg hover:bg-yellow-50 transition-colors">Đánh giá</button>
                                    </>
                                  )}
                                  {order.uiStatus === 'refund' && (
                                    <button className="px-4 py-2 text-sm border border-green-300 text-green-600 rounded-lg hover:bg-green-50 transition-colors">Liên hệ hỗ trợ</button>
                                  )}
                                  {order.uiStatus !== 'pending' && (
                                  <button
                                    onClick={() => {
                                      // Nếu trạng thái là từ Vận chuyển trở đi thì mở modal tracking
                                      const trackable = ['shipping', 'delivering', 'completed'].includes(order.uiStatus);
                                      if (trackable) {
                                        handleShowTracking(order.orderId);
                                      } else {
                                        // Ngược lại, điều hướng đến trang chi tiết đơn (nếu handler được cung cấp)
                                        onNavigate?.('orderDetail', { orderId: order.orderId });
                                      }
                                    }}
                                    className="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                                  >
                                    Chi tiết
                                  </button>
                                  )}
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'addresses' && (
                <div>
                  <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold text-gray-900">Địa chỉ giao hàng</h2>
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

                  {/* Address List */}
                  {addressLoading ? (
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
                      {addresses.map((address) => (
                        <div key={address.addressId}>
                          <div className="border border-gray-200 rounded-lg p-6 relative">
                            <div className="pr-16">
                              <div className="flex items-center gap-3 mb-2">
                                <h4 className="font-semibold">{address.name}</h4>
                                <span className="text-gray-400">|</span>
                                <span className="text-gray-600">{address.phoneNumber}</span>
                                {address.isDefault && (
                                  <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full flex items-center gap-1">
                                    <Check className="h-3 w-3" />
                                    Mặc định
                                  </span>
                                )}
                              </div>
                              <p className="text-gray-700 mb-3">{address.fullAddress}</p>
                              
                              {!address.isDefault && (
                                <button
                                  onClick={() => handleSetDefaultAddress(address.addressId)}
                                  className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                                >
                                  Đặt làm mặc định
                                </button>
                              )}
                            </div>
                            
                            {/* Nút chỉnh sửa/xóa ở góc phải */}
                            <div className="absolute bottom-4 right-4 flex gap-2">
                              <button
                                onClick={() => handleEditAddress(address)}
                                className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                title="Chỉnh sửa"
                              >
                                <Edit className="h-4 w-4" />
                              </button>
                              <button
                                onClick={() => {
                                  if (!confirm('Bạn có chắc chắn muốn xóa địa chỉ này?')) return;
                                  handleDeleteAddress(address.addressId);
                                }}
                                className={`p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors`}
                                title="Xóa"
                              >
                                <Trash2 className="h-4 w-4" />
                              </button>
                            </div>
                          </div>
                          
                          {/* Edit Form Below Address */}
                          {showAddressForm && formPosition === 'bottom' && editingAddress?.addressId === address.addressId && (
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
              )}

              {activeTab === 'vouchers' && (
                <div>
                  <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold text-gray-900">Quản lý Voucher</h2>
                    <div className="text-sm text-gray-600">
                      Tổng: {savedVouchers.length} voucher đã lưu
                    </div>
                  </div>

                  {/* Quick save form (paste voucher id/code) */}
                  <div className="mb-4 flex items-center gap-3">
                    <input
                      value={voucherToSaveCode}
                      onChange={e => setVoucherToSaveCode(e.target.value)}
                      placeholder="Nhập mã voucher để lưu"
                      className="px-3 py-2 border border-gray-300 rounded-md w-72"
                    />
                    <button
                      onClick={() => handleSaveVoucher(voucherToSaveCode)}
                      disabled={savingVoucher}
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-60"
                    >
                      {savingVoucher ? 'Đang lưu...' : 'Lưu voucher'}
                    </button>
                    {saveVoucherError && <p className="text-sm text-red-600">{saveVoucherError}</p>}
                  </div>

                  {/* Voucher Tabs */}
                  <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg mb-6">
                    {[
                      { id: 'available', label: 'Có thể dùng', count: savedVouchers.filter(v => v.can_use && v.is_active && new Date(v.end_date) > new Date()).length },
                      { id: 'used', label: 'Đã sử dụng', count: savedVouchers.filter(v => !v.can_use && v.used_count > 0).length },
                      { id: 'expired', label: 'Hết hạn', count: savedVouchers.filter(v => !v.is_active || new Date(v.end_date) <= new Date()).length }
                    ].map((tab) => (
                      <button
                        key={tab.id}
                        onClick={() => setVoucherTab(tab.id)}
                        className={`flex-1 py-3 px-4 rounded-md text-sm font-medium transition-colors ${
                          voucherTab === tab.id
                            ? 'bg-white text-blue-600 shadow-sm'
                            : 'text-gray-600 hover:text-gray-900'
                        }`}
                      >
                        {tab.label} ({tab.count})
                      </button>
                    ))}
                  </div>

                  {/* Voucher List */}
                  <div className="space-y-4">
                    {savedVouchers
                      .filter(voucher => {
                        if (voucherTab === 'available') {
                          return voucher.can_use && voucher.is_active && new Date(voucher.end_date) > new Date();
                        } else if (voucherTab === 'used') {
                          return !voucher.can_use && voucher.used_count > 0;
                        } else if (voucherTab === 'expired') {
                          return !voucher.is_active || new Date(voucher.end_date) <= new Date();
                        }
                        return true;
                      })
                      .map((voucher) => {
                        const isExpired = new Date(voucher.end_date) <= new Date();
                        const isUsedUp = !voucher.can_use && voucher.used_count >= voucher.per_user_limit;
                        
                        return (
                          <div
                            key={voucher.voucher_id}
                            className={`border rounded-xl p-6 transition-all ${
                              voucher.can_use && !isExpired
                                ? 'border-blue-200 bg-blue-50 hover:shadow-md'
                                : 'border-gray-200 bg-gray-50 opacity-75'
                            }`}
                          >
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                {/* Voucher Header */}
                                <div className="flex items-center gap-3 mb-3">
                                  <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                                    voucher.type === 'platform' 
                                      ? 'bg-purple-100 text-purple-700' 
                                      : 'bg-green-100 text-green-700'
                                  }`}>
                                    <Tag className="h-3 w-3 mr-1" />
                                    {voucher.type === 'platform' ? 'Platform' : voucher.seller?.name}
                                  </div>
                                  
                                  {/* Status badges */}
                                  {isExpired && (
                                    <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-red-100 text-red-700">
                                      Hết hạn
                                    </span>
                                  )}
                                  {isUsedUp && (
                                    <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-700">
                                      Đã hết lượt
                                    </span>
                                  )}
                                </div>

                                {/* Voucher Code */}
                                <div className="flex items-center gap-2 mb-2">
                                  <code className="bg-gray-800 text-white px-3 py-1 rounded font-mono text-lg font-bold">
                                    {voucher.code}
                                  </code>
                                  <button 
                                    onClick={() => navigator.clipboard.writeText(voucher.code)}
                                    className="text-blue-600 hover:text-blue-700 text-sm"
                                  >
                                    Sao chép
                                  </button>
                                </div>

                                {/* Voucher Details */}
                                <div className="text-gray-900 font-semibold text-lg mb-1">
                                  {voucher.discount_type === 'percent' 
                                    ? `Giảm ${voucher.discount_value}%${voucher.max_discount ? ` (tối đa ${formatPrice(voucher.max_discount)})` : ''}`
                                    : `Giảm ${formatPrice(voucher.discount_value)}`
                                  }
                                </div>

                                <p className="text-gray-600 mb-3">{voucher.description}</p>

                                {/* Voucher Info Grid */}
                                <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                                  <div>
                                    <span className="font-medium">Đơn tối thiểu:</span> {formatPrice(voucher.min_order_amount)}
                                  </div>
                                  <div>
                                    <span className="font-medium">Hết hạn:</span> {new Date(voucher.end_date).toLocaleDateString('vi-VN')}
                                  </div>
                                  <div>
                                    <span className="font-medium">Đã dùng:</span> {voucher.used_count}/{voucher.per_user_limit}
                                  </div>
                                  <div>
                                    <span className="font-medium">Lưu từ:</span> {new Date(voucher.saved_at).toLocaleDateString('vi-VN')}
                                  </div>
                                </div>
                              </div>

                              {/* Action Button */}
                              <div className="ml-6">
                                {voucher.can_use && !isExpired ? (
                                  <button
                                    onClick={() => onNavigate?.('cart')}
                                    className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium"
                                  >
                                    Dùng ngay
                                  </button>
                                ) : (
                                  <div className="text-gray-400 text-sm font-medium px-6 py-2">
                                    {isExpired ? 'Đã hết hạn' : isUsedUp ? 'Hết lượt dùng' : 'Không khả dụng'}
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        );
                      })}
                  </div>

                  {/* Empty State */}
                  {savedVouchers.filter(voucher => {
                    if (voucherTab === 'available') {
                      return voucher.can_use && voucher.is_active && new Date(voucher.end_date) > new Date();
                    } else if (voucherTab === 'used') {
                      return !voucher.can_use && voucher.used_count > 0;
                    } else if (voucherTab === 'expired') {
                      return !voucher.is_active || new Date(voucher.end_date) <= new Date();
                    }
                    return true;
                  }).length === 0 && (
                    <div className="text-center py-12">
                      <Gift className="h-16 w-16 mx-auto text-gray-300 mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        {voucherTab === 'available' && 'Không có voucher khả dụng'}
                        {voucherTab === 'used' && 'Chưa sử dụng voucher nào'}
                        {voucherTab === 'expired' && 'Không có voucher hết hạn'}
                      </h3>
                      <p className="text-gray-600 mb-6">
                        {voucherTab === 'available' && 'Hãy khám phá các voucher mới tại trang chính'}
                        {voucherTab === 'used' && 'Voucher đã sử dụng sẽ hiển thị ở đây'}
                        {voucherTab === 'expired' && 'Voucher hết hạn sẽ hiển thị ở đây'}
                      </p>
                      {voucherTab === 'available' && (
                        <button
                          onClick={() => onNavigate?.('promotions')}
                          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                        >
                          Khám phá voucher
                        </button>
                      )}
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'settings' && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">Cài đặt tài khoản</h2>
                  <div className="space-y-6">
                    <div className="border border-gray-200 rounded-lg p-6">
                      <h3 className="font-bold mb-2">Thông báo</h3>
                      <div className="space-y-3">
                        <label className="flex items-center">
                          <input type="checkbox" className="mr-3" defaultChecked />
                          <span>Nhận email về đơn hàng</span>
                        </label>
                        <label className="flex items-center">
                          <input type="checkbox" className="mr-3" defaultChecked />
                          <span>Nhận thông báo khuyến mãi</span>
                        </label>
                        <label className="flex items-center">
                          <input type="checkbox" className="mr-3" />
                          <span>Nhận SMS thông báo</span>
                        </label>
                      </div>
                    </div>

                    <div className="border border-gray-200 rounded-lg p-6">
                      <h3 className="font-bold mb-4">Bảo mật</h3>
                      <div className="space-y-3">
                        <button className="w-full text-left p-3 border border-gray-300 rounded-lg hover:bg-gray-50">
                          Đổi mật khẩu
                        </button>
                        <button className="w-full text-left p-3 border border-gray-300 rounded-lg hover:bg-gray-50">
                          Xác thực hai yếu tố
                        </button>
                      </div>
                    </div>

                    <div className="border border-red-200 rounded-lg p-6">
                      <h3 className="font-bold text-red-600 mb-2">Vùng nguy hiểm</h3>
                      <p className="text-gray-600 mb-4">Hành động này không thể hoàn tác</p>
                      <button className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors">
                        Xóa tài khoản
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Loyalty Program */}
        <div className="mt-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl text-white p-8">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center mb-2">
                <Gift className="h-6 w-6 mr-2" />
                <h3 className="text-xl font-bold">Chương trình thành viên</h3>
              </div>
              <p className="mb-4">Bạn có {stats.loyaltyPoints} điểm tích lũy</p>
              <div className="w-64 bg-white bg-opacity-20 rounded-full h-2 mb-2">
                <div className="bg-white rounded-full h-2" style={{width: '65%'}}></div>
              </div>
              <p className="text-sm text-purple-100">Còn 550 điểm nữa để lên hạng Vàng</p>
            </div>
            <button className="bg-white text-purple-600 px-6 py-3 rounded-lg hover:bg-gray-100 transition-colors font-medium">
              Đổi điểm
            </button>
          </div>
        </div>
      </div>

      {/* Tracking Modal */}
      {showTrackingModal && selectedOrderTracking && (
        <TrackingModal orderId={selectedOrderTracking} />
      )}
    </CustomerLayout>
  );
}