import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

# Add backend to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.sample_data.generator import generate_sample_curriculum_pdf
from app.rag.pdf_extractor import PDFExtractor
from app.rag.chunker import PageAwareChunker
from app.rag.metadata_extractor import MetadataExtractor
from app.rag.embedder import Embedder
from app.rag.vector_store import FAISSVectorStore
from app.rag.retriever import MetadataAwareRetriever
from app.rag.pipeline import rag_pipeline


def test_full_rag_pipeline():
    print("=== STARTING COURSEGUIDE AI BACKEND TEST ===")
    
    # 1. Generate Sample Curriculum PDF
    sample_pdf = backend_dir / "sample_data" / "B.Tech_CSE_Curriculum_2024-2028.pdf"
    print(f"Generating sample curriculum PDF at: {sample_pdf}")
    generate_sample_curriculum_pdf(sample_pdf)
    assert sample_pdf.exists(), "Sample PDF was not created!"
    print("PASS: Sample PDF created successfully.")

    # 2. Extract pages with PyMuPDF
    pages = PDFExtractor.extract_pages(sample_pdf)
    print(f"Extracted {len(pages)} pages.")
    assert len(pages) == 6, f"Expected 6 pages, got {len(pages)}"
    for p in pages:
        assert p["page_number"] >= 1 and p["page_number"] <= 6
        assert len(p["text"]) > 50
    print("PASS: Page extraction and page number preservation verified.")

    # 3. Test Chunking
    chunker = PageAwareChunker(chunk_size=500, chunk_overlap=100)
    chunks = chunker.chunk_document(pages, doc_id="test_doc")
    print(f"Generated {len(chunks)} chunks across 6 pages.")
    assert len(chunks) > 10, "Expected at least 10 chunks."
    for c in chunks:
        assert "page_number" in c
        assert "filename" in c
        assert "chunk_id" in c
    print("PASS: Page-aware chunking verified.")

    # 4. Test Metadata Extraction
    enriched = [MetadataExtractor.enrich_chunk(c) for c in chunks]
    detected_semesters = [c["metadata"]["semester"] for c in enriched if c["metadata"]["semester"]]
    detected_codes = [code for c in enriched for code in c["metadata"]["course_codes"]]
    print(f"Detected semesters in chunks: {set(detected_semesters)}")
    print(f"Sample detected course codes: {list(set(detected_codes))[:8]}")
    assert len(detected_semesters) > 0, "No semesters detected!"
    assert any("CS301" in c["metadata"]["course_codes"] for c in enriched), "CS301 not detected!"
    print("PASS: Academic metadata extraction verified.")

    # 5. Ingest into Pipeline
    print("Ingesting PDF into RAG pipeline...")
    summary = rag_pipeline.process_pdf(sample_pdf, doc_id="sample_btech_cse")
    print(f"Ingested: {summary['filename']} with {summary['chunks_count']} chunks in {summary['ingestion_metrics']['total_sec']}s")

    # 6. Test Query 1: Semester 3 subjects
    q1 = "What subjects are available in the third semester?"
    res1 = rag_pipeline.query(q1)
    print(f"\n--- Query: '{q1}' ---")
    print("Answer:", res1["answer"][:250], "...")
    print("Sources:", res1["sources"])
    print("Detected filters:", res1["detected_filters"])
    assert res1["detected_filters"].get("semester") == 3, f"Expected semester 3 filter, got {res1['detected_filters']}"
    assert len(res1["sources"]) > 0, "Expected sources!"
    print("PASS: Semester 3 query verified.")

    # 7. Test Query 2: Programming prerequisites
    q2 = "Which courses have programming prerequisites?"
    res2 = rag_pipeline.query(q2)
    print(f"\n--- Query: '{q2}' ---")
    print("Answer:", res2["answer"][:250], "...")
    print("Sources:", res2["sources"])
    assert len(res2["sources"]) > 0
    print("PASS: Prerequisite query verified.")

    # 8. Test Query 3: Credits for Data Science
    q3 = "What are the credits for Data Science?"
    res3 = rag_pipeline.query(q3)
    print(f"\n--- Query: '{q3}' ---")
    print("Answer:", res3["answer"][:250], "...")
    print("Sources:", res3["sources"])
    assert "3" in res3["answer"], "Expected 3 credits for Data Science"
    print("PASS: Credits query verified.")

    # 9. Test Query 4: Course code for Database Management Systems
    q4 = "What is the course code for Database Management Systems?"
    res4 = rag_pipeline.query(q4)
    print(f"\n--- Query: '{q4}' ---")
    print("Answer:", res4["answer"][:250], "...")
    print("Sources:", res4["sources"])
    assert "CS301" in res4["answer"] or "CS301" in str(res4["retrieved_chunks"]), "Expected CS301"
    print("PASS: Course code query verified.")

    # 10. Test Query 5: Non-existent info (Grounding test)
    q5 = "What is the annual hostel and mess fee for first year students?"
    res5 = rag_pipeline.query(q5)
    print(f"\n--- Query: '{q5}' ---")
    print("Answer:", res5["answer"])
    print("Not found flag:", res5["not_found"])
    assert res5["not_found"] is True or "couldn't find" in res5["answer"].lower()
    print("PASS: Grounded non-existent query refusal verified.")

    print("\nALL 10 RAG PIPELINE TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    test_full_rag_pipeline()
