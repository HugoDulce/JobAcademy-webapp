export interface SyncResult {
  success: boolean;
  stdout: string;
  stderr: string;
  duration_ms?: number;
}

export interface SyncStatus {
  running: boolean;
  last_sync: string | null;
  last_result: SyncResult | null;
}
