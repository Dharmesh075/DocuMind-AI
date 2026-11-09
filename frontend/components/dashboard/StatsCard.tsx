import { LucideIcon } from "lucide-react";

interface StatsCardProps {
  title: string;
  value: string | number;
  subtitle: string;
  icon: LucideIcon;
  variant?: "blue" | "indigo" | "emerald" | "amber";
}

export default function StatsCard({
  title,
  value,
  subtitle,
  icon: Icon,
  variant = "blue",
}: StatsCardProps) {
  const variantStyles = {
    blue: {
      border: "border-white/[0.08] hover:border-blue-500/30",
      icon: "bg-blue-500/10 text-blue-400 border-blue-500/20",
    },
    indigo: {
      border: "border-white/[0.08] hover:border-indigo-500/30",
      icon: "bg-indigo-500/10 text-indigo-400 border-indigo-500/20",
    },
    emerald: {
      border: "border-white/[0.08] hover:border-emerald-500/30",
      icon: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    },
    amber: {
      border: "border-white/[0.08] hover:border-amber-500/30",
      icon: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    },
  }[variant];

  // Outer container: rounded-2xl (16px), p-4 (16px) -> inner icon container: rounded-lg (8px)
  return (
    <div className={`p-4 rounded-2xl border ${variantStyles.border} bg-[#0E1526]/80 transition-colors shadow-sm`}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium text-slate-300">{title}</span>
        <div className={`w-8 h-8 rounded-lg border flex items-center justify-center ${variantStyles.icon}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>

      <div className="text-2xl font-bold tracking-tight text-white mb-1 tabular-nums font-mono">
        {value}
      </div>

      <div className="text-[11px] text-slate-400">
        {subtitle}
      </div>
    </div>
  );
}
