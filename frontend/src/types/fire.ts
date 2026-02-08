export interface EncompassingRelationship {
  parent_card_id: string;
  child_card_id: string;
  weight: number;
}

export interface FIReData {
  relationships: EncompassingRelationship[];
  standalone_cards: string[];
}

export interface CreditSimulationResult {
  card_id: string;
  passed: boolean;
  credits: { card_id: string; credit: number }[];
}
