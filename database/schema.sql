-- ==========================================================
-- BIS Intelligent Assistant - Supabase Schema
-- SIH Problem Statement 26107: BIS Intelligent Assistant
-- ==========================================================

-- 1. Enable the pgvector extension to support vector operations
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create the bis_documents table for storing chunked BIS documents & embeddings
CREATE TABLE IF NOT EXISTS bis_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id TEXT,
    document_name TEXT NOT NULL,
    file_name TEXT NOT NULL,
    category TEXT,
    standard_number TEXT,
    title TEXT,
    content TEXT NOT NULL,
    page_number INTEGER,
    section TEXT,
    source_url TEXT,
    publication_date TEXT,
    amendment_information TEXT,
    chunk_index INTEGER,
    metadata JSONB DEFAULT '{}'::jsonb,
    -- Gemini text-embedding-004 produces 768-dimensional embeddings by default
    embedding VECTOR(768),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Create relational & metadata indexes for ultra-fast filtering
CREATE INDEX IF NOT EXISTS idx_bis_documents_doc_name ON bis_documents(document_name);
CREATE INDEX IF NOT EXISTS idx_bis_documents_category ON bis_documents(category);
CREATE INDEX IF NOT EXISTS idx_bis_documents_std_number ON bis_documents(standard_number);
CREATE INDEX IF NOT EXISTS idx_bis_documents_page ON bis_documents(page_number);
CREATE INDEX IF NOT EXISTS idx_bis_documents_file_name ON bis_documents(file_name);
CREATE INDEX IF NOT EXISTS idx_bis_documents_metadata ON bis_documents USING gin (metadata);

-- 4. Full-text search index for keyword & hybrid search
CREATE INDEX IF NOT EXISTS idx_bis_documents_fts ON bis_documents USING gin(to_tsvector('english', content));

-- 5. HNSW Vector Index for efficient approximate nearest neighbors (Cosine similarity)
CREATE INDEX IF NOT EXISTS idx_bis_documents_embedding ON bis_documents 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
