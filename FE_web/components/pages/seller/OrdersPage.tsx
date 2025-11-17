import { useState } from "react";
import clsx from "clsx";
import { Order, OrderStatus } from "../../../types";
import { ToolbarButton } from "../../index";

interface OrdersPageProps {
  orders: Order[];
  setOrders: (orders: Order[]) => void;
  query: string;
}

export default function OrdersPage({ orders, setOrders, query }: OrdersPageProps) {
  const [statusTab, setStatusTab] = useState<"All" | OrderStatus>("All");
  const [selected, setSelected] = useState<Record<string, boolean>>({});

  const filtered = orders.filter((o) => {
    const matchQuery =
      o.id.toLowerCase().includes(query.toLowerCase()) ||
      o.customer.toLowerCase().includes(query.toLowerCase()) ||
      o.status.toLowerCase().includes(query.toLowerCase());
    const matchStatus = statusTab === "All" ? true : o.status === statusTab;
    return matchQuery && matchStatus;
  });

  const allChecked = filtered.length > 0 && filtered.every((o) => selected[o.id]);
  const toggleAll = (v: boolean) => {
    const copy = { ...selected };
    filtered.forEach((o) => (copy[o.id] = v));
    setSelected(copy);
  };

  const bulkUpdate = (to: OrderStatus) => {
    const ids = Object.keys(selected).filter((k) => selected[k]);
    if (!ids.length) {
      alert("No orders selected");
      return;
    }
    setOrders(orders.map((o) => (ids.includes(o.id) ? { ...o, status: to } : o)));
    setSelected({});
  };

  // Format currency
  const fmt = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });

  // Get status color
  const getStatusColor = (status: OrderStatus) => {
    switch (status) {
      case "Processing": return "text-blue-600 bg-blue-50";
      case "Shipped": return "text-orange-600 bg-orange-50";
      case "Delivered": return "text-green-600 bg-green-50";
      case "Cancelled": return "text-red-600 bg-red-50";
      default: return "text-gray-600 bg-gray-50";
    }
  };

  return (
    <section className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        {["All", "Processing", "Shipped", "Delivered", "Cancelled"].map((t) => (
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
            {t}
          </button>
        ))}
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
                <th className="px-3 py-2 font-medium">Status</th>
                <th className="px-3 py-2 font-medium">Date</th>
                <th className="px-3 py-2 font-medium">Amount</th>
                <th className="px-3 py-2 font-medium">Items</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((o) => (
                <tr key={o.id} className="border-t border-gray-100">
                  <td className="px-3 py-3">
                    <input
                      type="checkbox"
                      checked={selected[o.id] || false}
                      onChange={(e) => setSelected({ ...selected, [o.id]: e.target.checked })}
                      className="rounded border-gray-300"
                    />
                  </td>
                  <td className="px-3 py-3 font-medium text-gray-900">{o.id}</td>
                  <td className="px-3 py-3">{o.customer}</td>
                  <td className="px-3 py-3">
                    <span className={clsx("inline-flex rounded-full px-2 py-1 text-xs font-medium", getStatusColor(o.status))}>
                      {o.status}
                    </span>
                  </td>
                  <td className="px-3 py-3">{new Date(o.date).toLocaleDateString()}</td>
                  <td className="px-3 py-3">{fmt.format(o.amount)}</td>
                  <td className="px-3 py-3">{o.items.reduce((sum, item) => sum + item.qty, 0)} items</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}