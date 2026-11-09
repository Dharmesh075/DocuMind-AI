"use client";

import { useState } from "react";
import { ZoomIn, ZoomOut, RotateCcw, FileText } from "lucide-react";
import { ExtractedField } from "@/lib/api";

interface DocumentViewerProps {
  previewUrl: string | null;
  filename: string;
  fields: ExtractedField[];
  selectedField: string | null;
  onSelectField: (fieldName: string) => void;
}

export default function DocumentViewer({
  previewUrl,
  filename,
  fields,
  selectedField,
  onSelectField,
}: DocumentViewerProps) {
  const [zoom, setZoom] = useState<number>(100);

  const handleZoomIn = () => setZoom((z) => Math.min(175, z + 15));
  const handleZoomOut = () => setZoom((z) => Math.max(70, z - 15));
  const handleResetZoom = () => setZoom(100);

  // Outer container: rounded-2xl (16px), toolbar p-3 (12px) -> buttons: rounded-lg (8px = 16px - 8px / 12px)
  return (
    <div className="flex flex-col h-full rounded-2xl border border-white/[0.08] bg-[#0E1526]/80 overflow-hidden shadow-xl">
      {/* Viewer Toolbar */}
      <div className="h-12 border-b border-white/[0.08] px-4 flex items-center justify-between bg-white/[0.02]">
        <div className="flex items-center gap-2 text-xs font-medium text-slate-200">
          <FileText className="w-4 h-4 text-blue-400 shrink-0" />
          <span className="truncate max-w-[280px]">{filename}</span>
        </div>

        {/* Zoom Controls */}
        <div className="flex items-center gap-1 bg-white/[0.04] border border-white/[0.08] rounded-lg p-1">
          <button
            onClick={handleZoomOut}
            className="p-1 rounded-md hover:bg-white/[0.08] text-slate-400 hover:text-slate-100 transition-colors"
            title="Zoom Out"
            aria-label="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <span className="text-xs tabular-nums text-slate-300 px-1.5 min-w-[38px] text-center">
            {zoom}%
          </span>
          <button
            onClick={handleZoomIn}
            className="p-1 rounded-md hover:bg-white/[0.08] text-slate-400 hover:text-slate-100 transition-colors"
            title="Zoom In"
            aria-label="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <div className="w-[1px] h-3.5 bg-white/[0.08] mx-0.5" />
          <button
            onClick={handleResetZoom}
            className="p-1 rounded-md hover:bg-white/[0.08] text-slate-400 hover:text-slate-100 transition-colors"
            title="Reset Zoom"
            aria-label="Reset Zoom"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Canvas Area */}
      <div className="flex-1 overflow-auto p-6 flex justify-center items-start bg-[#080C16] custom-scrollbar">
        <div
          className="relative transition-transform duration-150 ease-out shadow-2xl rounded-lg overflow-hidden border border-white/[0.1] bg-white select-none"
          style={{
            transform: `scale(${zoom / 100})`,
            transformOrigin: "top center",
          }}
        >
          {previewUrl ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={previewUrl}
              alt="Original Document Preview"
              className="max-w-[760px] w-auto h-auto block pointer-events-none"
            />
          ) : (
            <div className="w-[620px] h-[820px] bg-slate-900 flex flex-col items-center justify-center text-slate-400">
              <FileText className="w-10 h-10 text-slate-600 mb-2" />
              <span className="text-xs">Rendering preview image...</span>
            </div>
          )}

          {/* Interactive Coordinate Bounding Boxes */}
          {fields.map((f) => {
            if (!f.bounding_box) return null;
            const bbox = f.bounding_box;
            const isSelected = selectedField === f.field_name;

            const topPct = bbox.y0 * 100;
            const leftPct = bbox.x0 * 100;
            const widthPct = Math.max(3, (bbox.x1 - bbox.x0) * 100);
            const heightPct = Math.max(2, (bbox.y1 - bbox.y0) * 100);

            return (
              <div
                key={f.id}
                onClick={() => onSelectField(f.field_name)}
                className={`absolute cursor-pointer transition-all duration-150 ${
                  isSelected
                    ? "border-2 border-blue-400 bg-blue-500/25 ring-2 ring-blue-400/30 z-20"
                    : "border border-blue-400/40 bg-blue-500/10 hover:border-blue-400 hover:bg-blue-500/20 z-10"
                } rounded`}
                style={{
                  top: `${topPct}%`,
                  left: `${leftPct}%`,
                  width: `${widthPct}%`,
                  height: `${heightPct}%`,
                }}
              >
                {isSelected && (
                  <div className="absolute -top-5 left-0 px-1.5 py-0.5 rounded bg-blue-600 text-white text-[10px] font-medium tracking-tight shadow-md whitespace-nowrap">
                    {f.field_name.replace(/_/g, " ")} <span className="tabular-nums font-mono opacity-80">({Math.round(f.confidence * 100)}%)</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
