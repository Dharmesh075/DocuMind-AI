"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  ChevronLeft,
  FileText,
  Clock,
  Sparkles,
  Download,
  AlertCircle
} from "lucide-react";
import DocumentViewer from "@/components/review/DocumentViewer";
import ExtractionReviewPanel from "@/components/review/ExtractionReviewPanel";
import AuditTrailDrawer from "@/components/review/AuditTrailDrawer";
import { getDocument, DocumentDetail } from "@/lib/api";

export default function DocumentReviewPage() {
  const params = useParams();
  const router = useRouter();
  const documentId = params.id as string;

  const [document, setDocument] = useState<DocumentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedField, setSelectedField] = useState<string | null>(null);
  const [isAuditOpen, setIsAuditOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDoc = async () => {
    try {
      setLoading(true);
      const data = await getDocument(documentId);
      setDocument(data);
    } catch (e: any) {
      setError(e.message || "Failed to load document");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (documentId) {
      fetchDoc();
    }
  }, [documentId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-slate-400 space-y-2.5">
        <Clock className="w-6 h-6 text-blue-400 animate-spin" />
        <span className="text-xs">Loading review workspace...</span>
      </div>
    );
  }

  if (error || !document) {
    return (
      <div className="max-w-md mx-auto text-center p-8 rounded-2xl border border-white/[0.08] bg-[#0E1526]/80 space-y-4 my-12">
        <AlertCircle className="w-8 h-8 text-rose-400 mx-auto" />
        <div className="text-sm font-semibold text-slate-100">Document Not Found</div>
        <div className="text-xs text-slate-400">{error || "The requested document could not be retrieved."}</div>
        <Link
          href="/documents"
          className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-xs text-slate-200 transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
          <span>Back to Documents</span>
        </Link>
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-6.5rem)] flex flex-col space-y-4 max-w-[1700px] mx-auto">
      {/* Top Breadcrumb & Metadata Bar */}
      <div className="flex items-center justify-between pb-2 border-b border-white/[0.08]">
        <div className="flex items-center gap-3">
          <Link
            href="/documents"
            className="p-1.5 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-slate-400 hover:text-white transition-colors"
            title="Back to Documents"
          >
            <ChevronLeft className="w-4 h-4" />
          </Link>

          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-semibold text-slate-100 tracking-tight">{document.filename}</h1>
              <span className="text-[11px] font-mono tabular-nums px-2 py-0.5 rounded-md bg-white/[0.04] text-slate-400 border border-white/[0.08]">
                {document.id}
              </span>
            </div>
            <div className="text-[11px] text-slate-400 flex items-center gap-2 mt-0.5 font-mono tabular-nums">
              <span>Uploaded {new Date(document.uploaded_at).toLocaleString()}</span>
              <span>•</span>
              <span>{document.page_count} {document.page_count === 1 ? "page" : "pages"}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsAuditOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-xs text-slate-300 hover:text-white transition-colors"
          >
            <span>Audit History</span>
            <span className="font-mono tabular-nums opacity-75">({document.audit_logs.length})</span>
          </button>
        </div>
      </div>

      {/* Split-Screen Review Workspace */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-5 min-h-0 overflow-hidden">
        {/* Left Panel: Document Preview & Interactive Bounding Boxes */}
        <div className="lg:col-span-7 h-full min-h-0">
          <DocumentViewer
            previewUrl={document.preview_url}
            filename={document.filename}
            fields={document.fields}
            selectedField={selectedField}
            onSelectField={(f) => setSelectedField(f)}
          />
        </div>

        {/* Right Panel: Extracted Data & Human-in-the-Loop */}
        <div className="lg:col-span-5 h-full min-h-0">
          <ExtractionReviewPanel
            document={document}
            selectedField={selectedField}
            onSelectField={(f) => setSelectedField(f)}
            onRefresh={fetchDoc}
            onOpenAuditLog={() => setIsAuditOpen(true)}
          />
        </div>
      </div>

      {/* Audit Trail Drawer */}
      <AuditTrailDrawer
        isOpen={isAuditOpen}
        onClose={() => setIsAuditOpen(false)}
        logs={document.audit_logs}
      />
    </div>
  );
}
