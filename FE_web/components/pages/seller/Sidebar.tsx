import { 
  LayoutDashboard,
  Package,
  ShoppingCart,
  Tags,
  Megaphone,
  CreditCard,
  Settings,
  Store,
  MessageSquare,
} from "lucide-react";
import { SidebarProps } from "../../../types";

interface NavItemProps {
  icon: React.ReactNode;
  label: string;
  active: boolean;
  onClick: () => void;
}

const NavItem = ({ icon, label, active, onClick }: NavItemProps) => {
  return (
    <button
      onClick={onClick}
      className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left font-medium transition ${
        active
          ? "bg-gray-900 text-white"
          : "text-gray-700 hover:bg-gray-100"
      }`}
    >
      {icon}
      {label}
    </button>
  );
};

export default function Sidebar({ activeMenu, onMenuChange }: SidebarProps) {
  const menuItems = [
    { key: "dashboard" as const, icon: <LayoutDashboard className="h-4 w-4" />, label: "Dashboard" },
    { key: "products" as const, icon: <Package className="h-4 w-4" />, label: "Products" },
    { key: "orders" as const, icon: <ShoppingCart className="h-4 w-4" />, label: "Orders" },
    { key: "listings" as const, icon: <Tags className="h-4 w-4" />, label: "Listings" },
  { key: "promotions" as const, icon: <Megaphone className="h-4 w-4" />, label: "Promotions" },
  { key: "chatbot" as const, icon: <MessageSquare className="h-4 w-4" />, label: "Chatbot AI" },
    { key: "payments" as const, icon: <CreditCard className="h-4 w-4" />, label: "Payments" },
    { key: "settings" as const, icon: <Settings className="h-4 w-4" />, label: "Settings" },
  ];

  return (
    <aside className="sticky top-4 h-fit rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
      <div className="mb-6 flex items-center gap-2 px-2">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gray-900 text-white">
          <Store className="h-5 w-5" />
        </div>
        <div>
          <div className="text-sm font-semibold">Seller Center</div>
          <div className="text-xs text-gray-500">
            {menuItems.find(item => item.key === activeMenu)?.label}
          </div>
        </div>
      </div>

      <nav className="grid gap-1 text-sm">
        {menuItems.map((item) => (
          <NavItem
            key={item.key}
            icon={item.icon}
            label={item.label}
            active={activeMenu === item.key}
            onClick={() => onMenuChange(item.key)}
          />
        ))}
      </nav>

      <div className="mt-6 rounded-xl bg-gray-50 p-3 text-xs text-gray-500">
        Tip: Keep your listings updated to improve conversion.
      </div>
    </aside>
  );
}