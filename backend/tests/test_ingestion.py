import pytest
from pathlib import Path
from backend.app.chunking import clean_text, split_text_into_chunks, extract_sections_from_page
from backend.app.embeddings import _generate_deterministic_vector


def test_clean_text():
    raw = "Bureau of Indian Standards\xa0\xa0\n\n\n\nSection 1: Scope\r\n"
    cleaned = clean_text(raw)
    assert "\xa0" not in cleaned
    assert "\r" not in cleaned
    assert "Bureau of Indian Standards" in cleaned
    assert "Section 1: Scope" in cleaned


def test_split_text_into_chunks():
    sample_text = (
        "The Bureau of Indian Standards (BIS) is the National Standard Body of India. "
        "It was established under the BIS Act 2016 for the harmonious development of standardisation, "
        "marking and quality certification of goods and for matters connected therewith or incidental thereto. "
        "BIS has been providing traceable and tangible benefits to the national economy in a number of ways. "
        "Providing safe reliable quality goods, minimizing health hazards to consumers, and promoting exports."
    )
    chunks = split_text_into_chunks(sample_text, chunk_size=150, chunk_overlap=30)
    assert len(chunks) >= 1
    for c in chunks:
        assert len(c) > 0


def test_extract_sections():
    page_text = "CHAPTER II\nBUREAU OF INDIAN STANDARDS\n\nSection 3. Establishment of Bureau."
    sec = extract_sections_from_page(page_text)
    assert "CHAPTER" in sec or "Section" in sec


def test_deterministic_embedding_vector():
    vec1 = _generate_deterministic_vector("BIS Act 2016", dimension=768)
    vec2 = _generate_deterministic_vector("BIS Act 2016", dimension=768)
    vec3 = _generate_deterministic_vector("Hallmarking Scheme", dimension=768)

    assert len(vec1) == 768
    assert vec1 == vec2  # deterministic
    assert vec1 != vec3  # different text produces different vector
