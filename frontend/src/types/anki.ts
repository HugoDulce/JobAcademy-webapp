export interface DueCard {
  card_id: number;
  note_id: number;
  front: string;
  back: string;
  deck: string;
  interval: number;
  ease: number;
  tags: string[];
}

export interface AnkiStats {
  total_notes: number;
  due_today: number;
  reviewed_today: number;
  new_count: number;
  learning_count: number;
  mastered_count: number;
}
