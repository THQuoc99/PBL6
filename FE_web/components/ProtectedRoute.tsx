/**
 * Component bảo vệ route - yêu cầu đăng nhập
 */

import { useRouter } from 'next/router';
import { useAuth } from '../hooks/useAuth';
import { useEffect } from 'react';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string; // Optional: Yêu cầu role cụ thể
}

export default function ProtectedRoute({ 
  children, 
  requiredRole 
}: ProtectedRouteProps) {
  const { user, loading, isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      // Nếu chưa đăng nhập → redirect login
      if (!isAuthenticated) {
        router.push('/auth/login');
        return;
      }

      // Nếu có yêu cầu role cụ thể
      if (requiredRole && user?.role !== requiredRole) {
        router.push('/unauthorized'); // Trang báo không đủ quyền
        return;
      }
    }
  }, [loading, isAuthenticated, user, requiredRole, router]);

  // Show loading
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  // Chưa đăng nhập hoặc không đủ quyền
  if (!isAuthenticated || (requiredRole && user?.role !== requiredRole)) {
    return null; // Router sẽ redirect
  }

  // Đã xác thực → hiển thị content
  return <>{children}</>;
}