import { useEffect, useState } from 'react';
import { GraduationCap, Eye, RotateCcw } from 'lucide-react';
import { fetchDueCards, answerCard } from '../api/anki';
import type { DueCard } from '../types/anki';
import LatexRenderer from '../components/shared/LatexRenderer';

type SessionState = 'loading' | 'start' | 'prompt' | 'answer' | 'done' | 'error' | 'no-cards';

export default function DrillSessionPage() {
  const [cards, setCards] = useState<DueCard[]>([]);
  const [current, setCurrent] = useState(0);
  const [state, setState] = useState<SessionState>('loading');
  const [results, setResults] = useState<{ card_id: number; ease: number }[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    loadCards();
  }, []);

  async function loadCards() {
    setState('loading');
    try {
      const due = await fetchDueCards();
      setCards(due);
      setCurrent(0);
      setResults([]);
      setState(due.length > 0 ? 'start' : 'no-cards');
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
      setState('error');
    }
  }

  function startSession() {
    setCurrent(0);
    setResults([]);
    setState('prompt');
  }

  function showAnswer() {
    setState('answer');
  }

  async function grade(ease: number) {
    const card = cards[current];
    try {
      await answerCard(card.card_id, ease);
    } catch { /* continue even if Anki fails */ }
    setResults([...results, { card_id: card.card_id, ease }]);

    if (current + 1 < cards.length) {
      setCurrent(current + 1);
      setState('prompt');
    } else {
      setState('done');
    }
  }

  const card = cards[current];
  const correct = results.filter((r) => r.ease >= 3).length;

  if (state === 'loading') return <div className="text-gray-500">Loading due cards...</div>;
  if (state === 'error') return <div className="text-red-600">Error: {error}<br />Make sure Anki is running with AnkiConnect.</div>;

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

  // prompt or answer state
  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex justify-between items-center mb-4 text-sm text-gray-500">
        <span>Card {current + 1} of {cards.length}</span>
        <span>{correct} correct so far</span>
      </div>

      <div className="bg-white rounded-lg shadow p-6 mb-4">
        <p className="text-xs text-gray-400 mb-2">FRONT</p>
        <div className="text-lg">
          <LatexRenderer content={card.front.replace(/<br\s*\/?>/g, '\n')} />
        </div>
      </div>

      {state === 'prompt' && (
        <button onClick={showAnswer}
          className="w-full flex items-center justify-center gap-2 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
          <Eye size={18} /> Show Answer
        </button>
      )}

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
