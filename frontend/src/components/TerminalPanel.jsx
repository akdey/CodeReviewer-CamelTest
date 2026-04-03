import React, { useEffect, useRef } from 'react';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import 'xterm/css/xterm.css';

export default function TerminalPanel({ lastOutput }) {
  const terminalRef = useRef(null);
  const xtermInstance = useRef(null);
  const fitAddon = useRef(null);

  useEffect(() => {
    // Initialize xterm.js
    const term = new Terminal({
      theme: {
        background: '#0a0a0f',
        foreground: '#00ff88',
        cursor: '#00f0ff',
        selectionBackground: 'rgba(0, 240, 255, 0.3)',
      },
      fontFamily: '"Fira Code", monospace',
      fontSize: 13,
      cursorBlink: true,
      disableStdin: true,
    });
    
    const fit = new FitAddon();
    term.loadAddon(fit);
    
    term.open(terminalRef.current);
    
    // Initial fit with small delay to ensure container dimensions are set
    const timer = setTimeout(() => {
      try {
        if (terminalRef.current) fit.fit();
      } catch (e) {
        console.warn("Xterm fit failed on init:", e);
      }
    }, 100);

    xtermInstance.current = term;
    fitAddon.current = fit;

    // Use ResizeObserver for more reliable fitting
    const resizeObserver = new ResizeObserver(() => {
      try {
        if (terminalRef.current) fit.fit();
      } catch (e) {
        // Safe to ignore if resizing occurs during unmount
      }
    });
    resizeObserver.observe(terminalRef.current);

    return () => {
      clearTimeout(timer);
      resizeObserver.disconnect();
      term.dispose();
    };
  }, []);

  // Effect to write new output when the prop updates
  useEffect(() => {
    if (lastOutput && xtermInstance.current) {
      xtermInstance.current.write(lastOutput);
    }
  }, [lastOutput]);

  return (
    <div style={{ flex: 1, padding: '12px', background: '#0a0a0f' }}>
      <div style={{ width: '100%', height: '100%' }} ref={terminalRef} />
    </div>
  );
}
