import React from 'react';
import { ShieldCheck, Database, Sparkles, BookOpen, Layers } from 'lucide-react';

export default function Header({ health, onOpenDocModal }) {
  const isOnline = health?.status === 'healthy';

  return (
    <header className="glass-panel" style={{
      padding: '16px 28px',
      margin: '16px 20px 24px 20px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      flexWrap: 'wrap',
      gap: '16px',
      borderColor: 'var(--border-subtle)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{
          width: '50px',
          height: '50px',
          borderRadius: '14px',
          background: 'linear-gradient(135deg, #0f2b5c 0%, #1e3a8a 100%)',
          border: '2px solid var(--accent-gold)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 4px 12px rgba(245, 158, 11, 0.25)',
        }}>
          <ShieldCheck size={28} color="#f59e0b" />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h1 style={{
              fontSize: '1.4rem',
              fontWeight: 800,
              letterSpacing: '-0.02em',
              background: 'linear-gradient(90deg, #ffffff 0%, #cbd5e1 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}>
              BIS Intelligent Assistant
            </h1>
            <span style={{
              fontSize: '0.65rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              padding: '2px 8px',
              borderRadius: '999px',
              background: 'var(--accent-gold-dim)',
              color: 'var(--accent-gold)',
              border: '1px solid var(--border-glow)',
            }}>
              SIH 26107
            </span>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
            AI-powered RAG assistant for Bureau of Indian Standards Official Documents & Regulations
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
        {/* Status indicator */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 14px',
          background: isOnline ? 'var(--accent-green-dim)' : 'rgba(239, 68, 68, 0.15)',
          border: `1px solid ${isOnline ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
          borderRadius: '999px',
          fontSize: '0.8rem',
          color: isOnline ? '#34d399' : '#f87171',
          fontWeight: 600,
        }}>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: isOnline ? '#10b981' : '#ef4444',
            boxShadow: isOnline ? '0 0 8px #10b981' : 'none',
          }} />
          {isOnline ? 'System Operational' : 'Connecting API...'}
        </div>

        {/* Chunks count badge */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          padding: '6px 12px',
          background: 'rgba(255, 255, 255, 0.05)',
          borderRadius: '8px',
          fontSize: '0.8rem',
          color: 'var(--text-secondary)',
          border: '1px solid var(--border-subtle)',
        }}>
          <Layers size={14} color="#94a3b8" />
          <span><b>{health?.total_chunks || 0}</b> Chunks Indexed</span>
        </div>

        {/* View indexed docs button */}
        <button
          onClick={onOpenDocModal}
          className="btn-secondary"
          style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
          title="View indexed BIS documents repository"
        >
          <BookOpen size={14} />
          <span>BIS Knowledge Base</span>
        </button>
      </div>
    </header>
  );
}
