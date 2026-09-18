import React, { useState } from 'react';
import { 
  Search, 
  Filter, 
  ChevronDown, 
  ChevronUp, 
  FileText, 
  Sparkles, 
  CheckCircle2, 
  Database,
  Hash,
  BookOpen,
  Info
} from 'lucide-react';

export default function RetrievalPanel({
  retrievalData,
  highlightedChunkId,
  onCloseMobile,
}) {
  const [expandedChunks, setExpandedChunks] = useState({});

  const toggleExpand = (chunkId) => {
    setExpandedChunks(prev => ({
      ...prev,
      [chunkId]: !prev[chunkId]
    }));
  };

  const chunks = retrievalData?.retrieved_chunks || [];
  const filters = retrievalData?.detected_filters || {};
  const hasFilters = Object.keys(filters).length > 0;

  return (
    <aside className="w-full lg:w-96 flex-shrink-0 flex flex-col h-full border-l border-white/10 bg-[#0d1322]/80 backdrop-blur-md p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-white/5">
        <div className="flex items-center gap-2 text-white font-semibold text-sm">
          <Search className="w-4 h-4 text-teal-400" />
          <span>Retrieved Information</span>
        </div>
        <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-slate-800 text-teal-300 border border-white/5">
          {chunks.length} chunks
        </span>
      </div>

      {/* Query Filters Inspector */}
      <div className="p-3 rounded-xl bg-slate-900/60 border border-white/5 space-y-2">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-300">
          <Filter className="w-3.5 h-3.5 text-indigo-400" />
          <span>Metadata Filter Analysis</span>
        </div>

        {hasFilters ? (
          <div className="flex flex-wrap gap-1.5 pt-1">
            {filters.semester && (
              <span className="inline-flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded-md bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                Semester: {filters.semester}
              </span>
            )}
            {filters.credits && (
              <span className="inline-flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded-md bg-teal-500/20 text-teal-300 border border-teal-500/30">
                Credits: {filters.credits}
              </span>
            )}
            {filters.course_type && (
              <span className="inline-flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded-md bg-purple-500/20 text-purple-300 border border-purple-500/30">
                Type: {filters.course_type}
              </span>
            )}
            {filters.course_codes && filters.course_codes.length > 0 && (
              <span className="inline-flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded-md bg-sky-500/20 text-sky-300 border border-sky-500/30">
                Codes: {filters.course_codes.join(', ')}
              </span>
            )}
            {filters.department && (
              <span className="inline-flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded-md bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                Dept: {filters.department}
              </span>
            )}
          </div>
        ) : (
          <p className="text-[11px] text-slate-500 italic">
            Semantic similarity retrieval active (no explicit metadata filters in query).
          </p>
        )}
      </div>

      {/* Retrieved Chunks List */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-1">
        <div className="flex items-center justify-between px-1">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            Context Chunks Passed to LLM
          </span>
          <span className="text-[10px] text-slate-500 font-mono">Ranked by score</span>
        </div>

        {chunks.length === 0 ? (
          <div className="text-center py-12 px-4 rounded-xl border border-dashed border-slate-800 bg-slate-900/20">
            <Database className="w-8 h-8 text-slate-600 mx-auto mb-2" />
            <p className="text-xs font-medium text-slate-300">No chunks retrieved</p>
            <p className="text-[11px] text-slate-500 mt-1">
              Ask a question in the chat to see real-time FAISS retrieval & metadata grounding.
            </p>
          </div>
        ) : (
          chunks.map((chunk, idx) => {
            const isExpanded = !!expandedChunks[chunk.chunk_id];
            const isHighlighted = highlightedChunkId === chunk.chunk_id;
            const meta = chunk.metadata || {};
            const scorePercent = Math.min(Math.round((chunk.similarity_score || 0) * 100), 100);

            return (
              <div
                key={chunk.chunk_id || idx}
                id={`chunk-${chunk.chunk_id}`}
                className={`rounded-xl border transition-all ${
                  isHighlighted 
                    ? 'border-indigo-500 bg-indigo-950/40 ring-2 ring-indigo-500/30' 
                    : 'border-white/5 bg-slate-800/40 hover:bg-slate-800/70 hover:border-white/10'
                }`}
              >
                {/* Chunk Header */}
                <div className="p-3">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2 min-w-0">
                      <span className="w-5 h-5 rounded-full bg-slate-700 text-slate-300 text-[10px] font-bold flex items-center justify-center flex-shrink-0">
                        {idx + 1}
                      </span>
                      <div className="min-w-0">
                        <p className="text-xs font-medium text-slate-200 truncate">
                          {chunk.filename}
                        </p>
                        <p className="text-[11px] text-indigo-400 font-medium">
                          Page {chunk.page_number}
                        </p>
                      </div>
                    </div>

                    {/* Similarity score meter */}
                    <div className="text-right flex-shrink-0">
                      <div className="flex items-center gap-1 text-[11px] font-mono text-teal-400 font-semibold">
                        <span>Score:</span>
                        <span>{chunk.similarity_score}</span>
                      </div>
                      <div className="w-16 h-1.5 bg-slate-700 rounded-full mt-1 overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-indigo-500 to-teal-400 rounded-full"
                          style={{ width: `${Math.max(scorePercent, 10)}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>

                  {/* Metadata Tags Pill Container */}
                  <div className="flex flex-wrap gap-1.5 mt-2.5">
                    {meta.semester && (
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/15 text-indigo-300 border border-indigo-500/20">
                        Sem {meta.semester}
                      </span>
                    )}
                    {meta.credits !== null && meta.credits !== undefined && (
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-teal-500/15 text-teal-300 border border-teal-500/20">
                        {meta.credits} Credits
                      </span>
                    )}
                    {meta.course_type && (
                      <span className="text-[10px] px-2 py-0.5 rounded bg-purple-500/15 text-purple-300 border border-purple-500/20">
                        {meta.course_type}
                      </span>
                    )}
                    {meta.primary_course_code && (
                      <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-sky-500/15 text-sky-300 border border-sky-500/20">
                        {meta.primary_course_code}
                      </span>
                    )}
                    {meta.prerequisites && (
                      <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/15 text-amber-300 border border-amber-500/20 truncate max-w-[150px]" title={meta.prerequisites}>
                        Prereq: {meta.prerequisites}
                      </span>
                    )}
                  </div>
                </div>

                {/* Expandable Raw Chunk Content */}
                <div className="border-t border-white/5">
                  <button
                    onClick={() => toggleExpand(chunk.chunk_id)}
                    className="w-full px-3 py-1.5 flex items-center justify-between text-[11px] font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-700/20 transition-colors cursor-pointer"
                  >
                    <span>{isExpanded ? 'Hide Raw Context' : 'Inspect Retrieved Context'}</span>
                    {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </button>

                  {isExpanded && (
                    <div className="p-3 pt-1 bg-slate-900/90 text-[11px] font-mono text-slate-300 leading-relaxed whitespace-pre-wrap rounded-b-xl border-t border-white/5 max-h-60 overflow-y-auto">
                      {chunk.text}
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </aside>
  );
}
