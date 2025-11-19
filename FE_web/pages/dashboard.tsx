/**
 * Trang Dashboard - Sử dụng API với authentication
 */

import { useState, useEffect } from 'react';
import { useAuth, useAuthenticatedApi } from '../hooks/useAuth';
import ProtectedRoute from '../components/ProtectedRoute';

interface User {
  id: string;
  username: string;
  email: string;
  fullName: string;
  role: string;
}

export default function Dashboard() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const { user, logout } = useAuth();
  const { apiCall } = useAuthenticatedApi();

  // Lấy danh sách users khi component mount
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const query = `
          query {
            users {
              id
              username
              email
              fullName
              role
            }
          }
        `;

        // ĐÂY LÀ CÁCH DÙNG ACCESS TOKEN - tự động gửi trong header!
        const result = await apiCall(query);
        
        if (result.data?.users) {
          setUsers(result.data.users);
        }
      } catch (error) {
        console.error('Lỗi khi lấy danh sách users:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, [apiCall]);

  const handleCreateUser = async () => {
    try {
      const query = `
        mutation {
          userCreate(input: {
            fullName: "Test User ${Date.now()}"
            username: "testuser${Date.now()}"
            email: "test${Date.now()}@example.com"
            password: "password123"
            role: "buyer"
          }) {
            success
            message
            user {
              id
              username
              email
              fullName
              role
            }
          }
        }
      `;

      // API call với authentication tự động!
      const result = await apiCall(query);
      
      if (result.data?.userCreate?.success) {
        // Refresh danh sách users
        const refreshQuery = `
          query {
            users {
              id
              username
              email
              fullName
              role
            }
          }
        `;
        
        const refreshResult = await apiCall(refreshQuery);
        if (refreshResult.data?.users) {
          setUsers(refreshResult.data.users);
        }
        
        alert('Tạo user thành công!');
      } else {
        alert('Lỗi khi tạo user: ' + result.data?.userCreate?.message);
      }
    } catch (error) {
      console.error('Lỗi khi tạo user:', error);
      alert('Lỗi khi tạo user');
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-100">
        {/* Header */}
        <nav className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-semibold">SHOEX Dashboard</h1>
              </div>
              
              <div className="flex items-center space-x-4">
                <span className="text-gray-700">
                  Xin chào, {user?.fullName} ({user?.role})
                </span>
                <button
                  onClick={logout}
                  className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
                >
                  Đăng xuất
                </button>
              </div>
            </div>
          </div>
        </nav>

        {/* Main content */}
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            {/* Stats */}
            <div className="mb-6">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="text-2xl font-bold text-gray-900">
                        {users.length}
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Tổng số users
                        </dt>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="mb-6">
              <button
                onClick={handleCreateUser}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              >
                Tạo User Mới (Test API)
              </button>
            </div>

            {/* Users List */}
            <div className="bg-white shadow overflow-hidden sm:rounded-md">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Danh sách Users
                </h3>
                
                {loading ? (
                  <div className="text-center py-4">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                    <p className="mt-2 text-gray-500">Đang tải...</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            ID
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Username
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Họ tên
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Email
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Role
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {users.map((user) => (
                          <tr key={user.id}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {user.id}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {user.username}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {user.fullName}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {user.email}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                user.role === 'admin' ? 'bg-red-100 text-red-800' :
                                user.role === 'seller' ? 'bg-blue-100 text-blue-800' :
                                'bg-green-100 text-green-800'
                              }`}>
                                {user.role}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}