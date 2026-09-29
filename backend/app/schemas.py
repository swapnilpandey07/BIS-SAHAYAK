from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SourceCitation(BaseModel):
    document_name: str
    file_name: Optional[str] = None
    title: Optional[str] = None
    page_number: Optional[int] = None
    section: Optional[str] = None
    standard_number: Optional[str] = None
    category: Optional[str] = None
    document_type: Optional[str] = None
    version: Optional[str] = None
    source_url: Optional[str] = None
    similarity: Optional[float] = None
    snippet: Optional[str] = None


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The user's question about BIS in English, Hindi, or Hinglish")
    category_filter: Optional[str] = Field(None, description="Optional category filter (e.g., 'acts', 'standards', 'hallmarking')")
    document_type_filter: Optional[str] = Field(None, description="Optional document type filter")
    top_k: Optional[int] = Field(None, ge=1, le=20, description="Override number of chunks to retrieve")


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceCitation]
    retrieved_chunks: int
    model_used: str
    is_grounded: bool = True


class DocumentMetadata(BaseModel):
    document_id: str
    document_name: str
    title: str
    document_type: str
    category: str
    file_name: str
    standard_number: Optional[str] = None
    source_url: Optional[str] = None
    publication_date: Optional[str] = None
    effective_date: Optional[str] = None
    amendment_date: Optional[str] = None
    amendment_information: Optional[str] = None
    version: Optional[str] = "1.0"
    base_document: Optional[str] = None
    is_amendment: bool = False
    total_pages: Optional[int] = None
    chunks_count: Optional[int] = None
    file_hash: Optional[str] = None
    status: str = "indexed"


class DocumentChunk(BaseModel):
    document_id: str
    document_name: str
    file_name: str
    category: str
    document_type: Optional[str] = "general"
    standard_number: Optional[str] = None
    title: Optional[str] = None
    content: str
    page_number: int
    section: Optional[str] = None
    source_url: Optional[str] = None
    publication_date: Optional[str] = None
    effective_date: Optional[str] = None
    amendment_date: Optional[str] = None
    amendment_information: Optional[str] = None
    version: Optional[str] = "1.0"
    chunk_index: int
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = None


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    category: Optional[str] = None
    document_type: Optional[str] = None
    standard_number: Optional[str] = None
    top_k: int = Field(default=8, ge=1, le=50)


class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[Dict[str, Any]]
    citations: List[SourceCitation]


class IngestRequest(BaseModel):
    force_reindex: bool = Field(default=False, description="Whether to re-index already processed files")


class IngestResponse(BaseModel):
    status: str
    documents_processed: int
    documents_skipped: int
    total_chunks_created: int
    total_chunks_indexed: int
    duplicates_skipped: int
    failed_count: int
    indexed_documents: List[Dict[str, Any]]
    errors: List[str] = Field(default_factory=list)


class DocumentStatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    categories: Dict[str, int]
    document_types: Dict[str, int]
    latest_ingestion_date: Optional[str] = None
    failed_documents: List[str] = Field(default_factory=list)
    duplicate_documents_skipped: int = 0


class HealthResponse(BaseModel):
    status: str
    version: str
    database_connected: bool
    gemini_configured: bool
    embedding_model: str
    total_documents: int
    total_chunks: int
