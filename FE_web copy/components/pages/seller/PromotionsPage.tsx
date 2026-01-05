import { useState, useEffect } from "react";
import { ToolbarButton } from "../../index";
import { useCreateStoreVoucher, useUpdateVoucher } from "../../../hooks/discount/discount";
import { useStoreAuth } from "../../../hooks/store/storeAuth";
import { useStoreVouchers } from "../../../hooks/discount/discount";

type Promo = {
  id: string;
  code: string;
  type?: 'platform' | 'store';
  discount_type: 'percent' | 'fixed' | 'freeship';
  discount_value: number; // decimal
  max_discount?: number | null; // decimal
  min_order_amount: number; // decimal
  start_date: string; // ISO date
  end_date: string; // ISO date
  per_user_limit: number;
  active: boolean;
};

// Start with empty list; we'll load store vouchers from server
const sample: Promo[] = [];

export default function PromotionsPage() {
  const [promos, setPromos] = useState<Promo[]>(sample);
  const [showForm, setShowForm] = useState(false);

  const [code, setCode] = useState("");
  const [ptype, setPtype] = useState<'platform' | 'store'>('store');
  const [discountType, setDiscountType] = useState<'percent' | 'fixed' | 'freeship'>('percent');
  const [discountValue, setDiscountValue] = useState<number>(0);
  const [maxDiscount, setMaxDiscount] = useState<number | ''>('');
  const [minOrderAmount, setMinOrderAmount] = useState<number>(0);
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [perUserLimit, setPerUserLimit] = useState<number>(1);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [isActive, setIsActive] = useState<boolean>(true);

  const { createStoreVoucher, creating } = useCreateStoreVoucher();
  const { updateVoucher, updating } = useUpdateVoucher();
  const { store } = useStoreAuth();
  const { vouchers: storeVouchers, loading: loadingVouchers, error: storeVouchersError, refetch: refetchStoreVouchers } = useStoreVouchers(store?.storeId);
  const addPromo = async () => {
    if (!code) return alert("Vui lòng nhập mã");
    if (!discountType) return alert('Vui lòng chọn loại khuyến mãi');
    if (!minOrderAmount) return alert('Vui lòng nhập giá trị tối thiểu đơn hàng');
    if (!startDate || !endDate) return alert('Vui lòng chọn ngày bắt đầu và kết thúc');

    const storeId = store?.storeId;
    if (!storeId) return alert('Không tìm thấy thông tin cửa hàng. Vui lòng đăng nhập hoặc chọn cửa hàng.');

    const payload: any = {
      code,
      // Graphene fields are exposed as camelCase in GraphQL schema
      discountType: discountType === 'percent' ? 'percent' : discountType === 'fixed' ? 'fixed' : 'freeship',
      discountValue: Number(discountValue),
      maxDiscount: maxDiscount === '' ? null : Number(maxDiscount),
      minOrderAmount: Number(minOrderAmount),
      startDate,
      endDate,
      perUserLimit: Number(perUserLimit),
      isActive,
    };

    try {
      if (editingId) {
        const res = await updateVoucher(editingId, payload);
        if (!res || !res.ok) {
          alert('Cập nhật khuyến mãi thất bại');
          return;
        }

        const updated = res.voucher;
        setPromos(prev => prev.map(p => p.id === String(updated.id ?? updated.voucherId ?? editingId) ? ({
          id: String(updated.id ?? updated.voucherId ?? editingId),
          code: updated.code ?? code,
          type: 'store',
          discount_type: (String(updated.discountType || '').toLowerCase() === 'percent') ? 'percent' : (String(updated.discountType || '').toLowerCase() === 'freeship' ? 'freeship' : 'fixed'),
          discount_value: Number(updated.discountValue ?? payload.discountValue),
          max_discount: updated.maxDiscount != null ? Number(updated.maxDiscount) : (maxDiscount === '' ? null : Number(maxDiscount)),
          min_order_amount: Number(updated.minOrderAmount ?? payload.minOrderAmount),
          start_date: updated.startDate ?? startDate,
          end_date: updated.endDate ?? endDate,
          per_user_limit: Number(updated.perUserLimit ?? payload.perUserLimit),
          active: Boolean(updated.isActive ?? isActive),
        }) : p));

        setEditingId(null);
        setShowForm(false);
        alert('Cập nhật khuyến mãi thành công');
        return;
      }

      // Create flow
      const res = await createStoreVoucher(storeId, payload);
      if (!res || !res.ok) {
        alert('Tạo khuyến mãi thất bại');
        return;
      }

      const created = res.voucher || {};
      const newPromo: Promo = {
        id: String(created.id ?? created.voucherId ?? `P${Date.now()}`),
        code: created.code ?? code,
        type: 'store',
        discount_type: (String(created.discountType || discountType).toLowerCase() === 'percent') ? 'percent' : (String(created.discountType || discountType).toLowerCase() === 'freeship' ? 'freeship' : 'fixed'),
        discount_value: Number(created.discountValue ?? discountValue),
        max_discount: created.maxDiscount != null ? Number(created.maxDiscount) : (maxDiscount === '' ? null : Number(maxDiscount)),
        min_order_amount: Number(created.minOrderAmount ?? minOrderAmount),
        start_date: created.startDate ?? startDate,
        end_date: created.endDate ?? endDate,
        per_user_limit: Number(created.perUserLimit ?? perUserLimit),
        active: Boolean(created.isActive ?? isActive),
      };

      setPromos(prev => [newPromo, ...prev]);
      setShowForm(false);
      setCode("");
      setDiscountType('percent');
      setDiscountValue(0);
      setMaxDiscount('');
      setMinOrderAmount(0);
      setStartDate('');
      setEndDate('');
      setPerUserLimit(1);

      alert('Tạo khuyến mãi thành công');
    } catch (err: any) {
      console.error('createStoreVoucher error:', err);
      alert('Tạo khuyến mãi thất bại: ' + (err?.message || 'Lỗi server'));
    }
  };

  const toggleActive = async (id: string) => {
    const target = promos.find(p => p.id === id);
    if (!target) return;
    const newActive = !target.active;

    try {
      // attempt to update on server
      await updateVoucher(id, { isActive: newActive });
    } catch (err) {
      console.error('Failed to update active state:', err);
      alert('Cập nhật trạng thái thất bại');
      return;
    }

    setPromos(promos.map(p => p.id === id ? { ...p, active: newActive } : p));
  };

  const startEdit = (v: Promo) => {
    setEditingId(v.id);
    setShowForm(true);
    setCode(v.code);
    setDiscountType(v.discount_type);
    setDiscountValue(v.discount_value);
    setMaxDiscount(v.max_discount ?? '');
    setMinOrderAmount(v.min_order_amount);
    setStartDate(v.start_date);
    setEndDate(v.end_date);
    setPerUserLimit(v.per_user_limit);
    setIsActive(v.active);
  };

  useEffect(() => {
    if (!storeVouchers) return;
    // Map service Voucher -> Promo
    const mapped: Promo[] = storeVouchers.map((v: any) => ({
      id: String(v.voucherId ?? v.id),
      code: v.code,
      type: 'store',
      discount_type: (String(v.discountType || '').toLowerCase() === 'percent') ? 'percent' : (String(v.discountType || '').toLowerCase() === 'freeship' ? 'freeship' : 'fixed'),
      discount_value: Number(v.discountValue ?? v.discount_value ?? 0),
      max_discount: v.maxDiscount != null ? Number(v.maxDiscount) : (v.max_discount != null ? Number(v.max_discount) : null),
      min_order_amount: Number(v.minOrderAmount ?? v.min_order_amount ?? 0),
      start_date: v.startDate ?? v.start_date ?? '',
      end_date: v.endDate ?? v.end_date ?? '',
      per_user_limit: Number(v.perUserLimit ?? v.per_user_limit ?? 1),
      active: Boolean(v.isActive ?? true),
    }));

    setPromos(mapped);
  }, [storeVouchers]);

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Chương trình khuyến mãi</h2>
        <ToolbarButton onClick={() => setShowForm(s => !s)}>{showForm ? 'Đóng' : 'Tạo khuyến mãi'}</ToolbarButton>
      </div>

      {showForm && (
        <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
          <div className="grid gap-3 sm:grid-cols-3">
            <div>
              <label className="block text-sm text-gray-600 mb-1">Mã khuyến mãi</label>
              <input value={code} onChange={e => setCode(e.target.value)} placeholder="VD: WELCOME10" className="rounded-xl border p-2 w-full" />
            </div>

            <div>
              <label className="block text-sm text-gray-600 mb-1">Loại</label>
              <input value="Cửa hàng" disabled className="rounded-xl border p-2 w-full bg-gray-50 text-gray-700" />
              <input type="hidden" name="type" value={ptype} />
            </div>

            <div>
              <label className="block text-sm text-gray-600 mb-1">Hình thức giảm</label>
              <select value={discountType} onChange={e => setDiscountType(e.target.value as any)} className="rounded-xl border p-2 w-full">
                <option value="percent">Phần trăm</option>
                <option value="fixed">Cố định</option>
                <option value="freeship">Miễn phí vận chuyển</option>
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-600 mb-1">Giá trị giảm</label>
              <input value={discountValue} onChange={e => setDiscountValue(Number(e.target.value))} type="number" step="0.01" className="rounded-xl border p-2 w-full" placeholder="Nhập giá trị" />
            </div>

            <div>
              <label className="block text-sm text-gray-600 mb-1">Giảm tối đa (tùy chọn)</label>
              <input value={maxDiscount as any} onChange={e => setMaxDiscount(e.target.value === '' ? '' : Number(e.target.value))} type="number" step="0.01" className="rounded-xl border p-2 w-full" placeholder="Ví dụ: 100000" />
            </div>

            <div>
              <label className="block text-sm text-gray-600 mb-1">Giá trị tối thiểu đơn hàng</label>
              <input value={minOrderAmount} onChange={e => setMinOrderAmount(Number(e.target.value))} type="number" step="0.01" className="rounded-xl border p-2 w-full" placeholder="Ví dụ: 500000" />
            </div>

            <div>
              <label className="block text-sm text-gray-600 mb-1">Ngày bắt đầu</label>
              <input value={startDate} onChange={e => setStartDate(e.target.value)} type="date" className="rounded-xl border p-2 w-full" />
            </div>

            <div>
              <label className="block text-sm text-gray-600 mb-1">Ngày kết thúc</label>
              <input value={endDate} onChange={e => setEndDate(e.target.value)} type="date" className="rounded-xl border p-2 w-full" />
            </div>

            <div>
              <label className="block text-sm text-gray-600 mb-1">Giới hạn/người</label>
              <input value={perUserLimit} onChange={e => setPerUserLimit(Number(e.target.value))} type="number" min={1} className="rounded-xl border p-2 w-full" placeholder="Số lần 1 người có thể dùng" />
            </div>
          </div>
          <div className="mt-3 flex gap-2">
            <button onClick={addPromo} className="rounded-xl bg-gray-900 px-4 py-2 text-white">{editingId ? 'Lưu' : 'Thêm'}</button>
            <button onClick={() => { setShowForm(false); setEditingId(null); setCode(''); setDiscountType('percent'); setDiscountValue(0); setMaxDiscount(''); setMinOrderAmount(0); setStartDate(''); setEndDate(''); setPerUserLimit(1); setIsActive(true); }} className="rounded-xl border px-4 py-2">Hủy</button>
          </div>
        </div>
      )}

      <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500">
                <th className="px-3 py-2 font-medium">Mã</th>
                <th className="px-3 py-2 font-medium">Loại</th>
                <th className="px-3 py-2 font-medium">Giảm</th>
                <th className="px-3 py-2 font-medium">Tối đa</th>
                <th className="px-3 py-2 font-medium">Tối thiểu đơn hàng</th>
                <th className="px-3 py-2 font-medium">Bắt đầu</th>
                <th className="px-3 py-2 font-medium">Kết thúc</th>
                <th className="px-3 py-2 font-medium">Giới hạn/người</th>
                <th className="px-3 py-2 font-medium">Trạng thái</th>
              </tr>
            </thead>
            <tbody>
              {promos.map(p => (
                <tr key={p.id} className="border-t border-gray-100">
                  <td className="px-3 py-3 font-medium text-gray-900">{p.code}</td>
                  <td className="px-3 py-3">{p.type ? (p.type === 'platform' ? 'Nền tảng' : 'Cửa hàng') : '-'}</td>
                  <td className="px-3 py-3">{p.discount_type === 'percent' ? `${p.discount_value}%` : p.discount_type === 'freeship' ? 'Miễn phí vận chuyển' : `${p.discount_value}`}</td>
                  <td className="px-3 py-3">{p.max_discount ? p.max_discount.toLocaleString() : '-'}</td>
                  <td className="px-3 py-3">{p.min_order_amount.toLocaleString()}</td>
                  <td className="px-3 py-3">{p.start_date}</td>
                  <td className="px-3 py-3">{p.end_date}</td>
                  <td className="px-3 py-3">{p.per_user_limit}</td>
                  <td className="px-3 py-3">
                    <div className="flex items-center gap-2">
                      <button onClick={() => startEdit(p)} className="rounded-lg border border-gray-200 px-3 py-1 text-sm flex items-center gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M11 5h6m2 2v6m0 0l-9 9-4 1 1-4 9-9z" />
                        </svg>
                        <span>Sửa</span>
                      </button>

                      <button onClick={() => toggleActive(p.id)} className="rounded-lg border border-gray-200 px-3 py-1 text-sm">
                        {p.active ? 'Vô hiệu hóa' : 'Kích hoạt'}
                      </button>
                    </div>
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