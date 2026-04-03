import React from 'react';
import ReactDiffViewer, { DiffMethod } from 'react-diff-viewer-continued';

export default function DiffPanel({ diffFiles }) {
  if (!diffFiles || diffFiles.length === 0) {
    return (
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)', padding: '20px', fontStyle: 'italic', fontSize: '0.9rem' }}>
        No code changes staged yet. Execute the mission to stream diffs.
      </div>
    );
  }

  return (
    <div style={{ flex: 1, padding: '16px', overflowY: 'auto' }}>
      {diffFiles.map((fileDiff, idx) => (
        <div key={idx} style={{ marginBottom: '24px' }}>
          <div style={{ 
            padding: '8px 12px', 
            background: 'var(--bg-primary)', 
            border: '1px solid var(--glass-border)', 
            borderBottom: 'none',
            borderRadius: '8px 8px 0 0',
            fontFamily: 'monospace',
            fontSize: '0.85rem',
            color: 'var(--accent-cyan)'
          }}>
            📄 {fileDiff.filename}
          </div>
          <div style={{ 
            border: '1px solid var(--glass-border)', 
            borderRadius: '0 0 8px 8px', 
            overflow: 'hidden' 
          }}>
            <ReactDiffViewer
              oldValue={fileDiff.old_code}
              newValue={fileDiff.new_code}
              splitView={true}
              useDarkTheme={true}
              compareMethod={DiffMethod.WORDS}
              styles={{
                variables: {
                  dark: {
                    diffViewerBackground: 'var(--bg-primary)',
                    diffViewerTitleBackground: 'rgba(0,0,0,0.5)',
                    addedBackground: 'rgba(0, 255, 136, 0.1)',
                    addedColor: 'var(--text-primary)',
                    removedBackground: 'rgba(255, 51, 102, 0.1)',
                    removedColor: 'var(--text-primary)',
                    wordAddedBackground: 'rgba(0, 255, 136, 0.3)',
                    wordRemovedBackground: 'rgba(255, 51, 102, 0.3)',
                    emptyLineBackground: 'var(--bg-primary)',
                  }
                }
              }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
