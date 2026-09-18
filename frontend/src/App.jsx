import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import DocumentPanel from './components/DocumentPanel';
import ChatPanel from './components/ChatPanel';
import RetrievalPanel from './components/RetrievalPanel';
import SettingsModal from './components/SettingsModal';
import HowItWorksModal from './components/HowItWorksModal';

const API_BASE = import.meta.env.VITE_API_URL || '';

export default function App() {
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState({ total_documents: 0, total_chunks: 0, courses_count: 0, semesters_count: 0 });
  const [selectedDocId, setSelectedDocId] = useState(null);
  const [selectedDocChunks, setSelectedDocChunks] = useState([]);
  const [settings, setSettings] = useState({
    chunk_size: 500,
    chunk_overlap: 50,
    top_k: 4,
    llm_provider: 'groq',
    has_groq_key: false,
    groq_model: 'groq/compound-mini',
  });
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content: '👋 Welcome to **CourseGuide AI**! I am your intelligent academic curriculum advisor.\n\nUpload your syllabus or academic regulation PDF, or click **"Load Sample Curriculum"** on the left to start exploring course credits, semester plans, prerequisites, and degree requirements.',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStage, setLoadingStage] = useState('');
  const [retrievalState, setRetrievalState] = useState({
    activeQuery: null,
    chunks: [],
    provider: 'groq',
  });
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState('');
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isHowItWorksOpen, setIsHowItWorksOpen] = useState(false);
  const [activeMobileTab, setActiveMobileTab] = useState('chat'); // 'docs', 'chat', 'retrieval'

  // Fetch initial documents and settings
  const fetchDocuments = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/documents`);
      if (res.ok) {
        const data = await res.json();
        setDocuments(data.documents || []);
        setStats(data || { total_documents: 0, total_chunks: 0 });
      }
    } catch (err) {
      console.error('Failed to fetch documents:', err);
    }
  };

  const fetchSettings = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/settings`);
      if (res.ok) {
        const data = await res.json();
        setSettings(data);
      }
    } catch (err) {
      console.error('Failed to fetch settings:', err);
    }
  };

  useEffect(() => {
    fetchDocuments();
    fetchSettings();
  }, []);

  // Handle uploading PDF files
  const handleUploadFiles = async (files) => {
    if (!files || files.length === 0) return;
    setIsUploading(true);
    setUploadProgress(`Uploading & indexing ${files.length} file(s)...`);

    const formData = new FormData();
    for (const file of files) {
      formData.append('files', file);
    }

    try {
      setUploadProgress('Extracting text with PyMuPDF & chunking...');
      const res = await fetch(`${API_BASE}/api/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Upload failed');
      }

      const data = await res.json();
      setUploadProgress('Generating FAISS embeddings...');
      await fetchDocuments();
      setUploadProgress('');
    } catch (err) {
      alert(`Error uploading file: ${err.message}`);
      setUploadProgress('');
    } finally {
      setIsUploading(false);
    }
  };

  // Handle loading sample B.Tech curriculum
  const handleLoadSample = async () => {
    setIsUploading(true);
    setUploadProgress('Loading B.Tech CSE Curriculum (6 pages)...');

    try {
      const res = await fetch(`${API_BASE}/api/sample-curriculum`, {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to load sample curriculum');

      await fetchDocuments();
      setUploadProgress('');
    } catch (err) {
      alert(`Error loading sample curriculum: ${err.message}`);
      setUploadProgress('');
    } finally {
      setIsUploading(false);
    }
  };

  // Handle deleting a document
  const handleDeleteDocument = async (docId) => {
    if (!confirm('Are you sure you want to remove this document and its embeddings from the vector store?')) return;
    try {
      const res = await fetch(`${API_BASE}/api/documents/${docId}`, {
        method: 'DELETE',
      });
      if (res.ok) {
        await fetchDocuments();
      }
    } catch (err) {
      console.error('Failed to delete document:', err);
    }
  };

  // Handle sending a user question through RAG pipeline
  const handleSendMessage = async (questionText) => {
    if (!questionText || isLoading) return;

    // Append user message
    const userMsg = { role: 'user', content: questionText };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    // Dynamic loading stage sequence
    setLoadingStage('Searching curriculum with FAISS...');
    const stageTimer1 = setTimeout(() => {
      setLoadingStage('Applying metadata filters & ranking...');
    }, 450);
    const stageTimer2 = setTimeout(() => {
      setLoadingStage('Synthesizing grounded curriculum answer...');
    }, 900);

    try {
      const res = await fetch(`${API_BASE}/api/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: questionText,
          top_k: settings.top_k,
          provider: settings.llm_provider,
        }),
      });

      clearTimeout(stageTimer1);
      clearTimeout(stageTimer2);

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Query execution failed');
      }

      const data = await res.json();

      // Append AI response
      const aiMsg = {
        role: 'assistant',
        content: data.answer,
        sources: data.sources || [],
        retrieved_chunks: data.retrieved_chunks || [],
        detected_filters: data.detected_filters || {},
        not_found: data.not_found || false,
        latency: data.latency,
        provider_used: data.provider_used,
      };

      setMessages((prev) => [...prev, aiMsg]);
      setRetrievalData(data);
    } catch (err) {
      clearTimeout(stageTimer1);
      clearTimeout(stageTimer2);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `An error occurred while processing your question: ${err.message}. Please check your backend connection.`,
          not_found: true,
        },
      ]);
    } finally {
      setIsLoading(false);
      setLoadingStage('');
    }
  };

  // Handle citation click: highlight chunk and scroll in retrieval panel
  const handleSelectCitation = (src) => {
    if (src.chunk_id) {
      setHighlightedChunkId(src.chunk_id);
      setActiveMobileTab('retrieval');
      const el = document.getElementById(`chunk-${src.chunk_id}`);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  };

  // Handle settings update
  const handleSaveSettings = async (newSettings) => {
    try {
      const res = await fetch(`${API_BASE}/api/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newSettings),
      });
      if (res.ok) {
        const data = await res.json();
        setSettings(data.settings);
      }
    } catch (err) {
      console.error('Failed to save settings:', err);
    }
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#080c14] text-slate-100">
      {/* Top Header */}
      <Header
        stats={stats}
        settings={settings}
        onOpenSettings={() => setIsSettingsOpen(true)}
        onOpenHowItWorks={() => setIsHowItWorksOpen(true)}
        onClearChat={() => {
          setMessages([]);
          setRetrievalData(null);
        }}
        chatLength={messages.length}
      />

      {/* Mobile Tab Switcher */}
      <div className="lg:hidden flex border-b border-white/10 bg-slate-900/90 text-xs font-medium">
        <button
          onClick={() => setActiveMobileTab('docs')}
          className={`flex-1 py-2 text-center border-b-2 transition-all ${
            activeMobileTab === 'docs'
              ? 'border-indigo-500 text-indigo-400 font-semibold'
              : 'border-transparent text-slate-400'
          }`}
        >
          Documents ({stats.total_documents})
        </button>
        <button
          onClick={() => setActiveMobileTab('chat')}
          className={`flex-1 py-2 text-center border-b-2 transition-all ${
            activeMobileTab === 'chat'
              ? 'border-indigo-500 text-indigo-400 font-semibold'
              : 'border-transparent text-slate-400'
          }`}
        >
          AI Advisor
        </button>
        <button
          onClick={() => setActiveMobileTab('retrieval')}
          className={`flex-1 py-2 text-center border-b-2 transition-all ${
            activeMobileTab === 'retrieval'
              ? 'border-indigo-500 text-indigo-400 font-semibold'
              : 'border-transparent text-slate-400'
          }`}
        >
          Retrieval ({retrievalData?.retrieved_chunks?.length || 0})
        </button>
      </div>

      {/* Main 3-Part Experience Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel: Documents */}
        <div className={`h-full ${activeMobileTab === 'docs' ? 'block w-full' : 'hidden lg:block'}`}>
          <DocumentPanel
            documents={documents}
            stats={stats}
            isUploading={isUploading}
            uploadProgress={uploadProgress}
            onUploadFiles={handleUploadFiles}
            onLoadSample={handleLoadSample}
            onDeleteDocument={handleDeleteDocument}
          />
        </div>

        {/* Center Panel: AI Advisor Chat */}
        <div className={`flex-1 h-full ${activeMobileTab === 'chat' ? 'block' : 'hidden lg:block'}`}>
          <ChatPanel
            messages={messages}
            isLoading={isLoading}
            loadingStage={loadingStage}
            onSendMessage={handleSendMessage}
            onSelectCitation={handleSelectCitation}
            documentsCount={stats.total_documents}
            onLoadSample={handleLoadSample}
          />
        </div>

        {/* Right Panel: Retrieval Inspector */}
        <div className={`h-full ${activeMobileTab === 'retrieval' ? 'block w-full' : 'hidden lg:block'}`}>
          <RetrievalPanel
            retrievalData={retrievalData}
            highlightedChunkId={highlightedChunkId}
            onCloseMobile={() => setActiveMobileTab('chat')}
          />
        </div>
      </div>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        settings={settings}
        onSaveSettings={handleSaveSettings}
      />

      {/* How It Works Visual Pipeline Modal */}
      <HowItWorksModal
        isOpen={isHowItWorksOpen}
        onClose={() => setIsHowItWorksOpen(false)}
      />
    </div>
  );
}
