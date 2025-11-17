import { useMemo, useState } from "react";

type Tx = { id: string; type: "sale" | "fee" | "refund" | "payout"; amount: number; date: string; status: "pending" | "completed" };

const sample: Tx[] = [
  { id: "T1", type: "sale", amount: 199.99, date: new Date().toISOString(), status: "completed" },
  { id: "T2", type: "fee", amount: -5.5, date: new Date().toISOString(), status: "completed" },
  { id: "T3", type: "payout", amount: 150.0, date: new Date().toISOString(), status: "pending" },
];

export default function PaymentsPage() {
  const [txs] = useState<Tx[]>(sample);
  const [filter, setFilter] = useState<string>("all");

  const visible = useMemo(() => txs.filter(t => filter === "all" ? true : t.type === filter), [txs, filter]);

  const fmt = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Payments & Transactions</h2>
        <div className="flex items-center gap-2">
          <select value={filter} onChange={e => setFilter(e.target.value)} className="rounded-xl border p-2">
            <option value="all">All</option>
            <option value="sale">Sales</option>
            <option value="fee">Fees</option>
            <option value="refund">Refunds</option>
            <option value="payout">Payouts</option>
          </select>
        </div>
      </div>

      <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500">
                <th className="px-3 py-2 font-medium">ID</th>
                <th className="px-3 py-2 font-medium">Type</th>
                <th className="px-3 py-2 font-medium">Amount</th>
                <th className="px-3 py-2 font-medium">Date</th>
                <th className="px-3 py-2 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {visible.map(t => (
                <tr key={t.id} className="border-t border-gray-100">
                  <td className="px-3 py-3 font-medium text-gray-900">{t.id}</td>
                  <td className="px-3 py-3">{t.type}</td>
                  <td className="px-3 py-3">{fmt.format(t.amount)}</td>
                  <td className="px-3 py-3">{new Date(t.date).toLocaleDateString()}</td>
                  <td className="px-3 py-3">{t.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}