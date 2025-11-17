"use client";

import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import {
  BarChart3,
  ShoppingCart,
  DollarSign,
  Package,
} from "lucide-react";

// Import types
import { Product, Order, MenuItems, StoreSettings } from "./types";

// Import components
import {
  Sidebar,
  MetricCard,
  SalesChart,
  SellerProductsPage as ProductsPageComponent,
  OrdersPage as OrdersPageComponent,
  ListingsPage as ListingsPageComponent,
  PromotionsPage as PromotionsPageComponent,
  PaymentsPage as PaymentsPageComponent,
  SettingsPage as SettingsPageComponent,
  ChatbotAIPage as ChatbotAIPageComponent,
  AskAI,
} from "./components";

// Mock data và utility functions (simplified)
const fmt = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });
const uid = (prefix: string) => prefix + "_" + Math.random().toString(36).substr(2, 9);

const initialProducts: Product[] = [
  { id: uid("P"), name: "Premium Headphones", sku: "HP001", stock: 24, price: 199.99, active: true },
  { id: uid("P"), name: "Wireless Mouse", sku: "WM002", stock: 45, price: 29.99, active: true },
  { id: uid("P"), name: "Gaming Keyboard", sku: "GK003", stock: 18, price: 129.99, active: true },
];

const initialOrders: Order[] = [
  { id: uid("O"), customer: "John Doe", status: "Processing", date: new Date().toISOString(), amount: 199.99, items: [] },
  { id: uid("O"), customer: "Jane Smith", status: "Shipped", date: new Date().toISOString(), amount: 159.98, items: [] },
];

// Simple Dashboard Page Component
function DashboardPage({ products, orders }: { products: Product[]; orders: Order[] }) {
  const sales = useMemo(() => {
    // Mock last 7 days sales data
    const days = 7;
    const today = new Date();
    return Array.from({ length: days }).map((_, i) => {
      const d = new Date(today);
      d.setDate(today.getDate() - (days - 1 - i));
      const name = d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
      const value = Math.round(500 + Math.random() * 2000);
      return { name, value, sales: value }; // Added 'sales' for backward compatibility
    });
  }, []);

  const totalRevenue = orders.reduce((sum, o) => sum + o.amount, 0);
  const todaySales = sales[sales.length - 1]?.value || 0;

  return (
    <div className="space-y-6">
      {/* Metrics Section */}
      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard 
          title="Today's Sales" 
          value={fmt.format(todaySales)} 
          sub="vs yesterday +12%" 
          icon={<BarChart3 className="h-5 w-5" />} 
        />
        <MetricCard 
          title="Total Orders" 
          value={String(orders.length)} 
          sub="7 pending fulfillment" 
          icon={<ShoppingCart className="h-5 w-5" />} 
        />
        <MetricCard 
          title="Total Revenue" 
          value={fmt.format(totalRevenue)} 
          sub="last 30 days" 
          icon={<DollarSign className="h-5 w-5" />} 
        />
        <MetricCard 
          title="Active Products" 
          value={String(products.filter((p) => p.active !== false).length)} 
          sub="Live listings" 
          icon={<Package className="h-5 w-5" />} 
        />
      </section>

      {/* Charts Section */}
      <section className="grid gap-6 lg:grid-cols-2">
        <SalesChart data={sales} />
        
        {/* Top Products Table */}
        <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
          <div className="mb-2 flex items-center justify-between">
            <h3 className="text-lg font-semibold">Top Products (by stock)</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500">
                  <th className="px-3 py-2 font-medium">Product</th>
                  <th className="px-3 py-2 font-medium">SKU</th>
                  <th className="px-3 py-2 font-medium">Stock</th>
                  <th className="px-3 py-2 font-medium">Price</th>
                </tr>
              </thead>
              <tbody>
                {products.slice(0, 5).map((p) => (
                  <tr key={p.id} className="border-t border-gray-100">
                    <td className="px-3 py-3 font-medium text-gray-900">{p.name}</td>
                    <td className="px-3 py-3">{p.sku}</td>
                    <td className="px-3 py-3">{p.stock}</td>
                    <td className="px-3 py-3">{fmt.format(p.price)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>
  );
}

// Simple placeholder pages
function DefaultPage() {
  return <div className="p-4 text-center text-gray-500">Coming soon...</div>;
}

// Main Dashboard Component
export default function SellerDashboard() {
  const [activeMenu, setActiveMenu] = useState<MenuItems>("dashboard");
  const [products, setProducts] = useState<Product[]>(initialProducts);
  const [orders, setOrders] = useState<Order[]>(initialOrders);
  const [query, setQuery] = useState<string>("");
  const defaultSettings: StoreSettings = {
    storeName: "My Store",
    email: "owner@example.com",
    phone: "+84 912 345 678",
    address: "Ho Chi Minh City, Vietnam",
    currency: "USD",
    logo: "",
    avatar: "https://nganhquangcao.vn/upload/filemanager/files/adidas-logo-lich-su-y-nghia-bieu-tuong-adidas-5.jpg",
    coverImage: "https://aobongda.net/pic/Images/Module/News/images/giay-dep-nhat-10.jpg",
    shipping: {
      cod: true,
      express: true,
      standard: true,
    },
  };
  const [settings, setSettings] = useState<StoreSettings>(defaultSettings);

  const renderPage = () => {
    switch (activeMenu) {
      case "dashboard":
        return <DashboardPage products={products} orders={orders} />;
      case "products":
        return <ProductsPageComponent products={products} setProducts={setProducts} />;
      case "orders":
        return <OrdersPageComponent orders={orders} setOrders={setOrders} query={query} />;
      case "listings":
        return <ListingsPageComponent />;
      case "promotions":
        return <PromotionsPageComponent />;
      case "payments":
        return <PaymentsPageComponent />;
      case "chatbot":
        return <ChatbotAIPageComponent />;
      case "settings":
        return <SettingsPageComponent settings={settings} setSettings={setSettings} />;
      default:
        return <DefaultPage />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Full-bleed layout: remove centered max-width to align to viewport edges */}
      <div className="grid w-full grid-cols-1 gap-6 p-0 md:grid-cols-[260px_1fr] md:px-6 md:py-8">
        {/* Sidebar */}
        <Sidebar activeMenu={activeMenu} onMenuChange={setActiveMenu} />

        {/* Main Content */}
        <main className="space-y-6">
          {renderPage()}
        </main>
      </div>

      {/* AI Assistant - Floating across all pages */}
      <AskAI 
        currentComponent={activeMenu}
        storeData={{
          products,
          orders,
          settings,
          stats: {
            totalProducts: products.length,
            totalOrders: orders.length,
            totalRevenue: orders.reduce((sum, order) => sum + order.amount, 0),
            activeProducts: products.filter(p => p.active !== false).length,
          }
        }}
      />
    </div>
  );
}