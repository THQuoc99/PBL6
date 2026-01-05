import { useState, useEffect } from "react";
import clsx from "clsx";
import { Order, OrderStatus } from "../../../types";
import { ToolbarButton } from "../../index";
import useSubOrdersByStore from "../../../hooks/order/storeOrder";
import { useStoreAuth } from '../../../hooks/store/storeAuth';

interface OrdersPageProps {
  orders: Order[];
  setOrders: (orders: Order[]) => void;
  query: string;
  storeId?: string; // optional: when provided, component will load sub-orders from API
}

export default function OrdersPage({ orders, setOrders, query, storeId }: OrdersPageProps) {
  const [statusTab, setStatusTab] = useState<"All" | string>("All");
  const [selected, setSelected] = useState<Record<string, boolean>>({});
  const [localSource, setLocalSource] = useState<any[]>([]);
  const [selectedSubOrder, setSelectedSubOrder] = useState<any | null>(null);

  // get current store from auth and load sub-orders for that store
  const { store } = useStoreAuth();
  const storeIdFromAuth = store?.storeId;
  const activeStoreId = storeId ?? storeIdFromAuth;
  // isPayment = false: OrdersPage cần xem tất cả suborder của store
  const { data: subOrdersData, loading: loadingSubOrders, refetch: refetchSubOrders, confirmSubOrder } = useSubOrdersByStore(activeStoreId, false);
  // define shipment status tabs (use values from Shipment.STATUS_CHOICES)
  const SHIPMENT_STATUS_TABS = [
    "All",
    "pending",
    "shipping",
    "out_for_delivery",
    "completed",
    "cancelled",
    "returned",
  ];

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

  const normalizeStatus = (s: any) => {
    if (!s && s !== 0) return '';
    try {
      const str = String(s).trim();
      // handle uppercase server values like 'PENDING' or 'OUT_FOR_DELIVERY'
      return str.toLowerCase().replace(/\s+/g, '_');
    } catch {
      return '';
    }
  };

  // decide data source: API subOrders (when storeId or authenticated store) or provided orders prop
  const source = activeStoreId ? (subOrdersData || []) : orders;

  // keep a local editable copy when using API data (for optimistic confirm)
  useEffect(() => {
    setLocalSource(source.map((s: any) => ({ ...s })));
  }, [source]);

  const displaySource = activeStoreId ? localSource : orders;

  // Precompute counts per shipment status for UI badges
  const statusCounts: Record<string, number> = (displaySource || []).reduce((acc: Record<string, number>, o: any) => {
    const raw = o.shipment?.status ?? o.status ?? '';
    const s = normalizeStatus(raw) || 'unknown';
    acc[s] = (acc[s] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const filtered = displaySource.filter((o: any) => {
    // Normalize fields for both shapes
    const id = o.subOrderId ?? o.id;
    const customer = (o.order?.buyer?.email) || o.customer || "";
    const rawShipmentStatus = o.shipment?.status ?? o.status ?? "";
    const shipmentStatus = normalizeStatus(rawShipmentStatus);
    const rawPaymentStatus = o.order?.payment?.status ?? o.payment?.status ?? "";
    const paymentStatus = normalizeStatus(rawPaymentStatus);

    const q = query?.toLowerCase() || "";
    const matchQuery =
      String(id).toLowerCase().includes(q) ||
      String(customer).toLowerCase().includes(q) ||
      String(shipmentStatus).toLowerCase().includes(q) ||
      String(paymentStatus).toLowerCase().includes(q);

    const matchStatus = statusTab === "All" ? true : shipmentStatus === statusTab;
    return matchQuery && matchStatus;
  });

  const allChecked = filtered.length > 0 && filtered.every((o) => selected[(o.subOrderId ?? o.id)]);
  const toggleAll = (v: boolean) => {
    const copy = { ...selected };
    filtered.forEach((o) => {
      const key = o.subOrderId ?? o.id;
      copy[key] = v;
    });
    setSelected(copy);
  };

  const bulkUpdate = (to: OrderStatus) => {
    const ids = Object.keys(selected).filter((k) => selected[k]);
    if (!ids.length) {
      alert("No orders selected");
      return;
    }
    if (activeStoreId) {
      alert('Bulk update is disabled when viewing store sub-orders.');
      setSelected({});
      return;
    }
    setOrders(orders.map((o) => (ids.includes(o.id) ? { ...o, status: to } : o)));
    setSelected({});
  };

  const handleConfirmShipment = async (subOrderId: any) => {
    if (!activeStoreId || typeof confirmSubOrder !== 'function') return;

    // optimistic update
    setLocalSource((prev) => prev.map((s: any) => {
      const id = s.subOrderId ?? s.id;
      if (String(id) === String(subOrderId)) {
        if (!s.shipment) s.shipment = {};
        s.shipment.status = 'shipping';
      }
      return { ...s };
    }));

    try {
      const res = await confirmSubOrder(subOrderId);
      // server confirmed — ensure latest data
      refetchSubOrders();
      const msg = res?.message ?? 'Đã xác nhận giao hàng';
      alert(msg);
    } catch (e) {
      // on error, re-fetch to revert optimistic change
      console.error('Confirm suborder failed', e);
      // show backend error message when available
      const errMsg = (e && (e.message || String(e))) || 'Xác nhận thất bại';
      alert(errMsg);
      refetchSubOrders();
    }
  };

  const openDetails = (subOrder: any) => setSelectedSubOrder(subOrder);
  const closeDetails = () => setSelectedSubOrder(null);

  // Format currency as VND (no $)
  const fmt = new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND", maximumFractionDigits: 0 });

  // Get status color
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

  return (
    <section className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        {SHIPMENT_STATUS_TABS.map((t) => {
          const label = t === 'All'
            ? `Tất cả (${(displaySource || []).length})`
            : `${STATUS_LABEL_VI[t] ?? t} (${statusCounts[t] ?? 0})`;
          return (
            <button
              key={t}
              onClick={() => setStatusTab(t as any)}
              className={clsx(
                "rounded-full border px-3 py-1.5 text-sm",
                statusTab === t 
                  ? "border-gray-900 bg-gray-900 text-white" 
                  : "border-gray-200 bg-white text-gray-700 hover:bg-gray-50"
              )}
            >
              {label}
            </button>
          );
        })}
      </div>

      {Object.values(selected).some(Boolean) && (
        <div className="flex items-center gap-2 rounded-xl bg-blue-50 p-3">
          <span className="text-sm text-blue-700">
            {Object.values(selected).filter(Boolean).length} selected
          </span>
          <div className="flex gap-2">
            <ToolbarButton onClick={() => bulkUpdate("Processing")}>
              Mark Processing
            </ToolbarButton>
            <ToolbarButton onClick={() => bulkUpdate("Shipped")}>
              Mark Shipped
            </ToolbarButton>
            <ToolbarButton onClick={() => bulkUpdate("Delivered")}>
              Mark Delivered
            </ToolbarButton>
          </div>
        </div>
      )}

      <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="text-left text-gray-500">
                <th className="px-3 py-2 font-medium">
                  <input
                    type="checkbox"
                    checked={allChecked}
                    onChange={(e) => toggleAll(e.target.checked)}
                    className="rounded border-gray-300"
                  />
                </th>
                <th className="px-3 py-2 font-medium">Order ID</th>
                <th className="px-3 py-2 font-medium">Customer</th>
                <th className="px-3 py-2 font-medium">Shipment Status</th>
                <th className="px-3 py-2 font-medium">Payment Method</th>
                <th className="px-3 py-2 font-medium">Payment Status</th>
                <th className="px-3 py-2 font-medium">Date</th>
                <th className="px-3 py-2 font-medium">Amount</th>
                <th className="px-3 py-2 font-medium">Items</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((o: any) => {
                const id = o.subOrderId ?? o.id;
                const customer = o.order?.buyer?.email ?? o.customer ?? "-";
                const rawShipmentStatus = o.shipment?.status ?? o.status ?? "-";
                const shipmentStatus = normalizeStatus(rawShipmentStatus) || '-';
                const paymentMethod = o.order?.payment?.paymentMethod ?? o.payment?.paymentMethod ?? "-";
                const rawPaymentStatus = o.order?.payment?.status ?? o.payment?.status ?? "-";
                const paymentStatus = normalizeStatus(rawPaymentStatus) || '-';
                const date = o.order?.createdAt ?? o.createdAt ?? o.date ?? null;
                const amount = o.subtotal ?? o.order?.totalAmount ?? o.amount ?? 0;
                const itemsCount = Array.isArray(o.items) ? o.items.reduce((sum: number, it: any) => sum + (it.quantity ?? it.qty ?? 0), 0) : 0;
                const firstImageUrl = Array.isArray(o.items) && (o.items[0]?.variant?.colorImageUrl ?? o.items[0]?.variant?.product?.galleryImages?.[0]?.imageUrl) || null;

                return (
                  <tr key={id} className="border-t border-gray-100">
                    <td className="px-3 py-3">
                      <input
                        type="checkbox"
                        checked={selected[id] || false}
                        onChange={(e) => setSelected({ ...selected, [id]: e.target.checked })}
                        className="rounded border-gray-300"
                      />
                    </td>
                    <td className="px-3 py-3 font-medium text-gray-900">{id}</td>
                    <td className="px-3 py-3">{customer}</td>
                    <td className="px-3 py-3">
                          <span className={clsx("inline-flex rounded-full px-2 py-1 text-xs font-medium", getStatusColor(shipmentStatus))}>
                            {shipmentStatus === '-' ? '-' : (STATUS_LABEL_VI[shipmentStatus] ?? shipmentStatus)}
                          </span>
                          {/* Show confirm button only when shipment pending AND either COD or VNPAY with completed payment */}
                          {(() => {
                            const paymentMethodRaw = o.order?.payment?.paymentMethod ?? o.payment?.paymentMethod ?? "";
                            const paymentMethod = String(paymentMethodRaw).toLowerCase();
                            const paymentStatus = normalizeStatus(o.order?.payment?.status ?? o.payment?.status ?? "");
                            const isCOD = paymentMethod === 'cod' || paymentMethod === 'cash_on_delivery' || paymentMethod === 'cash';
                            const isVNPAY = paymentMethod === 'vnpay';
                            const canConfirm = shipmentStatus === 'pending' && (isCOD || (isVNPAY && paymentStatus === 'completed'));

                            // determine tracking code presence (accept snake_case and camelCase and treat 'none' as absent)
                            const trackingCode = o.shipment?.trackingCode ?? o.shipment?.tracking_code ?? null;
                            const hasTracking = !!trackingCode && String(trackingCode).toLowerCase() !== 'none';

                            if (hasTracking) {
                              return <span className="ml-2 text-sm text-gray-500">Đã xác nhận</span>;
                            }

                            return canConfirm ? (
                              <button
                                onClick={() => handleConfirmShipment(id)}
                                className="ml-2 inline-flex items-center rounded px-2 py-1 text-xs bg-green-50 text-green-700 border border-green-100"
                              >
                                Xác nhận
                              </button>
                            ) : null;
                          })()}
                        </td>
                    <td className="px-3 py-3">{paymentMethod}</td>
                    <td className="px-3 py-3">{paymentStatus === '-' ? '-' : (PAYMENT_STATUS_LABEL_VI[paymentStatus] ?? paymentStatus)}</td>
                    <td className="px-3 py-3">{date ? new Date(date).toLocaleDateString() : "-"}</td>
                    <td className="px-3 py-3">{fmt.format(Number(amount))}</td>
                    <td className="px-3 py-3">
                      <div className="flex items-center gap-2">
                        {firstImageUrl ? (
                          <img src={firstImageUrl} alt="product" className="w-10 h-10 rounded object-cover" />
                        ) : null}
                        <span>{itemsCount} sp</span>
                      </div>
                    </td>
                    <td className="px-3 py-3">
                      <button onClick={() => openDetails(o)} className="text-sm text-blue-600 hover:underline">Xem</button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
      {/* Details modal / panel */}
      {selectedSubOrder && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/30" onClick={closeDetails} />
          <div className="relative z-10 w-full max-w-6xl rounded-lg bg-white p-6 shadow-xl max-h-[80vh] overflow-y-auto">
            <div className="flex items-start justify-between">
              <h3 className="text-lg font-semibold">Chi tiết SubOrder #{selectedSubOrder.subOrderId ?? selectedSubOrder.sub_order_id}</h3>
              <button onClick={closeDetails} className="text-sm text-gray-500">Đóng</button>
            </div>
            <div className="mt-4 grid grid-cols-1 gap-4 text-sm md:grid-cols-4">
              <div className="col-span-3 space-y-4">
                <div className="rounded-lg bg-gray-50 p-4 shadow-sm">
                  <h4 className="text-sm font-semibold mb-2">Thông tin người mua</h4>
                  <div className="text-sm text-gray-700">{selectedSubOrder.order?.buyer?.email ?? '-'}</div>
                </div>

                <div className="rounded-lg bg-white p-4 shadow-sm">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-semibold">Đơn hàng</h4>
                      <div className="text-xs text-gray-500">Order ID: {selectedSubOrder.order?.orderId ?? selectedSubOrder.order?.order_id ?? '-'}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm">Thanh toán</div>
                      <div className="text-xs text-gray-600">{selectedSubOrder.order?.payment?.paymentMethod ?? '-'}</div>
                      <div className="text-xs text-gray-600">{PAYMENT_STATUS_LABEL_VI[normalizeStatus(selectedSubOrder.order?.payment?.status)] ?? (selectedSubOrder.order?.payment?.status ?? '-')}</div>
                    </div>
                  </div>

                  <div className="mt-3 grid grid-cols-2 gap-3">
                    <div className="text-sm text-gray-600">Ship phí</div>
                    <div className="text-sm font-medium text-right">{fmt.format(Number(selectedSubOrder.shippingFee ?? selectedSubOrder.order?.shippingFee ?? 0))}</div>

                    <div className="text-sm text-gray-600">Tổng</div>
                    <div className="text-sm font-medium text-right">{fmt.format(Number(selectedSubOrder.subtotal ?? selectedSubOrder.order?.totalAmount ?? 0))}</div>
                  </div>
                </div>

                <div className="rounded-lg bg-white p-4 shadow-sm">
                  <h4 className="text-sm font-semibold mb-2">Sản phẩm</h4>
                  <div className="space-y-3">
                    {Array.isArray(selectedSubOrder.items) && selectedSubOrder.items.map((it: any) => {
                      const img = it.variant?.colorImageUrl ?? it.variant?.product?.galleryImages?.[0]?.imageUrl ?? null;
                      return (
                        <div key={it.itemId ?? it.item_id} className="flex items-center gap-4 rounded border p-3">
                          {img ? (
                            <img src={img} alt="product" className="w-14 h-14 object-cover rounded" />
                          ) : (
                            <div className="w-14 h-14 bg-gray-100 rounded flex items-center justify-center text-xs text-gray-400">No image</div>
                          )}

                          <div className="flex-1 min-w-0">
                            <div className="font-medium truncate">{it.variant?.product?.name ?? it.variant?.product?.productId ?? '—'}</div>
                            <div className="text-xs text-gray-500">SKU: {it.variant?.sku ?? it.variant?.variantId}</div>
                            <div className="mt-2 text-xs text-gray-600">Số lượng: <span className="font-medium">{it.quantity ?? it.qty}</span></div>
                          </div>

                          <div className="text-right w-28">
                            <div className="text-xs text-gray-500">Giá</div>
                            <div className="font-semibold">{fmt.format(Number(it.priceAtOrder ?? it.price_at_order ?? it.variant?.price ?? 0))}</div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>

              <aside className="space-y-4">
                <div className="rounded-lg bg-white p-4 shadow-sm">
                  <h4 className="text-sm font-semibold">Vận chuyển</h4>
                  <div className="mt-2 text-sm text-gray-700">
                    <div className="mb-1"><span className="text-gray-500">Mã vận đơn:</span> <span className="font-medium">{selectedSubOrder.shipment?.trackingCode ?? '-'}</span></div>
                    <div className="mb-1"><span className="text-gray-500">Trạng thái:</span> <span className="font-medium">{STATUS_LABEL_VI[normalizeStatus(selectedSubOrder.shipment?.status)] ?? (selectedSubOrder.shipment?.status ?? '-')}</span></div>
                    <div><span className="text-gray-500">Ghi chú:</span> <span className="font-medium">{selectedSubOrder.shipment?.note ?? '-'}</span></div>
                  </div>
                </div>

                <div className="rounded-lg bg-white p-4 shadow-sm">
                  <h4 className="text-sm font-semibold">Tóm tắt</h4>
                  <div className="mt-2 text-sm text-gray-700 grid grid-cols-1 gap-2">
                    <div className="flex justify-between"><span className="text-gray-500">Số mặt hàng</span><span className="font-medium">{Array.isArray(selectedSubOrder.items) ? selectedSubOrder.items.reduce((s: number, it: any) => s + (it.quantity ?? it.qty ?? 0), 0) : 0}</span></div>
                    <div className="flex justify-between"><span className="text-gray-500">Ship phí</span><span className="font-medium">{fmt.format(Number(selectedSubOrder.shippingFee ?? selectedSubOrder.order?.shippingFee ?? 0))}</span></div>
                    <div className="flex justify-between"><span className="text-gray-500">Tổng</span><span className="font-semibold">{fmt.format(Number(selectedSubOrder.subtotal ?? selectedSubOrder.order?.totalAmount ?? 0))}</span></div>
                  </div>
                </div>
              </aside>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}