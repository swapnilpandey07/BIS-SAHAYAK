-- ==========================================================
-- BIS Intelligent Assistant - Supabase RPC Functions
-- Vector similarity & Hybrid search routines
-- ==========================================================

-- Function 1: Vector Similarity Search
CREATE OR REPLACE FUNCTION match_documents (
    query_embedding VECTOR(768),
    match_threshold FLOAT DEFAULT 0.3,
    match_count INT DEFAULT 8,
    filter_category TEXT DEFAULT NULL,
    filter_standard TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    document_id TEXT,
    document_name TEXT,
    file_name TEXT,
    category TEXT,
    standard_number TEXT,
    title TEXT,
    content TEXT,
    page_number INT,
    section TEXT,
    source_url TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        bd.id,
        bd.document_id,
        bd.document_name,
        bd.file_name,
        bd.category,
        bd.standard_number,
        bd.title,
        bd.content,
        bd.page_number,
        bd.section,
        bd.source_url,
        bd.metadata,
        1 - (bd.embedding <=> query_embedding) AS similarity
    FROM bis_documents bd
    WHERE 
        (1 - (bd.embedding <=> query_embedding)) > match_threshold
        AND (filter_category IS NULL OR bd.category = filter_category)
        AND (filter_standard IS NULL OR bd.standard_number ILIKE '%' || filter_standard || '%')
    ORDER BY bd.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;


-- Function 2: Hybrid Search (Combining vector similarity + keyword FTS)
CREATE OR REPLACE FUNCTION hybrid_match_documents (
    query_text TEXT,
    query_embedding VECTOR(768),
    match_threshold FLOAT DEFAULT 0.25,
    match_count INT DEFAULT 8,
    full_text_weight FLOAT DEFAULT 0.3,
    semantic_weight FLOAT DEFAULT 0.7
)
RETURNS TABLE (
    id UUID,
    document_id TEXT,
    document_name TEXT,
    file_name TEXT,
    category TEXT,
    standard_number TEXT,
    title TEXT,
    content TEXT,
    page_number INT,
    section TEXT,
    source_url TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH semantic_search AS (
        SELECT
            bd.id,
            1 - (bd.embedding <=> query_embedding) AS sem_score
        FROM bis_documents bd
        WHERE 1 - (bd.embedding <=> query_embedding) > match_threshold
    ),
    keyword_search AS (
        SELECT
            bd.id,
            ts_rank_cd(to_tsvector('english', bd.content), websearch_to_tsquery('english', query_text)) AS kw_score
        FROM bis_documents bd
        WHERE to_tsvector('english', bd.content) @@ websearch_to_tsquery('english', query_text)
           OR bd.standard_number ILIKE '%' || query_text || '%'
           OR bd.document_name ILIKE '%' || query_text || '%'
    )
    SELECT
        bd.id,
        bd.document_id,
        bd.document_name,
        bd.file_name,
        bd.category,
        bd.standard_number,
        bd.title,
        bd.content,
        bd.page_number,
        bd.section,
        bd.source_url,
        bd.metadata,
        COALESCE(s.sem_score * semantic_weight, 0.0) + 
        COALESCE(LEAST(k.kw_score, 1.0) * full_text_weight, 0.0) AS similarity
    FROM bis_documents bd
    LEFT JOIN semantic_search s ON bd.id = s.id
    LEFT JOIN keyword_search k ON bd.id = k.id
    WHERE (s.sem_score IS NOT NULL OR k.kw_score IS NOT NULL)
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;
