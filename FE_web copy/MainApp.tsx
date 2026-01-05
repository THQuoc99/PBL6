// MainApp.tsx
import React, { useState, useEffect } from "react";
import DashboardPage from "./components/pages/seller/DashboardPage";
import {
  CustomerHomePage,
  CustomerProductsPage,
  CustomerProductDetailPage,
  CustomerStorePage,
  CustomerPaymentPage,
  CustomerPromotionsPage,
  CustomerContactPage,
  CustomerCartPage,
  CustomerWishlistPage,
  CustomerAccountPage,
  CollectionsPage,
  SellerProductsPage,
  OrdersPage,
  ListingsPage,
  PromotionsPage,
  ChatbotAIPage,
  PaymentsPage,
  SettingsPage,
  AdminLayout,
  PlatformAdminLayout,
  AdminDashboardPage,
  AdminStoresPage,
  AdminUsersPage,
  AdminOrdersPage,
  AdminProductsPage,
  AdminAnalyticsPage,
  AdminReportsPage,
  AdminVouchersPage
} from "./components";
import { MenuItems, Product, Order, StoreSettings } from "./types";

type AppPage =
  | "customer-home"
  | "customer-products"
  | "customer-product-detail"
  | "customer-store"
  | "customer-payment"
  | "customer-promotions"
  | "customer-contact"
  | "customer-cart"
  | "customer-wishlist"
  | "customer-account"
  | "collections"
  | "seller-dashboard"
  | "platform-admin";

type AdminMenuItem = 
  | 'dashboard' 
  | 'stores' 
  | 'users' 
  | 'orders' 
  | 'products' 
  | 'analytics'
  | 'reports'
  | 'vouchers';

interface MainAppProps {
  initialPage?: AppPage;
}

export default function MainApp({ initialPage = "customer-home" }: MainAppProps) {
  const [currentAppPage, setCurrentAppPage] = useState<AppPage>(initialPage);
  const [currentSellerPage, setCurrentSellerPage] = useState<MenuItems>("dashboard");
  const [currentAdminPage, setCurrentAdminPage] = useState<AdminMenuItem>("dashboard");

  useEffect(() => setCurrentAppPage(initialPage), [initialPage]);

  const [products, setProducts] = useState<Product[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [settings, setSettings] = useState<StoreSettings>({
    storeName: "SHOEX Store",
    email: "",
    phone: "",
    address: "",
    currency: "VND",
    shipping: { cod: true, express: true, standard: true }
  });

  const storeData = {
    name: settings.storeName,
    totalProducts: products.length,
    totalOrders: orders.length,
    totalRevenue: orders.reduce((sum, o) => sum + o.amount, 0),
    totalCustomers: 892
  };

  const handleSellerMenuChange = (menu: MenuItems) => setCurrentSellerPage(menu);
  const handleAdminMenuChange = (menu: AdminMenuItem) => setCurrentAdminPage(menu);

  const renderSellerPageContent = () => {
    switch (currentSellerPage) {
      case "dashboard": return <DashboardPage onNavigate={handleSellerMenuChange} />;
      case "products": return <SellerProductsPage products={products} setProducts={setProducts} />;
      case "orders": return <OrdersPage orders={orders} setOrders={setOrders} query="" />;
      case "promotions": return <PromotionsPage />;
      case "chatbot": return <ChatbotAIPage />;
      case "payments": return <PaymentsPage />;
      case "settings": return <SettingsPage settings={settings} setSettings={setSettings} />;
      default: return <DashboardPage onNavigate={handleSellerMenuChange} />;
    }
  };

  const renderAdminPageContent = () => {
    switch (currentAdminPage) {
      case "dashboard": return <AdminDashboardPage />;
      case "stores": return <AdminStoresPage />;
      case "users": return <AdminUsersPage />;
      case "orders": return <AdminOrdersPage />;
      case "products": return <AdminProductsPage />;
        case "analytics": return <AdminAnalyticsPage />;
        case "reports": return <AdminReportsPage />;
        case "vouchers": return <AdminVouchersPage />;
      default: return <AdminDashboardPage />;
    }
  };

  switch (currentAppPage) {
    case "customer-home": return <CustomerHomePage />;
    case "customer-products": return <CustomerProductsPage />;
    case "customer-product-detail": return <CustomerProductDetailPage />;
    case "customer-store": return <CustomerStorePage />;
    case "customer-payment": return <CustomerPaymentPage />;
    case "customer-promotions": return <CustomerPromotionsPage />;
    case "customer-contact": return <CustomerContactPage />;
    case "customer-cart": return <CustomerCartPage />;
    case "customer-wishlist": return <CustomerWishlistPage />;
    case "customer-account": return <CustomerAccountPage />;
    case "collections": return <CollectionsPage />;
    case "seller-dashboard":
      return (
        <AdminLayout currentPage={currentSellerPage} onMenuChange={handleSellerMenuChange} storeData={storeData}>
          {renderSellerPageContent()}
        </AdminLayout>
      );
    case "platform-admin":
      return (
        <PlatformAdminLayout currentPage={currentAdminPage} onMenuChange={handleAdminMenuChange}>
          {renderAdminPageContent()}
        </PlatformAdminLayout>
      );
    default: return <CustomerHomePage />;
  }
}
