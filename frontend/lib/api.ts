/**
 * DocuMind AI - Frontend API Service Client
 */

export interface BoundingBox {
  x0: number;
  y0: number;
  x1: number;
  y1: number;
}

export interface ExtractedField {
  id: string;
  field_name: string;
  field_value: string | null;
  confidence: number;
  page_number: number;
  bounding_box: BoundingBox | null;
  is_verified: boolean;
  validation_status: "valid" | "warning" | "error" | "unverified";
  warning_message: string | null;
}

export interface AuditLogItem {
  id: string;
  field_id: string | null;
  field_name: string;
  old_value: string | null;
  new_value: string | null;
  modified_by: string;
  modified_at: string;
}

export interface DocumentDetail {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  document_type: string;
  status: string;
  confidence_score: number;
  page_count: number;
  uploaded_at: string;
  updated_at: string;
  raw_ocr_text: string | null;
  preview_url: string | null;
  fields: ExtractedField[];
  audit_logs: AuditLogItem[];
  structured_data: any;
}

export interface DocumentSummary {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  document_type: string;
  status: string;
  confidence_score: number;
  page_count: number;
  uploaded_at: string;
  updated_at: string;
}

export interface AnalyticsData {
  total_documents: number;
  successfully_processed: number;
  processing: number;
  needs_review: number;
  document_type_distribution: Record<string, number>;
  status_distribution: Record<string, number>;
  avg_confidence_score: number;
  avg_processing_time_sec: number;
}

const API_BASE = "/api/v1";

export async function getDocuments(status?: string, documentType?: string, search?: string): Promise<DocumentSummary[]> {
  const params = new URLSearchParams();
  if (status && status !== "all") params.append("status", status);
  if (documentType && documentType !== "all") params.append("document_type", documentType);
  if (search) params.append("search", search);

  const res = await fetch(`${API_BASE}/documents?${params.toString()}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch documents");
  return res.json();
}

export async function getDocument(id: string): Promise<DocumentDetail> {
  const res = await fetch(`${API_BASE}/documents/${id}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch document ${id}`);
  return res.json();
}

export async function uploadDocumentFile(file: File, autoProcess = true): Promise<{ document_id: string; message: string }> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/documents/upload?auto_process=${autoProcess}&filename=${encodeURIComponent(file.name)}`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || "Upload failed");
  }
  return res.json();
}

export async function createSample(sampleType: string): Promise<{ document_id: string; sample_type: string }> {
  const res = await fetch(`${API_BASE}/documents/sample/${sampleType}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to create sample document");
  return res.json();
}

export async function updateField(documentId: string, fieldId: string, newValue: string): Promise<any> {
  const res = await fetch(`${API_BASE}/documents/${documentId}/fields/${fieldId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ field_value: newValue, modified_by: "human_reviewer" }),
  });
  if (!res.ok) throw new Error("Failed to update field");
  return res.json();
}

export async function approveDocument(documentId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/documents/${documentId}/approve`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to approve document");
  return res.json();
}

export async function reprocessDocument(documentId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/documents/${documentId}/reprocess`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to reprocess document");
  return res.json();
}

export async function getAnalytics(): Promise<AnalyticsData> {
  const res = await fetch(`${API_BASE}/analytics`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch analytics");
  return res.json();
}
