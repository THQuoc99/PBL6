import React from 'react';
import { ShoppingBag } from 'lucide-react';

interface AuthLayoutProps {
  children: React.ReactNode;
  title: string;
  subtitle?: string;
}

export default function AuthLayout({ children, title, subtitle }: AuthLayoutProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        {/* Logo */}
        <div className="text-center">
          <div className="flex justify-center items-center space-x-2 mb-4">
            <ShoppingBag className="h-12 w-12 text-blue-600" />
            <span className="text-3xl font-bold text-gray-900">SHOEX</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
          {subtitle && <p className="mt-2 text-sm text-gray-600">{subtitle}</p>}
        </div>

        {/* Form Content */}
        <div className="bg-white py-8 px-6 shadow-xl rounded-2xl border border-gray-100">
          {children}
        </div>

        {/* Footer */}
        <div className="text-center text-sm text-gray-600">
          <p>&copy; 2024 SHOEX. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
}