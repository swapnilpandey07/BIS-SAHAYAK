"""
Command-line utility for ingesting authorized BIS documents into the knowledge base.
Usage: python backend/ingest_documents.py [--force]
"""

import sys
import argparse
import logging
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.ingestion import ingest_all_documents


def main():
    parser = argparse.ArgumentParser(description="Ingest BIS PDF documents into Supabase Vector Store")
    parser.add_argument("--force", action="store_true", help="Force re-indexing of already processed documents")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    print("\n=======================================================")
    print("  BIS Intelligent Assistant - Document Ingestion Pipeline")
    print("=======================================================\n")

    result = ingest_all_documents(force_reindex=args.force)

    print("\n-------------------------------------------------------")
    print(f"Ingestion Status:            {result.status.upper()}")
    print(f"Total Documents Processed:   {result.documents_processed}")
    print(f"Duplicates Skipped:          {result.duplicates_skipped}")
    print(f"Total Chunks Created:        {result.total_chunks_created}")
    print(f"Total Chunks Inserted:       {result.total_chunks_indexed}")
    print(f"Failed Documents:            {result.failed_count}")
    print("-------------------------------------------------------")
    
    print(f"\nIndexed Documents Summary ({len(result.indexed_documents)}):")
    for idx, doc in enumerate(result.indexed_documents, 1):
        print(f"  [{idx:02d}] {doc.get('title')} ({doc.get('category')} / {doc.get('document_type')}): {doc.get('chunks_count')} chunks (Pages: {doc.get('total_pages')})")

    if result.errors:
        print(f"\nErrors / Warnings ({len(result.errors)}):")
        for err in result.errors:
            print(f"  - {err}")
            
    print("\n=======================================================\n")


if __name__ == "__main__":
    main()
