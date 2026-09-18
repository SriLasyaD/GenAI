import time
import uuid
from typing import Dict, Any, List, Optional
from pathlib import Path

from app.rag.pdf_extractor import PDFExtractor
from app.rag.chunker import PageAwareChunker
from app.rag.metadata_extractor import MetadataExtractor
from app.rag.embedder import Embedder
from app.rag.vector_store import FAISSVectorStore
from app.rag.retriever import MetadataAwareRetriever
from app.rag.llm_service import LLMService
from app.config import settings, UPLOADS_DIR, SAMPLE_DIR


class RAGPipeline:
    def __init__(self):
        self.embedder = Embedder.get_instance(settings.embedding_model)
        self.vector_store = FAISSVectorStore(dimension=384)
        self.retriever = MetadataAwareRetriever(self.vector_store, self.embedder)
        self.llm_service = LLMService()
        self.chunker = PageAwareChunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
        self.processed_documents: Dict[str, Dict[str, Any]] = {}

    def process_pdf(self, pdf_path: str | Path, doc_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Full ingestion pipeline:
        PDF -> Page Text -> Page-aware Chunks -> Metadata Enrichment -> Embeddings -> FAISS
        """
        start_time = time.time()
        path = Path(pdf_path)
        if not doc_id:
            doc_id = str(uuid.uuid4())[:8]

        # 1. PDF Extraction
        extract_start = time.time()
        pages = PDFExtractor.extract_pages(path)
        extract_time = time.time() - extract_start

        if not pages:
            raise ValueError(f"No readable text could be extracted from PDF: {path.name}")

        # 2. Chunking
        chunk_start = time.time()
        raw_chunks = self.chunker.chunk_document(pages, doc_id=doc_id)
        chunk_time = time.time() - chunk_start

        # 3. Metadata Extraction
        meta_start = time.time()
        enriched_chunks = [MetadataExtractor.enrich_chunk(c) for c in raw_chunks]
        meta_time = time.time() - meta_start

        # 4. Embeddings
        embed_start = time.time()
        texts = [c["text"] for c in enriched_chunks]
        embeddings = self.embedder.embed_texts(texts)
        embed_time = time.time() - embed_start

        # 5. Index into FAISS
        index_start = time.time()
        self.vector_store.add_chunks(enriched_chunks, embeddings)
        index_time = time.time() - index_start

        total_time = time.time() - start_time

        doc_summary = {
            "doc_id": doc_id,
            "filename": path.name,
            "filepath": str(path),
            "total_pages": len(pages),
            "chunks_count": len(enriched_chunks),
            "status": "Indexed",
            "ingestion_metrics": {
                "extract_sec": round(extract_time, 3),
                "chunk_sec": round(chunk_time, 3),
                "metadata_sec": round(meta_time, 3),
                "embed_sec": round(embed_time, 3),
                "index_sec": round(index_time, 3),
                "total_sec": round(total_time, 3),
            }
        }
        self.processed_documents[doc_id] = doc_summary
        return doc_summary

    def query(
        self,
        question: str,
        top_k: Optional[int] = None,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes query through the metadata-aware RAG pipeline.
        """
        start_time = time.time()
        k = top_k or settings.top_k

        # 1. Retrieval
        retrieve_start = time.time()
        retrieval_result = self.retriever.retrieve(query=question, top_k=k)
        retrieve_time = time.time() - retrieve_start

        retrieved_chunks = retrieval_result["chunks"]
        detected_filters = retrieval_result["detected_filters"]

        # 2. LLM Generation
        llm_start = time.time()
        llm_output = self.llm_service.generate_answer(
            question=question,
            retrieved_chunks=retrieved_chunks,
            provider=provider,
            api_key=api_key,
            model_name=model_name
        )
        llm_time = time.time() - llm_start

        total_latency = time.time() - start_time

        # Prepare sanitized chunks for frontend retrieval inspector
        chunks_display = []
        for c in retrieved_chunks:
            chunks_display.append({
                "chunk_id": c.get("chunk_id"),
                "filename": c.get("filename"),
                "page_number": c.get("page_number"),
                "text": c.get("text"),
                "similarity_score": c.get("similarity_score"),
                "combined_score": c.get("combined_score"),
                "metadata": c.get("metadata", {}),
                "metadata_matches": c.get("metadata_matches", {}),
            })

        return {
            "question": question,
            "answer": llm_output["answer"],
            "sources": llm_output["sources"],
            "retrieved_chunks": chunks_display,
            "detected_filters": detected_filters,
            "provider_used": llm_output["provider_used"],
            "not_found": llm_output["not_found"],
            "latency": {
                "retrieve_sec": round(retrieve_time, 3),
                "llm_sec": round(llm_time, 3),
                "total_sec": round(total_latency, 3),
            }
        }

    def delete_document(self, doc_id: str) -> bool:
        if doc_id in self.processed_documents:
            self.vector_store.remove_document(doc_id, embedder=self.embedder)
            del self.processed_documents[doc_id]
            return True
        return False

    def get_stats(self) -> Dict[str, Any]:
        store_stats = self.vector_store.get_document_stats()
        return {
            "total_documents": store_stats["total_documents"],
            "total_pages": store_stats["total_pages"],
            "total_chunks": store_stats["total_chunks"],
            "courses_count": store_stats["courses_count"],
            "courses_detected": store_stats["courses_detected"],
            "semesters_count": store_stats["semesters_count"],
            "semesters_detected": store_stats["semesters_detected"],
            "course_types_detected": store_stats["course_types_detected"],
            "documents": store_stats["documents"],
            "embedding_model": settings.embedding_model,
            "active_llm_provider": settings.llm_provider,
        }


# Singleton pipeline instance
rag_pipeline = RAGPipeline()
