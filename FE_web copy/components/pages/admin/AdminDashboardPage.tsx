import React, { useMemo } from 'react';
import {
  TrendingUp, Users, Store, ShoppingCart, DollarSign,
  Package, ArrowUp, ArrowDown, BarChart3, PieChart
} from 'lucide-react';
import {
  AreaChart, Area, BarChart, Bar, PieChart as RePieChart, Pie, Cell,
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer
} from 'recharts';
import { useAdminDashboard } from '../../../hooks/dashboardAdmin/useDashboard';

export default function AdminDashboardPage() {
  const { data, loading, error } = useAdminDashboard();

  // Helper formats
  const formatCurrency = (value: number) => {
    return (value / 1000000).toFixed(1) + 'M₫';
  };

  const getColorClass = (color: string) => {
    const colors: { [key: string]: string } = {
      green: 'from-green-500 to-emerald-600',
      blue: 'from-blue-500 to-cyan-600',
      purple: 'from-purple-500 to-pink-600',
      orange: 'from-orange-500 to-red-600',
    };
    return colors[color] || colors.blue;
  };

  const getStatusColor = (status: string) => {
    const colors: { [key: string]: string } = {
      pending: 'bg-yellow-100 text-yellow-800',
      success: 'bg-green-100 text-green-800',
      warning: 'bg-orange-100 text-orange-800',
      info: 'bg-blue-100 text-blue-800',
      danger: 'bg-red-100 text-red-800',
    };
    return colors[status] || colors.info;
  };

  // Map API data to UI stats
  const stats = useMemo(() => {
    if (!data) return [];
    return [
      {
        title: 'Tổng doanh thu',
        value: formatCurrency(data.totalRevenue),
        change: '+12.5%', // Mock change for now
        isUp: true,
        icon: DollarSign,
        color: 'green',
        description: 'So với tháng trước'
      },
      {
        title: 'Tổng đơn hàng',
        value: data.totalOrders.toLocaleString(),
        change: '+8.2%',
        isUp: true,
        icon: ShoppingCart,
        color: 'blue',
        description: '30 ngày qua'
      },
      {
        title: 'Cửa hàng hoạt động',
        value: data.totalStores.toLocaleString(),
        change: '+23',
        isUp: true,
        icon: Store,
        color: 'purple',
        description: 'Cửa hàng mới tháng này'
      },
      {
        title: 'Người dùng',
        value: data.totalUsers.toLocaleString(),
        change: '+15.3%',
        isUp: true,
        icon: Users,
        color: 'orange',
        description: 'Người dùng hoạt động'
      },
    ];
  }, [data]);


  if (loading) return <div className="p-8 text-center">Đang tải dữ liệu...</div>;
  if (error) return <div className="p-8 text-center text-red-600">Lỗi tải dữ liệu: {error.message}</div>;
  if (!data) return <div className="p-8 text-center">Không có dữ liệu</div>;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Tổng quan Platform</h1>
        <p className="text-gray-600 mt-2">Theo dõi hoạt động và hiệu suất của sàn thương mại</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div
              key={index}
              className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 hover:shadow-xl transition-shadow"
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-xl bg-gradient-to-br ${getColorClass(stat.color)}`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
                <div className={`flex items-center space-x-1 text-sm font-semibold ${stat.isUp ? 'text-green-600' : 'text-red-600'
                  }`}>
                  {stat.isUp ? <ArrowUp className="h-4 w-4" /> : <ArrowDown className="h-4 w-4" />}
                  <span>{stat.change}</span>
                </div>
              </div>
              <h3 className="text-2xl font-bold text-gray-900">{stat.value}</h3>
              <p className="text-sm text-gray-500 mt-1">{stat.title}</p>
              <p className="text-xs text-gray-400 mt-2">{stat.description}</p>
            </div>
          );
        })}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Revenue Chart */}
        <div className="lg:col-span-2 bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Doanh thu 30 ngày</h3>
              <p className="text-sm text-gray-500 mt-1">Tổng doanh thu theo ngày</p>
            </div>
            <TrendingUp className="h-5 w-5 text-green-600" />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={data.revenueByDay}>
              <defs>
                <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="day" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" tickFormatter={(value: number) => formatCurrency(value)} />
              <Tooltip
                formatter={(value: number) => formatCurrency(value)}
                contentStyle={{ borderRadius: '8px', border: '1px solid #E5E7EB' }}
              />
              <Area
                type="monotone"
                dataKey="revenue"
                stroke="#3B82F6"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorRevenue)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Category Distribution */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Phân loại sản phẩm</h3>
              <p className="text-sm text-gray-500 mt-1">Theo danh mục</p>
            </div>
            <PieChart className="h-5 w-5 text-purple-600" />
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <RePieChart>
              <Pie
                data={data.productByCategory}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(d: any) => `${d.name}: ${Math.round((d.percent ?? 0) * 100)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {data.productByCategory.map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </RePieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bottom Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Stores */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Top cửa hàng</h3>
            <BarChart3 className="h-5 w-5 text-blue-600" />
          </div>
          <div className="space-y-4">
            {data.topStores.map((store: any, index: number) => (
              <div key={index} className="flex items-center space-x-4 p-3 hover:bg-gray-50 rounded-lg transition-colors">
                <div className="flex-shrink-0">
                  <div className="h-12 w-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
                    #{index + 1}
                  </div>
                </div>
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900">{store.name}</h4>
                  <p className="text-sm text-gray-500">{store.orders} đơn hàng</p>
                </div>
                <div className="text-right">
                  <p className="font-bold text-gray-900">{formatCurrency(store.revenue)}</p>
                  <div className="flex items-center space-x-1 text-yellow-500 text-sm">
                    <span>⭐</span>
                    <span>{store.rating}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activities */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Hoạt động gần đây</h3>
            <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">
              Xem tất cả
            </button>
          </div>
          <div className="space-y-3">
            {data.recentActivities.map((activity: any) => (
              <div key={activity.id} className="flex items-start space-x-3 p-3 hover:bg-gray-50 rounded-lg transition-colors">
                <div className={`mt-1 px-2 py-1 rounded text-xs font-medium ${getStatusColor(activity.status)}`}>
                  {activity.type}
                </div>
                <div className="flex-1">
                  <p className="text-sm text-gray-900">{activity.text}</p>
                  <p className="text-xs text-gray-500 mt-1">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
