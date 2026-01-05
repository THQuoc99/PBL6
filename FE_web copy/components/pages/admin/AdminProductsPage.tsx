import React, { useState } from 'react';
import {
  Package, Search, Filter, Eye, CheckCircle, XCircle,
  AlertTriangle, Star, DollarSign, TrendingUp
} from 'lucide-react';

import { useAdminProducts } from '../../../hooks/dashboardAdmin/useProducts';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export default function AdminProductsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 9;

  const { data, loading, error } = useAdminProducts();
  const products = data?.items || [];

  const formatCurrency = (value: number) => {
    return (value / 1000000).toFixed(1) + 'M₫';
  };

  const getStatusConfig = (status: string) => {
    const configs: { [key: string]: { bg: string; text: string; label: string; icon: any } } = {
      approved: { bg: 'bg-green-100', text: 'text-green-800', label: 'Đã duyệt', icon: CheckCircle },
      pending: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Chờ duyệt', icon: AlertTriangle },
      rejected: { bg: 'bg-red-100', text: 'text-red-800', label: 'Từ chối', icon: XCircle },
    };
    return configs[status] || configs.pending;
  };

  const filteredProducts = products.filter((product: any) => {
    if (statusFilter !== 'all' && product.status !== statusFilter) return false;
    if (categoryFilter !== 'all' && product.category !== categoryFilter) return false;
    if (searchQuery &&
      !product.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
      !product.store.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  const totalPages = Math.ceil(filteredProducts.length / itemsPerPage);
  const paginatedProducts = filteredProducts.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const stats = [
    { label: 'Tổng sản phẩm', value: products.length, color: 'blue' },
    { label: 'Đã duyệt', value: products.filter((p: any) => p.status === 'approved').length, color: 'green' },
    { label: 'Chờ duyệt', value: products.filter((p: any) => p.status === 'pending').length, color: 'yellow' },
    { label: 'Từ chối', value: products.filter((p: any) => p.status === 'rejected').length, color: 'red' },
  ];

  if (loading) return <div>Loading products...</div>;
  if (error) return <div>Error loading products: {error.message}</div>;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Quản lý sản phẩm</h1>
        <p className="text-gray-600 mt-2">Kiểm duyệt và quản lý sản phẩm trên platform</p>
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

      {/* Filters */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Tìm sản phẩm, cửa hàng..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">Tất cả danh mục</option>
            <option value="Giày thể thao">Giày thể thao</option>
            <option value="Giày casual">Giày casual</option>
            <option value="Giày cao gót">Giày cao gót</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">Tất cả trạng thái</option>
            <option value="approved">Đã duyệt</option>
            <option value="pending">Chờ duyệt</option>
            <option value="rejected">Từ chối</option>
          </select>
        </div>
      </div>

      {/* Products Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {paginatedProducts.map((product) => {
          const statusConfig = getStatusConfig(product.status);
          const StatusIcon = statusConfig.icon;

          return (
            <div key={product.id} className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden hover:shadow-xl transition-shadow">
              {/* Product Image */}
              <div className="relative h-48 bg-gray-100">
                <img
                  src={product.image ? `${BACKEND_URL}${product.image}` : 'https://via.placeholder.com/200/CCCCCC/FFFFFF?text=No+Image'}
                  alt={product.name}
                  className="w-full h-full object-cover"
                />
                <div className="absolute top-3 right-3">
                  <span className={`inline-flex items-center space-x-1 px-3 py-1 rounded-full text-xs font-semibold ${statusConfig.bg} ${statusConfig.text}`}>
                    <StatusIcon className="h-3 w-3" />
                    <span>{statusConfig.label}</span>
                  </span>
                </div>
              </div>

              {/* Product Info */}
              <div className="p-6">
                <h3 className="font-bold text-lg text-gray-900 mb-1">{product.name}</h3>
                <p className="text-sm text-gray-500 mb-3">📦 {product.store}</p>

                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-medium text-gray-600 bg-gray-100 px-2 py-1 rounded">
                    {product.category}
                  </span>
                  <div className="flex items-center space-x-1">
                    <Star className="h-4 w-4 text-yellow-500 fill-current" />
                    <span className="font-semibold text-sm">{product.rating}</span>
                    <span className="text-xs text-gray-500">({product.reviews})</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 mb-4 py-3 border-t border-gray-100">
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Giá bán</p>
                    <p className="font-bold text-blue-600">{formatCurrency(product.price)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Đã bán</p>
                    <p className="font-bold text-green-600">{product.sold}</p>
                  </div>
                </div>

                <div className="mb-4">
                  <p className="text-xs text-gray-500 mb-1">Tồn kho</p>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${product.stock > 50 ? 'bg-green-500' : product.stock > 0 ? 'bg-yellow-500' : 'bg-red-500'}`}
                      style={{ width: `${Math.min((product.stock / 200) * 100, 100)}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-600 mt-1">{product.stock} sản phẩm</p>
                </div>

                {/* Actions */}
                <div className="flex items-center space-x-2">
                  <button className="flex-1 px-3 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors font-medium text-sm">
                    <Eye className="h-4 w-4 inline mr-1" />
                    Chi tiết
                  </button>
                  {product.status === 'pending' && (
                    <>
                      <button className="px-3 py-2 bg-green-50 text-green-600 rounded-lg hover:bg-green-100 transition-colors">
                        <CheckCircle className="h-4 w-4" />
                      </button>
                      <button className="px-3 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors">
                        <XCircle className="h-4 w-4" />
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Pagination */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 px-6 py-4 flex items-center justify-between">
        <p className="text-sm text-gray-600">
          Hiển thị {(currentPage - 1) * itemsPerPage + 1} - {Math.min(currentPage * itemsPerPage, filteredProducts.length)} / {filteredProducts.length}
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
  );
}
