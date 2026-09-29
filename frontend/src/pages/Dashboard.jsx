import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BarChart2, Database, FileText, Layers, ShieldCheck,
  CheckCircle, AlertCircle, RefreshCw, Cpu, Activity,
  Server, Calendar, ArrowRight, Tag, BookOpen, ExternalLink
} from 'lucide-react';
import { getDocumentStats, getHealth, getDocuments } from '../services/api';

const CATEGORY_NAMES = {
  acts: 'Acts & Legislation',
  rules: 'Statutory Rules',
  regulations: 'Regulations',
  certification: 'Certification Schemes',
  hallmarking: 'Hallmarking & Purity',
  laboratories: 'Laboratory Testing',
  standards: 'Indian Standards (IS)',
  qco: 'Quality Control Orders',
  consumer: 'Consumer Awareness',
  handbooks: 'Technical Handbooks',
  awareness: 'Public Information',
  booklets: 'Guides & Booklets'
};

const CATEGORY_COLORS = {
  acts: '#1d4ed8',
  rules: '#059669',
  regulations: '#7c3aed',
  certification: '#d97706',
  hallmarking: '#b45309',
  laboratories: '#0891b2',
  standards: '#6366f1',
  qco: '#e11d48',
  consumer: '#10b981',
  handbooks: '#2563eb',
  awareness: '#f59e0b',
  booklets: '#8b5cf6'
};

