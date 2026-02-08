import { apiFetch } from './client';

export interface DashboardStats {
  total_cards: number;
  due_today: number;
  mastery_pct: number;
  reviewed_today: number;
  cards_by_pillar: Record<string, number>;
  cards_by_layer: Record<string, number>;
}

export function fetchDashboardStats(): Promise<DashboardStats> {
  return apiFetch<DashboardStats>('/api/dashboard/stats');
}
