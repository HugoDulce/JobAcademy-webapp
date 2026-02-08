import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Search } from 'lucide-react';
import type { Card } from '../types/card';
import { fetchCards } from '../api/cards';
import { PILLARS, LAYERS } from '../constants';

export default function CardBrowserPage() {
  const [cards, setCards] = useState<Card[]>([]);
  const [search, setSearch] = useState('');
  const [pillarFilter, setPillarFilter] = useState('');
  const [layerFilter, setLayerFilter] = useState('');
  const [sortCol, setSortCol] = useState<keyof Card>('card_id');
  const [sortAsc, setSortAsc] = useState(true);

  useEffect(() => {
    fetchCards().then(setCards).catch(() => {});
  }, []);

  const filtered = useMemo(
    () =>
      cards
        .filter((c) => !pillarFilter || c.pillar === pillarFilter)
        .filter((c) => !layerFilter || c.knowledge_layer === layerFilter)
        .filter(
          (c) =>
            !search ||
            c.card_id.toLowerCase().includes(search.toLowerCase()) ||
            c.prompt.toLowerCase().includes(search.toLowerCase())
        )
        .sort((a, b) => {
          const av = a[sortCol] ?? '';
          const bv = b[sortCol] ?? '';
          const cmp = String(av).localeCompare(String(bv), undefined, { numeric: true });
          return sortAsc ? cmp : -cmp;
        }),
    [cards, pillarFilter, layerFilter, search, sortCol, sortAsc]
  );

  function toggleSort(col: keyof Card) {
    if (sortCol === col) setSortAsc(!sortAsc);
    else { setSortCol(col); setSortAsc(true); }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Cards ({filtered.length})</h1>
        <Link to="/cards/new" className="flex items-center gap-1 px-3 py-2 bg-indigo-600 text-white rounded-md text-sm hover:bg-indigo-700">
          <Plus size={16} /> New Card
        </Link>
      </div>

      <div className="flex gap-3 mb-4">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-2.5 text-gray-400" />
          <input
            type="text"
            placeholder="Search cards..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-2 border rounded-md text-sm"
          />
        </div>
        <select value={pillarFilter} onChange={(e) => setPillarFilter(e.target.value)} className="border rounded-md px-3 py-2 text-sm">
          <option value="">All Pillars</option>
          {PILLARS.map((p) => <option key={p} value={p}>{p}</option>)}
        </select>
        <select value={layerFilter} onChange={(e) => setLayerFilter(e.target.value)} className="border rounded-md px-3 py-2 text-sm">
          <option value="">All Layers</option>
          {LAYERS.map((l) => <option key={l} value={l}>{l}</option>)}
        </select>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-600">
            <tr>
              {(['card_id', 'pillar', 'knowledge_layer', 'fire_weight'] as const).map((col) => (
                <th key={col} className="px-4 py-3 text-left cursor-pointer hover:bg-gray-100" onClick={() => toggleSort(col)}>
                  {col.replace('_', ' ')}{sortCol === col ? (sortAsc ? ' ^' : ' v') : ''}
                </th>
              ))}
              <th className="px-4 py-3 text-left">Prompt</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {filtered.map((c) => (
              <tr key={c.card_id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <Link to={`/cards/${c.card_id}/edit`} className="text-indigo-600 hover:underline font-mono">
                    {c.card_id}
                  </Link>
                </td>
                <td className="px-4 py-3">{c.pillar}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                    c.knowledge_layer === 'Conceptual' ? 'bg-blue-100 text-blue-700' :
                    c.knowledge_layer === 'Mathematical' ? 'bg-purple-100 text-purple-700' :
                    'bg-green-100 text-green-700'
                  }`}>
                    {c.knowledge_layer}
                  </span>
                </td>
                <td className="px-4 py-3 font-mono">{c.fire_weight}</td>
                <td className="px-4 py-3 text-gray-600 truncate max-w-xs">{c.prompt}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
