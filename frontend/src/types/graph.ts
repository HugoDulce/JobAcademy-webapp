export interface GraphNode {
  id: string;
  label: string;
  layer: number;
  layer_name: string;
  style_class: string;
  fill_color: string;
  stroke_color: string;
  mastery: number | null;
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
