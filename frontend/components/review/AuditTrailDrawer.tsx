"use client";

import { X, History, User, Clock, ArrowRight } from "lucide-react";
import { AuditLogItem } from "@/lib/api";

interface AuditTrailDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  logs: AuditLogItem[];
}

export default function AuditTrailDrawer({
  isOpen,
  onClose,
  logs,
}: AuditTrailDrawerProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm transition-opacity">
      <div className="w-96 h-full border-l border-white/[0.08] bg-[#090D18]/95 p-5 flex flex-col shadow-2xl">
        <div className="flex items-center justify-between pb-3 border-b border-white/[0.08] mb-4">
          <div className="flex items-center gap-2">
            <History className="w-4 h-4 text-blue-400" />
            <h3 className="text-xs font-semibold text-slate-100">Audit History</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-md text-slate-400 hover:text-white hover:bg-white/[0.08] transition-colors"
            title="Close"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="flex-1 overflow-auto space-y-2.5 custom-scrollbar">
          {logs.length === 0 ? (
            <div className="text-center py-12 text-slate-500 text-xs">
              No manual corrections recorded.
            </div>
          ) : (
            logs.map((log) => (
              <div
                key={log.id}
                className="p-3 rounded-xl border border-white/[0.06] bg-white/[0.02] space-y-2 text-xs"
              >
                <div className="flex items-center justify-between text-[11px] text-slate-400">
                  <span className="font-medium text-slate-300 capitalize">
                    {log.field_name.replace(/_/g, " ")}
                  </span>
                  <div className="flex items-center gap-1 text-[10px] font-mono tabular-nums text-slate-400">
                    <Clock className="w-3 h-3 text-slate-500" />
                    <span>{new Date(log.modified_at).toLocaleTimeString()}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2 p-2 rounded-lg bg-black/40 border border-white/[0.04] font-mono tabular-nums text-xs">
                  <span className="text-rose-400 line-through truncate max-w-[100px]">
                    {log.old_value || "—"}
                  </span>
                  <ArrowRight className="w-3 h-3 text-slate-500 shrink-0" />
                  <span className="text-emerald-400 font-medium truncate max-w-[100px]">
                    {log.new_value}
                  </span>
                </div>

                <div className="flex items-center gap-1.5 text-[10px] text-slate-400">
                  <User className="w-3 h-3 text-slate-500" />
                  <span>Modified by {log.modified_by}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
