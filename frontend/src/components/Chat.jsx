import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Filter, RefreshCw, HelpCircle, Globe } from 'lucide-react';
import Message from './Message';
import Loading from './Loading';

const SUGGESTED_QUERIES = [
  { text: "What is BIS and what are its key functions?", lang: "EN" },
  { text: "What is the purpose of the BIS Act 2016?", lang: "EN" },
  { text: "What is the BIS product certification process?", lang: "EN" },
  { text: "Hallmarking kya hai aur HUID verify kaise karein?", lang: "HI" },
  { text: "BIS certification ke liye kya requirements hain?", lang: "HINGLISH" },
  { text: "IS 302 standard kis electrical appliance ke liye hai?", lang: "HINGLISH" },
  { text: "What are the penalties for misuse of Standard Mark?", lang: "EN" },
  { text: "How can consumers use the BIS Care App?", lang: "EN" },
];

const CATEGORIES = [
  { id: '', label: 'All BIS Categories' },
  { id: 'acts', label: 'BIS Act & Legislation' },
  { id: 'certification', label: 'Product Certification (ISI)' },
  { id: 'hallmarking', label: 'Gold & Silver Hallmarking' },
  { id: 'laboratories', label: 'Testing Laboratories' },
  { id: 'standards', label: 'Indian Standards (IS)' },
  { id: 'booklets', label: 'Consumer Booklets' },
];

export default function Chat({ messages, onSendMessage, loading, onResetChat }) {
  const [inputText, setInputText] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (!inputText.trim() || loading) return;

    onSendMessage({
      question: inputText.trim(),
      category_filter: selectedCategory || null,
    });
    setInputText('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleChipClick = (queryText) => {
    if (loading) return;
    onSendMessage({
      question: queryText,
      category_filter: selectedCategory || null,
    });
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: 'calc(100vh - 140px)',
      maxWidth: '1200px',
      margin: '0 auto',
      width: '100%',
      padding: '0 20px',
    }}>
      {/* Control Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '12px',
        flexWrap: 'wrap',
        gap: '10px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Filter size={15} color="var(--accent-gold)" />
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            style={{
              background: 'var(--bg-surface)',
              color: 'var(--text-primary)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
              padding: '6px 12px',
              fontSize: '0.82rem',
              outline: 'none',
              cursor: 'pointer',
            }}
          >
            {CATEGORIES.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.label}
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={onResetChat}
          className="btn-secondary"
          style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem' }}
          title="Start fresh conversation"
        >
          <RefreshCw size={13} />
          <span>New Chat</span>
        </button>
      </div>

      {/* Messages Container */}
      <div className="glass-panel" style={{
        flex: 1,
        overflowY: 'auto',
        padding: '24px',
        display: 'flex',
        flexDirection: 'column',
        marginBottom: '16px',
      }}>
        {messages.length === 0 ? (
          <div style={{
            margin: 'auto',
            textAlign: 'center',
            maxWidth: '680px',
            padding: '20px 0',
          }}>
            <div style={{
              width: '64px',
              height: '64px',
              borderRadius: '18px',
              background: 'linear-gradient(135deg, #0f2b5c 0%, #1e3a8a 100%)',
              border: '2px solid var(--accent-gold)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 20px auto',
              boxShadow: 'var(--shadow-glow)',
            }}>
              <Sparkles size={32} color="#f59e0b" />
            </div>

            <h2 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: '8px', color: '#ffffff' }}>
              How can I assist you with BIS Standards today?
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', marginBottom: '28px' }}>
              Ask any question in <b>English</b>, <b>हिंदी (Hindi)</b>, or <b>Hinglish</b>. Answers are strictly verified against authorized Bureau of Indian Standards documentation.
            </p>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
              gap: '10px',
              textAlign: 'left',
            }}>
              {SUGGESTED_QUERIES.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => handleChipClick(q.text)}
                  style={{
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-sm)',
                    padding: '12px 14px',
                    color: 'var(--text-primary)',
                    fontSize: '0.84rem',
                    cursor: 'pointer',
                    textAlign: 'left',
                    transition: 'all 0.2s ease',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: '8px',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = 'var(--accent-gold)';
                    e.currentTarget.style.transform = 'translateY(-2px)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = 'var(--border-subtle)';
                    e.currentTarget.style.transform = 'translateY(0)';
                  }}
                >
                  <span style={{ lineHeight: '1.4' }}>{q.text}</span>
                  <span style={{
                    fontSize: '0.68rem',
                    fontWeight: 700,
                    padding: '2px 6px',
                    borderRadius: '4px',
                    background: 'rgba(255, 255, 255, 0.08)',
                    color: 'var(--accent-gold)',
                    flexShrink: 0,
                  }}>
                    {q.lang}
                  </span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div>
            {messages.map((msg, index) => (
              <Message key={index} message={msg} />
            ))}
            {loading && <Loading />}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Box Area */}
      <form onSubmit={handleSubmit} style={{
        position: 'relative',
        marginBottom: '16px',
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          background: 'var(--bg-surface)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          padding: '8px 12px 8px 18px',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
          transition: 'border-color 0.2s ease',
        }}>
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything about BIS standards, certification, hallmarking, or acts (English / हिंदी / Hinglish)..."
            rows={1}
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              outline: 'none',
              color: '#ffffff',
              fontSize: '0.95rem',
              fontFamily: 'inherit',
              resize: 'none',
              maxHeight: '120px',
            }}
          />

          <button
            type="submit"
            disabled={!inputText.trim() || loading}
            className="btn-gold"
            style={{
              padding: '10px 18px',
              borderRadius: 'var(--radius-sm)',
              marginLeft: '10px',
            }}
          >
            <Send size={16} />
            <span>Ask BIS</span>
          </button>
        </div>
        <div style={{
          fontSize: '0.72rem',
          color: 'var(--text-muted)',
          textAlign: 'center',
          marginTop: '6px',
        }}>
          Grounded RAG Assistant • Refuses hallucination when evidence is absent • Press <b>Enter</b> to submit
        </div>
      </form>
    </div>
  );
}
