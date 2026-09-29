import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import Chat from '../components/Chat';
import { askBISAssistant, fetchSystemHealth, fetchIndexedDocuments, triggerIngestion } from '../services/api';
import { X, BookOpen, FileCheck, RefreshCw, ExternalLink, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function Home() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState(null);
  const [showDocModal, setShowDocModal] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [ingesting, setIngesting] = useState(false);
  const [ingestStatus, setIngestStatus] = useState(null);

  const loadHealthAndDocs = async () => {
    const h = await fetchSystemHealth();
    setHealth(h);
    const d = await fetchIndexedDocuments();
    setDocuments(d.documents || []);
  };

  useEffect(() => {
    loadHealthAndDocs();
    const interval = setInterval(loadHealthAndDocs, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleSendMessage = async ({ question, category_filter }) => {
    const userMsg = { role: 'user', content: question };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const response = await askBISAssistant({ question, category_filter });
      const assistantMsg = {
        role: 'assistant',
        content: response.answer,
        sources: response.sources || [],
        retrieved_chunks: response.retrieved_chunks || 0,
        model_used: response.model_used,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      console.error('Error asking assistant:', err);
      const errorMsg = {
        role: 'assistant',
        content: `Sorry, an error occurred while connecting to the BIS Assistant: ${err.message}. Please check that the backend server is running.`,
        sources: [],
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleResetChat = () => {
    setMessages([]);
  };

  const handleTriggerIngest = async (force = false) => {
    setIngesting(true);
    setIngestStatus(null);
    try {
      const result = await triggerIngestion(force);
      setIngestStatus({
        type: 'success',
        message: `Successfully processed ${result.indexed_documents?.length || 0} documents (${result.total_chunks_indexed} chunks indexed).`,
      });
      await loadHealthAndDocs();
    } catch (err) {
      setIngestStatus({
        type: 'error',
        message: `Ingestion failed: ${err.message}`,
      });
    } finally {
      setIngesting(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Header
        health={health}
        onOpenDocModal={() => setShowDocModal(true)}
      />

      <main style={{ flex: 1 }}>
        <Chat
          messages={messages}
          onSendMessage={handleSendMessage}
          loading={loading}
          onResetChat={handleResetChat}
        />
      </main>

      {/* Document Knowledge Base Modal */}
      {showDocModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(5, 10, 25, 0.85)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '20px',
        }}>
          <div className="glass-panel animate-fade-in" style={{
            width: '100%',
            maxWidth: '800px',
            maxHeight: '85vh',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            boxShadow: 'var(--shadow-md)',
          }}>
            {/* Modal Header */}
            <div style={{
              padding: '18px 24px',
              borderBottom: '1px solid var(--border-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <BookOpen size={22} color="var(--accent-gold)" />
                <h3 style={{ fontSize: '1.2rem', fontWeight: 800 }}>
                  Indexed BIS Knowledge Repository
                </h3>
              </div>
              <button
                onClick={() => setShowDocModal(false)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--text-secondary)',
                  cursor: 'pointer',
                  padding: '4px',
                }}
              >
                <X size={20} />
              </button>
            </div>

            {/* Ingest Action Bar */}
            <div style={{
              padding: '12px 24px',
              background: 'rgba(255, 255, 255, 0.02)',
              borderBottom: '1px solid var(--border-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '10px',
            }}>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Total indexed documents: <b>{documents.length}</b>
              </span>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  onClick={() => handleTriggerIngest(false)}
                  disabled={ingesting}
                  className="btn-secondary"
                  style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
                >
                  <RefreshCw size={13} className={ingesting ? "spin-slow" : ""} />
                  <span>{ingesting ? 'Indexing...' : 'Index New Documents'}</span>
                </button>
                <button
                  onClick={() => handleTriggerIngest(true)}
                  disabled={ingesting}
                  className="btn-secondary"
                  style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
                >
                  <span>Force Re-Index All</span>
                </button>
              </div>
            </div>

            {/* Ingestion status alert */}
            {ingestStatus && (
              <div style={{
                margin: '12px 24px 0 24px',
                padding: '10px 14px',
                borderRadius: '8px',
                fontSize: '0.85rem',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                background: ingestStatus.type === 'success' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                color: ingestStatus.type === 'success' ? '#34d399' : '#f87171',
                border: `1px solid ${ingestStatus.type === 'success' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
              }}>
                {ingestStatus.type === 'success' ? <CheckCircle2 size={16} /> : <AlertTriangle size={16} />}
                <span>{ingestStatus.message}</span>
              </div>
            )}

            {/* Modal Body */}
            <div style={{ padding: '20px 24px', overflowY: 'auto', flex: 1 }}>
              {documents.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)' }}>
                  <FileCheck size={40} style={{ opacity: 0.5, marginBottom: '12px' }} />
                  <p>No documents indexed yet. Place PDFs into <code>documents/raw/</code> and click "Index New Documents".</p>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {documents.map((doc, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: '14px 16px',
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: 'var(--radius-sm)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        flexWrap: 'wrap',
                        gap: '10px',
                      }}
                    >
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <span style={{ fontWeight: 700, fontSize: '0.92rem', color: '#ffffff' }}>
                            {doc.document_name}
                          </span>
                          <span style={{
                            fontSize: '0.7rem',
                            textTransform: 'uppercase',
                            padding: '2px 8px',
                            borderRadius: '4px',
                            background: 'var(--accent-blue-dim)',
                            color: '#60a5fa',
                            fontWeight: 700,
                          }}>
                            {doc.category || 'General'}
                          </span>
                        </div>
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                          File: <code>{doc.file_name}</code> • Chunks: <b>{doc.chunks_count || 'N/A'}</b>
                        </div>
                      </div>

                      {doc.source_url && (
                        <a
                          href={doc.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="btn-secondary"
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '6px',
                            textDecoration: 'none',
                            fontSize: '0.78rem',
                          }}
                        >
                          <span>Official Portal</span>
                          <ExternalLink size={12} />
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
