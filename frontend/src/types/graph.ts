export interface GraphNode {
  id: string;
  label: string;
  layer: number;
  layer_name: string;
  style_class: string;
  fill_color: string;
  stroke_color: string;
  mastery: number | null;
  card_count: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
}

export interface KnowledgeGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
  layers: Record<number, string>;
}

export type GraphNodeType = 'concept' | 'subtopic' | 'card';

export interface NavItem {
  id: string;
  type: GraphNodeType;
  name: string;
}

export interface Subtopic {
  id: string;
  name: string;
  card_count: number;
}

export interface SubtreeCardBreakdownItem {
  concept: string;
  count: number;
  is_prerequisite: boolean;
}

export interface SubtreeCardDistribution {
  node_id: string;
  total: number;
  breakdown: SubtreeCardBreakdownItem[];
}
