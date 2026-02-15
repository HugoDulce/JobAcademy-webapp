export interface Card {
  card_id: string;
  deck: string;
  tags: string[];
  fire_weight: number;
  notion_last_edited: string;
  prompt: string;
  solution: string;
  pillar: string | null;
  knowledge_layer: string | null;
  cognitive_layer: string | null;
  filename: string | null;
  topic: string | null;
  concept: string | null;
  has_visual: boolean;
  concept_node: string | null;
  subtopic: string | null;
}

export interface CardCreate {
  card_id: string;
  deck: string;
  tags: string[];
  fire_weight: number;
  prompt: string;
  solution: string;
}

export interface CardUpdate {
  deck?: string;
  tags?: string[];
  fire_weight?: number;
  prompt?: string;
  solution?: string;
}

export interface ValidationResult {
  card_id: string;
  is_valid: boolean;
  errors: string[];
  warnings: string[];
  checks: Record<string, boolean>;
}
