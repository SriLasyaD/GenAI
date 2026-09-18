from typing import List, Dict, Any
import re


class PageAwareChunker:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be strictly less than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_page_text(self, page_info: Dict[str, Any], doc_id: str) -> List[Dict[str, Any]]:
        """
        Splits a single page's text into chunks while preserving page metadata.
        Guarantees that structured course rows (Code | Name | Credits | Prerequisite)
        are kept atomic and never split across chunk boundaries.
        """
        text = page_info["text"]
        filename = page_info["filename"]
        page_number = page_info["page_number"]
        total_pages = page_info.get("total_pages", 1)

        # Split into semantic blocks (paragraphs or table sections)
        sections = [s.strip() for s in text.split("\n\n") if s.strip()]
        if not sections:
            sections = [text]

        chunks_text: List[str] = []
        current_chunk = ""
        last_table_header = ""
        current_semester_label = ""

        for sec in sections:
            lines = [l.strip() for l in sec.split("\n") if l.strip()]
            is_table_section = any("|" in l for l in lines)

            # Check if this section defines a new semester header
            sem_match = re.search(r'\b(?:Semester|Sem)\s*[:\-]?\s*([1-8]|first|second|third|fourth|fifth|sixth|seventh|eighth)\b', sec, re.IGNORECASE)
            if sem_match:
                # Flush previous chunk
                if current_chunk:
                    chunks_text.append(current_chunk.strip())
                    current_chunk = ""
                # Extract clean semester header label, e.g. "Semester 3 Course Structure"
                for l in lines:
                    if re.search(r'\b(?:Semester|Sem)\s*[:\-]?\s*([1-8]|first|second|third|fourth|fifth|sixth|seventh|eighth)\b', l, re.IGNORECASE):
                        current_semester_label = l
                        break

            if is_table_section:
                # Find table header if present
                for line in lines:
                    if "|" in line and any(k in line.lower() for k in ["course", "code", "credits", "subject"]):
                        last_table_header = line
                        break

                # Process table line-by-line (each row is atomic)
                for line in lines:
                    if len(line) > self.chunk_size:
                        if current_chunk:
                            chunks_text.append(current_chunk.strip())
                            current_chunk = ""
                        chunks_text.append(line)
                        continue

                    tentative_len = len(current_chunk) + len(line) + (1 if current_chunk else 0)
                    if tentative_len <= self.chunk_size:
                        current_chunk = f"{current_chunk}\n{line}" if current_chunk else line
                    else:
                        if current_chunk:
                            chunks_text.append(current_chunk.strip())
                        # If starting continuation chunk inside a table, preserve header and semester label
                        prefix_lines = []
                        if current_semester_label:
                            prefix_lines.append(current_semester_label)
                        if last_table_header and line != last_table_header:
                            prefix_lines.append(last_table_header)

                        prefix = "\n".join(prefix_lines)
                        current_chunk = f"{prefix}\n{line}" if prefix else line
            else:
                # Regular paragraph text
                if len(sec) <= self.chunk_size:
                    tentative_len = len(current_chunk) + len(sec) + (2 if current_chunk else 0)
                    if tentative_len <= self.chunk_size:
                        current_chunk = f"{current_chunk}\n\n{sec}" if current_chunk else sec
                    else:
                        if current_chunk:
                            chunks_text.append(current_chunk.strip())
                        current_chunk = sec
                else:
                    # Split long non-table paragraph by sentences
                    sentences = re.split(r'(?<=[.!?])\s+', sec)
                    for sent in sentences:
                        if not sent.strip():
                            continue
                        tentative_len = len(current_chunk) + len(sent) + (1 if current_chunk else 0)
                        if tentative_len <= self.chunk_size:
                            current_chunk = f"{current_chunk} {sent}" if current_chunk else sent
                        else:
                            if current_chunk:
                                chunks_text.append(current_chunk.strip())
                            current_chunk = sent

        if current_chunk and current_chunk.strip():
            chunks_text.append(current_chunk.strip())

        # Build chunk records
        chunk_objects = []
        for idx, chunk_str in enumerate(chunks_text):
            if not chunk_str.strip():
                continue
            chunk_id = f"{doc_id}_p{page_number}_c{idx}"
            chunk_objects.append({
                "chunk_id": chunk_id,
                "doc_id": doc_id,
                "filename": filename,
                "page_number": page_number,
                "total_pages": total_pages,
                "chunk_index": idx,
                "text": chunk_str.strip(),
                "char_count": len(chunk_str.strip()),
            })

        return chunk_objects

    def chunk_document(self, pages: List[Dict[str, Any]], doc_id: str) -> List[Dict[str, Any]]:
        all_chunks = []
        for page in pages:
            page_chunks = self.chunk_page_text(page, doc_id)
            all_chunks.extend(page_chunks)
        return all_chunks
