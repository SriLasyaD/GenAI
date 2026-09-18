import React, { useState } from 'react';
import { 
  HelpCircle, 
  ChevronDown, 
  ChevronUp, 
  FileText, 
  Filter, 
  CheckCircle2, 
  TrendingUp,
  BookOpen,
  Info
} from 'lucide-react';

export default function WhyThisAnswer({ 
  retrievedChunks = [], 
  detectedFilters = {}, 
  sources = [] 
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [expandedChunkId, setExpandedChunkId] = useState(null);

  if (!retrievedChunks || retrievedChunks.length === 0) {
    return null;
  }

  const hasFilters = Object.keys(detectedFilters).length > 0;

  return (
    <div className="pt-2 border-t border-white/5 mt-2">
      {/* Accordion Toggle Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 text-xs font-semibold text-teal-400 hover:text-teal-300 transition-colors py-1 px-2 rounded-lg bg-teal-950/30 hover:bg-teal-950/50 border border-teal-500/30 cursor-pointer group"
      >
        <HelpCircle className="w-3.5 h-3.5 text-teal-400 group-hover:scale-110 transition-transform" />
        <span>Why this answer?</span>
        <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-teal-500/20 text-teal-300">
          {retrievedChunks.length} chunks analyzed
        </span>
        {isOpen ? (
          <ChevronUp className="w-3.5 h-3.5 text-teal-400 ml-auto" />
        ) : (
          <ChevronDown className="w-3.5 h-3.5 text-teal-400 ml-auto" />
        )}
      </button>

      {/* Expanded RAG Transparency Drawer */}
      {isOpen && (
        <div className="mt-2.5 p-3.5 rounded-xl bg-slate-900/90 border border-teal-500/30 shadow-xl space-y-3 animate-in fade-in slide-in-from-top-1 duration-150">
          {/* Header Summary */}
          <div className="flex items-center justify-between pb-2 border-b border-white/10 text-xs">
            <span className="font-semibold text-white flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              Retrieval & Grounding Transparency
            </span>
            <span className="text-[10px] text-slate-400">
              Zero-Hallucination Audit Trail
            </span>
          </div>

          {/* Detected Metadata Filters */}
          <div className="p-2.5 rounded-lg bg-slate-800/60 border border-white/5 space-y-1.5">
            <div className="flex items-center gap-1.5 text-[11px] font-semibold text-slate-300">
              <Filter className="w-3 h-3 text-indigo-400" />
              <span>Detected Metadata Filters:</span>
            </div>
            {hasFilters ? (
              <div className="flex flex-wrap gap-1.5 pt-0.5">
                {detectedFilters.semester && (
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-200 border border-indigo-500/30">
                    Semester: {detectedFilters.semester}
                  </span>
                )}
                {detectedFilters.credits && (
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-teal-500/20 text-teal-200 border border-teal-500/30">
                    Credits: {detectedFilters.credits}
                  </span>
                )}
                {detectedFilters.course_type && (
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-500/20 text-purple-200 border border-purple-500/30">
                    Type: {detectedFilters.course_type}
                  </span>
                )}
                {detectedFilters.course_codes && detectedFilters.course_codes.length > 0 && (
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-sky-500/20 text-sky-200 border border-sky-500/30">
                    Codes: {detectedFilters.course_codes.join(', ')}
                  </span>
                )}
                {detectedFilters.department && (
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-200 border border-emerald-500/30">
                    Dept: {detectedFilters.department}
                  </span>
                )}
              </div>
            ) : (
              <p className="text-[10px] text-slate-400 italic">
                General semantic retrieval used (no specific metadata filters detected in query).
              </p>
            )}
          </div>

          {/* Retrieved Chunks List */}
          <div className="space-y-2">
            <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
              Retrieved Curriculum Chunks ({retrievedChunks.length})
            </p>

            <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
              {retrievedChunks.map((chunk, idx) => {
                const isItemExpanded = expandedChunkId === (chunk.chunk_id || idx);
                const scorePercent = Math.min(Math.round((chunk.similarity_score || 0) * 100), 100);
                const meta = chunk.metadata || {};

                return (
                  <div
                    key={chunk.chunk_id || idx}
                    className="p-2.5 rounded-lg bg-slate-800/40 border border-white/5 hover:border-teal-500/30 transition-all space-y-1.5"
                  >
                    {/* Top Row: Doc Name, Page, Score */}
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2 min-w-0">
                        <FileText className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0" />
                        <span className="text-xs font-semibold text-slate-200 truncate" title={chunk.filename}>
                          {chunk.filename}
                        </span>
                        <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-indigo-500/20 text-indigo-300">
                          Page {chunk.page_number}
                        </span>
                      </div>

                      {/* Relevance Score Bar */}
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <span className="text-[11px] font-mono text-teal-400 font-bold">
                          {chunk.similarity_score ? `${Math.round(chunk.similarity_score * 100)}% match` : 'Matched'}
                        </span>
                        <div className="w-12 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-teal-400 rounded-full"
                            style={{ width: `${Math.max(scorePercent, 15)}%` }}
                          />
                        </div>
                      </div>
                    </div>

                    {/* Metadata Badges */}
                    <div className="flex flex-wrap gap-1 text-[10px]">
                      {meta.semester && (
                        <span className="px-1.5 py-0.2 rounded bg-indigo-500/15 text-indigo-200 border border-indigo-500/20 font-mono">
                          Sem {meta.semester}
                        </span>
                      )}
                      {meta.credits !== null && meta.credits !== undefined && (
                        <span className="px-1.5 py-0.2 rounded bg-teal-500/15 text-teal-200 border border-teal-500/20 font-mono">
                          {meta.credits} Credits
                        </span>
                      )}
                      {meta.primary_course_code && (
                        <span className="px-1.5 py-0.2 rounded bg-purple-500/15 text-purple-200 border border-purple-500/20 font-mono font-bold">
                          {meta.primary_course_code}
                        </span>
                      )}
                      {meta.prerequisites && (
                        <span className="px-1.5 py-0.2 rounded bg-amber-500/15 text-amber-200 border border-amber-500/20 truncate max-w-[180px]">
                          Prereq: {meta.prerequisites}
                        </span>
                      )}
                    </div>

                    {/* Expandable Chunk Excerpt */}
                    <div className="pt-1">
                      <button
                        type="button"
                        onClick={() => setExpandedChunkId(isItemExpanded ? null : (chunk.chunk_id || idx))}
                        className="text-[10px] text-slate-400 hover:text-slate-200 flex items-center gap-1 font-mono cursor-pointer"
                      >
                        <span>{isItemExpanded ? '▾ Hide text snippet' : '▸ View text snippet'}</span>
                      </button>

                      {isItemExpanded && (
                        <div className="mt-1.5 p-2 rounded bg-slate-900 text-[11px] font-mono text-slate-300 leading-relaxed whitespace-pre-wrap border border-white/5">
                          {chunk.text}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
