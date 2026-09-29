import re
import logging
from typing import List, Dict, Any, Optional, Tuple

from backend.app.config import settings
from backend.app.embeddings import get_embedding
from backend.app.database import db_client, local_vector_store
from backend.app.schemas import SourceCitation

logger = logging.getLogger("bis_retrieval")

# Regex to detect standard numbers (e.g., IS 302, IS 1786, IS 9873, IS 1180, IS 13252, IS 16046, IS 269, IS:302)
STD_REGEX = re.compile(r'\b(?:IS|is)[\s:\-]*(\d+)(?:\s*[:\-]\s*(?:Part|part|Pt)\s*(\d+))?', re.IGNORECASE)

# Common multilingual synonym & category mapping (English, Hindi, Hinglish)
MULTILINGUAL_INTENTS = [
    # Acts / Law / Governance / Penalties
    (r'\b(act|act 2016|law|dhara|section|penalty|penalties|saza|fine|jail|imprisonment|court|magistrate|compounding|enforcement|raid|seizure|chhape|chhapemari|adhiniyam)\b', 'acts'),
    # Rules & Governance
    (r'\b(rules|rules 2018|niyam|executive committee|director general|dg|powers|appeal)\b', 'rules'),
    # Regulations
    (r'\b(conformity assessment regulation|hallmarking regulation|viniyam|viniyaman)\b', 'regulations'),
    # Hallmarking / Gold / Jewellery
    (r'\b(hallmark|hallmarking|huid|gold|sona|chandi|silver|jewel|jeweller|jewellery|karat|carat|fineness|22k|18k|14k|916|750|585|ahc|assay|assaying|cupellation|fire assay)\b', 'hallmarking'),
    # Certification / Schemes / ISI Mark / FMCS / CRS / MSME
    (r'\b(certif|licence|license|isi mark|isi stamp|manak|scheme i|scheme-i|scheme 1|scheme ii|scheme 2|scheme iv|scheme 4|scheme x|scheme 10|crs|compulsory registration|fmcs|foreign manufacturer|msme|startup|concession|chhoot|anudan|surveillance|market sample|renewal|rol|gol|cml)\b', 'certification'),
    # Laboratories / Testing / LRS / LIMS
    (r'\b(lab|laboratory|testing|janch|test report|lims|lrs|nabl|iso 17025|sahibabad|blind coding|etr|sample drawing)\b', 'laboratories'),
    # Quality Control Orders (QCO)
    (r'\b(qco|quality control order|mandatory order|anivarya|toys|khilone|footwear|jute|shoes|steel rebar|chemicals|caustic soda|cables)\b', 'qco'),
    # Reference Handbooks & Engineering
    (r'\b(handbook|transformer|electric cable|switchgear|induction motor|artificial intelligence|ai|iot|software testing|sqa|building material|cement|concrete|refrigeration|ac|hvac|solar pv|mechanical testing|tensile|charpy|hardness)\b', 'handbooks'),
    # Consumer Information & Complaints
    (r'\b(consumer|grahak|care app|bis care|complaint|shikayat|grievance|verify|asli|nakli|counterfeit|fake|verification)\b', 'consumer'),
    # Standards & Standardization Process
    (r'\b(standardization|manakikaran|division council|committee|nwip|wide circulation|stages|formulation|adoption|iso|iec)\b', 'standards'),
    # Awareness & NBC 2016
    (r'\b(standards club|school|college|youth|nbc|nbc 2016|national building code|building code|sp 7)\b', 'awareness'),
    # Booklets & Milestones
    (r'\b(history|milestone|established|1947|annual report|overview)\b', 'booklets'),
]


def extract_search_entities(query: str) -> Dict[str, Any]:
    """Extracts known standard numbers, sections, or category hints from English, Hindi, and Hinglish queries."""
    entities = {}
    
    # Extract standard number
    std_match = STD_REGEX.search(query)
    if std_match:
        base_num = std_match.group(1)
        part_num = std_match.group(2)
        if part_num:
            entities["standard_number"] = f"IS {base_num}"
            entities["full_standard"] = f"IS {base_num} Part {part_num}"
        else:
            entities["standard_number"] = f"IS {base_num}"

    # Extract category from multilingual intents
    query_lower = query.lower()
    for pattern, cat in MULTILINGUAL_INTENTS:
        if re.search(pattern, query_lower, re.IGNORECASE):
            entities["category"] = cat
            break

    return entities


