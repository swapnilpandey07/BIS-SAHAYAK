import React from 'react';
import { Sparkles, Database, Search } from 'lucide-react';

export default function Loading() {
  return (
    <div className="animate-fade-in" style={{
      display: 'flex',
      gap: '14px',
      margin: '18px 0',
      alignItems: 'flex-start',
    }}>
      <div style={{
        width: '38px',
        height: '38px',
        borderRadius: '10px',
        background: 'linear-gradient(135deg, #0f2b5c 0%, #1e3a8a 100%)',
        border: '1.5px solid var(--accent-gold)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
        boxShadow: '0 0 12px rgba(245, 158, 11, 0.3)',
      }}>
        <Sparkles size={18} color="#f59e0b" className="spin-slow" />
      </div>

      <div style={{
        flex: 1,
        background: 'var(--bg-surface)',
        borderRadius: 'var(--radius-md)',
        border: '1px solid var(--border-subtle)',
        padding: '16px 20px',
        maxWidth: '85%',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '0.8rem',
            color: 'var(--accent-gold)',
            fontWeight: 600,
          }}>
            <Search size={14} />
            <span>Searching BIS Documents & Formulating Grounded Answer...</span>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div className="skeleton-shimmer" style={{ height: '14px', borderRadius: '4px', width: '92%' }} />
          <div className="skeleton-shimmer" style={{ height: '14px', borderRadius: '4px', width: '78%' }} />
          <div className="skeleton-shimmer" style={{ height: '14px', borderRadius: '4px', width: '60%' }} />
        </div>
      </div>
    </div>
  );
}
