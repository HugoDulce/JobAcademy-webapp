import { useState } from 'react';
import { RefreshCw, ArrowRight, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { syncNotionToObsidian, syncObsidianToAnki, syncFull, fetchSyncLog } from '../api/sync';
import type { SyncResult } from '../types/sync';

type StepStatus = 'idle' | 'running' | 'success' | 'error';

export default function SyncPanelPage() {
  const [step1Status, setStep1Status] = useState<StepStatus>('idle');
  const [step2Status, setStep2Status] = useState<StepStatus>('idle');
  const [result, setResult] = useState<SyncResult | null>(null);
  const [log, setLog] = useState('');
  const [fullRunning, setFullRunning] = useState(false);

  async function runStep1() {
    setStep1Status('running');
    setResult(null);
    try {
      const r = await syncNotionToObsidian();
      setResult(r);
      setStep1Status(r.success ? 'success' : 'error');
    } catch (e: unknown) {
      setResult({ success: false, stdout: '', stderr: e instanceof Error ? e.message : String(e), duration_ms: 0 });
      setStep1Status('error');
    }
  }

  async function runStep2() {
    setStep2Status('running');
    setResult(null);
    try {
      const r = await syncObsidianToAnki();
      setResult(r);
      setStep2Status(r.success ? 'success' : 'error');
    } catch (e: unknown) {
      setResult({ success: false, stdout: '', stderr: e instanceof Error ? e.message : String(e), duration_ms: 0 });
      setStep2Status('error');
    }
  }

  async function runFull() {
    setFullRunning(true);
    setStep1Status('running');
    setStep2Status('idle');
    setResult(null);
    try {
      const r = await syncFull();
      setResult(r);
      setStep1Status(r.success ? 'success' : 'error');
      setStep2Status(r.success ? 'success' : 'error');
    } catch (e: unknown) {
      setResult({ success: false, stdout: '', stderr: e instanceof Error ? e.message : String(e), duration_ms: 0 });
      setStep1Status('error');
    } finally {
      setFullRunning(false);
    }
  }

  async function loadLog() {
    try {
      const data = await fetchSyncLog(30);
      setLog(data.log);
    } catch { setLog('Failed to load log'); }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Sync Panel</h1>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <PipelineStep
          title="Notion -> Obsidian"
          description="Sync cards from Notion DB to .md files"
          status={step1Status}
          onRun={runStep1}
          disabled={fullRunning}
        />
        <div className="flex items-center justify-center">
          <ArrowRight className="text-gray-400" />
        </div>
        <PipelineStep
          title="Obsidian -> Anki"
          description="Push .md cards to Anki via AnkiConnect"
          status={step2Status}
          onRun={runStep2}
          disabled={fullRunning}
        />
      </div>

      <div className="flex gap-3 mb-6">
        <button onClick={runFull} disabled={fullRunning}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50">
          {fullRunning ? <Loader2 size={16} className="animate-spin" /> : <RefreshCw size={16} />}
          {fullRunning ? 'Running Full Pipeline...' : 'Run Full Pipeline'}
        </button>
        <button onClick={loadLog}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300">
          View Sync Log
        </button>
      </div>

      {result && (
        <div className={`mb-6 p-4 rounded-lg border ${result.success ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
          <h3 className={`font-medium mb-2 ${result.success ? 'text-green-700' : 'text-red-700'}`}>
            {result.success ? 'Sync Successful' : 'Sync Failed'}
            {result.duration_ms ? ` (${(result.duration_ms / 1000).toFixed(1)}s)` : ''}
          </h3>
          {result.stdout && (
            <pre className="text-xs bg-white p-3 rounded border overflow-x-auto whitespace-pre-wrap max-h-64 overflow-y-auto">
              {result.stdout}
            </pre>
          )}
          {result.stderr && (
            <pre className="text-xs bg-red-100 text-red-800 p-3 rounded border border-red-200 mt-2 overflow-x-auto whitespace-pre-wrap max-h-32 overflow-y-auto">
              {result.stderr}
            </pre>
          )}
        </div>
      )}

      {log && (
        <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-xs max-h-80 overflow-y-auto">
          <h3 className="text-gray-500 mb-2">sync.log (last 30 lines)</h3>
          <pre className="whitespace-pre-wrap">{log}</pre>
        </div>
      )}
    </div>
  );
}

function PipelineStep({ title, description, status, onRun, disabled }: {
  title: string; description: string; status: StepStatus; onRun: () => void; disabled: boolean;
}) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-medium text-sm">{title}</h3>
        <StatusIcon status={status} />
      </div>
      <p className="text-xs text-gray-500 mb-3">{description}</p>
      <button onClick={onRun} disabled={disabled || status === 'running'}
        className="w-full px-3 py-1.5 text-xs bg-gray-100 rounded hover:bg-gray-200 disabled:opacity-50">
        {status === 'running' ? 'Running...' : 'Run'}
      </button>
    </div>
  );
}

function StatusIcon({ status }: { status: StepStatus }) {
  switch (status) {
    case 'running': return <Loader2 size={16} className="animate-spin text-blue-500" />;
    case 'success': return <CheckCircle size={16} className="text-green-500" />;
    case 'error': return <XCircle size={16} className="text-red-500" />;
    default: return <div className="w-4 h-4 rounded-full bg-gray-200" />;
  }
}
