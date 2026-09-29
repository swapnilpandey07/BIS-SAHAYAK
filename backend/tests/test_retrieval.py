import pytest
from backend.app.schemas import DocumentChunk
from backend.app.database import local_vector_store
from backend.app.retrieval import extract_search_entities, retrieve_relevant_chunks, format_context_for_prompt
from backend.app.embeddings import _generate_deterministic_vector


@pytest.fixture(autouse=True)
def populate_test_store():
    # Insert sample BIS chunks into local store
    chunk1 = DocumentChunk(
        document_id="test_act",
        document_name="BIS Act 2016",
        file_name="BIS_Act_2016.pdf",
        category="acts",
        standard_number=None,
        title="Bureau of Indian Standards Act 2016",
        content="The BIS Act 2016 establishes the Bureau of Indian Standards as the National Standards Body of India.",
        page_number=2,
        section="Chapter I - Preliminary",
        source_url="https://www.bis.gov.in/act2016",
        chunk_index=0,
        embedding=_generate_deterministic_vector("The BIS Act 2016 establishes the Bureau of Indian Standards as the National Standards Body of India.")
    )

    chunk2 = DocumentChunk(
        document_id="test_std",
        document_name="IS 302 Safety of Household Appliances",
        file_name="IS_302.pdf",
        category="standards",
        standard_number="IS 302",
        title="Safety of Household and Similar Electrical Appliances",
        content="IS 302 Part 1 specifies general safety requirements for electrical appliances for household use.",
        page_number=5,
        section="Clause 1 - Scope",
        source_url="https://www.bis.gov.in/is302",
        chunk_index=0,
        embedding=_generate_deterministic_vector("IS 302 Part 1 specifies general safety requirements for electrical appliances for household use.")
    )

    local_vector_store.insert_chunks([chunk1, chunk2])


def test_extract_search_entities():
    entities1 = extract_search_entities("What is IS 302 : Part 1 standard?")
    assert entities1.get("standard_number") == "IS 302"

    entities2 = extract_search_entities("What are the penalties under BIS Act?")
    assert entities2.get("category") == "acts"

    entities3 = extract_search_entities("Gold hallmarking process")
    assert entities3.get("category") == "hallmarking"


def test_retrieval_and_formatting():
    chunks, citations = retrieve_relevant_chunks("What is BIS Act 2016?", top_k=2)
    assert len(chunks) >= 1
    assert len(citations) >= 1
    assert any("bis_act" in c.document_name.lower() or "bis act" in (c.title or "").lower() for c in citations)

    formatted = format_context_for_prompt(chunks)
    assert "BIS" in formatted
    assert "Page:" in formatted
