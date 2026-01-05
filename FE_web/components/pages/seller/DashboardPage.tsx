import React from 'react';
import { Calendar, DollarSign, ShoppingCart, Package, Users, Eye, TrendingUp, BarChart3 } from 'lucide-react';
import MetricCard from '../../ui/MetricCard';
import SalesChart from '../../charts/SalesChart';
import OrderChart from '../../charts/OrderChart';


interface DashboardPageProps {
	onNavigate: (menu: string) => void;
}

const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
	// Mock data tự thiết lập bên trong
	const storeData = {
		name: 'SHOEX Store',
		totalProducts: 1,
		totalOrders: 1,
		totalRevenue: 2500000,
		totalCustomers: 892
	};

	const salesData = [
		{ name: 'T2', value: 4000000 },
		{ name: 'T3', value: 3000000 },
		{ name: 'T4', value: 5000000 },
		{ name: 'T5', value: 4500000 },
		{ name: 'T6', value: 6000000 },
		{ name: 'T7', value: 7000000 },
		{ name: 'CN', value: 5500000 }
	];

	const orderData = [
		{ name: 'Đang xử lý', value: 12, color: '#3B82F6' },
		{ name: 'Đã giao', value: 19, color: '#10B981' },
		{ name: 'Đã hủy', value: 3, color: '#EF4444' },
		{ name: 'Đang giao', value: 8, color: '#F59E0B' }
	];

	return (
		<div className="space-y-6">
			<div className="flex justify-between items-center">
				<div>
					<h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
					<p className="text-gray-600 mt-2">Tổng quan về cửa hàng của bạn</p>
				</div>
				<div className="flex items-center space-x-3 text-sm text-gray-600">
					<Calendar className="h-4 w-4" />
					<span>7 ngày qua</span>
				</div>
			</div>

			{/* Metrics */}
			<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
				<MetricCard
					title="Doanh thu"
					value={`${(storeData.totalRevenue / 1000000).toFixed(1)}M₫`}
					sub="+12.5% so với tuần trước"
					icon={<DollarSign className="h-6 w-6 text-green-600" />}
				/>
				<MetricCard
					title="Đơn hàng"
					value={storeData.totalOrders.toString()}
					sub="+8.2% so với tuần trước"
					icon={<ShoppingCart className="h-6 w-6 text-blue-600" />}
				/>
				<MetricCard
					title="Sản phẩm"
					value={storeData.totalProducts.toString()}
					sub="5 sản phẩm mới"
					icon={<Package className="h-6 w-6 text-purple-600" />}
				/>
				<MetricCard
					title="Khách hàng"
					value={storeData.totalCustomers.toString()}
					sub="+15.3% so với tuần trước"
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
					<SalesChart data={salesData} />
				</div>
        
				<div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
					<div className="flex items-center justify-between mb-6">
						<h3 className="text-lg font-semibold text-gray-900">Đơn hàng theo trạng thái</h3>
						<BarChart3 className="h-5 w-5 text-blue-600" />
					</div>
					<OrderChart data={orderData} />
				</div>
			</div>

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