export default function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [health, setHealth] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    setLoading(true);
    setError('');
    try {
      const [statsData, healthData, docsData] = await Promise.all([
        getDocumentStats().catch(() => null),
        getHealth().catch(() => null),
        getDocuments().catch(() => ({ count: 0, documents: [] }))
      ]);

      setStats(statsData);
      setHealth(healthData);
      setDocuments(docsData.documents || []);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Unable to load live dashboard statistics. Please verify FastAPI backend service.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  const totalDocs = stats?.total_documents ?? health?.total_documents ?? documents.length ?? 0;
  const totalChunks = stats?.total_chunks ?? health?.total_chunks ?? 0;
  const categoriesMap = stats?.categories || {};
  const docTypesMap = stats?.document_types || {};

  return (
    <div className="page-wrapper" style={{ padding: '40px 24px 80px', minHeight: 'calc(100vh - var(--nav-height))' }}>
      <div className="container" style={{ maxWidth: 1100 }}>

        {/* Page Header */}
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16, marginBottom: 32 }} className="animate-fade-up">
          <div>
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              padding: '6px 14px', borderRadius: 'var(--radius-full)',
              background: 'var(--clr-primary-light)', color: 'var(--clr-primary)',
              fontSize: '0.78rem', fontWeight: 700, marginBottom: 12
            }}>
              <Activity size={14} />
              REAL-TIME RAG TELEMETRY & STATS
            </div>
            <h1 style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--clr-primary-dark)', margin: 0 }}>
              Knowledge Base Dashboard
            </h1>
            <p style={{ color: 'var(--clr-text-secondary)', fontSize: '0.95rem', marginTop: 6, margin: 0 }}>
              Live metrics retrieved directly from the BIS vector index and FastAPI backend.
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <button
              onClick={handleRefresh}
              disabled={refreshing || loading}
              className="btn btn-secondary btn-sm"
              style={{ padding: '8px 16px' }}
            >
              <RefreshCw size={14} className={refreshing ? 'animate-spin' : ''} />
              {refreshing ? 'Refreshing...' : 'Refresh Telemetry'}
            </button>
            <button
              onClick={() => navigate('/documents')}
              className="btn btn-primary btn-sm"
              style={{ padding: '8px 16px' }}
            >
              <BookOpen size={14} />
              Explore All Documents
            </button>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="alert alert-error animate-fade-in" style={{ marginBottom: 24 }}>
            <AlertCircle size={18} />
            <div>{error}</div>
          </div>
        )}

        {/* Key Metrics Cards */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))',
          gap: 20,
          marginBottom: 32
        }} className="animate-fade-up">

          {/* Metric 1: Total Documents */}
          <div className="card" style={{ padding: '20px 24px', position: 'relative', overflow: 'hidden' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
              <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--clr-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Total Indexed Docs
              </span>
              <div style={{ width: 36, height: 36, borderRadius: 8, background: '#eff6ff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <FileText size={18} color="#1d4ed8" />
              </div>
            </div>
            <div style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--clr-primary-dark)', lineHeight: 1 }}>
              {loading ? '—' : totalDocs}
            </div>
            <div style={{ fontSize: '0.78rem', color: 'var(--clr-text-secondary)', marginTop: 8, display: 'flex', alignItems: 'center', gap: 4 }}>
              <CheckCircle size={12} color="var(--clr-success)" />
              100% verified official standards
            </div>
          </div>

          {/* Metric 2: Total Vector Chunks */}
          <div className="card" style={{ padding: '20px 24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
              <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--clr-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Vector Chunks
              </span>
              <div style={{ width: 36, height: 36, borderRadius: 8, background: '#f0fdf4', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Layers size={18} color="#059669" />
              </div>
            </div>
            <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#059669', lineHeight: 1 }}>
              {loading ? '—' : totalChunks}
            </div>
            <div style={{ fontSize: '0.78rem', color: 'var(--clr-text-secondary)', marginTop: 8 }}>
              Text passages with embeddings
            </div>
          </div>

          {/* Metric 3: Active Categories */}
          <div className="card" style={{ padding: '20px 24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
              <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--clr-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Categories
              </span>
              <div style={{ width: 36, height: 36, borderRadius: 8, background: '#fdf4ff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Tag size={18} color="#7c3aed" />
              </div>
            </div>
            <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#7c3aed', lineHeight: 1 }}>
              {loading ? '—' : Object.keys(categoriesMap).length}
            </div>
            <div style={{ fontSize: '0.78rem', color: 'var(--clr-text-secondary)', marginTop: 8 }}>
              Acts, Standards, QCOs, Rules
            </div>
          </div>

          {/* Metric 4: System Status */}
          <div className="card" style={{ padding: '20px 24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
              <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--clr-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                RAG Engine Status
              </span>
              <div style={{ width: 36, height: 36, borderRadius: 8, background: health?.status === 'healthy' ? '#f0fdf4' : '#fff1f2', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Server size={18} color={health?.status === 'healthy' ? '#059669' : '#e11d48'} />
              </div>
            </div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: health?.status === 'healthy' ? 'var(--clr-success)' : 'var(--clr-error)', lineHeight: 1.2 }}>
              {health?.status === 'healthy' ? 'OPERATIONAL' : 'OFFLINE / DISCONNECTED'}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--clr-text-muted)', marginTop: 8 }}>
              FastAPI v{health?.version || '2.0.0'}
            </div>
          </div>

        </div>

        {/* Two Columns: Category Breakdown + System Health Spec */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))',
          gap: 24,
          marginBottom: 32
        }} className="animate-fade-up">

          {/* Category Distribution Card */}
          <div className="card" style={{ padding: '24px' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--clr-primary-dark)', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
              <BarChart2 size={18} color="var(--clr-primary)" />
              Category Breakdown
            </h3>

            {Object.keys(categoriesMap).length === 0 ? (
              <p style={{ color: 'var(--clr-text-muted)', fontSize: '0.88rem' }}>No categories registered.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                {Object.entries(categoriesMap).map(([catKey, count]) => {
                  const percentage = totalDocs > 0 ? Math.round((count / totalDocs) * 100) : 0;
                  const clr = CATEGORY_COLORS[catKey] || '#1d4ed8';
                  const label = CATEGORY_NAMES[catKey] || catKey.toUpperCase();

                  return (
                    <div key={catKey}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: 4 }}>
                        <span style={{ fontWeight: 600, color: 'var(--clr-text-primary)' }}>{label}</span>
                        <span style={{ color: 'var(--clr-text-muted)', fontWeight: 700 }}>{count} doc{count > 1 ? 's' : ''} ({percentage}%)</span>
                      </div>
                      <div style={{ height: 8, width: '100%', background: 'var(--clr-border)', borderRadius: 4, overflow: 'hidden' }}>
                        <div
                          style={{
                            height: '100%',
                            width: `${percentage}%`,
                            background: clr,
                            borderRadius: 4,
                            transition: 'width 0.6s ease'
                          }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* System Components & Health */}
          <div className="card" style={{ padding: '24px' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--clr-primary-dark)', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
              <Cpu size={18} color="var(--clr-primary)" />
              Backend Architecture Health
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 14px', background: 'var(--clr-bg)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--clr-border)' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--clr-text-secondary)' }}>Vector Store (pgvector / HNSW)</span>
                <span className={`badge ${health?.database_connected ? 'badge-green' : 'badge-gray'}`}>
                  {health?.database_connected ? 'Supabase Connected' : 'Local Vector Store Active'}
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 14px', background: 'var(--clr-bg)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--clr-border)' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--clr-text-secondary)' }}>Embedding Model</span>
                <span className="badge badge-indigo">
                  {health?.embedding_model || 'text-embedding-004 (768-dim)'}
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 14px', background: 'var(--clr-bg)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--clr-border)' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--clr-text-secondary)' }}>Google Gemini AI</span>
                <span className={`badge ${health?.gemini_configured ? 'badge-green' : 'badge-warning'}`}>
                  {health?.gemini_configured ? 'API Configured' : 'Key Missing'}
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 14px', background: 'var(--clr-bg)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--clr-border)' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--clr-text-secondary)' }}>Last Ingestion Date</span>
                <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--clr-text-primary)' }}>
                  {stats?.latest_ingestion_date ? new Date(stats.latest_ingestion_date).toLocaleDateString() : 'Active Index'}
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 14px', background: 'var(--clr-bg)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--clr-border)' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--clr-text-secondary)' }}>Strict Anti-Hallucination</span>
                <span className="badge badge-green">
                  Enabled (Grounded Refusal)
                </span>
              </div>

            </div>
          </div>

        </div>

        {/* Recently Indexed Documents Table */}
        <div className="card animate-fade-up" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--clr-primary-dark)', margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
              <Database size={18} color="var(--clr-primary)" />
              Indexed Documents Sample ({documents.slice(0, 6).length} of {documents.length})
            </h3>
            <button
              onClick={() => navigate('/documents')}
              className="btn btn-ghost btn-sm"
              style={{ fontSize: '0.82rem' }}
            >
              View Full Directory <ArrowRight size={13} />
            </button>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--clr-border)', color: 'var(--clr-text-muted)' }}>
                  <th style={{ padding: '10px 12px', fontWeight: 700 }}>DOCUMENT TITLE</th>
                  <th style={{ padding: '10px 12px', fontWeight: 700 }}>STANDARD #</th>
                  <th style={{ padding: '10px 12px', fontWeight: 700 }}>CATEGORY</th>
                  <th style={{ padding: '10px 12px', fontWeight: 700 }}>CHUNKS</th>
                  <th style={{ padding: '10px 12px', fontWeight: 700 }}>STATUS</th>
                  <th style={{ padding: '10px 12px', fontWeight: 700, textAlign: 'right' }}>ACTION</th>
                </tr>
              </thead>
              <tbody>
                {documents.slice(0, 6).map((doc, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid var(--clr-border)', transition: 'background 0.15s ease' }}>
                    <td style={{ padding: '12px', fontWeight: 600, color: 'var(--clr-primary-dark)' }}>
                      {doc.title || doc.document_name}
                    </td>
                    <td style={{ padding: '12px', color: 'var(--clr-text-secondary)', fontFamily: 'monospace' }}>
                      {doc.standard_number || '—'}
                    </td>
                    <td style={{ padding: '12px' }}>
                      <span className="badge badge-gray">{doc.category || 'general'}</span>
                    </td>
                    <td style={{ padding: '12px', color: 'var(--clr-text-secondary)' }}>
                      {doc.chunks_count || '—'}
                    </td>
                    <td style={{ padding: '12px' }}>
                      <span className="badge badge-green">{doc.status || 'indexed'}</span>
                    </td>
                    <td style={{ padding: '12px', textAlign: 'right' }}>
                      <button
                        onClick={() => navigate(`/documents/${encodeURIComponent(doc.document_id || doc.document_name)}`)}
                        className="btn btn-ghost btn-sm"
                        style={{ padding: '4px 8px', fontSize: '0.78rem' }}
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  );
}
