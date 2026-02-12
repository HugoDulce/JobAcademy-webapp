import type { Card, CardCreate, CardUpdate, ValidationResult } from '../types/card';
import { apiFetch } from './client';

export function fetchCards(params?: { pillar?: string; layer?: string; topic?: string; search?: string }): Promise<Card[]> {
  const qs = new URLSearchParams();
  if (params?.pillar) qs.set('pillar', params.pillar);
  if (params?.layer) qs.set('layer', params.layer);
  if (params?.topic) qs.set('topic', params.topic);
  if (params?.search) qs.set('search', params.search);
  const q = qs.toString();
  return apiFetch<Card[]>(`/api/cards${q ? '?' + q : ''}`);
}

export function fetchCard(cardId: string): Promise<Card> {
  return apiFetch<Card>(`/api/cards/${cardId}`);
}

export function createCard(data: CardCreate): Promise<Card> {
  return apiFetch<Card>('/api/cards', { method: 'POST', body: JSON.stringify(data) });
}

export function updateCard(cardId: string, data: CardUpdate): Promise<Card> {
  return apiFetch<Card>(`/api/cards/${cardId}`, { method: 'PUT', body: JSON.stringify(data) });
}

export function deleteCard(cardId: string): Promise<void> {
  return apiFetch<void>(`/api/cards/${cardId}`, { method: 'DELETE' });
}

export function validateCard(cardId: string): Promise<ValidationResult> {
  return apiFetch<ValidationResult>(`/api/cards/${cardId}/validate`);
}
