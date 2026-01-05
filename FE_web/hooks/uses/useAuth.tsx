/**
 * React Hook cho Authentication
 */

import { useState, useEffect, createContext, useContext } from 'react';
import { authService } from '../../services/auth';
import { storeService } from '../../services/store';

interface User {
  id: string;
  username: string;
  email: string;
  fullName: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<any>;
  logout: () => void;
  register: (userData: any) => Promise<any>;
}

const AuthContext = createContext<AuthContextType | null>(null);

// Provider component
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Kiểm tra authentication khi app load
    const initAuth = () => {
      try {
        if (authService.isAuthenticated()) {
          const currentUser = authService.getCurrentUser();
          setUser(currentUser);
        }
      } catch (error) {
        console.error('Init auth error:', error);
        authService.logout();
      } finally {
        setLoading(false);
      }
    };

    initAuth();
    
    // Listen for auth state changes
    const unsubscribe = authService.addAuthStateListener(() => {
      if (authService.isAuthenticated()) {
        const currentUser = authService.getCurrentUser();
        setUser(currentUser);
      } else {
        setUser(null);
      }
    });

    return unsubscribe;
  }, []);

  const login = async (username: string, password: string) => {
    setLoading(true);
    try {
      const result = await authService.login(username, password);
      
      if (result.success && result.user) {
        setUser(result.user);
      }
      
      return result;
    } catch (error) {
      console.error('Login hook error:', error);
      return { success: false, message: 'Lỗi đăng nhập' };
    } finally {
      setLoading(false);
    }
  };
  const logout = () => {
    authService.logout();
    storeService.clearCurrentStore(); // Xóa store khi logout
    setUser(null);
  };
  const register = async (userData: any) => {
    setLoading(true);
    try {
      const result = await authService.register(userData);
      return result;
    } catch (error) {
      console.error('Register hook error:', error);
      return { success: false, message: 'Lỗi đăng ký' };
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: !!user,
        login,
        logout,
        register
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

// Hook để sử dụng auth context
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}

// Hook để gọi API với authentication
export function useAuthenticatedApi() {
  const { logout } = useAuth();

  const apiCall = async (query: string, variables?: any) => {
    try {
      return await authService.apiCall(query, variables);
    } catch (error: any) {
      if (error.message.includes('Authentication failed')) {
        logout();
      }
      throw error;
    }
  };

  return { apiCall };
}