import React, { useState, useMemo } from 'react';
import { useEffect } from 'react';
import { useCalculateShippingFee } from '../../../hooks/shipment/shipment';
import { useAddresses } from '../../../hooks/user/address';
import { useCreateOrder } from '../../../hooks/order/order';
import { getProvinces, getWards, getHamlets } from '../../../services/callAPI/apiAddress';
import { useVoucherManagement, useUseVoucher } from '../../../hooks/discount/discount';
import { applyVoucher, Voucher } from '../../../services/discount/discount';
import { useLocation } from 'react-router-dom';
import CustomerLayout from '../../layout/CustomerLayout';
import useCreateVnPayLink from '../../../hooks/payment/payment';
import useCreateGhtkOrders from '../../../hooks/shipment/ghtk';
import { 
  CreditCard, MapPin, Truck, Shield, ChevronDown, 
  Plus, Edit, Trash2, Check, Clock, Package
} from 'lucide-react';

interface PaymentPageProps {
  onNavigate?: (page: string) => void;
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


interface PaymentMethod {
  id: string;
  type: 'qr' | 'vnpay' | 'cod';
  name: string;
  icon: string;
  description: string;
}
interface StoreInfo {
  storeId: string | number;
  name: string;
  avatar?: string;
}
interface OrderItem {
  id: string;
  quantity: number;
  subtotal: number;
  variant: {
    variantId: string;
    unitPrice: number;
    weight: number;
    colorImageUrl: string;
    product: {
      name: string;
      store: StoreInfo;
    };
  };
}




export default function PaymentPage({ onNavigate }: PaymentPageProps) {
  const location = useLocation();
  // Lấy danh sách sản phẩm đã chọn từ state khi chuyển từ CartPage
  const orderItems = location.state?.orderItems || [];
  const [selectedDeliveryAddress, setSelectedDeliveryAddress] = useState<string>('1'); // Địa chỉ giao hàng được chọn
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState<string>('qr');
  const [selectedShipping, setSelectedShipping] = useState<string>('standard');
  const [showAddressList, setShowAddressList] = useState(false);
  const [showAddressForm, setShowAddressForm] = useState(false);
  const [editingAddress, setEditingAddress] = useState<Address | null>(null);
  const [cardDetails, setCardDetails] = useState({
    number: '',
    expiry: '',
    cvv: '',
    name: ''
  });
  const [isProcessing, setIsProcessing] = useState(false);
  const [newAddress, setNewAddress] = useState<any>({
    name: '',
    phone: '',
    phoneNumber: '',
    province: '',
    provinceId: '',
    ward: '',
    wardId: '',
    hamlet: '',
    hamletId: '',
    specificAddress: '',
    detail: ''
  });

  // Use address hook from AccountPage for real API
  const {
    addresses,
    loading: addressLoading,
    addAddress,
    updateAddress,
    deleteAddress,
    setDefaultAddress,
    defaultAddress
  } = useAddresses();

  const [provinces, setProvinces] = useState<any[]>([]);
  const [wards, setWards] = useState<any[]>([]);
  const [hamlets, setHamlets] = useState<any[]>([]);
  const [loadingWards, setLoadingWards] = useState(false);
  const [loadingHamlets, setLoadingHamlets] = useState(false);

  useEffect(() => {
    const loadProvinces = async () => {
      const p = await getProvinces();
      setProvinces(p || []);
    };
    loadProvinces();
  }, []);

  useEffect(() => {
    const loadWards = async () => {
      if (!newAddress.provinceId) {
        setWards([]);
        return;
      }
      setLoadingWards(true);
      const w = await getWards(newAddress.provinceId);
      setWards(w || []);
      setLoadingWards(false);
    };
    loadWards();
  }, [newAddress.provinceId]);

  useEffect(() => {
    const loadHamlets = async () => {
      if (!newAddress.province || !newAddress.ward) {
        setHamlets([]);
        return;
      }
      setLoadingHamlets(true);
      const h = await getHamlets(newAddress.province, newAddress.ward);
      setHamlets(h || []);
      setLoadingHamlets(false);
    };
    loadHamlets();
  }, [newAddress.province, newAddress.ward]);
 const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
  const [verifyingReturn, setVerifyingReturn] = useState(false);
  const [verifyResult, setVerifyResult] = useState<any>(null);

  // If VNPay redirects back to /payment with vnp_* params, verify with backend
  useEffect(() => {
    try {
      const qs = window.location.search || '';
      if (!qs) return;
      const params = Object.fromEntries(new URLSearchParams(qs));
      // detect VNPay return by checking vnp_TxnRef or vnp_ResponseCode
      if (!params.vnp_TxnRef && !params.vnp_ResponseCode) return;

      const txnRef = String(params.vnp_TxnRef || '');
      if (!txnRef) return;

      const processedKey = `vnp_processed_${txnRef}`;
      // Avoid double-processing in same tab/session (reloads or StrictMode remounts)
      if (sessionStorage.getItem(processedKey)) return;
      sessionStorage.setItem(processedKey, String(Date.now()));

      // Notify user once we start processing
      alert('Xử lý kết quả thanh toán VNPAY, vui lòng chờ...');

      (async () => {
        setVerifyingReturn(true);
        setVerifyResult(null);
        try {
          const verifyUrl = (apiUrl ? apiUrl.replace(/\/$/, '') : '') + '/api/vnpay/verify-return';
          const res = await fetch(verifyUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ params, rawQuery: qs })
          });

          const json = await res.json();
          setVerifyResult(json);
          if (json?.valid) {
            alert('Thanh toán đã được xác thực: giao dịch thành công bằng VNPAY');
            try {
              const orderId = json.orderId || txnRef;
              if (orderId) {
                // try {
                //   await createGhtkOrders(orderId);
                //   alert('Tạo đơn vận chuyển thành công khi thanh toán bằng VNPAY');
                // } catch (err: any) {
                //   console.error('createGhtkOrders error after vnpay verify', err);
                //   alert('Tạo đơn vận chuyển thất bại khi thanh toán VNPAY ' + (err?.message || ''));
                // }

                // Mark applied vouchers as used for this order
                try {
                  await markVouchersAsUsed(orderId);
                } catch (err: any) {
                  console.error('markVouchersAsUsed after vnpay error', err);
                }
              }
            } catch (err: any) {
              console.error('Error processing vnpay verify result', err);
            }
          } else {
            console.warn('VNPay verify returned invalid:', json);
            alert('Thanh toán chưa được xác thực hoặc thất bại: ' + (json?.reason || ''));
          }
        } catch (err) {
          console.error('Error verifying VNPay return:', err);
          alert('Có lỗi khi xác thực kết quả thanh toán. Vui lòng thử lại sau.');
        } finally {
          // clear query string to avoid reprocessing on reload
          try { window.history.replaceState({}, document.title, window.location.pathname); } catch(e){}
          setVerifyingReturn(false);
        }
      })();
    } catch (e) {
      console.warn('Error parsing return URL', e);
    }
  }, [apiUrl]);
  // Voucher state
  const [showVoucherModal, setShowVoucherModal] = useState(false);
  const [voucherTab, setVoucherTab] = useState<'discount' | 'shipping'>('discount');
  const [modalStoreId, setModalStoreId] = useState<string | number | null>(null);
  const [modalSelectedDiscountVoucher, setModalSelectedDiscountVoucher] = useState<Voucher | null>(null);
  const [modalSelectedShippingVoucher, setModalSelectedShippingVoucher] = useState<Voucher | null>(null);

  // Per-store applied voucher discounts
  const [discountsByStore, setDiscountsByStore] = useState<Record<string, number>>({});
  const [appliedDiscountVoucherByStore, setAppliedDiscountVoucherByStore] = useState<Record<string, Voucher | null>>({});

  // Per-store applied shipping discounts
  const [shippingDiscountByStore, setShippingDiscountByStore] = useState<Record<string, number>>({});
  const [appliedShippingVoucherByStore, setAppliedShippingVoucherByStore] = useState<Record<string, Voucher | null>>({});
  // Tính tổng khối lượng (totalWeight) cho từng store
  const storeWeights = useMemo(() => {
    const map = new Map<string | number, number>();
    orderItems.forEach(item => {
      const storeId = item.variant.product.store.storeId;
      if (!storeId) return;
      const weight = item.variant.weight || 0;
      const prev = map.get(storeId) || 0;
      map.set(storeId, prev + weight * (item.quantity || 1));
    });
    return map;
  }, [orderItems]);

  // Tính subtotal cho từng store
  const subtotalByStore = useMemo(() => {
    const map = new Map<string | number, number>();
    orderItems.forEach(item => {
      const storeId = item.variant.product.store.storeId;
      if (!storeId) return;
      const prev = map.get(storeId) || 0;
      map.set(storeId, prev + Number(item.subtotal));
    });
    return map;
  }, [orderItems]);

  // Tính phí ship cho từng store (dùng hook useCalculateShippingFee)
  const shippingByStore: Record<string, number> = {};
  const shippingLoadingByStore: Record<string, boolean> = {};
  const shippingErrorByStore: Record<string, string | null> = {};
  for (const [storeId, totalWeight] of storeWeights.entries()) {
    const { data, loading, error } = useCalculateShippingFee({ storeId: String(storeId), weight: totalWeight });
    shippingByStore[storeId] = data?.totalFee || 0;
    shippingLoadingByStore[storeId] = loading;
    shippingErrorByStore[storeId] = error;
  }
  const getFullAddress = (a: any) => {
    if (!a) return '';
    if (a.fullAddress) return a.fullAddress;
    if (a.address) return a.address;
    const parts = [a.province, a.ward, a.street || a.detail || a.specificAddress, a.specificAddress || a.detail];
    return parts.filter(Boolean).join(', ');
  };

  const currentDeliveryAddress = ((addresses && addresses.length)
    ? addresses.find((addr: any) => String(addr.addressId || addr.id) === String(selectedDeliveryAddress))
    : undefined) || defaultAddress;

  const getAddressId = (a: any) => String(a?.addressId ?? a?.id ?? '');
  
  const handleSelectAddress = (addressId: string) => {
    setSelectedDeliveryAddress(addressId);
    setShowAddressList(false);
  };

  const handleEditAddress = (address: any) => {
    setEditingAddress(address);
    // Prepare address selects: ensure province/ward/hamlet lists and set names and ids
    console.log('Preparing to edit address:', address);
    (async () => {
      try {
        // Ensure provinces loaded
        let localProvinces = provinces || [];
        if (!localProvinces || localProvinces.length === 0) {
          const p = await getProvinces();
          localProvinces = p || [];
          setProvinces(localProvinces);
        }

        // Determine province id/name
        let provinceId = address.provinceId || '';
        let provinceName = address.province || '';
        if ((!provinceId || provinceId === '') && provinceName) {
          const found = localProvinces.find((p: any) => String(p.name).toLowerCase() === String(provinceName).toLowerCase());
          if (found) {
            provinceId = String(found.code || found.id || '');
            provinceName = found.name || provinceName;
          }
        }
        if (provinceId && (!provinceName || provinceName === '')) {
          const found = localProvinces.find((p: any) => String(p.code) === String(provinceId) || String(p.id) === String(provinceId));
          provinceName = found?.name || provinceName;
        }

        // Load wards for provinceId
        let wardId = address.wardId || address.ward_code || '';
        let wardName = address.ward || '';
        if (provinceId) {
          setLoadingWards(true);
          try {
            const w = await getWards(provinceId);
            setWards(w || []);
            if ((!wardId || wardId === '') && wardName && (w || []).length > 0) {
              const foundW = (w || []).find((x: any) => String(x.name).toLowerCase() === String(wardName).toLowerCase());
              if (foundW) wardId = String(foundW.code || foundW.id || '');
            }
            if (wardId && (!wardName || wardName === '')) {
              const foundW = (w || []).find((x: any) => String(x.code) === String(wardId) || String(x.id) === String(wardId));
              wardName = foundW?.name || wardName;
            }
          } catch (err) {
            console.warn('Error loading wards for edit:', err);
          } finally {
            setLoadingWards(false);
          }
        }

        // Load hamlets for provinceName + wardName
        let ham = address.hamlet || '';
        let hamletIndex = -1;
        if (provinceName && wardName) {
          setLoadingHamlets(true);
          try {
            const hamletsData = await getHamlets(provinceName, wardName);
            setHamlets(hamletsData || []);
            if (hamletsData && hamletsData.length > 0) {
              if (address.hamlet) {
                const idx = hamletsData.findIndex((h: any) => (h.name || h) === address.hamlet);
                if (idx !== -1) hamletIndex = idx;
              }
            }
          } catch (err) {
            console.warn('Error loading hamlets for edit:', err);
          } finally {
            setLoadingHamlets(false);
          }
        }

        setNewAddress({
          name: address.name || '',
          phone: address.phone || address.phoneNumber || '',
          phoneNumber: address.phone || address.phoneNumber || '',
          province: provinceName || address.province || '',
          provinceId: provinceId || address.provinceId || '',
          ward: wardName || address.ward || '',
          wardId: wardId || address.wardId || '',
          hamlet: ham || address.hamlet || '',
          hamletId: hamletIndex,
          street: address.street || '',
          specificAddress: address.specificAddress || address.detail || '',
          detail: address.detail || address.specificAddress || ''
        });
      } catch (err) {
        console.warn('Error preparing address edit:', err);
        setNewAddress({
          name: address.name || '',
          phone: address.phone || address.phoneNumber || '',
          phoneNumber: address.phone || address.phoneNumber || '',
          province: address.province || '',
          provinceId: address.provinceId || '',
          ward: address.ward || '',
          wardId: address.wardId || '',
          hamlet: address.hamlet || '',
          street: address.street || '',
          specificAddress: address.specificAddress || address.detail || '',
          detail: address.detail || address.specificAddress || ''
        });
      }
      setShowAddressForm(true);
      setShowAddressList(false);
    })();
  };

  const handleSaveAddress = async () => {
    // Ensure ward is a human-readable name (map wardId -> name if needed)
    let wardName = newAddress.ward;
    if ((!wardName || wardName === '') && newAddress.wardId) {
      const found = (wards || []).find((w: any) => String(w.code) === String(newAddress.wardId) || String(w.id) === String(newAddress.wardId));
      wardName = found?.name || wardName;
    }

    const payload = {
      name: newAddress.name,
      phoneNumber: newAddress.phone || newAddress.phoneNumber,
      province: newAddress.province,
      ward: wardName || newAddress.ward,
      hamlet: newAddress.hamlet,
      detail: newAddress.specificAddress || newAddress.detail || newAddress.street || ''
    } as any;

    try {
      if (editingAddress) {
        const res = await updateAddress({ addressId: String(editingAddress.addressId || editingAddress.addressId || editingAddress.addressId), ...payload });
        if ((res as any)?.success) {
          setShowAddressForm(false);
          setEditingAddress(null);
        }
      } else {
        const res = await addAddress(payload);
        if ((res as any)?.success) {
          setShowAddressForm(false);
          setEditingAddress(null);
        }
      }
    } catch (err) {
      console.error('save address error', err);
    } finally {
      setNewAddress({ name: '', phone: '', phoneNumber: '', province: '', provinceId: '', ward: '', wardId: '', hamlet: '', street: '', specificAddress: '', detail: '' });
    }
  };

  const handleCancelAddressForm = () => {
    setShowAddressForm(false);
    setEditingAddress(null);
    setNewAddress({ name: '', phone: '', phoneNumber: '', province: '', provinceId: '', ward: '', wardId: '', hamlet: '', street: '', specificAddress: '', detail: '' });
    if (showAddressList) {
      setShowAddressList(true);
    }
  };

  const paymentMethods: PaymentMethod[] = [
    {
      id: 'qr',
      type: 'qr',
      name: 'Thanh toán QR / Chuyển khoản',
      icon: '💳',
      description: 'Thanh toán QR / Chuyển khoản'
    },
    {
      id: 'vnpay',
      type: 'vnpay',
      name: 'Thanh toán qua VNPAY',
      icon: '🎯',
      description: 'Thanh toán qua VNPAY'
    },
    {
      id: 'cod',
      type: 'cod',
      name: 'Thanh toán khi nhận hàng',
      icon: '💰',
      description: 'Thanh toán bằng tiền mặt'
    }
  ];

  // orderItems đã lấy từ location.state ở trên

  const shippingOptions = [
    { id: 'standard', name: 'Giao hàng tiêu chuẩn', time: '3-5 ngày', price: 30000 },
    { id: 'express', name: 'Giao hàng nhanh', time: '1-2 ngày', price: 50000 },
    { id: 'same-day', name: 'Giao hàng trong ngày', time: 'Trong ngày', price: 100000 }
  ];
  /* =======================
     GROUP ORDER ITEMS BY STORE
  ======================= */

  const itemsByStore = useMemo(() => {
    const map = new Map<string | number, { store: StoreInfo; items: OrderItem[] }>();

    orderItems.forEach(item => {
      const store = item.variant.product.store;
      if (!store) return;

      if (!map.has(store.storeId)) {
        map.set(store.storeId, { store, items: [] });
      }
      map.get(store.storeId)!.items.push(item);
    });

    return Array.from(map.values());
  }, [orderItems]);

  const openVoucherModalForStore = (storeId: string | number, tab: 'discount' | 'shipping') => {
    setModalStoreId(storeId);
    setVoucherTab(tab);
    // initialize modal selections from applied per-store vouchers if present
    const sid = String(storeId);
    setModalSelectedDiscountVoucher(appliedDiscountVoucherByStore[sid] || null);
    setModalSelectedShippingVoucher(appliedShippingVoucherByStore[sid] || null);
    setShowVoucherModal(true);
  };

  const applyVoucherToStore = async (v: Voucher) => {
    // If modalStoreId is not set, choose the store where this voucher gives the largest benefit
    const computeDiscountForStore = (storeId: string | number) => {
      const sid = String(storeId);
      const storeSubtotalRaw = subtotalByStore.get(storeId) || 0;
      const storeSubtotal = Number(storeSubtotalRaw || 0);
      const storeShip = Number(shippingByStore[sid] || 0);

      const minOrder = Number(v.minOrderAmount || 0);
      if (minOrder > 0 && storeSubtotal < minOrder) return { eligible: false, amount: 0, type: 'none' as const };

      if (v.discountType === 'FREESHIP') {
        const approx = Number(v.discountValue || 0);
        const amount = Math.min(approx || Infinity, storeShip);
        return { eligible: amount > 0, amount, type: 'shipping' as const };
      }

      // PERCENT or FIXED on subtotal
      let raw = 0;
      if (v.discountType === 'PERCENT') raw = (storeSubtotal * Number(v.discountValue || 0)) / 100;
      else raw = Number(v.discountValue || 0);

      const maxDisc = Number(v.maxDiscount || 0);
      if (maxDisc > 0) raw = Math.min(raw, maxDisc);
      const amount = Math.max(0, raw);
      return { eligible: amount > 0, amount, type: 'discount' as const };
    };

    const findBestStore = () => {
      let best = { storeId: null as string | number | null, amount: 0, type: 'none' as 'none' | 'discount' | 'shipping' };
      // iterate known stores from subtotalByStore
      subtotalByStore.forEach((_, storeId) => {
        const res = computeDiscountForStore(storeId as string | number);
        if (res.eligible && res.amount > best.amount) best = { storeId: storeId as string | number, amount: res.amount, type: res.type };
      });
      return best;
    };

    try {
      // If modalStoreId provided, apply to that store. Otherwise choose best-fit store.
      const target = modalStoreId ?? findBestStore().storeId;
      if (!target) {
        // nothing eligible
        setShowVoucherModal(false);
        return;
      }

      const sid = String(target);
      const storeSubtotal = subtotalByStore.get(target) || 0;
      const res = await applyVoucher(v.code, storeSubtotal);
      const discount = res?.discountAmount || 0;

      if (v.discountType === 'FREESHIP') {
        const shipFee = shippingByStore[sid] || 0;
        const applied = Math.min(discount, shipFee);
        setShippingDiscountByStore(prev => ({ ...prev, [sid]: applied }));
        setAppliedShippingVoucherByStore(prev => ({ ...prev, [sid]: v }));
      } else {
        setDiscountsByStore(prev => ({ ...prev, [sid]: discount }));
        setAppliedDiscountVoucherByStore(prev => ({ ...prev, [sid]: v }));
      }

      setShowVoucherModal(false);
      setModalStoreId(null);
    } catch (err) {
      console.error('applyVoucherToStore error', err);
    }
  };

  // Helper to format currency for UI (VNĐ assumed). Replace/integrate with project util if available.
  const formatCurrency = (n?: number) => {
    if (!n) return '0';
    return n.toLocaleString(undefined, { minimumFractionDigits: 0 });
  };


  const orderTotal = Array.from(subtotalByStore.values()).reduce((sum, storeSubtotal) => sum + storeSubtotal, 0);


  // --- VOUCHER MANAGEMENT HOOK ---
  const {
    discountVouchers,
    shippingVouchers,
    selectedDiscountVoucher,
    selectedShippingVoucher,
    discountAmount: voucherDiscountAmount,
    shippingDiscount: voucherShippingDiscount,
    loading: voucherLoading,
    applyDiscountVoucher,
    applyShippingVoucher,
    clearDiscountVoucher,
    clearShippingVoucher,
    clearAllVouchers,
    refetchVouchers
  } = useVoucherManagement(orderTotal);
  // Hook to mark vouchers as used after successful payment
  const { useVoucher: markVoucherUsed, using: markingVoucher, error: markVoucherError } = useUseVoucher();
  // Helper: iterate applied vouchers and call markVoucherUsed
  async function markVouchersAsUsed(orderId: string) {
    if (!orderId) return;
    const tasks: Promise<any>[] = [];

    // Discount vouchers per store
    for (const sid of Object.keys(appliedDiscountVoucherByStore || {})) {
      const v = appliedDiscountVoucherByStore[sid];
      const amount = Number(discountsByStore[sid] || 0);
      if (v && (v.voucherId)) {
        const vid = String(v.voucherId);
        if (vid) tasks.push(markVoucherUsed(vid, amount, orderId));
      }
    }

    // Shipping vouchers per store
    for (const sid of Object.keys(appliedShippingVoucherByStore || {})) {
      const v = appliedShippingVoucherByStore[sid];
      const amount = Number(shippingDiscountByStore[sid] || 0);
      if (v && (v.voucherId)) {
        const vid = String(v.voucherId ||'');
        if (vid) tasks.push(markVoucherUsed(vid, amount, orderId));
      }
    }

    if (tasks.length === 0) return;
    await Promise.all(tasks);
  }
  // Calculate shipping cost after shipping voucher
  const totalShipping = Object.values(shippingByStore).reduce((sum, fee) => sum + fee, 0);
  const totalStoreDiscount = Object.values(discountsByStore).reduce((s, v) => s + (v || 0), 0);
  const totalStoreShipDiscount = Object.values(shippingDiscountByStore).reduce((s, v) => s + (v || 0), 0);
  const shippingCost = Math.max(0, totalShipping - (voucherShippingDiscount || 0) - totalStoreShipDiscount);
  const total = orderTotal - (voucherDiscountAmount || 0) - totalStoreDiscount + shippingCost;

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(price);
  };

  const formatDate = (iso?: string) => {
    if (!iso) return '';
    try {
      return new Date(iso).toLocaleDateString('vi-VN');
    } catch {
      return iso;
    }
  };

  const formatVoucherValue = (v: any) => {
    if (!v) return '';
    if (v.discountType === 'PERCENT') return `${v.discountValue}%`;
    const num = Number(v.discountValue || 0);
    return formatPrice(isNaN(num) ? 0 : num);
  };
  // createOrder hook
  const { createOrder, loading: creatingOrder, error: createOrderError, data: createOrderData } = useCreateOrder();
  // VNPay link hook
  const { createVnpayLink, loading: creatingVnPayLoading, error: createVnPayError } = useCreateVnPayLink();
  // GHTK hook
  const { createGhtkOrders, loading: creatingGhtk, error: createGhtkError } = useCreateGhtkOrders();

  const handlePayment = async () => {
    try {
      if (!itemsByStore || itemsByStore.length === 0) {
        alert('Chọn sản phẩm để đặt hàng.');
        return;
      }
      setIsProcessing(true);

      // Build CreateOrderInput according to backend inputs.py
      const addressId = String(selectedDeliveryAddress || getAddressId(currentDeliveryAddress) || '');
      const paymentMethod = selectedPaymentMethod || 'cod';
      const totalAmount = Number(total || 0);
      const shippingFee = Number(shippingCost || 0);

      const subOrders = itemsByStore.map(storeGroup => {
        const sid = String(storeGroup.store.storeId);
        const items = storeGroup.items.map((it: any) => ({
          variantId: String(it.variant.variantId || ''),
          quantity: Number(it.quantity || 1),
          priceAtOrder: Number(it.variant?.unitPrice ?? (it.subtotal && it.quantity ? it.subtotal / it.quantity : 0))
        }));

        return {
          storeId: sid,
          shippingFee: Number(shippingByStore[sid] || 0),
          subtotal: Number(subtotalByStore.get(storeGroup.store.storeId) || 0),
          items
        };
      });

      const input = {
        paymentMethod,
        addressId,
        totalAmount,
        shippingFee,
        subOrders
      };
      alert(paymentMethod);
      const res = await createOrder(input);
      const payload = res?.data?.createOrder;
      if (payload && payload.success) {
        if (paymentMethod !== 'cod') {
          try {
            const payUrl = await createVnpayLink(payload.orderId, totalAmount);
            if (payUrl) {
              window.location.href = payUrl;
            }
          } catch (err: any) {
            console.error('createVnpayLink error', err);
            alert('Tạo liên kết VNPay thất bại: ' + (err?.message || ''));
          }
        } else {
          // For COD payment, create GHTK orders
          alert('Tạo đơn hàng thành công khi thanh toán COD');
            try {
              // const ghtkRes = await createGhtkOrders(payload.orderId);
              // console.log('createGhtkOrders result', ghtkRes);
              // alert('Tạo đơn vận chuyển thành công với thanh toán COD');
              // // Mark applied vouchers as used for this order
              try {
                await markVouchersAsUsed(payload.orderId);
              } catch (err: any) {
                console.error('markVouchersAsUsed error', err);
              }
            } catch (err: any) {
              console.error('createGhtkOrders error', err);
              alert('Tạo đơn vận chuyển thất bại khi thanh toán COD ' + (err?.message || ''));
            }
          
        }
      } else {
        const msg = payload?.message || (res?.errors && JSON.stringify(res.errors)) || 'Lỗi khi tạo đơn hàng';
        alert(`Tạo đơn thất bại: ${msg}`);
      }
    } catch (err: any) {
      console.error('createOrder error', err);
      alert('Có lỗi xảy ra khi tạo đơn hàng. Vui lòng thử lại.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <CustomerLayout onNavigate={onNavigate}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumb */}
        <nav className="flex mb-6 text-sm">
          <button 
            onClick={() => onNavigate?.('home')}
            className="text-gray-500 hover:text-gray-700"
          >
            Trang chủ
          </button>
          <span className="mx-2 text-gray-500">/</span>
          <button 
            onClick={() => onNavigate?.('cart')}
            className="text-gray-500 hover:text-gray-700"
          >
            Giỏ hàng
          </button>
          <span className="mx-2 text-gray-500">/</span>
          <span className="text-gray-900">Thanh toán</span>
        </nav>

        {/* Voucher Modal */}
        {showVoucherModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
            <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg p-6 relative animate-fade-in">
              <button className="absolute top-2 right-2 text-gray-400 hover:text-gray-600" onClick={() => { setShowVoucherModal(false); setModalSelectedDiscountVoucher(null); setModalSelectedShippingVoucher(null); setModalStoreId(null); }}>
                ×
              </button>
              <div className="flex gap-2 mb-4">
                <button
                  className={`flex-1 py-2 rounded-lg font-medium ${voucherTab === 'discount' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'}`}
                  onClick={() => setVoucherTab('discount')}
                >
                  Voucher giảm giá
                </button>
                <button
                  className={`flex-1 py-2 rounded-lg font-medium ${voucherTab === 'shipping' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'}`}
                  onClick={() => setVoucherTab('shipping')}
                >
                  Voucher vận chuyển
                </button>
              </div>
              <div className="max-h-72 overflow-y-auto space-y-3">
                {voucherTab === 'discount' && discountVouchers.map(v => (
                  <div
                    key={v.voucherId}
                    className={`border rounded-xl p-4 flex items-center justify-between cursor-pointer transition-colors ${(
                      modalSelectedDiscountVoucher?.voucherId === v.voucherId ||
                      (modalStoreId ? (appliedDiscountVoucherByStore[String(modalStoreId)]?.voucherId === v.voucherId) : (selectedDiscountVoucher?.voucherId === v.voucherId))
                    ) ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'}`}
                    onClick={() => setModalSelectedDiscountVoucher(v)}
                  >
                    <div className="flex-1 pr-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-semibold text-blue-600">{v.name}</div>
                          <div className="text-xs text-gray-500 mt-1">{v.description}</div>
                          <div className="text-xs text-gray-400 mt-1">Mã: {v.code}</div>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-bold text-green-600">{formatVoucherValue(v)}</div>
                          <div className="text-xs text-gray-400">Loại: {v.discountType}</div>
                        </div>
                      </div>

                      <div className="mt-3 text-xs text-gray-500 grid grid-cols-2 gap-2">
                        <div>Điều kiện tối thiểu: <span className="text-gray-700">{formatPrice(Number(v.minOrderAmount || 0))}</span></div>
                        <div>Giảm tối đa: <span className="text-gray-700">{v.maxDiscount ? formatPrice(Number(v.maxDiscount)) : '-'}</span></div>
                        <div>Bắt đầu: <span className="text-gray-700">{formatDate(v.startDate)}</span></div>
                        <div>Kết thúc: <span className="text-gray-700">{formatDate(v.endDate)}</span></div>
                      </div>
                    </div>
                    <input type="radio" className="ml-3" checked={modalSelectedDiscountVoucher?.voucherId === v.voucherId || (modalStoreId ? appliedDiscountVoucherByStore[String(modalStoreId)]?.voucherId === v.voucherId : selectedDiscountVoucher?.voucherId === v.voucherId)} readOnly />
                  </div>
                ))}
                {voucherTab === 'shipping' && shippingVouchers.map(v => (
                  <div
                    key={v.voucherId}
                    className={`border rounded-xl p-4 flex items-center justify-between cursor-pointer transition-colors ${(
                      modalSelectedShippingVoucher?.voucherId === v.voucherId ||
                      (modalStoreId ? (appliedShippingVoucherByStore[String(modalStoreId)]?.voucherId === v.voucherId) : (selectedShippingVoucher?.voucherId === v.voucherId))
                    ) ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'}`}
                    onClick={() => setModalSelectedShippingVoucher(v)}
                  >
                    <div className="flex-1 pr-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-semibold text-blue-600">{v.name}</div>
                          <div className="text-xs text-gray-500 mt-1">{v.description}</div>
                          <div className="text-xs text-gray-400 mt-1">Mã: {v.code}</div>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-bold text-green-600">{formatVoucherValue(v)}</div>
                          <div className="text-xs text-gray-400">Loại: {v.discountType}</div>
                        </div>
                      </div>

                      <div className="mt-3 text-xs text-gray-500 grid grid-cols-2 gap-2">
                        <div>Điều kiện tối thiểu: <span className="text-gray-700">{formatPrice(Number(v.minOrderAmount || 0))}</span></div>
                        <div>Giảm tối đa: <span className="text-gray-700">{v.maxDiscount ? formatPrice(Number(v.maxDiscount)) : '-'}</span></div>
                        <div>Bắt đầu: <span className="text-gray-700">{formatDate(v.startDate)}</span></div>
                        <div>Kết thúc: <span className="text-gray-700">{formatDate(v.endDate)}</span></div>
                      </div>
                    </div>
                    <input type="radio" className="ml-3" checked={modalSelectedShippingVoucher?.voucherId === v.voucherId || (modalStoreId ? appliedShippingVoucherByStore[String(modalStoreId)]?.voucherId === v.voucherId : selectedShippingVoucher?.voucherId === v.voucherId)} readOnly />
                  </div>
                ))}
              </div>
              <div className="mt-6 flex gap-3">
                <button
                  className="flex-1 bg-blue-600 text-white py-2 rounded-lg font-medium hover:bg-blue-700"
                  onClick={async () => {
                    // Apply both selected discount and shipping vouchers if present
                    try {
                      // Always apply per-store so we can record which store received the voucher
                      if (modalSelectedDiscountVoucher) await applyVoucherToStore(modalSelectedDiscountVoucher);
                      if (modalSelectedShippingVoucher) await applyVoucherToStore(modalSelectedShippingVoucher as Voucher);
                      setShowVoucherModal(false);
                    } finally {
                      setModalSelectedDiscountVoucher(null);
                      setModalSelectedShippingVoucher(null);
                      setModalStoreId(null);
                    }
                  }}
                >
                  Áp dụng
                </button>
                <button
                  className="flex-1 border border-gray-300 py-2 rounded-lg font-medium text-gray-700 hover:bg-gray-50"
                  onClick={clearAllVouchers}
                >
                  Bỏ chọn tất cả
                </button>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Payment Form */}
          <div className="lg:col-span-2 space-y-8">
            {/* Delivery Address */}
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                  <MapPin className="h-5 w-5 text-blue-600" />
                  Địa chỉ giao hàng
                </h2>
              </div>

              {!showAddressList && !showAddressForm && currentDeliveryAddress && (
                <div className="border border-gray-200 rounded-xl p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h4 className="font-medium">{currentDeliveryAddress.name}</h4>
                        <span className="text-gray-500">|</span>
                        <span className="text-gray-600">{currentDeliveryAddress.phoneNumber}</span>
                        {currentDeliveryAddress.isDefault && (
                          <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                            Mặc định
                          </span>
                        )}
                        {currentDeliveryAddress.addressId !== defaultAddress?.addressId && (
                          <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                            Địa chễ giao hàng
                          </span>
                        )}
                      </div>
                      <p className="text-gray-700">{getFullAddress(currentDeliveryAddress)}</p>
                    </div>
                    <button
                      onClick={() => setShowAddressList(true)}
                      className="text-blue-600 hover:text-blue-800 font-medium px-4 py-2 border border-blue-200 rounded-lg hover:bg-blue-50 transition-colors"
                    >
                      Thay đổi
                    </button>
                  </div>
                </div>
              )}

              {showAddressList && !showAddressForm && (
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-medium">Chọn địa chỉ giao hàng</h3>
                    <button
                      onClick={() => {
                        setShowAddressForm(true);
                        setShowAddressList(false);
                        setEditingAddress(null);
                      }}
                      className="text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1"
                    >
                      <Plus className="h-4 w-4" />
                      Thêm địa chỉ mới
                    </button>
                  </div>

                  <div className="space-y-3 mb-4">
                    {addresses.map((address) => {
                      const aid = getAddressId(address);
                      return (
                        <div
                          key={aid}
                          className={`border rounded-xl p-4 cursor-pointer transition-colors ${
                            String(selectedDeliveryAddress) === aid
                              ? 'border-blue-500 bg-blue-50'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                          onClick={() => handleSelectAddress(aid)}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <h4 className="font-medium">{address.name}</h4>
                                <span className="text-gray-500">|</span>
                                <span className="text-gray-600">{address.phoneNumber}</span>
                                {address.isDefault && (
                                  <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                                    Mặc định
                                  </span>
                                )}
                              </div>
                              <p className="text-gray-700 text-sm">{getFullAddress(address)}</p>
                            </div>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleEditAddress(address);
                              }}
                              className="text-blue-600 hover:text-blue-800"
                            >
                              <Edit className="h-4 w-4" />
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  <button
                    onClick={() => setShowAddressList(false)}
                    className="w-full border border-gray-300 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Quay lại
                  </button>
                </div>
              )}

              {showAddressForm && (
                <div>
                  <h4 className="font-medium mb-4">
                    {editingAddress ? 'Chỉnh sửa địa chỉ' : 'Thêm địa chỉ mới'}
                  </h4>
                  <div className="space-y-4">
                    {/* Thông tin liên hệ */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <input
                        type="text"
                        placeholder="Họ và tên *"
                        value={newAddress.name}
                        onChange={(e) => setNewAddress({...newAddress, name: e.target.value})}
                        className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                      <input
                        type="tel"
                        placeholder="Số điện thoại *"
                        value={newAddress.phone}
                        onChange={(e) => setNewAddress({...newAddress, phone: e.target.value})}
                        className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    
                    {/* Địa chỉ hành chính theo thứ tự: Tỉnh/TP → Phường/Xã → Đường/Khu/Ấp → Địa chỉ đặc biệt */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <select
                        value={newAddress.provinceId || ''}
                        onChange={(e) => {
                          const code = e.target.value;
                          const selected = provinces.find(p => p.code === parseInt(code));
                          console.log('Province selected:', selected);
                          // If provinces list is empty (fallback), use the option value as province name
                          const provinceName = selected?.name || code;
                          console.log('Selected province:', provinceName, code);
                          setNewAddress({...newAddress, province: provinceName, provinceId: code, ward: '', wardId: '', hamlet: ''});
                        }}
                        className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="">Chọn Tỉnh/Thành phố *</option>
                        {provinces.length > 0 ? (
                          provinces.map((province: any) => (
                            <option key={province.code} value={province.code}>{province.name}</option>
                          ))
                        ) : (
                          <>
                          </>
                        )}
                      </select>
                      
                      <select
                        value={newAddress.wardId || ''}
                        onChange={(e) => {
                          const code = e.target.value;
                          const selected = wards.find((w: any) => String(w.code) === String(code) || String(w.ward_code) === String(code) || String(w.id) === String(code));
                          const wardName = selected?.name || selected?.label || e.target.value;
                          setNewAddress({...newAddress, ward: wardName, wardId: code, hamlet: ''});
                        }}
                        className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        disabled={!newAddress.provinceId}
                      >
                        <option value="">Chọn Phường/Xã *</option>
                        {loadingWards ? (
                          <option value="">Đang tải...</option>
                        ) : (
                          wards.map((w: any) => (
                            <option key={w.code || w.ward_code || w.id} value={w.code || w.ward_code || w.id}>{w.name || w.label}</option>
                          ))
                        )}
                      </select>
                    </div>
                    
                    <select
                      value={newAddress.hamletId !== undefined && newAddress.hamletId !== null ? String(newAddress.hamletId) : ''}
                      onChange={(e) => {
                        const idx = Number(e.target.value);
                        const name = (hamlets && hamlets.length > 0 && idx >= 0) ? (typeof hamlets[idx] === 'string' ? hamlets[idx] : hamlets[idx].name) : '';
                        setNewAddress({ ...newAddress, hamletId: isNaN(idx) ? '' : idx, hamlet: name });
                      }}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      disabled={!newAddress.ward || !hamlets || hamlets.length === 0}
                    >
                      <option value="">Chọn Đường/Khu/Ấp *</option>
                      {hamlets && hamlets.length > 0 ? (
                        hamlets.map((h: any, idx: number) => {
                          const name = typeof h === 'string' ? h : h.name;
                          return (
                            <option key={String(idx)} value={String(idx)}>{name}</option>
                          );
                        })
                      ) : (
                        <option value="" disabled>Không có dữ liệu ấp/khu/đường</option>
                      )}
                    </select>
                    
                    {/* Địa chỉ cụ thể (tự nhập) */}
                    <textarea
                      placeholder="Địa chỉ đặc biệt (Số nhà, tầng, căn hộ, ghi chú thêm...) *"
                      rows={2}
                      value={newAddress.specificAddress}
                      onChange={(e) => setNewAddress({...newAddress, specificAddress: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    
                    <div className="flex gap-3">
                      <button 
                        onClick={handleSaveAddress}
                        className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        {editingAddress ? 'Cập nhật' : 'Thêm địa chỉ'}
                      </button>
                      <button
                        onClick={handleCancelAddressForm}
                        className="border border-gray-300 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors"
                      >
                        Hủy
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Payment Method */}
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
              <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                <CreditCard className="h-5 w-5 text-blue-600" />
                Phương thức thanh toán
              </h2>

              <div className="space-y-4">
                {paymentMethods.map((method) => (
                  <div
                    key={method.id}
                    className={`border rounded-xl p-4 cursor-pointer transition-colors ${
                      selectedPaymentMethod === method.id 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedPaymentMethod(method.id)}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{method.icon}</span>
                      <div className="flex-1">
                        <h4 className="font-medium">{method.name}</h4>
                        <p className="text-sm text-gray-600">{method.description}</p>
                      </div>
                      {selectedPaymentMethod === method.id && (
                        <Check className="h-5 w-5 text-blue-600" />
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* Card Details Form */}
              {selectedPaymentMethod === 'card' && (
                <div className="mt-6 p-4 border rounded-xl bg-gray-50">
                  <h4 className="font-medium mb-4">Chi tiết thẻ</h4>
                  <div className="space-y-4">
                    <input
                      type="text"
                      placeholder="Số thẻ"
                      value={cardDetails.number}
                      onChange={(e) => setCardDetails({...cardDetails, number: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <input
                      type="text"
                      placeholder="Tên trên thẻ"
                      value={cardDetails.name}
                      onChange={(e) => setCardDetails({...cardDetails, name: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <div className="grid grid-cols-2 gap-4">
                      <input
                        type="text"
                        placeholder="MM/YY"
                        value={cardDetails.expiry}
                        onChange={(e) => setCardDetails({...cardDetails, expiry: e.target.value})}
                        className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                      <input
                        type="text"
                        placeholder="CVV"
                        value={cardDetails.cvv}
                        onChange={(e) => setCardDetails({...cardDetails, cvv: e.target.value})}
                        className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Shipping Method */}
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
              <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                <Truck className="h-5 w-5 text-blue-600" />
                Phương thức vận chuyển
              </h2>

              <div className="space-y-4">
                {shippingOptions.map((option) => (
                  <div
                    key={option.id}
                    className={`border rounded-xl p-4 cursor-pointer transition-colors ${
                      selectedShipping === option.id 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedShipping(option.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="flex-1">
                          <h4 className="font-medium">{option.name}</h4>
                          <p className="text-sm text-gray-600 flex items-center gap-1">
                            <Clock className="h-4 w-4" />
                            {option.time}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">{formatPrice(option.price)}</p>
                        {selectedShipping === option.id && (
                          <Check className="h-5 w-5 text-blue-600 ml-auto" />
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Order Summary */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 h-fit">
            <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
              <Package className="h-5 w-5 text-blue-600" />
              Tóm tắt đơn hàng
            </h2>

          {/* ITEMS BY STORE */}
          <div className="space-y-6">
            {itemsByStore.map(({ store, items }) => (
              <div key={store.storeId} className="border rounded-lg p-4">
                <div className="flex items-center gap-3 mb-3">
                  {store.avatar && (
                    <img
                      src={store.avatar}
                      alt={store.name}
                      className="w-8 h-8 rounded-full object-cover"
                    />
                  )}
                  <div className="font-medium">{store.name}</div>
                </div>

                <div className="space-y-3">
                  {items.map(item => (
                    <div key={item.id} className="flex gap-3">
                      <img
                        src={item.variant.colorImageUrl}
                        className="w-14 h-14 rounded object-cover"
                        alt=""
                      />
                      <div className="flex-1">
                        <div className="text-sm font-medium">
                          {item.variant.product.name}
                        </div>
                        <div className="flex justify-between text-sm text-gray-600">
                          <span>x{item.quantity}</span>
                          <span>{formatPrice(item.subtotal)}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                {/* Removed per-store "Chọn voucher" button — use the global voucher selector above */}
                {/* Tạm tính theo từng store */}
                <div className="flex justify-between items-center mt-3 pt-3 border-t">
                  <span className="text-sm text-gray-500">Tạm tính</span>
                  <span className="font-medium text-gray-700">
                    {formatPrice(subtotalByStore.get(store.storeId) || 0)}
                  </span>
                </div>
                {/* Phí vận chuyển cho từng store */}
                <div className="flex justify-between items-center mt-3 pt-3 border-t">
                  <span className="text-sm text-gray-500">Phí vận chuyển</span>
                  <span className="font-medium text-gray-700">
                    {formatPrice(shippingByStore[store.storeId] || 0)}
                  </span>
                </div>
                {/* Hiển thị số tiền giảm cho store này (nếu có) */}
                {( (discountsByStore[String(store.storeId)] || 0) > 0 || (shippingDiscountByStore[String(store.storeId)] || 0) > 0) && (
                  <div className="mt-2 space-y-1 text-sm">
                    {appliedDiscountVoucherByStore[String(store.storeId)] && (
                      <div className="text-gray-700">
                        <div className="font-medium">Voucher áp dụng: {appliedDiscountVoucherByStore[String(store.storeId)]!.name} <span className="text-xs text-gray-500">({appliedDiscountVoucherByStore[String(store.storeId)]!.code})</span></div>
                      </div>
                    )}
                    { (discountsByStore[String(store.storeId)] || 0) > 0 && (
                      <div className="text-green-600 flex justify-between">
                        <span>Giảm trên sản phẩm</span>
                        <span>-{formatPrice(discountsByStore[String(store.storeId)])}</span>
                      </div>
                    )}
                    {appliedShippingVoucherByStore[String(store.storeId)] && (
                      <div className="text-gray-700">
                        <div className="font-medium">Voucher ship: {appliedShippingVoucherByStore[String(store.storeId)]!.name} <span className="text-xs text-gray-500">({appliedShippingVoucherByStore[String(store.storeId)]!.code})</span></div>
                      </div>
                    )}
                    { (shippingDiscountByStore[String(store.storeId)] || 0) > 0 && (
                      <div className="text-green-600 flex justify-between">
                        <span>Giảm phí ship</span>
                        <span>-{formatPrice(shippingDiscountByStore[String(store.storeId)])}</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>

            {/* Voucher section */}
            <div className="mb-4">
              <div className="flex items-center justify-between">
                <span className="font-medium">Voucher</span>
                <button
                  className="text-blue-600 hover:underline text-sm font-medium"
                  onClick={() => {
                    setModalStoreId(null);
                    setModalSelectedDiscountVoucher(selectedDiscountVoucher || null);
                    setModalSelectedShippingVoucher(selectedShippingVoucher || null);
                    setShowVoucherModal(true);
                  }}
                >
                  {selectedDiscountVoucher || selectedShippingVoucher ? 'Đổi voucher' : 'Chọn voucher'}
                </button>
              </div>
              <div className="mt-1 text-xs text-gray-500">
                {selectedDiscountVoucher && (
                  <div>
                    <span className="text-blue-600 mr-2">{selectedDiscountVoucher.name}</span>
                    <span>({selectedDiscountVoucher.description})</span>
                  </div>
                )}
                {selectedShippingVoucher && (
                  <div>
                    <span className="text-blue-600 mr-2">{selectedShippingVoucher.name}</span>
                    <span>({selectedShippingVoucher.description})</span>
                  </div>
                )}
                {!selectedDiscountVoucher && !selectedShippingVoucher && <span>Chưa chọn voucher</span>}
              </div>
            </div>

            <div className="border-t pt-4 space-y-3">
              <div className="flex justify-between">
                <span>Tạm tính</span>
                <span>{formatPrice(orderTotal)}</span>
              </div>
              {voucherDiscountAmount > 0 && (
                <div className="flex justify-between text-green-600">
                  <span>Giảm giá</span>
                  <span>-{formatPrice(voucherDiscountAmount)}</span>
                </div>
              )}
              {totalStoreDiscount > 0 && (
                <div className="flex justify-between text-green-600">
                  <span>Giảm giá theo cửa hàng</span>
                  <span>-{formatPrice(totalStoreDiscount)}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span>Phí vận chuyển</span>
                <span>{formatPrice(shippingCost)}</span>
              </div>
              {voucherShippingDiscount > 0 && (
                <div className="flex justify-between text-green-600">
                  <span>Giảm phí ship</span>
                  <span>-{formatPrice(voucherShippingDiscount)}</span>
                </div>
              )}
              {totalStoreShipDiscount > 0 && (
                <div className="flex justify-between text-green-600">
                  <span>Giảm phí ship theo cửa hàng</span>
                  <span>-{formatPrice(totalStoreShipDiscount)}</span>
                </div>
              )}
              <div className="flex justify-between text-lg font-semibold border-t pt-3">
                <span>Tổng cộng</span>
                <span className="text-blue-600">{formatPrice(total)}</span>
              </div>
            </div>

            <button
              onClick={handlePayment}
              disabled={isProcessing}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white py-4 rounded-xl font-medium mt-6 transition-colors flex items-center justify-center gap-2"
            >
              {isProcessing ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                  Đang xử lý...
                </>
              ) : (
                <>
                  <Shield className="h-5 w-5" />
                  Đặt hàng ({formatPrice(total)})
                </>
              )}
            </button>

            <div className="mt-4 text-xs text-gray-500 text-center">
              Bằng cách đặt hàng, bạn đồng ý với{' '}
              <button className="text-blue-600 hover:underline">Điều khoản dịch vụ</button>
              {' '}và{' '}
              <button className="text-blue-600 hover:underline">Chính sách bảo mật</button>
            </div>
          </div>
        </div>
      </div>
    </CustomerLayout>
  );
}