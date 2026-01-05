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
      <div className="max-w-[2560px] mx-auto px-2 sm:px-3 lg:px-4 py-6">
        <div className="flex flex-col lg:flex-row items-start gap-4 lg:gap-6">
          {/* Sidebar (fixed width) */}
          <div className="w-full lg:w-[220px] flex-shrink-0">
            <Sidebar activeMenu={currentPage} onMenuChange={onMenuChange} />
          </div>

          {/* Main Content (flex-1 so it sits flush to sidebar) */}
          <div className="flex-1">
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