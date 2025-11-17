import React, { useState } from 'react';
import AuthLayout from '../../layout/AuthLayout';
import { Eye, EyeOff, User, Lock, Mail, Phone, Store, Chrome } from 'lucide-react';

interface SellerRegisterPageProps {
  onRegister?: (formData: any) => void;
  onNavigateToLogin?: () => void;
  onBackToCustomer?: () => void;
}

export default function SellerRegisterPage({ onRegister, onNavigateToLogin, onBackToCustomer }: SellerRegisterPageProps) {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    shopName: '',
    phoneNumber: '',
    agreeTerms: false
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.username) {
      newErrors.username = 'Tên đăng nhập là bắt buộc';
    }

    if (!formData.email) {
      newErrors.email = 'Email là bắt buộc';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email không hợp lệ';
    }

    if (!formData.shopName) {
      newErrors.shopName = 'Tên cửa hàng là bắt buộc';
    }

    if (!formData.phoneNumber) {
      newErrors.phoneNumber = 'Số điện thoại là bắt buộc';
    }

    if (!formData.password) {
      newErrors.password = 'Mật khẩu là bắt buộc';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Mật khẩu phải có ít nhất 6 ký tự';
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Xác nhận mật khẩu là bắt buộc';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Mật khẩu xác nhận không khớp';
    }

    if (!formData.agreeTerms) {
      newErrors.agreeTerms = 'Bạn phải đồng ý với điều khoản sử dụng';
    }

    return newErrors;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const newErrors = validateForm();
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    alert('Tính năng đăng ký đang được phát triển. Vui lòng sử dụng tài khoản demo để đăng nhập.');
  };

  const handleGoogleRegister = () => {
    alert('Tính năng đăng ký Google đang được phát triển');
  };

  return (
    <AuthLayout title="Đăng ký Seller">
      <div className="w-full max-w-md mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Đăng ký Seller</h1>
          <p className="text-gray-600">Tạo tài khoản để bán hàng trên SHOEX</p>
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-yellow-800">
            <strong>Lưu ý:</strong> Tính năng đăng ký đang được phát triển. 
            Vui lòng sử dụng tài khoản demo để trải nghiệm.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic form fields */}
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
              Tên đăng nhập
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <User className="h-5 w-5 text-gray-400" />
              </div>
              <input
                id="username"
                type="text"
                value={formData.username}
                onChange={(e) => handleInputChange('username', e.target.value)}
                className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Nhập tên đăng nhập"
              />
            </div>
            {errors.username && <p className="mt-1 text-sm text-red-600">{errors.username}</p>}
          </div>

          <button
            type="submit"
            className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 transition-colors"
          >
            Đăng ký
          </button>

          <div className="flex flex-col space-y-3 text-center">
            <button
              type="button"
              onClick={onNavigateToLogin}
              className="text-sm text-blue-600 hover:text-blue-500 transition-colors"
            >
              Đã có tài khoản? Đăng nhập ngay
            </button>
            
            <button
              type="button"
              onClick={onBackToCustomer}
              className="text-sm text-gray-600 hover:text-gray-500 transition-colors"
            >
              ← Quay lại trang khách hàng
            </button>
          </div>
        </form>
      </div>
    </AuthLayout>
  );
}