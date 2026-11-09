"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  FileText,
  UploadCloud,
  BarChart3,
  Settings,
  Sparkles,
  Layers,
  ShieldCheck,
  Cpu
} from "lucide-react";

const NAV_ITEMS = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Documents", href: "/documents", icon: FileText },
  { name: "Upload", href: "/upload", icon: UploadCloud },
  { name: "Analytics", href: "/analytics", icon: BarChart3 },
  { name: "Settings", href: "/settings", icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 glass-sidebar min-h-screen p-5 flex flex-col justify-between select-none">
      <div>
        {/* Brand Header */}
        <Link href="/" className="flex items-center gap-3 mb-8 px-2 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 via-sky-500 to-violet-500 p-[1px] shadow-lg shadow-indigo-500/20 group-hover:shadow-indigo-500/40 transition-all">
            <div className="w-full h-full bg-[#090D18] rounded-[11px] flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-sky-400" />
            </div>
          </div>
          <div>
            <div className="font-semibold text-lg tracking-tight text-white flex items-center gap-1.5">
              DocuMind <span className="text-xs px-1.5 py-0.5 rounded bg-sky-500/20 text-sky-400 font-mono">AI</span>
            </div>
            <div className="text-[11px] text-slate-400 leading-none">Intelligent IDP Platform</div>
          </div>
        </Link>

        {/* Navigation Section */}
        <div className="space-y-1">
          <div className="text-[10px] uppercase font-semibold text-slate-400 px-3 mb-2 tracking-wider">
            Workspace
          </div>
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? "bg-white/10 text-white border border-white/15 shadow-sm shadow-indigo-500/10 backdrop-blur-md"
                    : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-sky-400" : "text-slate-400"}`} />
                <span>{item.name}</span>
                {item.name === "Upload" && (
                  <span className="ml-auto text-[10px] bg-indigo-500/20 text-indigo-300 px-1.5 py-0.5 rounded-full font-mono">
                    New
                  </span>
                )}
              </Link>
            );
          })}
        </div>

        {/* Pipeline Info Card */}
        <div className="mt-8 p-3.5 rounded-2xl bg-white/[0.03] border border-white/10 backdrop-blur-sm">
          <div className="flex items-center gap-2 text-xs font-medium text-slate-300 mb-2">
            <Cpu className="w-3.5 h-3.5 text-indigo-400" />
            <span>AI/ML Pipeline V1</span>
          </div>
          <div className="space-y-1.5 text-[11px] text-slate-400">
            <div className="flex justify-between items-center">
              <span>OCR Engine</span>
              <span className="text-emerald-400 font-mono">PP-Structure</span>
            </div>
            <div className="flex justify-between items-center">
              <span>Classifier</span>
              <span className="text-sky-400 font-mono">TF-IDF + LR</span>
            </div>
            <div className="flex justify-between items-center">
              <span>Extraction</span>
              <span className="text-indigo-400 font-mono">Pydantic Grounded</span>
            </div>
          </div>
        </div>
      </div>

      {/* System Health Status Footer */}
      <div className="pt-4 border-t border-white/10">
        <div className="flex items-center justify-between text-xs px-2">
          <div className="flex items-center gap-2 text-slate-300">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
            <span>FastAPI Server</span>
          </div>
          <span className="text-[10px] text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded font-mono">
            8000 OK
          </span>
        </div>
      </div>
    </aside>
  );
}
