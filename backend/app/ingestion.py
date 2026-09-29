import hashlib
import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

from backend.app.config import settings, DOCUMENTS_RAW_DIR, DOCUMENTS_PROCESSED_DIR
from backend.app.chunking import process_pdf_document
from backend.app.embeddings import get_embeddings_batch
from backend.app.database import db_client
from backend.app.schemas import IngestResponse, DocumentChunk

logger = logging.getLogger("bis_ingestion")

METADATA_FILE = DOCUMENTS_PROCESSED_DIR / "metadata.json"
DOCUMENTS_FAILED_DIR = BASE_DIR = Path(__file__).resolve().parent.parent.parent / "documents" / "failed"

# Comprehensive official metadata dictionary mapping for BIS documents
DOCUMENT_METADATA_REGISTRY = {
    # Acts
    "BIS_Act_2016_Official": {
        "title": "The Bureau of Indian Standards Act, 2016 (Act No. 11 of 2016)",
        "document_type": "act",
        "category": "acts",
        "standard_number": None,
        "publication_date": "2016-03-22",
        "effective_date": "2017-10-12",
        "version": "Act 11 of 2016",
        "source_url": "https://www.bis.gov.in/the-bis-act-2016/"
    },
    "BIS_Act_2016_Handbook": {
        "title": "BIS Act 2016 Reference Handbook",
        "document_type": "act",
        "category": "acts",
        "standard_number": None,
        "publication_date": "2017-10-12",
        "effective_date": "2017-10-12",
        "version": "1.0",
        "source_url": "https://www.bis.gov.in/the-bis-act-2016/"
    },
    "BIS_Enforcement_and_Search_Seizure_Guidelines": {
        "title": "BIS Enforcement, Search, Seizure & Prosecution Manual",
        "document_type": "guideline",
        "category": "acts",
        "standard_number": None,
        "publication_date": "2023-01-15",
        "effective_date": "2023-01-15",
        "version": "2.0",
        "source_url": "https://www.bis.gov.in/enforcement-raids/"
    },
    # Rules
    "BIS_Rules_2018_and_Amendments": {
        "title": "Bureau of Indian Standards Rules, 2018 (G.S.R. 584(E) with Amendments)",
        "document_type": "rule",
        "category": "rules",
        "standard_number": None,
        "publication_date": "2018-06-25",
        "effective_date": "2018-06-25",
        "amendment_date": "2022-08-10",
        "amendment_information": "Incorporates 2020 MSME and 2022 Electronic Sample Tracking Amendments",
        "version": "2022 Consolidated",
        "source_url": "https://www.bis.gov.in/rules-and-regulations/"
    },
    # Regulations
    "BIS_Conformity_Assessment_Regulations_2018_Amended": {
        "title": "BIS (Conformity Assessment) Regulations, 2018 (Amended 2021, 2023)",
        "document_type": "regulation",
        "category": "regulations",
        "standard_number": None,
        "publication_date": "2018-06-04",
        "effective_date": "2018-06-04",
        "amendment_date": "2023-05-18",
        "version": "2023 Consolidated",
        "source_url": "https://www.bis.gov.in/conformity-assessment-regulations/"
    },
    "BIS_Hallmarking_Regulations_2018_Amended": {
        "title": "BIS (Hallmarking) Regulations, 2018 (with Amendments)",
        "document_type": "regulation",
        "category": "regulations",
        "standard_number": None,
        "publication_date": "2018-06-14",
        "effective_date": "2018-06-14",
        "amendment_date": "2023-09-01",
        "version": "2023 Consolidated",
        "source_url": "https://www.bis.gov.in/hallmarking-regulations/"
    },
    # Certification
    "BIS_Product_Certification_Scheme_I_Manual": {
        "title": "BIS Product Certification Scheme-I (ISI Mark) Operating Manual",
        "document_type": "manual",
        "category": "certification",
        "standard_number": None,
        "publication_date": "2022-04-01",
        "effective_date": "2022-04-01",
        "version": "3.1",
        "source_url": "https://www.bis.gov.in/product-certification-scheme-1/"
    },
    "BIS_Product_Certification_Scheme_I_Guide": {
        "title": "BIS Product Certification Scheme-I Guide",
        "document_type": "manual",
        "category": "certification",
        "standard_number": None,
        "publication_date": "2022-01-01",
        "effective_date": "2022-01-01",
        "version": "2.0",
        "source_url": "https://www.bis.gov.in/product-certification/"
    },
    "BIS_Compulsory_Registration_Scheme_CRS_Guide": {
        "title": "BIS Compulsory Registration Scheme (CRS) Scheme-II Guidelines",
        "document_type": "manual",
        "category": "certification",
        "standard_number": "IS 13252 / IS 16046",
        "publication_date": "2023-02-15",
        "effective_date": "2023-02-15",
        "version": "4.0",
        "source_url": "https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/crs"
    },
    "BIS_Foreign_Manufacturers_Certification_Scheme_FMCS": {
        "title": "BIS Foreign Manufacturers Certification Scheme (FMCS) Guidelines",
        "document_type": "guideline",
        "category": "certification",
        "standard_number": None,
        "publication_date": "2022-09-01",
        "effective_date": "2022-09-01",
        "version": "2.5",
        "source_url": "https://www.bis.gov.in/fmcs-overview/"
    },
    "BIS_MSME_Startups_and_Women_Entrepreneurs_Concessions": {
        "title": "BIS Policy on Concessions & Rebates for MSMEs, Startups & Women Entrepreneurs",
        "document_type": "circular",
        "category": "certification",
        "standard_number": None,
        "publication_date": "2023-06-01",
        "effective_date": "2023-06-01",
        "version": "2023 Release",
        "source_url": "https://www.bis.gov.in/msme-concessions/"
    },
    "BIS_Scheme_IV_Batch_Certification_Procedures": {
        "title": "BIS Scheme-IV Batch / Lot Certification Procedures",
        "document_type": "procedure",
        "category": "certification",
        "standard_number": "IS 2500",
        "publication_date": "2021-11-10",
        "effective_date": "2021-11-10",
        "version": "1.8",
        "source_url": "https://www.bis.gov.in/scheme-iv-batch/"
    },
    "BIS_Scheme_X_Modular_Certification_Framework": {
        "title": "BIS Scheme-X Modular & Capital Goods Certification Framework",
        "document_type": "procedure",
        "category": "certification",
        "standard_number": None,
        "publication_date": "2022-08-20",
        "effective_date": "2022-08-20",
        "version": "1.2",
        "source_url": "https://www.bis.gov.in/scheme-x-modular/"
    },
    # Hallmarking
    "BIS_Gold_and_Silver_Hallmarking_Guidelines_2024": {
        "title": "BIS Gold and Silver Jewellery Hallmarking Guidelines (2024 Edition)",
        "document_type": "guideline",
        "category": "hallmarking",
        "standard_number": "IS 1417 / IS 2112",
        "publication_date": "2024-01-10",
        "effective_date": "2024-01-10",
        "version": "2024.1",
        "source_url": "https://www.bis.gov.in/hallmarking-overview/"
    },
    "BIS_Gold_and_Silver_Hallmarking_Guidelines": {
        "title": "BIS Gold and Silver Hallmarking Guidelines",
        "document_type": "guideline",
        "category": "hallmarking",
        "standard_number": "IS 1417",
        "publication_date": "2021-06-01",
        "effective_date": "2021-06-01",
        "version": "1.0",
        "source_url": "https://www.bis.gov.in/hallmarking-overview/"
    },
    "BIS_Jeweller_Registration_and_HUID_Portal_Guide": {
        "title": "BIS Jeweller Registration & HUID Portal User Manual",
        "document_type": "manual",
        "category": "hallmarking",
        "standard_number": None,
        "publication_date": "2023-04-15",
        "effective_date": "2023-04-15",
        "version": "3.0",
        "source_url": "https://www.manakonline.in/MANAK/hallmarking"
    },
    "BIS_Assaying_and_Hallmarking_Centres_AHC_Manual": {
        "title": "BIS Assaying & Hallmarking Centres (AHC) Technical & Quality Manual",
        "document_type": "manual",
        "category": "hallmarking",
        "standard_number": "IS 15820 / IS 1418",
        "publication_date": "2022-10-05",
        "effective_date": "2022-10-05",
        "version": "2.2",
        "source_url": "https://www.bis.gov.in/ahc-recognition/"
    },
    # Laboratories
    "BIS_Central_and_Regional_Laboratories_Directory": {
        "title": "BIS Central & Regional Laboratories Infrastructure Directory",
        "document_type": "directory",
        "category": "laboratories",
        "standard_number": "ISO/IEC 17025",
        "publication_date": "2023-07-01",
        "effective_date": "2023-07-01",
        "version": "2023 Edition",
        "source_url": "https://www.bis.gov.in/laboratory-network/"
    },
    "BIS_Laboratory_Recognition_Scheme_LRS_2020": {
        "title": "BIS Laboratory Recognition Scheme (LRS) 2020 and Audit Rules",
        "document_type": "scheme",
        "category": "laboratories",
        "standard_number": "ISO/IEC 17025",
        "publication_date": "2020-09-15",
        "effective_date": "2020-09-15",
        "version": "LRS 2020",
        "source_url": "https://www.bis.gov.in/laboratory-recognition-scheme/"
    },
    "BIS_Testing_Manual_and_LIMS_Portal_Guidelines": {
        "title": "BIS Testing Manual & LIMS Portal Digital Guidelines",
        "document_type": "manual",
        "category": "laboratories",
        "standard_number": None,
        "publication_date": "2023-03-20",
        "effective_date": "2023-03-20",
        "version": "2.0",
        "source_url": "https://www.bis.gov.in/lims-portal/"
    },
    "BIS_Laboratory_Testing_and_Recognition_Manual": {
        "title": "BIS Laboratory Testing and Recognition Manual",
        "document_type": "manual",
        "category": "laboratories",
        "standard_number": "ISO/IEC 17025",
        "publication_date": "2021-01-01",
        "effective_date": "2021-01-01",
        "version": "1.0",
        "source_url": "https://www.bis.gov.in/laboratory-network/"
    },
    # Standards
    "BIS_Standardization_Process_and_Committee_Structure": {
        "title": "BIS Standardization Process, Division Councils & Committee Structure",
        "document_type": "handbook",
        "category": "standards",
        "standard_number": None,
        "publication_date": "2023-08-01",
        "effective_date": "2023-08-01",
        "version": "4.0",
        "source_url": "https://standards.bis.gov.in/"
    },
    "IS_302_Household_Electrical_Appliances_Safety_Overview": {
        "title": "Indian Standard Specification IS 302 (Part 1): 2024 - Safety of Household Electrical Appliances",
        "document_type": "standard",
        "category": "standards",
        "standard_number": "IS 302",
        "publication_date": "2024-02-01",
        "effective_date": "2024-02-01",
        "version": "2024 Edition",
        "source_url": "https://standards.bis.gov.in/is302"
    },
    "IS_1786_High_Strength_Deformed_Steel_Rebar_Standard": {
        "title": "Indian Standard Specification IS 1786 : 2008 - High Strength Deformed Steel Bars (TMT)",
        "document_type": "standard",
        "category": "standards",
        "standard_number": "IS 1786",
        "publication_date": "2008-05-15",
        "effective_date": "2008-05-15",
        "version": "Reaffirmed 2023",
        "source_url": "https://standards.bis.gov.in/is1786"
    },
    "IS_9873_Safety_of_Toys_Specification_Guide": {
        "title": "Indian Standard Specification IS 9873 (Parts 1 to 9) - Safety of Toys",
        "document_type": "standard",
        "category": "standards",
        "standard_number": "IS 9873",
        "publication_date": "2020-08-01",
        "effective_date": "2020-08-01",
        "version": "2020 Consolidated",
        "source_url": "https://standards.bis.gov.in/is9873"
    },
    # Reference Handbooks
    "BIS_Handbook_Electrical_Engineering_and_Power_Apparatus": {
        "title": "BIS Reference Handbook: Electrical Engineering & Power Apparatus (Transformers, Cables, Motors)",
        "document_type": "handbook",
        "category": "handbooks",
        "standard_number": "IS 1180 / IS 694 / IS 12615",
        "publication_date": "2023-11-01",
        "effective_date": "2023-11-01",
        "version": "2.0",
        "source_url": "https://standards.bis.gov.in/handbooks/electrical"
    },
    "BIS_Handbook_Electronics_AI_IoT_and_Software_Testing": {
        "title": "BIS Reference Handbook: Emerging Technologies - AI, IoT, Cybersecurity & Software Testing",
        "document_type": "handbook",
        "category": "handbooks",
        "standard_number": "IS/ISO 22989 / IS/ISO 42001 / IS 29119",
        "publication_date": "2024-03-01",
        "effective_date": "2024-03-01",
        "version": "1.0",
        "source_url": "https://standards.bis.gov.in/handbooks/litd"
    },
    "BIS_Handbook_Building_Materials_and_Civil_Engineering": {
        "title": "BIS Reference Handbook: Building Materials & Civil Engineering (Cement, Concrete, Rebar)",
        "document_type": "handbook",
        "category": "handbooks",
        "standard_number": "IS 269 / IS 456 / IS 1786",
        "publication_date": "2023-05-10",
        "effective_date": "2023-05-10",
        "version": "3.0",
        "source_url": "https://standards.bis.gov.in/handbooks/civil"
    },
    "BIS_Handbook_Refrigeration_Air_Conditioning_and_Renewable_Energy": {
        "title": "BIS Reference Handbook: HVAC, Refrigeration & Renewable Energy (Solar PV, Air Conditioners)",
        "document_type": "handbook",
        "category": "handbooks",
        "standard_number": "IS 1391 / IS 14286 / IS 16221",
        "publication_date": "2023-09-12",
        "effective_date": "2023-09-12",
        "version": "1.5",
        "source_url": "https://standards.bis.gov.in/handbooks/energy"
    },
    "BIS_Handbook_Mechanical_Testing_and_Safety_Risk_Assessment": {
        "title": "BIS Reference Handbook: Mechanical Testing Methods & Machinery Safety Risk Assessment",
        "document_type": "handbook",
        "category": "handbooks",
        "standard_number": "IS 1608 / IS 1757 / IS 1586",
        "publication_date": "2023-10-01",
        "effective_date": "2023-10-01",
        "version": "2.1",
        "source_url": "https://standards.bis.gov.in/handbooks/mechanical"
    },
    # Consumer Information
    "BIS_Consumer_Protection_Rights_and_Care_App_Handbook": {
        "title": "BIS Consumer Protection Rights & Care App Citizen Handbook",
        "document_type": "consumer_guide",
        "category": "consumer",
        "standard_number": None,
        "publication_date": "2023-12-01",
        "effective_date": "2023-12-01",
        "version": "4.0",
        "source_url": "https://www.bis.gov.in/consumer-affairs/"
    },
    "BIS_Consumer_Grievance_Redressal_Mechanism_and_FAQs": {
        "title": "BIS Consumer Grievance Redressal Mechanism & FAQs",
        "document_type": "consumer_guide",
        "category": "consumer",
        "standard_number": None,
        "publication_date": "2024-02-15",
        "effective_date": "2024-02-15",
        "version": "2024.1",
        "source_url": "https://www.bis.gov.in/consumer-faqs/"
    },
    "BIS_Care_App_and_Consumer_Rights_Booklet": {
        "title": "BIS Care App & Consumer Rights Booklet",
        "document_type": "booklet",
        "category": "consumer",
        "standard_number": None,
        "publication_date": "2021-08-01",
        "effective_date": "2021-08-01",
        "version": "1.0",
        "source_url": "https://www.bis.gov.in/consumer-affairs/"
    },
    # QCOs
    "BIS_Quality_Control_Orders_QCO_Compendium_2024": {
        "title": "BIS Quality Control Orders (QCO) Statutory Compendium 2024",
        "document_type": "qco",
        "category": "qco",
        "standard_number": "Section 16 Orders",
        "publication_date": "2024-01-01",
        "effective_date": "2024-01-01",
        "version": "2024 Compendium",
        "source_url": "https://www.bis.gov.in/product-certification/qco-notifications/"
    },
    "BIS_QCO_Toys_Safety_and_Footwear_Orders_Guide": {
        "title": "BIS Quality Control Orders Guide: Toys Safety & Footwear Mandates",
        "document_type": "qco",
        "category": "qco",
        "standard_number": "IS 9873 / IS 15844",
        "publication_date": "2023-07-15",
        "effective_date": "2023-07-15",
        "version": "2.0",
        "source_url": "https://www.bis.gov.in/qco-toys-footwear/"
    },
    "BIS_QCO_Steel_Products_Chemicals_and_Cables_Compendium": {
        "title": "BIS Quality Control Orders: Steel, Industrial Chemicals & Electric Cables",
        "document_type": "qco",
        "category": "qco",
        "standard_number": "IS 2062 / IS 252 / IS 694",
        "publication_date": "2023-11-20",
        "effective_date": "2023-11-20",
        "version": "1.5",
        "source_url": "https://www.bis.gov.in/qco-steel-chemicals/"
    },
    # Awareness & Booklets
    "BIS_Standards_Clubs_and_Educational_Outreach_Manual": {
        "title": "BIS Standards Clubs & Educational Outreach Manual for Schools and Colleges",
        "document_type": "awareness",
        "category": "awareness",
        "standard_number": None,
        "publication_date": "2023-06-15",
        "effective_date": "2023-06-15",
        "version": "3.0",
        "source_url": "https://www.bis.gov.in/standards-clubs/"
    },
    "BIS_National_Building_Code_NBC_2016_Awareness_Guide": {
        "title": "National Building Code of India (NBC 2016 - SP 7) Comprehensive Awareness Guide",
        "document_type": "awareness",
        "category": "awareness",
        "standard_number": "NBC 2016 / SP 7",
        "publication_date": "2016-12-01",
        "effective_date": "2016-12-01",
        "version": "SP 7 : 2016",
        "source_url": "https://standards.bis.gov.in/nbc2016"
    },
    "BIS_Overview_and_Milestones_Annual_Handbook": {
        "title": "Bureau of Indian Standards Overview, Milestones & Digital Transformation Handbook",
        "document_type": "booklet",
        "category": "booklets",
        "standard_number": None,
        "publication_date": "2024-01-06",
        "effective_date": "2024-01-06",
        "version": "2024 Annual Edition",
        "source_url": "https://www.bis.gov.in/about-us/"
    }
}


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA-256 hash of a file for exact duplicate and change detection."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def load_metadata_registry() -> List[Dict[str, Any]]:
    """Loads indexed documents registry from metadata.json."""
    if METADATA_FILE.exists():
        try:
            with open(METADATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read metadata.json: {e}")
    return []


def save_metadata_registry(registry: List[Dict[str, Any]]):
    """Saves updated registry to metadata.json."""
    DOCUMENTS_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)


