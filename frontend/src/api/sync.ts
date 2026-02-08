import type { SyncResult } from '../types/sync';
import { apiFetch } from './client';

export function syncNotionToObsidian(): Promise<SyncResult> {
  return apiFetch<SyncResult>('/api/sync/notion-to-obsidian', { method: 'POST' });
}

export function syncObsidianToAnki(): Promise<SyncResult> {
  return apiFetch<SyncResult>('/api/sync/obsidian-to-anki', { method: 'POST' });
}

export function syncFull(): Promise<SyncResult> {
  return apiFetch<SyncResult>('/api/sync/full', { method: 'POST' });
}

export function fetchSyncLog(lines?: number): Promise<{ log: string }> {
  const q = lines ? `?lines=${lines}` : '';
  return apiFetch<{ log: string }>(`/api/sync/log${q}`);
}
