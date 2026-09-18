import pymupdf as fitz
from typing import List, Dict, Any
from pathlib import Path


class PDFExtractor:
    @staticmethod
    def extract_pages(pdf_path: str | Path) -> List[Dict[str, Any]]:
        """
        Extract text and structured table rows from a PDF file page by page.
        Preserves page numbers (1-indexed), filename, and structural layout.
        Ensures course rows in tables (Course Code | Course Name | Credits | Prerequisite)
        are kept as unified, intact lines so relationships are never severed.
        """
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {path}")

        doc = fitz.open(str(path))
        filename = path.name
        total_pages = len(doc)
        pages_data = []

        try:
            for page_idx in range(total_pages):
                page = doc[page_idx]
                page_num = page_idx + 1

                # Check if page has structured tables
                tabs = page.find_tables()
                if tabs.tables:
                    # Collect table bounding boxes
                    tables_bboxes = [t.bbox for t in tabs.tables]
                    
                    def is_inside_table(bbox, t_bboxes):
                        cy = (bbox[1] + bbox[3]) / 2
                        cx = (bbox[0] + bbox[2]) / 2
                        for tx0, ty0, tx1, ty1 in t_bboxes:
                            if ty0 <= cy <= ty1 and tx0 <= cx <= tx1:
                                return True
                        return False

                    page_elements = []

                    # Add structured table lines
                    for t in tabs.tables:
                        rows = t.extract()
                        table_lines = []
                        for r in rows:
                            cleaned_cells = [
                                str(c).replace('\n', ' ').strip() 
                                for c in r if c is not None and str(c).strip()
                            ]
                            if cleaned_cells:
                                table_lines.append(" | ".join(cleaned_cells))
                        if table_lines:
                            page_elements.append((t.bbox[1], "\n".join(table_lines)))

                    # Add non-table text blocks
                    for b in page.get_text("blocks"):
                        if not is_inside_table(b, tables_bboxes):
                            txt = b[4].strip()
                            if txt:
                                page_elements.append((b[1], txt))

                    # Sort top to bottom by vertical coordinate
                    page_elements.sort(key=lambda x: x[0])
                    cleaned_text = "\n\n".join(item[1] for item in page_elements if item[1])
                else:
                    # Fallback to standard text extraction
                    text = page.get_text("text")
                    cleaned_text = "\n".join(
                        line.strip() for line in text.splitlines() if line.strip()
                    )

                if cleaned_text:
                    pages_data.append({
                        "filename": filename,
                        "page_number": page_num,
                        "total_pages": total_pages,
                        "text": cleaned_text,
                    })
        finally:
            doc.close()

        return pages_data
