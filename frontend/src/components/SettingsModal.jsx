import React, { useState } from 'react';
import { X, Sliders, Key, Cpu, ShieldCheck, Check, Sparkles, Zap } from 'lucide-react';

export default function SettingsModal({
  isOpen,
  onClose,
  settings,
  onSaveSettings,
}) {
  const [groqKey, setGroqKey] = useState('');
  const [chunkSize, setChunkSize] = useState(settings.chunk_size || 500);
  const [chunkOverlap, setChunkOverlap] = useState(settings.chunk_overlap || 100);
  const [topK, setTopK] = useState(settings.top_k || 4);
  const [isSaved, setIsSaved] = useState(false);

  if (!isOpen) return null;

  const handleSave = () => {
    const payload = {
      llm_provider: 'groq',
      chunk_size: parseInt(chunkSize),
      chunk_overlap: parseInt(chunkOverlap),
      top_k: parseInt(topK),
    };
    if (groqKey.trim()) payload.groq_api_key = groqKey.trim();

    onSaveSettings(payload);
    setIsSaved(true);
    setTimeout(() => {
      setIsSaved(false);
      onClose();
    }, 800);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="w-full max-w-md bg-[#0e1424] border border-white/10 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-white/10 bg-slate-900/50">
          <div className="flex items-center gap-2 text-white font-semibold text-sm">
            <Sliders className="w-4 h-4 text-indigo-400" />
            <span>LLM & RAG Settings</span>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-5 space-y-4 overflow-y-auto">
          {/* Sole LLM Engine: Groq AI */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-200 flex items-center gap-1.5">
              <Zap className="w-4 h-4 text-amber-400" />
              <span>Dedicated LLM Reasoning Engine</span>
            </label>
            <div className="p-3.5 rounded-xl border border-indigo-500/40 bg-indigo-950/30 text-xs space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-bold text-white text-sm">Groq AI Engine</span>
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 font-semibold">
                  Active & Connected
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                Powers CourseGuide AI with sub-second RAG response generation and strict grounded academic reasoning.
              </p>
            </div>
          </div>

          {/* Groq API Key input */}
          <div className="space-y-1.5 p-3 rounded-xl bg-slate-900/60 border border-white/5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-medium text-slate-300 flex items-center gap-1.5">
                <Key className="w-3.5 h-3.5 text-amber-400" />
                <span>Groq API Key</span>
              </label>
              {settings.has_groq_key && (
                <span className="text-[10px] text-emerald-400 flex items-center gap-1 font-medium">
                  <ShieldCheck className="w-3.5 h-3.5" /> Configured & Verified
                </span>
              )}
            </div>
            <input
              type="password"
              placeholder={settings.has_groq_key ? '••••••••••••••••••••••••' : 'Enter Groq API Key'}
              value={groqKey}
              onChange={(e) => setGroqKey(e.target.value)}
              className="w-full bg-slate-950 text-slate-200 text-xs rounded-lg px-3 py-2 border border-white/10 focus:outline-none focus:border-indigo-500 font-mono"
            />
            <p className="text-[10px] text-slate-500">
              API key securely saved on the backend.
            </p>
          </div>

          {/* RAG Chunker & Retrieval Parameters */}
          <div className="space-y-3 pt-2 border-t border-white/5">
            <h3 className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-indigo-400" />
              <span>Retrieval & Chunking Parameters</span>
            </h3>

            {/* Top-K Slider */}
            <div className="space-y-1">
              <div className="flex justify-between text-xs text-slate-300">
                <span>Top-K Retrieved Chunks</span>
                <span className="font-mono text-indigo-300">{topK}</span>
              </div>
              <input
                type="range"
                min="2"
                max="8"
                step="1"
                value={topK}
                onChange={(e) => setTopK(e.target.value)}
                className="w-full accent-indigo-500 cursor-pointer"
              />
            </div>

            {/* Chunk Size Slider */}
            <div className="space-y-1">
              <div className="flex justify-between text-xs text-slate-300">
                <span>Chunk Size</span>
                <span className="font-mono text-indigo-300">{chunkSize} chars</span>
              </div>
              <input
                type="range"
                min="300"
                max="1000"
                step="50"
                value={chunkSize}
                onChange={(e) => setChunkSize(e.target.value)}
                className="w-full accent-indigo-500 cursor-pointer"
              />
            </div>

            {/* Chunk Overlap Slider */}
            <div className="space-y-1">
              <div className="flex justify-between text-xs text-slate-300">
                <span>Chunk Overlap</span>
                <span className="font-mono text-indigo-300">{chunkOverlap} chars</span>
              </div>
              <input
                type="range"
                min="50"
                max="200"
                step="25"
                value={chunkOverlap}
                onChange={(e) => setChunkOverlap(e.target.value)}
                className="w-full accent-indigo-500 cursor-pointer"
              />
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-white/10 bg-slate-900/50 flex items-center justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            className="px-3.5 py-1.5 text-xs text-slate-400 hover:text-white rounded-lg transition-colors cursor-pointer"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSave}
            className="px-4 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/30 transition-all cursor-pointer flex items-center gap-1.5"
          >
            {isSaved ? <Check className="w-3.5 h-3.5" /> : null}
            <span>{isSaved ? 'Saved!' : 'Apply Settings'}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
