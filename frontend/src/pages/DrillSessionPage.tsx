import { useEffect, useState } from 'react';
import { GraduationCap, Eye, RotateCcw, Play, Code } from 'lucide-react';
import { fetchDueCards, answerCard, checkAnkiStatus } from '../api/anki';
import { executeCode } from '../api/code';
import type { DueCard } from '../types/anki';
import type { CodeExecuteResponse } from '../api/code';
import LatexRenderer from '../components/shared/LatexRenderer';
import CodeEditor from '../components/shared/CodeEditor';
import CodeOutputPanel from '../components/shared/CodeOutputPanel';

type SessionState = 'loading' | 'start' | 'prompt' | 'answer' | 'done' | 'error' | 'no-cards';

// ---------------------------------------------------------------------------
// Programming card helpers
// ---------------------------------------------------------------------------

function isProgrammingCard(card: DueCard): boolean {
  return card.tags.includes('programming');
}

function getCognitiveType(card: DueCard): 'build' | 'debug' | 'extend' | null {
  if (card.tags.includes('build')) return 'build';
  if (card.tags.includes('debug')) return 'debug';
  if (card.tags.includes('extend')) return 'extend';
  return null;
}

/** Extract the first Python code block from the card front (prompt). */
function extractStarterCode(front: string): string {
  const match = front.match(/```(?:python)?\s*\n([\s\S]*?)```/);
  return match ? match[1].trimEnd() + '\n' : '';
}

