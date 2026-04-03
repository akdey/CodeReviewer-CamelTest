import React, { useMemo } from 'react';
import { 
  ReactFlow, 
  Background, 
  Controls, 
  Handle, 
  Position 
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import dagre from 'dagre';
import { Network, Zap, CheckCircle2, Circle } from 'lucide-react';

const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

const nodeWidth = 220;
const nodeHeight = 60; // Adjusted for a sleeker node

const getLayoutedElements = (nodes, edges, direction = 'TB') => {
  dagreGraph.setGraph({ rankdir: direction, nodesep: 50, ranksep: 60 });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  const newNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    const newNode = {
      ...node,
      targetPosition: 'top',
      sourcePosition: 'bottom',
      position: {
        x: nodeWithPosition.x - nodeWidth / 2,
        y: nodeWithPosition.y - nodeHeight / 2,
      },
    };
    return newNode;
  });

  return { nodes: newNodes, edges };
};

const CustomTaskNode = ({ data }) => {
  let statusIcon = <Circle size={14} />;
  let borderClass = 'border-pending';
  let bgClass = 'bg-pending';

  if (data.status === 'completed') {
    statusIcon = <CheckCircle2 size={14} className="icon-success" />;
    borderClass = 'border-completed';
  } else if (data.status === 'active') {
    statusIcon = <Zap size={14} className="icon-active pulse" />;
    borderClass = 'border-active shadow-glow';
    bgClass = 'bg-active';
  }

  return (
    <div className={`mission-node ${borderClass} ${bgClass}`}>
      <Handle type="target" position={Position.Top} className="handle-hidden" />
      <div className="node-status">{statusIcon}</div>
      <div className="node-content">
        <div className="node-id">{data.workerId || 'STRATEGIST'}</div>
        <div className="node-desc" title={data.description}>{data.description}</div>
      </div>
      <Handle type="source" position={Position.Bottom} className="handle-hidden" />
    </div>
  );
};

const nodeTypes = {
  customTask: CustomTaskNode,
};

export default function MissionBlueprint({ missionTree }) {
  const tasks = Object.values(missionTree);

  if (tasks.length === 0) {
    return (
      <div className="blueprint-empty" style={{ height: '100%', display: 'flex', justifyContent: 'center' }}>
        <Network size={24} style={{ opacity: 0.3 }} />
        <span>Awaiting Strategy Decomposition...</span>
      </div>
    );
  }

  const { nodes: initialNodes, edges: initialEdges } = useMemo(() => {
    const rawNodes = tasks.map((task) => ({
      id: task.id,
      type: 'customTask',
      data: {
        description: task.description,
        status: task.status,
        workerId: task.workerId,
      },
      position: { x: 0, y: 0 }, // Handled by dagre
    }));

    const rawEdges = tasks
      .filter((task) => task.parentId)
      .map((task) => ({
        id: `e${task.parentId}-${task.id}`,
        source: task.parentId,
        target: task.id,
        type: 'smoothstep',
        animated: task.status === 'active',
        style: { stroke: 'var(--border-color)', strokeWidth: 2 },
      }));

    return getLayoutedElements(rawNodes, rawEdges);
  }, [tasks]);

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ReactFlow
        nodes={initialNodes}
        edges={initialEdges}
        nodeTypes={nodeTypes}
        fitView
        proOptions={{ hideAttribution: true }}
        minZoom={0.2}
        maxZoom={3}
      >
        <Background gap={16} size={1} color="rgba(255, 255, 255, 0.05)" />
        <Controls showInteractive={false} style={{ display: 'flex', flexDirection: 'column' }} />
      </ReactFlow>
    </div>
  );
}
