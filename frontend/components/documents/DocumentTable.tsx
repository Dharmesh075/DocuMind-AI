"use client";

import Link from "next/link";
import { DocumentSummary } from "@/lib/api";
import {
  FileText,
  Clock,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Receipt,
  FileCheck2,
  UserCheck
} from "lucide-react";

interface DocumentTableProps {
  documents: DocumentSummary[];
  onRefresh?: () => void;
}

export default function DocumentTable({ documents }: DocumentTableProps) {
  if (documents.length === 0) {
    return (
      <div className="p-12 text-center text-slate-400 glass-panel rounded-2xl">
        <FileText className="w-8 h-8 mx-auto text-slate-600 mb-2" />
        <div className="text-xs font-medium text-slate-300">No documents in repository</div>
        <div className="text-[11px] text-slate-500 mt-1">Upload a document to begin processing.</div>
      </div>
    );
  }

  const getTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case "invoice":
        return <FileText className="w-3.5 h-3.5 text-blue-400" />;
      case "receipt":
        return <Receipt className="w-3.5 h-3.5 text-amber-400" />;
      case "resume":
        return <UserCheck className="w-3.5 h-3.5 text-emerald-400" />;
      default:
        return <FileCheck2 className="w-3.5 h-3.5 text-purple-400" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case "approved":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3 h-3" /> Approved
          </span>
        );
      case "extracted":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <CheckCircle2 className="w-3 h-3" /> Extracted
          </span>
        );
      case "needs_review":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <AlertTriangle className="w-3 h-3" /> Needs Review
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-medium bg-slate-500/10 text-slate-400 border border-slate-500/20">
            <Clock className="w-3 h-3" /> {status}
          </span>
        );
    }
  };

  return (
    <div className="overflow-x-auto rounded-2xl border border-white/[0.08] bg-[#0E1526]/80 backdrop-blur-md">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-white/[0.08] bg-white/[0.01] text-[11px] uppercase tracking-wider text-slate-400 font-medium">
            <th className="py-3 px-4">Document</th>
            <th className="py-3 px-4">Type</th>
            <th className="py-3 px-4">Status</th>
            <th className="py-3 px-4">Confidence</th>
            <th className="py-3 px-4">Uploaded</th>
            <th className="py-3 px-4 text-right">Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/[0.04] text-xs text-slate-300">
          {documents.map((doc) => {
            const confPct = Math.round((doc.confidence_score || 0) * 100);
            return (
              <tr key={doc.id} className="hover:bg-white/[0.02] transition-colors group">
                <td className="py-3 px-4">
                  <div className="font-medium text-slate-100 flex items-center gap-2">
                    <FileText className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                    <span className="truncate max-w-[220px]">{doc.filename}</span>
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono tabular-nums mt-0.5">{doc.id}</div>
                </td>

                <td className="py-3 px-4">
                  <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-white/[0.04] text-[11px] capitalize text-slate-200">
                    {getTypeIcon(doc.document_type)}
                    {doc.document_type.replace("_", " ")}
                  </span>
                </td>

                <td className="py-3 px-4">{getStatusBadge(doc.status)}</td>

                <td className="py-3 px-4">
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          confPct >= 90
                            ? "bg-emerald-400"
                            : confPct >= 75
                            ? "bg-blue-400"
                            : "bg-amber-400"
                        }`}
                        style={{ width: `${confPct}%` }}
                      />
                    </div>
                    <span className="text-[11px] font-mono tabular-nums text-slate-400">{confPct}%</span>
                  </div>
                </td>

                <td className="py-3 px-4 text-slate-400 text-[11px] font-mono tabular-nums">
                  {new Date(doc.uploaded_at).toLocaleDateString()}
                </td>

                <td className="py-3 px-4 text-right">
                  <Link
                    href={`/review/${doc.id}`}
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-slate-300 hover:text-white transition-colors text-xs font-medium"
                  >
                    <span>Open</span>
                    <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                  </Link>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
