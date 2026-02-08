import type { KnowledgeGraph } from '../types/graph';
import { apiFetch } from './client';

export function fetchGraph(): Promise<KnowledgeGraph> {
  return apiFetch<KnowledgeGraph>('/api/graph');
}
