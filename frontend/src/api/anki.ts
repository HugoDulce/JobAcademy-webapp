import type { DueCard, AnkiStats } from '../types/anki';
import { apiFetch } from './client';

export function fetchDueCards(): Promise<DueCard[]> {
  return apiFetch<DueCard[]>('/api/anki/due');
}

export function answerCard(cardId: number | string, ease: number): Promise<void> {
  return apiFetch<void>('/api/anki/answer', {
    method: 'POST',
    body: JSON.stringify({ card_id: cardId, ease }),
  });
}

export function updateNote(
  noteId: number | string,
  front: string,
  back: string,
  cardId?: string,
): Promise<void> {
  return apiFetch<void>('/api/anki/update-note', {
    method: 'PUT',
    body: JSON.stringify({ note_id: noteId, front, back, card_id: cardId }),
  });
}

export function fetchAnkiStats(): Promise<AnkiStats> {
  return apiFetch<AnkiStats>('/api/anki/stats');
}

export function checkAnkiStatus(): Promise<{ connected: boolean; version: number }> {
  return apiFetch('/api/anki/status');
}
