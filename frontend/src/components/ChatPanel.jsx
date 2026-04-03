import React, { useEffect, useRef } from 'react';

export default function ChatPanel({ messages }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const getColor = (actor) => {
    if (actor?.includes('Auditor')) return 'var(--accent-red)';
    if (actor?.includes('Fixer')) return 'var(--accent-cyan)';
    if (actor?.includes('Strategist') || actor?.includes('Workforce')) return 'var(--accent-purple)';
    return 'var(--text-primary)';
  };

  return (
    <div style={{ flex: 1, padding: '16px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {messages.length === 0 && (
        <div style={{ margin: 'auto', color: 'var(--text-secondary)', fontStyle: 'italic', fontSize: '0.9rem' }}>
          Awaiting agent streams...
        </div>
      )}
      
      {messages.map((msg, i) => {
        // Extract inner details depending on stream type
        const isThought = msg.type === "thought_stream";
        const actor = isThought ? msg.data.agent : msg.data.speaker;
        const text = isThought ? msg.data.message : msg.data.text;
        const color = getColor(actor);

        return (
          <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div style={{ fontSize: '0.8rem', fontWeight: 600, color: color, textTransform: 'uppercase' }}>
              {actor} {isThought && <span style={{opacity: 0.5}}>[THOUGHT]</span>}
            </div>
            <div style={{ 
              background: 'rgba(0,0,0,0.3)', 
              padding: '12px', 
              borderRadius: '8px', 
              borderLeft: `2px solid ${color}`,
              fontSize: '0.9rem',
              whiteSpace: 'pre-wrap',
              lineHeight: 1.5,
              wordBreak: 'break-word'
            }}>
              {text}
            </div>
            {isThought && msg.data.tool_calls && msg.data.tool_calls !== "None" && (
                <div style={{ 
                    marginTop: '4px', padding: '8px', background: 'rgba(20,20,30,0.8)', 
                    borderRadius: '4px', fontSize: '0.75rem', fontFamily: 'monospace', color: 'var(--accent-green)'
                }}>
                    [TOOL INVOCATION]: {msg.data.tool_calls}
                </div>
            )}
          </div>
        );
      })}
      <div ref={endRef} />
    </div>
  );
}
