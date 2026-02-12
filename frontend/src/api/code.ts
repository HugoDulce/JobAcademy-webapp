import { apiFetch } from './client';

export interface CodeExecuteResponse {
  stdout: string;
  stderr: string;
  exit_code: number;
  timed_out: boolean;
  error: string | null;
}

export function executeCode(code: string): Promise<CodeExecuteResponse> {
  return apiFetch<CodeExecuteResponse>('/api/code/execute', {
    method: 'POST',
    body: JSON.stringify({ code }),
  });
}
