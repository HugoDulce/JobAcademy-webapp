import { useCallback, useEffect, useState } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  type Node,
  type Edge,
  useNodesState,
  useEdgesState,
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import dagre from 'dagre';
import { fetchGraph } from '../api/graph';
import type { KnowledgeGraph, GraphNode as GN } from '../types/graph';

function getLayoutedElements(graphData: KnowledgeGraph) {
  const g = new dagre.graphlib.Graph();
  g.setDefaultEdgeLabel(() => ({}));
  g.setGraph({ rankdir: 'TB', nodesep: 60, ranksep: 100, marginx: 40, marginy: 40 });

  graphData.nodes.forEach((node) => {
    g.setNode(node.id, { width: 160, height: 50 });
  });
  graphData.edges.forEach((edge) => {
    g.setEdge(edge.source, edge.target);
  });

  dagre.layout(g);

  const nodes: Node[] = graphData.nodes.map((node) => {
    const pos = g.node(node.id);
    const masteryBorder = node.mastery !== null
      ? node.mastery >= 0.8 ? '#22c55e'
        : node.mastery >= 0.3 ? '#eab308'
        : '#d1d5db'
      : '#d1d5db';

    return {
      id: node.id,
      position: { x: pos.x - 80, y: pos.y - 25 },
      data: { label: node.label, node },
      style: {
        background: node.fill_color,
        border: `2px solid ${masteryBorder}`,
        borderRadius: '8px',
        padding: '8px 12px',
        fontSize: '11px',
        fontWeight: 500,
        width: 160,
        textAlign: 'center' as const,
        color: '#1f2937',
      },
    };
  });

  const edges: Edge[] = graphData.edges.map((edge, i) => ({
    id: `e-${i}`,
    source: edge.source,
    target: edge.target,
    type: 'smoothstep',
    animated: false,
    style: { stroke: '#9ca3af', strokeWidth: 1 },
    markerEnd: { type: MarkerType.ArrowClosed, width: 12, height: 12, color: '#9ca3af' },
  }));

  return { nodes, edges };
}

export default function KnowledgeGraphPage() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selected, setSelected] = useState<GN | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchGraph().then((data) => {
      const { nodes: n, edges: e } = getLayoutedElements(data);
      setNodes(n);
      setEdges(e);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const onNodeClick = useCallback((_: unknown, node: Node) => {
    setSelected(node.data.node as GN);
  }, []);

  if (loading) return <div className="text-gray-500">Loading knowledge graph...</div>;

  return (
    <div className="h-[calc(100vh-48px)] flex">
      <div className="flex-1 relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
          fitView
          minZoom={0.1}
          maxZoom={2}
        >
          <Background />
          <Controls />
          <MiniMap
            nodeColor={(n) => n.style?.background as string || '#e5e7eb'}
            maskColor="rgba(0,0,0,0.1)"
          />
        </ReactFlow>
      </div>
      {selected && (
        <div className="w-72 bg-white border-l p-4 overflow-y-auto">
          <h3 className="font-bold text-lg mb-2">{selected.label}</h3>
          <div className="space-y-2 text-sm">
            <div><span className="text-gray-500">Layer:</span> {selected.layer_name}</div>
            <div><span className="text-gray-500">Level:</span> {selected.layer}</div>
            <div>
              <span className="text-gray-500">Mastery:</span>{' '}
              {selected.mastery !== null ? `${Math.round(selected.mastery * 100)}%` : 'No data'}
            </div>
            <div className="mt-3">
              <span className="inline-block px-2 py-1 rounded text-xs" style={{
                background: selected.fill_color,
                border: `1px solid ${selected.stroke_color}`,
              }}>
                {selected.style_class}
              </span>
            </div>
          </div>
          <button onClick={() => setSelected(null)} className="mt-4 text-xs text-gray-400 hover:text-gray-600">
            Close
          </button>
        </div>
      )}
    </div>
  );
}
