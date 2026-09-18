import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Sparkles, 
  Bot, 
  User, 
  BookOpen, 
  FileText, 
  AlertTriangle, 
  ArrowRight,
  ChevronRight,
  Clock,
  Compass,
  GraduationCap,
  Calendar,
  Layers,
  HelpCircle
} from 'lucide-react';
import FormattedAnswer from './FormattedAnswer';
import WhyThisAnswer from './WhyThisAnswer';

const QUICK_QUESTION_CATEGORIES = [
  {
    category: "Semester",
    icon: Calendar,
    color: "from-blue-500/20 to-indigo-500/20 text-indigo-300 border-indigo-500/30",
    questions: [
      { text: "What subjects are available in the third semester?", label: "Semester 3 Subjects" },
      { text: "List all courses and labs in Semester 5", label: "Semester 5 Subjects" },
    ],
  },
  {
    category: "Courses",
    icon: GraduationCap,
    color: "from-purple-500/20 to-pink-500/20 text-purple-300 border-purple-500/30",
    questions: [
      { text: "What is the course code for Database Management Systems?", label: "Course Code" },
      { text: "What are the course credits for Operating Systems?", label: "Course Credits" },
      { text: "Which courses have programming prerequisites?", label: "Course Prerequisites" },
    ],
  },
  {
    category: "Curriculum",
    icon: Layers,
    color: "from-teal-500/20 to-emerald-500/20 text-teal-300 border-teal-500/30",
    questions: [
      { text: "List the elective subjects available in the curriculum", label: "Electives" },
      { text: "What are the core courses in the curriculum?", label: "Core Courses" },
      { text: "What is the total credit requirement across the curriculum?", label: "Total Credits" },
    ],
  },
];

