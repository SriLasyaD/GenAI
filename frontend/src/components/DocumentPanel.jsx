import React, { useState, useRef } from 'react';
import { 
  FileText, 
  UploadCloud, 
  Loader2, 
  Trash2, 
  FileCheck2, 
  Sparkles, 
  Layers, 
  AlertCircle,
  FileSpreadsheet,
  BarChart3,
  Calendar,
  GraduationCap,
  Hash
} from 'lucide-react';

export default function DocumentPanel({
  documents,
  stats = {},
  isUploading,
  uploadProgress,
  onUploadFiles,
  onLoadSample,
  onDeleteDocument,
}) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onUploadFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      onUploadFiles(Array.from(e.target.files));
      e.target.value = '';
    }
  };

  return (
    <aside className="w-full lg:w-80 flex-shrink-0 flex flex-col h-full border-r border-white/10 bg-[#0d1322]/80 backdrop-blur-md p-4 space-y-4">
      {/* Panel Header */}
      <div className="flex items-center justify-between pb-2 border-b border-white/5">
        <div className="flex items-center gap-2 text-white font-semibold text-sm">
          <Layers className="w-4 h-4 text-indigo-400" />
          <span>Curriculum Documents</span>
        </div>
        <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-white/5">
          {documents.length} {documents.length === 1 ? 'doc' : 'docs'}
        </span>
      </div>

      {/* Drag & Drop Upload Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`group relative border-2 border-dashed rounded-xl p-4 text-center cursor-pointer transition-all ${
          isDragging 
            ? 'border-indigo-500 bg-indigo-500/10' 
            : 'border-slate-700/80 hover:border-indigo-400/60 bg-slate-900/40 hover:bg-slate-900/80'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          multiple
          onChange={handleFileChange}
          className="hidden"
        />

        <div className="flex flex-col items-center justify-center space-y-2">
          <div className="w-10 h-10 rounded-full bg-indigo-500/10 group-hover:bg-indigo-500/20 text-indigo-400 flex items-center justify-center transition-colors">
            {isUploading ? (
              <Loader2 className="w-5 h-5 animate-spin text-indigo-400" />
            ) : (
              <UploadCloud className="w-5 h-5 group-hover:scale-110 transition-transform" />
            )}
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-200">
              {isUploading ? 'Extracting & Indexing...' : 'Upload Curriculum PDF'}
            </p>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Drag & drop or click to browse
            </p>
          </div>
        </div>

        {uploadProgress && (
          <div className="mt-2 text-[10px] text-indigo-300 font-mono bg-indigo-950/60 px-2 py-1 rounded">
            {uploadProgress}
          </div>
        )}
      </div>

      {/* Instant Sample Curriculum Button */}
      <div className="bg-gradient-to-r from-indigo-950/40 via-purple-950/30 to-slate-900/40 border border-indigo-500/20 rounded-xl p-3">
        <div className="flex items-start justify-between">
          <div>
            <span className="inline-flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wider text-teal-400">
              <Sparkles className="w-3 h-3" /> Quick Start
            </span>
            <h2 className="text-xs font-semibold text-white mt-0.5">B.Tech CSE Curriculum</h2>
            <p className="text-[11px] text-slate-400 mt-0.5">
              8 Semesters, CS301, Credits, Prerequisites
            </p>
          </div>
        </div>
        <button
          onClick={onLoadSample}
          disabled={isUploading}
          className="mt-2.5 w-full flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-lg text-xs font-medium bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/20 transition-all disabled:opacity-50 cursor-pointer"
        >
          <FileSpreadsheet className="w-3.5 h-3.5" />
          <span>Load Sample Curriculum</span>
        </button>
      </div>

      {/* Curriculum Statistics Card (Calculated purely from uploaded data) */}
      {stats.total_documents > 0 && (
        <div className="p-3.5 rounded-xl bg-slate-900/70 border border-teal-500/20 shadow-md space-y-2.5">
          <div className="flex items-center justify-between pb-1.5 border-b border-white/5">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-teal-300">
              <BarChart3 className="w-4 h-4 text-teal-400" />
              <span>Curriculum Statistics</span>
            </div>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-teal-500/10 text-teal-300 border border-teal-500/20">
              Live Data
            </span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="p-2 rounded-lg bg-slate-800/60 border border-white/5">
              <span className="text-[10px] text-slate-400 block">Documents</span>
              <span className="text-sm font-bold text-white">{stats.total_documents}</span>
            </div>
            <div className="p-2 rounded-lg bg-slate-800/60 border border-white/5">
              <span className="text-[10px] text-slate-400 block">Pages</span>
              <span className="text-sm font-bold text-teal-300">{stats.total_pages || 0}</span>
            </div>
            <div className="p-2 rounded-lg bg-slate-800/60 border border-white/5">
              <span className="text-[10px] text-slate-400 block">Chunks</span>
              <span className="text-sm font-bold text-indigo-300">{stats.total_chunks}</span>
            </div>
            <div className="p-2 rounded-lg bg-slate-800/60 border border-white/5">
              <span className="text-[10px] text-slate-400 block">Courses</span>
              <span className="text-sm font-bold text-purple-300">{stats.courses_count || (stats.courses_detected?.length || 0)}</span>
            </div>
          </div>

          {/* Semesters Detected List */}
          {stats.semesters_detected && stats.semesters_detected.length > 0 && (
            <div className="pt-1">
              <div className="flex items-center justify-between text-[11px] mb-1">
                <span className="text-slate-400 flex items-center gap-1">
                  <Calendar className="w-3 h-3 text-indigo-400" /> Semesters Detected:
                </span>
                <span className="text-xs font-mono font-semibold text-indigo-300">
                  {stats.semesters_detected.length} total
                </span>
              </div>
              <div className="flex flex-wrap gap-1">
                {stats.semesters_detected.map((sem) => (
                  <span
                    key={sem}
                    className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-indigo-500/15 text-indigo-200 border border-indigo-500/20"
                  >
                    Sem {sem}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Course Codes Preview */}
          {stats.courses_detected && stats.courses_detected.length > 0 && (
            <div className="pt-1">
              <div className="flex items-center justify-between text-[11px] mb-1">
                <span className="text-slate-400 flex items-center gap-1">
                  <GraduationCap className="w-3 h-3 text-purple-400" /> Courses Sample:
                </span>
                <span className="text-[10px] text-slate-500 font-mono">
                  {stats.courses_detected.length} codes
                </span>
              </div>
              <div className="flex flex-wrap gap-1 max-h-16 overflow-y-auto pr-0.5">
                {stats.courses_detected.slice(0, 10).map((c) => (
                  <span
                    key={c}
                    className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-purple-500/15 text-purple-200 border border-purple-500/20"
                  >
                    {c}
                  </span>
                ))}
                {stats.courses_detected.length > 10 && (
                  <span className="text-[10px] text-slate-500 px-1 py-0.5">
                    +{stats.courses_detected.length - 10} more
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Uploaded Documents List */}
      <div className="flex-1 overflow-y-auto space-y-2 pr-1">
        <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider px-1">
          Indexed Documents
        </p>

        {documents.length === 0 ? (
          <div className="text-center py-8 px-4 rounded-xl border border-dashed border-slate-800 bg-slate-900/20">
            <AlertCircle className="w-8 h-8 text-slate-600 mx-auto mb-2" />
            <p className="text-xs font-medium text-slate-300">No documents yet</p>
            <p className="text-[11px] text-slate-500 mt-1">
              Upload university syllabi or click "Load Sample" to begin asking questions.
            </p>
          </div>
        ) : (
          documents.map((doc) => (
            <div
              key={doc.doc_id}
              className="p-3 rounded-xl bg-slate-800/40 hover:bg-slate-800/70 border border-white/5 hover:border-indigo-500/30 transition-all group"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-start gap-2.5 min-w-0">
                  <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 flex-shrink-0 mt-0.5">
                    <FileText className="w-4 h-4" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs font-medium text-slate-200 truncate" title={doc.filename}>
                      {doc.filename}
                    </p>
                    <div className="flex items-center gap-2 mt-1 text-[10px] text-slate-400">
                      <span>{doc.total_pages} {doc.total_pages === 1 ? 'page' : 'pages'}</span>
                      <span>•</span>
                      <span className="text-indigo-300 font-mono">{doc.chunks_count} chunks</span>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => onDeleteDocument(doc.doc_id)}
                  className="p-1 rounded text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors opacity-0 group-hover:opacity-100 cursor-pointer"
                  title="Remove Document"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* Ingestion status bar */}
              <div className="mt-2 pt-2 border-t border-white/5 flex items-center justify-between text-[10px]">
                <div className="flex items-center gap-1.5 text-emerald-400">
                  <FileCheck2 className="w-3 h-3" />
                  <span>{doc.status || 'Indexed in FAISS'}</span>
                </div>
                {doc.ingestion_metrics?.total_sec && (
                  <span className="text-slate-500 font-mono">
                    {doc.ingestion_metrics.total_sec}s
                  </span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </aside>
  );
}
