# BIS Intelligent Assistant (SIH Problem Statement 26107)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5.4-646CFF.svg)](https://vitejs.dev/)
[![Supabase pgvector](https://img.shields.io/badge/Supabase-pgvector-3ECF8E.svg)](https://supabase.com/)
[![Google Gemini](https://img.shields.io/badge/Google-Gemini_AI-4285F4.svg)](https://ai.google.dev/)

> **A Production-Ready, Multilingual Retrieval-Augmented Generation (RAG) AI Assistant for the Bureau of Indian Standards (BIS).**

---

## 📑 Table of Contents
1. [Project Overview](#-project-overview)
2. [Key Capabilities](#-key-capabilities)
3. [Architecture & RAG Pipeline](#-architecture--rag-pipeline)
4. [Project Structure](#-project-structure)
5. [Prerequisites & System Setup](#-prerequisites--system-setup)
6. [Supabase & pgvector Database Setup](#-supabase--pgvector-database-setup)
7. [Environment Configuration (.env)](#-environment-configuration-env)
8. [Document Collection & Ingestion Pipeline](#-document-collection--ingestion-pipeline)
9. [Running the Application Locally](#-running-the-application-locally)
10. [Automated Testing & Verification](#-automated-testing--verification)
11. [Multilingual Support](#-multilingual-support)
12. [API Documentation (Swagger UI)](#-api-documentation-swagger-ui)
13. [Docker & Containerized Deployment](#-docker--containerized-deployment)
14. [Troubleshooting & FAQ](#-troubleshooting--faq)

---

## 🌟 Project Overview

The **BIS Intelligent Assistant** is an end-to-end, production-grade AI system designed for **Smart India Hackathon (SIH) Problem Statement 26107**. It enables citizens, industry manufacturers, conformity testing bodies, laboratory personnel, and legal auditors to query authorized Bureau of Indian Standards (BIS) documentation in **English**, **हिंदी (Hindi)**, and **Hinglish**.

### Strict Anti-Hallucination Grounding
Unlike generic chatbots that guess or hallucinate regulations, the BIS Intelligent Assistant adheres to a strict grounding protocol:
- **Zero Invention:** Generates answers **only** when supported by verified chunks retrieved from indexed BIS official documents.
- **Explicit Refusal:** If an inquiry falls outside indexed materials, the assistant reliably responds:
  > *"I could not verify this information from the available BIS documents."*
- **Traceable Source Citations:** Every factual response shows the exact **Document Name**, **Page Number**, **Section**, and link to the official BIS portal.

---

## 🚀 Key Capabilities

- 📄 **Page-Aware PDF Parsing:** Preserves page numbers, clause hierarchies, standard identifiers, and section titles during chunking.
- ⚡ **Google Gemini Embeddings & Generation:** Utilizes Gemini `text-embedding-004` (768-dim) and `gemini-1.5-flash` for high-fidelity grounded synthesis.
- 🔍 **Hybrid Retrieval Engine:** Combines dense vector cosine similarity (via Supabase pgvector / HNSW index) with exact keyword boosting for standard numbers (e.g. `IS 302`, `IS 1293`) and legislative acts.
- 🌐 **Full Multilingual Comprehension:** Fluent in English, Devanagari Hindi, and Romanized Hinglish.
- 🎨 **Modern Glassmorphic React UI:** Built with Vite, interactive source cards, text-to-speech audio reader, copy-to-clipboard, category filters, and live knowledge base explorer.

---

## 🏗 Architecture & RAG Pipeline

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Ingestion Pipeline                              │
│                                                                        │
│  [Authorized BIS PDFs] ──> [Text & Section Extraction] ──> [Page Chunks]│
│                                                                 │      │
│                                                                 ▼      │
│  [Supabase pgvector] <── [Vector Embeddings] <── [Gemini Embedding API]│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                         Query & RAG Pipeline                           │
│                                                                        │
│  [User Question (EN/HI/Hinglish)] ──> [Entity & Keyword Extraction]   │
│                                                │                       │
│                                                ▼                       │
│                                       [Query Embedding]                │
│                                                │                       │
│                                                ▼                       │
│                           [Hybrid Retrieval: Vector + Keyword]        │
│                                                │                       │
│                                                ▼                       │
│                          [Similarity & Grounding Guardrail]            │
│                          /                                \           │
│              [Below Threshold]                       [Sufficient Context]
│                     │                                         │        │
│                     ▼                                         ▼        │
│        "Could not verify..."                       [Context Builder]   │
│                                                               │        │
│                                                               ▼        │
│                                                     [Gemini Grounded]  │
│                                                               │        │
│                                                               ▼        │
│                                               [Answer + Citations + UI]│
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```text
c:/website/Rag BIS/
├── backend/
│   ├── app/
│   │   ├── __init__.py           # Backend package init
│   │   ├── main.py               # FastAPI server & REST API endpoints
│   │   ├── config.py             # Pydantic BaseSettings & env config
│   │   ├── database.py           # Supabase pgvector & Local Vector Store
│   │   ├── embeddings.py         # Google Gemini embedding client
│   │   ├── llm.py                # Gemini generative model integration
│   │   ├── chunking.py           # Page-aware PDF parsing & section detector
│   │   ├── ingestion.py          # Ingestion pipeline & metadata registry
│   │   ├── retrieval.py          # Hybrid search, reranking & citations
│   │   ├── rag.py                # Grounded RAG orchestrator
│   │   ├── prompts.py            # Strict grounding prompt templates
│   │   └── schemas.py            # Pydantic request/response schemas
│   ├── tests/
│   │   ├── test_ingestion.py     # PDF chunking and cleaner tests
│   │   ├── test_retrieval.py     # Entity extraction & ranking tests
│   │   └── test_api.py           # FastAPI endpoint tests
│   ├── ingest_documents.py       # Standalone ingestion CLI
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example              # Backend env template
│   └── Dockerfile                # Backend container definition
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx        # Top banner, status pill & nav
│   │   │   ├── Chat.jsx          # Conversation view, chips & input
│   │   │   ├── Message.jsx       # Markdown bubble, TTS & citations
│   │   │   ├── SourceCard.jsx    # Expandable cited source cards
│   │   │   └── Loading.jsx       # Shimmer loading indicator
│   │   ├── pages/
│   │   │   └── Home.jsx          # Root page & Knowledge repository modal
│   │   ├── services/
│   │   │   └── api.js            # API communication client
│   │   ├── App.jsx               # React app root
│   │   ├── main.jsx              # DOM root mount
│   │   └── index.css             # Glassmorphism design system
│   ├── package.json              # Node dependencies
│   ├── vite.config.js            # Vite bundler & reverse proxy config
│   ├── index.html                # HTML entrypoint
│   └── Dockerfile                # Multi-stage production container
│
├── documents/
│   ├── raw/                      # Authorized BIS PDF collection
│   │   ├── acts/                 # BIS Act 2016 Handbooks
│   │   ├── rules/                # BIS Rules & Regulations
│   │   ├── certification/        # Conformity Assessment & Scheme-I
│   │   ├── hallmarking/          # Gold & Silver Hallmarking Guidelines
│   │   ├── laboratories/         # Testing & Laboratory Manuals
│   │   ├── booklets/             # BIS Care App & Consumer Booklets
│   │   └── standards/            # Indian Standards (IS 302, etc.)
│   └── processed/
│       ├── metadata.json         # Indexed documents registry
│       └── vector_store.json     # Persisted vector cache
│
├── database/
│   ├── schema.sql                # Supabase pgvector tables & HNSW index
│   └── functions.sql             # Vector match & hybrid search RPCs
│
├── scripts/
│   ├── ingest_all.py             # Batch ingest script
│   ├── test_rag.py               # 12-query automated RAG benchmark
│   └── generate_sample_bis_pdfs.py # Reference PDF builder
│
├── .env.example                  # Root environment template
├── .gitignore                    # Secrets and build ignore rules
├── docker-compose.yml            # Multi-service container compose
└── README.md                     # Comprehensive documentation
```

---

## ⚙ Prerequisites & System Setup

### 1. Requirements
- **Operating System:** Windows 10/11, macOS, or Linux
- **Python:** 3.10, 3.11, 3.12, or 3.13
- **Node.js:** 18.x or 20.x LTS

### 2. Windows PowerShell Setup

Open **PowerShell** in the project root directory (`c:\website\Rag BIS`):

```powershell
# 1. Create Python Virtual Environment
python -m venv .venv

# 2. Activate Virtual Environment
.\.venv\Scripts\Activate.ps1

# 3. Install Backend Dependencies
pip install -r backend\requirements.txt

# 4. Install Frontend Dependencies
cd frontend
npm install
cd ..
```

---

## 🗄 Supabase & pgvector Database Setup

1. Log in to [Supabase](https://supabase.com/) and create a new project.
2. Open the **SQL Editor** from the left navigation panel.
3. Open [`database/schema.sql`](file:///c:/website/Rag%20BIS/database/schema.sql), copy its contents, and run it in the Supabase SQL Editor. This enables the `vector` extension and creates the `bis_documents` table with HNSW indexing.
4. Open [`database/functions.sql`](file:///c:/website/Rag%20BIS/database/functions.sql), copy its contents, and run it. This installs the `match_documents` and `hybrid_match_documents` stored procedures.
5. In **Project Settings** > **API**, copy your **Project URL** and **Anon Key** (or Service Role Key).

---

## 🔑 Environment Configuration (.env)

Create a `.env` file in the root directory by copying `.env.example`:

```powershell
Copy-Item .env.example .env
```

Edit `.env` with your API keys:

```ini
# Google Gemini API Settings
# Obtain a free API key at: https://aistudio.google.com/
GEMINI_API_KEY=AIzaSyYourGeminiApiKeyHere
GEMINI_MODEL=gemini-1.5-flash
GEMINI_EMBEDDING_MODEL=models/text-embedding-004
EMBEDDING_DIMENSION=768

# Supabase PostgreSQL & pgvector Settings
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_TABLE=bis_documents

# RAG & Retrieval Tuning
RAG_TOP_K=6
SIMILARITY_THRESHOLD=0.30
ENABLE_HYBRID_SEARCH=true

# Server Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:5173
```

> **Note:** If `SUPABASE_URL` is omitted, the application automatically activates its high-performance **Local Vector Store**, allowing offline testing, evaluation, and local development.

---

## 📥 Document Collection & Ingestion Pipeline

### Adding Authorized BIS Documents
Place legally accessible, public BIS PDF documents into the respective subdirectories under `documents/raw/`:
- `documents/raw/acts/` — BIS Act 2016 enactments
- `documents/raw/certification/` — Conformity assessment, ISI scheme guidelines
- `documents/raw/hallmarking/` — Gold/Silver hallmarking & HUID rules
- `documents/raw/laboratories/` — Testing & laboratory recognition manuals
- `documents/raw/standards/` — Indian Standards (e.g. `IS_302.pdf`)
- `documents/raw/booklets/` — Consumer awareness guides

### Running the Ingestion Command

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Ingest all documents
python backend\ingest_documents.py

# Or force re-indexing of all documents
python backend\ingest_documents.py --force
```

---

## 🚀 Running the Application Locally

### Step 1: Start the Backend Server (FastAPI)

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Base URL: `http://localhost:8000`
- Interactive Swagger UI: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### Step 2: Start the Frontend Dev Server (React + Vite)

Open a second terminal window:

```powershell
cd frontend
npm run dev
```
- Frontend Web UI: `http://localhost:5173`

---

## 🧪 Automated Testing & Verification

### Run PyTest Unit & Integration Tests

```powershell
.\.venv\Scripts\Activate.ps1
pytest backend\tests -v
```

### Run the 12-Query RAG Benchmark (Multilingual & Anti-Hallucination)

```powershell
python scripts\test_rag.py
```

This benchmark verifies:
1. Fundamental BIS queries
2. BIS Act 2016 legal provisions & penalties
3. ISI Certification & Scheme-I workflow
4. Gold Hallmarking, Carat fineness & HUID verification
5. Multi-lingual Hindi queries (`Hallmarking kya hai?`)
6. Hinglish technical queries (`IS 302 kis product ke liye hai?`)
7. Laboratory network capabilities
8. BIS Care mobile app verification features
9. **Negative Test:** Out-of-scope query (`What is the capital of France?`) ➔ **Pass: Refuses hallucination**.
10. **Negative Test:** Non-existent standard (`IS 9999999 for flying cars`) ➔ **Pass: Refuses hallucination**.

---

## 🌐 Multilingual Support

The system natively accepts queries in three linguistic formats:

| Language | Sample Query | System Behavior |
| :--- | :--- | :--- |
| **English** | *"What is the BIS certification process?"* | Returns precise English synthesis citing Scheme-I guidelines and pages. |
| **Hindi (हिंदी)** | *"हॉलमार्किंग क्या है और यह सोने के लिए क्यों जरूरी है?"* | Answers in natural, grammatically correct Hindi with citations. |
| **Hinglish** | *"IS 302 standard kis product safety ke liye use hota hai?"* | Explains appliance safety provisions in fluent Hinglish while preserving exact standard IDs. |

---

## 📖 API Documentation (Swagger UI)

Navigate to `http://localhost:8000/docs` to interact directly with the REST endpoints:

- **`GET /health`** — Returns system status, vector chunk counts, and database connection state.
- **`POST /api/ask`** — Submits a natural language question and receives grounded answer with source citations.
- **`POST /api/ingest`** — Triggers ingestion of raw documents.
- **`GET /api/documents`** — Lists all indexed BIS documents and their metadata.

---

## 🐳 Docker & Containerized Deployment

Run the complete full-stack assistant via Docker Compose:

```bash
docker-compose up --build -d
```
- Frontend UI: `http://localhost:5173`
- Backend API: `http://localhost:8000`

---

## ❓ Troubleshooting & FAQ

**Q: Why does the assistant respond *"I could not verify this information from the available BIS documents."*?**  
A: This is an intentional safeguard. If the question asks for information not present in the indexed documents in `documents/raw/` (or similarity is below threshold), the system refuses to invent facts.

**Q: Can I add my own BIS standard PDFs?**  
A: Yes. Simply place any authorized PDF inside `documents/raw/<category>/` and execute `python backend/ingest_documents.py`. The system will automatically chunk, embed, and index it.

---

## ⚖ License & Legal Notice
This project is built for **SIH Problem Statement 26107**. Only legally accessible, authorized public BIS reference documents are utilized. All registered trademarks and standard designations remain the property of the Bureau of Indian Standards (BIS), Government of India.
