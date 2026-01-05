import { useEffect, useMemo, useState } from "react";
import useSubOrdersByStore from "../../../hooks/order/storeOrder";
import { useStoreAuth } from '../../../hooks/store/storeAuth';
import useCreateSettlement, { useSettlements } from '../../../hooks/settlement/settlement';
import useCreateVnPayLink from '../../../hooks/payment/payment';
import clsx from 'clsx';

export default function PaymentsPage() {
  const { store } = useStoreAuth();
  const storeId = store?.storeId;
  // isPayment=true: chỉ lấy các suborder chưa thuộc SettlementItem (chưa được rút tiền)
  const { data: subOrders = [], loading, refetch } = useSubOrdersByStore(storeId, true);
  const { createSettlement, loading: settlementLoading } = useCreateSettlement();
  const { createVnpayLink, loading: vnpayLoading } = useCreateVnPayLink();
  const { data: settlements, loading: settlementsLoading, fetchSettlements } = useSettlements(storeId);
  const [paymentMethodTab, setPaymentMethodTab] = useState<"All" | "COD" | "VNPAY">("All");
  const [selectedSubOrder, setSelectedSubOrder] = useState<any | null>(null);
  const [showWithdrawModal, setShowWithdrawModal] = useState(false);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [eligibleSubOrders, setEligibleSubOrders] = useState<any[]>([]);

  const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
  const [verifyingReturn, setVerifyingReturn] = useState(false);
  const [verifyResult, setVerifyResult] = useState<any>(null);

  const fmt = new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND", maximumFractionDigits: 0 });

  // Verify VNPay return for store settlement payment
  useEffect(() => {
    try {
      const qs = window.location.search || '';
      if (!qs) return;
      const params = Object.fromEntries(new URLSearchParams(qs));
      
      // detect VNPay return by checking vnp_TxnRef or vnp_ResponseCode
      if (!params.vnp_TxnRef && !params.vnp_ResponseCode) return;

      const txnRef = String(params.vnp_TxnRef || '');
      if (!txnRef) return;

      const processedKey = `vnp_store_processed_${txnRef}`;
      // Avoid double-processing in same tab/session (reloads or StrictMode remounts)
      if (sessionStorage.getItem(processedKey)) return;
      sessionStorage.setItem(processedKey, String(Date.now()));

      // Notify user once we start processing
      alert('Xử lý kết quả thanh toán Settlement qua VNPAY, vui lòng chờ...');

      (async () => {
        setVerifyingReturn(true);
        setVerifyResult(null);
        try {
          const verifyUrl = (apiUrl ? apiUrl.replace(/\/$/, '') : '') + '/api/vnpay/verify-return-store';
          const res = await fetch(verifyUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ params, rawQuery: qs })
          });

          const json = await res.json();
          setVerifyResult(json);
          if (json?.valid) {
            alert(`✅ Thanh toán Settlement thành công!\nSettlement ID: ${json.settlementId}\nSố tiền: ${fmt.format(Number(json.totalAmount))}\nTrạng thái: ${json.status}`);
            
            // Refresh danh sách suborders sau khi thanh toán thành công
            try {
              await refetch();
            } catch (err: any) {
              console.error('Error refetching suborders after settlement payment', err);
            }
          } else {
            console.warn('VNPay verify settlement returned invalid:', json);
            alert('Thanh toán Settlement chưa được xác thực hoặc thất bại: ' + (json?.reason || ''));
          }
        } catch (err) {
          console.error('Error verifying VNPay settlement return:', err);
          alert('Có lỗi khi xác thực kết quả thanh toán Settlement. Vui lòng thử lại sau.');
        } finally {
          // clear query string to avoid reprocessing on reload
          try { 
            window.history.replaceState({}, document.title, window.location.pathname); 
          } catch(e){}
          setVerifyingReturn(false);
        }
      })();
    } catch (e) {
      console.warn('Error parsing VNPay return URL', e);
    }
  }, [apiUrl, refetch, fmt]);

  // helper to safely read numeric fields
  const asNumber = (v: any) => {
    const n = Number(v);
    return Number.isFinite(n) ? n : 0;
  };

  // compute payout per suborder: subtotal + shipping (try several field names)
  const computePayout = (s: any) => {
    const subtotal = asNumber(s.subtotal ?? s.sub_total ?? s.order?.subtotal ?? s.order?.totalAmount ?? s.order?.total_amount ?? 0);
    const shipping = asNumber(s.shippingFee ?? s.shipping_fee ?? s.shipping_amount ?? s.shipment?.pickMoney ?? s.order?.shippingFee ?? 0);
    return subtotal + shipping;
  };

  const normalizeStatus = (s: any) => {
    if (!s && s !== 0) return '';
    try {
      const str = String(s).trim();
      return str.toLowerCase().replace(/\s+/g, '_');
    } catch {
      return '';
    }
  };

  const STATUS_LABEL_VI: Record<string, string> = {
    pending: 'Chờ xác nhận',
    shipping: 'Vận chuyển',
    out_for_delivery: 'Chờ giao hàng',
    completed: 'Hoàn thành',
    cancelled: 'Đã hủy',
    returned: 'Trả hàng / Hoàn tiền',
  };

  const PAYMENT_STATUS_LABEL_VI: Record<string, string> = {
    pending: 'Chờ thanh toán',
    completed: 'Hoàn thành',
    failed: 'Thất bại',
    cancelled: 'Đã hủy',
    refunded: 'Đã hoàn tiền',
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "pending":
        return "text-blue-600 bg-blue-50";
      case "shipping":
        return "text-orange-600 bg-orange-50";
      case "out_for_delivery":
        return "text-yellow-700 bg-yellow-50";
      case "completed":
        return "text-green-600 bg-green-50";
      case "cancelled":
      case "returned":
        return "text-red-600 bg-red-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  // partition by payment method
  const byMethod = useMemo(() => {
    const cod: any[] = [];
    const vnpay: any[] = [];
    subOrders.forEach((s: any) => {
      const rawMethod = s.order?.payment?.paymentMethod ?? s.order?.payment?.payment_method ?? s.payment?.paymentMethod ?? s.payment?.method;
      const method = String(rawMethod || '').toUpperCase();
      if (method === 'COD' || method === 'CASH_ON_DELIVERY') cod.push(s);
      else if (method === 'VNPAY' || method === 'VNPAY_QR') vnpay.push(s);
      else {
        vnpay.push(s);
      }
    });
    return { cod, vnpay };
  }, [subOrders]);

  const displaySource = paymentMethodTab === 'All' ? subOrders : (paymentMethodTab === 'COD' ? byMethod.cod : byMethod.vnpay);

  const handleOpenWithdrawModal = () => {
    if (!storeId) return alert('Store ID không tồn tại');
    
    // Lọc tất cả suborders có shipment.status=completed (cả COD và VNPAY)
    const completed = subOrders.filter((s) => {
      const status = normalizeStatus(s.shipment?.status ?? s.status ?? '');
      return status === 'completed';
    });
    
    if (completed.length === 0) {
      return alert('Không có đơn nào đủ điều kiện rút (shipment status = completed)');
    }
    
    setEligibleSubOrders(completed);
    setShowWithdrawModal(true);
  };

  const handleConfirmWithdraw = async () => {
    if (!storeId) return;
    
    try {
      const result = await createSettlement(storeId);
      setShowWithdrawModal(false);
      alert(`✅ Tạo Settlement thành công!\nSettlement ID: ${result.settlementId}\nTổng tiền: ${fmt.format(Number(result.totalAmount))}\nTrạng thái: ${result.status}`);
      
      // Tạo link VNPay cho store để thanh toán settlement
      try {
        const vnpayUrl = await createVnpayLink(result.settlementId, Number(result.totalAmount), true);
        // Mở link VNPay trong tab mới
        window.open(vnpayUrl, '_blank');
      } catch (vnpayErr: any) {
        console.error('Tạo VNPay link thất bại:', vnpayErr);
        alert(`⚠️ Tạo link thanh toán VNPay thất bại:\n${vnpayErr?.message || String(vnpayErr)}`);
      }
      
      // Refresh danh sách suborders sau khi tạo settlement
      refetch();
    } catch (e: any) {
      const errMsg = e?.message || String(e);
      alert(`❌ Tạo Settlement thất bại:\n${errMsg}`);
    }
  };

  const totalWithdrawAmount = useMemo(() => {
    return eligibleSubOrders.reduce((acc, s) => acc + computePayout(s), 0);
  }, [eligibleSubOrders]);

  const openDetails = (s: any) => setSelectedSubOrder(s);
  const closeDetails = () => setSelectedSubOrder(null);

  const handleOpenHistoryModal = () => {
    if (storeId) {
      fetchSettlements(storeId);
    }
    setShowHistoryModal(true);
  };

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'paid':
        return 'bg-green-100 text-green-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'pending':
        return 'Chờ thanh toán';
      case 'paid':
        return 'Đã thanh toán';
      case 'cancelled':
        return 'Đã hủy';
      default:
        return status;
    }
  };

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Payments & Withdrawals</h2>
        <div className="text-sm text-gray-500">Store: {store?.name ?? '—'}</div>
      </div>

      {/* Payment method tabs */}
      <div className="flex flex-wrap items-center gap-2">
        {(['All', 'COD', 'VNPAY'] as const).map((t) => {
          const count = t === 'All' ? subOrders.length : (t === 'COD' ? byMethod.cod.length : byMethod.vnpay.length);
          return (
            <button
              key={t}
              onClick={() => setPaymentMethodTab(t)}
              className={clsx(
                "rounded-full border px-3 py-1.5 text-sm",
                paymentMethodTab === t
                  ? "border-gray-900 bg-gray-900 text-white"
                  : "border-gray-200 bg-white text-gray-700 hover:bg-gray-50"
              )}
            >
              {t} ({count})
            </button>
          );
        })}
        
        {/* Single Withdraw button */}
        <button 
          onClick={handleOpenWithdrawModal} 
          disabled={settlementLoading || vnpayLoading}
          className={clsx(
            "ml-auto bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors",
            (settlementLoading || vnpayLoading) && "opacity-50 cursor-not-allowed"
          )}
        >
          {settlementLoading ? 'Đang xử lý...' : vnpayLoading ? 'Tạo link thanh toán...' : 'Rút tiền'}
        </button>

        {/* History button */}
        <button 
          onClick={handleOpenHistoryModal}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          📋 Lịch sử rút tiền
        </button>
      </div>

      {/* Table */}
      <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="text-left text-gray-500">
                <th className="px-3 py-2 font-medium">SubOrder ID</th>
                <th className="px-3 py-2 font-medium">Customer</th>
                <th className="px-3 py-2 font-medium">Payment Method</th>
                <th className="px-3 py-2 font-medium">Payment Status</th>
                <th className="px-3 py-2 font-medium">Shipment Status</th>
                <th className="px-3 py-2 font-medium">Date</th>
                <th className="px-3 py-2 font-medium">Amount</th>
                <th className="px-3 py-2 font-medium">Items</th>
                <th className="px-3 py-2 font-medium"></th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={9} className="px-3 py-4 text-center text-gray-500">Loading...</td></tr>
              ) : displaySource.length === 0 ? (
                <tr><td colSpan={9} className="px-3 py-4 text-center text-gray-500">Không có đơn hàng</td></tr>
              ) : (
                displaySource.map((s: any) => {
                  const id = s.subOrderId ?? s.sub_order_id ?? s.id;
                  const customer = s.order?.buyer?.email ?? s.customer ?? "-";
                  const paymentMethod = s.order?.payment?.paymentMethod ?? s.payment?.paymentMethod ?? "-";
                  const rawPaymentStatus = s.order?.payment?.status ?? s.payment?.status ?? "-";
                  const paymentStatus = normalizeStatus(rawPaymentStatus);
                  const rawShipmentStatus = s.shipment?.status ?? s.status ?? "-";
                  const shipmentStatus = normalizeStatus(rawShipmentStatus);
                  const date = s.order?.createdAt ?? s.createdAt ?? s.date ?? null;
                  const amount = computePayout(s);
                  const itemsCount = Array.isArray(s.items) ? s.items.reduce((sum: number, it: any) => sum + (it.quantity ?? it.qty ?? 0), 0) : 0;

                  return (
                    <tr key={id} className="border-t border-gray-100">
                      <td className="px-3 py-3 font-medium text-gray-900">{id}</td>
                      <td className="px-3 py-3">{customer}</td>
                      <td className="px-3 py-3">{paymentMethod}</td>
                      <td className="px-3 py-3">{paymentStatus === '-' ? '-' : (PAYMENT_STATUS_LABEL_VI[paymentStatus] ?? paymentStatus)}</td>
                      <td className="px-3 py-3">
                        <span className={clsx("inline-flex rounded-full px-2 py-1 text-xs font-medium", getStatusColor(shipmentStatus))}>
                          {shipmentStatus === '-' ? '-' : (STATUS_LABEL_VI[shipmentStatus] ?? shipmentStatus)}
                        </span>
                      </td>
                      <td className="px-3 py-3">{date ? new Date(date).toLocaleDateString() : "-"}</td>
                      <td className="px-3 py-3">{fmt.format(amount)}</td>
                      <td className="px-3 py-3">{itemsCount}</td>
                      <td className="px-3 py-3">
                        <button onClick={() => openDetails(s)} className="text-sm text-blue-600 hover:underline">Xem</button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Details modal */}
      {selectedSubOrder && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/30" onClick={closeDetails} />
          <div className="relative z-10 w-full max-w-4xl rounded-lg bg-white p-6 shadow-xl max-h-[80vh] overflow-y-auto">
            <div className="flex items-start justify-between">
              <h3 className="text-lg font-semibold">Chi tiết SubOrder #{selectedSubOrder.subOrderId ?? selectedSubOrder.sub_order_id}</h3>
              <button onClick={closeDetails} className="text-sm text-gray-500 hover:underline">Đóng</button>
            </div>
            <div className="mt-4 space-y-4 text-sm">
              <div className="rounded-lg bg-gray-50 p-4">
                <h4 className="font-semibold mb-2">Thông tin người mua</h4>
                <div className="text-gray-700">{selectedSubOrder.order?.buyer?.email ?? '-'}</div>
              </div>

              <div className="rounded-lg bg-white border p-4">
                <h4 className="font-semibold mb-2">Thanh toán</h4>
                <div className="grid grid-cols-2 gap-2">
                  <div className="text-gray-500">Phương thức</div>
                  <div className="font-medium">{selectedSubOrder.order?.payment?.paymentMethod ?? '-'}</div>
                  <div className="text-gray-500">Trạng thái</div>
                  <div className="font-medium">{PAYMENT_STATUS_LABEL_VI[normalizeStatus(selectedSubOrder.order?.payment?.status)] ?? (selectedSubOrder.order?.payment?.status ?? '-')}</div>
                  <div className="text-gray-500">Subtotal</div>
                  <div className="font-medium">{fmt.format(asNumber(selectedSubOrder.subtotal ?? 0))}</div>
                  <div className="text-gray-500">Shipping Fee</div>
                  <div className="font-medium">{fmt.format(asNumber(selectedSubOrder.shippingFee ?? 0))}</div>
                  <div className="text-gray-500">Tổng rút về</div>
                  <div className="font-semibold text-green-600">{fmt.format(computePayout(selectedSubOrder))}</div>
                </div>
              </div>

              <div className="rounded-lg bg-white border p-4">
                <h4 className="font-semibold mb-2">Vận chuyển</h4>
                <div className="grid grid-cols-2 gap-2">
                  <div className="text-gray-500">Mã vận đơn</div>
                  <div className="font-medium">{selectedSubOrder.shipment?.trackingCode ?? '-'}</div>
                  <div className="text-gray-500">Trạng thái</div>
                  <div className="font-medium">{STATUS_LABEL_VI[normalizeStatus(selectedSubOrder.shipment?.status)] ?? (selectedSubOrder.shipment?.status ?? '-')}</div>
                  <div className="text-gray-500">Ghi chú</div>
                  <div className="font-medium">{selectedSubOrder.shipment?.note ?? '-'}</div>
                </div>
              </div>

              <div className="rounded-lg bg-white border p-4">
                <h4 className="font-semibold mb-2">Sản phẩm</h4>
                <div className="space-y-2">
                  {Array.isArray(selectedSubOrder.items) && selectedSubOrder.items.map((it: any) => {
                    const img = it.variant?.colorImageUrl ?? it.variant?.product?.galleryImages?.[0]?.imageUrl ?? null;
                    return (
                      <div key={it.itemId ?? it.item_id} className="flex items-center gap-4 border rounded p-2">
                        {img ? (
                          <img src={img} alt="product" className="w-12 h-12 object-cover rounded" />
                        ) : (
                          <div className="w-12 h-12 bg-gray-200 rounded flex items-center justify-center text-xs text-gray-500">No img</div>
                        )}
                        <div className="flex-1">
                          <div className="font-medium">{it.variant?.product?.name ?? '-'}</div>
                          <div className="text-xs text-gray-500">{it.variant?.colorName ?? ''} / {it.variant?.sizeName ?? ''}</div>
                        </div>
                        <div className="text-right">
                          <div className="text-xs text-gray-500">x{it.quantity ?? it.qty ?? 0}</div>
                          <div className="font-medium">{fmt.format(asNumber(it.priceAtOrder ?? it.price_at_order ?? 0))}</div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Withdraw Summary Modal */}
      {showWithdrawModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/30" onClick={() => !settlementLoading && setShowWithdrawModal(false)} />
          <div className="relative z-10 w-full max-w-3xl rounded-lg bg-white p-6 shadow-xl max-h-[80vh] overflow-y-auto">
            <div className="flex items-start justify-between mb-4">
              <h3 className="text-lg font-semibold">Tổng hợp rút tiền</h3>
              <button 
                onClick={() => setShowWithdrawModal(false)} 
                disabled={settlementLoading}
                className="text-sm text-gray-500 hover:underline"
              >
                Đóng
              </button>
            </div>

            <div className="mb-4 p-4 bg-green-50 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-gray-600">Tổng số đơn đủ điều kiện</span>
                <span className="text-lg font-bold text-green-700">{eligibleSubOrders.length} đơn</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Tổng tiền rút về</span>
                <span className="text-2xl font-bold text-green-600">{fmt.format(totalWithdrawAmount)}</span>
              </div>
              <div className="mt-2 text-xs text-gray-500">
                * Bao gồm: Subtotal + Phí vận chuyển
              </div>
            </div>

            <div className="mb-4">
              <h4 className="font-semibold mb-2 text-sm">Danh sách đơn hàng ({eligibleSubOrders.length})</h4>
              <div className="max-h-60 overflow-y-auto border rounded">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 sticky top-0">
                    <tr className="text-left text-gray-500">
                      <th className="px-3 py-2 font-medium">SubOrder ID</th>
                      <th className="px-3 py-2 font-medium">Customer</th>
                      <th className="px-3 py-2 font-medium">Payment</th>
                      <th className="px-3 py-2 font-medium text-right">Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    {eligibleSubOrders.map((s: any) => {
                      const id = s.subOrderId ?? s.sub_order_id ?? s.id;
                      const customer = s.order?.buyer?.email ?? s.customer ?? "-";
                      const paymentMethod = s.order?.payment?.paymentMethod ?? s.payment?.paymentMethod ?? "-";
                      const amount = computePayout(s);
                      
                      return (
                        <tr key={id} className="border-t border-gray-100">
                          <td className="px-3 py-2 font-medium">#{id}</td>
                          <td className="px-3 py-2 text-xs">{customer}</td>
                          <td className="px-3 py-2 text-xs">
                            <span className={clsx(
                              "px-2 py-1 rounded text-xs",
                              paymentMethod === 'COD' ? "bg-blue-100 text-blue-700" : "bg-purple-100 text-purple-700"
                            )}>
                              {paymentMethod}
                            </span>
                          </td>
                          <td className="px-3 py-2 text-right font-medium">{fmt.format(amount)}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowWithdrawModal(false)}
                disabled={settlementLoading}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Hủy
              </button>
              <button
                onClick={handleConfirmWithdraw}
                disabled={settlementLoading}
                className={clsx(
                  "px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors",
                  settlementLoading && "opacity-50 cursor-not-allowed"
                )}
              >
                {settlementLoading ? 'Đang xử lý...' : '✓ Đồng ý rút'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* History Modal */}
      {showHistoryModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/30" onClick={() => setShowHistoryModal(false)} />
          <div className="relative z-10 w-full max-w-5xl rounded-lg bg-white p-6 shadow-xl max-h-[80vh] overflow-y-auto">
            <div className="flex items-start justify-between mb-4">
              <h3 className="text-lg font-semibold">📋 Lịch sử rút tiền</h3>
              <button 
                onClick={() => setShowHistoryModal(false)} 
                className="text-sm text-gray-500 hover:underline"
              >
                Đóng
              </button>
            </div>

            {settlementsLoading ? (
              <div className="py-8 text-center text-gray-500">Đang tải...</div>
            ) : settlements.length === 0 ? (
              <div className="py-8 text-center text-gray-500">Chưa có lịch sử rút tiền</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full border-collapse text-sm">
                  <thead className="bg-gray-50">
                    <tr className="text-left text-gray-500">
                      <th className="px-3 py-2 font-medium">Settlement ID</th>
                      <th className="px-3 py-2 font-medium">Số tiền</th>
                      <th className="px-3 py-2 font-medium">Trạng thái</th>
                      <th className="px-3 py-2 font-medium">Ngày tạo</th>
                      <th className="px-3 py-2 font-medium">Ngày thanh toán</th>
                      <th className="px-3 py-2 font-medium">Ghi chú</th>
                    </tr>
                  </thead>
                  <tbody>
                    {settlements.map((settlement: any) => (
                      <tr key={settlement.settlementId} className="border-t border-gray-100">
                        <td className="px-3 py-3 font-medium text-gray-900">#{settlement.settlementId}</td>
                        <td className="px-3 py-3 font-semibold text-green-600">
                          {fmt.format(Number(settlement.totalAmount))}
                        </td>
                        <td className="px-3 py-3">
                          <span className={clsx(
                            "inline-flex rounded-full px-2 py-1 text-xs font-medium",
                            getStatusBadgeColor(settlement.status)
                          )}>
                            {getStatusLabel(settlement.status)}
                          </span>
                        </td>
                        <td className="px-3 py-3 text-gray-600">
                          {settlement.createdAt ? new Date(settlement.createdAt).toLocaleString('vi-VN') : '-'}
                        </td>
                        <td className="px-3 py-3 text-gray-600">
                          {settlement.paidAt ? new Date(settlement.paidAt).toLocaleString('vi-VN') : '-'}
                        </td>
                        <td className="px-3 py-3 text-gray-600 text-xs">
                          {settlement.note || '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </section>
  );
}