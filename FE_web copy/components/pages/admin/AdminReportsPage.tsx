import React, { useState } from 'react';
import { 
  FileText, Download, Calendar, Filter, TrendingUp, 
  DollarSign, ShoppingCart, Users, Store, Eye, Printer
} from 'lucide-react';

export default function AdminReportsPage() {
  const [reportType, setReportType] = useState<string>('revenue');
  const [dateRange, setDateRange] = useState<string>('this_month');

  const reportTypes = [
    { id: 'revenue', name: 'Báo cáo doanh thu', icon: DollarSign, color: 'green' },
    { id: 'orders', name: 'Báo cáo đơn hàng', icon: ShoppingCart, color: 'blue' },
    { id: 'stores', name: 'Báo cáo cửa hàng', icon: Store, color: 'purple' },
    { id: 'users', name: 'Báo cáo người dùng', icon: Users, color: 'orange' },
  ];

  const revenueReport = {
    summary: {
      totalRevenue: 1200000000,
      totalOrders: 15420,
      avgOrderValue: 77821,
      growth: 23.5,
    },
    breakdown: [
      { category: 'Giày thể thao', revenue: 540000000, orders: 6200, percentage: 45 },
      { category: 'Giày cao gót', revenue: 336000000, orders: 3850, percentage: 28 },
      { category: 'Giày lười', revenue: 180000000, orders: 2310, percentage: 15 },
      { category: 'Sandals', revenue: 96000000, orders: 1540, percentage: 8 },
      { category: 'Khác', revenue: 48000000, orders: 1520, percentage: 4 },
    ],
    topStores: [
      { name: 'Nike Official Store', revenue: 125000000, orders: 1520, growth: 28.5 },
      { name: 'Adidas Vietnam', revenue: 98000000, orders: 1230, growth: 22.3 },
      { name: 'Converse Store', revenue: 87000000, orders: 980, growth: 18.7 },
      { name: 'Vans Official', revenue: 76000000, orders: 890, growth: 15.2 },
      { name: 'Puma Vietnam', revenue: 65000000, orders: 750, growth: 12.8 },
    ],
  };

  const ordersReport = {
    summary: {
      totalOrders: 15420,
      completed: 12850,
      cancelled: 1120,
      pending: 1450,
    },
    byStatus: [
      { status: 'Hoàn thành', count: 12850, percentage: 83.3, color: '#10B981' },
      { status: 'Đang xử lý', count: 1450, percentage: 9.4, color: '#F59E0B' },
      { status: 'Đã hủy', count: 1120, percentage: 7.3, color: '#EF4444' },
    ],
    byPayment: [
      { method: 'VNPay', count: 8950, percentage: 58.1 },
      { method: 'COD', count: 4820, percentage: 31.3 },
      { method: 'Khác', count: 1650, percentage: 10.6 },
    ],
  };

  const formatCurrency = (value: number) => {
    return (value / 1000000).toFixed(1) + 'M₫';
  };

  const formatNumber = (num: number) => {
    return num.toLocaleString('vi-VN');
  };

  const getReportData = () => {
    switch (reportType) {
      case 'revenue':
        return revenueReport;
      case 'orders':
        return ordersReport;
      default:
        return revenueReport;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Báo cáo</h1>
          <p className="text-gray-600 mt-2">Tạo và xuất báo cáo chi tiết</p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center space-x-2">
            <Printer className="h-4 w-4" />
            <span>In</span>
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2">
            <Download className="h-4 w-4" />
            <span>Xuất Excel</span>
          </button>
        </div>
      </div>

      {/* Report Type Selection */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {reportTypes.map((type) => {
          const Icon = type.icon;
          return (
            <button
              key={type.id}
              onClick={() => setReportType(type.id)}
              className={`p-6 rounded-xl border-2 transition-all ${
                reportType === type.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 bg-white hover:border-gray-300'
              }`}
            >
              <div className={`inline-flex p-3 rounded-lg bg-${type.color}-100 mb-3`}>
                <Icon className={`h-6 w-6 text-${type.color}-600`} />
              </div>
              <p className={`font-semibold ${reportType === type.id ? 'text-blue-900' : 'text-gray-900'}`}>
                {type.name}
              </p>
            </button>
          );
        })}
      </div>

      {/* Filters */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Khoảng thời gian</label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <select
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="today">Hôm nay</option>
                <option value="yesterday">Hôm qua</option>
                <option value="this_week">Tuần này</option>
                <option value="last_week">Tuần trước</option>
                <option value="this_month">Tháng này</option>
                <option value="last_month">Tháng trước</option>
                <option value="this_year">Năm nay</option>
                <option value="custom">Tùy chỉnh</option>
              </select>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Từ ngày</label>
            <input
              type="date"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Đến ngày</label>
            <input
              type="date"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* Revenue Report */}
      {reportType === 'revenue' && (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl shadow-lg p-6 text-white">
              <DollarSign className="h-8 w-8 mb-3 opacity-80" />
              <h3 className="text-3xl font-bold">{formatCurrency(revenueReport.summary.totalRevenue)}</h3>
              <p className="text-sm opacity-90 mt-1">Tổng doanh thu</p>
            </div>
            <div className="bg-gradient-to-br from-blue-500 to-cyan-600 rounded-xl shadow-lg p-6 text-white">
              <ShoppingCart className="h-8 w-8 mb-3 opacity-80" />
              <h3 className="text-3xl font-bold">{formatNumber(revenueReport.summary.totalOrders)}</h3>
              <p className="text-sm opacity-90 mt-1">Tổng đơn hàng</p>
            </div>
            <div className="bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl shadow-lg p-6 text-white">
              <TrendingUp className="h-8 w-8 mb-3 opacity-80" />
              <h3 className="text-3xl font-bold">{formatCurrency(revenueReport.summary.avgOrderValue)}</h3>
              <p className="text-sm opacity-90 mt-1">Giá trị TB/đơn</p>
            </div>
            <div className="bg-gradient-to-br from-orange-500 to-red-600 rounded-xl shadow-lg p-6 text-white">
              <TrendingUp className="h-8 w-8 mb-3 opacity-80" />
              <h3 className="text-3xl font-bold">+{revenueReport.summary.growth}%</h3>
              <p className="text-sm opacity-90 mt-1">Tăng trưởng</p>
            </div>
          </div>

          {/* Revenue Breakdown */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Doanh thu theo danh mục</h3>
            <div className="space-y-4">
              {revenueReport.breakdown.map((item, index) => (
                <div key={index} className="flex items-center space-x-4">
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-gray-900">{item.category}</span>
                      <span className="text-sm text-gray-600">{item.percentage}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div
                        className="bg-gradient-to-r from-blue-500 to-indigo-600 h-3 rounded-full transition-all"
                        style={{ width: `${item.percentage}%` }}
                      ></div>
                    </div>
                  </div>
                  <div className="text-right min-w-[120px]">
                    <p className="font-bold text-gray-900">{formatCurrency(item.revenue)}</p>
                    <p className="text-sm text-gray-500">{formatNumber(item.orders)} đơn</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Top Stores */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Top cửa hàng theo doanh thu</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">#</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Cửa hàng</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Doanh thu</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Đơn hàng</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Tăng trưởng</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {revenueReport.topStores.map((store, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="flex items-center justify-center h-8 w-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-white font-bold text-sm">
                          {index + 1}
                        </div>
                      </td>
                      <td className="px-6 py-4 font-medium text-gray-900">{store.name}</td>
                      <td className="px-6 py-4 font-bold text-green-600">{formatCurrency(store.revenue)}</td>
                      <td className="px-6 py-4 text-gray-700">{formatNumber(store.orders)}</td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800">
                          +{store.growth}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Orders Report */}
      {reportType === 'orders' && (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white rounded-xl shadow-md border border-gray-100 p-6">
              <h3 className="text-2xl font-bold text-gray-900">{formatNumber(ordersReport.summary.totalOrders)}</h3>
              <p className="text-sm text-gray-500">Tổng đơn hàng</p>
            </div>
            <div className="bg-white rounded-xl shadow-md border border-gray-100 p-6">
              <h3 className="text-2xl font-bold text-green-600">{formatNumber(ordersReport.summary.completed)}</h3>
              <p className="text-sm text-gray-500">Hoàn thành</p>
            </div>
            <div className="bg-white rounded-xl shadow-md border border-gray-100 p-6">
              <h3 className="text-2xl font-bold text-yellow-600">{formatNumber(ordersReport.summary.pending)}</h3>
              <p className="text-sm text-gray-500">Đang xử lý</p>
            </div>
            <div className="bg-white rounded-xl shadow-md border border-gray-100 p-6">
              <h3 className="text-2xl font-bold text-red-600">{formatNumber(ordersReport.summary.cancelled)}</h3>
              <p className="text-sm text-gray-500">Đã hủy</p>
            </div>
          </div>

          {/* Orders by Status & Payment */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Phân bố theo trạng thái</h3>
              <div className="space-y-4">
                {ordersReport.byStatus.map((item, index) => (
                  <div key={index}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-gray-900">{item.status}</span>
                      <span className="text-sm font-semibold" style={{ color: item.color }}>
                        {formatNumber(item.count)} ({item.percentage}%)
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div
                        className="h-3 rounded-full transition-all"
                        style={{ width: `${item.percentage}%`, backgroundColor: item.color }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Phương thức thanh toán</h3>
              <div className="space-y-4">
                {ordersReport.byPayment.map((item, index) => (
                  <div key={index}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-gray-900">{item.method}</span>
                      <span className="text-sm font-semibold text-blue-600">
                        {formatNumber(item.count)} ({item.percentage}%)
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div
                        className="bg-gradient-to-r from-blue-500 to-indigo-600 h-3 rounded-full transition-all"
                        style={{ width: `${item.percentage}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
