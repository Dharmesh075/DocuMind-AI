"use client";

import { useEffect, useState } from "react";
import { Search, Filter, RefreshCw, FileText, Upload } from "lucide-react";
import Link from "next/link";
import DocumentTable from "@/components/documents/DocumentTable";
import { getDocuments, DocumentSummary } from "@/lib/api";

const TYPE_FILTERS = [
  { id: "all", label: "All Types" },
  { id: "invoice", label: "Invoices" },
  { id: "receipt", label: "Receipts" },
  { id: "resume", label: "Resumes" },
  { id: "application_form", label: "Application Forms" },
];

const STATUS_FILTERS = [
  { id: "all", label: "All Statuses" },
  { id: "needs_review", label: "Needs Review" },
  { id: "extracted", label: "Extracted" },
  { id: "approved", label: "Approved" },
];

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedType, setSelectedType] = useState("all");
  const [selectedStatus, setSelectedStatus] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");

  const fetchDocs = async () => {
    try {
      setLoading(true);
      const data = await getDocuments(selectedStatus, selectedType, searchQuery);
      setDocuments(data);
    } catch (e) {
      console.error("Error loading documents:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, [selectedType, selectedStatus]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchDocs();
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-white/[0.08]">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight">Document Repository</h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Manage, inspect, and review processed documents and classification runs.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchDocs}
            disabled={loading}
            className="p-2 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-slate-400 hover:text-white transition-colors"
            title="Refresh list"
            aria-label="Refresh list"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-blue-400" : ""}`} />
          </button>

          <Link
            href="/upload"
            className="btn-primary flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs"
          >
            <Upload className="w-3.5 h-3.5" />
            <span>Upload Document</span>
          </Link>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="p-3.5 rounded-2xl border border-white/[0.08] bg-[#0E1526]/80 flex flex-col md:flex-row items-center justify-between gap-3">
        {/* Type Filter Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto w-full md:w-auto custom-scrollbar pb-1 md:pb-0">
          {TYPE_FILTERS.map((t) => (
            <button
              key={t.id}
              onClick={() => setSelectedType(t.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
                selectedType === t.id
                  ? "bg-white/[0.1] text-white border border-white/[0.15]"
                  : "text-slate-400 hover:text-white hover:bg-white/[0.04] border border-transparent"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* Status Dropdown & Search Form */}
        <div className="flex items-center gap-2.5 w-full md:w-auto">
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-3 py-1.5 text-xs rounded-lg glass-input bg-[#0A0F1E] text-slate-300"
          >
            {STATUS_FILTERS.map((s) => (
              <option key={s.id} value={s.id} className="bg-[#0A0F1E]">
                {s.label}
              </option>
            ))}
          </select>

          <form onSubmit={handleSearch} className="relative flex-1 md:w-60">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by filename or ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 text-xs rounded-lg glass-input text-slate-200"
            />
          </form>
        </div>
      </div>

      {/* Table */}
      <DocumentTable documents={documents} onRefresh={fetchDocs} />
    </div>
  );
}