export default function ChatPanel({
  messages,
  isLoading,
  loadingStage,
  onSendMessage,
  onSelectCitation,
  documentsCount,
  onLoadSample,
}) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, loadingStage]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleQuickQuestionClick = (query) => {
    if (isLoading) return;
    onSendMessage(query);
  };

  return (
    <main className="flex-1 flex flex-col h-full bg-[#0a0f1d] relative overflow-hidden">
      {/* Scrollable Conversation Area */}
      <div className="flex-1 overflow-y-auto px-4 md:px-8 py-6 space-y-6">
        {messages.length === 0 ? (
          /* Welcome Hero & Categorized Quick Questions */
          <div className="max-w-3xl mx-auto py-6 text-center space-y-6">
            <div className="inline-flex items-center justify-center p-3.5 rounded-2xl bg-gradient-to-tr from-indigo-500/20 via-purple-500/20 to-teal-500/20 border border-indigo-500/30 text-indigo-300 shadow-xl shadow-indigo-500/10 mb-1">
              <Compass className="w-8 h-8 text-indigo-400" />
            </div>

            <div className="space-y-2">
              <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white">
                CourseGuide AI
              </h2>
              <p className="text-sm text-slate-400 max-w-xl mx-auto">
                Ask questions about subjects, prerequisites, semesters, course codes, and academic credits grounded directly in your uploaded syllabus.
              </p>
            </div>

            {documentsCount === 0 && (
              <div className="p-4 rounded-xl bg-indigo-950/40 border border-indigo-500/30 text-left max-w-xl mx-auto flex items-start gap-3">
                <Sparkles className="w-5 h-5 text-teal-400 flex-shrink-0 mt-0.5" />
                <div className="text-xs">
                  <p className="font-semibold text-white">Get started instantly</p>
                  <p className="text-slate-400 mt-0.5">
                    Click below to load the authentic 8-semester B.Tech Computer Science curriculum.
                  </p>
                  <button
                    onClick={onLoadSample}
                    className="mt-2.5 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs shadow-md transition-colors cursor-pointer"
                  >
                    <span>Load B.Tech CSE Curriculum</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            )}

            {/* Quick Question Categories */}
            <div className="space-y-4 pt-2 text-left">
              <div className="flex items-center justify-between px-1">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Quick Question Categories
                </span>
                <span className="text-[11px] text-teal-400 font-medium">Click to execute live query</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
                {QUICK_QUESTION_CATEGORIES.map((cat, cIdx) => {
                  const CategoryIcon = cat.icon;
                  return (
                    <div
                      key={cIdx}
                      className="p-3.5 rounded-xl bg-slate-900/60 border border-white/5 space-y-2.5 flex flex-col justify-between"
                    >
                      <div className="flex items-center gap-2 pb-2 border-b border-white/5">
                        <div className={`p-1.5 rounded-lg bg-gradient-to-r ${cat.color} border`}>
                          <CategoryIcon className="w-3.5 h-3.5" />
                        </div>
                        <span className="text-xs font-bold text-white tracking-wide">
                          {cat.category}
                        </span>
                      </div>

                      <div className="space-y-1.5 flex-1">
                        {cat.questions.map((q, qIdx) => (
                          <button
                            key={qIdx}
                            onClick={() => handleQuickQuestionClick(q.text)}
                            className="w-full text-left p-2 rounded-lg bg-slate-800/40 hover:bg-indigo-950/60 border border-white/5 hover:border-indigo-500/30 transition-all text-xs text-slate-300 hover:text-white group flex items-start justify-between gap-1.5 cursor-pointer"
                          >
                            <span className="leading-snug">{q.label}</span>
                            <ChevronRight className="w-3 h-3 text-slate-500 group-hover:text-teal-400 group-hover:translate-x-0.5 transition-transform flex-shrink-0 mt-0.5" />
                          </button>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        ) : (
          /* Messages History */
          messages.map((msg, index) => (
            <div
              key={index}
              className={`flex gap-3.5 max-w-3xl ${
                msg.role === 'user' ? 'ml-auto flex-row-reverse' : 'mr-auto'
              }`}
            >
              {/* Avatar */}
              <div
                className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 text-white text-xs ${
                  msg.role === 'user'
                    ? 'bg-gradient-to-tr from-indigo-600 to-indigo-500 shadow-md shadow-indigo-600/30'
                    : 'bg-gradient-to-tr from-purple-600 via-indigo-600 to-teal-500 shadow-md shadow-purple-600/20'
                }`}
              >
                {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              {/* Message Bubble */}
              <div className="space-y-2 max-w-[85%]">
                <div
                  className={`p-4 rounded-2xl text-xs md:text-sm leading-relaxed ${
                    msg.role === 'user'
                      ? 'bg-indigo-600 text-white rounded-tr-none shadow-md shadow-indigo-600/15'
                      : msg.not_found
                      ? 'bg-amber-950/30 border border-amber-500/40 text-amber-100 rounded-tl-none'
                      : 'bg-slate-900/90 border border-white/10 text-slate-100 rounded-tl-none shadow-xl'
                  }`}
                >
                  {/* Warning Header for Not-Found / Guardrail refusal state */}
                  {msg.not_found && (
                    <div className="flex items-center gap-2 mb-2 pb-2 border-b border-amber-500/20 text-amber-400 font-semibold text-xs">
                      <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0" />
                      <span>Not Found in Uploaded Curriculum</span>
                    </div>
                  )}

                  {/* Formatted Content with Tables Support */}
                  {msg.role === 'user' ? (
                    <div className="whitespace-pre-wrap">{msg.content}</div>
                  ) : (
                    <FormattedAnswer content={msg.content} />
                  )}

                  {/* RAG Transparency: Why this answer? */}
                  {msg.role === 'assistant' && msg.retrieved_chunks && msg.retrieved_chunks.length > 0 && (
                    <WhyThisAnswer
                      retrievedChunks={msg.retrieved_chunks}
                      detectedFilters={msg.detected_filters || {}}
                      sources={msg.sources || []}
                    />
                  )}
                </div>

                {/* Source Citations */}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="pt-1 space-y-1.5">
                    <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 px-1">
                      Official Source Documents
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {msg.sources.map((src, sIdx) => (
                        <button
                          key={sIdx}
                          onClick={() => onSelectCitation(src)}
                          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-indigo-950/80 border border-white/10 hover:border-indigo-400/40 text-[11px] text-indigo-300 transition-all cursor-pointer group"
                        >
                          <FileText className="w-3 h-3 text-indigo-400" />
                          <span className="font-medium text-slate-200 group-hover:text-white">
                            {src.filename}
                          </span>
                          <span className="px-1.5 py-0.2 rounded bg-indigo-500/20 text-indigo-300 font-mono text-[10px]">
                            Page {src.page_number}
                          </span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Metadata & Latency Pills */}
                {msg.latency && (
                  <div className="flex items-center gap-2 text-[10px] text-slate-500 px-1">
                    <Clock className="w-3 h-3" />
                    <span>Total: {msg.latency.total_sec}s</span>
                    <span>•</span>
                    <span>Retrieval: {msg.latency.retrieve_sec}s</span>
                    {msg.provider_used && (
                      <>
                        <span>•</span>
                        <span className="text-slate-400">{msg.provider_used}</span>
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {/* Dynamic Loading State Indicator */}
        {isLoading && (
          <div className="flex gap-3.5 max-w-xl mr-auto">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-600 flex items-center justify-center flex-shrink-0 text-white animate-pulse">
              <Bot className="w-4 h-4" />
            </div>
            <div className="p-4 rounded-2xl rounded-tl-none bg-slate-900/80 border border-indigo-500/30 text-xs text-slate-300 flex items-center gap-3">
              <div className="flex space-x-1">
                <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 rounded-full bg-purple-400 animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 rounded-full bg-teal-400 animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
              <span className="font-medium text-indigo-300 font-mono">
                {loadingStage || 'Processing question through RAG pipeline...'}
              </span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area with Quick Category Chips */}
      <div className="p-4 border-t border-white/10 bg-[#0c1220]/90 backdrop-blur-md space-y-3">
        {/* Category Quick Chips Bar */}
        <div className="max-w-3xl mx-auto flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
          <span className="text-[10px] uppercase font-bold text-slate-500 px-1 flex-shrink-0">Quick:</span>
          <button
            type="button"
            onClick={() => handleQuickQuestionClick("What subjects are available in the third semester?")}
            className="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 hover:text-white border border-white/5 text-[11px] whitespace-nowrap cursor-pointer transition-colors"
          >
            Subjects in Sem 3
          </button>
          <button
            type="button"
            onClick={() => handleQuickQuestionClick("List all courses and labs in Semester 5")}
            className="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 hover:text-white border border-white/5 text-[11px] whitespace-nowrap cursor-pointer transition-colors"
          >
            Subjects in Sem 5
          </button>
          <button
            type="button"
            onClick={() => handleQuickQuestionClick("What is the course code for Database Management Systems?")}
            className="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 hover:text-white border border-white/5 text-[11px] whitespace-nowrap cursor-pointer transition-colors"
          >
            Course Code
          </button>
          <button
            type="button"
            onClick={() => handleQuickQuestionClick("What are the course credits for Operating Systems?")}
            className="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 hover:text-white border border-white/5 text-[11px] whitespace-nowrap cursor-pointer transition-colors"
          >
            Course Credits
          </button>
          <button
            type="button"
            onClick={() => handleQuickQuestionClick("Which courses have programming prerequisites?")}
            className="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 hover:text-white border border-white/5 text-[11px] whitespace-nowrap cursor-pointer transition-colors"
          >
            Prerequisites
          </button>
          <button
            type="button"
            onClick={() => handleQuickQuestionClick("List the elective subjects available in the curriculum")}
            className="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 hover:text-white border border-white/5 text-[11px] whitespace-nowrap cursor-pointer transition-colors"
          >
            Electives
          </button>
          <button
            type="button"
            onClick={() => handleQuickQuestionClick("What are the core courses in the curriculum?")}
            className="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 hover:text-white border border-white/5 text-[11px] whitespace-nowrap cursor-pointer transition-colors"
          >
            Core Courses
          </button>
          <button
            type="button"
            onClick={() => handleQuickQuestionClick("What is the total credit requirement across the curriculum?")}
            className="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 hover:text-white border border-white/5 text-[11px] whitespace-nowrap cursor-pointer transition-colors"
          >
            Total Credits
          </button>
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto flex items-center gap-2">
          <div className="relative flex-1">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about subjects, prerequisites, credits, course codes..."
              disabled={isLoading}
              className="w-full bg-slate-900/90 text-slate-100 text-xs md:text-sm placeholder-slate-500 rounded-xl px-4 py-3 border border-white/10 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all pr-10"
            />
          </div>

          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="p-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium shadow-md shadow-indigo-600/25 transition-all disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer flex-shrink-0"
            title="Send Question"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>

        <p className="text-[10px] text-center text-slate-500">
          Responses are strictly grounded in uploaded curriculum documents. Zero hallucination guarantee.
        </p>
      </div>
    </main>
  );
}

