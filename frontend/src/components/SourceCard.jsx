import React, { useState } from 'react';
import { FileText, ExternalLink, ChevronDown, ChevronUp, Bookmark, Tag } from 'lucide-react';

export default function SourceCard({ source, index }) {
  const [expanded, setExpanded] = useState(false);

  const confidencePercent = source.similarity
    ? Math.round(source.similarity * 100)
    : null;

  return (
    <div style={{
      background: 'var(--bg-card)',
      borderRadius: 'var(--radius-sm)',
      border: '1px solid var(--border-subtle)',
      padding: '12px 14px',
      marginTop: '8px',
      transition: 'all 0.2s ease',
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '8px',
        flexWrap: 'wrap',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1, minWidth: '220px' }}>
          <FileText size={16} color="#f59e0b" style={{ flexShrink: 0 }} />
          <span style={{ fontWeight: 700, fontSize: '0.88rem', color: '#f1f5f9' }}>
            {source.document_name}
          </span>
          {source.page_number && (
            <span style={{
              background: 'rgba(59, 130, 246, 0.2)',
              color: '#60a5fa',
              padding: '2px 8px',
              borderRadius: '6px',
              fontSize: '0.75rem',
              fontWeight: 700,
              border: '1px solid rgba(59, 130, 246, 0.3)',
            }}>
              Page {source.page_number}
            </span>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {confidencePercent !== null && (
            <span style={{
              fontSize: '0.75rem',
              color: '#34d399',
              background: 'rgba(16, 185, 129, 0.12)',
              padding: '2px 8px',
              borderRadius: '6px',
              fontWeight: 600,
            }}>
              {confidencePercent}% match
            </span>
          )}

          {source.source_url && (
            <a
              href={source.source_url}
              target="_blank"
              rel="noopener noreferrer"
              title="Open official BIS reference"
              style={{
                color: 'var(--accent-gold)',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '0.75rem',
                textDecoration: 'none',
                padding: '3px 8px',
                borderRadius: '6px',
                background: 'var(--accent-gold-dim)',
              }}
            >
              <span>BIS Portal</span>
              <ExternalLink size={12} />
            </a>
          )}

          {source.snippet && (
            <button
              onClick={() => setExpanded(!expanded)}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--text-secondary)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                padding: '2px',
              }}
              title={expanded ? "Hide snippet" : "View context snippet"}
            >
              {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </button>
          )}
        </div>
      </div>

      {source.section && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          marginTop: '6px',
          fontSize: '0.75rem',
          color: 'var(--text-secondary)',
        }}>
          <Tag size={12} color="#94a3b8" />
          <span><b>Section:</b> {source.section}</span>
          {source.standard_number && (
            <span style={{
              marginLeft: '8px',
              background: 'rgba(245, 158, 11, 0.15)',
              color: 'var(--accent-gold)',
              padding: '1px 6px',
              borderRadius: '4px',
              fontWeight: 600,
            }}>
              {source.standard_number}
            </span>
          )}
        </div>
      )}

      {expanded && source.snippet && (
        <div style={{
          marginTop: '8px',
          padding: '8px 10px',
          background: 'rgba(0, 0, 0, 0.25)',
          borderRadius: '6px',
          fontSize: '0.8rem',
          color: '#cbd5e1',
          borderLeft: '3px solid var(--accent-gold)',
          fontStyle: 'italic',
          lineHeight: '1.4',
        }}>
          "{source.snippet}"
        </div>
      )}
    </div>
  );
}
