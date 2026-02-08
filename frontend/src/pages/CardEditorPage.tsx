import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Save, ArrowLeft } from 'lucide-react';
import { fetchCard, createCard, updateCard } from '../api/cards';
import LatexRenderer from '../components/shared/LatexRenderer';

export default function CardEditorPage() {
  const { cardId } = useParams();
  const navigate = useNavigate();
  const isNew = !cardId;

  const [form, setForm] = useState({
    card_id: '',
    deck: 'JobAcademy::Uncategorized::3-Algorithm',
    tags: '',
    fire_weight: 0.5,
    prompt: '',
    solution: '',
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (cardId) {
      fetchCard(cardId).then((c) =>
        setForm({
          card_id: c.card_id,
          deck: c.deck,
          tags: c.tags.join(', '),
          fire_weight: c.fire_weight,
          prompt: c.prompt,
          solution: c.solution,
        })
      );
    }
  }, [cardId]);

  async function handleSave() {
    setSaving(true);
    setError('');
    try {
      const tags = form.tags.split(',').map((t) => t.trim()).filter(Boolean);
      if (isNew) {
        await createCard({ ...form, tags });
      } else {
        await updateCard(cardId!, { deck: form.deck, tags, fire_weight: form.fire_weight, prompt: form.prompt, solution: form.solution });
      }
      navigate('/cards');
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => navigate('/cards')} className="p-2 hover:bg-gray-200 rounded">
          <ArrowLeft size={20} />
        </button>
        <h1 className="text-2xl font-bold">{isNew ? 'New Card' : `Edit ${cardId}`}</h1>
      </div>

      {error && <div className="mb-4 p-3 bg-red-50 text-red-700 rounded">{error}</div>}

      <div className="grid grid-cols-2 gap-6">
        <div className="space-y-4">
          <Field label="Card ID">
            <input value={form.card_id} onChange={(e) => setForm({ ...form, card_id: e.target.value })} disabled={!isNew}
              className="w-full border rounded px-3 py-2 text-sm font-mono disabled:bg-gray-100" placeholder="nb-3M-01" />
          </Field>
          <Field label="Deck">
            <input value={form.deck} onChange={(e) => setForm({ ...form, deck: e.target.value })}
              className="w-full border rounded px-3 py-2 text-sm" />
          </Field>
          <Field label="Tags (comma-separated)">
            <input value={form.tags} onChange={(e) => setForm({ ...form, tags: e.target.value })}
              className="w-full border rounded px-3 py-2 text-sm" />
          </Field>
          <Field label={`FIRe Weight: ${form.fire_weight}`}>
            <input type="range" min="0" max="1" step="0.1" value={form.fire_weight}
              onChange={(e) => setForm({ ...form, fire_weight: parseFloat(e.target.value) })}
              className="w-full" />
          </Field>
          <Field label="Prompt (Front)">
            <textarea value={form.prompt} onChange={(e) => setForm({ ...form, prompt: e.target.value })}
              rows={4} className="w-full border rounded px-3 py-2 text-sm font-mono" />
          </Field>
          <Field label="Solution (Back)">
            <textarea value={form.solution} onChange={(e) => setForm({ ...form, solution: e.target.value })}
              rows={10} className="w-full border rounded px-3 py-2 text-sm font-mono" />
          </Field>
          <button onClick={handleSave} disabled={saving}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50">
            <Save size={16} /> {saving ? 'Saving...' : 'Save Card'}
          </button>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500 mb-4">Preview</h3>
          <div className="mb-4">
            <p className="text-xs text-gray-400 mb-1">FRONT</p>
            <div className="p-3 bg-blue-50 rounded border border-blue-200">
              <LatexRenderer content={form.prompt} />
            </div>
          </div>
          <div>
            <p className="text-xs text-gray-400 mb-1">BACK</p>
            <div className="p-3 bg-green-50 rounded border border-green-200">
              <LatexRenderer content={form.solution} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      {children}
    </div>
  );
}
