import React, { useState, useMemo } from 'react';
import { useLocation } from 'react-router-dom';
import CustomerLayout from '../../layout/CustomerLayout';
import {
  CreditCard,
  MapPin,
  Truck,
  Shield,
  Plus,
  Edit,
  Check,
  Clock,
  Package
} from 'lucide-react';

/* =======================
   TYPES
======================= */

interface PaymentPageProps {
  onNavigate?: (page: string) => void;
}

interface Address {
  id: string;
  name: string;
  phone: string;
  province: string;
  ward: string;
  street: string;
  specificAddress: string;
  address: string;
  isDefault: boolean;
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
    unitPrice: number;
    colorImageUrl: string;
    product: {
      name: string;
      store: StoreInfo;
    };
  };
}

/* =======================
   COMPONENT
======================= */

export default function PaymentPage({ onNavigate }: PaymentPageProps) {
  const location = useLocation();
  const orderItems: OrderItem[] = location.state?.orderItems || [];

  const [selectedDeliveryAddress] = useState<string>('1');
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState<string>('card');
  const [selectedShipping, setSelectedShipping] = useState<string>('standard');
  const [isProcessing, setIsProcessing] = useState(false);

  /* =======================
     MOCK DATA
  ======================= */

  const addresses: Address[] = [
    {
      id: '1',
      name: 'Nguyễn Văn A',
      phone: '0901234567',
      province: 'TP.Hồ Chí Minh',
      ward: 'Phường Bến Nghé',
      street: 'Đường Lê Lợi',
      specificAddress: 'Số 123, Tầng 2',
      address: 'TP.HCM, Phường Bến Nghé, Đường Lê Lợi, Số 123',
      isDefault: true
    }
  ];

  const shippingOptions = [
    { id: 'standard', name: 'Giao hàng tiêu chuẩn', time: '3-5 ngày', price: 30000 },
    { id: 'express', name: 'Giao hàng nhanh', time: '1-2 ngày', price: 50000 }
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

  /* =======================
     PRICE CALCULATION
  ======================= */

  const subtotal = orderItems.reduce((sum, i) => sum + i.subtotal, 0);
  const shippingCost =
    shippingOptions.find(s => s.id === selectedShipping)?.price || 0;
  const total = subtotal + shippingCost;

  const formatPrice = (v: number) =>
    new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(v);

  const handlePayment = async () => {
    setIsProcessing(true);
    await new Promise(r => setTimeout(r, 2000));
    setIsProcessing(false);
    alert('Đặt hàng thành công');
    onNavigate?.('home');
  };

  const currentAddress = addresses.find(a => a.id === selectedDeliveryAddress);

  /* =======================
     RENDER
  ======================= */

  return (
    <CustomerLayout onNavigate={onNavigate}>
      <div className="max-w-7xl mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-3 gap-8">

        {/* LEFT */}
        <div className="lg:col-span-2 space-y-6">

          {/* Address */}
          <div className="bg-white p-6 rounded-xl shadow">
            <h2 className="flex items-center gap-2 font-semibold text-lg mb-3">
              <MapPin className="w-5 h-5 text-blue-600" /> Địa chỉ giao hàng
            </h2>
            {currentAddress && (
              <p className="text-gray-700">{currentAddress.address}</p>
            )}
          </div>

          {/* Payment */}
          <div className="bg-white p-6 rounded-xl shadow">
            <h2 className="flex items-center gap-2 font-semibold text-lg mb-4">
              <CreditCard className="w-5 h-5 text-blue-600" /> Thanh toán
            </h2>

            {['card', 'cod'].map(m => (
              <div
                key={m}
                className={`border rounded-lg p-4 mb-3 cursor-pointer ${
                  selectedPaymentMethod === m ? 'border-blue-500 bg-blue-50' : ''
                }`}
                onClick={() => setSelectedPaymentMethod(m)}
              >
                {m === 'card' ? 'Thẻ / VNPay' : 'Thanh toán khi nhận hàng'}
                {selectedPaymentMethod === m && <Check className="inline ml-2 w-4 h-4" />}
              </div>
            ))}
          </div>

          {/* Shipping */}
          <div className="bg-white p-6 rounded-xl shadow">
            <h2 className="flex items-center gap-2 font-semibold text-lg mb-4">
              <Truck className="w-5 h-5 text-blue-600" /> Vận chuyển
            </h2>

            {shippingOptions.map(s => (
              <div
                key={s.id}
                className={`border rounded-lg p-4 mb-3 cursor-pointer ${
                  selectedShipping === s.id ? 'border-blue-500 bg-blue-50' : ''
                }`}
                onClick={() => setSelectedShipping(s.id)}
              >
                <div className="flex justify-between">
                  <div>
                    <div className="font-medium">{s.name}</div>
                    <div className="text-sm text-gray-500 flex items-center gap-1">
                      <Clock className="w-4 h-4" /> {s.time}
                    </div>
                  </div>
                  <div>{formatPrice(s.price)}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* RIGHT – ORDER SUMMARY */}
        <div className="bg-white p-6 rounded-xl shadow h-fit">
          <h2 className="flex items-center gap-2 font-semibold text-lg mb-4">
            <Package className="w-5 h-5 text-blue-600" /> Tóm tắt đơn hàng
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
              </div>
            ))}
          </div>

          {/* TOTAL */}
          <div className="border-t mt-6 pt-4 space-y-2">
            <div className="flex justify-between">
              <span>Tạm tính</span>
              <span>{formatPrice(subtotal)}</span>
            </div>
            <div className="flex justify-between">
              <span>Phí ship</span>
              <span>{formatPrice(shippingCost)}</span>
            </div>
            <div className="flex justify-between font-semibold text-lg">
              <span>Tổng cộng</span>
              <span className="text-blue-600">{formatPrice(total)}</span>
            </div>
          </div>

          <button
            onClick={handlePayment}
            disabled={isProcessing}
            className="w-full bg-blue-600 text-white py-3 rounded-xl mt-5 flex justify-center items-center gap-2"
          >
            {isProcessing ? 'Đang xử lý...' : (
              <>
                <Shield className="w-5 h-5" />
                Đặt hàng
              </>
            )}
          </button>
        </div>
      </div>
    </CustomerLayout>
  );
}
