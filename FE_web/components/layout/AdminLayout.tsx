import React from 'react';
import Sidebar from '../pages/seller/Sidebar';
import { AskAI } from '../index';
import { MenuItems } from '../../types';

interface AdminLayoutProps {
  children: React.ReactNode;
  currentPage: MenuItems;
  onMenuChange: (menu: MenuItems) => void;
  storeData?: any;
}

export default function AdminLayout({ children, currentPage, onMenuChange, storeData }: AdminLayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <Sidebar activeMenu={currentPage} onMenuChange={onMenuChange} />
          </div>
          
          {/* Main Content */}
          <div className="lg:col-span-3">
            <div className="space-y-6">
              {children}
            </div>
          </div>
        </div>
      </div>
      
      {/* Ask AI Assistant */}
      <AskAI currentComponent={currentPage} storeData={storeData} />
    </div>
  );
}