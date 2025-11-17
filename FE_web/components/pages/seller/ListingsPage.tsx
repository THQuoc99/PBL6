import { useState } from "react";
import { ToolbarButton } from "../../index";

type Listing = { id: string; marketplace: string; product: string; synced: boolean };

const sample: Listing[] = [
  { id: "L1", marketplace: "Shopee", product: "Premium Headphones", synced: true },
  { id: "L2", marketplace: "Lazada", product: "Wireless Mouse", synced: false },
  { id: "L3", marketplace: "Tiki", product: "Gaming Keyboard", synced: false },
];

export default function ListingsPage() {
  const [listings, setListings] = useState<Listing[]>(sample);
  const toggleSync = (id: string) => {
    setListings(listings.map(l => l.id === id ? { ...l, synced: !l.synced } : l));
  };

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Listings Management</h2>
        <ToolbarButton onClick={() => alert('Trigger marketplace sync (simulated)')}>Sync All</ToolbarButton>
      </div>

      <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500">
                <th className="px-3 py-2 font-medium">Marketplace</th>
                <th className="px-3 py-2 font-medium">Product</th>
                <th className="px-3 py-2 font-medium">Status</th>
                <th className="px-3 py-2 font-medium">Action</th>
              </tr>
            </thead>
            <tbody>
              {listings.map(l => (
                <tr key={l.id} className="border-t border-gray-100">
                  <td className="px-3 py-3 font-medium text-gray-900">{l.marketplace}</td>
                  <td className="px-3 py-3">{l.product}</td>
                  <td className="px-3 py-3">{l.synced ? <span className="text-green-600">Synced</span> : <span className="text-gray-500">Not synced</span>}</td>
                  <td className="px-3 py-3">
                    <button onClick={() => toggleSync(l.id)} className="rounded-lg border border-gray-200 px-3 py-1 text-sm">
                      {l.synced ? 'Unpublish' : 'Publish'}
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