"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  FileText,
  Receipt,
  UserCheck,
  FileCheck2,
  Upload,
  Plus,
  RefreshCw,
  Clock
} from "lucide-react";
import DocumentViewer from "@/components/review/DocumentViewer";
import ExtractionReviewPanel from "@/components/review/ExtractionReviewPanel";
import AuditTrailDrawer from "@/components/review/AuditTrailDrawer";
import { getDocuments, getDocument, DocumentSummary, DocumentDetail } from "@/lib/api";

export default function WorkspacePage() {
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [activeDoc, setActiveDoc] = useState<DocumentDetail | null>(null);
  const [loadingList, setLoadingList] = useState(true);
  const [loadingDoc, setLoadingDoc] = useState(false);
  const [selectedField, setSelectedField] = useState<string | null>(null);
  const [isAuditOpen, setIsAuditOpen] = useState(false);

  // Load document list
  const loadDocuments = async () => {
    try {
      setLoadingList(true);
      const docs = await getDocuments();
      setDocuments(docs);
      if (docs.length > 0 && !selectedDocId) {
        setSelectedDocId(docs[0].id);
      }
    } catch (e) {
      console.error("Failed to load documents:", e);
    } finally {
      setLoadingList(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  // Load selected document details
  const loadActiveDoc = async (id: string) => {
    try {
      setLoadingDoc(true);
      const detail = await getDocument(id);
      setActiveDoc(detail);
      setSelectedField(null);
    } catch (e) {
      console.error("Failed to load active document:", e);
    } finally {
      setLoadingDoc(false);
    }
  };

  useEffect(() => {
    if (selectedDocId) {
      loadActiveDoc(selectedDocId);
    }
  }, [selectedDocId]);

  const getDocIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case "invoice":
        return <FileText className="w-3.5 h-3.5 text-blue-400 shrink-0" />;
      case "receipt":
        return <Receipt className="w-3.5 h-3.5 text-amber-400 shrink-0" />;
      case "resume":
        return <UserCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />;
      default:
        return <FileCheck2 className="w-3.5 h-3.5 text-purple-400 shrink-0" />;
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-6.5rem)] space-y-4">
      {/* Top Document Switcher Bar */}
      <div className="flex items-center justify-between gap-4 pb-2 border-b border-white/[0.08]">
        {/* Document Tabs */}
        <div className="flex items-center gap-2 overflow-x-auto custom-scrollbar pb-1">
          {loadingList ? (
            <div className="flex items-center gap-2 text-xs text-slate-500 py-1">
              <Clock className="w-3.5 h-3.5 animate-spin" />
              <span>Loading documents...</span>
            </div>
          ) : (
            documents.map((doc) => {
              const isSelected = selectedDocId === doc.id;
              const confPct = Math.round((doc.confidence_score || 0) * 100);
              return (
                <button
                  key={doc.id}
                  onClick={() => setSelectedDocId(doc.id)}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs transition-colors whitespace-nowrap ${
                    isSelected
                      ? "bg-white/[0.08] text-white border border-white/[0.12]"
                      : "text-slate-400 hover:text-slate-200 hover:bg-white/[0.04] border border-transparent"
                  }`}
                >
                  {getDocIcon(doc.document_type)}
                  <span className="font-medium max-w-[140px] truncate">{doc.filename}</span>
                  <span className="text-[10px] tabular-nums font-mono opacity-70">
                    {confPct}%
                  </span>
                </button>
              );
            })
          )}
        </div>

        {/* Top Actions */}
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={loadDocuments}
            disabled={loadingList}
            className="p-1.5 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] text-slate-400 hover:text-slate-200 transition-colors"
            title="Refresh documents"
            aria-label="Refresh documents"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loadingList ? "animate-spin text-blue-400" : ""}`} />
          </button>

          <Link
            href="/upload"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] text-xs font-medium text-slate-300 hover:text-white border border-white/[0.08] transition-colors"
          >
            <Plus className="w-3.5 h-3.5 text-blue-400" />
            <span>Upload</span>
          </Link>
        </div>
      </div>

      {/* Main Split-Screen Workspace (The enlarged product feature) */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-5 min-h-0 overflow-hidden">
        {loadingDoc || !activeDoc ? (
          <div className="lg:col-span-12 flex flex-col items-center justify-center h-full rounded-2xl border border-white/[0.08] bg-[#0E1526]/50 text-slate-400">
            <Clock className="w-6 h-6 text-blue-400 animate-spin mb-2" />
            <span className="text-xs">Loading document workspace...</span>
          </div>
        ) : (
          <>
            {/* Left: Document Canvas (7 cols = ~58% width) */}
            <div className="lg:col-span-7 h-full min-h-0">
              <DocumentViewer
                previewUrl={activeDoc.preview_url}
                filename={activeDoc.filename}
                fields={activeDoc.fields}
                selectedField={selectedField}
                onSelectField={(f) => setSelectedField(f)}
              />
            </div>

            {/* Right: Extracted Data Inspector (5 cols = ~42% width) */}
            <div className="lg:col-span-5 h-full min-h-0">
              <ExtractionReviewPanel
                document={activeDoc}
                selectedField={selectedField}
                onSelectField={(f) => setSelectedField(f)}
                onRefresh={() => loadActiveDoc(activeDoc.id)}
                onOpenAuditLog={() => setIsAuditOpen(true)}
              />
            </div>
          </>
        )}
      </div>

      {/* Audit Drawer */}
      {activeDoc && (
        <AuditTrailDrawer
          isOpen={isAuditOpen}
          onClose={() => setIsAuditOpen(false)}
          logs={activeDoc.audit_logs}
        />
      )}
    </div>
  );
}
