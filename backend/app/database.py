import json
import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np

from backend.app.config import settings, DOCUMENTS_PROCESSED_DIR
from backend.app.schemas import DocumentChunk

logger = logging.getLogger("bis_database")

LOCAL_STORE_PATH = DOCUMENTS_PROCESSED_DIR / "vector_store.json"


class LocalVectorStore:
    """
    In-memory / JSON persisted vector store for local testing & caching.
    Ensures tests and offline evaluation work seamlessly without mandatory external DB.
    """
    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []
        self.load()

    def load(self):
        if LOCAL_STORE_PATH.exists():
            try:
                with open(LOCAL_STORE_PATH, "r", encoding="utf-8") as f:
                    self.chunks = json.load(f)
                logger.info(f"Loaded {len(self.chunks)} chunks from local vector store.")
            except Exception as e:
                logger.error(f"Error loading local vector store: {e}")
                self.chunks = []
        else:
            self.chunks = []

    def save(self):
        DOCUMENTS_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        try:
            with open(LOCAL_STORE_PATH, "w", encoding="utf-8") as f:
                json.dump(self.chunks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving local vector store: {e}")

    def insert_chunks(self, new_chunks: List[DocumentChunk]):
        # Upsert by document_name + page_number + chunk_index
        chunk_map = {
            f"{c.get('document_name')}_{c.get('page_number')}_{c.get('chunk_index')}": c
            for c in self.chunks
        }
        added = 0
        updated = 0
        for chunk in new_chunks:
            key = f"{chunk.document_name}_{chunk.page_number}_{chunk.chunk_index}"
            if key not in chunk_map:
                added += 1
            else:
                updated += 1
            chunk_map[key] = chunk.model_dump()

        self.chunks = list(chunk_map.values())
        self.save()
        logger.info(f"Upserted {len(new_chunks)} chunks into local vector store ({added} added, {updated} updated). Total: {len(self.chunks)}")
        return len(new_chunks)

    def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 6,
        similarity_threshold: float = 0.30,
        category: Optional[str] = None,
        standard_number: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if not self.chunks or not query_embedding:
            return []

        q_vec = np.array(query_embedding, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0:
            return []
        q_vec = q_vec / q_norm

        results = []
        for c in self.chunks:
            if category and c.get("category") != category:
                continue
            if standard_number and standard_number.lower() not in (c.get("standard_number") or "").lower():
                continue

            emb = c.get("embedding")
            if not emb:
                continue
            
            c_vec = np.array(emb, dtype=np.float32)
            if c_vec.shape[0] != q_vec.shape[0]:
                continue
            c_norm = np.linalg.norm(c_vec)
            if c_norm == 0:
                continue
            c_vec = c_vec / c_norm

            sim = float(np.dot(q_vec, c_vec))
            if sim >= similarity_threshold:
                c_copy = dict(c)
                c_copy["similarity"] = round(sim, 4)
                results.append(c_copy)

        results.sort(key=lambda x: x.get("similarity", 0.0), reverse=True)
        return results[:top_k]

    def keyword_search(self, query_text: str, top_k: int = 6) -> List[Dict[str, Any]]:
        if not self.chunks or not query_text:
            return []

        terms = [t.lower() for t in query_text.split() if len(t) > 2]
        if not terms:
            return []

        scored = []
        for c in self.chunks:
            content_lower = c.get("content", "").lower()
            doc_name_lower = c.get("document_name", "").lower()
            std_no_lower = (c.get("standard_number") or "").lower()

            score = 0.0
            for term in terms:
                if term in std_no_lower:
                    score += 3.0
                if term in doc_name_lower:
                    score += 2.0
                if term in content_lower:
                    score += 1.0

            if score > 0:
                c_copy = dict(c)
                c_copy["keyword_score"] = score
                scored.append(c_copy)

        scored.sort(key=lambda x: x.get("keyword_score", 0.0), reverse=True)
        return scored[:top_k]


# Global local store instance
local_vector_store = LocalVectorStore()


class SupabaseVectorClient:
    """
    Client for interacting with Supabase PostgreSQL + pgvector.
    Falls back cleanly to LocalVectorStore when Supabase is not configured.
    """
    def __init__(self):
        self._client = None
        self._init_client()

    def _init_client(self):
        if settings.SUPABASE_URL and settings.SUPABASE_KEY and "your-project" not in settings.SUPABASE_URL:
            try:
                from supabase import create_client, Client
                self._client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
                logger.info("Connected to Supabase pgvector successfully.")
            except Exception as e:
                logger.error(f"Failed to connect to Supabase: {e}")
                self._client = None
        else:
            self._client = None

    @property
    def is_connected(self) -> bool:
        return self._client is not None

    def insert_chunks(self, chunks: List[DocumentChunk]) -> int:
        """
        Inserts document chunks into Supabase and local store.
        """
        # Always persist to local store for reliability
        local_vector_store.insert_chunks(chunks)

        if not self.is_connected:
            return len(chunks)

        try:
            records = []
            for c in chunks:
                records.append({
                    "document_id": c.document_id,
                    "document_name": c.document_name,
                    "file_name": c.file_name,
                    "category": c.category,
                    "standard_number": c.standard_number,
                    "title": c.title,
                    "content": c.content,
                    "page_number": c.page_number,
                    "section": c.section,
                    "source_url": c.source_url,
                    "publication_date": c.publication_date,
                    "amendment_information": c.amendment_information,
                    "chunk_index": c.chunk_index,
                    "metadata": c.metadata,
                    "embedding": c.embedding
                })
            
            # Batch upsert in chunks of 50
            batch_size = 50
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                self._client.table(settings.SUPABASE_TABLE).upsert(batch).execute()
            
            logger.info(f"Uploaded {len(records)} chunks to Supabase {settings.SUPABASE_TABLE}.")
            return len(records)
        except Exception as e:
            logger.error(f"Error inserting chunks to Supabase: {e}")
            return len(chunks)

    def search(
        self,
        query_embedding: List[float],
        query_text: str = "",
        top_k: int = 6,
        similarity_threshold: float = 0.30,
        category: Optional[str] = None,
        standard_number: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Performs vector/hybrid search using Supabase RPC or local store.
        """
        if self.is_connected:
            try:
                # Try hybrid_match_documents or match_documents RPC
                if settings.ENABLE_HYBRID_SEARCH and query_text:
                    rpc_params = {
                        "query_text": query_text,
                        "query_embedding": query_embedding,
                        "match_threshold": similarity_threshold,
                        "match_count": top_k
                    }
                    res = self._client.rpc("hybrid_match_documents", rpc_params).execute()
                else:
                    rpc_params = {
                        "query_embedding": query_embedding,
                        "match_threshold": similarity_threshold,
                        "match_count": top_k,
                        "filter_category": category,
                        "filter_standard": standard_number
                    }
                    res = self._client.rpc("match_documents", rpc_params).execute()

                if res and res.data:
                    return res.data
            except Exception as e:
                logger.warning(f"Supabase RPC search failed: {e}. Falling back to local vector store.")

        # Fallback to local vector store
        return local_vector_store.similarity_search(
            query_embedding=query_embedding,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            category=category,
            standard_number=standard_number
        )


db_client = SupabaseVectorClient()
