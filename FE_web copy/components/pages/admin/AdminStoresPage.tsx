import React, { useState } from 'react';
import {
  Store, Search, Filter, MoreVertical, Eye, CheckCircle,
  XCircle, TrendingUp, MapPin, Star, DollarSign
} from 'lucide-react';
import { useAdminStores } from '../../../hooks/dashboardAdmin/useStores';

export default function AdminStoresPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'pending' | 'suspended'>('all');
  const [sortBy, setSortBy] = useState<'revenue' | 'orders' | 'rating' | 'date'>('revenue');
  const [selectedStore, setSelectedStore] = useState<number | null>(null);

  const { data, loading, error, lockStore } = useAdminStores();
  const stores = data?.items || [];

  const formatCurrency = (value: number) => {
    return (value / 1000000).toFixed(1) + 'M₫';
  };

  const getStatusBadge = (status: string) => {
    const badges: { [key: string]: { bg: string; text: string; label: string } } = {
      active: { bg: 'bg-green-100', text: 'text-green-800', label: 'Hoạt động' },
      pending: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Chờ duyệt' },
      suspended: { bg: 'bg-red-100', text: 'text-red-800', label: 'Tạm khóa' },
    };
    const badge = badges[status] || badges.active;
    return (
      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${badge.bg} ${badge.text}`}>
        {badge.label}
      </span>
    );
  };

  const filteredStores = stores
    .filter((store: any) => {
      if (statusFilter !== 'all' && store.status !== statusFilter) return false;
      if (searchQuery && !store.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
        !store.ownerName?.toLowerCase().includes(searchQuery.toLowerCase())) return false; // Use ownerName
      return true;
    })
    .sort((a: any, b: any) => {
      switch (sortBy) {
        case 'revenue': return b.revenue - a.revenue;
        case 'orders': return b.orders - a.orders;
        case 'rating': return b.rating - a.rating;
        case 'date': return new Date(b.joinDate).getTime() - new Date(a.joinDate).getTime();
        default: return 0;
      }
    });

  if (loading) return <div className="p-12 text-center">Đang tải dữ liệu cửa hàng...</div>;
  if (error) return <div className="p-12 text-center text-red-600">Lỗi: {error.message}</div>;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Quản lý cửa hàng</h1>
          <p className="text-gray-600 mt-2">Tổng số: {stores.length} cửa hàng</p>
        </div>
        <button className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg font-semibold hover:shadow-lg transition-shadow">
          + Thêm cửa hàng
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="md:col-span-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Tìm kiếm tên cửa hàng, chủ sở hữu..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Status Filter */}
          <div>
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as any)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none"
              >
                <option value="all">Tất cả trạng thái</option>
                <option value="active">Hoạt động</option>
                <option value="pending">Chờ duyệt</option>
                <option value="suspended">Tạm khóa</option>
              </select>
            </div>
          </div>

          {/* Sort */}
          <div>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="revenue">Doanh thu cao nhất</option>
              <option value="orders">Đơn hàng nhiều nhất</option>
              <option value="rating">Đánh giá cao nhất</option>
              <option value="date">Mới nhất</option>
            </select>
          </div>
        </div>
      </div>

      {/* Stores Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredStores.map((store) => (
          <div
            key={store.id}
            className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden hover:shadow-xl transition-shadow"
          >
            {/* Store Header */}
            <div className="bg-gradient-to-r from-blue-500 to-indigo-600 p-6 text-white">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="h-16 w-16 rounded-full bg-white flex items-center justify-center text-2xl font-bold text-blue-600">
                    {store.name.charAt(0)}
                  </div>
                  <div>
                    <h3 className="font-bold text-lg">{store.name}</h3>
                    <p className="text-blue-100 text-sm">{store.ownerName}</p>
                  </div>
                </div>
                <button className="p-2 hover:bg-white/20 rounded-lg transition-colors">
                  <MoreVertical className="h-5 w-5" />
                </button>
              </div>
              {getStatusBadge(store.status)}
            </div>

            {/* Store Info */}
            <div className="p-6">
              <div className="space-y-3 mb-4">
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <MapPin className="h-4 w-4" />
                  <span>{store.address}</span>
                </div>
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <span>📧 {store.email}</span>
                </div>
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <span>📱 {store.phone}</span>
                </div>
              </div>

              {/* Metrics */}
              <div className="grid grid-cols-2 gap-4 py-4 border-t border-gray-100">
                <div>
                  <div className="flex items-center space-x-2 text-green-600 mb-1">
                    <DollarSign className="h-4 w-4" />
                    <span className="text-xs font-medium">Doanh thu</span>
                  </div>
                  <p className="text-lg font-bold text-gray-900">{formatCurrency(store.revenue)}</p>
                </div>
                <div>
                  <div className="flex items-center space-x-2 text-blue-600 mb-1">
                    <TrendingUp className="h-4 w-4" />
                    <span className="text-xs font-medium">Đơn hàng</span>
                  </div>
                  <p className="text-lg font-bold text-gray-900">{store.orders}</p>
                </div>
                <div>
                  <div className="flex items-center space-x-2 text-purple-600 mb-1">
                    <Store className="h-4 w-4" />
                    <span className="text-xs font-medium">Sản phẩm</span>
                  </div>
                  <p className="text-lg font-bold text-gray-900">{store.products}</p>
                </div>
                <div>
                  <div className="flex items-center space-x-2 text-yellow-600 mb-1">
                    <Star className="h-4 w-4" />
                    <span className="text-xs font-medium">Đánh giá</span>
                  </div>
                  <p className="text-lg font-bold text-gray-900">{store.rating}</p>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center space-x-2 mt-4">
                <button className="flex-1 px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors font-medium text-sm">
                  <Eye className="h-4 w-4 inline mr-1" />
                  Chi tiết
                </button>
                {store.status === 'pending' && (
                  <button className="flex-1 px-4 py-2 bg-green-50 text-green-600 rounded-lg hover:bg-green-100 transition-colors font-medium text-sm">
                    <CheckCircle className="h-4 w-4 inline mr-1" />
                    Duyệt
                  </button>
                )}
                {store.status === 'active' && (
                  <button
                    onClick={() => lockStore(store.id)}
                    className="flex-1 px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors font-medium text-sm"
                  >
                    <XCircle className="h-4 w-4 inline mr-1" />
                    Khóa
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {filteredStores.length === 0 && (
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-12 text-center">
          <Store className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Không tìm thấy cửa hàng</h3>
          <p className="text-gray-500">Thử thay đổi bộ lọc hoặc từ khóa tìm kiếm</p>
        </div>
      )}
    </div>
  );
}
