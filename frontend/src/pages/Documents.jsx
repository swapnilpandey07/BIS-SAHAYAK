import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BookOpen, Search, Filter, FileText, ExternalLink,
  RefreshCw, ChevronRight, AlertCircle, Database,
} from 'lucide-react';
import { getDocuments } from '../services/api';

const CATEGORY_COLORS = {
  acts: { bg: '#eff6ff', clr: '#1d4ed8', border: '#bfdbfe' },
  rules: { bg: '#f0fdf4', clr: '#059669', border: '#a7f3d0' },
  regulations: { bg: '#fdf4ff', clr: '#7c3aed', border: '#ddd6fe' },
  certification: { bg: '#fff7ed', clr: '#d97706', border: '#fde68a' },
  hallmarking: { bg: '#fefce8', clr: '#b45309', border: '#fef08a' },
  laboratories: { bg: '#f0f9ff', clr: '#0891b2', border: '#bae6fd' },
  standards: { bg: '#fdf4ff', clr: '#7c3aed', border: '#ddd6fe' },
  qco: { bg: '#fff1f2', clr: '#e11d48', border: '#fecdd3' },
  consumer: { bg: '#f0fdf4', clr: '#059669', border: '#a7f3d0' },
  handbooks: { bg: '#eff6ff', clr: '#1d4ed8', border: '#bfdbfe' },
  awareness: { bg: '#fff7ed', clr: '#d97706', border: '#fde68a' },
  booklets: { bg: '#f5f3ff', clr: '#6d28d9', border: '#ede9fe' },
};

const ALL_CATS = [
  '', 'acts', 'rules', 'regulations', 'certification', 'hallmarking',
  'laboratories', 'standards', 'qco', 'consumer', 'handbooks', 'awareness', 'booklets',
];

function DocCard({ doc }) {
  const navigate = useNavigate();
  const style = CATEGORY_COLORS[doc.category] || CATEGORY_COLORS.acts;

  return (
    <div
      className="doc-card animate-fade-up"
      onClick={() => navigate(`/documents/${encodeURIComponent(doc.document_id)}`)}
      role="button"
      tabIndex={0}
      onKeyDown={e => e.key === 'Enter' && navigate(`/documents/${encodeURIComponent(doc.document_id)}`)}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 8 }}>
        <div style={{
          width: 40, height: 40, borderRadius: 10,
          background: style.bg, border: `1px solid ${style.border}`,
          display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
        }}>
          <FileText size={18} color={style.clr} />
        </div>
        <div style={{
          fontSize: '0.65rem', fontWeight: 700, textTransform: 'uppercase',
          letterSpacing: '0.06em', padding: '3px 8px', borderRadius: 'var(--radius-full)',
          background: style.bg, color: style.clr, border: `1px solid ${style.border}`,
          whiteSpace: 'nowrap', alignSelf: 'flex-start',
        }}>
          {doc.category || 'General'}
        </div>
      </div>

      <div className="doc-card-title">{doc.title || doc.document_name}</div>

      {doc.document_name !== (doc.title || doc.document_name) && (
        <div style={{ fontSize: '0.78rem', color: 'var(--clr-text-muted)', fontFamily: 'monospace' }}>
          {doc.document_name}
        </div>
      )}

      <div className="doc-card-meta">
        {doc.standard_number && (
          <span className="badge badge-warning" style={{ fontSize: '0.7rem' }}>
            {doc.standard_number.length > 30 ? doc.standard_number.slice(0, 30) + '…' : doc.standard_number}
          </span>
        )}
        {doc.chunks_count > 0 && (
          <span style={{ display: 'flex', alignItems: 'center', gap: 3 }}>
            <Database size={11} /> {doc.chunks_count} chunks
          </span>
        )}
        {doc.status && (
          <span className={`badge ${doc.status === 'indexed' ? 'badge-green' : 'badge-gray'}`}>
            {doc.status}
          </span>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 4 }}>
        {doc.source_url ? (
          <a
            href={doc.source_url} target="_blank" rel="noopener noreferrer"
            onClick={e => e.stopPropagation()}
            style={{ fontSize: '0.75rem', color: 'var(--clr-primary)', display: 'flex', alignItems: 'center', gap: 4 }}
          >
            BIS Portal <ExternalLink size={11} />
          </a>
        ) : <span />}
        <ChevronRight size={16} color="var(--clr-text-muted)" />
      </div>
    </div>
  );
}

