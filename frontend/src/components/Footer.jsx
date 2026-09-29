import React from 'react';
import { ShieldCheck, ExternalLink } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer style={{
      background: '#fff',
      borderTop: '1px solid var(--clr-border)',
      padding: '32px 24px',
      marginTop: 'auto',
    }}>
      <div className="container" style={{
        display: 'flex', flexDirection: 'column', gap: 20, alignItems: 'center', textAlign: 'center',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 34, height: 34, borderRadius: 8,
            background: 'linear-gradient(135deg, #1e3a8a, #1d4ed8)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <ShieldCheck size={18} color="#fff" />
          </div>
          <span style={{ fontWeight: 800, color: 'var(--clr-primary-dark)', fontSize: '0.95rem' }}>
            BIS Intelligent Assistant
          </span>
          <span className="badge badge-blue">SIH 26107</span>
        </div>

        <p style={{ fontSize: '0.82rem', color: 'var(--clr-text-muted)', maxWidth: 500, lineHeight: 1.6 }}>
          AI-powered RAG assistant for Bureau of Indian Standards. Answers are grounded exclusively in official BIS documents. For official information visit{' '}
          <a href="https://www.bis.gov.in" target="_blank" rel="noopener noreferrer"
            style={{ color: 'var(--clr-primary)', display: 'inline-flex', alignItems: 'center', gap: 3 }}>
            bis.gov.in <ExternalLink size={10} />
          </a>
        </p>

        <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap', justifyContent: 'center' }}>
          {[
            ['/', 'Home'],
            ['/assistant', 'AI Assistant'],
            ['/documents', 'Documents'],
            ['/search', 'Search'],
            ['/dashboard', 'Dashboard'],
            ['/how-it-works', 'How It Works'],
          ].map(([to, label]) => (
            <Link key={to} to={to} style={{ fontSize: '0.82rem', color: 'var(--clr-text-muted)' }}
              onMouseEnter={e => e.target.style.color = 'var(--clr-primary)'}
              onMouseLeave={e => e.target.style.color = 'var(--clr-text-muted)'}>
              {label}
            </Link>
          ))}
        </div>

        <p style={{ fontSize: '0.75rem', color: '#cbd5e1' }}>
          © {new Date().getFullYear()} BIS Intelligent Assistant · Smart India Hackathon
        </p>
      </div>
    </footer>
  );
}
