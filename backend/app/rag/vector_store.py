import faiss
import numpy as np
from typing import List, Dict, Any, Tuple
import threading
import json
from pathlib import Path


class FAISSVectorStore:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)  # Inner product on normalized vectors = Cosine similarity
        self.chunks: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: np.ndarray):
        """
        Adds document chunks and their corresponding embedding vectors to the FAISS index.
        """
        if len(chunks) == 0:
            return

        if embeddings.shape[0] != len(chunks):
            raise ValueError(f"Mismatch: {embeddings.shape[0]} embeddings for {len(chunks)} chunks.")

        if embeddings.shape[1] != self.dimension:
            raise ValueError(f"Expected embedding dimension {self.dimension}, got {embeddings.shape[1]}")

        with self._lock:
            self.index.add(embeddings)
            self.chunks.extend(chunks)

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """
        Searches the FAISS index using cosine similarity.
        Returns list of (chunk_dict, cosine_score) sorted by score descending.
        """
        with self._lock:
            total_items = self.index.ntotal
            if total_items == 0:
                return []

            actual_k = min(top_k, total_items)
            distances, indices = self.index.search(query_embedding, actual_k)

            results = []
            for score, idx in zip(distances[0], indices[0]):
                if idx != -1 and idx < len(self.chunks):
                    chunk = self.chunks[idx]
                    results.append((chunk, float(score)))

            return results

    def remove_document(self, doc_id: str, embedder=None) -> int:
        """
        Removes all chunks belonging to a document and rebuilds the FAISS index.
        """
        with self._lock:
            kept_chunks = [c for c in self.chunks if c.get("doc_id") != doc_id]
            removed_count = len(self.chunks) - len(kept_chunks)
            if removed_count == 0:
                return 0

            # Rebuild index with kept chunks
            new_index = faiss.IndexFlatIP(self.dimension)
            if kept_chunks and embedder:
                texts = [c["text"] for c in kept_chunks]
                new_embeddings = embedder.embed_texts(texts)
                new_index.add(new_embeddings)

            self.index = new_index
            self.chunks = kept_chunks
            return removed_count

    def clear(self):
        with self._lock:
            self.index = faiss.IndexFlatIP(self.dimension)
            self.chunks = []

    def get_document_stats(self) -> Dict[str, Any]:
        """
        Returns real-time curriculum statistics strictly computed from actual chunk metadata.
        Zero hardcoded or fake statistics.
        """
        with self._lock:
            docs_summary = {}
            unique_courses = set()
            unique_semesters = set()
            unique_types = set()
            total_unique_pages = set()

            for chunk in self.chunks:
                d_id = chunk["doc_id"]
                fname = chunk["filename"]
                p_num = chunk["page_number"]
                total_unique_pages.add((d_id, p_num))

                if d_id not in docs_summary:
                    docs_summary[d_id] = {
                        "doc_id": d_id,
                        "filename": fname,
                        "pages": set(),
                        "chunks_count": 0,
                    }
                docs_summary[d_id]["pages"].add(p_num)
                docs_summary[d_id]["chunks_count"] += 1

                # Collect real metadata from chunk
                meta = chunk.get("metadata", {})
                for code in meta.get("course_codes", []):
                    if code:
                        unique_courses.add(code)
                if meta.get("semester") is not None:
                    unique_semesters.add(meta["semester"])
                if meta.get("course_type"):
                    unique_types.add(meta["course_type"])

            doc_list = []
            for d_id, data in docs_summary.items():
                doc_list.append({
                    "doc_id": d_id,
                    "filename": data["filename"],
                    "total_pages": len(data["pages"]),
                    "chunks_count": data["chunks_count"],
                    "status": "Indexed in FAISS",
                })

            sorted_courses = sorted(list(unique_courses))
            sorted_semesters = sorted(list(unique_semesters))

            return {
                "total_documents": len(doc_list),
                "total_pages": len(total_unique_pages),
                "total_chunks": len(self.chunks),
                "courses_count": len(sorted_courses),
                "courses_detected": sorted_courses,
                "semesters_count": len(sorted_semesters),
                "semesters_detected": sorted_semesters,
                "course_types_detected": sorted(list(unique_types)),
                "documents": doc_list
            }
