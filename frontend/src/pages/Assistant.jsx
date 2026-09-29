import React, { useState, useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import {
  Send, RefreshCw, Filter, ShieldCheck, User, Copy, Check,
  Volume2, VolumeX, BookOpen, AlertCircle, Sparkles, Search,
  ChevronDown, ChevronUp, FileText, ExternalLink, Tag,
  Globe, MessageSquare,
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { askQuestion } from '../services/api';

/* ─────────────────────────────────────────────── */
const SUGGESTED = [
  { text: 'What is BIS certification?', lang: 'EN' },
  { text: 'What is an ISI mark?', lang: 'EN' },
  { text: 'What is hallmarking?', lang: 'EN' },
  { text: 'What is a Quality Control Order?', lang: 'EN' },
  { text: 'BIS certification kya hota hai?', lang: 'HI' },
  { text: 'ISI mark kaise milta hai?', lang: 'HINGLISH' },
  { text: 'What are the penalties for misuse of Standard Mark?', lang: 'EN' },
  { text: 'How can consumers use the BIS Care App?', lang: 'EN' },
];

const CATEGORIES = [
  { id: '', label: 'All Categories' },
  { id: 'acts', label: 'BIS Acts' },
  { id: 'rules', label: 'Rules' },
  { id: 'regulations', label: 'Regulations' },
  { id: 'certification', label: 'Certification' },
  { id: 'hallmarking', label: 'Hallmarking' },
  { id: 'laboratories', label: 'Laboratories' },
  { id: 'standards', label: 'IS Standards' },
  { id: 'qco', label: 'Quality Control Orders' },
  { id: 'consumer', label: 'Consumer Info' },
  { id: 'handbooks', label: 'Handbooks' },
  { id: 'awareness', label: 'Awareness' },
];

/* ─────────────────────────────────────────────── */
function SourceCard({ source, index }) {
  const [open, setOpen] = useState(false);
  const pct = source.similarity ? Math.round(source.similarity * 100) : null;
  return (
    <div className="source-card" style={{ marginTop: 8 }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1, minWidth: 200 }}>
          <FileText size={15} color="var(--clr-primary)" style={{ flexShrink: 0 }} />
          <span style={{ fontWeight: 700, fontSize: '0.87rem', color: 'var(--clr-text-primary)' }}>
            {source.document_name}
          </span>
          {source.page_number && (
            <span className="badge badge-blue">Page {source.page_number}</span>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
          {pct !== null && (
            <span className="badge badge-green">{pct}% match</span>
          )}
          {source.source_url && (
            <a href={source.source_url} target="_blank" rel="noopener noreferrer"
              className="badge badge-blue" style={{ cursor: 'pointer', textDecoration: 'none' }}>
              BIS Portal <ExternalLink size={10} />
            </a>
          )}
          {source.snippet && (
            <button onClick={() => setOpen(v => !v)} className="btn btn-icon" style={{ width: 28, height: 28 }}>
              {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>
          )}
        </div>
      </div>

      {(source.section || source.standard_number || source.category) && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 6 }}>
          {source.section && (
            <span style={{ fontSize: '0.75rem', color: 'var(--clr-text-secondary)', display: 'flex', alignItems: 'center', gap: 3 }}>
              <Tag size={11} /> {source.section}
            </span>
          )}
          {source.standard_number && (
            <span className="badge badge-warning">{source.standard_number}</span>
          )}
          {source.category && (
            <span className="badge badge-gray">{source.category}</span>
          )}
        </div>
      )}

      {open && source.snippet && (
        <div style={{
          marginTop: 10, padding: '8px 12px',
          background: 'var(--clr-bg)', borderRadius: 'var(--radius-sm)',
          borderLeft: '3px solid var(--clr-primary)',
          fontSize: '0.82rem', color: 'var(--clr-text-secondary)',
          fontStyle: 'italic', lineHeight: 1.55,
        }}>
          "{source.snippet}"
        </div>
      )}
    </div>
  );
}

/* ─────────────────────────────────────────────── */
function BotMessage({ msg }) {
  const [copied, setCopied] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [showContext, setShowContext] = useState(false);
  const isRefusal = msg.content?.toLowerCase().includes('could not verify');

  const copy = () => {
    navigator.clipboard.writeText(msg.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  const speak = () => {
    if (!('speechSynthesis' in window)) return;
    if (speaking) { window.speechSynthesis.cancel(); setSpeaking(false); return; }
    const u = new SpeechSynthesisUtterance(msg.content);
    u.onend = () => setSpeaking(false);
    u.onerror = () => setSpeaking(false);
    setSpeaking(true);
    window.speechSynthesis.speak(u);
  };

  return (
    <div className="animate-fade-up" style={{ display: 'flex', gap: 12, alignItems: 'flex-start', maxWidth: '92%' }}>
      <div style={{
        width: 36, height: 36, borderRadius: 10, flexShrink: 0,
        background: 'linear-gradient(135deg, #1e3a8a, #1d4ed8)',
        border: '1.5px solid rgba(29,78,216,0.3)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        boxShadow: '0 2px 12px rgba(29,78,216,0.2)',
      }}>
        <ShieldCheck size={18} color="#93c5fd" />
      </div>

      <div style={{ flex: 1 }}>
        {/* Header */}
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          flexWrap: 'wrap', gap: 8, marginBottom: 8,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontWeight: 700, fontSize: '0.85rem', color: 'var(--clr-primary)' }}>
              BIS Intelligent Assistant
            </span>
            {isRefusal ? (
              <span className="badge badge-error"><AlertCircle size={11} /> Not Found</span>
            ) : (
              <span className="badge badge-green"><ShieldCheck size={11} /> Grounded</span>
            )}
            {msg.model_used && (
              <span className="badge badge-gray" style={{ fontSize: '0.65rem' }}>
                {msg.model_used.replace('models/', '').replace('gemini-', 'Gemini ')}
              </span>
            )}
          </div>
          <div style={{ display: 'flex', gap: 4 }}>
            <button className="btn btn-ghost btn-sm" onClick={speak} title={speaking ? 'Stop' : 'Read aloud'}>
              {speaking ? <VolumeX size={13} /> : <Volume2 size={13} />}
              {speaking ? 'Stop' : 'Listen'}
            </button>
            <button className="btn btn-ghost btn-sm" onClick={copy}>
              {copied ? <Check size={13} color="var(--clr-success)" /> : <Copy size={13} />}
              {copied ? 'Copied' : 'Copy'}
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="chat-bubble-assistant md-content">
          <ReactMarkdown
            components={{
              p: ({ children }) => <p style={{ marginBottom: 10 }}>{children}</p>,
              ul: ({ children }) => <ul style={{ paddingLeft: 22, marginBottom: 10 }}>{children}</ul>,
              ol: ({ children }) => <ol style={{ paddingLeft: 22, marginBottom: 10 }}>{children}</ol>,
              li: ({ children }) => <li style={{ marginBottom: 4 }}>{children}</li>,
              strong: ({ children }) => <strong style={{ color: 'var(--clr-primary-dark)' }}>{children}</strong>,
            }}
          >
            {msg.content}
          </ReactMarkdown>

          {/* RAG transparency footer */}
          <div style={{
            marginTop: 12, paddingTop: 10, borderTop: '1px solid var(--clr-border)',
            fontSize: '0.72rem', color: 'var(--clr-text-muted)',
            display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap',
          }}>
            <Database size={11} />
            Answer generated using retrieved BIS documents.
            {msg.retrieved_chunks > 0 && (
              <span>· {msg.retrieved_chunks} chunks retrieved.</span>
            )}
          </div>
        </div>

        {/* Sources */}
        {msg.sources?.length > 0 && (
          <div style={{ marginTop: 10 }}>
            <button
              onClick={() => setShowContext(v => !v)}
              style={{
                background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'inherit',
                display: 'flex', alignItems: 'center', gap: 6,
                fontSize: '0.8rem', fontWeight: 700, color: 'var(--clr-text-secondary)',
                padding: '4px 0', marginBottom: 6,
              }}
            >
              <BookOpen size={14} color="var(--clr-primary)" />
              CITED SOURCES ({msg.sources.length})
              {showContext ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>
            {showContext && msg.sources.map((s, i) => <SourceCard key={i} source={s} index={i} />)}
          </div>
        )}

        {/* No-info disclaimer */}
        {isRefusal && (
          <div className="alert alert-info" style={{ marginTop: 10, fontSize: '0.82rem' }}>
            <AlertCircle size={14} />
            Information not found in the available BIS knowledge base. Please refine your question.
          </div>
        )}
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────── */
function LoadingMessage() {
  return (
    <div className="animate-fade-in" style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
      <div style={{
        width: 36, height: 36, borderRadius: 10, flexShrink: 0,
        background: 'linear-gradient(135deg, #1e3a8a, #1d4ed8)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        <Sparkles size={18} color="#93c5fd" style={{ animation: 'spin 1.5s linear infinite' }} />
      </div>
      <div className="chat-bubble-assistant" style={{ maxWidth: 320 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12, fontSize: '0.82rem', color: 'var(--clr-primary)', fontWeight: 600 }}>
          <Search size={13} className="animate-spin" />
          Searching BIS knowledge base…
        </div>
        {[92, 76, 55].map((w, i) => (
          <div key={i} className="skeleton" style={{ height: 12, borderRadius: 4, width: `${w}%`, marginBottom: 8 }} />
        ))}
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────── */
const Database = ({ size, ...p }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" {...p}>
    <ellipse cx="12" cy="5" rx="9" ry="3" /><path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5" /><path d="M3 12c0 1.7 4 3 9 3s9-1.3 9-3" />
  </svg>
);

/* ─────────────────────────────────────────────── */
export default function Assistant() {
  const location = useLocation();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [category, setCategory] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [lastFailedQuery, setLastFailedQuery] = useState('');
  const bottomRef = useRef(null);
  const textareaRef = useRef(null);

  // Auto-populate from landing page suggestion
  useEffect(() => {
    if (location.state?.question) {
      const q = location.state.question;
      setInput(q);
      window.history.replaceState({}, '');
      // Auto-send after a small delay
      setTimeout(() => sendMessage(q), 300);
    }
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const sendMessage = async (text) => {
    const q = (text || input).trim();
    if (!q || loading) return;
    setError('');
    setLastFailedQuery('');
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: q }]);
    setLoading(true);
    try {
      const res = await askQuestion({ question: q, category_filter: category || null });
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: res.answer,
        sources: res.sources || [],
        retrieved_chunks: res.retrieved_chunks || 0,
        model_used: res.model_used,
        is_grounded: res.is_grounded,
      }]);
    } catch (e) {
      setLastFailedQuery(q);
      setError(e.message || 'Unable to connect to BIS Assistant. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => {
    if (lastFailedQuery) {
      // Remove last user message before re-sending to avoid duplicate bubbles
      setMessages(prev => prev.slice(0, -1));
      sendMessage(lastFailedQuery);
    }
  };

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  };

  const reset = () => { setMessages([]); setError(''); setInput(''); };

  const isEmptyChat = messages.length === 0 && !loading;

  return (
    <div className="page-wrapper" style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Top bar */}
      <div style={{
        background: '#fff', borderBottom: '1px solid var(--clr-border)',
        padding: '10px 24px', display: 'flex', alignItems: 'center',
        justifyContent: 'space-between', flexWrap: 'wrap', gap: 10,
        position: 'sticky', top: 'var(--nav-height)', zIndex: 50,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <MessageSquare size={18} color="var(--clr-primary)" />
          <span style={{ fontWeight: 700, fontSize: '0.95rem' }}>AI Assistant</span>
          <span className="badge badge-blue">RAG-Powered</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
          <Filter size={14} color="var(--clr-text-muted)" />
          <select
            value={category}
            onChange={e => setCategory(e.target.value)}
            className="input"
            style={{ width: 'auto', padding: '5px 10px', fontSize: '0.82rem' }}
          >
            {CATEGORIES.map(c => <option key={c.id} value={c.id}>{c.label}</option>)}
          </select>
          <button className="btn btn-ghost btn-sm" onClick={reset} style={{ gap: 6 }}>
            <RefreshCw size={13} /> New Chat
          </button>
        </div>
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '24px' }}>
        <div style={{ maxWidth: 860, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 20 }}>

          {isEmptyChat && (
            <div className="animate-fade-up" style={{ textAlign: 'center', padding: '40px 0 20px' }}>
              <div style={{
                width: 64, height: 64, borderRadius: 18,
                background: 'linear-gradient(135deg, #1e3a8a, #1d4ed8)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                margin: '0 auto 20px', boxShadow: '0 8px 32px rgba(29,78,216,0.25)',
              }}>
                <ShieldCheck size={32} color="#93c5fd" />
              </div>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: 8, color: 'var(--clr-text-primary)' }}>
                How can I assist you with BIS Standards?
              </h2>
              <p style={{ color: 'var(--clr-text-secondary)', fontSize: '0.9rem', maxWidth: 500, margin: '0 auto 32px' }}>
                Ask in <strong>English</strong>, <strong>हिंदी</strong>, or <strong>Hinglish</strong>. All answers are grounded in official BIS documents.
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center' }}>
                {SUGGESTED.map(q => (
                  <button
                    key={q.text}
                    onClick={() => sendMessage(q.text)}
                    className="suggestion-chip"
                  >
                    <Globe size={12} />
                    <span style={{
                      fontSize: '0.65rem', fontWeight: 700,
                      background: 'var(--clr-primary-dim)', color: 'var(--clr-primary)',
                      padding: '1px 5px', borderRadius: 3,
                    }}>{q.lang}</span>
                    {q.text}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) =>
            msg.role === 'user' ? (
              <div key={i} className="animate-fade-up" style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, alignItems: 'flex-start' }}>
                <div>
                  <div className="chat-bubble-user">{msg.content}</div>
                </div>
                <div style={{
                  width: 36, height: 36, borderRadius: 10, flexShrink: 0,
                  background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <User size={18} color="#fff" />
                </div>
              </div>
            ) : (
              <BotMessage key={i} msg={msg} />
            )
          )}

          {loading && <LoadingMessage />}

          {error && (
            <div className="alert alert-error animate-fade-in" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 10 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1 }}>
                <AlertCircle size={16} style={{ flexShrink: 0 }} />
                <span>{error}</span>
              </div>
              {lastFailedQuery && (
                <button
                  className="btn btn-sm"
                  onClick={handleRetry}
                  style={{ background: '#fff', color: 'var(--clr-error)', border: '1px solid var(--clr-error)', borderRadius: 6, fontWeight: 600, padding: '4px 10px' }}
                >
                  <RefreshCw size={12} style={{ marginRight: 4 }} /> Retry
                </button>
              )}
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </div>

      {/* Input */}
      <div style={{
        background: '#fff', borderTop: '1px solid var(--clr-border)',
        padding: '16px 24px',
        position: 'sticky', bottom: 0,
      }}>
        <div style={{ maxWidth: 860, margin: '0 auto' }}>
          <div style={{
            display: 'flex', gap: 10, alignItems: 'flex-end',
            background: 'var(--clr-bg)', border: '1.5px solid var(--clr-border)',
            borderRadius: 'var(--radius-lg)', padding: '10px 14px',
            transition: 'border-color var(--transition)',
          }}
            onFocusCapture={e => e.currentTarget.style.borderColor = 'var(--clr-border-focus)'}
            onBlurCapture={e => e.currentTarget.style.borderColor = 'var(--clr-border)'}
          >
            <textarea
              ref={textareaRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKey}
              placeholder="Ask anything about BIS standards, certification, hallmarking… (English / हिंदी / Hinglish)"
              rows={1}
              style={{
                flex: 1, border: 'none', outline: 'none',
                background: 'transparent', resize: 'none',
                fontFamily: 'inherit', fontSize: '0.95rem',
                color: 'var(--clr-text-primary)', maxHeight: 140,
                lineHeight: 1.5,
              }}
            />
            <button
              className="btn btn-primary"
              onClick={() => sendMessage()}
              disabled={!input.trim() || loading}
              style={{ borderRadius: 10, padding: '9px 16px', flexShrink: 0 }}
            >
              {loading ? <div className="spinner" style={{ width: 16, height: 16 }} /> : <Send size={16} />}
              Ask BIS
            </button>
          </div>
          <p style={{ textAlign: 'center', fontSize: '0.72rem', color: 'var(--clr-text-muted)', marginTop: 6 }}>
            Press <kbd style={{ fontFamily: 'monospace', background: 'var(--clr-bg)', border: '1px solid var(--clr-border)', borderRadius: 3, padding: '0 4px' }}>Enter</kbd> to send · Shift+Enter for new line · RAG grounded · Refuses hallucination
          </p>
        </div>
      </div>
    </div>
  );
}
