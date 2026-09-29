import React, { useState, useEffect } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  ShieldCheck, Home, MessageSquare, BookOpen,
  Search, BarChart2, HelpCircle, Menu, X
} from 'lucide-react';

const NAV_LINKS = [
  { to: '/',             label: 'Home',          icon: Home },
  { to: '/assistant',    label: 'AI Assistant',  icon: MessageSquare },
  { to: '/documents',    label: 'Documents',     icon: BookOpen },
  { to: '/search',       label: 'Search',        icon: Search },
  { to: '/dashboard',    label: 'Dashboard',     icon: BarChart2 },
  { to: '/how-it-works', label: 'How It Works',  icon: HelpCircle },
];

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();

  useEffect(() => {
    setMenuOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <>
      <nav style={{
        position: 'fixed',
        top: 0, left: 0, right: 0,
        height: 'var(--nav-height)',
        zIndex: 1000,
        background: scrolled ? 'rgba(255,255,255,0.95)' : 'rgba(255,255,255,0.9)',
        backdropFilter: 'blur(14px)',
        WebkitBackdropFilter: 'blur(14px)',
        borderBottom: `1px solid ${scrolled ? 'var(--clr-border)' : 'rgba(226,232,240,0.6)'}`,
        boxShadow: scrolled ? 'var(--shadow-sm)' : 'none',
        transition: 'all var(--transition)',
      }}>
        <div className="container" style={{
          height: '100%', display: 'flex',
          alignItems: 'center', justifyContent: 'space-between', gap: 16,
        }}>
          {/* Brand */}
          <NavLink to="/" style={{ display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0 }}>
            <div style={{
              width: 38, height: 38, borderRadius: 10,
              background: 'linear-gradient(135deg, #1e3a8a, #1d4ed8)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 2px 12px rgba(29,78,216,0.25)',
            }}>
              <ShieldCheck size={20} color="#fff" />
            </div>
            <div>
              <div style={{ fontWeight: 800, fontSize: '0.95rem', color: 'var(--clr-primary-dark)', lineHeight: 1.2 }}>
                BIS Assistant
              </div>
              <div style={{ fontSize: '0.65rem', color: 'var(--clr-text-muted)', fontWeight: 500, letterSpacing: '0.04em' }}>
                RAG-POWERED
              </div>
            </div>
          </NavLink>

          {/* Desktop Links */}
          <div className="hide-mobile" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            {NAV_LINKS.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
              >
                <Icon size={15} />
                {label}
              </NavLink>
            ))}
          </div>

          {/* Desktop CTA */}
          <NavLink to="/assistant" className="btn btn-primary btn-sm hide-mobile">
            <MessageSquare size={15} />
            Ask BIS
          </NavLink>

          {/* Mobile hamburger */}
          <button
            className="hide-desktop btn btn-icon"
            onClick={() => setMenuOpen(v => !v)}
            aria-label="Toggle menu"
          >
            {menuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </nav>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="hide-desktop animate-slide-down" style={{
          position: 'fixed',
          top: 'var(--nav-height)', left: 0, right: 0,
          zIndex: 999,
          background: 'rgba(255,255,255,0.98)',
          backdropFilter: 'blur(16px)',
          borderBottom: '1px solid var(--clr-border)',
          padding: '16px',
          boxShadow: 'var(--shadow-lg)',
          display: 'flex',
          flexDirection: 'column',
          gap: 4,
        }}>
          {NAV_LINKS.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
              style={{ padding: '12px 16px', borderRadius: 'var(--radius-md)', fontSize: '0.95rem' }}
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
          <div style={{ marginTop: 8, paddingTop: 12, borderTop: '1px solid var(--clr-border)' }}>
            <NavLink to="/assistant" className="btn btn-primary" style={{ width: '100%', justifyContent: 'center' }}>
              <MessageSquare size={16} />
              Open AI Assistant
            </NavLink>
          </div>
        </div>
      )}
    </>
  );
}
