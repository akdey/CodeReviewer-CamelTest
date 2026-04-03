import React from 'react';
import { Network, Zap, CheckCircle2, Circle } from 'lucide-react';

export default function MissionBlueprint({ missionTree }) {
  const tasks = Object.values(missionTree);
  
  if (tasks.length === 0) {
    return (
      <div className="blueprint-empty">
        <Network size={24} style={{ opacity: 0.3 }} />
        <span>Awaiting Strategy Decomposition...</span>
      </div>
    );
  }

  // Find root tasks (no parent)
  const rootTasks = tasks.filter(t => !t.parentId);

  const renderTaskNode = (task) => {
    const isDecomposed = tasks.some(t => t.parentId === task.id);
    const childTasks = tasks.filter(t => t.parentId === task.id);
    
    let statusIcon = <Circle size={14} />;
    let statusClass = "pending";
    
    if (task.status === "completed") {
        statusIcon = <CheckCircle2 size={14} className="icon-success" />;
        statusClass = "completed";
    } else if (task.status === "active") {
        statusIcon = <Zap size={14} className="icon-active pulse" />;
        statusClass = "active";
    }

    return (
      <div key={task.id} className={`blueprint-node-container ${statusClass}`}>
        <div className="blueprint-node">
          <div className="node-status">{statusIcon}</div>
          <div className="node-content">
            <div className="node-id">{task.workerId || "STRATEGIST"}</div>
            <div className="node-desc">{task.description}</div>
          </div>
        </div>
        
        {childTasks.length > 0 && (
          <div className="blueprint-children">
            <div className="connector-line"></div>
            <div className="children-grid">
              {childTasks.map(child => renderTaskNode(child))}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="mission-blueprint-scroll">
       <div className="blueprint-tree">
          {rootTasks.map(root => renderTaskNode(root))}
       </div>
    </div>
  );
}
