import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import pypdf

from backend.app.schemas import DocumentChunk

logger = logging.getLogger("bis_chunking")

# Common regex patterns to detect section headers in legal/standards documents
SECTION_PATTERNS = [
    re.compile(r'^(SECTION\s+\d+[\.:]?\s*[^\n]*)', re.IGNORECASE | re.MULTILINE),
    re.compile(r'^(CHAPTER\s+[IVXLCDM\d]+[\.:]?\s*[^\n]*)', re.IGNORECASE | re.MULTILINE),
    re.compile(r'^(CLAUSE\s+\d+[\.:]?\s*[^\n]*)', re.IGNORECASE | re.MULTILINE),
    re.compile(r'^(RULE\s+\d+[\.:]?\s*[^\n]*)', re.IGNORECASE | re.MULTILINE),
    re.compile(r'^(SCHEDULE\s+[IVXLCDM\d]*[\.:]?\s*[^\n]*)', re.IGNORECASE | re.MULTILINE),
    re.compile(r'^(\d+\.\d+\s+[A-Z][^\n]*)', re.MULTILINE),
    re.compile(r'^(\d+\s+[A-Z][A-Za-z\s]{3,40}:)', re.MULTILINE),
]


def clean_text(text: str) -> str:
    """Clean extracted PDF text while preserving structural linebreaks."""
    if not text:
        return ""
    # Normalize unicode whitespace
    text = text.replace('\xa0', ' ').replace('\r\n', '\n').replace('\r', '\n')
    # Collapse multiple blank lines to at most two
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove control characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text.strip()


def extract_sections_from_page(page_text: str) -> str:
    """Detects active section title in a page."""
    for pattern in SECTION_PATTERNS:
        match = pattern.search(page_text)
        if match:
            return match.group(1).strip()
    return "General"


def split_text_into_chunks(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 150
) -> List[str]:
    """
    Intelligently chunks text using LangChain RecursiveCharacterTextSplitter
    or a resilient regex-based fallback.
    """
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\n\n\n",
                "\n\n",
                "\nSection ",
                "\nClause ",
                "\nChapter ",
                "\nRule ",
                "\n",
                ". ",
                ", ",
                " ",
                ""
            ]
        )
        return splitter.split_text(text)
    except Exception:
        # Resilient fallback splitter
        chunks = []
        start = 0
        text_len = len(text)
        while start < text_len:
            end = min(start + chunk_size, text_len)
            if end < text_len:
                # Find nearest sentence boundary
                split_at = max(
                    text.rfind('. ', start, end),
                    text.rfind('\n', start, end)
                )
                if split_at > start + (chunk_size // 2):
                    end = split_at + 1
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = end - chunk_overlap if end < text_len else text_len
        return chunks


def process_pdf_document(
    file_path: Path,
    document_id: str,
    document_name: str,
    category: str = "general",
    standard_number: Optional[str] = None,
    title: Optional[str] = None,
    source_url: Optional[str] = None,
    publication_date: Optional[str] = None,
    amendment_information: Optional[str] = None,
    chunk_size: int = 1000,
    chunk_overlap: int = 150
) -> List[DocumentChunk]:
    """
    Extracts text page-by-page from a PDF, detects sections, and produces structured DocumentChunks.
    """
    chunks_list: List[DocumentChunk] = []
    chunk_counter = 0

    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return []

    try:
        reader = pypdf.PdfReader(str(file_path))
        total_pages = len(reader.pages)
        logger.info(f"Processing '{file_path.name}' ({total_pages} pages)...")

        current_section = "Introduction"

        for page_idx, page in enumerate(reader.pages):
            page_number = page_idx + 1
            raw_text = page.extract_text() or ""
            cleaned_page = clean_text(raw_text)

            if not cleaned_page or len(cleaned_page.strip()) < 20:
                continue

            detected_sec = extract_sections_from_page(cleaned_page)
            if detected_sec != "General":
                current_section = detected_sec

            page_chunks = split_text_into_chunks(
                cleaned_page,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )

            for chunk_text in page_chunks:
                if len(chunk_text.strip()) < 15:
                    continue

                chunk_obj = DocumentChunk(
                    document_id=document_id,
                    document_name=document_name,
                    file_name=file_path.name,
                    category=category,
                    standard_number=standard_number,
                    title=title or document_name,
                    content=chunk_text,
                    page_number=page_number,
                    section=current_section,
                    source_url=source_url,
                    publication_date=publication_date,
                    amendment_information=amendment_information,
                    chunk_index=chunk_counter,
                    metadata={
                        "total_pages": total_pages,
                        "file_size_bytes": file_path.stat().st_size,
                        "char_count": len(chunk_text)
                    }
                )
                chunks_list.append(chunk_obj)
                chunk_counter += 1

        logger.info(f"Generated {len(chunks_list)} chunks from {file_path.name}")
        return chunks_list

    except Exception as e:
        logger.error(f"Error extracting PDF '{file_path.name}': {e}")
        return []
