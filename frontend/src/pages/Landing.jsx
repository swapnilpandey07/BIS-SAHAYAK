import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShieldCheck, MessageSquare, BookOpen, Search,
  Zap, Database, Brain, ChevronRight, ArrowRight,
  CheckCircle, Globe, FileText, Award, Layers,
} from 'lucide-react';
import { getHealth } from '../services/api';

const SUGGESTED = [
  { text: 'What is BIS certification?', lang: 'EN' },
  { text: 'What is an ISI mark?', lang: 'EN' },
  { text: 'What is hallmarking?', lang: 'EN' },
  { text: 'What is a Quality Control Order?', lang: 'EN' },
  { text: 'BIS certification kya hota hai?', lang: 'HI' },
  { text: 'ISI mark kaise milta hai?', lang: 'HINGLISH' },
];

const FEATURES = [
  {
    icon: Brain,
    title: 'RAG-Powered Answers',
    desc: 'Retrieval-Augmented Generation retrieves relevant BIS documents before generating any answer — no hallucination.',
    color: '#1d4ed8',
  },
  {
    icon: FileText,
    title: '40+ BIS Documents',
    desc: 'Acts, Rules, Regulations, Standards, Certification Guides, QCOs, Hallmarking — all indexed and searchable.',
    color: '#059669',
  },
  {
    icon: Globe,
    title: 'Multilingual Support',
    desc: 'Ask questions in English, Hindi (हिंदी), or Hinglish. The AI understands and answers accordingly.',
    color: '#4f46e5',
  },
  {
    icon: CheckCircle,
    title: 'Verified Sources',
    desc: 'Every answer comes with exact page numbers, sections, and similarity scores from official BIS documents.',
    color: '#d97706',
  },
  {
    icon: Search,
    title: 'Semantic Search',
    desc: 'Deep vector search across all BIS knowledge using Google text-embedding-004 for high accuracy retrieval.',
    color: '#0891b2',
  },
  {
    icon: Award,
    title: 'Grounded Responses',
    desc: "If information isn't in the BIS knowledge base, the assistant refuses to fabricate — full transparency.",
    color: '#7c3aed',
  },
];

const HOW_STEPS = [
  { n: '01', title: 'You Ask', desc: 'Type your question in English, Hindi, or Hinglish.' },
  { n: '02', title: 'Vector Search', desc: 'The query is embedded and matched against 96+ BIS document chunks.' },
  { n: '03', title: 'Context Retrieved', desc: 'Most relevant passages are retrieved with similarity scores.' },
  { n: '04', title: 'LLM Answers', desc: 'Gemini generates a grounded answer using only retrieved context.' },
  { n: '05', title: 'Sources Shown', desc: 'Every answer includes document citations with page and section.' },
];

