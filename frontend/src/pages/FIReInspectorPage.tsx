import { useEffect, useState } from 'react';
import { Flame } from 'lucide-react';
import { fetchFIReData, simulateCredit } from '../api/fire';
import type { FIReData, CreditSimulationResult, EncompassingRelationship } from '../types/fire';

export default function FIReInspectorPage() {
  const [data, setData] = useState<FIReData | null>(null);
  const [simCard, setSimCard] = useState('');
  const [simResult, setSimResult] = useState<CreditSimulationResult | null>(null);
  const [tab, setTab] = useState<'heatmap' | 'simulator' | 'tree'>('heatmap');

  useEffect(() => {
    fetchFIReData().then(setData).catch(() => {});
  }, []);

  async function runSim(passed: boolean) {
    if (!simCard) return;
    const result = await simulateCredit(simCard, passed);
    setSimResult(result);
  }

  if (!data) return <div className="text-gray-500">Loading FIRe data...</div>;

  const parents = [...new Set(data.relationships.map((r) => r.parent_card_id))].sort();
  const children = [...new Set(data.relationships.map((r) => r.child_card_id))].sort();
  const allCards = [...new Set([...parents, ...children])].sort();

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4 flex items-center gap-2">
        <Flame size={24} className="text-orange-500" /> FIRe Inspector
      </h1>
      <p className="text-sm text-gray-500 mb-4">
        {data.relationships.length} encompassing relationships across {allCards.length} cards
      </p>

      <div className="flex gap-2 mb-4">
        {(['heatmap', 'simulator', 'tree'] as const).map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-md text-sm font-medium ${
              tab === t ? 'bg-orange-100 text-orange-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}>
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {tab === 'heatmap' && <Heatmap relationships={data.relationships} parents={parents} children={children} />}

      {tab === 'simulator' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-medium mb-4">Credit Simulator</h3>
          <div className="flex gap-3 mb-4">
            <select value={simCard} onChange={(e) => setSimCard(e.target.value)}
              className="border rounded px-3 py-2 text-sm flex-1">
              <option value="">Select a card...</option>
              {allCards.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
            <button onClick={() => runSim(true)} disabled={!simCard}
              className="px-4 py-2 bg-green-600 text-white rounded text-sm hover:bg-green-700 disabled:opacity-50">
              Pass
            </button>
            <button onClick={() => runSim(false)} disabled={!simCard}
              className="px-4 py-2 bg-red-600 text-white rounded text-sm hover:bg-red-700 disabled:opacity-50">
              Fail
            </button>
          </div>
          {simResult && (
            <div className="mt-4">
              <p className="text-sm font-medium mb-2">
                {simResult.passed ? 'Credit flows to:' : 'Needs review:'}
              </p>
              {simResult.credits.length === 0 ? (
                <p className="text-sm text-gray-400">No credit flow (standalone card)</p>
              ) : (
                <div className="space-y-1">
                  {simResult.credits.map((c, i) => (
                    <div key={i} className="flex justify-between text-sm py-1 px-2 rounded bg-gray-50">
                      <span className="font-mono">{c.card_id}</span>
                      <span className={c.credit > 0 ? 'text-green-600' : 'text-red-600'}>
                        {c.credit > 0 ? '+' : ''}{(c.credit * 100).toFixed(0)}%
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {tab === 'tree' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-medium mb-4">Encompassing Tree</h3>
          {parents.map((parent) => {
            const rels = data.relationships.filter((r) => r.parent_card_id === parent);
            if (rels.length === 0) return null;
            return (
              <div key={parent} className="mb-3">
                <div className="font-mono text-sm font-bold text-indigo-700">{parent}</div>
                <div className="ml-6 space-y-0.5">
                  {rels.map((r, i) => (
                    <div key={i} className="flex items-center gap-2 text-sm text-gray-600">
                      <span className="text-gray-300">|--</span>
                      <span className="font-mono">{r.child_card_id}</span>
                      <span className="text-xs text-gray-400">(w={r.weight})</span>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
          {data.standalone_cards.length > 0 && (
            <div className="mt-4 pt-4 border-t">
              <h4 className="text-sm font-medium text-gray-500 mb-2">Standalone Cards</h4>
              <div className="flex flex-wrap gap-2">
                {data.standalone_cards.map((c) => (
                  <span key={c} className="px-2 py-1 bg-gray-100 rounded text-xs font-mono">{c}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function Heatmap({ relationships, parents, children }: {
  relationships: EncompassingRelationship[]; parents: string[]; children: string[];
}) {
  const lookup = new Map<string, number>();
  relationships.forEach((r) => lookup.set(`${r.parent_card_id}:${r.child_card_id}`, r.weight));

  return (
    <div className="bg-white rounded-lg shadow p-4 overflow-x-auto">
      <table className="text-xs">
        <thead>
          <tr>
            <th className="px-1 py-1 sticky left-0 bg-white"></th>
            {children.map((c) => (
              <th key={c} className="px-1 py-1 font-mono transform -rotate-45 origin-left whitespace-nowrap">
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {parents.map((p) => (
            <tr key={p}>
              <td className="px-2 py-1 font-mono font-bold sticky left-0 bg-white whitespace-nowrap">{p}</td>
              {children.map((c) => {
                const w = lookup.get(`${p}:${c}`);
                return (
                  <td key={c} className="px-1 py-1 text-center" style={{
                    backgroundColor: w ? `rgba(249, 115, 22, ${w})` : 'transparent',
                  }}>
                    {w ? w.toFixed(1) : ''}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
