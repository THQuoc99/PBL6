import React, { useState } from 'react';
import {
  Tag, Plus, Search, Filter, Calendar, Percent, DollarSign,
  Edit, Trash2, Power, X, Copy, TrendingUp, Users, CheckCircle
} from 'lucide-react';
import { useAdminVouchers } from '../../../hooks/dashboardAdmin/useVouchers';

interface Voucher {
  voucher_id: number;
  code: string;
  name: string;
  type: 'platform' | 'store';
  discount_type: 'percent' | 'fixed' | 'freeship';
  discount_value: number;
  description: string;
  min_order_amount: number;
  max_discount: number | null;
  start_date: string;
  end_date: string;
  usage_limit: number | null;
  per_user_limit: number;
  times_used: number;
  is_active: boolean;
  store_name?: string;
}

export default function AdminVouchersPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [filterDiscountType, setFilterDiscountType] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [showModal, setShowModal] = useState(false);
  const [editingVoucher, setEditingVoucher] = useState<Voucher | null>(null);

  // Fetch vouchers from API
  const { data, loading, error, refetch, toggleVoucher, deleteVoucher, createVoucher, updateVoucher } = useAdminVouchers();

  // Map API data to component format
  const vouchers: Voucher[] = (data?.items || []).map((v: any) => ({
    voucher_id: v.voucherId,
    code: v.code,
    name: v.name,
    type: v.type,
    discount_type: v.discountType,
    discount_value: parseFloat(v.discountValue),
    description: v.description || '',
    min_order_amount: parseFloat(v.minOrderAmount),
    max_discount: v.maxDiscount ? parseFloat(v.maxDiscount) : null,
    start_date: v.startDate,
    end_date: v.endDate,
    usage_limit: v.usageLimit,
    per_user_limit: v.perUserLimit,
    times_used: v.timesUsed || 0,
    is_active: v.isActive,
  }));

  // Form state
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    type: 'platform' as 'platform' | 'store',
    discount_type: 'percent' as 'percent' | 'fixed' | 'freeship',
    discount_value: '',
    description: '',
    min_order_amount: '',
    max_discount: '',
    start_date: '',
    end_date: '',
    usage_limit: '',
    per_user_limit: '1',
    is_active: true,
    is_auto: false,
  });

  const stats = {
    total: vouchers.length,
    active: vouchers.filter(v => v.is_active).length,
    expired: vouchers.filter(v => new Date(v.end_date) < new Date() && !v.is_active).length,
    upcoming: vouchers.filter(v => new Date(v.start_date) > new Date()).length,
  };

  if (loading) return <div className="flex items-center justify-center h-96"><div className="text-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div><p className="mt-4 text-gray-600">Đang tải vouchers...</p></div></div>;
  if (error) return <div className="flex items-center justify-center h-96"><div className="text-center"><p className="text-red-600 mb-4">Lỗi khi tải vouchers</p><button onClick={() => refetch()} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Thử lại</button></div></div>;

  const formatCurrency = (value: number) => {
    return value.toLocaleString('vi-VN') + '₫';
  };

  const getDiscountDisplay = (voucher: Voucher) => {
    if (voucher.discount_type === 'percent') {
      return `${voucher.discount_value}%`;
    } else if (voucher.discount_type === 'fixed') {
      return formatCurrency(voucher.discount_value);
    } else {
      return 'Miễn phí ship';
    }
  };

  const getStatusBadge = (voucher: Voucher) => {
    const now = new Date();
    const start = new Date(voucher.start_date);
    const end = new Date(voucher.end_date);

    if (!voucher.is_active) {
      return <span className="px-3 py-1 bg-gray-200 text-gray-700 rounded-full text-xs font-semibold">Tắt</span>;
    }
    if (now < start) {
      return <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-semibold">Sắp diễn ra</span>;
    }
    if (now > end) {
      return <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-xs font-semibold">Hết hạn</span>;
    }
    if (voucher.usage_limit && voucher.times_used >= voucher.usage_limit) {
      return <span className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-xs font-semibold">Hết lượt</span>;
    }
    return <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">Đang hoạt động</span>;
  };

  const getTypeBadge = (type: string) => {
    if (type === 'platform') {
      return <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs font-semibold">Platform</span>;
    }
    return <span className="px-2 py-1 bg-orange-100 text-orange-800 rounded text-xs font-semibold">Store</span>;
  };

  const getDiscountTypeBadge = (type: string) => {
    const badges = {
      percent: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Phần trăm' },
      fixed: { bg: 'bg-green-100', text: 'text-green-800', label: 'Cố định' },
      freeship: { bg: 'bg-indigo-100', text: 'text-indigo-800', label: 'Free ship' },
    };
    const badge = badges[type as keyof typeof badges] || { bg: 'bg-gray-100', text: 'text-gray-800', label: type };
    return <span className={`px-2 py-1 ${badge.bg} ${badge.text} rounded text-xs font-semibold`}>{badge.label}</span>;
  };

  const filteredVouchers = vouchers.filter(voucher => {
    const matchesSearch = voucher.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      voucher.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === 'all' || voucher.type === filterType;
    const matchesDiscountType = filterDiscountType === 'all' || voucher.discount_type === filterDiscountType;

    let matchesStatus = true;
    if (filterStatus === 'active') matchesStatus = voucher.is_active;
    if (filterStatus === 'inactive') matchesStatus = !voucher.is_active;
    if (filterStatus === 'expired') matchesStatus = new Date(voucher.end_date) < new Date();
    if (filterStatus === 'upcoming') matchesStatus = new Date(voucher.start_date) > new Date();

    return matchesSearch && matchesType && matchesDiscountType && matchesStatus;
  });




  const handleEdit = (voucher: Voucher) => {
    setEditingVoucher(voucher);
    setFormData({
      code: voucher.code,
      name: voucher.name,
      type: voucher.type,
      discount_type: voucher.discount_type,
      discount_value: voucher.discount_value.toString(),
      description: voucher.description,
      min_order_amount: voucher.min_order_amount.toString(),
      max_discount: voucher.max_discount?.toString() || '',
      start_date: voucher.start_date,
      end_date: voucher.end_date,
      usage_limit: voucher.usage_limit?.toString() || '',
      per_user_limit: voucher.per_user_limit.toString(),
      is_active: voucher.is_active,
      is_auto: false,
    });
    setShowModal(true);
  };

  const handleCreate = () => {
    setEditingVoucher(null);
    setFormData({
      code: '',
      name: '',
      type: 'platform',
      discount_type: 'percent',
      discount_value: '',
      description: '',
      min_order_amount: '0',
      max_discount: '',
      start_date: '',
      end_date: '',
      usage_limit: '',
      per_user_limit: '1',
      is_active: true,
      is_auto: false,
    });
    setShowModal(true);
  };

  const handleFormChange = (field: string, value: any) => {
    // Reset discount_value when discount_type changes to avoid validation issues
    if (field === 'discount_type') {
      setFormData(prev => ({ ...prev, [field]: value, discount_value: '' }));
    } else {
      setFormData(prev => ({ ...prev, [field]: value }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!formData.code || !formData.name) {
      alert('Vui lòng điền mã và tên voucher');
      return;
    }

    if (!formData.discount_value || parseFloat(formData.discount_value) <= 0) {
      alert('Giá trị giảm giá phải lớn hơn 0');
      return;
    }

    if (formData.discount_type === 'percent' && parseFloat(formData.discount_value) > 100) {
      alert('Giảm giá phần trăm không được vượt quá 100%');
      return;
    }

    if (!formData.start_date || !formData.end_date) {
      alert('Vui lòng chọn ngày bắt đầu và kết thúc');
      return;
    }

    if (new Date(formData.end_date) <= new Date(formData.start_date)) {
      alert('Ngày kết thúc phải sau ngày bắt đầu');
      return;
    }

    if (formData.discount_type === 'fixed' && formData.max_discount) {
      alert('Giảm tối đa chỉ áp dụng cho voucher phần trăm');
      return;
    }

    const newVoucher: Voucher = {
      voucher_id: editingVoucher?.voucher_id || Date.now(),
      code: formData.code.toUpperCase(),
      name: formData.name,
      type: formData.type,
      discount_type: formData.discount_type,
      discount_value: parseFloat(formData.discount_value),
      description: formData.description,
      min_order_amount: parseFloat(formData.min_order_amount) || 0,
      max_discount: formData.max_discount ? parseFloat(formData.max_discount) : null,
      start_date: formData.start_date,
      end_date: formData.end_date,
      usage_limit: formData.usage_limit ? parseInt(formData.usage_limit) : null,
      per_user_limit: parseInt(formData.per_user_limit),
      times_used: editingVoucher?.times_used || 0,
      is_active: formData.is_active,
      store_name: formData.type === 'store' ? editingVoucher?.store_name : undefined,
    };

    if (editingVoucher) {
      // Update existing voucher
      try {
        const payload = {
          code: formData.code.toUpperCase(),
          name: formData.name,
          type: formData.type,
          discountType: formData.discount_type,
          discountValue: formData.discount_value,
          description: formData.description,
          minOrderAmount: formData.min_order_amount || '0',
          maxDiscount: formData.max_discount || null,
          startDate: formData.start_date,
          endDate: formData.end_date,
          usageLimit: formData.usage_limit ? parseInt(formData.usage_limit) : null,
          perUserLimit: parseInt(formData.per_user_limit),
          isActive: formData.is_active
        };

        await updateVoucher(editingVoucher.voucher_id, payload);
        setShowModal(false);
        alert('Cập nhật voucher thành công!');
      } catch (err) {
        alert('Lỗi khi cập nhật voucher: ' + (err as Error).message);
      }
    } else {
      // Create new voucher
      try {
        const payload = {
          code: formData.code.toUpperCase(),
          name: formData.name,
          type: formData.type,
          discountType: formData.discount_type,
          discountValue: formData.discount_value,
          description: formData.description,
          minOrderAmount: formData.min_order_amount || '0',
          maxDiscount: formData.max_discount || null,
          startDate: formData.start_date,
          endDate: formData.end_date,
          usageLimit: formData.usage_limit ? parseInt(formData.usage_limit) : null,
          perUserLimit: parseInt(formData.per_user_limit),
          isActive: formData.is_active
        };

        await createVoucher(payload);
        setShowModal(false);
        alert('Tạo voucher thành công!');
      } catch (err) {
        alert('Lỗi khi tạo voucher: ' + (err as Error).message);
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Quản lý Voucher</h1>
          <p className="text-gray-600 mt-2">Tạo và quản lý mã giảm giá cho nền tảng</p>
        </div>
        <button
          onClick={handleCreate}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 shadow-lg"
        >
          <Plus className="h-5 w-5" />
          <span>Tạo voucher mới</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-md border border-gray-100 p-6">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Tag className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              <p className="text-sm text-gray-600">Tổng voucher</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-md border border-gray-100 p-6">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-green-100 rounded-lg">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-green-600">{stats.active}</p>
              <p className="text-sm text-gray-600">Đang hoạt động</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-md border border-gray-100 p-6">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-red-100 rounded-lg">
              <Calendar className="h-6 w-6 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-red-600">{stats.expired}</p>
              <p className="text-sm text-gray-600">Đã hết hạn</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-md border border-gray-100 p-6">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-purple-100 rounded-lg">
              <TrendingUp className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-purple-600">{stats.upcoming}</p>
              <p className="text-sm text-gray-600">Sắp diễn ra</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Tìm theo mã hoặc tên..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">Tất cả loại</option>
            <option value="platform">Platform</option>
            <option value="store">Store</option>
          </select>
          <select
            value={filterDiscountType}
            onChange={(e) => setFilterDiscountType(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">Tất cả giảm giá</option>
            <option value="percent">Phần trăm</option>
            <option value="fixed">Cố định</option>
            <option value="freeship">Free ship</option>
          </select>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">Tất cả trạng thái</option>
            <option value="active">Đang hoạt động</option>
            <option value="inactive">Đã tắt</option>
            <option value="expired">Hết hạn</option>
            <option value="upcoming">Sắp diễn ra</option>
          </select>
        </div>
      </div>

      {/* Vouchers Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredVouchers.map((voucher) => (
          <div key={voucher.voucher_id} className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden hover:shadow-xl transition-shadow">
            <div className="p-6">
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <div className="px-3 py-1 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg font-mono font-bold text-sm flex items-center space-x-2">
                      <Tag className="h-4 w-4" />
                      <span>{voucher.code}</span>
                    </div>
                    <button className="p-1 hover:bg-gray-100 rounded" title="Copy mã">
                      <Copy className="h-4 w-4 text-gray-500" />
                    </button>
                  </div>
                  <h3 className="text-lg font-bold text-gray-900">{voucher.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">{voucher.description}</p>
                </div>
                {getStatusBadge(voucher)}
              </div>

              {/* Badges */}
              <div className="flex items-center space-x-2 mb-4">
                {getTypeBadge(voucher.type)}
                {getDiscountTypeBadge(voucher.discount_type)}
              </div>

              {/* Discount Info */}
              <div className="bg-gradient-to-r from-orange-50 to-yellow-50 rounded-lg p-4 mb-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-gray-600 mb-1">Giảm giá</p>
                    <p className="text-xl font-bold text-orange-600">{getDiscountDisplay(voucher)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600 mb-1">Đơn tối thiểu</p>
                    <p className="text-sm font-semibold text-gray-900">{formatCurrency(voucher.min_order_amount)}</p>
                  </div>
                  {voucher.max_discount && (
                    <div>
                      <p className="text-xs text-gray-600 mb-1">Giảm tối đa</p>
                      <p className="text-sm font-semibold text-gray-900">{formatCurrency(voucher.max_discount)}</p>
                    </div>
                  )}
                  <div>
                    <p className="text-xs text-gray-600 mb-1">Giới hạn/người</p>
                    <p className="text-sm font-semibold text-gray-900">{voucher.per_user_limit} lượt</p>
                  </div>
                </div>
              </div>

              {/* Usage Progress */}
              {voucher.usage_limit && (
                <div className="mb-4">
                  <div className="flex items-center justify-between text-sm mb-2">
                    <span className="text-gray-600">Lượt sử dụng</span>
                    <span className="font-semibold text-gray-900">
                      {voucher.times_used} / {voucher.usage_limit}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-indigo-600 h-2 rounded-full transition-all"
                      style={{ width: `${(voucher.times_used / voucher.usage_limit) * 100}%` }}
                    ></div>
                  </div>
                </div>
              )}

              {/* Date Range */}
              <div className="flex items-center text-sm text-gray-600 mb-4">
                <Calendar className="h-4 w-4 mr-2" />
                <span>{voucher.start_date} → {voucher.end_date}</span>
              </div>

              {/* Store Info */}
              {voucher.store_name && (
                <div className="bg-gray-50 rounded-lg p-3 mb-4">
                  <p className="text-xs text-gray-500">Cửa hàng</p>
                  <p className="font-semibold text-gray-900">{voucher.store_name}</p>
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center space-x-2 pt-4 border-t border-gray-200">
                <button
                  onClick={() => handleEdit(voucher)}
                  className="flex-1 px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors flex items-center justify-center space-x-2"
                >
                  <Edit className="h-4 w-4" />
                  <span>Sửa</span>
                </button>
                <button
                  onClick={() => toggleVoucher(voucher.voucher_id)}
                  className={`flex-1 px-4 py-2 rounded-lg transition-colors flex items-center justify-center space-x-2 ${voucher.is_active
                    ? 'bg-yellow-50 text-yellow-600 hover:bg-yellow-100'
                    : 'bg-green-50 text-green-600 hover:bg-green-100'
                    }`}
                >
                  <Power className="h-4 w-4" />
                  <span>{voucher.is_active ? 'Tắt' : 'Bật'}</span>
                </button>
                <button
                  onClick={() => { if (confirm('Xóa voucher?')) deleteVoucher(voucher.voucher_id); }}
                  className="flex-1 px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors flex items-center justify-center space-x-2"
                >
                  <Trash2 className="h-4 w-4" />
                  <span>Xóa</span>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {filteredVouchers.length === 0 && (
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-12 text-center">
          <Tag className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Không tìm thấy voucher</h3>
          <p className="text-gray-600">Thử thay đổi bộ lọc hoặc tạo voucher mới</p>
        </div>
      )}

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">
                {editingVoucher ? 'Chỉnh sửa voucher' : 'Tạo voucher mới'}
              </h2>
              <button
                onClick={() => setShowModal(false)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6">
              <div className="space-y-6">
                {/* Code & Name */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Mã voucher <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.code}
                      onChange={(e) => handleFormChange('code', e.target.value.toUpperCase())}
                      placeholder="VD: WELCOME2024"
                      maxLength={50}
                      required
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Tên voucher <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => handleFormChange('name', e.target.value)}
                      placeholder="VD: Voucher chào mừng"
                      maxLength={50}
                      required
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                {/* Type & Discount Type */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Loại voucher <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={formData.type}
                      onChange={(e) => handleFormChange('type', e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="platform">Platform (Toàn hệ thống)</option>
                      <option value="store">Store (Cửa hàng cụ thể)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Loại giảm giá <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={formData.discount_type}
                      onChange={(e) => handleFormChange('discount_type', e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="percent">Phần trăm (%)</option>
                      <option value="fixed">Cố định (₫)</option>
                      <option value="freeship">Miễn phí vận chuyển</option>
                    </select>
                  </div>
                </div>

                {/* Discount Value & Min Order */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Giá trị giảm <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <input
                        type="number"
                        value={formData.discount_value}
                        onChange={(e) => handleFormChange('discount_value', e.target.value)}
                        placeholder={formData.discount_type === 'percent' ? '0-100' : '0'}
                        min="0"
                        max={formData.discount_type === 'percent' ? '100' : undefined}
                        step={formData.discount_type === 'percent' ? '1' : '1000'}
                        required
                        className="w-full px-4 py-2 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <span className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-500 font-semibold">
                        {formData.discount_type === 'percent' ? '%' : '₫'}
                      </span>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Đơn hàng tối thiểu
                    </label>
                    <div className="relative">
                      <input
                        type="number"
                        value={formData.min_order_amount}
                        onChange={(e) => handleFormChange('min_order_amount', e.target.value)}
                        placeholder="0"
                        min="0"
                        step="1000"
                        className="w-full px-4 py-2 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <span className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-500 font-semibold">₫</span>
                    </div>
                  </div>
                </div>

                {/* Max Discount (only for percent) */}
                {formData.discount_type === 'percent' && (
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Giảm tối đa
                    </label>
                    <div className="relative">
                      <input
                        type="number"
                        value={formData.max_discount}
                        onChange={(e) => handleFormChange('max_discount', e.target.value)}
                        placeholder="Không giới hạn"
                        min="0"
                        step="1000"
                        className="w-full px-4 py-2 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <span className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-500 font-semibold">₫</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">Chỉ áp dụng cho voucher phần trăm</p>
                  </div>
                )}

                {/* Description */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Mô tả
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => handleFormChange('description', e.target.value)}
                    placeholder="Mô tả chi tiết về voucher..."
                    maxLength={200}
                    rows={3}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  />
                  <p className="text-xs text-gray-500 mt-1">{formData.description.length}/200 ký tự</p>
                </div>

                {/* Date Range */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Ngày bắt đầu <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="date"
                      value={formData.start_date}
                      onChange={(e) => handleFormChange('start_date', e.target.value)}
                      required
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Ngày kết thúc <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="date"
                      value={formData.end_date}
                      onChange={(e) => handleFormChange('end_date', e.target.value)}
                      required
                      min={formData.start_date}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                {/* Usage Limits */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Tổng lượt sử dụng
                    </label>
                    <input
                      type="number"
                      value={formData.usage_limit}
                      onChange={(e) => handleFormChange('usage_limit', e.target.value)}
                      placeholder="Không giới hạn"
                      min="1"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <p className="text-xs text-gray-500 mt-1">Để trống nếu không giới hạn</p>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Lượt sử dụng/người <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="number"
                      value={formData.per_user_limit}
                      onChange={(e) => handleFormChange('per_user_limit', e.target.value)}
                      placeholder="1"
                      min="1"
                      required
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                {/* Active Toggle */}
                <div className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg">
                  <input
                    type="checkbox"
                    id="is_active"
                    checked={formData.is_active}
                    onChange={(e) => handleFormChange('is_active', e.target.checked)}
                    className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                  />
                  <label htmlFor="is_active" className="text-sm font-semibold text-gray-700 cursor-pointer">
                    Kích hoạt voucher ngay sau khi tạo
                  </label>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center space-x-3 mt-8 pt-6 border-t border-gray-200">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-semibold"
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold shadow-lg"
                >
                  {editingVoucher ? 'Cập nhật' : 'Tạo voucher'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
