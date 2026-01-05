export type Product = {
  id: string;
  name: string;
  sku: string;
  category?: string;
  stock: number;
  price: number;
  images?: string[]; // data URLs
  createdAt?: string; // ISO date string
  // Demo-only: extra fields to match backend payload shape
  attributes?: Array<{
    name: string;
    type?: "Size" | "Color" | "Custom";
    // values can be simple strings or objects with image for color
    values: Array<string | { value: string; image?: string }>;
  }>;
  variants?: Array<{
    id: string;
    sku?: string;
    price?: number;
    stock?: number;
    attributes?: { name: string; value: string }[];
  }>;
  active?: boolean;
};

export type OrderStatus = "Processing" | "Shipped" | "Delivered" | "Cancelled";

export type Order = {
  id: string;
  customer: string;
  status: OrderStatus;
  date: string; // ISO
  amount: number;
  items: { productId: string; qty: number; price: number }[];
};

export type Promotion = {
  id: string;
  code: string;
  type: "percent" | "fixed";
  value: number;
  active: boolean;
  startsAt?: string;
  endsAt?: string;
};

export type Transaction = {
  id: string;
  type: "sale" | "fee" | "refund" | "payout";
  amount: number;
  date: string;
  status: "pending" | "completed";
  reference?: string;
};

export type StoreSettings = {
  storeName: string;
  email: string;
  phone: string;
  address: string;
  currency: string;
  logo?: string; // data URL
  avatar?: string; // data URL or URL
  coverImage?: string; // data URL or URL
  shipping: {
    cod: boolean;
    express: boolean;
    standard: boolean;
  };
};

export type MenuItems = "dashboard" | "products" | "orders" | "promotions" | "payments" | "settings" | "chatbot";

export type ChartData = {
  name: string;
  value: number;
  [key: string]: any;
};

export interface MetricCardProps {
  title: string;
  value: string;
  sub?: string;
  icon?: React.ReactNode;
}

export interface SidebarProps {
  activeMenu: MenuItems;
  onMenuChange: (menu: MenuItems) => void;
}