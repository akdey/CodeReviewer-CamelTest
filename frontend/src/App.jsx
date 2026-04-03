import React, { useState, useEffect, useRef } from 'react';
import MissionControl from './components/MissionControl';
import ChatPanel from './components/ChatPanel';
import DiffPanel from './components/DiffPanel';
import TerminalPanel from './components/TerminalPanel';
import MissionBlueprint from './components/MissionBlueprint';
import { Activity, Layout } from 'lucide-react';

export default function App() {
  const [messages, setMessages] = useState([]);
  const [diffFiles, setDiffFiles] = useState([]);
  const [terminalOutput, setTerminalOutput] = useState(null);
  const [missionTree, setMissionTree] = useState({});
  const ws = useRef(null);

  useEffect(() => {
    let mounted = true;
    const socket = new WebSocket('ws://localhost:8000/ws/events');
    ws.current = socket;
    
    socket.onopen = () => {
      if (mounted) console.log("WS: Connected to mission control");
    };
    
    socket.onmessage = (event) => {
      if (!mounted) return;
      try {
        const payload = JSON.parse(event.data);
        console.log("WS RECV:", payload.type, payload.data);
        
        if (payload.type === "communications_stream" || payload.type === "thought_stream") {
          setMessages(prev => [...prev, payload]);
        } else if (payload.type === "orchestration_event") {
          const { subtype, ...details } = payload.data;
          
          setMissionTree(prev => {
              const next = { ...prev };
              if (subtype === "task_created") {
                  next[details.task_id] = { 
                      id: details.task_id, 
                      description: details.description, 
                      parentId: details.parent_id,
                      status: "pending",
                      workerId: null
                  };
              } else if (subtype === "task_assigned" || subtype === "task_started") {
                  if (next[details.task_id]) {
                      next[details.task_id].workerId = details.worker_id;
                      next[details.task_id].status = "active";
                  }
              } else if (subtype === "task_completed") {
                  if (next[details.task_id]) {
                      next[details.task_id].status = "completed";
                  }
              }
              return next;
          });

          // Surfacing rationale and interesting orchestration events
          if (subtype !== "log" || details.is_rationale) {
             const label = details.is_rationale ? "RATIONALE" : subtype.replace(/_/g, ' ');
             setMessages(prev => [...prev, {
                type: "communications_stream",
                data: { speaker: "System", text: `[${label}] ${details.message || details.task_id || ''}` }
             }]);
          }
        } else if (payload.type === "diff_stream") {
          setDiffFiles(payload.data.files || []);
        } else if (payload.type === "terminal_stream") {
          setTerminalOutput(payload.data.output);
        }
      } catch (err) {
        console.error("WS Parse Error:", err, event.data);
      }
    };

    socket.onerror = (err) => {
      if (mounted) console.error("WS Error:", err);
    }
    
    socket.onclose = () => {
      if (mounted) console.warn("WS: Connection closed");
    }

    return () => {
      mounted = false;
      // Only close if it was actually in a state that can be closed
      if (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING) {
        socket.close();
      }
    };
  }, []);

  const handleStartAudit = async () => {
    setMessages([]);
    setDiffFiles([]);
    setTerminalOutput(null);
    setMissionTree({});
    try {
      await fetch('http://localhost:8000/api/start_audit', { method: 'POST' });
    } catch (e) {
      console.error("Failed to start audit", e);
    }
  };

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="glass-panel header-bar">
        <div className="brand">CAMEL-REVIEWER {/* */} HUB</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'linear-gradient(to right, var(--accent-cyan), var(--accent-purple))', WebkitBackgroundClip: 'text', backgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          <Activity size={18} />
          <span style={{ fontSize: '0.9rem', fontWeight: '500'}}>Systems Linked</span>
        </div>
      </header>

      {/* Top Section: Mission Blueprint (THE VISION) */}
      <div className="glass-panel blueprint-area">
        <div className="panel-header">
           <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Layout size={16} />
              Mission Blueprint & Loop Sequence
           </div>
        </div>
        <MissionBlueprint missionTree={missionTree} />
      </div>

      <div className="main-grid">
         {/* Left Column: Mission Control */}
         <div className="glass-panel controls-area">
            <div className="panel-header">Mission Control</div>
            <MissionControl onStart={handleStartAudit} />
         </div>

         {/* Center Column: Chat Matrix */}
         <div className="glass-panel chat-area">
            <div className="panel-header">Agent Neural Feed</div>
            <ChatPanel messages={messages} />
         </div>

         {/* Right Column: Insights */}
         <div className="insights-column">
            {/* Right Column Top: Diff Viewer */}
            <div className="glass-panel diff-area">
               <div className="panel-header">Code Differentiator</div>
               <DiffPanel diffFiles={diffFiles} />
            </div>

            {/* Right Column Bottom: Terminal */}
            <div className="glass-panel terminal-area">
               <div className="panel-header">Terminal I/O</div>
               <TerminalPanel lastOutput={terminalOutput} />
            </div>
         </div>
      </div>
    </div>
  );
}
