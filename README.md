# CourseGuide AI — College Course Advisor

A production-grade, metadata-aware **Retrieval-Augmented Generation (RAG)** application designed for universities and engineering colleges. **CourseGuide AI** enables students, faculty, and academic advisors to upload official college curriculum PDFs and ask natural-language questions about courses, semesters, credits, prerequisites, and degree requirements with guaranteed contextual grounding and verified source citations.

---

## Table of Contents
1. [Problem Statement](#problem-statement)
2. [Key Features](#key-features)
3. [System Architecture](#system-architecture)
4. [Technology Stack](#technology-stack)
5. [Complete RAG Workflow](#complete-rag-workflow)
6. [Page-Aware Chunking & Table Preservation](#page-aware-chunking--table-preservation)
7. [Dense Embeddings & Normalization](#dense-embeddings--normalization)
8. [FAISS Vector Database Indexing](#faiss-vector-database-indexing)
9. [Metadata-Aware Retrieval Pipeline](#metadata-aware-retrieval-pipeline)
10. [Grounding & Hallucination Prevention Guardrails](#grounding--hallucination-prevention-guardrails)
11. [Source Citations & RAG Transparency](#source-citations--rag-transparency)
12. [Installation Guide](#installation-guide)
13. [Running the Application](#running-the-application)
14. [Example Viva & Demonstration Questions](#example-viva--demonstration-questions)
15. [Known Limitations & Future Scope](#known-limitations--future-scope)

---

## Problem Statement

Navigating college curriculum documents is challenging:
* Syllabi are typically distributed as dense, multi-page PDFs (often 50–200 pages long) containing semester structures, tabular course codes, lab requirements, and complex prerequisite chains.
* Students frequently miss critical prerequisites or misunderstand credit allocations.
* Standard LLM chatbots (e.g. raw ChatGPT) hallucinate course codes, guess degree credits, or invent curriculum policies because they lack localized, authoritative context.
* Traditional full-text search (Ctrl+F) fails when queries are semantic (e.g., *"Which courses teach neural networks?"* or *"What are the electives in year three?"*).

**CourseGuide AI** solves this by enforcing an end-to-end, metadata-aware RAG pipeline that grounds every answer strictly in uploaded university PDFs.

---

## Key Features

- **Multi-PDF Ingestion**: Upload multiple official syllabi (e.g., *B.Tech CSE Curriculum*, *Academic Regulations*, *Department Elective Baskets*).
- **Tabular Atomicity Preservation**: Extracts table rows using PyMuPDF `find_tables()` so course codes, titles, credits, and prerequisites stay together.
- **Dynamic Curriculum Statistics**: Automatically counts and displays documents, pages, vector chunks, unique course codes detected, and active semesters calculated directly from the vector store.
- **"How It Works" 10-Step Visual Modal**: A clear diagrammatic breakdown of the RAG architecture for viva examiners and college project presentations.
- **"Why This Answer?" Transparency**: An expandable audit drawer for every answer showing the retrieved chunks, document name, page number, detected metadata filters, and cosine similarity match scores.
- **Categorized Quick Questions**: Pre-configured query categories (*Semester*, *Courses*, *Curriculum*) that execute real queries with one click.
- **Structured Markdown Tables**: Automatically formats course listings into readable tables:
  ```markdown
  | Course Code | Course Name | Type | Credits |
  |-------------|-------------|------|---------|
  | CS301       | Database Management Systems | Core | 4 |
  ```
- **Strict Grounding Guardrail**: If an inquiry asks about something not present in the documents (e.g. non-existent hostel fees or unlisted attendance rules), the system explicitly refuses to guess.
- **Zero API Key Leakage**: LLM keys remain securely on the backend server; frontend code exposes 0 credentials.

---

## System Architecture

```
                                  +-------------------------------------------------+
                                  |            Client Browser (React + Vite)        |
                                  |  - 3-Panel Layout (Documents, Chat, Inspector)  |
                                  |  - "How It Works" Modal & "Why This Answer?"    |
                                  +-----------------------+-------------------------+
                                                          | HTTP REST (Port 8000)
                                                          v
                                  +-------------------------------------------------+
                                  |           FastAPI Application Server            |
                                  +-----------------------+-------------------------+
                                                          |
                 +----------------------------------------+---------------------------------------+
                 | Ingestion Pipeline                                                             | Query Pipeline
                 v                                                                                v
  +-------------------------------+                                              +-------------------------------+
  |        PyMuPDF Extractor      |                                              |  Query Intent & Filter Parser |
  | (find_tables + text blocks)   |                                              | (Semester, Code, Credits)     |
  +---------------+---------------+                                              +---------------+---------------+
                  |                                                                              |
                  v                                                                              v
  +-------------------------------+                                              +-------------------------------+
  |      PageAwareChunker         |                                              |      SentenceTransformers     |
  | (500 chars, 100 overlap)      |                                              |  Query Embedding (384-dim)    |
  +---------------+---------------+                                              +---------------+---------------+
                  |                                                                              |
                  v                                                                              v
  +-------------------------------+                                              +-------------------------------+
  |   Metadata Extraction Engine  |                                              |     FAISS Dense Retrieval     |
  | (Course codes, credits, sem)  |                                              |   (IndexFlatIP Cosine Search) |
  +---------------+---------------+                                              +---------------+---------------+
                  |                                                                              |
                  v                                                                              v
  +-------------------------------+                                              +-------------------------------+
  |      SentenceTransformers     |                                              |  Metadata Filter Re-ranking   |
  |  (all-MiniLM-L6-v2, 384-dim)  |                                              |  (Boost matching semester/id) |
  +---------------+---------------+                                              +---------------+---------------+
                  |                                                                              |
                  v                                                                              v
  +-------------------------------+                                              +-------------------------------+
  |      FAISS Vector Store       |=============================================>| Grounded LLM Context Builder  |
  |   (Cosine similarity index)   |                                              |  (Atomic Context + Boundaries)|
  +-------------------------------+                                              +---------------+---------------+
                                                                                                 |
                                                                                                 v
                                                                                 +-------------------------------+
                                                                                 |     Groq AI Engine            |
                                                                                 |  (Strict Grounding Prompt)    |
                                                                                 +---------------+---------------+
                                                                                                 |
                                                                                                 v
                                                                                 +-------------------------------+
                                                                                 | Grounded Answer + Citations   |
                                                                                 |  (Document, Page, Table, Why) |
                                                                                 +-------------------------------+
```

---

## Technology Stack

| Layer | Component | Technology / Library | Purpose |
|---|---|---|---|
| **Frontend** | UI Framework | React 19 + Vite | High-performance reactive user interface |
| **Frontend** | Styling & Icons | Vanilla Tailwind CSS v4 + Lucide React | Modern dark aesthetic, glassmorphic panels, and icons |
| **Backend** | Web Framework | FastAPI + Uvicorn | High-throughput asynchronous Python REST API |
| **Document Processing** | PDF Parsing | PyMuPDF (`fitz`) | High-speed text extraction and layout table extraction |
| **Chunking** | Text Splitter | Custom `PageAwareChunker` | Page boundary retention, sliding window, and row preservation |
| **Metadata** | Attribute Extraction | Custom `MetadataExtractor` | Regex and heuristic parsing of semesters, course codes, and credits |
| **Embeddings** | Dense Vector Model | `sentence-transformers/all-MiniLM-L6-v2` | 384-dimensional dense vectors with L2 unit normalization |
| **Vector DB** | Vector Search | FAISS (`faiss-cpu`) | In-memory `IndexFlatIP` calculating exact cosine similarities |
| **LLM Engine** | Generative Reasoning | Groq API (`groq/compound-mini`) | Sub-second inference speed with grounding prompt guardrail |

---

## Complete RAG Workflow

1. **Upload**: User uploads a university syllabus PDF.
2. **Text & Table Extraction**: PyMuPDF extracts page text and identifies structured course matrices (`find_tables`).
3. **Page-Aware Chunking**: Text is split into chunks of ~500 characters with 100 character overlap, strictly retaining page numbers.
4. **Metadata Enrichment**: Each chunk is annotated with:
   - `document`: Filename
   - `page`: Page number
   - `course_codes`: e.g. `['CS301', 'CS102']`
   - `semester`: e.g. `3`
   - `credits`: e.g. `4.0`
   - `prerequisites`: e.g. `'CS102 (Data Structures)'`
   - `course_type`: e.g. `'Core'` or `'Lab'`
5. **Embedding Generation**: Chunks are encoded via `all-MiniLM-L6-v2` into 384-dimensional dense vectors.
6. **FAISS Indexing**: Normalized vectors are added to a FAISS `IndexFlatIP` index.
7. **Query Processing**: When a student asks a question:
   - The query intent is analyzed for metadata filters (e.g. *Semester 3*).
   - The query is embedded into a dense vector.
8. **Hybrid Retrieval**: Top-$K$ semantic matches from FAISS are retrieved and combined with metadata boost scoring.
9. **Context Assembly**: Retrieved chunks are ordered and formatted with page citation headers.
10. **Grounded Generation**: Groq LLM synthesizes an answer strictly from the retrieved chunks with document and page citations. If ungrounded, it returns an explicit refusal.

---

## Page-Aware Chunking & Table Preservation

Standard chunkers slice text arbitrarily, splitting a course code from its credits or cutting a table row in half. **CourseGuide AI** implements two safeguards:
1. **Row Atomicity**: Tabular lines formatted as `Course Code | Course Name | Type | Prerequisite | Credits` are never split across chunks.
2. **Header Propagation**: If a semester table spans across chunks, the semester header (e.g., `Semester 3 Course Structure`) is propagated to subsequent chunks so context is never lost.

---

## Dense Embeddings & Normalization

We use the lightweight, high-performance `all-MiniLM-L6-v2` model:
* **Dimensions**: 384
* **Normalization**: All chunk and query vectors are $L_2$-normalized:
  $$\hat{\mathbf{v}} = \frac{\mathbf{v}}{\|\mathbf{v}\|_2}$$
* **Mathematical Property**: For unit vectors, inner product equals cosine similarity:
  $$\mathbf{u} \cdot \mathbf{v} = \cos(\theta)$$
  This allows FAISS `IndexFlatIP` (Inner Product) to compute exact cosine similarities in microseconds.

---

## FAISS Vector Database Indexing

* Uses `faiss.IndexFlatIP(384)`.
* Zero quantization loss (exact search).
* Thread-safe updates using Python `threading.Lock`.
* Supports dynamic multi-document indexing, removal, and incremental ingestion.

---

## Metadata-Aware Retrieval Pipeline

When a user asks:
> *"What subjects are available in the third semester?"*

1. **Intent Analysis**: The system extracts metadata filter `{'semester': 3}`.
2. **Dense Vector Search**: FAISS retrieves candidates with high semantic similarity.
3. **Re-Ranking & Boosting**: Candidates whose chunk metadata matches `semester: 3` receive an additive relevance boost:
   $$\text{Score}_{\text{combined}} = \text{Score}_{\text{cosine}} + 0.35 \times \mathbb{I}_{\text{semester\_match}}$$
4. Chunks from other semesters are deprioritized, eliminating cross-semester contamination.

---

## Grounding & Hallucination Prevention Guardrails

To ensure academic reliability, CourseGuide AI enforces strict grounding:
1. **System Prompt Constraint**: The LLM is instructed: *"If the answer cannot be found or verified in the provided context, you MUST state exactly: 'I couldn't find this information in the uploaded curriculum documents.' Never guess or invent."*
2. **Temperature Control**: Temperature is locked at `0.1` to enforce deterministic, factual output.
3. **Precision Fallback**: If an ungrounded question (e.g. non-existent attendance rules or hostel fees) is submitted, the system returns a verified refusal with 0 cited sources.

---

## Source Citations & RAG Transparency

* **Clickable Document & Page Badges**: Answers include badges linking directly to `Document Name` and `Page X`.
* **"Why This Answer?" Drawer**: Users can expand any answer to view:
  - Total chunks retrieved and analyzed
  - Detected metadata filters applied
  - Cosine relevance match percentage
  - Raw context excerpt toggle for verification

---

## Installation Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Clone or Open Project Directory
```bash
cd "College course advisor"
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows PowerShell:
venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Backend Environment Configuration
Create or verify `backend/.env`:
```env
GROQ_API_KEY=your_groq_api_key_here
LLM_PROVIDER=groq
GROQ_MODEL=groq/compound-mini
```

### 4. Frontend Setup
```bash
cd ../frontend
npm install
```

---

## Running the Application

### Start Backend API Server
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
*API Swagger Documentation is available at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)*

### Start Frontend Dev Server
In a separate terminal:
```bash
cd frontend
npm run dev -- --host 127.0.0.1
```
*Web Application is accessible at: [http://127.0.0.1:5173/](http://127.0.0.1:5173/)*

---

## Example Viva & Demonstration Questions

Use these queries during presentations to demonstrate different capabilities:

| Category | Example Question | Expected Demonstration Behavior |
|---|---|---|
| **Semester Structure** | *"What subjects are available in semester 3?"* | Triggers `Semester: 3` metadata filter; returns table with `CS301`, `CS202`, `MA201`, credits, and citations to Page 3. |
| **Credits** | *"What are the credits for Database Management Systems?"* | Returns exact credit value (`4 Credits`) with citation to Page 3 and Page 6. |
| **Prerequisites** | *"Which courses have programming prerequisites?"* | Returns list of courses requiring `CS101` or `CS102` with prerequisites clearly marked. |
| **Course Code** | *"What is the course code of Database Management Systems?"* | Returns `CS301` with official syllabus citation. |
| **Semester Structure** | *"What subjects are available in semester 6?"* | Returns `CS306` (Compiler Design), `CS307` (Web Tech), `CS308P`, and electives with citations to Page 4. |
| **Ungrounded Refusal** | *"What is the attendance requirement for a rule that is NOT present in the uploaded curriculum?"* | **Strict Refusal**: Returns *"I couldn't find this information in the uploaded curriculum documents."* with zero hallucinated sources. |

---

## Known Limitations & Future Scope

In the spirit of honest academic engineering, here are the real system boundaries:

1. **Scanned Image PDFs (OCR)**: Currently, the system relies on native PDF text and vector table extraction via PyMuPDF. Scanned image-only PDFs without an OCR layer require pre-processing with Tesseract or `pdf2image`.
2. **In-Memory FAISS Index**: The vector store runs in RAM using `IndexFlatIP`. While ideal for syllabi (tens of thousands of chunks), scaling to campus-wide libraries with millions of documents would benefit from persistent vector databases (such as Milvus, Qdrant, or pgvector) with IVF-PQ clustering.
3. **Complex Nested Multi-Column Spans**: Unusually formatted PDFs with irregular nested sub-tables can occasionally have merged column headers; PyMuPDF's table detection handles standard grids best.
4. **Groq Free Tier Rate Limits**: On free Groq API tiers, running multiple high-token queries in rapid succession (< 2 seconds) may hit rate limits; the system includes an offline precision guardrail fallback to guarantee zero crashes.
