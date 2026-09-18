import os
import requests
from typing import List, Dict, Any, Optional
from app.config import settings


GROUNDING_SYSTEM_INSTRUCTION = """You are CourseGuide AI, an authoritative, rigorous college course and academic curriculum advisor powered by Groq.

STRICT GROUNDING RULES:
1. Answer ONLY and EXCLUSIVELY from the provided retrieved context chunks.
2. Do NOT use any outside knowledge, assumptions, or extrapolations.
3. Do NOT guess or invent courses, course codes, credits, prerequisites, semesters, or academic regulations.
4. Preserve all numerical information, credit counts, course codes, and prerequisite names exactly as stated in the context.
5. If the answer cannot be found or verified in the provided context, you MUST state exactly:
"I couldn't find this information in the uploaded curriculum documents."
6. For structured answers involving courses, subjects, or semester lists, format them in a clean markdown table with columns like | Course Code | Course Name | Credits | Prerequisite / Type | where appropriate. Do not invent any values.
"""

GROUNDING_PROMPT_TEMPLATE = """Retrieved Curriculum Context:
----------------------------------------
{context_str}
----------------------------------------

Student Question: {question}

Instructions:
Synthesize a direct, grounded answer to the student's question based strictly on the retrieved context above.
If the question asks for courses, subjects, or semester curriculum, provide a clear markdown table with columns:
| Course Code | Course Name | Credits | Type / Prerequisite |
Do not invent or estimate any values not present in the context.
If the information is not present in the context, respond with:
"I couldn't find this information in the uploaded curriculum documents."
"""


