"use client";

import { useState } from "react";
import {
  CheckCircle2,
  AlertTriangle,
  Edit2,
  Check,
  X,
  Download,
  RotateCw,
  History,
  FileCheck2
} from "lucide-react";
import { ExtractedField, DocumentDetail, updateField, approveDocument, reprocessDocument } from "@/lib/api";

interface ExtractionReviewPanelProps {
  document: DocumentDetail;
  selectedField: string | null;
  onSelectField: (fieldName: string) => void;
  onRefresh: () => void;
  onOpenAuditLog: () => void;
}

export default function ExtractionReviewPanel({
  document,
  selectedField,
  onSelectField,
  onRefresh,
  onOpenAuditLog,
}: ExtractionReviewPanelProps) {
  const [editingFieldId, setEditingFieldId] = useState<string | null>(null);
  const [editValue, setEditValue] = useState<string>("");
  const [isSaving, setIsSaving] = useState(false);
  const [isApproving, setIsApproving] = useState(false);
  const [isReprocessing, setIsReprocessing] = useState(false);
  const [justSavedId, setJustSavedId] = useState<string | null>(null);

  const startEdit = (field: ExtractedField) => {
    setEditingFieldId(field.id);
    setEditValue(field.field_value || "");
  };

  const cancelEdit = () => {
    setEditingFieldId(null);
    setEditValue("");
  };

  const saveEdit = async (field: ExtractedField) => {
    try {
      setIsSaving(true);
      await updateField(document.id, field.id, editValue);
      setEditingFieldId(null);
      setJustSavedId(field.id);
      setTimeout(() => setJustSavedId(null), 2000);
      onRefresh();
    } catch (e) {
      alert("Failed to update field: " + e);
    } finally {
      setIsSaving(false);
    }
  };

  const handleApprove = async () => {
    try {
      setIsApproving(true);
      await approveDocument(document.id);
      onRefresh();
    } catch (e) {
      alert("Failed to approve document: " + e);
    } finally {
      setIsApproving(false);
    }
  };

  const handleReprocess = async () => {
    try {
      setIsReprocessing(true);
      await reprocessDocument(document.id);
      onRefresh();
    } catch (e) {
      alert("Failed to reprocess: " + e);
    } finally {
      setIsReprocessing(false);
    }
  };

  const handleExport = (format: "json" | "csv") => {
    window.open(`/api/v1/documents/${document.id}/export?format=${format}`, "_blank");
  };

  const confPct = Math.round((document.confidence_score || 0) * 100);

  // Outer container: rounded-2xl (16px) with p-4 -> inner cards: rounded-xl (12px) -> buttons: rounded-lg (8px)
  return (
    <div className="flex flex-col h-full rounded-2xl border border-white/[0.08] bg-[#0E1526]/80 overflow-hidden shadow-xl">
      {/* Header Bar */}
      <div className="p-4 border-b border-white/[0.08] bg-white/[0.01]">
        <div className="flex items-center justify-between mb-2.5">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-300">
              {document.document_type.replace("_", " ")}
            </span>
            <span className="text-xs font-mono text-slate-500">•</span>
            <span className="text-xs text-slate-400 font-mono tabular-nums">{document.id}</span>
          </div>

          <div className="flex items-center gap-1.5">
            <span
              className={`text-xs font-semibold tabular-nums px-2 py-0.5 rounded-md ${
                confPct >= 85
                  ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                  : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
              }`}
            >
              {confPct}% confidence
            </span>
          </div>
        </div>

        {/* Status Verification Banner */}
        {document.status === "approved" ? (
          <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>Document verified and approved.</span>
          </div>
        ) : document.status === "needs_review" ? (
          <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs">
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
            <span>Review required: Check highlighted values or arithmetic totals.</span>
          </div>
        ) : (
          <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-300 text-xs">
            <CheckCircle2 className="w-4 h-4 text-blue-400 shrink-0" />
            <span>Extracted with grounded token coordinates.</span>
          </div>
        )}
      </div>

      {/* Field List */}
      <div className="flex-1 overflow-auto p-4 space-y-2 custom-scrollbar">
        <div className="flex items-center justify-between text-xs font-semibold text-slate-300 px-1 mb-2">
          <span>Extracted Fields</span>
          <span className="tabular-nums text-slate-500 text-[11px]">{document.fields.length} detected</span>
        </div>

        {document.fields.map((field) => {
          const isSelected = selectedField === field.field_name;
          const isEditing = editingFieldId === field.id;
          const isJustSaved = justSavedId === field.id;
          const fieldConf = Math.round(field.confidence * 100);

          return (
            <div
              key={field.id}
              onClick={() => onSelectField(field.field_name)}
              className={`p-3 rounded-xl border transition-all duration-150 cursor-pointer ${
                isSelected
                  ? "bg-blue-500/10 border-blue-500/40 shadow-sm"
                  : isJustSaved
                  ? "bg-emerald-500/10 border-emerald-500/30"
                  : "bg-white/[0.02] border-white/[0.06] hover:bg-white/[0.04] hover:border-white/[0.12]"
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-slate-400 capitalize">
                  {field.field_name.replace(/_/g, " ")}
                </span>

                <div className="flex items-center gap-2">
                  <span
                    className={`text-[11px] tabular-nums px-1.5 py-0.5 rounded ${
                      fieldConf >= 90
                        ? "text-emerald-400 bg-emerald-500/10"
                        : fieldConf >= 75
                        ? "text-blue-400 bg-blue-500/10"
                        : "text-amber-400 bg-amber-500/10"
                    }`}
                  >
                    {fieldConf}%
                  </span>

                  {field.is_verified && (
                    <span title="Verified">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    </span>
                  )}
                </div>
              </div>

              {/* Value & Edit Form */}
              {isEditing ? (
                <div className="flex items-center gap-2 mt-1.5" onClick={(e) => e.stopPropagation()}>
                  <input
                    type="text"
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                    className="flex-1 px-2.5 py-1 text-xs glass-input rounded-lg font-medium"
                    autoFocus
                  />
                  <button
                    onClick={() => saveEdit(field)}
                    disabled={isSaving}
                    className="p-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white transition-colors"
                    title="Save"
                  >
                    <Check className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={cancelEdit}
                    className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                    title="Cancel"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
              ) : (
                <div className="flex items-center justify-between mt-0.5">
                  <span
                    className={`text-sm font-semibold tracking-tight ${
                      field.field_value ? "text-slate-100 tabular-nums" : "text-slate-500 font-normal"
                    }`}
                  >
                    {field.field_value || "—"}
                  </span>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      startEdit(field);
                    }}
                    className="p-1 rounded-md text-slate-500 hover:text-slate-200 hover:bg-white/[0.08] transition-colors"
                    title="Edit Field"
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}

              {/* Validation Warning */}
              {field.warning_message && (
                <div className="text-[11px] text-amber-400/90 mt-1 flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3 shrink-0" />
                  <span>{field.warning_message}</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Action Footer Bar */}
      <div className="p-3 border-t border-white/[0.08] bg-white/[0.01] flex items-center justify-between gap-3">
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => handleExport("json")}
            className="px-2.5 py-1.5 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-xs text-slate-300 hover:text-white transition-colors flex items-center gap-1.5"
            title="Export JSON"
          >
            <Download className="w-3.5 h-3.5" />
            <span>JSON</span>
          </button>
          <button
            onClick={() => handleExport("csv")}
            className="px-2.5 py-1.5 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-xs text-slate-300 hover:text-white transition-colors flex items-center gap-1.5"
            title="Export CSV"
          >
            <Download className="w-3.5 h-3.5" />
            <span>CSV</span>
          </button>
          <button
            onClick={onOpenAuditLog}
            className="p-1.5 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-slate-400 hover:text-slate-200 transition-colors"
            title="Audit History"
          >
            <History className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleReprocess}
            disabled={isReprocessing}
            className="p-2 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-slate-400 hover:text-slate-200 transition-colors"
            title="Reprocess Document"
          >
            <RotateCw className={`w-3.5 h-3.5 ${isReprocessing ? "animate-spin text-blue-400" : ""}`} />
          </button>

          {/* Emphasized Primary CTA */}
          <button
            onClick={handleApprove}
            disabled={isApproving || document.status === "approved"}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-semibold transition-all shadow-md ${
              document.status === "approved"
                ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 cursor-default"
                : "bg-emerald-600 hover:bg-emerald-500 text-white active:translate-y-px"
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>{document.status === "approved" ? "Approved" : "Approve Document"}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
