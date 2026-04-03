import React from 'react';
import { Play, ShieldAlert, FileCode2, Terminal as TermIcon } from 'lucide-react';

export default function MissionControl({ onStart }) {
  return (
    <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      <div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '16px' }}>
          Initialize the CAMEL Workforce to autonomously audit the isolated `targeted_source_code` environment.
        </p>
        <button className="run-btn" onClick={onStart}>
          <Play size={18} fill="currentColor" />
          START AUDIT
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '20px' }}>
        <div style={{ fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--text-secondary)', fontWeight: 600 }}>Active Nodes</div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', background: 'rgba(0,0,0,0.2)', padding: '12px', borderRadius: '8px' }}>
          <ShieldAlert size={20} color="var(--accent-red)" />
          <div>
            <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>Security Auditor</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>CVE Search & Parsing</div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', background: 'rgba(0,0,0,0.2)', padding: '12px', borderRadius: '8px' }}>
          <TermIcon size={20} color="var(--accent-cyan)" />
          <div>
            <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>SETA Fixer</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Terminal & Subprocess</div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', background: 'rgba(0,0,0,0.2)', padding: '12px', borderRadius: '8px' }}>
          <FileCode2 size={20} color="var(--accent-purple)" />
          <div>
            <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>OWL Strategist</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Workforce Coordinator</div>
          </div>
        </div>

      </div>
    </div>
  );
}