const COGNITIVE_BADGE: Record<string, { label: string; cls: string }> = {
  build: { label: 'Build', cls: 'bg-indigo-100 text-indigo-700' },
  debug: { label: 'Debug', cls: 'bg-red-100 text-red-700' },
  extend: { label: 'Extend', cls: 'bg-amber-100 text-amber-700' },
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function DrillSessionPage() {
  const [cards, setCards] = useState<DueCard[]>([]);
  const [current, setCurrent] = useState(0);
  const [state, setState] = useState<SessionState>('loading');
  const [results, setResults] = useState<{ card_id: number | string; ease: number }[]>([]);
  const [error, setError] = useState('');
  const [mode, setMode] = useState<'anki' | 'server-srs' | null>(null);

  // Code execution state
  const [userCode, setUserCode] = useState('');
  const [codeOutput, setCodeOutput] = useState<CodeExecuteResponse | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    loadCards();
  }, []);

  async function loadCards() {
    setState('loading');
    try {
      const status = await checkAnkiStatus();
      setMode(status.connected ? 'anki' : 'server-srs');
      const due = await fetchDueCards();
      setCards(due);
      setCurrent(0);
      setResults([]);
      resetCodeState();
      setState(due.length > 0 ? 'start' : 'no-cards');
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
      setState('error');
    }
  }

  function resetCodeState() {
    setUserCode('');
    setCodeOutput(null);
    setIsRunning(false);
  }

  function startSession() {
    setCurrent(0);
    setResults([]);
    resetCodeState();
    initCodeForCard(cards[0]);
    setState('prompt');
  }

  /** Pre-fill editor for debug/extend cards. */
  function initCodeForCard(card: DueCard) {
    if (!isProgrammingCard(card)) return;
    const cogType = getCognitiveType(card);
    if (cogType === 'debug' || cogType === 'extend') {
      setUserCode(extractStarterCode(card.front));
    } else {
      setUserCode('');
    }
    setCodeOutput(null);
  }

  function showAnswer() {
    setState('answer');
  }

  async function runCode() {
    if (isRunning) return;
    setIsRunning(true);
    setCodeOutput(null);
    try {
      const result = await executeCode(userCode);
      setCodeOutput(result);
    } catch (e: unknown) {
      setCodeOutput({
        stdout: '',
        stderr: '',
        exit_code: -1,
        timed_out: false,
        error: e instanceof Error ? e.message : String(e),
      });
    } finally {
      setIsRunning(false);
    }
  }

  async function grade(ease: number) {
    const card = cards[current];
    try {
      await answerCard(card.card_id, ease);
    } catch { /* continue even if Anki fails */ }
    setResults([...results, { card_id: card.card_id, ease }]);

    if (current + 1 < cards.length) {
      const next = current + 1;
      setCurrent(next);
      resetCodeState();
      initCodeForCard(cards[next]);
      setState('prompt');
    } else {
      setState('done');
    }
  }

  const card = cards[current];
  const correct = results.filter((r) => r.ease >= 3).length;

  if (state === 'loading') return <div className="text-gray-500">Loading due cards...</div>;
  if (state === 'error') return <div className="text-red-600">Error: {error}<br />Could not load drill cards. Please try again.</div>;

  if (state === 'no-cards') {
    return (
      <div className="text-center py-16">
        <GraduationCap size={48} className="mx-auto text-gray-300 mb-4" />
        <h2 className="text-xl font-semibold text-gray-600">No cards due</h2>
        <p className="text-gray-400 mt-2">All caught up! Come back later.</p>
      </div>
    );
  }

  if (state === 'start') {
    return (
      <div className="text-center py-16">
        <GraduationCap size={48} className="mx-auto text-indigo-400 mb-4" />
        <h2 className="text-xl font-semibold mb-2">Drill Session</h2>
        {mode && (
          <span className={`inline-block text-xs px-2 py-0.5 rounded-full mb-2 ${mode === 'anki' ? 'bg-blue-100 text-blue-700' : 'bg-amber-100 text-amber-700'}`}>
            {mode === 'anki' ? 'Anki' : 'Server SRS'}
          </span>
        )}
        <p className="text-gray-500 mb-6">{cards.length} cards due for review</p>
        <button onClick={startSession}
          className="px-6 py-3 bg-indigo-600 text-white rounded-lg text-lg hover:bg-indigo-700">
          Begin Review
        </button>
      </div>
    );
  }

  if (state === 'done') {
    return (
      <div className="max-w-lg mx-auto text-center py-16">
        <h2 className="text-2xl font-bold mb-4">Session Complete</h2>
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">Total</p>
            <p className="text-2xl font-bold">{results.length}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">Correct</p>
            <p className="text-2xl font-bold text-green-600">{correct}/{results.length}</p>
          </div>
        </div>
        <button onClick={loadCards}
          className="flex items-center gap-2 mx-auto px-4 py-2 bg-gray-200 rounded-md hover:bg-gray-300">
          <RotateCcw size={16} /> New Session
        </button>
      </div>
    );
  }

  // ---------------------------------------------------------------------------
  // prompt or answer state
  // ---------------------------------------------------------------------------

  const programming = isProgrammingCard(card);
  const cogType = programming ? getCognitiveType(card) : null;
  const badge = cogType ? COGNITIVE_BADGE[cogType] : null;

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex justify-between items-center mb-4 text-sm text-gray-500">
        <span>Card {current + 1} of {cards.length}</span>
        <span>{correct} correct so far</span>
      </div>

      {/* FRONT card */}
      <div className="bg-white rounded-lg shadow p-6 mb-4">
        <div className="flex items-center gap-2 mb-2">
          <p className="text-xs text-gray-400">FRONT</p>
          {badge && (
            <span className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full ${badge.cls}`}>
              <Code size={12} /> {badge.label}
            </span>
          )}
        </div>
        <div className="text-lg">
          <LatexRenderer content={card.front.replace(/<br\s*\/?>/g, '\n')} />
        </div>
      </div>

      {/* Code editor for programming cards */}
      {programming && (
        <div className="mb-4 space-y-3">
          <CodeEditor
            value={userCode}
            onChange={setUserCode}
            onRun={runCode}
          />

          <div className="flex items-center gap-2">
            <button
              onClick={runCode}
              disabled={isRunning || !userCode.trim()}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
            >
              <Play size={14} />
              {isRunning ? 'Running...' : 'Run Code'}
            </button>
            <span className="text-xs text-gray-400">Ctrl+Enter to run</span>
          </div>

          <CodeOutputPanel result={codeOutput} isRunning={isRunning} />
        </div>
      )}

      {/* Show Answer button */}
      {state === 'prompt' && (
        <button onClick={showAnswer}
          className="w-full flex items-center justify-center gap-2 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
          <Eye size={18} /> Show Answer
        </button>
      )}

      {/* Answer + grading */}
      {state === 'answer' && (
        <>
          <div className="bg-green-50 rounded-lg border border-green-200 p-6 mb-4">
            <p className="text-xs text-gray-400 mb-2">BACK</p>
            <LatexRenderer content={card.back.replace(/<br\s*\/?>/g, '\n')} />
          </div>
          <div className="grid grid-cols-4 gap-2">
            <button onClick={() => grade(1)} className="py-3 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 font-medium">Again</button>
            <button onClick={() => grade(2)} className="py-3 bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200 font-medium">Hard</button>
            <button onClick={() => grade(3)} className="py-3 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 font-medium">Good</button>
            <button onClick={() => grade(4)} className="py-3 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 font-medium">Easy</button>
          </div>
        </>
      )}

      <div className="flex justify-between mt-4 text-xs text-gray-400">
        <span>Deck: {card.deck}</span>
        <span>Tags: {card.tags.join(', ')}</span>
      </div>
    </div>
  );
}
