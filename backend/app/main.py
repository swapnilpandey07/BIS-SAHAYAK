import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, Path as FastApiPath
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.schemas import (
    AskRequest,
    AskResponse,
    IngestRequest,
    IngestResponse,
    HealthResponse,
    SearchRequest,
    SearchResponse,
    DocumentStatsResponse
)
from backend.app.rag import answer_bis_question
from backend.app.ingestion import ingest_all_documents, load_metadata_registry
from backend.app.retrieval import retrieve_relevant_chunks
from backend.app.database import db_client, local_vector_store

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("bis_main")

app = FastAPI(
    title="BIS Intelligent Assistant API",
    description="Production-Grade Official RAG Assistant for Bureau of Indian Standards (SIH Problem Statement 26107)",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
origins = [
    settings.FRONTEND_URL,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
def root():
    return {
        "service": "BIS Intelligent Assistant API",
        "status": "operational",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "stats": "/api/document-stats"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    registry = load_metadata_registry()
    total_chunks = len(local_vector_store.chunks)

    return HealthResponse(
        status="healthy",
        version="2.0.0",
        database_connected=db_client.is_connected,
        gemini_configured=bool(settings.GEMINI_API_KEY),
        embedding_model=settings.GEMINI_EMBEDDING_MODEL,
        total_documents=len(registry),
        total_chunks=total_chunks
    )


@app.post("/api/ask", response_model=AskResponse, tags=["RAG Query"])
def ask_question(request: AskRequest):
    """
    Submits a natural language query (English, Hindi, Hinglish) to the BIS RAG engine.
    Retrieves official BIS context and returns a strictly grounded answer with verified source citations.
    """
    try:
        response = answer_bis_question(request)
        return response
    except Exception as e:
        logger.error(f"Error processing ask_question: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.post("/api/ingest", response_model=IngestResponse, tags=["Ingestion"])
def trigger_ingest(request: IngestRequest = IngestRequest()):
    """
    Triggers ingestion of authorized BIS PDFs located in documents/raw/.
    Extracts text, splits chunks, computes embeddings, and indexes into Supabase/local store.
    """
    try:
        result = ingest_all_documents(force_reindex=request.force_reindex)
        return result
    except Exception as e:
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.post("/api/search", response_model=SearchResponse, tags=["Search"])
def search_documents(request: SearchRequest):
    """
    Direct hybrid search across the BIS knowledge base.
    Returns matched chunks, similarity scores, and structured citations.
    """
    try:
        chunks, citations = retrieve_relevant_chunks(
            query=request.query,
            top_k=request.top_k,
            category_filter=request.category,
            document_type_filter=request.document_type
        )
        return SearchResponse(
            query=request.query,
            total_results=len(chunks),
            results=chunks,
            citations=citations
        )
    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/api/documents", tags=["Documents"])
def list_documents(
    category: Optional[str] = Query(None, description="Filter documents by category"),
    document_type: Optional[str] = Query(None, description="Filter by document type")
):
    """
    Returns list of all currently indexed BIS documents and their rich metadata.
    """
    registry = load_metadata_registry()
    filtered = registry
    if category:
        filtered = [d for d in filtered if d.get("category", "").lower() == category.lower()]
    if document_type:
        filtered = [d for d in filtered if d.get("document_type", "").lower() == document_type.lower()]

    return {
        "count": len(filtered),
        "total": len(registry),
        "documents": filtered
    }


@app.get("/api/documents/{document_id}", tags=["Documents"])
def get_document_details(document_id: str = FastApiPath(..., description="Document ID or Document Name")):
    """
    Retrieves detailed metadata and all associated chunks for a specific BIS document.
    """
    registry = load_metadata_registry()
    doc = next((d for d in registry if d.get("document_id") == document_id or d.get("document_name") == document_id), None)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found in registry")

    matching_chunks = [
        c for c in local_vector_store.chunks
        if c.get("document_id") == doc.get("document_id") or c.get("document_name") == doc.get("document_name")
    ]

    return {
        "document": doc,
        "total_chunks": len(matching_chunks),
        "chunks": matching_chunks
    }


@app.get("/api/document-stats", response_model=DocumentStatsResponse, tags=["Documents"])
def get_document_stats():
    """
    Returns high-level statistics of the BIS knowledge base:
    - total documents
    - total chunks
    - documents grouped by category
    - documents grouped by document type
    - latest ingestion timestamp
    - failed and duplicate counts
    """
    registry = load_metadata_registry()
    total_chunks = len(local_vector_store.chunks)

    categories_count = {}
    doc_types_count = {}
    latest_date = None

    for doc in registry:
        cat = doc.get("category", "general")
        categories_count[cat] = categories_count.get(cat, 0) + 1

        dtype = doc.get("document_type", "general")
        doc_types_count[dtype] = doc_types_count.get(dtype, 0) + 1

        ing_date = doc.get("ingested_at")
        if ing_date:
            if not latest_date or ing_date > latest_date:
                latest_date = ing_date

    return DocumentStatsResponse(
        total_documents=len(registry),
        total_chunks=total_chunks,
        categories=categories_count,
        document_types=doc_types_count,
        latest_ingestion_date=latest_date,
        failed_documents=[],
        duplicate_documents_skipped=0
    )
