import logging
from typing import List, Optional
import numpy as np

from backend.app.config import settings

logger = logging.getLogger("bis_embeddings")

_is_configured = False

CANDIDATE_EMBEDDING_MODELS = [
    "models/gemini-embedding-001",
    "models/gemini-embedding-2-preview",
    "models/gemini-embedding-2",
    "models/text-embedding-004",
    "models/embedding-001",
    "text-embedding-004",
]

_active_model = None


def _init_gemini():
    global _is_configured
    if not _is_configured and settings.GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            _is_configured = True
            logger.info("Google Gemini Embeddings configured successfully.")
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {e}")


def _generate_deterministic_vector(text: str, dimension: int = 768) -> List[float]:
    """Generates a deterministic vector based on text hash for offline/test fallback."""
    import hashlib
    h = hashlib.sha256(text.encode('utf-8')).digest()
    seed = int.from_bytes(h[:4], 'little')
    rng = np.random.default_rng(seed)
    vec = rng.standard_normal(dimension)
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()


def get_embedding(text: str, task_type: str = "retrieval_query") -> List[float]:
    """
    Generate an embedding vector for the given text using Gemini API with auto-fallback.
    """
    global _active_model
    if not text or not text.strip():
        return [0.0] * settings.EMBEDDING_DIMENSION

    _init_gemini()

    if settings.GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            
            models_to_try = [_active_model] if _active_model else []
            for m in [settings.GEMINI_EMBEDDING_MODEL] + CANDIDATE_EMBEDDING_MODELS:
                if m and m not in models_to_try:
                    models_to_try.append(m)

            for model_name in models_to_try:
                try:
                    result = genai.embed_content(
                        model=model_name,
                        content=text.strip(),
                        task_type=task_type,
                    )
                    embedding = result.get('embedding', [])
                    if embedding:
                        _active_model = model_name
                        return embedding
                except Exception as me:
                    continue

        except Exception as e:
            logger.warning(f"Gemini embedding API call failed: {e}. Falling back to deterministic vector.")

    return _generate_deterministic_vector(text, dimension=settings.EMBEDDING_DIMENSION)


def get_embeddings_batch(texts: List[str], task_type: str = "retrieval_document") -> List[List[float]]:
    """
    Generate embeddings for a batch of text chunks.
    """
    if not texts:
        return []

    return [get_embedding(t, task_type=task_type) for t in texts]
