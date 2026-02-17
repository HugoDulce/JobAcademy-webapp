import { useCallback, useEffect, useState, type MouseEvent } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Position,
  type Node,
  type Edge,
  useNodesState,
  useEdgesState,
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import dagre from 'dagre';
import { Play } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import {
  fetchGraph,
  fetchSubtree,
  fetchSubtreeCardDistribution,
  fetchNodeSubtopics,
  fetchSubtopicCards,
} from '../api/graph';
import type { Card } from '../types/card';
import type {
  KnowledgeGraph,
  GraphNode as GN,
  NavItem,
  Subtopic,
  SubtreeCardDistribution,
} from '../types/graph';

type ViewMode = 'full' | 'prerequisiteTree' | 'subtopic' | 'card';
type LayoutMode = 'auto' | 'arrange';
type ManualNodePositions = Record<string, { x: number; y: number }>;

const MANUAL_LAYOUT_STORAGE_KEY = 'knowledge-graph.manual-layouts.v1';
const MERGE_NODE_PREFIX = '__merge__::';

function extractQuestionLabel(card: Card): string {
  const source = card.prompt || '';
  const match = source.match(/^#?\s*Q:\s*(.+?)(?:\n|$)/im);
  if (match?.[1]) return match[1].trim();
  const firstLine = source.split('\n')[0]?.replace(/^#\s*/, '').trim() || card.card_id;
  if (firstLine.length <= 80) return firstLine;
  return `${firstLine.slice(0, 77)}...`;
}

function extractLayerFromDeck(deck: string | null): string {
  if (!deck) return 'Unknown';
  const layer = deck.split('::')[2];
  return layer?.trim() || 'Unknown';
}

function parseLayerOrder(layer: string): number {
  const numericPrefix = layer.match(/^\s*(\d+)/)?.[1];
  return numericPrefix ? Number.parseInt(numericPrefix, 10) : 999;
}

function formatLayerLabel(layer: string): string {
  const match = layer.match(/^\s*(\d+)\s*-\s*(.+)\s*$/);
  if (!match) return layer;
  const [, num, name] = match;
  return `Layer ${num}: ${name}`;
}

function slugify(value: string): string {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
}

/* ---------- Layout helpers ---------- */

function toNumeric(value: unknown, fallback: number): number {
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (typeof value === 'string') {
    const parsed = Number.parseFloat(value);
    if (Number.isFinite(parsed)) return parsed;
  }
  return fallback;
}

function getNodeDimensions(node: Node, fallbackWidth: number, fallbackHeight: number) {
  const style = (node.style ?? {}) as { width?: unknown; height?: unknown };
  const width = toNumeric(node.width ?? style.width, fallbackWidth);
  const height = toNumeric(node.height ?? style.height, fallbackHeight);
  return { width, height };
}

function getNodeCenter(node: Node, fallbackWidth: number, fallbackHeight: number) {
  const { width, height } = getNodeDimensions(node, fallbackWidth, fallbackHeight);
  return {
    x: node.position.x + width / 2,
    y: node.position.y + height / 2,
  };
}

function buildRoutedEdges(
  graphEdges: KnowledgeGraph['edges'],
  baseNodes: Node[],
  mode: ViewMode,
) {
  if (mode === 'full') {
    const directEdges: Edge[] = graphEdges.map((edge, i) => ({
      id: `e-${i}`,
      source: edge.source,
      target: edge.target,
      type: 'smoothstep',
      animated: false,
      style: { stroke: '#9ca3af', strokeWidth: 1 },
      markerEnd: { type: MarkerType.ArrowClosed, width: 12, height: 12, color: '#9ca3af' },
    }));
    return { nodes: baseNodes, edges: directEdges };
  }

  const nodeById = new Map(baseNodes.map((node) => [node.id, node]));
  const groupedByTarget = new Map<string, KnowledgeGraph['edges']>();
  graphEdges.forEach((edge) => {
    const existing = groupedByTarget.get(edge.target) ?? [];
    groupedByTarget.set(edge.target, [...existing, edge]);
  });

  const edges: Edge[] = [];
  const extraNodes: Node[] = [];
  let edgeIndex = 0;

  const addDirectEdge = (edge: KnowledgeGraph['edges'][number], withArrow: boolean) => {
    edges.push({
      id: `e-${edgeIndex++}`,
      source: edge.source,
      target: edge.target,
      type: 'step',
      animated: false,
      style: { stroke: '#111827', strokeWidth: 1.8 },
      ...(withArrow
        ? { markerEnd: { type: MarkerType.ArrowClosed, width: 12, height: 12, color: '#111827' } }
        : {}),
    });
  };

  groupedByTarget.forEach((incomingEdges, targetId) => {
    const targetNode = nodeById.get(targetId);
    if (!targetNode || incomingEdges.length <= 1) {
      incomingEdges.forEach((edge) => addDirectEdge(edge, true));
      return;
    }

    const sourceNodes = incomingEdges
      .map((edge) => nodeById.get(edge.source))
      .filter((node): node is Node => !!node);

    if (sourceNodes.length <= 1) {
      incomingEdges.forEach((edge) => addDirectEdge(edge, true));
      return;
    }

    const targetCenter = getNodeCenter(targetNode, 160, 50);
    const targetDims = getNodeDimensions(targetNode, 160, 50);
    const sourceCenters = sourceNodes.map((node) => getNodeCenter(node, 160, 50));
    const minX = Math.min(...sourceCenters.map((point) => point.x));
    const maxX = Math.max(...sourceCenters.map((point) => point.x));
    const avgX = sourceCenters.reduce((sum, point) => sum + point.x, 0) / sourceCenters.length;
    const avgY = sourceCenters.reduce((sum, point) => sum + point.y, 0) / sourceCenters.length;
    const sourcesAreBelowTarget = avgY > targetCenter.y;
    const junctionX = Math.min(Math.max(avgX, minX), maxX);
    const junctionY = sourcesAreBelowTarget
      ? targetNode.position.y + targetDims.height + 24
      : targetNode.position.y - 24;

    const junctionId = `${MERGE_NODE_PREFIX}${targetId}`;
    if (!nodeById.has(junctionId)) {
      const junctionNode: Node = {
        id: junctionId,
        position: { x: junctionX, y: junctionY },
        data: { isVirtual: true },
        selectable: false,
        draggable: false,
        focusable: false,
        sourcePosition: Position.Top,
        targetPosition: Position.Bottom,
        style: {
          width: 1,
          height: 1,
          opacity: 0,
          pointerEvents: 'none',
        },
      };
      nodeById.set(junctionId, junctionNode);
      extraNodes.push(junctionNode);
    }

    incomingEdges.forEach((edge) => {
      edges.push({
        id: `e-${edgeIndex++}`,
        source: edge.source,
        target: junctionId,
        type: 'step',
        animated: false,
        style: { stroke: '#111827', strokeWidth: 1.8 },
      });
    });

    edges.push({
      id: `e-${edgeIndex++}`,
      source: junctionId,
      target: targetId,
      type: 'step',
      animated: false,
      style: { stroke: '#111827', strokeWidth: 2 },
      markerEnd: { type: MarkerType.ArrowClosed, width: 12, height: 12, color: '#111827' },
    });
  });

  return { nodes: [...baseNodes, ...extraNodes], edges };
}

function buildClickableNodeIds(
  graphData: KnowledgeGraph,
  viewMode: ViewMode,
  rootNodeId: string | null,
): Set<string> {
  if (viewMode === 'full') {
    return new Set(graphData.nodes.map((node) => node.id));
  }

  if (viewMode === 'subtopic') {
    // Only card nodes are clickable; layer headers are not.
    return new Set(
      graphData.nodes
        .filter((node) => node.style_class !== 'layerHeader')
        .map((node) => node.id),
    );
  }

  const nodesWithPrerequisites = new Set(graphData.edges.map((edge) => edge.target));
  return new Set(
    graphData.nodes
      .filter((node) => nodesWithPrerequisites.has(node.id) && node.id !== rootNodeId)
      .map((node) => node.id),
  );
}

function getLayoutedElements(
  graphData: KnowledgeGraph,
  selectedId?: string | null,
  clickableNodeIds?: Set<string>,
  mode: ViewMode = 'full',
  manualPositions?: ManualNodePositions,
) {
  if (mode === 'subtopic') {
    const orderedNodes = [...graphData.nodes].sort((a, b) => {
      if (a.layer !== b.layer) return a.layer - b.layer;
      if (a.style_class === 'layerHeader' && b.style_class !== 'layerHeader') return -1;
      if (a.style_class !== 'layerHeader' && b.style_class === 'layerHeader') return 1;
      return a.label.localeCompare(b.label);
    });

    let currentY = 60;
    let previousLayer: number | null = null;
    const nodes: Node[] = orderedNodes.map((node) => {
      if (previousLayer !== null && previousLayer !== node.layer && node.style_class === 'layerHeader') {
        currentY += 24;
      }

      const isHeader = node.style_class === 'layerHeader';
      const autoPosition = { x: isHeader ? 110 : 170, y: currentY };
      const position = manualPositions?.[node.id] ?? autoPosition;
      const height = isHeader ? 42 : 76;
      currentY += isHeader ? 60 : 92;
      previousLayer = node.layer;

      return {
        id: node.id,
        position,
        data: { label: node.label, node },
        style: {
          background: isHeader
            ? '#e0e7ff'
            : node.id === selectedId ? '#eef2ff' : '#f8fafc',
          border: isHeader
            ? '2px solid #6366f1'
            : `${node.id === selectedId ? '3' : '2'}px solid ${node.id === selectedId ? '#6366f1' : '#cbd5e1'}`,
          borderRadius: '8px',
          padding: isHeader ? '10px 12px' : '10px 12px',
          fontSize: isHeader ? '12px' : '11px',
          fontWeight: isHeader ? 700 : node.id === selectedId ? 700 : 500,
          width: isHeader ? 360 : 340,
          height,
          textAlign: 'center' as const,
          lineHeight: isHeader ? 1.2 : 1.35,
          color: isHeader ? '#312e81' : '#1f2937',
          cursor: clickableNodeIds && !clickableNodeIds.has(node.id) ? 'default' : 'pointer',
          pointerEvents: 'auto',
          transition: 'box-shadow 0.15s, border-color 0.15s',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        },
      };
    });
    return buildRoutedEdges(graphData.edges, nodes, mode);
  }

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
    const autoPosition = { x: pos.x - 80, y: pos.y - 25 };
    const position = manualPositions?.[node.id] ?? autoPosition;
    const masteryBorder = node.mastery !== null
      ? node.mastery >= 0.8 ? '#22c55e'
        : node.mastery >= 0.3 ? '#eab308'
        : '#d1d5db'
      : '#d1d5db';

    return {
      id: node.id,
      position,
      data: { label: node.label, node },
      style: {
        background: node.id === selectedId ? '#eef2ff' : node.fill_color,
        border: `${node.id === selectedId ? '3' : node.card_count > 0 ? '3' : '2'}px solid ${node.id === selectedId ? '#6366f1' : masteryBorder}`,
        borderRadius: '8px',
        padding: '8px 12px',
        fontSize: '11px',
        fontWeight: node.id === selectedId ? 700 : 500,
        width: 160,
        textAlign: 'center' as const,
        color: '#1f2937',
        cursor: clickableNodeIds && !clickableNodeIds.has(node.id) ? 'default' : 'pointer',
        pointerEvents: 'auto',
        transition: 'box-shadow 0.15s, border-color 0.15s',
      },
    };
  });

  return buildRoutedEdges(graphData.edges, nodes, mode);
}

