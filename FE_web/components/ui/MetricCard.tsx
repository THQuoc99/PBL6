import { motion } from "framer-motion";
import { MetricCardProps } from "../../types";

export default function MetricCard({ title, value, sub, icon }: MetricCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm"
    >
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-500">{title}</div>
        {icon && <div className="text-gray-400">{icon}</div>}
      </div>
      <div className="mt-2 text-3xl font-semibold tracking-tight">{value}</div>
      {sub && <div className="mt-1 text-xs text-gray-400">{sub}</div>}
    </motion.div>
  );
}