def retrieve_relevant_chunks(
    query: str,
    top_k: Optional[int] = None,
    category_filter: Optional[str] = None,
    document_type_filter: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], List[SourceCitation]]:
    """
    Hybrid semantic + keyword + metadata retrieval engine for BIS queries.
    Returns:
      - raw retrieved chunk dictionaries with score
      - structured SourceCitation list for frontend
    """
    k = top_k or settings.RAG_TOP_K
    threshold = settings.SIMILARITY_THRESHOLD

    entities = extract_search_entities(query)
    target_category = category_filter or entities.get("category")
    target_std = entities.get("standard_number")

    # 1. Compute query vector embedding
    query_vector = get_embedding(query, task_type="retrieval_query")

    # 2. Vector search (via Supabase or local store)
    vector_results = db_client.search(
        query_embedding=query_vector,
        query_text=query,
        top_k=k * 3,
        similarity_threshold=threshold * 0.70,
        category=target_category,
        standard_number=target_std
    )

    # 3. Keyword / Full-text search
    keyword_results = local_vector_store.keyword_search(query, top_k=k * 2)

    # 4. Hybrid merge & reranking
    combined_map: Dict[str, Dict[str, Any]] = {}

    for item in vector_results:
        key = f"{item.get('document_name')}_{item.get('page_number')}_{item.get('chunk_index')}"
        combined_map[key] = dict(item)
        combined_map[key]["score"] = float(item.get("similarity", 0.0))

    for item in keyword_results:
        key = f"{item.get('document_name')}_{item.get('page_number')}_{item.get('chunk_index')}"
        kw_score = float(item.get("keyword_score", 0.0))
        kw_boost = min(kw_score * 0.12, 0.45)

        if key in combined_map:
            combined_map[key]["score"] = combined_map[key].get("score", 0.0) + kw_boost
        else:
            item_copy = dict(item)
            item_copy["score"] = kw_boost
            item_copy["similarity"] = kw_boost
            combined_map[key] = item_copy

    # Standard Number exact match bonus
    if target_std:
        std_target_lower = target_std.lower()
        for key, item in combined_map.items():
            std_in_item = (item.get("standard_number") or "").lower()
            content_in_item = (item.get("content") or "").lower()
            doc_name_in_item = (item.get("document_name") or "").lower()

            if std_target_lower in std_in_item or std_target_lower in doc_name_in_item:
                combined_map[key]["score"] += 0.40
            elif std_target_lower in content_in_item:
                combined_map[key]["score"] += 0.25

    # Document type filter if requested
    if document_type_filter:
        doc_type_lower = document_type_filter.lower()
        for key in list(combined_map.keys()):
            if (combined_map[key].get("document_type") or "").lower() != doc_type_lower:
                del combined_map[key]

    # Sort descending by final combined score
    ranked_chunks = sorted(combined_map.values(), key=lambda x: x.get("score", 0.0), reverse=True)

    # Grounding filter: ensure chunks meet threshold
    final_chunks = []
    citations: List[SourceCitation] = []
    seen_citations = set()

    # Strict standard number requirement: If a specific standard is requested (e.g. IS 999999), require at least one matching chunk
    if target_std:
        any_std_match = any(
            target_std.lower() in (c.get("standard_number") or "").lower() or
            target_std.lower() in (c.get("document_name") or "").lower() or
            target_std.lower() in (c.get("content") or "").lower()
            for c in ranked_chunks
        )
        if not any_std_match:
            logger.info(f"Target standard '{target_std}' was requested but not found in any BIS documents. Returning empty context.")
            return [], []

    for chunk in ranked_chunks[:k]:
        score = chunk.get("score", 0.0)
        has_std_match = bool(target_std and (
            target_std.lower() in (chunk.get("standard_number") or "").lower() or
            target_std.lower() in (chunk.get("document_name") or "").lower() or
            target_std.lower() in (chunk.get("content") or "").lower()
        ))

        # Strict score threshold
        min_required_score = 0.38 if not has_std_match else 0.20
        if score < min_required_score:
            continue

        final_chunks.append(chunk)

        cite_key = f"{chunk.get('document_name')}_{chunk.get('page_number')}"
        if cite_key not in seen_citations:
            seen_citations.add(cite_key)
            citations.append(
                SourceCitation(
                    document_name=chunk.get("document_name", "BIS Official Document"),
                    file_name=chunk.get("file_name"),
                    title=chunk.get("title") or chunk.get("document_name"),
                    page_number=chunk.get("page_number"),
                    section=chunk.get("section"),
                    standard_number=chunk.get("standard_number"),
                    category=chunk.get("category"),
                    document_type=chunk.get("document_type"),
                    version=chunk.get("version"),
                    source_url=chunk.get("source_url"),
                    similarity=round(float(chunk.get("similarity") or score), 3),
                    snippet=chunk.get("content", "")[:220] + "..."
                )
            )

    logger.info(f"Retrieved {len(final_chunks)} relevant chunks for query: '{query}'")
    return final_chunks, citations


def format_context_for_prompt(chunks: List[Dict[str, Any]]) -> str:
    """Formats retrieved chunks into clear, authoritative context blocks for the LLM."""
    if not chunks:
        return "NO RELEVANT BIS DOCUMENTS FOUND."

    blocks = []
    for i, c in enumerate(chunks, 1):
        doc_name = c.get("title") or c.get("document_name", "Unknown Document")
        page_no = c.get("page_number", "N/A")
        sec = c.get("section", "General")
        std_no = f" [Standard: {c.get('standard_number')}]" if c.get("standard_number") else ""
        ver = f" [Version: {c.get('version')}]" if c.get("version") else ""
        content = c.get("content", "").strip()

        block = (
            f"[Source {i}: {doc_name} | Page: {page_no} | Section: {sec}{std_no}{ver}]\n"
            f"{content}\n"
        )
        blocks.append(block)

    return "\n---\n".join(blocks)