const Database2 = ({ size, ...p }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" {...p}>
    <ellipse cx="12" cy="5" rx="9" ry="3" /><path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5" /><path d="M3 12c0 1.7 4 3 9 3s9-1.3 9-3" />
  </svg>
);

export default function Documents() {
  const [documents, setDocuments] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [total, setTotal] = useState(0);

  const load = useCallback(async () => {
    setLoading(true); setError('');
    try {
      const data = await getDocuments({ category });
      setDocuments(data.documents || []);
      setTotal(data.total || data.count || 0);
    } catch (e) {
      setError(e.message || 'Failed to load documents');
    } finally {
      setLoading(false);
    }
  }, [category]);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    if (!search.trim()) { setFiltered(documents); return; }
    const q = search.toLowerCase();
    setFiltered(documents.filter(d =>
      (d.title || '').toLowerCase().includes(q) ||
      (d.document_name || '').toLowerCase().includes(q) ||
      (d.standard_number || '').toLowerCase().includes(q) ||
      (d.category || '').toLowerCase().includes(q)
    ));
  }, [search, documents]);

  return (
    <div className="page-wrapper">
      {/* Header */}
      <div style={{ background: '#fff', borderBottom: '1px solid var(--clr-border)', padding: '32px 24px' }}>
        <div className="container">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 6 }}>
            <BookOpen size={24} color="var(--clr-primary)" />
            <h1 style={{ fontWeight: 800, fontSize: '1.6rem', color: 'var(--clr-text-primary)' }}>BIS Knowledge Repository</h1>
            <span className="badge badge-blue">{total} Documents</span>
          </div>
          <p style={{ color: 'var(--clr-text-secondary)', fontSize: '0.9rem', marginBottom: 20 }}>
            Browse all official BIS documents indexed in the RAG knowledge base.
          </p>

          {/* Filters */}
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center' }}>
            <div className="search-wrap" style={{ flex: '1 1 280px', maxWidth: 400 }}>
              <Search size={16} className="search-icon" />
              <input
                className="input"
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Search documents…"
              />
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <Filter size={14} color="var(--clr-text-muted)" />
              <select
                className="input"
                value={category}
                onChange={e => setCategory(e.target.value)}
                style={{ width: 'auto' }}
              >
                {ALL_CATS.map(c => (
                  <option key={c} value={c}>{c ? c.charAt(0).toUpperCase() + c.slice(1) : 'All Categories'}</option>
                ))}
              </select>
            </div>
            <button className="btn btn-ghost btn-sm" onClick={load} style={{ gap: 6 }}>
              <RefreshCw size={13} /> Refresh
            </button>
          </div>
        </div>
      </div>

      <div className="container" style={{ padding: '32px 24px' }}>
        {error && (
          <div className="alert alert-error" style={{ marginBottom: 20 }}>
            <AlertCircle size={16} />{error}
          </div>
        )}

        {loading ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 16 }}>
            {Array.from({ length: 9 }).map((_, i) => (
              <div key={i} style={{ height: 180, borderRadius: 'var(--radius-lg)' }} className="skeleton" />
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">
              <Database2 size={28} color="var(--clr-primary)" />
            </div>
            <p style={{ fontWeight: 600, marginBottom: 4 }}>No documents found</p>
            <p style={{ fontSize: '0.85rem' }}>
              {search ? 'Try a different search term.' : 'No documents indexed yet. Use the ingest API to add documents.'}
            </p>
          </div>
        ) : (
          <>
            <p style={{ fontSize: '0.82rem', color: 'var(--clr-text-muted)', marginBottom: 16 }}>
              Showing {filtered.length} of {total} documents
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 16 }}>
              {filtered.map(doc => <DocCard key={doc.document_id} doc={doc} />)}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
