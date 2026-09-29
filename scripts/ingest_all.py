"""
Script to ingest all raw BIS documents into the vector store.
Usage: python scripts/ingest_all.py
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.ingest_documents import main

if __name__ == "__main__":
    main()
