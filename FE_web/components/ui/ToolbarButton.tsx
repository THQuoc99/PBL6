interface ToolbarButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
}

export default function ToolbarButton({ children, onClick }: ToolbarButtonProps) {
  return (
    <button 
      onClick={onClick} 
      className="inline-flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm font-medium shadow-sm hover:bg-gray-50"
    >
      {children}
    </button>
  );
}