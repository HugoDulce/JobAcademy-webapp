interface CodeExecuteResponse {
  stdout: string;
  stderr: string;
  exit_code: number;
  timed_out: boolean;
  error: string | null;
}

interface Props {
  result: CodeExecuteResponse | null;
  isRunning: boolean;
}

export default function CodeOutputPanel({ result, isRunning }: Props) {
  if (isRunning) {
    return (
      <div className="bg-gray-900 text-green-300 p-4 rounded-lg text-sm font-mono">
        <span className="animate-pulse">Running...</span>
      </div>
    );
  }

  if (!result) return null;

  const hasError = result.error || result.timed_out;
  const hasStderr = result.stderr.trim().length > 0;

  return (
    <div className="bg-gray-900 rounded-lg text-sm font-mono overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
        <span className="text-gray-400 text-xs">Output</span>
        {!hasError && (
          <span className={`text-xs ${result.exit_code === 0 ? 'text-green-400' : 'text-red-400'}`}>
            exit {result.exit_code}
          </span>
        )}
      </div>

      <div className="p-4 space-y-2">
        {/* Validation / pre-execution error */}
        {result.error && (
          <div className="text-yellow-400 whitespace-pre-wrap">{result.error}</div>
        )}

        {/* Timeout */}
        {result.timed_out && (
          <div className="text-red-400">Execution timed out (10s limit)</div>
        )}

        {/* stdout */}
        {result.stdout && (
          <div className="text-green-300 whitespace-pre-wrap">{result.stdout}</div>
        )}

        {/* stderr */}
        {hasStderr && (
          <div className="text-red-400 whitespace-pre-wrap">{result.stderr}</div>
        )}

        {/* Empty output */}
        {!result.error && !result.timed_out && !result.stdout && !hasStderr && (
          <div className="text-gray-500 italic">No output</div>
        )}
      </div>
    </div>
  );
}
