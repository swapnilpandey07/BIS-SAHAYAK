import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileText, Database, Sparkles, Brain, ShieldCheck,
  Search, ArrowDown, ArrowRight, Layers, CheckCircle2,
  AlertTriangle, Lock, Globe, Cpu, BookOpen, MessageSquare
} from 'lucide-react';

const INGESTION_STEPS = [
  {
    step: '01',
    title: 'Document Processing',
    desc: 'Authorized Bureau of Indian Standards PDFs (Acts, Standards, QCOs, Manuals) are ingested with structural hierarchy preserved.',
    icon: FileText,
    badge: 'PyPDF / Parser'
  },
  {
    step: '02',
    title: 'Contextual Chunking',
    desc: 'Documents are partitioned into semantic passages, maintaining page numbers, clause IDs, section headings, and standard numbers.',
    icon: Layers,
    badge: 'Page-Aware Chunks'
  },
  {
    step: '03',
    title: 'Vector Embeddings',
    desc: 'Each text chunk is mapped into high-dimensional geometric space using Google text-embedding-004 (768-dimensional vectors).',
    icon: Sparkles,
    badge: 'text-embedding-004'
  },
  {
    step: '04',
    title: 'Vector Database Storage',
    desc: 'Embeddings and metadata are indexed in Supabase PostgreSQL pgvector using HNSW indexes for sub-millisecond retrieval.',
    icon: Database,
    badge: 'pgvector / HNSW'
  }
];

const QUERY_STEPS = [
  {
    step: '01',
    title: 'Natural Language Inquiry',
    desc: 'Citizens or manufacturers enter questions in English, Devanagari Hindi, or Hinglish.',
    icon: MessageSquare,
    badge: 'Multilingual Input'
  },
  {
    step: '02',
    title: 'Hybrid Semantic Retrieval',
    desc: 'Combines vector cosine similarity with exact keyword boosting for standard identifiers (e.g. IS 302, IS 1293) and acts.',
    icon: Search,
    badge: 'Hybrid Vector + BM25'
  },
  {
    step: '03',
    title: 'Anti-Hallucination Guardrail',
    desc: 'If retrieved chunk similarities fall below the strict confidence threshold, the assistant refuses to fabricate answers.',
    icon: ShieldCheck,
    badge: 'Grounding Filter'
  },
  {
    step: '04',
    title: 'Synthesized Grounded Answer',
    desc: 'Google Gemini 1.5 Flash generates a factual response strictly bounded by the retrieved context, complete with page citations.',
    icon: Brain,
    badge: 'Gemini 1.5 Flash'
  }
];

