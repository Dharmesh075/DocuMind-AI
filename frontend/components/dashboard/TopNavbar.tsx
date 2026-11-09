"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { FileText, Upload, BarChart3, Settings, Layers } from "lucide-react";

const NAV_ITEMS = [
  { label: "Workspace", href: "/", icon: Layers },
  { label: "Documents", href: "/documents", icon: FileText },
  { label: "Upload", href: "/upload", icon: Upload },
  { label: "Analytics", href: "/analytics", icon: BarChart3 },
  { label: "Settings", href: "/settings", icon: Settings },
];

export default function TopNavbar() {
  const pathname = usePathname();

  return (
    <header className="h-14 glass-header px-6 flex items-center justify-between sticky top-0 z-40 select-none">
      {/* Brand */}
      <div className="flex items-center gap-8">
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center text-white font-semibold text-xs shadow-sm">
            D
          </div>
          <span className="font-semibold text-sm tracking-tight text-slate-100">
            DocuMind <span className="text-blue-400 font-normal">AI</span>
          </span>
        </Link>

        {/* Navigation Tabs */}
        <nav className="hidden md:flex items-center gap-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  isActive
                    ? "bg-white/[0.08] text-white"
                    : "text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]"
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? "text-blue-400" : "text-slate-500"}`} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3">
        <Link
          href="/upload"
          className="btn-primary flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs"
        >
          <Upload className="w-3.5 h-3.5" />
          <span>Upload File</span>
        </Link>
      </div>
    </header>
  );
}
