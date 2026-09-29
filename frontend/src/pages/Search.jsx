import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search as SearchIcon, FileText, ExternalLink, Filter,
  Sparkles, ChevronRight, AlertCircle, Database, Tag,
  ArrowRight, ShieldCheck
} from 'lucide-react';
import { searchDocuments } from '../services/api';

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
];

const SUGGESTED_QUERIES = [
  'ISI Mark certification requirements',
  'IS 302 electrical safety',
  'Gold hallmarking purity standards',
  'Foreign Manufacturers Certification FMCS',
  'Penalties for misuse of standard mark',
  'BIS Care Mobile App consumer verification'
];

export default function Search() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  const handleSearch = async (e, customQuery) => {
    if (e) e.preventDefault();
    const q = (customQuery !== undefined ? customQuery : query).trim();
    if (!q) return;

    setLoading(true);
    setError('');
    try {
      const data = await searchDocuments({
        query: q,
        category: category || null,
        top_k: 10
      });
      setResults(data);
    } catch (err) {
      console.error('Search error:', err);
      setError(err.message || 'Failed to search documents. Please verify backend connection.');
    } finally {
      setLoading(false);
    }
  };

  const onSelectSuggested = (text) => {
    setQuery(text);
    handleSearch(null, text);
  };

  return (
    <div className="page-wrapper" style={{ padding: '40px 24px 80px', minHeight: 'calc(100vh - var(--nav-height))' }}>
      <div className="container" style={{ maxWidth: 1000 }}>
        
        {/* Header Section */}
        <div style={{ textAlign: 'center', marginBottom: 36 }} className="animate-fade-up">
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: 8,
            padding: '6px 16px', borderRadius: 'var(--radius-full)',
            background: 'var(--clr-primary-light)', color: 'var(--clr-primary)',
            fontSize: '0.8rem', fontWeight: 700, marginBottom: 16
          }}>
            <Database size={14} />
            SEMANTIC KNOWLEDGE BASE SEARCH
          </div>
          <h1 style={{ fontSize: '2.4rem', fontWeight: 800, color: 'var(--clr-primary-dark)', marginBottom: 12 }}>
            Search BIS Documentation
          </h1>
          <p style={{ fontSize: '1.05rem', color: 'var(--clr-text-secondary)', maxWidth: 650, margin: '0 auto' }}>
            Retrieve exact clauses, sections, and standard specifications indexed directly from authorized Bureau of Indian Standards PDFs.
          </p>
        </div>

        {/* Search Bar & Filters Card */}
        <div className="card shadow-md animate-fade-up" style={{ padding: '24px', marginBottom: 32 }}>
          <form onSubmit={(e) => handleSearch(e)} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
              <div style={{
                flex: 1, minWidth: 280, display: 'flex', alignItems: 'center', gap: 12,
                background: 'var(--clr-bg)', border: '1.5px solid var(--clr-border)',
                borderRadius: 'var(--radius-md)', padding: '4px 16px',
                transition: 'border-color var(--transition)'
              }}>
                <SearchIcon size={20} color="var(--clr-primary)" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search by keywords, clauses, standard numbers (e.g. IS 302, Hallmarking, BIS Act)..."
                  style={{
                    width: '100%', border: 'none', background: 'transparent',
                    padding: '12px 0', fontSize: '1rem', outline: 'none',
                    color: 'var(--clr-text-primary)', fontFamily: 'inherit'
                  }}
                />
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  style={{
                    padding: '12px 16px', borderRadius: 'var(--radius-md)',
                    border: '1.5px solid var(--clr-border)', background: 'var(--clr-bg)',
                    fontSize: '0.9rem', color: 'var(--clr-text-primary)',
                    fontFamily: 'inherit', outline: 'none', cursor: 'pointer'
                  }}
                >
                  {CATEGORIES.map(c => (
                    <option key={c.id} value={c.id}>{c.label}</option>
                  ))}
                </select>

                <button
                  type="submit"
                  disabled={loading || !query.trim()}
                  className="btn btn-primary"
                  style={{ padding: '12px 24px', whiteSpace: 'nowrap' }}
                >
                  {loading ? (
                    <>
                      <div className="animate-spin" style={{ width: 16, height: 16, border: '2px solid #fff', borderTopColor: 'transparent', borderRadius: '50%' }} />
                      Searching...
                    </>
                  ) : (
                    <>
                      <SearchIcon size={16} />
                      Search Knowledge Base
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Quick Suggestions */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', paddingTop: 8 }}>
              <span style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--clr-text-muted)' }}>
                Popular Searches:
              </span>
              {SUGGESTED_QUERIES.map((sq, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => onSelectSuggested(sq)}
                  className="badge badge-blue"
                  style={{
                    border: '1px solid #bfdbfe', background: '#eff6ff',
                    cursor: 'pointer', padding: '4px 10px', fontSize: '0.75rem',
                    transition: 'all 0.15s ease'
                  }}
                >
                  {sq}
                </button>
              ))}
            </div>
          </form>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="alert alert-error animate-fade-in" style={{ marginBottom: 24 }}>
            <AlertCircle size={18} />
            <div>
              <strong>Search Error:</strong> {error}
            </div>
          </div>
        )}

        {/* Loading Skeleton State */}
        {loading && (
          <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--clr-primary)', fontWeight: 600, fontSize: '0.9rem' }}>
              <Sparkles size={16} className="animate-spin" />
              Executing hybrid semantic retrieval over BIS vector database...
            </div>
            {[1, 2, 3].map((_, i) => (
              <div key={i} className="card" style={{ padding: 20 }}>
                <div className="skeleton" style={{ height: 20, width: '40%', marginBottom: 12, borderRadius: 4 }} />
                <div className="skeleton" style={{ height: 14, width: '90%', marginBottom: 8, borderRadius: 4 }} />
                <div className="skeleton" style={{ height: 14, width: '75%', borderRadius: 4 }} />
              </div>
            ))}
          </div>
        )}

        {/* Search Results Display */}
        {results && !loading && (
          <div className="animate-fade-up">
            <div style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              marginBottom: 20, padding: '0 4px'
            }}>
              <div style={{ fontSize: '0.95rem', color: 'var(--clr-text-secondary)' }}>
                Found <strong style={{ color: 'var(--clr-primary-dark)' }}>{results.total_results || results.results?.length || 0}</strong> relevant results for "{results.query}"
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.75rem', color: 'var(--clr-text-muted)' }}>
                <ShieldCheck size={14} color="var(--clr-success)" />
                Directly retrieved from verified BIS indexed corpus
              </div>
            </div>

            {(!results.results || results.results.length === 0) ? (
              <div className="card" style={{ padding: '48px 24px', textAlign: 'center' }}>
                <Database size={40} color="var(--clr-text-muted)" style={{ margin: '0 auto 16px' }} />
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--clr-text-primary)', marginBottom: 8 }}>
                  No matching BIS documents found
                </h3>
                <p style={{ color: 'var(--clr-text-secondary)', fontSize: '0.9rem', maxWidth: 450, margin: '0 auto 20px' }}>
                  We could not find relevant passages matching your query in the current knowledge base. Try broader keywords or standard identifiers.
                </p>
                <button onClick={() => navigate('/assistant', { state: { question: query } })} className="btn btn-primary btn-sm" style={{ margin: '0 auto' }}>
                  Ask AI Assistant Instead
                </button>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                {results.results.map((item, idx) => {
                  const pct = item.similarity ? Math.round(item.similarity * 100) : null;
                  const docId = item.document_id || item.document_name;

                  return (
                    <div
                      key={idx}
                      className="card"
                      style={{
                        padding: '20px 24px',
                        borderLeft: '4px solid var(--clr-primary)',
                        transition: 'transform var(--transition), box-shadow var(--transition)',
                      }}
                    >
                      {/* Top metadata row */}
                      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8, marginBottom: 10 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flex: 1, minWidth: 260 }}>
                          <FileText size={18} color="var(--clr-primary)" style={{ flexShrink: 0 }} />
                          <div>
                            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--clr-primary-dark)', margin: 0 }}>
                              {item.title || item.document_name}
                            </h3>
                            {item.title && item.document_name !== item.title && (
                              <div style={{ fontSize: '0.75rem', color: 'var(--clr-text-muted)', fontFamily: 'monospace' }}>
                                {item.document_name}
                              </div>
                            )}
                          </div>
                        </div>

                        <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
                          {pct !== null && (
                            <span className="badge badge-green" style={{ fontWeight: 700 }}>
                              {pct}% Match
                            </span>
                          )}
                          {item.page_number && (
                            <span className="badge badge-blue">
                              Page {item.page_number}
                            </span>
                          )}
                          {item.category && (
                            <span className="badge badge-gray">
                              {item.category}
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Snippet / Content */}
                      <div style={{
                        background: 'var(--clr-bg)', borderRadius: 'var(--radius-sm)',
                        padding: '12px 16px', fontSize: '0.88rem', color: 'var(--clr-text-secondary)',
                        lineHeight: 1.6, marginBottom: 12, border: '1px solid var(--clr-border)'
                      }}>
                        {item.content || item.snippet}
                      </div>

                      {/* Footer tags and link */}
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 10, fontSize: '0.8rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                          {item.standard_number && (
                            <span className="badge badge-warning">
                              <Tag size={10} /> {item.standard_number}
                            </span>
                          )}
                          {item.section && (
                            <span style={{ color: 'var(--clr-text-muted)', display: 'flex', alignItems: 'center', gap: 4 }}>
                              Section: <strong>{item.section}</strong>
                            </span>
                          )}
                        </div>

                        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                          {item.source_url && (
                            <a
                              href={item.source_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              style={{ color: 'var(--clr-primary)', display: 'flex', alignItems: 'center', gap: 4, textDecoration: 'none', fontWeight: 600 }}
                            >
                              BIS Portal <ExternalLink size={12} />
                            </a>
                          )}
                          {docId && (
                            <button
                              onClick={() => navigate(`/documents/${encodeURIComponent(docId)}`)}
                              className="btn btn-ghost btn-sm"
                              style={{ padding: '4px 8px', fontSize: '0.8rem' }}
                            >
                              View Full Document <ArrowRight size={13} />
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}
