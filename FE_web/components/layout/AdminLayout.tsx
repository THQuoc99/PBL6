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
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <Sidebar activeMenu={currentPage} onMenuChange={onMenuChange} />
      
      {/* Main Content */}
      <div className="flex-1 ml-64">
        <div className="p-6">
          {children}
        </div>
      </div>
      
      {/* Ask AI Assistant */}
      <AskAI currentComponent={currentPage} storeData={storeData} />
    </div>
  );
}