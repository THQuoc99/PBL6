import { useState } from "react";
import { ToolbarButton } from "../../index";

type Promo = { id: string; code: string; type: "percent" | "fixed"; value: number; active: boolean };

const sample: Promo[] = [
  { id: "P1", code: "WELCOME10", type: "percent", value: 10, active: true },
  { id: "P2", code: "SHIPFREE", type: "fixed", value: 0, active: false },
];

export default function PromotionsPage() {
  const [promos, setPromos] = useState<Promo[]>(sample);
  const [showForm, setShowForm] = useState(false);
  const [code, setCode] = useState("");
  const [type, setType] = useState<"percent" | "fixed">("percent");
  const [value, setValue] = useState<number>(0);

  const addPromo = () => {
    if (!code) return alert("Code required");
    setPromos([{ id: `P${Date.now()}`, code, type, value, active: true }, ...promos]);
    setShowForm(false);
    setCode("");
    setValue(0);
  };

  const toggleActive = (id: string) => setPromos(promos.map(p => p.id === id ? { ...p, active: !p.active } : p));

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Promotions & Discounts</h2>
        <ToolbarButton onClick={() => setShowForm(s => !s)}>{showForm ? 'Close' : 'New Promotion'}</ToolbarButton>
      </div>

      {showForm && (
        <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
          <div className="grid gap-3 sm:grid-cols-3">
            <input value={code} onChange={e => setCode(e.target.value)} placeholder="Code" className="rounded-xl border p-2" />
            <select value={type} onChange={e => setType(e.target.value as any)} className="rounded-xl border p-2">
              <option value="percent">Percent</option>
              <option value="fixed">Fixed</option>
            </select>
            <input value={value} onChange={e => setValue(Number(e.target.value))} type="number" className="rounded-xl border p-2" placeholder="Value" />
          </div>
          <div className="mt-3 flex gap-2">
            <button onClick={addPromo} className="rounded-xl bg-gray-900 px-4 py-2 text-white">Add</button>
            <button onClick={() => setShowForm(false)} className="rounded-xl border px-4 py-2">Cancel</button>
          </div>
        </div>
      )}

      <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500">
                <th className="px-3 py-2 font-medium">Code</th>
                <th className="px-3 py-2 font-medium">Type</th>
                <th className="px-3 py-2 font-medium">Value</th>
                <th className="px-3 py-2 font-medium">Active</th>
              </tr>
            </thead>
            <tbody>
              {promos.map(p => (
                <tr key={p.id} className="border-t border-gray-100">
                  <td className="px-3 py-3 font-medium text-gray-900">{p.code}</td>
                  <td className="px-3 py-3">{p.type}</td>
                  <td className="px-3 py-3">{p.type === 'percent' ? `${p.value}%` : `${p.value}`}</td>
                  <td className="px-3 py-3">
                    <button onClick={() => toggleActive(p.id)} className="rounded-lg border border-gray-200 px-3 py-1 text-sm">
                      {p.active ? 'Disable' : 'Enable'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}