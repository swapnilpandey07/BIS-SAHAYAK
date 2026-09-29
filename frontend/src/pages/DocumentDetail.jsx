import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  FileText, ArrowLeft, ExternalLink, BookOpen, Calendar,
  Tag, Hash, Layers, CheckCircle, AlertCircle, ChevronDown, ChevronUp,
} from 'lucide-react';
import { getDocumentById } from '../services/api';

function MetaRow({ label, value, color }) {
  if (!value) return null;
  return (
    <div style={{ display: 'flex', gap: 12, padding: '10px 0', borderBottom: '1px solid var(--clr-border)' }}>
      <span style={{ minWidth: 160, fontSize: '0.82rem', fontWeight: 600, color: 'var(--clr-text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
        {label}
      </span>
      <span style={{ fontSize: '0.88rem', color: color || 'var(--clr-text-primary)', fontWeight: 500, flex: 1 }}>
        {value}
      </span>
    </div>
  );
}

function ChunkViewer({ chunks }) {
  const [open, setOpen] = useState(false);
  const [expanded, setExpanded] = useState({});
  if (!chunks?.length) return null;
  return (
    <div style={{ background: '#fff', border: '1px solid var(--clr-border)', borderRadius: 'var(--radius-lg)', overflow: 'hidden' }}>
      <button
        onClick={() => setOpen(v => !v)}
        style={{
          width: '100%', padding: '14px 20px', display: 'flex', alignItems: 'center',
          justifyContent: 'space-between', background: 'none', border: 'none',
          cursor: 'pointer', fontFamily: 'inherit', gap: 8,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Layers size={18} color="var(--clr-primary)" />
          <span style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--clr-text-primary)' }}>
            Retrieved Context Viewer
          </span>
          <span className="badge badge-blue">{chunks.length} chunks</span>
          <span className="badge badge-indigo">RAG Demo</span>
        </div>
        {open ? <ChevronUp size={18} color="var(--clr-text-muted)" /> : <ChevronDown size={18} color="var(--clr-text-muted)" />}
      </button>

      {open && (
        <div style={{ borderTop: '1px solid var(--clr-border)', padding: '0 20px 16px', display: 'flex', flexDirection: 'column', gap: 12, marginTop: 12 }}>
          {chunks.slice(0, 10).map((chunk, i) => (
            <div key={i} style={{
              background: 'var(--clr-bg)', borderRadius: 'var(--radius-md)',
              border: '1px solid var(--clr-border)', overflow: 'hidden',
            }}>
              <button
                onClick={() => setExpanded(p => ({ ...p, [i]: !p[i] }))}
                style={{
                  width: '100%', padding: '10px 14px', display: 'flex',
                  alignItems: 'center', justifyContent: 'space-between',
                  background: 'none', border: 'none', cursor: 'pointer',
                  fontFamily: 'inherit', gap: 8,
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span className="badge badge-blue">Chunk {i + 1}</span>
                  {chunk.page_number && <span className="badge badge-gray">Page {chunk.page_number}</span>}
                  {chunk.section && (
                    <span style={{ fontSize: '0.78rem', color: 'var(--clr-text-secondary)' }}>{chunk.section}</span>
                  )}
                </div>
                {expanded[i] ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              </button>
              {expanded[i] && (
                <div style={{
                  padding: '10px 14px', borderTop: '1px solid var(--clr-border)',
                  fontSize: '0.83rem', color: 'var(--clr-text-secondary)',
                  lineHeight: 1.65, fontFamily: 'inherit',
                }}>
                  {chunk.content}
                </div>
              )}
            </div>
          ))}
          {chunks.length > 10 && (
            <p style={{ textAlign: 'center', fontSize: '0.8rem', color: 'var(--clr-text-muted)', padding: '8px 0' }}>
              … and {chunks.length - 10} more chunks
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export default function DocumentDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true); setError('');
    getDocumentById(id)
      .then(setData)
      .catch(e => setError(e.message || 'Document not found'))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return (
    <div className="page-wrapper" style={{ padding: 40 }}>
      <div className="container">
        {[1, 0.7, 0.5].map((w, i) => (
          <div key={i} className="skeleton" style={{ height: i === 0 ? 36 : 20, width: `${w * 100}%`, borderRadius: 8, marginBottom: 12 }} />
        ))}
        <div className="skeleton" style={{ height: 300, borderRadius: 16 }} />
      </div>
    </div>
  );

  if (error) return (
    <div className="page-wrapper" style={{ padding: 40 }}>
      <div className="container">
        <button className="btn btn-ghost" onClick={() => navigate('/documents')} style={{ gap: 6, marginBottom: 20 }}>
          <ArrowLeft size={16} /> Back to Documents
        </button>
        <div className="alert alert-error">
          <AlertCircle size={16} /> {error}
        </div>
      </div>
    </div>
  );

  const doc = data?.document || {};
  const chunks = data?.chunks || [];

  return (
    <div className="page-wrapper">
      <div style={{ background: '#fff', borderBottom: '1px solid var(--clr-border)', padding: '24px' }}>
        <div className="container">
          <button className="btn btn-ghost btn-sm" onClick={() => navigate('/documents')} style={{ gap: 6, marginBottom: 16 }}>
            <ArrowLeft size={14} /> Back to Documents
          </button>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: 16, flexWrap: 'wrap' }}>
            <div style={{
              width: 56, height: 56, borderRadius: 14,
              background: 'var(--clr-primary-dim)',
              border: '1px solid rgba(29,78,216,0.2)',
              display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
            }}>
              <FileText size={28} color="var(--clr-primary)" />
            </div>
            <div style={{ flex: 1 }}>
              <h1 style={{ fontWeight: 800, fontSize: '1.4rem', color: 'var(--clr-text-primary)', lineHeight: 1.3, marginBottom: 8 }}>
                {doc.title || doc.document_name}
              </h1>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
                {doc.category && <span className="badge badge-blue">{doc.category}</span>}
                {doc.document_type && <span className="badge badge-indigo">{doc.document_type}</span>}
                {doc.status === 'indexed' && <span className="badge badge-green"><CheckCircle size={10} /> Indexed</span>}
                {doc.standard_number && (
                  <span className="badge badge-warning"><Hash size={10} /> {doc.standard_number.slice(0, 40)}</span>
                )}
              </div>
            </div>
            {doc.source_url && (
              <a href={doc.source_url} target="_blank" rel="noopener noreferrer" className="btn btn-secondary btn-sm" style={{ gap: 6 }}>
                <ExternalLink size={14} /> Official BIS Portal
              </a>
            )}
          </div>
        </div>
      </div>

      <div className="container" style={{ padding: '32px 24px', display: 'flex', flexDirection: 'column', gap: 20 }}>
        {/* Metadata card */}
        <div style={{ background: '#fff', border: '1px solid var(--clr-border)', borderRadius: 'var(--radius-lg)', padding: '20px 24px' }}>
          <h2 style={{ fontWeight: 700, fontSize: '1rem', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
            <BookOpen size={18} color="var(--clr-primary)" /> Document Metadata
          </h2>
          <MetaRow label="Document Name" value={doc.document_name} />
          <MetaRow label="Title" value={doc.title} />
          <MetaRow label="Document Type" value={doc.document_type} />
          <MetaRow label="Category" value={doc.category} />
          <MetaRow label="Standard Number" value={doc.standard_number} color="var(--clr-warning)" />
          <MetaRow label="Version" value={doc.version} />
          <MetaRow label="Publication Date" value={doc.publication_date} />
          <MetaRow label="Effective Date" value={doc.effective_date} />
          <MetaRow label="Amendment Date" value={doc.amendment_date} />
          <MetaRow label="Amendment Info" value={doc.amendment_information} />
          <MetaRow label="Total Pages" value={doc.total_pages} />
          <MetaRow label="Chunks Indexed" value={data?.total_chunks} color="var(--clr-primary)" />
          <MetaRow label="Ingested At" value={doc.ingested_at ? new Date(doc.ingested_at).toLocaleString() : null} />
          <MetaRow label="File Name" value={doc.file_name} />
        </div>

        {/* Retrieved context viewer */}
        <ChunkViewer chunks={chunks} />
      </div>
    </div>
  );
}
