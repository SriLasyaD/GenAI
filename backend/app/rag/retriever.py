import re
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from app.rag.metadata_extractor import MetadataExtractor
from app.rag.vector_store import FAISSVectorStore
from app.rag.embedder import Embedder


class MetadataAwareRetriever:
    def __init__(self, vector_store: FAISSVectorStore, embedder: Embedder):
        self.vector_store = vector_store
        self.embedder = embedder

    def extract_query_filters(self, query: str) -> Dict[str, Any]:
        """
        Extracts intentional filters and course targets from the user query.
        Understands natural variations:
        'third semester subjects', 'semester 3 courses', 'what do I study in sem 3?', etc.
        """
        filters: Dict[str, Any] = {}

        # 1. Semester filter
        sem = MetadataExtractor.extract_semester(query)
        if sem is not None:
            filters["semester"] = sem

        # 2. Credits filter
        cred = MetadataExtractor.extract_credits(query)
        if cred is not None:
            filters["credits"] = cred

        # 3. Course type filter
        ctype = MetadataExtractor.extract_course_type(query)
        if ctype is not None:
            filters["course_type"] = ctype
        elif re.search(r'\belective(s)?\b', query, re.IGNORECASE):
            filters["course_type"] = "Elective"

        # 4. Course code filter
        codes = MetadataExtractor.extract_course_codes(query)
        if codes:
            filters["course_codes"] = codes

        # 5. Course names mentioned in query
        c_names = MetadataExtractor.extract_course_names(query)
        if c_names:
            filters["course_names"] = c_names

        # 6. Prerequisite flag
        if any(p in query.lower() for p in ["prerequisite", "prereq", "pre-requisite"]):
            filters["prerequisite_query"] = True

        return filters

    def retrieve(self, query: str, top_k: int = 4) -> Dict[str, Any]:
        """
        RAG Retrieval Workflow:
        Query -> determine useful metadata filters -> semantic search -> retrieve relevant chunks -> construct context -> LLM.
        
        Guarantees:
        - NEVER prematurely eliminates relevant chunks (safe hybrid reranking).
        - High-confidence metadata matches are boosted.
        - Chunks without metadata are still retained by semantic score.
        """
        query_embedding = self.embedder.embed_query(query)
        detected_filters = self.extract_query_filters(query)

        total_chunks = len(self.vector_store.chunks)
        if total_chunks == 0:
            return {
                "chunks": [],
                "detected_filters": detected_filters,
                "total_available_chunks": 0,
            }

        # Step 1: Broad Semantic Candidate Pool via FAISS
        candidate_k = min(max(top_k * 4, 16), total_chunks)
        raw_results = self.vector_store.search(query_embedding, top_k=candidate_k)

        scored_candidates: Dict[str, Dict[str, Any]] = {}

        for chunk, score in raw_results:
            c_id = chunk["chunk_id"]
            scored_candidates[c_id] = {
                "chunk": chunk,
                "semantic_score": score,
                "combined_score": score,
                "metadata_matches": {},
            }

        # Step 2: Inject any chunks matching explicit metadata filters if not already in candidate pool
        target_sem = detected_filters.get("semester")
        target_ctype = detected_filters.get("course_type")
        target_codes = detected_filters.get("course_codes", [])
        target_cnames = detected_filters.get("course_names", [])

        if target_sem is not None or target_ctype is not None or target_codes or target_cnames:
            for chunk in self.vector_store.chunks:
                c_id = chunk["chunk_id"]
                meta = chunk.get("metadata", {})

                matches_filter = False
                if target_sem is not None and meta.get("semester") == target_sem:
                    matches_filter = True
                if target_codes and any(c in meta.get("course_codes", []) for c in target_codes):
                    matches_filter = True
                if target_cnames and any(
                    any(tn.lower() in cn.lower() for tn in target_cnames) 
                    for cn in meta.get("course_names", [])
                ):
                    matches_filter = True
                if target_ctype is not None and meta.get("course_type"):
                    if target_ctype.lower() in meta["course_type"].lower():
                        matches_filter = True

                if matches_filter and c_id not in scored_candidates:
                    chunk_text = chunk["text"]
                    chunk_vec = self.embedder.embed_texts([chunk_text])
                    sim = float(np.dot(query_embedding, chunk_vec.T)[0][0])
                    scored_candidates[c_id] = {
                        "chunk": chunk,
                        "semantic_score": sim,
                        "combined_score": sim,
                        "metadata_matches": {},
                    }

        # Step 3: Metadata Boost & Multi-Course Balance
        q_lower = query.lower()

        for c_id, item in scored_candidates.items():
            meta = item["chunk"].get("metadata", {})
            text_lower = item["chunk"]["text"].lower()
            boost = 0.0

            # Semester match boost
            if target_sem is not None and meta.get("semester") == target_sem:
                boost += 0.35
                item["metadata_matches"]["semester"] = target_sem

            # Course codes match boost
            if target_codes:
                matched_codes = [c for c in target_codes if c in meta.get("course_codes", [])]
                if matched_codes:
                    boost += 0.40
                    item["metadata_matches"]["course_code"] = matched_codes

            # Course name match boost
            if target_cnames:
                for target_name in target_cnames:
                    if target_name.lower() in text_lower or any(
                        target_name.lower() in cn.lower() for cn in meta.get("course_names", [])
                    ):
                        boost += 0.35
                        item["metadata_matches"]["course_name"] = target_name

            # Course type boost
            if target_ctype is not None and meta.get("course_type"):
                if target_ctype.lower() in meta["course_type"].lower() or (
                    target_ctype.lower() == "elective" and "elective" in meta["course_type"].lower()
                ):
                    boost += 0.30
                    item["metadata_matches"]["course_type"] = meta["course_type"]

            # Prerequisite boost
            if detected_filters.get("prerequisite_query") and meta.get("prerequisites"):
                if meta["prerequisites"] != "None":
                    boost += 0.25
                    item["metadata_matches"]["prerequisite"] = meta["prerequisites"]

            # Credits boost
            target_cred = detected_filters.get("credits")
            if target_cred is not None and meta.get("credits") == target_cred:
                boost += 0.25
                item["metadata_matches"]["credits"] = target_cred

            item["combined_score"] = item["semantic_score"] + boost

        # Step 4: Sort candidates by combined score descending
        sorted_items = sorted(
            scored_candidates.values(),
            key=lambda x: x["combined_score"],
            reverse=True
        )

        final_chunks = []
        for item in sorted_items[:top_k]:
            chunk_copy = dict(item["chunk"])
            chunk_copy["similarity_score"] = round(item["semantic_score"], 4)
            chunk_copy["combined_score"] = round(item["combined_score"], 4)
            chunk_copy["metadata_matches"] = item["metadata_matches"]
            final_chunks.append(chunk_copy)

        return {
            "chunks": final_chunks,
            "detected_filters": detected_filters,
            "total_available_chunks": total_chunks,
        }