export default function Landing() {
  const navigate = useNavigate();
  const [health, setHealth] = useState(null);

  useEffect(() => {
    getHealth().then(setHealth);
  }, []);

  const goAsk = (question) => {
    navigate('/assistant', { state: { question } });
  };

  return (
    <div className="page-wrapper" style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>

      {/* ===== HERO ===== */}
      <section className="hero-bg" style={{ padding: '96px 24px 80px', position: 'relative', overflow: 'hidden' }}>
        {/* Background circles */}
        <div style={{
          position: 'absolute', top: -80, right: -80,
          width: 400, height: 400, borderRadius: '50%',
          background: 'rgba(255,255,255,0.05)',
          pointerEvents: 'none',
        }} />
        <div style={{
          position: 'absolute', bottom: -120, left: -60,
          width: 300, height: 300, borderRadius: '50%',
          background: 'rgba(255,255,255,0.04)',
          pointerEvents: 'none',
        }} />

        <div className="container" style={{ position: 'relative', zIndex: 1 }}>
          {/* Eyebrow */}
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 20 }}>
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              background: 'rgba(255,255,255,0.12)', backdropFilter: 'blur(8px)',
              border: '1px solid rgba(255,255,255,0.2)',
              borderRadius: 'var(--radius-full)', padding: '6px 16px',
            }}>
              <span style={{
                width: 8, height: 8, borderRadius: '50%',
                background: health?.status === 'healthy' ? '#34d399' : '#fbbf24',
                boxShadow: `0 0 0 3px ${health?.status === 'healthy' ? 'rgba(52,211,153,0.3)' : 'rgba(251,191,36,0.3)'}`,
              }} />
              <span style={{ color: 'rgba(255,255,255,0.9)', fontSize: '0.8rem', fontWeight: 600 }}>
                {health?.status === 'healthy'
                  ? `Live · ${health.total_documents} Documents · ${health.total_chunks} Chunks`
                  : 'RAG-Powered · Official BIS Documents'}
              </span>
            </div>
          </div>

          <div style={{ textAlign: 'center', maxWidth: 760, margin: '0 auto' }}>
            <h1 className="animate-fade-up" style={{
              fontSize: 'clamp(2rem, 5vw, 3.5rem)',
              fontWeight: 900,
              color: '#ffffff',
              lineHeight: 1.15,
              marginBottom: 20,
              letterSpacing: '-0.02em',
            }}>
              BIS Intelligent{' '}
              <span style={{
                background: 'linear-gradient(90deg, #fcd34d, #f59e0b)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}>
                Assistant
              </span>
            </h1>

            <p className="animate-fade-up" style={{
              fontSize: 'clamp(1rem, 2vw, 1.2rem)',
              color: 'rgba(255,255,255,0.8)',
              lineHeight: 1.7,
              marginBottom: 40,
              animationDelay: '0.1s',
            }}>
              AI-powered assistance for understanding and searching Bureau of Indian Standards information.
              <br />
              <span style={{ color: 'rgba(255,255,255,0.6)', fontSize: '0.9em' }}>
                Grounded answers · Verified sources · English / हिंदी / Hinglish
              </span>
            </p>

            {/* CTA buttons */}
            <div className="animate-fade-up" style={{
              display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap',
              animationDelay: '0.2s', marginBottom: 48,
            }}>
              <button
                className="btn"
                onClick={() => navigate('/assistant')}
                style={{
                  background: '#ffffff', color: 'var(--clr-primary-dark)',
                  padding: '14px 28px', fontSize: '1rem', fontWeight: 700,
                  borderRadius: 'var(--radius-lg)', gap: 8,
                  boxShadow: '0 4px 24px rgba(0,0,0,0.2)',
                }}
              >
                <MessageSquare size={18} /> Ask Assistant
              </button>
              <button
                className="btn"
                onClick={() => navigate('/documents')}
                style={{
                  background: 'rgba(255,255,255,0.12)', color: '#ffffff',
                  border: '1.5px solid rgba(255,255,255,0.3)',
                  padding: '14px 28px', fontSize: '1rem', fontWeight: 700,
                  borderRadius: 'var(--radius-lg)', gap: 8,
                  backdropFilter: 'blur(8px)',
                }}
              >
                <BookOpen size={18} /> Explore Documents
              </button>
            </div>

            {/* Suggested questions */}
            <div className="animate-fade-up" style={{ animationDelay: '0.3s' }}>
              <p style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.8rem', marginBottom: 12, fontWeight: 500 }}>
                TRY ASKING:
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center' }}>
                {SUGGESTED.map((q) => (
                  <button
                    key={q.text}
                    onClick={() => goAsk(q.text)}
                    style={{
                      background: 'rgba(255,255,255,0.1)',
                      border: '1px solid rgba(255,255,255,0.2)',
                      borderRadius: 'var(--radius-full)',
                      padding: '7px 14px',
                      color: 'rgba(255,255,255,0.85)',
                      fontSize: '0.82rem',
                      cursor: 'pointer',
                      transition: 'all var(--transition)',
                      fontFamily: 'inherit',
                      display: 'flex', alignItems: 'center', gap: 6,
                    }}
                    onMouseEnter={e => {
                      e.currentTarget.style.background = 'rgba(255,255,255,0.2)';
                      e.currentTarget.style.transform = 'translateY(-2px)';
                    }}
                    onMouseLeave={e => {
                      e.currentTarget.style.background = 'rgba(255,255,255,0.1)';
                      e.currentTarget.style.transform = 'translateY(0)';
                    }}
                  >
                    <span style={{
                      fontSize: '0.65rem', fontWeight: 700,
                      background: 'rgba(255,255,255,0.2)',
                      padding: '1px 5px', borderRadius: 3, color: '#fcd34d',
                    }}>{q.lang}</span>
                    {q.text}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== STATS BANNER ===== */}
      <section style={{
        background: '#fff',
        borderBottom: '1px solid var(--clr-border)',
        padding: '28px 24px',
      }}>
        <div className="container" style={{
          display: 'flex', flexWrap: 'wrap', gap: 32,
          justifyContent: 'center', alignItems: 'center',
        }}>
          {[
            { label: 'BIS Documents', value: health?.total_documents ?? '40+', icon: FileText },
            { label: 'Vector Chunks', value: health?.total_chunks ?? '96+', icon: Layers },
            { label: 'Document Categories', value: '12', icon: BookOpen },
            { label: 'Embedding Dimensions', value: '768', icon: Database },
            { label: 'Languages', value: '3', icon: Globe },
          ].map(({ label, value, icon: Icon }) => (
            <div key={label} style={{ textAlign: 'center', minWidth: 100 }}>
              <div style={{
                fontSize: '1.6rem', fontWeight: 900,
                color: 'var(--clr-primary)', display: 'flex',
                alignItems: 'center', justifyContent: 'center', gap: 6,
              }}>
                <Icon size={20} color="var(--clr-primary)" style={{ opacity: 0.7 }} />
                {value}
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--clr-text-muted)', fontWeight: 500, marginTop: 2 }}>
                {label}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ===== FEATURES ===== */}
      <section style={{ padding: '80px 24px', background: 'var(--clr-bg)' }}>
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: 48 }}>
            <p className="section-eyebrow">Why use BIS Assistant?</p>
            <h2 className="section-title">Built for Accuracy & Transparency</h2>
            <p className="section-subtitle" style={{ margin: '0 auto' }}>
              Every answer is grounded in official BIS documentation — certified, reliable, and source-verified.
            </p>
          </div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: 20,
          }}>
            {FEATURES.map(({ icon: Icon, title, desc, color }) => (
              <div key={title} className="feature-card">
                <div className="feature-icon" style={{ background: `${color}18` }}>
                  <Icon size={24} color={color} />
                </div>
                <h3 style={{ fontWeight: 700, fontSize: '1rem', marginBottom: 8, color: 'var(--clr-text-primary)' }}>
                  {title}
                </h3>
                <p style={{ fontSize: '0.87rem', color: 'var(--clr-text-secondary)', lineHeight: 1.6 }}>{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== HOW IT WORKS ===== */}
      <section style={{ padding: '80px 24px', background: '#fff' }}>
        <div className="container">
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 48, alignItems: 'center' }}>
            <div style={{ flex: '1 1 280px' }}>
              <p className="section-eyebrow">Under the hood</p>
              <h2 className="section-title">How RAG Works</h2>
              <p style={{ color: 'var(--clr-text-secondary)', lineHeight: 1.7, marginBottom: 24, fontSize: '0.95rem' }}>
                RAG (Retrieval-Augmented Generation) retrieves relevant information from the BIS knowledge base before generating an answer. No knowledge is invented.
              </p>
              <button className="btn btn-secondary" onClick={() => navigate('/how-it-works')}
                style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                Learn More <ArrowRight size={16} />
              </button>
            </div>

            <div style={{ flex: '1 1 340px', display: 'flex', flexDirection: 'column', gap: 4 }}>
              {HOW_STEPS.map(({ n, title, desc }, i) => (
                <React.Fragment key={n}>
                  <div style={{
                    display: 'flex', alignItems: 'flex-start', gap: 16,
                    padding: '14px 18px',
                    background: 'var(--clr-bg)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--clr-border)',
                    transition: 'all var(--transition)',
                  }}
                    onMouseEnter={e => {
                      e.currentTarget.style.borderColor = 'var(--clr-primary-light)';
                      e.currentTarget.style.background = 'var(--clr-primary-dim)';
                    }}
                    onMouseLeave={e => {
                      e.currentTarget.style.borderColor = 'var(--clr-border)';
                      e.currentTarget.style.background = 'var(--clr-bg)';
                    }}
                  >
                    <div style={{
                      width: 36, height: 36, borderRadius: 8,
                      background: 'var(--clr-primary)', color: '#fff',
                      fontWeight: 800, fontSize: '0.75rem', display: 'flex',
                      alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                    }}>{n}</div>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--clr-text-primary)', marginBottom: 2 }}>{title}</div>
                      <div style={{ fontSize: '0.82rem', color: 'var(--clr-text-secondary)' }}>{desc}</div>
                    </div>
                  </div>
                  {i < HOW_STEPS.length - 1 && (
                    <div style={{ width: 2, height: 16, background: 'var(--clr-border)', margin: '0 auto', borderRadius: 2 }} />
                  )}
                </React.Fragment>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ===== CTA BANNER ===== */}
      <section className="hero-bg" style={{ padding: '64px 24px' }}>
        <div className="container" style={{ textAlign: 'center' }}>
          <h2 style={{ fontSize: 'clamp(1.5rem, 3vw, 2.2rem)', fontWeight: 900, color: '#fff', marginBottom: 12 }}>
            Ready to explore BIS standards?
          </h2>
          <p style={{ color: 'rgba(255,255,255,0.75)', marginBottom: 28, fontSize: '1rem' }}>
            Ask any question and get grounded answers in seconds.
          </p>
          <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
            <button
              className="btn"
              onClick={() => navigate('/assistant')}
              style={{ background: '#fff', color: 'var(--clr-primary-dark)', padding: '13px 26px', fontWeight: 700, borderRadius: 12, gap: 8 }}>
              <MessageSquare size={17} /> Open AI Assistant <ArrowRight size={16} />
            </button>
            <button
              className="btn"
              onClick={() => navigate('/documents')}
              style={{ background: 'rgba(255,255,255,0.12)', color: '#fff', border: '1.5px solid rgba(255,255,255,0.3)', padding: '13px 26px', fontWeight: 700, borderRadius: 12, gap: 8 }}>
              <BookOpen size={17} /> Browse Documents
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
