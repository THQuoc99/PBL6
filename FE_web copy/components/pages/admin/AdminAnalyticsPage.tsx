import React, { useState, useMemo } from 'react';
import {
  TrendingUp, Calendar, Download, BarChart3, PieChart as PieChartIcon,
  Users, Store, ShoppingCart, DollarSign, ArrowUp, ArrowDown
} from 'lucide-react';
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis
} from 'recharts';
import { useAdminAnalytics } from '../../../hooks/dashboardAdmin/useAnalytics';

export default function AdminAnalyticsPage() {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d' | '1y'>('30d');

  // Fetch analytics data from backend
  const { data, loading, error, refetch } = useAdminAnalytics({ range: timeRange });

  // Prepare chart data with color mappings
  const revenueTrendData = useMemo(() => data?.revenueTrend || [], [data]);

  const categoryData = useMemo(() => {
    const colors = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6'];
    return (data?.categoryPerformance || []).map((cat: any, idx: number) => ({
      ...cat,
      color: colors[idx % colors.length]
    }));
  }, [data]);

  const regionalData = useMemo(() => {
    const colors = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6'];
    return (data?.regionalDistribution || []).map((reg: any, idx: number) => ({
      ...reg,
      color: colors[idx % colors.length]
    }));
  }, [data]);

  const userGrowthData = useMemo(() => data?.userGrowth || [], [data]);

  const formatCurrency = (value: number) => {
    // Handle non-numeric values
    const numValue = typeof value === 'number' ? value : parseFloat(value) || 0;

    if (numValue >= 1000000000) {
      return (numValue / 1000000000).toFixed(1) + 'B₫';
    } else if (numValue >= 1000000) {
      return (numValue / 1000000).toFixed(1) + 'M₫';
    } else if (numValue >= 1000) {
      return (numValue / 1000).toFixed(0) + 'K₫';
    } else {
      return Math.round(numValue) + '₫';
    }
  };

  const formatPercent = (value: number) => {
    return value >= 0 ? `+${value.toFixed(1)}%` : `${value.toFixed(1)}%`;
  };

  // Calculate metrics from backend data
  const metrics = useMemo(() => {
    const keyMetrics = data?.keyMetrics;
    if (!keyMetrics) {
      return [];
    }

    return [
      {
        title: 'Tăng trưởng doanh thu',
        value: formatPercent(keyMetrics.revenueGrowth || 0),
        trend: (keyMetrics.revenueGrowth || 0) >= 0 ? 'up' : 'down',
        description: 'So với tháng trước',
        icon: TrendingUp,
        color: 'green'
      },
      {
        title: 'Giá trị đơn TB',
        value: formatCurrency(parseFloat(keyMetrics.averageOrderValue || '0')),
        trend: 'up',
        description: 'Giá trị trung bình',
        icon: DollarSign,
        color: 'purple'
      },
      {
        title: 'Tỷ lệ giữ chân KH',
        value: `${(keyMetrics.retentionRate || 0).toFixed(0)}%`,
        trend: (keyMetrics.retentionRate || 0) >= 60 ? 'up' : 'down',
        description: 'Khách hàng quay lại',
        icon: Users,
        color: 'orange'
      },
    ];
  }, [data]);

  // Store performance radar - mock for now (can be added to backend)
  const storeMetrics = [
    { metric: 'Doanh thu', value: 85 },
    { metric: 'Đơn hàng', value: 92 },
    { metric: 'Sản phẩm', value: 78 },
    { metric: 'Đánh giá', value: 88 },
    { metric: 'Tốc độ giao', value: 75 },
  ];

  // Show loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Đang tải dữ liệu phân tích...</p>
        </div>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <p className="text-red-600 mb-4">Lỗi khi tải dữ liệu phân tích</p>
          <button
            onClick={() => refetch()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Thử lại
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Phân tích & Thống kê</h1>
          <p className="text-gray-600 mt-2">Phân tích chi tiết hiệu suất platform</p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value as any)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="7d">7 ngày qua</option>
            <option value="30d">30 ngày qua</option>
            <option value="90d">90 ngày qua</option>
            <option value="1y">1 năm qua</option>
          </select>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2">
            <Download className="h-4 w-4" />
            <span>Xuất báo cáo</span>
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {metrics.map((metric, index) => {
          const Icon = metric.icon;
          return (
            <div key={index} className="bg-white rounded-xl shadow-md border border-gray-100 p-6">
              <div className="flex items-center justify-between mb-3">
                <div className={`p-2 rounded-lg bg-${metric.color}-100`}>
                  <Icon className={`h-5 w-5 text-${metric.color}-600`} />
                </div>
                <div className={`flex items-center space-x-1 text-sm font-semibold ${metric.trend === 'up' ? 'text-green-600' : 'text-red-600'
                  }`}>
                  {metric.trend === 'up' ? <ArrowUp className="h-4 w-4" /> : <ArrowDown className="h-4 w-4" />}
                </div>
              </div>
              <h3 className="text-2xl font-bold text-gray-900">{metric.value}</h3>
              <p className="text-sm text-gray-600 mt-1">{metric.title}</p>
              <p className="text-xs text-gray-500 mt-2">{metric.description}</p>
            </div>
          );
        })}
      </div>

      {/* Revenue Trend */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Xu hướng doanh thu & đơn hàng</h3>
            <p className="text-sm text-gray-500 mt-1">12 tháng gần nhất</p>
          </div>
          <TrendingUp className="h-6 w-6 text-green-600" />
        </div>
        <ResponsiveContainer width="100%" height={350}>
          <AreaChart data={revenueTrendData}>
            <defs>
              <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorOrders" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="month" stroke="#9CA3AF" />
            <YAxis yAxisId="left" stroke="#3B82F6" tickFormatter={formatCurrency} />
            <YAxis yAxisId="right" orientation="right" stroke="#10B981" />
            <Tooltip
              formatter={(value: number, name: string) => {
                if (name === 'Doanh thu') return [formatCurrency(value), 'Doanh thu'];
                if (name === 'Đơn hàng') return [value, 'Đơn hàng'];
                return [value, name];
              }}
              contentStyle={{ borderRadius: '8px', border: '1px solid #E5E7EB' }}
            />
            <Legend
              formatter={(value: string) => {
                if (value === 'revenue') return 'Doanh thu';
                if (value === 'orders') return 'Đơn hàng';
                return value;
              }}
            />
            <Area
              yAxisId="left"
              type="monotone"
              dataKey="revenue"
              stroke="#3B82F6"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorRevenue)"
              name="Doanh thu"
            />
            <Area
              yAxisId="right"
              type="monotone"
              dataKey="orders"
              stroke="#10B981"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorOrders)"
              name="Đơn hàng"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Category & Regional Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Performance */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Hiệu suất danh mục</h3>
              <p className="text-sm text-gray-500 mt-1">Top 5 danh mục bán chạy</p>
            </div>
            <BarChart3 className="h-6 w-6 text-blue-600" />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={categoryData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis type="number" tickFormatter={formatCurrency} stroke="#9CA3AF" />
              <YAxis type="category" dataKey="name" stroke="#9CA3AF" width={100} />
              <Tooltip
                formatter={(value: number) => formatCurrency(value)}
                contentStyle={{ borderRadius: '8px', border: '1px solid #E5E7EB' }}
              />
              <Bar dataKey="sales" radius={[0, 8, 8, 0]}>
                {categoryData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Regional Distribution */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Phân bố khu vực</h3>
              <p className="text-sm text-gray-500 mt-1">Theo vị trí khách hàng</p>
            </div>
            <PieChartIcon className="h-6 w-6 text-purple-600" />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={regionalData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(d: any) => `${d.name}: ${Math.round((d.percent ?? 0) * 100)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {regionalData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* User Growth & Store Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* User Growth */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Tăng trưởng người dùng</h3>
              <p className="text-sm text-gray-500 mt-1">Khách hàng & Người bán</p>
            </div>
            <Users className="h-6 w-6 text-green-600" />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={userGrowthData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="month" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #E5E7EB' }} />
              <Legend />
              <Line type="monotone" dataKey="customers" stroke="#3B82F6" strokeWidth={2} name="Khách hàng" />
              <Line type="monotone" dataKey="sellers" stroke="#10B981" strokeWidth={2} name="Người bán" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Store Performance Radar */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Chỉ số hiệu suất TB</h3>
              <p className="text-sm text-gray-500 mt-1">Trung bình các cửa hàng</p>
            </div>
            <Store className="h-6 w-6 text-orange-600" />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={storeMetrics}>
              <PolarGrid stroke="#E5E7EB" />
              <PolarAngleAxis dataKey="metric" stroke="#9CA3AF" />
              <PolarRadiusAxis angle={90} domain={[0, 100]} stroke="#9CA3AF" />
              <Radar name="Hiệu suất" dataKey="value" stroke="#8B5CF6" fill="#8B5CF6" fillOpacity={0.6} />
              <Tooltip />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