/** Build card-level graph nodes from card list (no edges). */
function buildCardGraphData(cards: Card[]): KnowledgeGraph {
  const groupedByLayer = new Map<string, Card[]>();
  for (const card of cards) {
    const layer = extractLayerFromDeck(card.deck);
    const existing = groupedByLayer.get(layer) ?? [];
    existing.push(card);
    groupedByLayer.set(layer, existing);
  }

  const sortedLayers = [...groupedByLayer.keys()].sort((a, b) => {
    const order = parseLayerOrder(a) - parseLayerOrder(b);
    if (order !== 0) return order;
    return a.localeCompare(b);
  });

  const nodes: GN[] = [];
  const edges: KnowledgeGraph['edges'] = [];
  sortedLayers.forEach((layerName) => {
    const layerCards = groupedByLayer.get(layerName) ?? [];
    const layerOrder = parseLayerOrder(layerName);
    const layerId = `layer-${layerOrder}-${slugify(layerName)}`;
    nodes.push({
      id: layerId,
      label: formatLayerLabel(layerName),
      layer: layerOrder,
      layer_name: layerName,
      style_class: 'layerHeader',
      fill_color: '#e0e7ff',
      stroke_color: '#6366f1',
      mastery: null,
      card_count: layerCards.length,
    });

    layerCards.forEach((card) => {
      nodes.push({
        id: card.card_id,
        label: extractQuestionLabel(card),
        layer: layerOrder,
        layer_name: layerName,
        style_class: 'card',
        fill_color: '#f8fafc',
        stroke_color: '#cbd5e1',
        mastery: null,
        card_count: 1,
      });
      edges.push({
        source: card.card_id,
        target: layerId,
        type: 'supports',
      });
    });
  });

  return { nodes, edges, layers: {} };
}

