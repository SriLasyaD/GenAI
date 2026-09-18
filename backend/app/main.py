import os
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import settings, UPLOADS_DIR, SAMPLE_DIR
from app.rag.pipeline import rag_pipeline
from app.sample_data.generator import generate_sample_curriculum_pdf

app = FastAPI(
    title="CourseGuide AI API",
    description="College Course Advisor RAG Pipeline API",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = None
    provider: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = None


class SettingsUpdateRequest(BaseModel):
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    top_k: Optional[int] = None
    llm_provider: Optional[str] = None
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    gemini_model: Optional[str] = None
    openai_model: Optional[str] = None


@app.on_event("startup")
def on_startup():
    # Ensure sample curriculum PDF exists
    sample_pdf = SAMPLE_DIR / "B.Tech_CSE_Curriculum_2024-2028.pdf"
    if not sample_pdf.exists():
        try:
            generate_sample_curriculum_pdf(sample_pdf)
        except Exception as e:
            print(f"Warning generating sample PDF: {e}")


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CourseGuide AI RAG API",
        "total_documents_indexed": len(rag_pipeline.processed_documents),
        "total_chunks_indexed": len(rag_pipeline.vector_store.chunks),
        "embedding_model": settings.embedding_model,
        "llm_provider": settings.llm_provider,
    }


@app.get("/api/documents")
def list_documents():
    return rag_pipeline.get_stats()


@app.post("/api/upload")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    results = []
    errors = []

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            errors.append(f"{file.filename}: Only PDF files are supported.")
            continue

        try:
            # Save uploaded file
            save_path = UPLOADS_DIR / file.filename
            with open(save_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Ingest into RAG pipeline
            doc_summary = rag_pipeline.process_pdf(save_path)
            results.append(doc_summary)
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")

    return {
        "uploaded_count": len(results),
        "documents": results,
        "errors": errors,
        "total_indexed": rag_pipeline.get_stats(),
    }


@app.post("/api/sample-curriculum")
def load_sample_curriculum():
    sample_pdf = SAMPLE_DIR / "B.Tech_CSE_Curriculum_2024-2028.pdf"
    if not sample_pdf.exists():
        generate_sample_curriculum_pdf(sample_pdf)

    # Ingest sample PDF
    doc_summary = rag_pipeline.process_pdf(sample_pdf, doc_id="sample_cse_2024")
    return {
        "message": "Sample B.Tech CSE Curriculum successfully loaded & indexed.",
        "document": doc_summary,
        "stats": rag_pipeline.get_stats()
    }


@app.delete("/api/documents/{doc_id}")
def delete_document(doc_id: str):
    success = rag_pipeline.delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"message": "Document removed successfully", "doc_id": doc_id, "stats": rag_pipeline.get_stats()}


@app.post("/api/query")
def ask_question(payload: QueryRequest):
    if not payload.question or not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    result = rag_pipeline.query(
        question=payload.question.strip(),
        top_k=payload.top_k,
        provider=payload.provider,
        api_key=payload.api_key,
        model_name=payload.model_name
    )
    return result


@app.get("/api/settings")
def get_settings():
    return {
        "chunk_size": settings.chunk_size,
        "chunk_overlap": settings.chunk_overlap,
        "top_k": settings.top_k,
        "llm_provider": "groq",
        "has_groq_key": bool(settings.groq_api_key or os.getenv("GROQ_API_KEY")),
        "groq_model": settings.groq_model,
        "embedding_model": settings.embedding_model,
    }


@app.post("/api/settings")
def update_settings(payload: SettingsUpdateRequest):
    if payload.chunk_size is not None:
        settings.chunk_size = payload.chunk_size
        rag_pipeline.chunker.chunk_size = payload.chunk_size
    if payload.chunk_overlap is not None:
        settings.chunk_overlap = payload.chunk_overlap
        rag_pipeline.chunker.chunk_overlap = payload.chunk_overlap
    if payload.top_k is not None:
        settings.top_k = payload.top_k
    if payload.groq_api_key is not None:
        settings.groq_api_key = payload.groq_api_key

    return {"message": "Settings updated successfully", "settings": get_settings()}


# Serve production frontend if built (e.g. for unified Render deployment)
from fastapi.staticfiles import StaticFiles
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="static")
else:
    @app.get("/")
    def root():
        return {
            "app": "CourseGuide AI API",
            "status": "online",
            "version": "1.0.0",
            "docs_url": "/docs"
        }
