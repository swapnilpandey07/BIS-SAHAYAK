import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { User, ShieldCheck, Copy, Check, Volume2, VolumeX, BookOpen, AlertCircle } from 'lucide-react';
import SourceCard from './SourceCard';

export default function Message({ message }) {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const handleCopy = () => {
    if (message.content) {
      navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleSpeak = () => {
    if (!('speechSynthesis' in window)) return;

    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    const utterance = new SpeechSynthesisUtterance(message.content);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);
    setIsSpeaking(true);
    window.speechSynthesis.speak(utterance);
  };

  const isRefusal = message.content?.toLowerCase().includes("could not verify");

  return (
    <div className="animate-fade-in" style={{
      display: 'flex',
      gap: '14px',
      margin: '18px 0',
      alignItems: 'flex-start',
      flexDirection: isUser ? 'row-reverse' : 'row',
    }}>
      {/* Avatar */}
      <div style={{
        width: '38px',
        height: '38px',
        borderRadius: '10px',
        background: isUser
          ? 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)'
          : 'linear-gradient(135deg, #0f2b5c 0%, #1e3a8a 100%)',
        border: `1.5px solid ${isUser ? '#60a5fa' : 'var(--accent-gold)'}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
        boxShadow: isUser ? '0 2px 8px rgba(59, 130, 246, 0.3)' : '0 2px 8px rgba(245, 158, 11, 0.3)',
      }}>
        {isUser ? <User size={20} color="#ffffff" /> : <ShieldCheck size={20} color="#f59e0b" />}
      </div>

      {/* Bubble */}
      <div style={{
        maxWidth: isUser ? '75%' : '85%',
        background: isUser
          ? 'linear-gradient(135deg, #1e3a8a 0%, #172554 100%)'
          : 'var(--bg-surface)',
        border: `1px solid ${isUser ? 'rgba(59, 130, 246, 0.3)' : 'var(--border-subtle)'}`,
        borderRadius: 'var(--radius-md)',
        padding: '16px 20px',
        color: 'var(--text-primary)',
        boxShadow: 'var(--shadow-sm)',
      }}>
        {/* Header meta for Assistant */}
        {!isUser && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '10px',
            borderBottom: '1px solid var(--border-subtle)',
            paddingBottom: '8px',
            flexWrap: 'wrap',
            gap: '8px',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontWeight: 700, fontSize: '0.85rem', color: 'var(--text-gold)' }}>
                BIS Intelligent Assistant
              </span>
              {isRefusal ? (
                <span style={{
                  fontSize: '0.7rem',
                  padding: '2px 8px',
                  borderRadius: '4px',
                  background: 'rgba(239, 68, 68, 0.15)',
                  color: '#f87171',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  fontWeight: 600,
                }}>
                  <AlertCircle size={12} />
                  Information Unverified
                </span>
              ) : (
                <span style={{
                  fontSize: '0.7rem',
                  padding: '2px 8px',
                  borderRadius: '4px',
                  background: 'rgba(16, 185, 129, 0.15)',
                  color: '#34d399',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  fontWeight: 600,
                }}>
                  <ShieldCheck size={12} />
                  Grounded in BIS Context
                </span>
              )}
            </div>

            {/* Actions */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <button
                onClick={handleSpeak}
                className="btn-secondary"
                style={{ padding: '4px 8px', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '4px' }}
                title={isSpeaking ? "Stop speech" : "Read answer aloud"}
              >
                {isSpeaking ? <VolumeX size={13} color="#f87171" /> : <Volume2 size={13} />}
                <span>{isSpeaking ? 'Stop' : 'Listen'}</span>
              </button>

              <button
                onClick={handleCopy}
                className="btn-secondary"
                style={{ padding: '4px 8px', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '4px' }}
                title="Copy answer to clipboard"
              >
                {copied ? <Check size={13} color="#34d399" /> : <Copy size={13} />}
                <span>{copied ? 'Copied' : 'Copy'}</span>
              </button>
            </div>
          </div>
        )}

        {/* Content Body */}
        <div style={{ fontSize: '0.94rem', lineHeight: '1.65', wordBreak: 'break-word' }}>
          {isUser ? (
            <div style={{ whiteSpace: 'pre-wrap' }}>{message.content}</div>
          ) : (
            <ReactMarkdown
              components={{
                p: ({ children }) => <p style={{ marginBottom: '10px' }}>{children}</p>,
                ul: ({ children }) => <ul style={{ paddingLeft: '20px', marginBottom: '10px' }}>{children}</ul>,
                ol: ({ children }) => <ol style={{ paddingLeft: '20px', marginBottom: '10px' }}>{children}</ol>,
                li: ({ children }) => <li style={{ marginBottom: '4px' }}>{children}</li>,
                strong: ({ children }) => <strong style={{ color: '#fbbf24' }}>{children}</strong>,
                code: ({ children }) => (
                  <code style={{
                    background: 'rgba(0,0,0,0.3)',
                    padding: '2px 6px',
                    borderRadius: '4px',
                    color: '#60a5fa',
                    fontFamily: 'monospace'
                  }}>
                    {children}
                  </code>
                )
              }}
            >
              {message.content}
            </ReactMarkdown>
          )}
        </div>

        {/* Verified Sources Accordion */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div style={{
            marginTop: '16px',
            paddingTop: '12px',
            borderTop: '1px solid var(--border-subtle)',
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '0.8rem',
              fontWeight: 700,
              color: 'var(--text-secondary)',
              marginBottom: '8px',
            }}>
              <BookOpen size={14} color="#f59e0b" />
              <span>CITED OFFICIAL SOURCES ({message.sources.length}):</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {message.sources.map((source, idx) => (
                <SourceCard key={idx} source={source} index={idx} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