/* ---------- Breadcrumb ---------- */

type BreadcrumbProps = {
  navigationStack: NavItem[];
  onFullGraph: () => void;
  onNavigate: (index: number) => void;
};

function Breadcrumb({ navigationStack, onFullGraph, onNavigate }: BreadcrumbProps) {
  return (
    <div className="flex items-center gap-2 px-4 py-2 text-sm border-b border-gray-200 bg-white">
      <button
        onClick={onFullGraph}
        className="text-indigo-600 hover:underline"
      >
        Full Graph
      </button>
      {navigationStack.map((item, idx) => (
        <span key={`${item.id}-${idx}`} className="flex items-center gap-2">
          <span className="text-gray-400">&rsaquo;</span>
          <button
            onClick={() => onNavigate(idx)}
            className={idx === navigationStack.length - 1
              ? 'font-semibold text-gray-900'
              : 'text-indigo-600 hover:underline'}
          >
            {item.name}
          </button>
        </span>
      ))}
    </div>
  );
}

/* ---------- Card Distribution (concept-level right panel section) ---------- */

type CardDistributionProps = {
  distribution: SubtreeCardDistribution | null;
  loading: boolean;
  error: string | null;
  onDrill: (conceptId: string) => void;
};

function CardDistribution({ distribution, loading, error, onDrill }: CardDistributionProps) {
  if (loading) {
    return <div className="mt-4 text-xs text-gray-400">Loading card distribution...</div>;
  }
  if (error) {
    return <div className="mt-4 text-xs text-red-600">Could not load distribution: {error}</div>;
  }
  if (!distribution) return null;

  return (
    <div className="mt-4 border-t border-gray-200 pt-4">
      <h4 className="text-sm font-semibold mb-2">Card Distribution</h4>
      <div className="space-y-1">
        {distribution.breakdown.map((item) => (
          <div key={item.concept} className="flex items-center justify-between py-1">
            <span className="text-sm text-gray-700">
              {item.concept} {item.is_prerequisite ? '(prerequisite)' : ''}
            </span>
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-gray-600">
                {item.count} {item.count === 1 ? 'card' : 'cards'}
              </span>
              <button
                onClick={() => onDrill(item.concept)}
                className="text-xs text-indigo-600 hover:underline"
                disabled={item.count === 0}
              >
                &rarr; Drill
              </button>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-2 border-t border-gray-200 pt-2 text-sm font-semibold text-gray-800">
        Total: {distribution.total} {distribution.total === 1 ? 'card' : 'cards'}
      </div>
    </div>
  );
}

/* ---------- Main page ---------- */

export default function KnowledgeGraphPage() {
  const navigate = useNavigate();
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [selected, setSelected] = useState<GN | null>(null);
  const [initialLoading, setInitialLoading] = useState(true);
  const [subtreeLoading, setSubtreeLoading] = useState(false);

  // View & graph data
  const [viewMode, setViewMode] = useState<ViewMode>('full');
  const [fullGraphData, setFullGraphData] = useState<KnowledgeGraph | null>(null);
  const [currentGraphData, setCurrentGraphData] = useState<KnowledgeGraph | null>(null);
  const [layoutMode, setLayoutMode] = useState<LayoutMode>('auto');
  const [manualLayouts, setManualLayouts] = useState<Record<string, ManualNodePositions>>(() => {
    try {
      const raw = localStorage.getItem(MANUAL_LAYOUT_STORAGE_KEY);
      if (!raw) return {};
      const parsed = JSON.parse(raw) as Record<string, ManualNodePositions>;
      return parsed && typeof parsed === 'object' ? parsed : {};
    } catch {
      return {};
    }
  });

  // 3-level navigation stack: concept → subtopic → card
  const [navigationStack, setNavigationStack] = useState<NavItem[]>([]);

  // Concept-level: card distribution
  const [distribution, setDistribution] = useState<SubtreeCardDistribution | null>(null);
  const [distributionError, setDistributionError] = useState<{ nodeId: string; message: string } | null>(null);

  // Concept-level: subtopics list for right panel
  const [subtopics, setSubtopics] = useState<Subtopic[]>([]);
  const [subtopicsNodeId, setSubtopicsNodeId] = useState<string | null>(null);

  // Card-level: selected card detail for right panel
  const [selectedCard, setSelectedCard] = useState<Card | null>(null);
  const [subtopicCards, setSubtopicCards] = useState<Card[]>([]);

  const getEffectiveGraphMode = useCallback((mode: ViewMode): ViewMode => (
    mode === 'card' ? 'subtopic' : mode
  ), []);

  const getScopeKey = useCallback((mode: ViewMode, stack: NavItem[]) => {
    const effectiveMode = getEffectiveGraphMode(mode);
    if (effectiveMode === 'full') return 'full';

    const conceptPath = stack
      .filter((item) => item.type === 'concept')
      .map((item) => item.id)
      .join('>');

    if (effectiveMode === 'prerequisiteTree') {
      return `tree:${conceptPath || 'root'}`;
    }

    const subtopicId = stack.find((item) => item.type === 'subtopic')?.id;
    return `subtopic:${subtopicId || conceptPath || 'root'}`;
  }, [getEffectiveGraphMode]);

  useEffect(() => {
    try {
      localStorage.setItem(MANUAL_LAYOUT_STORAGE_KEY, JSON.stringify(manualLayouts));
    } catch {
      // Ignore persistence errors.
    }
  }, [manualLayouts]);

  /* ---------- renderGraph ---------- */

  const renderGraph = useCallback((
    graphData: KnowledgeGraph,
    selectedId: string | null,
    mode: ViewMode,
    rootNodeId: string | null,
    scopeKey?: string,
  ) => {
    const clickableNodeIds = buildClickableNodeIds(graphData, mode, rootNodeId);
    const manualPositions = layoutMode === 'arrange' && scopeKey
      ? manualLayouts[scopeKey]
      : undefined;
    const { nodes: n, edges: e } = getLayoutedElements(
      graphData,
      selectedId,
      clickableNodeIds,
      mode,
      manualPositions,
    );
    setNodes(n);
    setEdges(e);
  }, [layoutMode, manualLayouts, setEdges, setNodes]);

  /* ---------- Initial load ---------- */

  useEffect(() => {
    fetchGraph().then((data) => {
      setFullGraphData(data);
      setCurrentGraphData(data);
      renderGraph(data, null, 'full', null, 'full');
      setInitialLoading(false);
    }).catch(() => setInitialLoading(false));
  }, [renderGraph]);

  const hasPrerequisites = useCallback((graphData: KnowledgeGraph | null, nodeId: string) => {
    if (!graphData) return false;
    return graphData.edges.some((edge) => edge.target === nodeId);
  }, []);

  /* ---------- Navigation helpers ---------- */

  const navigateToSubtree = useCallback((nodeId: string, stack: NavItem[], fallbackNode?: GN | null) => {
    setSubtreeLoading(true);
    setSelectedCard(null);
    setSubtopicCards([]);
    fetchSubtree(nodeId).then((subtree) => {
      setCurrentGraphData(subtree);
      setNavigationStack(stack);
      setViewMode('prerequisiteTree');
      const targetGn = subtree.nodes.find((n) => n.id === nodeId) ?? fallbackNode ?? null;
      setSelected(targetGn);
      renderGraph(subtree, nodeId, 'prerequisiteTree', nodeId, getScopeKey('prerequisiteTree', stack));
    }).finally(() => setSubtreeLoading(false));
  }, [getScopeKey, renderGraph]);

  const navigateToSubtopic = useCallback((conceptId: string, subtopic: Subtopic) => {
    if (import.meta.env.DEV) {
      console.debug('[KnowledgeGraph] navigateToSubtopic', { conceptId, subtopicId: subtopic.id });
    }
    setSubtreeLoading(true);
    setSelected(null);
    setSelectedCard(null);
    const conceptStack = navigationStack.filter((item) => item.type === 'concept');
    const newNav: NavItem = { id: `${conceptId}.${subtopic.id}`, type: 'subtopic', name: subtopic.name };
    const newStack = [...conceptStack, newNav];
    setNavigationStack(newStack);
    setViewMode('subtopic');
    const emptyGraph = buildCardGraphData([]);
    setCurrentGraphData(emptyGraph);
    const subtopicScopeKey = getScopeKey('subtopic', newStack);
    renderGraph(emptyGraph, null, 'subtopic', null, subtopicScopeKey);
    fetchSubtopicCards(conceptId, subtopic.id).then((cards) => {
      if (import.meta.env.DEV) {
        console.debug('[KnowledgeGraph] fetched subtopic cards', { subtopicId: subtopic.id, count: cards.length });
      }
      setSubtopicCards(cards);
      const cardGraph = buildCardGraphData(cards);
      setCurrentGraphData(cardGraph);
      renderGraph(cardGraph, null, 'subtopic', null, subtopicScopeKey);
    }).catch((err) => {
      if (import.meta.env.DEV) {
        console.error('[KnowledgeGraph] failed to load subtopic cards', err);
      }
      setSubtopicCards([]);
    }).finally(() => setSubtreeLoading(false));
  }, [getScopeKey, navigationStack, renderGraph]);

  const startDrill = useCallback((level: 'concept' | 'subtopic' | 'card', id: string) => {
    const params = new URLSearchParams();
    if (level === 'concept') {
      params.set('concept', id);
    } else if (level === 'subtopic') {
      const [conceptId, ...rest] = id.split('.');
      const subtopicId = rest.join('.');
      if (conceptId) params.set('concept', conceptId);
      if (subtopicId) params.set('subtopic', subtopicId);
    } else {
      params.set('card', id);
    }
    navigate(`/drill?${params.toString()}`);
  }, [navigate]);

  /* ---------- Node click handling ---------- */

  const handleNodeClick = useCallback((_event: MouseEvent, node: Node) => {
    const gn = (node.data as { node?: GN } | undefined)?.node;
    if (!gn) return;
    if (gn.style_class === 'layerHeader') {
      return;
    }

    if (viewMode === 'full') {
      // Click in full graph → navigate to prerequisite tree
      const navItem: NavItem = { id: gn.id, type: 'concept', name: gn.label };
      navigateToSubtree(gn.id, [navItem], gn);
      return;
    }

    if (viewMode === 'prerequisiteTree') {
      setSelected(gn);
      const currentRoot = navigationStack[navigationStack.length - 1]?.id ?? null;
      const shouldNavigate = hasPrerequisites(currentGraphData, gn.id) && gn.id !== currentRoot;
      if (shouldNavigate) {
        const navItem: NavItem = { id: gn.id, type: 'concept', name: gn.label };
        navigateToSubtree(gn.id, [...navigationStack, navItem], gn);
        return;
      }
      if (currentGraphData) {
        renderGraph(
          currentGraphData,
          gn.id,
          'prerequisiteTree',
          currentRoot,
          getScopeKey('prerequisiteTree', navigationStack),
        );
      }
      return;
    }

    if (viewMode === 'subtopic') {
      // Click a card node → show card detail in right panel
      const card = subtopicCards.find((c) => c.card_id === gn.id) ?? null;
      setSelectedCard(card);
      setSelected(gn);
      if (currentGraphData) {
        renderGraph(currentGraphData, gn.id, 'subtopic', null, getScopeKey('subtopic', navigationStack));
      }

      // Also add card to breadcrumb
      const cardNav: NavItem = { id: gn.id, type: 'card', name: gn.id };
      // Replace any existing card-level nav (keep concept + subtopic only)
      const baseStack = navigationStack.filter((n) => n.type !== 'card');
      setNavigationStack([...baseStack, cardNav]);
      setViewMode('card');
      return;
    }

    if (viewMode === 'card') {
      // Clicking another card at card level
      const card = subtopicCards.find((c) => c.card_id === gn.id) ?? null;
      setSelectedCard(card);
      setSelected(gn);
      if (currentGraphData) {
        renderGraph(currentGraphData, gn.id, 'subtopic', null, getScopeKey('subtopic', navigationStack));
      }
      const baseStack = navigationStack.filter((n) => n.type !== 'card');
      const cardNav: NavItem = { id: gn.id, type: 'card', name: gn.id };
      setNavigationStack([...baseStack, cardNav]);
    }
  }, [
    currentGraphData,
    hasPrerequisites,
    navigationStack,
    getScopeKey,
    navigateToSubtree,
    renderGraph,
    subtopicCards,
    viewMode,
  ]);

  const handleNodeDragStop = useCallback((_event: MouseEvent, node: Node) => {
    const effectiveMode = getEffectiveGraphMode(viewMode);
    if (layoutMode !== 'arrange' || effectiveMode === 'full') return;
    if (node.id.startsWith(MERGE_NODE_PREFIX)) return;

    const scopeKey = getScopeKey(effectiveMode, navigationStack);
    setManualLayouts((prev) => ({
      ...prev,
      [scopeKey]: {
        ...(prev[scopeKey] ?? {}),
        [node.id]: { x: node.position.x, y: node.position.y },
      },
    }));
  }, [getEffectiveGraphMode, getScopeKey, layoutMode, navigationStack, viewMode]);

  const resetCurrentLayout = useCallback(() => {
    const effectiveMode = getEffectiveGraphMode(viewMode);
    if (effectiveMode === 'full') return;
    const scopeKey = getScopeKey(effectiveMode, navigationStack);
    setManualLayouts((prev) => {
      if (!prev[scopeKey]) return prev;
      const next = { ...prev };
      delete next[scopeKey];
      return next;
    });
    setLayoutMode('auto');
  }, [getEffectiveGraphMode, getScopeKey, navigationStack, viewMode]);

  /* ---------- Breadcrumb navigation ---------- */

  function navigateToBreadcrumb(index: number) {
    if (index < 0) {
      // "Full Graph" clicked
      if (!fullGraphData) return;
      setViewMode('full');
      setNavigationStack([]);
      setSelected(null);
      setSelectedCard(null);
      setSubtopicCards([]);
      setSubtopics([]);
      setCurrentGraphData(fullGraphData);
      renderGraph(fullGraphData, null, 'full', null, 'full');
      return;
    }

    const targetItem = navigationStack[index];
    if (!targetItem) return;

    if (targetItem.type === 'concept') {
      const trimmedStack = navigationStack.slice(0, index + 1);
      setSelectedCard(null);
      setSubtopicCards([]);
      navigateToSubtree(targetItem.id, trimmedStack);
    } else if (targetItem.type === 'subtopic') {
      // Re-navigate to subtopic level
      const conceptNav = navigationStack.find((n) => n.type === 'concept');
      if (!conceptNav) return;
      const conceptId = conceptNav.id;
      const subtopicId = targetItem.id.split('.')[1];
      const trimmedStack = navigationStack.slice(0, index);
      setSelectedCard(null);
      setSubtreeLoading(true);
      fetchSubtopicCards(conceptId, subtopicId).then((cards) => {
        setSubtopicCards(cards);
        const cardGraph = buildCardGraphData(cards);
        const nextStack = [...trimmedStack, targetItem];
        setCurrentGraphData(cardGraph);
        setNavigationStack(nextStack);
        setViewMode('subtopic');
        setSelected(null);
        renderGraph(cardGraph, null, 'subtopic', null, getScopeKey('subtopic', nextStack));
      }).finally(() => setSubtreeLoading(false));
    }
    // card-level breadcrumb click: already at that card, no-op
  }

  /* ---------- Fetch subtopics when a concept is selected in prereq tree ---------- */

  useEffect(() => {
    const nodeId = selected?.id;
    if (viewMode !== 'prerequisiteTree' || !nodeId) return;
    let cancelled = false;
    fetchNodeSubtopics(nodeId)
      .then((items) => {
        if (cancelled) return;
        setSubtopics(items);
        setSubtopicsNodeId(nodeId);
      })
      .catch(() => {
        if (cancelled) return;
        setSubtopics([]);
        setSubtopicsNodeId(nodeId);
      });
    return () => {
      cancelled = true;
    };
  }, [selected?.id, viewMode]);

  /* ---------- Re-render graph on layout mode / saved position changes ---------- */

  useEffect(() => {
    if (!currentGraphData) return;
    const effectiveMode = getEffectiveGraphMode(viewMode);
    const selectedId = selected?.id ?? selectedCard?.card_id ?? null;
    const rootNodeId = effectiveMode === 'prerequisiteTree'
      ? navigationStack[navigationStack.length - 1]?.id ?? null
      : null;
    const scopeKey = getScopeKey(effectiveMode, navigationStack);
    renderGraph(currentGraphData, selectedId, effectiveMode, rootNodeId, scopeKey);
  }, [
    currentGraphData,
    getEffectiveGraphMode,
    getScopeKey,
    layoutMode,
    manualLayouts,
    navigationStack,
    renderGraph,
    selected?.id,
    selectedCard?.card_id,
    viewMode,
  ]);

  /* ---------- Fetch card distribution (existing) ---------- */

  useEffect(() => {
    const selectedNodeId = selected?.id;
    if (viewMode !== 'prerequisiteTree' || !selectedNodeId) return;

    let cancelled = false;
    fetchSubtreeCardDistribution(selectedNodeId)
      .then((data) => {
        if (cancelled) return;
        setDistribution(data);
        setDistributionError(null);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setDistribution(null);
        setDistributionError({
          nodeId: selectedNodeId,
          message: err instanceof Error ? err.message : 'Unknown error',
        });
      });

    return () => {
      cancelled = true;
    };
  }, [selected?.id, viewMode]);

  /* ---------- Render ---------- */

  if (initialLoading) return <div className="text-gray-500 p-4">Loading knowledge graph...</div>;

  const selectedNodeId = selected?.id ?? null;
  const distributionLoading = viewMode === 'prerequisiteTree'
    && !!selectedNodeId
    && distribution?.node_id !== selectedNodeId
    && distributionError?.nodeId !== selectedNodeId;
  const distributionErrorMessage = (selectedNodeId && distributionError?.nodeId === selectedNodeId)
    ? distributionError.message
    : null;

  const subtopicNav = navigationStack.find((n) => n.type === 'subtopic');
  const showRightPanel = viewMode === 'subtopic' || viewMode === 'card' || (viewMode === 'prerequisiteTree' && !!selected);
  const subtopicsLoading = viewMode === 'prerequisiteTree' && !!selected && subtopicsNodeId !== selected.id;
  const effectiveViewMode = getEffectiveGraphMode(viewMode);
  const canArrangeLayout = effectiveViewMode !== 'full';
  const currentScopeKey = getScopeKey(effectiveViewMode, navigationStack);
  const hasSavedLayout = !!manualLayouts[currentScopeKey] && Object.keys(manualLayouts[currentScopeKey]).length > 0;

  return (
    <div className="h-[calc(100vh-48px)] flex">
      <div className="flex-1 flex flex-col min-w-0">
        {viewMode !== 'full' && (
          <Breadcrumb
            navigationStack={navigationStack}
            onFullGraph={() => navigateToBreadcrumb(-1)}
            onNavigate={navigateToBreadcrumb}
          />
        )}
        <div className="flex-1 relative">
          {canArrangeLayout && (
            <div className="absolute left-3 top-3 z-10 flex items-center gap-1 rounded-md border border-gray-200 bg-white/95 p-1 text-xs shadow-sm">
              <button
                onClick={() => setLayoutMode('auto')}
                className={layoutMode === 'auto'
                  ? 'rounded px-2 py-1 font-medium bg-indigo-100 text-indigo-700'
                  : 'rounded px-2 py-1 text-gray-600 hover:bg-gray-100'}
              >
                Auto
              </button>
              <button
                onClick={() => setLayoutMode('arrange')}
                className={layoutMode === 'arrange'
                  ? 'rounded px-2 py-1 font-medium bg-indigo-100 text-indigo-700'
                  : 'rounded px-2 py-1 text-gray-600 hover:bg-gray-100'}
              >
                Arrange
              </button>
              <button
                onClick={resetCurrentLayout}
                disabled={!hasSavedLayout}
                className="rounded px-2 py-1 text-gray-600 hover:bg-gray-100 disabled:text-gray-300 disabled:hover:bg-transparent"
              >
                Reset
              </button>
            </div>
          )}
          {subtreeLoading && (
            <div className="absolute right-3 top-3 z-10 rounded-md border border-gray-200 bg-white/95 px-2 py-1 text-xs text-gray-500 shadow-sm">
              Updating tree...
            </div>
          )}
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={handleNodeClick}
            onNodeDragStop={handleNodeDragStop}
            nodesDraggable={canArrangeLayout && layoutMode === 'arrange'}
            elementsSelectable={canArrangeLayout && layoutMode === 'arrange'}
            nodesConnectable={false}
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
      </div>

      {/* ---------- Right Panel ---------- */}
      {showRightPanel && (
        <div className="w-80 bg-white border-l p-4 overflow-y-auto">

          {/* Concept-level right panel (prerequisite tree view) */}
          {viewMode === 'prerequisiteTree' && selected && (
            <>
              <h3 className="font-bold text-lg">{selected.id}: {selected.card_count} {selected.card_count === 1 ? 'card' : 'cards'}</h3>
              <p className="text-sm text-gray-500 mb-2">{selected.label}</p>
              <div className="space-y-2 text-sm">
                <div><span className="text-gray-500">Layer:</span> {selected.layer_name}</div>
                <div><span className="text-gray-500">Level:</span> {selected.layer}</div>
                <div>
                  <span className="text-gray-500">Mastery:</span>{' '}
                  {selected.mastery !== null ? `${Math.round(selected.mastery * 100)}%` : 'No data'}
                </div>
                <div>
                  <span className="text-gray-500">Cards:</span>{' '}
                  {selected.card_count > 0 ? (
                    <span className="inline-block px-1.5 py-0.5 bg-indigo-100 text-indigo-700 rounded text-xs font-medium">
                      {selected.card_count} cards
                    </span>
                  ) : (
                    <span className="text-gray-400">None</span>
                  )}
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

              {/* Subtopics section */}
              {selected.card_count > 0 && (
                <div className="mt-4 border-t border-gray-200 pt-4">
                  <h4 className="text-sm font-semibold mb-2">Subtopics</h4>
                  {subtopicsLoading ? (
                    <div className="text-xs text-gray-400">Loading subtopics...</div>
                  ) : subtopics.length > 0 ? (
                    <div className="space-y-1">
                      {subtopics.map((st) => (
                        <div
                          key={st.id}
                          onClick={() => navigateToSubtopic(selected.id, st)}
                          className="flex justify-between items-center py-2 px-3 hover:bg-gray-100 rounded cursor-pointer"
                        >
                          <span className="text-sm">{st.name}</span>
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-gray-600">{st.card_count} cards</span>
                            <button
                              onClick={(event) => {
                                event.stopPropagation();
                                navigateToSubtopic(selected.id, st);
                              }}
                              className="text-xs text-indigo-600 hover:underline"
                            >
                              &rarr; View
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-xs text-gray-400">No subtopics</div>
                  )}
                </div>
              )}

              {selected.card_count > 0 && (
                <button
                  onClick={() => startDrill('concept', selected.id)}
                  className="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium"
                >
                  <Play size={14} />
                  Start Drill ({selected.card_count} cards)
                </button>
              )}

              {selected.card_count === 0 && (
                <div className="mt-4 text-xs text-gray-400 text-center py-2 border border-dashed border-gray-200 rounded-lg">
                  No drill cards yet
                </div>
              )}

              <CardDistribution
                distribution={distribution}
                loading={distributionLoading}
                error={distributionErrorMessage}
                onDrill={(conceptId) => startDrill('concept', conceptId)}
              />
            </>
          )}

          {/* Subtopic-level right panel (card grid view, no card selected yet) */}
          {viewMode === 'subtopic' && !selectedCard && (
            <>
              <h3 className="font-bold text-lg">
                {subtopicNav?.name ?? 'Subtopic'}
              </h3>
              <p className="text-sm text-gray-500 mb-4">
                {subtopicCards.length} {subtopicCards.length === 1 ? 'card' : 'cards'} &mdash; click a node to see details
              </p>
              <div className="space-y-2">
                {subtopicCards.map((card) => (
                  <div
                    key={card.card_id}
                    className="py-2 px-3 rounded border border-gray-200 hover:bg-gray-50 cursor-pointer text-sm"
                    onClick={() => {
                      const gn = currentGraphData?.nodes.find((n) => n.id === card.card_id);
                      if (gn) {
                        setSelectedCard(card);
                        setSelected(gn);
                        if (currentGraphData) {
                          renderGraph(
                            currentGraphData,
                            card.card_id,
                            'subtopic',
                            null,
                            getScopeKey('subtopic', navigationStack),
                          );
                        }
                        const baseStack = navigationStack.filter((n) => n.type !== 'card');
                        setNavigationStack([...baseStack, { id: card.card_id, type: 'card', name: card.card_id }]);
                        setViewMode('card');
                      }
                    }}
                  >
                    <div className="font-medium text-xs text-gray-500 mb-1">{card.card_id}</div>
                    <div className="text-sm text-gray-800 leading-snug">{extractQuestionLabel(card)}</div>
                  </div>
                ))}
              </div>
              {subtopicNav && (
                <button
                  onClick={() => startDrill('subtopic', subtopicNav.id)}
                  className="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium"
                >
                  <Play size={14} />
                  Drill All {subtopicNav.name} Cards ({subtopicCards.length})
                </button>
              )}
            </>
          )}

          {/* Card-level right panel (individual card detail) */}
          {(viewMode === 'card' || (viewMode === 'subtopic' && selectedCard)) && selectedCard && (
            <>
              <h3 className="font-bold text-lg">{selectedCard.card_id}</h3>
              <div className="space-y-3 mt-3">
                {selectedCard.knowledge_layer && (
                  <div className="text-sm">
                    <span className="text-gray-500">Layer:</span> {selectedCard.knowledge_layer}
                  </div>
                )}
                {selectedCard.cognitive_layer && (
                  <div className="text-sm">
                    <span className="text-gray-500">Cognitive:</span> {selectedCard.cognitive_layer}
                  </div>
                )}
                <div className="text-sm">
                  <span className="text-gray-500">Weight:</span> {selectedCard.fire_weight}
                </div>
                <div className="text-sm">
                  <span className="text-gray-500">Tags:</span>{' '}
                  <span className="text-xs text-gray-600">{selectedCard.tags.join(', ')}</span>
                </div>

                <div className="border-t border-gray-200 pt-3">
                  <h4 className="text-sm font-semibold mb-1">Prompt</h4>
                  <div
                    className="text-sm text-gray-700 bg-gray-50 rounded p-2 max-h-40 overflow-y-auto"
                    dangerouslySetInnerHTML={{ __html: selectedCard.prompt }}
                  />
                </div>

                <div className="border-t border-gray-200 pt-3">
                  <h4 className="text-sm font-semibold mb-1">Solution</h4>
                  <div
                    className="text-sm text-gray-700 bg-gray-50 rounded p-2 max-h-40 overflow-y-auto"
                    dangerouslySetInnerHTML={{ __html: selectedCard.solution }}
                  />
                </div>
              </div>

              {selectedCard && (
                <button
                  onClick={() => startDrill('card', selectedCard.card_id)}
                  className="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium"
                >
                  <Play size={14} />
                  Drill This Card
                </button>
              )}
            </>
          )}

          <button
            onClick={() => {
              if (fullGraphData) {
                setNavigationStack([]);
                setViewMode('full');
                setCurrentGraphData(fullGraphData);
                renderGraph(fullGraphData, null, 'full', null, 'full');
              }
              setSelected(null);
              setSelectedCard(null);
            }}
            className="mt-4 text-xs text-gray-400 hover:text-gray-600"
          >
            Close
          </button>
        </div>
      )}
    </div>
  );
}