def ingest_all_documents(force_reindex: bool = False) -> IngestResponse:
    """
    Controlled discovery and ingestion engine for official BIS documents:
    1. Discovers PDFs in documents/raw/ across all categories
    2. Performs SHA-256 duplicate verification
    3. Extracts text page-by-page, headings, and clause structures
    4. Handles extraction failures gracefully by isolating into documents/failed/
    5. Computes high-dimensional vector embeddings
    6. Upserts chunks into Supabase + Local Vector Store
    7. Updates processed metadata registry with rich document properties
    """
    DOCUMENTS_RAW_DIR.mkdir(parents=True, exist_ok=True)
    DOCUMENTS_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    DOCUMENTS_FAILED_DIR.mkdir(parents=True, exist_ok=True)

    registry = load_metadata_registry()
    indexed_hashes = {item.get("file_hash"): item for item in registry if "file_hash" in item}

    all_pdf_files = sorted(list(DOCUMENTS_RAW_DIR.rglob("*.pdf")), key=lambda p: p.name)
    logger.info(f"Discovered {len(all_pdf_files)} PDF files in {DOCUMENTS_RAW_DIR}")

    total_chunks_created = 0
    total_chunks_inserted = 0
    processed_count = 0
    duplicates_skipped = 0
    failed_count = 0
    indexed_docs = []
    errors = []

    for pdf_path in all_pdf_files:
        stem_name = pdf_path.stem
        try:
            file_hash = compute_file_hash(pdf_path)
            rel_path = pdf_path.relative_to(DOCUMENTS_RAW_DIR)
            category_folder = rel_path.parts[0] if len(rel_path.parts) > 1 else "general"

            # Lookup rich metadata
            meta_info = DOCUMENT_METADATA_REGISTRY.get(stem_name, {})
            title = meta_info.get("title", stem_name.replace("_", " ").title())
            category = meta_info.get("category", category_folder)
            document_type = meta_info.get("document_type", category_folder)
            standard_number = meta_info.get("standard_number")
            publication_date = meta_info.get("publication_date")
            effective_date = meta_info.get("effective_date")
            amendment_date = meta_info.get("amendment_date")
            amendment_info = meta_info.get("amendment_information")
            version = meta_info.get("version", "1.0")
            source_url = meta_info.get("source_url", f"https://www.bis.gov.in/{category}/")

            # Duplicate Check
            if not force_reindex and file_hash in indexed_hashes:
                logger.info(f"Skipping identical indexed document (hash: {file_hash[:8]}): {pdf_path.name}")
                duplicates_skipped += 1
                continue

            processed_count += 1
            doc_id = f"bis_{file_hash[:10]}"

            # Process & Chunk PDF
            chunks: List[DocumentChunk] = process_pdf_document(
                file_path=pdf_path,
                document_id=doc_id,
                document_name=stem_name,
                category=category,
                standard_number=standard_number,
                title=title,
                source_url=source_url,
                publication_date=publication_date,
                amendment_information=amendment_info,
                chunk_size=900,
                chunk_overlap=120
            )

            if not chunks:
                logger.warning(f"Text extraction yielded 0 chunks for {pdf_path.name}. Moving to failed directory.")
                failed_dest = DOCUMENTS_FAILED_DIR / pdf_path.name
                shutil.copy2(pdf_path, failed_dest)
                failed_count += 1
                errors.append(f"Failed to extract readable text from {pdf_path.name}")
                continue

            total_chunks_created += len(chunks)

            # Assign document_type and dates to chunks
            for c in chunks:
                c.document_type = document_type
                c.effective_date = effective_date
                c.amendment_date = amendment_date
                c.version = version

            # Generate Embeddings in batch
            chunk_texts = [c.content for c in chunks]
            embeddings = get_embeddings_batch(chunk_texts, task_type="retrieval_document")

            for i, emb in enumerate(embeddings):
                chunks[i].embedding = emb

            # Insert into Supabase and local vector store
            inserted = db_client.insert_chunks(chunks)
            total_chunks_inserted += inserted

            doc_record = {
                "document_id": doc_id,
                "document_name": stem_name,
                "title": title,
                "document_type": document_type,
                "category": category,
                "file_name": pdf_path.name,
                "standard_number": standard_number,
                "source_url": source_url,
                "publication_date": publication_date,
                "effective_date": effective_date,
                "amendment_date": amendment_date,
                "amendment_information": amendment_info,
                "version": version,
                "file_hash": file_hash,
                "total_pages": chunks[-1].page_number if chunks else 1,
                "chunks_count": len(chunks),
                "ingested_at": datetime.now(timezone.utc).isoformat(),
                "status": "indexed"
            }

            # Update registry
            registry = [item for item in registry if item.get("document_name") != stem_name and item.get("file_hash") != file_hash]
            registry.append(doc_record)
            indexed_docs.append(doc_record)
            logger.info(f"Successfully ingested [{processed_count}] {pdf_path.name} ({len(chunks)} chunks)")

        except Exception as e:
            err_msg = f"Error processing {pdf_path.name}: {str(e)}"
            logger.error(err_msg, exc_info=True)
            errors.append(err_msg)
            failed_count += 1
            try:
                failed_dest = DOCUMENTS_FAILED_DIR / pdf_path.name
                shutil.copy2(pdf_path, failed_dest)
            except Exception:
                pass

    save_metadata_registry(registry)

    return IngestResponse(
        status="success" if not errors else ("partial_success" if indexed_docs else "failed"),
        documents_processed=processed_count,
        documents_skipped=duplicates_skipped,
        total_chunks_created=total_chunks_created,
        total_chunks_indexed=total_chunks_inserted,
        duplicates_skipped=duplicates_skipped,
        failed_count=failed_count,
        indexed_documents=indexed_docs,
        errors=errors
    )
