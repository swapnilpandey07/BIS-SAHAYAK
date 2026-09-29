import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOCUMENTS_RAW_DIR = BASE_DIR / "documents" / "raw"
DOCUMENTS_PROCESSED_DIR = BASE_DIR / "documents" / "processed"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(BASE_DIR / ".env", BASE_DIR / "backend" / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Google Gemini settings
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "models/text-embedding-004"
    EMBEDDING_DIMENSION: int = 768

    # Supabase PostgreSQL & pgvector settings
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_TABLE: str = "bis_documents"

    # RAG Retrieval Settings
    RAG_TOP_K: int = 6
    SIMILARITY_THRESHOLD: float = 0.30
    ENABLE_HYBRID_SEARCH: bool = True

    # Server settings
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:5173"
    ENVIRONMENT: str = "development"

    # Paths
    DOCS_RAW_PATH: Path = DOCUMENTS_RAW_DIR
    DOCS_PROCESSED_PATH: Path = DOCUMENTS_PROCESSED_DIR


settings = Settings()
