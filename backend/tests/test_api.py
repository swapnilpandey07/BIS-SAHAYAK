import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "BIS Intelligent Assistant API"
    assert data["status"] == "operational"


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "embedding_model" in data
    assert data["total_documents"] >= 30


def test_ask_valid_bis_question():
    response = client.post("/api/ask", json={"question": "What is BIS Act 2016?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert len(data["sources"]) > 0
    assert data["retrieved_chunks"] > 0


def test_ask_out_of_domain_negative_question():
    response = client.post("/api/ask", json={"question": "What is the secret cryptocurrency price in Atlantis?"})
    assert response.status_code == 200
    data = response.json()
    # Guardrail check: Should not hallucinate and should state unverified / insufficient context
    ans_lower = data["answer"].lower()
    assert "could not verify" in ans_lower or "not contain enough information" in ans_lower or data["retrieved_chunks"] == 0


def test_list_documents_endpoint():
    response = client.get("/api/documents")
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "documents" in data
    assert data["count"] >= 30


def test_filter_documents_by_category():
    response = client.get("/api/documents?category=hallmarking")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] > 0
    for d in data["documents"]:
        assert d["category"] == "hallmarking"


def test_document_stats_endpoint():
    response = client.get("/api/document-stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_documents"] >= 30
    assert data["total_chunks"] >= 80
    assert "acts" in data["categories"]
    assert "certification" in data["categories"]
    assert "hallmarking" in data["categories"]
    assert "qco" in data["categories"]


def test_search_endpoint():
    response = client.post("/api/search", json={"query": "IS 302 electrical safety"})
    assert response.status_code == 200
    data = response.json()
    assert data["total_results"] > 0
    assert len(data["citations"]) > 0
    assert any("302" in (c.get("standard_number") or "") or "302" in c.get("document_name", "") for c in data["citations"])


def test_document_details_endpoint():
    # Fetch first document from list
    list_res = client.get("/api/documents")
    docs = list_res.json()["documents"]
    doc_id = docs[0]["document_id"]

    response = client.get(f"/api/documents/{doc_id}")
    assert response.status_code == 200
    data = response.json()
    assert "document" in data
    assert "chunks" in data
    assert data["total_chunks"] > 0