export default function HowItWorks() {
  const navigate = useNavigate();

  return (
    <div className="page-wrapper" style={{ padding: '40px 24px 80px', minHeight: 'calc(100vh - var(--nav-height))' }}>
      <div className="container" style={{ maxWidth: 1040 }}>

        {/* Hero Header */}
        <div style={{ textAlign: 'center', marginBottom: 48 }} className="animate-fade-up">
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: 8,
            padding: '6px 16px', borderRadius: 'var(--radius-full)',
            background: 'var(--clr-primary-light)', color: 'var(--clr-primary)',
            fontSize: '0.8rem', fontWeight: 700, marginBottom: 16
          }}>
            <Cpu size={14} />
            RAG ARCHITECTURE & SYSTEM DESIGN
          </div>
          <h1 style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--clr-primary-dark)', marginBottom: 14 }}>
            How Retrieval-Augmented Generation Works
          </h1>
          <p style={{ fontSize: '1.1rem', color: 'var(--clr-text-secondary)', maxWidth: 720, margin: '0 auto', lineHeight: 1.6 }}>
            The <strong>BIS Intelligent Assistant</strong> eliminates hallucinations by retrieving verified standard passages from official documents <em>before</em> generating an answer.
          </p>
        </div>

        {/* Core RAG Principle Callout */}
        <div className="card shadow-md animate-fade-up" style={{
          padding: '24px 32px', marginBottom: 48,
          background: 'linear-gradient(135deg, #1e3a8a, #1d4ed8)',
          color: '#fff', border: 'none'
        }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: 20 }}>
            <div style={{
              width: 48, height: 48, borderRadius: 12,
              background: 'rgba(255,255,255,0.15)',
              display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0
            }}>
              <ShieldCheck size={26} color="#93c5fd" />
            </div>
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#fff', marginBottom: 8 }}>
                The Golden Rule: Zero Fact Invention
              </h3>
              <p style={{ fontSize: '0.95rem', color: 'rgba(255,255,255,0.85)', lineHeight: 1.65, margin: 0 }}>
                Standard AI models often guess regulatory figures, penalty amounts, or test standards. Our system enforces an immutable constraint: answers are generated <strong>exclusively</strong> from official BIS documentation, accompanied by exact document names, page numbers, and clause references.
              </p>
            </div>
          </div>
        </div>

        {/* Phase 1: Ingestion Pipeline */}
        <div style={{ marginBottom: 48 }} className="animate-fade-up">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 32, height: 32, borderRadius: 8, background: '#eff6ff', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#1d4ed8', fontWeight: 800 }}>
              1
            </div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--clr-primary-dark)', margin: 0 }}>
              Document Ingestion & Indexing Pipeline
            </h2>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))',
            gap: 16
          }}>
            {INGESTION_STEPS.map((step, idx) => {
              const Icon = step.icon;
              return (
                <div key={idx} className="card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', position: 'relative' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                    <div style={{ width: 36, height: 36, borderRadius: 8, background: 'var(--clr-primary-light)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Icon size={18} color="var(--clr-primary)" />
                    </div>
                    <span className="badge badge-blue">{step.badge}</span>
                  </div>
                  <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--clr-primary-dark)', marginBottom: 8 }}>
                    {step.step}. {step.title}
                  </h4>
                  <p style={{ fontSize: '0.85rem', color: 'var(--clr-text-secondary)', lineHeight: 1.55, flex: 1, margin: 0 }}>
                    {step.desc}
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Visual Connector */}
        <div style={{ display: 'flex', justifyContent: 'center', margin: '24px 0' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '6px 16px', background: 'var(--clr-bg)', borderRadius: 'var(--radius-full)', border: '1px solid var(--clr-border)', color: 'var(--clr-text-muted)', fontSize: '0.8rem', fontWeight: 600 }}>
            <ArrowDown size={14} color="var(--clr-primary)" />
            Real-time User Query Execution Flow
          </div>
        </div>

        {/* Phase 2: Query & RAG Retrieval Pipeline */}
        <div style={{ marginBottom: 48 }} className="animate-fade-up">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 32, height: 32, borderRadius: 8, background: '#f0fdf4', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#059669', fontWeight: 800 }}>
              2
            </div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--clr-primary-dark)', margin: 0 }}>
              Query Processing & Grounded Synthesis
            </h2>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))',
            gap: 16
          }}>
            {QUERY_STEPS.map((step, idx) => {
              const Icon = step.icon;
              return (
                <div key={idx} className="card" style={{ padding: '20px', display: 'flex', flexDirection: 'column' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                    <div style={{ width: 36, height: 36, borderRadius: 8, background: '#f0fdf4', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Icon size={18} color="#059669" />
                    </div>
                    <span className="badge badge-green">{step.badge}</span>
                  </div>
                  <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--clr-primary-dark)', marginBottom: 8 }}>
                    {step.step}. {step.title}
                  </h4>
                  <p style={{ fontSize: '0.85rem', color: 'var(--clr-text-secondary)', lineHeight: 1.55, flex: 1, margin: 0 }}>
                    {step.desc}
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Comparison Table: Standard LLM vs BIS RAG Assistant */}
        <div className="card animate-fade-up" style={{ padding: '28px', marginBottom: 48 }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--clr-primary-dark)', marginBottom: 20, textAlign: 'center' }}>
            Why RAG is Essential for Regulatory & Standards Queries
          </h3>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--clr-border)', textAlign: 'left' }}>
                  <th style={{ padding: '12px 14px', width: '30%', color: 'var(--clr-text-muted)' }}>FEATURE</th>
                  <th style={{ padding: '12px 14px', width: '35%', color: 'var(--clr-error)' }}>GENERIC CHATBOT (UNGROUNDED)</th>
                  <th style={{ padding: '12px 14px', width: '35%', color: 'var(--clr-success)' }}>BIS INTELLIGENT ASSISTANT (RAG)</th>
                </tr>
              </thead>
              <tbody>
                <tr style={{ borderBottom: '1px solid var(--clr-border)' }}>
                  <td style={{ padding: '12px 14px', fontWeight: 600, color: 'var(--clr-text-primary)' }}>Factual Accuracy</td>
                  <td style={{ padding: '12px 14px', color: 'var(--clr-text-secondary)' }}>May fabricate standard numbers or clauses</td>
                  <td style={{ padding: '12px 14px', fontWeight: 600, color: 'var(--clr-success)' }}>Strictly constrained to official BIS text</td>
                </tr>
                <tr style={{ borderBottom: '1px solid var(--clr-border)' }}>
                  <td style={{ padding: '12px 14px', fontWeight: 600, color: 'var(--clr-text-primary)' }}>Source Citations</td>
                  <td style={{ padding: '12px 14px', color: 'var(--clr-text-secondary)' }}>None or vague references</td>
                  <td style={{ padding: '12px 14px', fontWeight: 600, color: 'var(--clr-success)' }}>Exact document, page number, and section</td>
                </tr>
                <tr style={{ borderBottom: '1px solid var(--clr-border)' }}>
                  <td style={{ padding: '12px 14px', fontWeight: 600, color: 'var(--clr-text-primary)' }}>Out-of-Domain Safety</td>
                  <td style={{ padding: '12px 14px', color: 'var(--clr-text-secondary)' }}>Answers anything with high confidence</td>
                  <td style={{ padding: '12px 14px', fontWeight: 600, color: 'var(--clr-success)' }}>Explicitly refuses when context is absent</td>
                </tr>
                <tr>
                  <td style={{ padding: '12px 14px', fontWeight: 600, color: 'var(--clr-text-primary)' }}>Multilingual Understanding</td>
                  <td style={{ padding: '12px 14px', color: 'var(--clr-text-secondary)' }}>Inconsistent transliteration handling</td>
                  <td style={{ padding: '12px 14px', fontWeight: 600, color: 'var(--clr-success)' }}>Native English, Hindi, and Hinglish support</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* CTA Bar */}
        <div style={{
          textAlign: 'center', padding: '32px', background: 'var(--clr-bg)',
          borderRadius: 'var(--radius-lg)', border: '1.5px solid var(--clr-border)'
        }} className="animate-fade-up">
          <h3 style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--clr-primary-dark)', marginBottom: 8 }}>
            Experience Grounded BIS Intelligence
          </h3>
          <p style={{ color: 'var(--clr-text-secondary)', fontSize: '0.95rem', marginBottom: 20 }}>
            Try asking questions across certification schemes, laboratory testing, and Indian standards.
          </p>
          <div style={{ display: 'flex', justifyContent: 'center', gap: 12, flexWrap: 'wrap' }}>
            <button onClick={() => navigate('/assistant')} className="btn btn-primary">
              <MessageSquare size={16} />
              Open AI Assistant
            </button>
            <button onClick={() => navigate('/documents')} className="btn btn-secondary">
              <BookOpen size={16} />
              Browse Knowledge Base
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
