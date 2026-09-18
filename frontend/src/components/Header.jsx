import React from 'react';
import { Sparkles, Database, Sliders, Trash2, Cpu, BookOpen } from 'lucide-react';

export default function Header({ 
  stats, 
  settings, 
  onOpenSettings, 
  onOpenHowItWorks,
  onClearChat, 
  chatLength 
}) {
  return (
    <header className="sticky top-0 z-30 border-b border-white/10 bg-[#0c1220]/90 backdrop-blur-md px-4 lg:px-8 py-3.5 flex items-center justify-between">
      {/* Brand & Subtitle */}
      <div className="flex items-center gap-3.5">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 via-purple-600 to-teal-400 flex items-center justify-center shadow-lg shadow-indigo-500/20 text-white font-bold">
          <BookOpen className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg lg:text-xl font-bold tracking-tight text-white flex items-center gap-2">
              CourseGuide AI
            </h1>
            <span className="hidden sm:inline-flex items-center gap-1 text-[11px] font-medium tracking-wide uppercase px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              <Sparkles className="w-3 h-3 text-indigo-400 animate-pulse" />
              RAG Active
            </span>
          </div>
          <p className="text-xs text-slate-400 font-normal">
            Ask anything about your college curriculum
          </p>
        </div>
      </div>

      {/* RAG Status, Stats & Actions */}
      <div className="flex items-center gap-3">
        {/* Stats Pill */}
        <div className="hidden md:flex items-center gap-2.5 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-white/5 text-xs text-slate-300">
          <div className="flex items-center gap-1.5 text-slate-400">
            <Database className="w-3.5 h-3.5 text-teal-400" />
            <span>Docs:</span>
            <span className="font-semibold text-white">{stats.total_documents || 0}</span>
          </div>
          <span className="text-slate-600">|</span>
          <div className="flex items-center gap-1.5 text-slate-400">
            <Cpu className="w-3.5 h-3.5 text-indigo-400" />
            <span>Chunks:</span>
            <span className="font-semibold text-white">{stats.total_chunks || 0}</span>
          </div>
        </div>

        {/* LLM Mode Badge */}
        <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-800/80 border border-indigo-500/30 text-xs text-indigo-300 font-medium">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Groq AI Engine</span>
        </div>

        {/* Clear Chat */}
        {chatLength > 0 && (
          <button
            onClick={onClearChat}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors border border-transparent hover:border-white/10"
            title="Clear Chat History"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Clear</span>
          </button>
        )}

        {/* How It Works Button */}
        <button
          onClick={onOpenHowItWorks}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-gradient-to-r from-teal-500/20 to-indigo-500/20 hover:from-teal-500/30 hover:to-indigo-500/30 text-teal-300 border border-teal-500/30 transition-all hover:shadow-md hover:shadow-teal-500/10 cursor-pointer"
          title="View End-to-End RAG Pipeline Architecture"
        >
          <Sparkles className="w-3.5 h-3.5 text-teal-400" />
          <span>How It Works</span>
        </button>

        {/* Settings Button */}
        <button
          onClick={onOpenSettings}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 transition-all hover:shadow-md hover:shadow-indigo-500/10 cursor-pointer"
          title="RAG and LLM Settings"
        >
          <Sliders className="w-3.5 h-3.5" />
          <span>Settings</span>
        </button>
      </div>
    </header>
  );
}
