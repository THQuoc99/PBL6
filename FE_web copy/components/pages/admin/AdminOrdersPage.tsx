import React, { useState } from 'react';
import {
  ShoppingCart, Search, Filter, Package, MapPin, Clock,
  CheckCircle, XCircle, TruckIcon, DollarSign, Eye
} from 'lucide-react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer
} from 'recharts';

import { useAdminOrders } from '../../../hooks/dashboardAdmin/useOrders';
import { useAdminDashboard } from '../../../hooks/dashboardAdmin/useDashboard';

export default function AdminOrdersPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [dateFilter, setDateFilter] = useState<string>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 8;

  const { data, loading, error } = useAdminOrders();
  const { data: dashboardData } = useAdminDashboard();
  const orders = data?.items || [];

  // Chart data from dashboard API (revenue_by_day is 30 days, we take last 7)
  const revenueData = dashboardData?.revenueByDay || [];
  const ordersChartData = revenueData.slice(-7).map((item: any) => ({
    day: item.day,
    orders: item.orders,
    revenue: item.revenue
  }));

  const formatCurrency = (value: number) => {
    return (value / 1000000).toFixed(1) + 'M₫';
  };

  const getStatusConfig = (status: string) => {
    const configs: { [key: string]: { bg: string; text: string; label: string; icon: any } } = {
      pending: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Chờ xác nhận', icon: Clock },
      confirmed: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Đã xác nhận', icon: CheckCircle },
      shipping: { bg: 'bg-purple-100', text: 'text-purple-800', label: 'Đang giao', icon: TruckIcon },
      completed: { bg: 'bg-green-100', text: 'text-green-800', label: 'Hoàn thành', icon: CheckCircle },
      cancelled: { bg: 'bg-red-100', text: 'text-red-800', label: 'Đã hủy', icon: XCircle },
    };
    return configs[status] || configs.pending;
  };

  const filteredOrders = orders.filter((order: any) => {
    if (statusFilter !== 'all' && order.status !== statusFilter) return false;
    if (searchQuery &&
      !order.id.toLowerCase().includes(searchQuery.toLowerCase()) &&
      !order.customer.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  const totalPages = Math.ceil(filteredOrders.length / itemsPerPage);
  const paginatedOrders = filteredOrders.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const stats = [
    { label: 'Tổng đơn hàng', value: orders.length, color: 'blue' },
    { label: 'Đang xử lý', value: orders.filter((o: any) => o.status === 'pending' || o.status === 'confirmed').length, color: 'yellow' },
    { label: 'Đang giao', value: orders.filter((o: any) => o.status === 'shipping').length, color: 'purple' },
    { label: 'Hoàn thành', value: orders.filter((o: any) => o.status === 'completed').length, color: 'green' },
  ];

  if (loading) return <div>Loading orders...</div>;
  if (error) return <div>Error loading orders: {error.message}</div>;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Quản lý đơn hàng</h1>
        <p className="text-gray-600 mt-2">Tất cả đơn hàng trên platform</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <div key={index} className="bg-white rounded-xl shadow-md border border-gray-100 p-6">
            <h3 className="text-2xl font-bold text-gray-900">{stat.value}</h3>
            <p className="text-sm text-gray-500">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Đơn hàng 7 ngày</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={ordersChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="day" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #E5E7EB' }} />
              <Bar dataKey="orders" fill="#3B82F6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Doanh thu 7 ngày</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={ordersChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="day" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" tickFormatter={(value) => formatCurrency(value)} />
              <Tooltip
                formatter={(value: number) => formatCurrency(value)}
                contentStyle={{ borderRadius: '8px', border: '1px solid #E5E7EB' }}
              />
              <Line type="monotone" dataKey="revenue" stroke="#10B981" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Tìm mã đơn, khách hàng..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">Tất cả trạng thái</option>
            <option value="pending">Chờ xác nhận</option>
            <option value="confirmed">Đã xác nhận</option>
            <option value="shipping">Đang giao</option>
            <option value="completed">Hoàn thành</option>
            <option value="cancelled">Đã hủy</option>
          </select>

          <select
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">Tất cả thời gian</option>
            <option value="today">Hôm nay</option>
            <option value="week">Tuần này</option>
            <option value="month">Tháng này</option>
          </select>
        </div>
      </div>

      {/* Orders Table */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase">Mã đơn</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase">Khách hàng</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase">Cửa hàng</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase">Sản phẩm</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase">Tổng tiền</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase">Trạng thái</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase">Ngày đặt</th>
                <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase">Hành động</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {paginatedOrders.map((order) => {
                const statusConfig = getStatusConfig(order.status);
                const StatusIcon = statusConfig.icon;
                return (
                  <tr key={order.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4">
                      <span className="font-mono font-semibold text-blue-600">{order.id}</span>
                    </td>
                    <td className="px-6 py-4">
                      <p className="font-medium text-gray-900">{order.customer}</p>
                      <p className="text-sm text-gray-500 flex items-center space-x-1">
                        <MapPin className="h-3 w-3" />
                        <span>{order.shippingAddress}</span>
                      </p>
                    </td>
                    <td className="px-6 py-4">
                      <p className="text-sm text-gray-900">{order.store}</p>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        <Package className="h-4 w-4 text-gray-400" />
                        <span className="text-sm">{order.products} sản phẩm</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <p className="font-semibold text-gray-900">{formatCurrency(order.total)}</p>
                      <p className="text-xs text-gray-500">{order.paymentMethod.toUpperCase()}</p>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center space-x-1 px-3 py-1 rounded-full text-xs font-semibold ${statusConfig.bg} ${statusConfig.text}`}>
                        <StatusIcon className="h-3 w-3" />
                        <span>{statusConfig.label}</span>
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <p className="text-sm text-gray-900">{new Date(order.date).toLocaleDateString('vi-VN')}</p>
                    </td>
                    <td className="px-6 py-4">
                      <button className="px-3 py-1 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors text-sm font-medium">
                        <Eye className="h-4 w-4 inline mr-1" />
                        Chi tiết
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="bg-gray-50 px-6 py-4 flex items-center justify-between border-t border-gray-200">
          <p className="text-sm text-gray-600">
            Hiển thị {(currentPage - 1) * itemsPerPage + 1} - {Math.min(currentPage * itemsPerPage, filteredOrders.length)} / {filteredOrders.length}
          </p>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 disabled:opacity-50"
            >
              Trước
            </button>
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
              <button
                key={page}
                onClick={() => setCurrentPage(page)}
                className={`px-4 py-2 rounded-lg ${currentPage === page ? 'bg-blue-600 text-white' : 'border border-gray-300 hover:bg-gray-100'}`}
              >
                {page}
              </button>
            ))}
            <button
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 disabled:opacity-50"
            >
              Sau
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