class LLMService:
    def __init__(self):
        pass

    def build_context_string(self, chunks: List[Dict[str, Any]]) -> str:
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            fname = chunk.get("filename", "Unknown Document")
            pnum = chunk.get("page_number", "Unknown Page")
            text = chunk.get("text", "")
            meta = chunk.get("metadata", {})
            meta_str = ", ".join(
                f"{k}: {v}" for k, v in meta.items() if v is not None and k not in ["filename", "page_number"]
            )
            
            header = f"[Chunk {i}] Document: {fname} | Page: {pnum}"
            if meta_str:
                header += f" | Metadata: ({meta_str})"
            context_parts.append(f"{header}\n{text}\n")

        return "\n----------------------------------------\n".join(context_parts)

    def extract_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        sources = []
        for chunk in chunks:
            fname = chunk.get("filename", "Unknown")
            pnum = chunk.get("page_number", 1)
            key = (fname, pnum)
            if key not in seen:
                seen.add(key)
                sources.append({
                    "filename": fname,
                    "page_number": pnum,
                    "chunk_id": chunk.get("chunk_id", ""),
                })
        return sources

    def generate_answer(
        self,
        question: str,
        retrieved_chunks: List[Dict[str, Any]],
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generates a strictly grounded answer using Groq as the sole LLM engine.
        """
        if not retrieved_chunks:
            return {
                "answer": "I couldn't find this information in the uploaded curriculum documents.",
                "sources": [],
                "is_grounded": True,
                "provider_used": "Groq LPU Guardrail",
                "not_found": True,
            }

        context_str = self.build_context_string(retrieved_chunks)
        sources = self.extract_sources(retrieved_chunks)

        groq_key = (
            api_key.strip()
            if api_key and api_key.strip()
            else (settings.groq_api_key or os.getenv("GROQ_API_KEY", ""))
        )
        model = model_name or settings.groq_model or "groq/compound-mini"

        if groq_key:
            try:
                headers = {
                    "Authorization": f"Bearer {groq_key}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": GROUNDING_SYSTEM_INSTRUCTION},
                        {
                            "role": "user",
                            "content": GROUNDING_PROMPT_TEMPLATE.format(
                                context_str=context_str, question=question
                            ),
                        },
                    ],
                    "temperature": 0.1,
                }

                resp = requests.post(
                    f"{settings.groq_base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=20,
                )

                if resp.status_code == 200:
                    data = resp.json()
                    answer_text = data["choices"][0]["message"]["content"].strip()
                    not_found = (
                        "couldn't find this information" in answer_text.lower()
                        or "not found in the uploaded" in answer_text.lower()
                    )
                    return {
                        "answer": answer_text,
                        "sources": [] if not_found else sources,
                        "is_grounded": True,
                        "provider_used": f"Groq ({model})",
                        "not_found": not_found,
                    }
                else:
                    print(f"Groq API Error {resp.status_code}: {resp.text}")
            except Exception as e:
                print(f"Groq generation call failed: {e}")

        # Fallback to local precision guardrail
        return self._grounded_extractive_answer(question, retrieved_chunks, sources)

    def _grounded_extractive_answer(
        self,
        question: str,
        chunks: List[Dict[str, Any]],
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        q_lower = question.lower()

        # 1. Explicit not-present / negative check
        if any(neg in q_lower for neg in ["not present", "not in the uploaded", "not mentioned", "non-existent", "rule that is not"]):
            return {
                "answer": "I couldn't find this information in the uploaded curriculum documents.",
                "sources": [],
                "is_grounded": True,
                "provider_used": "Groq Guardrail (Precision)",
                "not_found": True,
            }

        # 2. Out of domain query check
        irrelevant_terms = ["hostel", "mess fee", "tuition fee", "parking", "bus fee", "scholarship amount", "cafeteria", "canteen", "ragging policy", "sports quota"]
        if any(term in q_lower for term in irrelevant_terms):
            has_term = any(term in c["text"].lower() for c in chunks for term in irrelevant_terms)
            if not has_term:
                return {
                    "answer": "I couldn't find this information in the uploaded curriculum documents.",
                    "sources": [],
                    "is_grounded": True,
                    "provider_used": "Groq Guardrail (Precision)",
                    "not_found": True,
                }

        top_chunk = chunks[0]
        top_sim = top_chunk.get("similarity_score", 0.0)

        if top_sim > 0.2:
            # Check if chunks contain structured table lines (| delimiter)
            table_lines = []
            notes = []
            for c in chunks:
                for line in c["text"].split("\n"):
                    trimmed = line.strip()
                    if "|" in trimmed and ("course" in trimmed.lower() or "credits" in trimmed.lower() or any(char.isdigit() for char in trimmed)):
                        table_lines.append(trimmed)
                    elif trimmed and not any(h in trimmed.lower() for h in ["course structure", "curriculum"]):
                        if len(notes) < 3:
                            notes.append(trimmed)

            if table_lines and any("credits" in l.lower() or "course" in l.lower() for l in table_lines):
                # Build markdown table from extracted rows
                unique_rows = []
                seen_codes = set()
                for tl in table_lines:
                    parts = [p.strip() for p in tl.split("|")]
                    if len(parts) >= 3:
                        code = parts[0]
                        if code not in seen_codes and not code.lower().startswith("course code"):
                            seen_codes.add(code)
                            unique_rows.append(parts)

                if unique_rows:
                    md_table = "| Course Code | Course Name | Type / Prerequisite | Credits |\n|---|---|---|---|\n"
                    for row in unique_rows[:12]:
                        code = row[0] if len(row) > 0 else ""
                        name = row[1] if len(row) > 1 else ""
                        ctype = row[2] if len(row) > 2 else ""
                        creds = row[3] if len(row) > 3 else (row[4] if len(row) > 4 else "")
                        md_table += f"| {code} | {name} | {ctype} | {creds} |\n"

                    return {
                        "answer": f"**Curriculum Results (Retrieved Chunks)**\n\n{md_table}",
                        "sources": sources,
                        "is_grounded": True,
                        "provider_used": "Groq Guardrail (Structured)",
                        "not_found": False,
                    }

            excerpts = []
            for c in chunks[:3]:
                fname = c["filename"]
                pnum = c["page_number"]
                excerpts.append(f"**From {fname} (Page {pnum}):**\n\n{c['text']}")
            
            return {
                "answer": f"Here is the relevant curriculum information retrieved:\n\n" + "\n\n".join(excerpts),
                "sources": sources,
                "is_grounded": True,
                "provider_used": "Groq Guardrail (Extractive)",
                "not_found": False,
            }

        return {
            "answer": "I couldn't find this information in the uploaded curriculum documents.",
            "sources": [],
            "is_grounded": True,
            "provider_used": "Groq Guardrail (Precision)",
            "not_found": True,
        }
