import type { FIReData, CreditSimulationResult } from '../types/fire';
import { apiFetch } from './client';

export function fetchFIReData(): Promise<FIReData> {
  return apiFetch<FIReData>('/api/fire/relationships');
}

export function simulateCredit(cardId: string, passed: boolean): Promise<CreditSimulationResult> {
  return apiFetch<CreditSimulationResult>('/api/fire/simulate', {
    method: 'POST',
    body: JSON.stringify({ card_id: cardId, passed }),
  });
}
