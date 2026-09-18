import React from 'react';
import { X, ArrowDown, FileText, Split, Tag, Cpu, Database, Search, Layers, Bot, CheckCircle, Sparkles } from 'lucide-react';

const PIPELINE_STEPS = [
  {
    step: 1,
    title: "PDF Documents",
    desc: "Official college syllabus or curriculum PDF uploaded by user",
    icon: FileText,
    color: "from-blue-500 to-indigo-600",
  },
  {
    step: 2,
    title: "Text & Table Extraction",
    desc: "PyMuPDF extracts text, headings & structured tabular rows page-by-page",
    icon: Split,
    color: "from-indigo-500 to-violet-600",
  },
  {
    step: 3,
    title: "Page-Aware Chunking",
    desc: "Preserves page numbers and course-credit table relationships",
    icon: Layers,
    color: "from-violet-500 to-purple-600",
  },
  {
    step: 4,
    title: "Metadata Extraction",
    desc: "Reliably detects semesters, course codes, credits, and prerequisites",
    icon: Tag,
    color: "from-purple-500 to-fuchsia-600",
  },
  {
    step: 5,
    title: "Dense Embeddings",
    desc: "SentenceTransformers (all-MiniLM-L6-v2) generates 384-dim normalized vectors",
    icon: Cpu,
    color: "from-fuchsia-500 to-pink-600",
  },
  {
    step: 6,
    title: "FAISS Vector Index",
    desc: "IndexFlatIP calculates exact cosine similarity in milliseconds",
    icon: Database,
    color: "from-pink-500 to-rose-600",
  },
  {
    step: 7,
    title: "Metadata + Semantic Retrieval",
    desc: "Analyzes student query filters & boosts matching chunks non-destructively",
    icon: Search,
    color: "from-rose-500 to-amber-600",
  },
  {
    step: 8,
    title: "Relevant Context",
    desc: "Top-ranked authentic chunks assembled with page boundaries",
    icon: CheckCircle,
    color: "from-amber-500 to-teal-600",
  },
  {
    step: 9,
    title: "LLM Generation (Groq)",
    desc: "Strictly grounded academic reasoning with zero hallucination guardrail",
    icon: Bot,
    color: "from-teal-500 to-emerald-600",
  },
  {
    step: 10,
    title: "Grounded Answer + Sources",
    desc: "Structured response citing exact document name and verified page numbers",
    icon: Sparkles,
    color: "from-emerald-500 to-cyan-500",
  },
];

export default function HowItWorksModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-md p-4 animate-in fade-in duration-200">
      <div className="w-full max-w-3xl bg-[#0b101d] border border-white/10 rounded-2xl shadow-2xl flex flex-col max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-white/10 bg-slate-900/60 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white">How CourseGuide AI Works</h2>
              <p className="text-[11px] text-slate-400">Complete end-to-end RAG (Retrieval-Augmented Generation) pipeline</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Pipeline Flow Content */}
        <div className="p-6 overflow-y-auto space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {PIPELINE_STEPS.map((step, idx) => {
              const Icon = step.icon;
              return (
                <div
                  key={step.step}
                  className="relative p-3.5 rounded-xl bg-slate-900/50 border border-white/5 hover:border-indigo-500/30 transition-all flex items-start gap-3 group"
                >
                  <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${step.color} flex items-center justify-center text-white flex-shrink-0 shadow-md font-bold text-xs`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono text-indigo-400 font-bold">
                        STEP {step.step}
                      </span>
                      <h3 className="text-xs font-bold text-white group-hover:text-indigo-300 transition-colors">
                        {step.title}
                      </h3>
                    </div>
                    <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                      {step.desc}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Project Viva / Demonstration Note */}
          <div className="mt-4 p-4 rounded-xl bg-gradient-to-r from-indigo-950/40 via-purple-950/20 to-slate-900/60 border border-indigo-500/20 text-xs text-slate-300 space-y-1">
            <p className="font-semibold text-white flex items-center gap-1.5">
              <CheckCircle className="w-3.5 h-3.5 text-teal-400" />
              Academic RAG Integrity Guarantee
            </p>
            <p className="text-[11px] text-slate-400">
              Unlike generic chatbots that guess when details are missing, CourseGuide AI enforces strict contextual grounding. If a course, credit, or prerequisite is not explicitly present in the uploaded curriculum PDFs, the system returns a verified refusal rather than generating unverified content.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-white/10 bg-slate-900/50 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 text-xs font-medium rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition-colors cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
