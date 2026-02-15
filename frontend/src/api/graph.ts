import type { Card } from '../types/card';
import type { KnowledgeGraph, Subtopic, SubtreeCardDistribution } from '../types/graph';
import { apiFetch } from './client';

export function fetchGraph(): Promise<KnowledgeGraph> {
  return apiFetch<KnowledgeGraph>('/api/graph');
}

export function fetchSubtree(nodeId: string): Promise<KnowledgeGraph> {
  return apiFetch<KnowledgeGraph>(`/api/graph/${nodeId}/subtree`);
}

export function fetchNodeCards(nodeId: string): Promise<Card[]> {
  return apiFetch<Card[]>(`/api/graph/${nodeId}/cards`);
}

export function fetchSubtreeCardDistribution(nodeId: string): Promise<SubtreeCardDistribution> {
  return apiFetch<SubtreeCardDistribution>(`/api/graph/nodes/${nodeId}/subtree-cards`);
}

export function fetchNodeSubtopics(nodeId: string): Promise<Subtopic[]> {
  return apiFetch<Subtopic[]>(`/api/graph/nodes/${nodeId}/subtopics`);
}

export function fetchSubtopicCards(nodeId: string, subtopic: string): Promise<Card[]> {
  return apiFetch<Card[]>(`/api/graph/nodes/${nodeId}/subtopics/${encodeURIComponent(subtopic)}/cards`);
}
