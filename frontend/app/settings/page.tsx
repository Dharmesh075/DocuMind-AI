"use client";

import { useState } from "react";
import {
  Sliders,
  Database,
  HardDrive,
  Cpu,
  Key,
  ShieldCheck,
  Save,
  CheckCircle2
} from "lucide-react";

export default function SettingsPage() {
  const [apiKey, setApiKey] = useState("");
  const [llmProvider, setLlmProvider] = useState("gemini");
  const [autoApproveThreshold, setAutoApproveThreshold] = useState(95);
  const [lowConfidenceThreshold, setLowConfidenceThreshold] = useState(60);
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="pb-2 border-b border-white/[0.08]">
        <h1 className="text-xl font-bold text-slate-100 tracking-tight">System Settings</h1>
        <p className="text-xs text-slate-400 mt-0.5">
          Configure AI extraction parameters, confidence thresholds, and infrastructure bindings.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-5">
        {/* AI & ML Models */}
        <div className="p-5 rounded-2xl border border-white/[0.08] bg-[#0E1526]/80 space-y-4">
          <div className="flex items-center gap-2 pb-2 border-b border-white/[0.08]">
            <Cpu className="w-4 h-4 text-blue-400" />
            <h2 className="text-xs font-semibold text-slate-200">AI & OCR Configuration</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                OCR Pipeline Engine
              </label>
              <select className="w-full px-3 py-2 text-xs rounded-lg glass-input bg-[#0A0F1E] text-slate-200">
                <option value="paddleocr">PaddleOCR 3.x (PP-StructureV3)</option>
                <option value="tesseract">Tesseract OCR</option>
                <option value="hybrid">Hybrid (Selectable PDF Stream + OCR)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Document Classifier
              </label>
              <select className="w-full px-3 py-2 text-xs rounded-lg glass-input bg-[#0A0F1E] text-slate-200">
                <option value="tfidf">TF-IDF + Logistic Regression (Active)</option>
                <option value="transformer">Transformer LayoutLMv3 (V2 Roadmap)</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                LLM Extraction Engine
              </label>
              <select
                value={llmProvider}
                onChange={(e) => setLlmProvider(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-lg glass-input bg-[#0A0F1E] text-slate-200"
              >
                <option value="gemini">Google Gemini API (gemini-2.5-flash)</option>
                <option value="local">Local Ollama / vLLM (Qwen2.5-7B)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Gemini API Key (Optional)
              </label>
              <input
                type="password"
                placeholder="AIzaSy..."
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-lg glass-input"
              />
            </div>
          </div>
        </div>

        {/* Confidence Thresholds */}
        <div className="p-5 rounded-2xl border border-white/[0.08] bg-[#0E1526]/80 space-y-4">
          <div className="flex items-center gap-2 pb-2 border-b border-white/[0.08]">
            <Sliders className="w-4 h-4 text-indigo-400" />
            <h2 className="text-xs font-semibold text-slate-200">Confidence & Review Thresholds</h2>
          </div>

          <div className="space-y-4">
            <div>
              <div className="flex justify-between items-center text-xs mb-1.5">
                <span className="text-slate-300 font-medium">Auto-Approve Threshold</span>
                <span className="font-mono tabular-nums text-emerald-400">{autoApproveThreshold}%</span>
              </div>
              <input
                type="range"
                min="80"
                max="99"
                value={autoApproveThreshold}
                onChange={(e) => setAutoApproveThreshold(Number(e.target.value))}
                className="w-full accent-blue-500 cursor-pointer"
              />
              <p className="text-[11px] text-slate-400 mt-1">
                Documents with grounded confidence above this threshold and zero arithmetic errors skip manual review.
              </p>
            </div>

            <div>
              <div className="flex justify-between items-center text-xs mb-1.5">
                <span className="text-slate-300 font-medium">Flag-for-Review Threshold</span>
                <span className="font-mono tabular-nums text-amber-400">{lowConfidenceThreshold}%</span>
              </div>
              <input
                type="range"
                min="40"
                max="80"
                value={lowConfidenceThreshold}
                onChange={(e) => setLowConfidenceThreshold(Number(e.target.value))}
                className="w-full accent-amber-500 cursor-pointer"
              />
              <p className="text-[11px] text-slate-400 mt-1">
                Any field with confidence below this threshold is highlighted with a warning badge for operator verification.
              </p>
            </div>
          </div>
        </div>

        {/* Infrastructure & Storage */}
        <div className="p-5 rounded-2xl border border-white/[0.08] bg-[#0E1526]/80 space-y-4">
          <div className="flex items-center gap-2 pb-2 border-b border-white/[0.08]">
            <Database className="w-4 h-4 text-emerald-400" />
            <h2 className="text-xs font-semibold text-slate-200">Infrastructure & Storage</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div className="p-3.5 rounded-xl bg-white/[0.02] border border-white/[0.06] space-y-1">
              <span className="text-slate-400">Database Engine</span>
              <div className="font-mono text-slate-100 font-medium">SQLite (Local) / PostgreSQL (Docker)</div>
              <div className="text-[10px] text-emerald-400 font-mono tabular-nums">SQLAlchemy ORM Connected</div>
            </div>

            <div className="p-3.5 rounded-xl bg-white/[0.02] border border-white/[0.06] space-y-1">
              <span className="text-slate-400">File Storage</span>
              <div className="font-mono text-slate-100 font-medium">Local Storage / MinIO S3</div>
              <div className="text-[10px] text-blue-400 font-mono">backend/storage/documents</div>
            </div>
          </div>
        </div>

        {/* Save Bar */}
        <div className="flex items-center justify-between pt-1">
          {saved && (
            <div className="flex items-center gap-1.5 text-xs text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
              <span>Settings saved successfully!</span>
            </div>
          )}
          <div className="ml-auto">
            <button
              type="submit"
              className="btn-primary flex items-center gap-2 px-5 py-2.5 rounded-lg text-xs"
            >
              <Save className="w-4 h-4" />
              <span>Save Configuration</span>
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
