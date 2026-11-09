"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  UploadCloud,
  FileText,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  FileCheck2,
  Receipt,
  UserCheck
} from "lucide-react";
import { uploadDocumentFile, createSample } from "@/lib/api";

export default function UploadPage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelected(e.target.files[0]);
    }
  };

  const handleFileSelected = (file: File) => {
    const ext = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();
    const validExts = [".pdf", ".png", ".jpg", ".jpeg"];
    if (!validExts.includes(ext)) {
      setErrorMessage("Unsupported file format. Please upload PDF, PNG, JPG, or JPEG.");
      return;
    }
    setErrorMessage(null);
    setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    try {
      setIsUploading(true);
      const res = await uploadDocumentFile(selectedFile, true);
      router.push(`/review/${res.document_id}`);
    } catch (err: any) {
      setErrorMessage(err.message || "Upload failed");
      setIsUploading(false);
    }
  };

  const handleQuickSample = async (type: string) => {
    try {
      setIsUploading(true);
      const res = await createSample(type);
      router.push(`/review/${res.document_id}`);
    } catch (e: any) {
      setErrorMessage("Failed to process sample: " + e.message);
      setIsUploading(false);
    }
  };

  // Outer container: rounded-2xl (16px) with p-6 -> inner elements: rounded-xl (12px)
  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Specific Headline */}
      <div>
        <h1 className="text-xl font-bold text-slate-100 tracking-tight">Upload Document</h1>
        <p className="text-xs text-slate-400 mt-0.5">
          Ingest a document for OCR extraction, ML classification, and arithmetic verification.
        </p>
      </div>

      {/* Drag & Drop Zone */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`glass-panel p-8 text-center rounded-2xl border-2 border-dashed transition-all ${
          dragActive
            ? "border-blue-500 bg-blue-500/10"
            : "border-white/[0.12] hover:border-white/[0.25]"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.png,.jpg,.jpeg"
          onChange={handleFileChange}
          className="hidden"
        />

        <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center mx-auto mb-3">
          <UploadCloud className="w-6 h-6 text-blue-400" />
        </div>

        <h3 className="text-sm font-semibold text-slate-100 mb-1">
          Drag and drop your document here, or{" "}
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="text-blue-400 hover:text-blue-300 underline underline-offset-4"
          >
            browse
          </button>
        </h3>
        <p className="text-xs text-slate-400 mb-5">
          PDF, PNG, JPG up to 25MB
        </p>

        {/* Selected File Card */}
        {selectedFile && (
          <div className="max-w-md mx-auto p-3 rounded-xl bg-white/[0.04] border border-white/[0.08] flex items-center justify-between text-left mb-5">
            <div className="flex items-center gap-2.5 truncate">
              <FileText className="w-4 h-4 text-blue-400 shrink-0" />
              <div className="truncate">
                <div className="text-xs font-medium text-slate-100 truncate">{selectedFile.name}</div>
                <div className="text-[10px] text-slate-400 font-mono tabular-nums">
                  {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                </div>
              </div>
            </div>

            <button
              onClick={() => setSelectedFile(null)}
              className="text-xs text-slate-400 hover:text-rose-400 transition-colors ml-3"
            >
              Remove
            </button>
          </div>
        )}

        {/* Upload Button */}
        {selectedFile && (
          <button
            onClick={handleUpload}
            disabled={isUploading}
            className="btn-primary px-6 py-2 rounded-lg text-xs"
          >
            {isUploading ? "Processing..." : "Process Document"}
          </button>
        )}

        {/* Error Alert */}
        {errorMessage && (
          <div className="max-w-md mx-auto mt-4 p-2.5 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center gap-2 justify-center">
            <AlertCircle className="w-3.5 h-3.5 text-rose-400 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}
      </div>

      {/* Quick Test Samples */}
      <div className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          Or Test with Grounded Benchmark Samples
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
          <button
            onClick={() => handleQuickSample("invoice")}
            disabled={isUploading}
            className="p-3.5 rounded-xl glass-card text-left group"
          >
            <FileText className="w-4 h-4 text-blue-400 mb-1.5" />
            <div className="text-xs font-medium text-slate-100">Invoice</div>
            <div className="text-[11px] text-slate-400 mt-0.5">INV-1024 • ₹11,800.00</div>
          </button>

          <button
            onClick={() => handleQuickSample("receipt")}
            disabled={isUploading}
            className="p-3.5 rounded-xl glass-card text-left group"
          >
            <Receipt className="w-4 h-4 text-amber-400 mb-1.5" />
            <div className="text-xs font-medium text-slate-100">Receipt</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Starbucks • $9.98</div>
          </button>

          <button
            onClick={() => handleQuickSample("resume")}
            disabled={isUploading}
            className="p-3.5 rounded-xl glass-card text-left group"
          >
            <UserCheck className="w-4 h-4 text-emerald-400 mb-1.5" />
            <div className="text-xs font-medium text-slate-100">Resume</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Engineer • Skills</div>
          </button>

          <button
            onClick={() => handleQuickSample("application_form")}
            disabled={isUploading}
            className="p-3.5 rounded-xl glass-card text-left group"
          >
            <FileCheck2 className="w-4 h-4 text-purple-400 mb-1.5" />
            <div className="text-xs font-medium text-slate-100">Application Form</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Identity • Address</div>
          </button>
        </div>
      </div>
    </div>
  );
}
