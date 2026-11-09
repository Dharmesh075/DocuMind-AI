"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  FileText,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Upload,
  Sparkles,
  ArrowRight,
  Receipt,
  UserCheck,
  FileCheck2,
  Cpu
} from "lucide-react";
import StatsCard from "@/components/dashboard/StatsCard";
import DocumentTable from "@/components/documents/DocumentTable";
import { getDocuments, getAnalytics, createSample, DocumentSummary, AnalyticsData } from "@/lib/api";

export default function DashboardOperationsPage() {
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [creatingSample, setCreatingSample] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [docsData, analyticsData] = await Promise.all([
        getDocuments(),
        getAnalytics(),
      ]);
      setDocuments(docsData);
      setAnalytics(analyticsData);
    } catch (e) {
      console.error("Error loading dashboard data:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateSample = async (type: string) => {
    try {
      setCreatingSample(type);
      await createSample(type);
      await loadData();
    } catch (e) {
      alert("Failed to generate sample: " + e);
    } finally {
      setCreatingSample(null);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Operations Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-white/[0.08]">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-100">
            Document Processing Operations
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time ingestion queue, OCR token layout extraction, and validation health.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/upload"
            className="btn-primary flex items-center gap-2 px-4 py-2 rounded-lg text-xs"
          >
            <Upload className="w-3.5 h-3.5" />
            <span>Upload Document</span>
          </Link>
        </div>
      </div>

      {/* 4 Statistics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Total Documents"
          value={analytics?.total_documents ?? documents.length}
          subtitle="Processed through pipeline"
          icon={FileText}
          variant="indigo"
        />
        <StatsCard
          title="Successfully Processed"
          value={analytics?.successfully_processed ?? 0}
          subtitle="Grounded & schema verified"
          icon={CheckCircle2}
          variant="emerald"
        />
        <StatsCard
          title="In Processing Queue"
          value={analytics?.processing ?? 0}
          subtitle="Background OCR / ML jobs"
          icon={Clock}
          variant="blue"
        />
        <StatsCard
          title="Requires Human Review"
          value={analytics?.needs_review ?? 0}
          subtitle="Flagged by validation engine"
          icon={AlertTriangle}
          variant="amber"
        />
      </div>

      {/* Instant Interactive Sample Pipeline Generators */}
      <div className="p-4 rounded-2xl border border-white/[0.08] bg-[#0E1526]/80 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-blue-400" />
            <h3 className="text-xs font-semibold text-slate-200">
              Benchmark Pipeline Runners
            </h3>
          </div>
          <span className="text-[11px] text-slate-400">
            Run complete 7-stage ML pipeline on verified fixtures
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <button
            onClick={() => handleCreateSample("invoice")}
            disabled={creatingSample !== null}
            className="p-3 rounded-xl bg-white/[0.02] hover:bg-white/[0.06] border border-white/[0.06] hover:border-blue-500/30 transition-all text-left group"
          >
            <div className="flex items-center justify-between mb-1.5">
              <FileText className="w-4 h-4 text-blue-400" />
              <span className="text-[10px] font-mono tabular-nums text-blue-400 group-hover:translate-x-0.5 transition-transform">
                + Run
              </span>
            </div>
            <div className="text-xs font-medium text-slate-200">Commercial Invoice</div>
            <div className="text-[10px] text-slate-400 mt-0.5 font-mono tabular-nums">INV-1024 • ₹11,800.00</div>
          </button>

          <button
            onClick={() => handleCreateSample("receipt")}
            disabled={creatingSample !== null}
            className="p-3 rounded-xl bg-white/[0.02] hover:bg-white/[0.06] border border-white/[0.06] hover:border-amber-500/30 transition-all text-left group"
          >
            <div className="flex items-center justify-between mb-1.5">
              <Receipt className="w-4 h-4 text-amber-400" />
              <span className="text-[10px] font-mono tabular-nums text-amber-400 group-hover:translate-x-0.5 transition-transform">
                + Run
              </span>
            </div>
            <div className="text-xs font-medium text-slate-200">Retail Receipt</div>
            <div className="text-[10px] text-slate-400 mt-0.5 font-mono tabular-nums">Starbucks • $9.98</div>
          </button>

          <button
            onClick={() => handleCreateSample("resume")}
            disabled={creatingSample !== null}
            className="p-3 rounded-xl bg-white/[0.02] hover:bg-white/[0.06] border border-white/[0.06] hover:border-emerald-500/30 transition-all text-left group"
          >
            <div className="flex items-center justify-between mb-1.5">
              <UserCheck className="w-4 h-4 text-emerald-400" />
              <span className="text-[10px] font-mono tabular-nums text-emerald-400 group-hover:translate-x-0.5 transition-transform">
                + Run
              </span>
            </div>
            <div className="text-xs font-medium text-slate-200">Candidate Resume</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Software Engineer</div>
          </button>

          <button
            onClick={() => handleCreateSample("application_form")}
            disabled={creatingSample !== null}
            className="p-3 rounded-xl bg-white/[0.02] hover:bg-white/[0.06] border border-white/[0.06] hover:border-purple-500/30 transition-all text-left group"
          >
            <div className="flex items-center justify-between mb-1.5">
              <FileCheck2 className="w-4 h-4 text-purple-400" />
              <span className="text-[10px] font-mono tabular-nums text-purple-400 group-hover:translate-x-0.5 transition-transform">
                + Run
              </span>
            </div>
            <div className="text-xs font-medium text-slate-200">Application Form</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Govt IDs • Addresses</div>
          </button>
        </div>
      </div>

      {/* Recent Documents Section */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-sm font-semibold text-slate-200">Recent Documents</h2>
            <p className="text-xs text-slate-400">Live processing history and confidence ratings</p>
          </div>
          <Link
            href="/documents"
            className="flex items-center gap-1.5 text-xs font-medium text-blue-400 hover:text-blue-300 transition-colors"
          >
            <span>View All Documents</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <DocumentTable documents={documents} onRefresh={loadData} />
      </div>
    </div>
  );
}
