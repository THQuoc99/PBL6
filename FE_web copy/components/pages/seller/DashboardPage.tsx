import React from 'react';
import { Calendar, DollarSign, ShoppingCart, Package, Users, Eye, TrendingUp, BarChart3 } from 'lucide-react';
import MetricCard from '../../ui/MetricCard';
import SalesChart from '../../charts/SalesChart';
import OrderChart from '../../charts/OrderChart';
import { useDashboard } from '../../../hooks/dashboard/dashboard';
import { useStoreAuth } from '../../../hooks/store/storeAuth';


interface DashboardPageProps {
	onNavigate: (menu: string) => void;
}

const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
	// Get current store
	const { store: currentStore, loading: loadingStore } = useStoreAuth();
	const storeId = currentStore?.storeId || null;

	// Fetch dashboard data
	const { data: dashboard, loading: loadingDashboard, error } = useDashboard(storeId, 7);

	const loading = loadingStore || loadingDashboard;

	// Format revenue for display
	const formatRevenue = (value: number) => {
		if (value >= 1000000) {
			return `${(value / 1000000).toFixed(1)}M₫`;
		}
		return `${(value / 1000).toFixed(0)}K₫`;
	};

	// Prepare chart data
	const salesData = dashboard?.charts.revenueByDay7d.map(day => ({
		name: day.label,
		value: parseFloat(day.value.toString())
	})) || [];

	const orderData = dashboard?.charts.ordersByStatus.map(status => ({
		name: status.label,
		value: status.count,
		color: status.color
	})) || [];

	return (
		<div className="space-y-6">
			<div className="flex justify-between items-center">
				<div>
					<h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
					<p className="text-gray-600 mt-2">
						{currentStore ? `Tổng quan về cửa hàng ${currentStore.name}` : 'Tổng quan về cửa hàng của bạn'}
					</p>
				</div>
				<div className="flex items-center space-x-3 text-sm text-gray-600">
					<Calendar className="h-4 w-4" />
					<span>7 ngày qua</span>
				</div>
			</div>

			{/* Loading state */}
			{loading && (
				<div className="flex justify-center items-center py-12">
					<div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
				</div>
			)}

			{/* Error state */}
			{error && (
				<div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
					<p className="font-medium">Lỗi tải dữ liệu dashboard</p>
					<p className="text-sm mt-1">{error}</p>
				</div>
			)}

			{/* Dashboard content */}
			{!loading && !error && dashboard && (
				<>
					{/* Metrics */}
					<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
						<MetricCard
							title="Doanh thu"
							value={formatRevenue(dashboard.metrics.totalRevenue7d)}
							sub="7 ngày qua"
							icon={<DollarSign className="h-6 w-6 text-green-600" />}
						/>
						<MetricCard
							title="Đơn hàng"
							value={dashboard.metrics.totalOrders7d.toString()}
							sub="7 ngày qua"
							icon={<ShoppingCart className="h-6 w-6 text-blue-600" />}
						/>
						<MetricCard
							title="Sản phẩm"
							value={dashboard.metrics.totalProducts.toString()}
							sub="Tổng sản phẩm đang bán"
							icon={<Package className="h-6 w-6 text-purple-600" />}
						/>
						<MetricCard
							title="Khách hàng"
							value={dashboard.metrics.totalCustomers7d.toString()}
							sub="7 ngày qua"
							icon={<Users className="h-6 w-6 text-orange-600" />}
						/>
					</div>

					{/* Charts */}
					<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
						<div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
							<div className="flex items-center justify-between mb-6">
								<h3 className="text-lg font-semibold text-gray-900">Doanh thu 7 ngày</h3>
								<TrendingUp className="h-5 w-5 text-green-600" />
							</div>
							{salesData.length > 0 ? (
								<SalesChart data={salesData} />
							) : (
								<div className="text-center py-8 text-gray-500">Chưa có dữ liệu</div>
							)}
						</div>
        
						<div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
							<div className="flex items-center justify-between mb-6">
								<h3 className="text-lg font-semibold text-gray-900">Đơn hàng theo trạng thái</h3>
								<BarChart3 className="h-5 w-5 text-blue-600" />
							</div>
							{orderData.length > 0 ? (
								<OrderChart data={orderData} />
							) : (
								<div className="text-center py-8 text-gray-500">Chưa có đơn hàng</div>
							)}
						</div>
					</div>
				</>
			)}

			{/* Quick Actions */}
			<div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
				<h3 className="text-lg font-semibold text-gray-900 mb-6">Hành động nhanh</h3>
				<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
					<button 
						onClick={() => onNavigate('products')}
						className="p-4 bg-blue-50 rounded-xl hover:bg-blue-100 transition-colors text-left"
					>
						<Package className="h-6 w-6 text-blue-600 mb-2" />
						<div className="font-medium text-gray-900">Thêm sản phẩm</div>
						<div className="text-sm text-gray-600">Tạo sản phẩm mới</div>
					</button>
          
					<button 
						onClick={() => onNavigate('orders')}
						className="p-4 bg-green-50 rounded-xl hover:bg-green-100 transition-colors text-left"
					>
						<ShoppingCart className="h-6 w-6 text-green-600 mb-2" />
						<div className="font-medium text-gray-900">Xem đơn hàng</div>
						<div className="text-sm text-gray-600">Quản lý đơn hàng</div>
					</button>
          
					<button 
						onClick={() => onNavigate('settings')}
						className="p-4 bg-purple-50 rounded-xl hover:bg-purple-100 transition-colors text-left"
					>
						<Eye className="h-6 w-6 text-purple-600 mb-2" />
						<div className="font-medium text-gray-900">Xem cửa hàng</div>
						<div className="text-sm text-gray-600">Cài đặt giao diện</div>
					</button>
				</div>
			</div>
		</div>
	);
};

export default DashboardPage;
