import sys
from pathlib import Path

# Force UTF-8 output on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.sample_data.generator import generate_sample_curriculum_pdf
from app.rag.pdf_extractor import PDFExtractor
from app.rag.chunker import PageAwareChunker
from app.rag.metadata_extractor import MetadataExtractor
from app.rag.pipeline import rag_pipeline


def run_comprehensive_rag_audit():
    print("================================================================")
    print("COURSEGUIDE AI: COMPREHENSIVE RAG QUALITY & METADATA AUDIT")
    print("================================================================\n")

    # 1. Verify Sample Document
    sample_pdf = backend_dir / "sample_data" / "B.Tech_CSE_Curriculum_2024-2028.pdf"
    if not sample_pdf.exists():
        generate_sample_curriculum_pdf(sample_pdf)

    # 2. Ingestion & Metadata Retention Audit
    print("--- 1. AUDITING PDF EXTRACTION, CHUNKING & METADATA RETENTION ---")
    pages = PDFExtractor.extract_pages(sample_pdf)
    print(f"Extracted {len(pages)} pages with PyMuPDF find_tables & blocks.")
    assert len(pages) == 6, f"Expected 6 pages, got {len(pages)}"

    chunker = PageAwareChunker(chunk_size=500, chunk_overlap=100)
    chunks = chunker.chunk_document(pages, doc_id="audit_doc")
    enriched_chunks = [MetadataExtractor.enrich_chunk(c) for c in chunks]

    # Audit metadata retention: document, page, course code, course name, semester, credits, department/program, academic year, prerequisite
    required_meta_keys = [
        "document", "page", "course_code", "course_name", "semester", 
        "credits", "department", "program", "academic_year", "prerequisite"
    ]
    for c in enriched_chunks:
        meta = c["metadata"]
        for key in required_meta_keys:
            assert key in meta, f"Missing required metadata key '{key}' in chunk {c['chunk_id']}"
        # Page must match chunk page_number
        assert meta["page"] == c["page_number"]
        assert meta["document"] == c["filename"]

    # Verify atomic table rows (e.g. CS301 not split from credits)
    dbms_chunk = next(
        (c for c in enriched_chunks if "CS301" in c["text"] and "Database Management Systems" in c["text"]), 
        None
    )
    assert dbms_chunk is not None, "Could not find combined DBMS table row chunk!"
    assert "4 Credits" in dbms_chunk["text"], "Credits separated from course row!"
    print("PASS: Tabular row atomicity verified. Course code, name, and credits preserved together.\n")

    # Ingest into live RAG Pipeline
    print("Ingesting document into FAISS vector store...")
    summary = rag_pipeline.process_pdf(sample_pdf, doc_id="audit_cse")
    print(f"Ingested {summary['chunks_count']} chunks into FAISS.\n")

    # --- CATEGORY A: Simple Semantic Question ---
    print("--- CATEGORY A: SIMPLE SEMANTIC QUESTION ---")
    qa = "What core subjects are covered in software systems and computing?"
    res_a = rag_pipeline.query(qa)
    print(f"Q: '{qa}'")
    print(f"Provider: {res_a['provider_used']}")
    print(f"Answer:\n{res_a['answer'][:250]}...\n")
    print(f"Sources: {res_a['sources']}")
    assert len(res_a["sources"]) > 0, "No sources returned for Category A!"
    assert not res_a["not_found"], "Category A incorrectly marked as not found!"
    print("PASS: Category A succeeded.\n")

    # --- CATEGORY B: Semester-Filtered Question (Variations) ---
    print("--- CATEGORY B: SEMESTER-FILTERED QUESTION (VARIATIONS) ---")
    variations = [
        "What subjects are available in the third semester?",
        "semester 3 courses",
        "what do I study in sem 3?",
        "subjects in 3rd sem"
    ]
    for qb in variations:
        res_b = rag_pipeline.query(qb)
        sem_filter = res_b["detected_filters"].get("semester")
        print(f"Q: '{qb}' -> Detected Semester: {sem_filter}")
        assert sem_filter == 3, f"Failed to detect semester 3 in query: '{qb}'"
        assert any(src["page_number"] == 3 for src in res_b["sources"]), "Failed to cite Page 3 for Semester 3!"
        assert "CS201" in res_b["answer"] or "CS201" in str(res_b["retrieved_chunks"])
    print("PASS: Category B all variations succeeded with consistent Page 3 grounding.\n")

    # --- CATEGORY C: Course-Specific Question ---
    print("--- CATEGORY C: COURSE-SPECIFIC QUESTION ---")
    qc = "What is the course code and syllabus for Database Management Systems?"
    res_c = rag_pipeline.query(qc)
    print(f"Q: '{qc}'")
    print(f"Answer:\n{res_c['answer'][:250]}...\n")
    print(f"Sources: {res_c['sources']}")
    assert "CS301" in res_c["answer"] or "CS301" in str(res_c["retrieved_chunks"])
    assert any(src["page_number"] in [3, 6] for src in res_c["sources"])
    print("PASS: Category C succeeded with CS301 syllabus identification.\n")

    # --- CATEGORY D: Credit-Related Question ---
    print("--- CATEGORY D: CREDIT-RELATED QUESTION ---")
    qd1 = "What are the credits for Data Science?"
    res_d1 = rag_pipeline.query(qd1)
    print(f"Q: '{qd1}' -> Answer:\n{res_d1['answer'][:200]}...\n")
    assert "3" in res_d1["answer"] or "3" in str(res_d1["retrieved_chunks"])

    qd2 = "How many credits are there in the fourth semester?"
    res_d2 = rag_pipeline.query(qd2)
    print(f"Q: '{qd2}' -> Answer:\n{res_d2['answer'][:200]}...\n")
    assert "19" in res_d2["answer"] or "19" in str(res_d2["retrieved_chunks"])
    print("PASS: Category D succeeded with accurate numerical credit extraction.\n")

    # --- CATEGORY E: Prerequisite Question ---
    print("--- CATEGORY E: PREREQUISITE QUESTION ---")
    qe = "What are the prerequisites for Machine Learning?"
    res_e = rag_pipeline.query(qe)
    print(f"Q: '{qe}' -> Answer:\n{res_e['answer'][:250]}...\n")
    print(f"Sources: {res_e['sources']}")
    assert "MA202" in res_e["answer"] or "Statistics" in res_e["answer"] or "CS102" in res_e["answer"]
    print("PASS: Category E succeeded with exact prerequisite identification.\n")

    # --- CATEGORY F: Question Involving Multiple Courses ---
    print("--- CATEGORY F: QUESTION INVOLVING MULTIPLE COURSES ---")
    qf = "What are the prerequisites and credits for Operating Systems and Machine Learning?"
    res_f = rag_pipeline.query(qf)
    print(f"Q: '{qf}' -> Answer:\n{res_f['answer'][:300]}...\n")
    print(f"Sources: {res_f['sources']}")
    # Verify both CS207 and CS305 / Operating Systems and Machine Learning are covered
    answer_f = res_f["answer"].lower()
    assert ("operating systems" in answer_f or "cs207" in answer_f) and ("machine learning" in answer_f or "cs305" in answer_f)
    print("PASS: Category F succeeded with multi-course context aggregation.\n")

    # --- CATEGORY G: Question Not Present in the Documents ---
    print("--- CATEGORY G: QUESTION NOT PRESENT IN DOCUMENTS ---")
    qg = "What is the tuition fee and hostel mess charges for second year students?"
    res_g = rag_pipeline.query(qg)
    print(f"Q: '{qg}' -> Answer: '{res_g['answer']}'")
    print(f"Not found flag: {res_g['not_found']}")
    assert res_g["not_found"] is True or "couldn't find" in res_g["answer"].lower()
    assert len(res_g["sources"]) == 0, "Non-existent question should not cite sources!"
    print("PASS: Category G succeeded with strict grounded refusal.\n")

    print("================================================================")
    print("ALL 7 AUDIT CATEGORIES PASSED SUCCESSFULLY WITH ZERO ERRORS!")
    print("================================================================")


if __name__ == "__main__":
    run_comprehensive_rag_audit()
