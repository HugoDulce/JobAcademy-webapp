import { useState, useEffect, useRef } from 'react';
import type { DueCard } from '../../types/anki';

interface CardEditModalProps {
  card: DueCard;
  onSave: (front: string, back: string) => Promise<void>;
  onClose: () => void;
}

export default function CardEditModal({ card, onSave, onClose }: CardEditModalProps) {
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const backdropRef = useRef<HTMLDivElement>(null);
  const frontRef = useRef<HTMLDivElement>(null);
  const backRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose();
    }
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [onClose]);

  function handleBackdropClick(e: React.MouseEvent) {
    if (e.target === backdropRef.current) onClose();
  }

  async function handleSave() {
    const front = frontRef.current?.innerHTML ?? card.front;
    const back = backRef.current?.innerHTML ?? card.back;
    setSaving(true);
    setError('');
    try {
      await onSave(front, back);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
      setSaving(false);
    }
  }

  const editableClass =
    'w-full border border-gray-300 rounded-md p-3 mb-4 text-sm min-h-[6rem] focus:outline-none focus:ring-2 focus:ring-indigo-400 overflow-y-auto';

  return (
    <div
      ref={backdropRef}
      onClick={handleBackdropClick}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
    >
      <div className="bg-white rounded-lg shadow-xl w-full max-w-lg mx-4 p-6">
        <h3 className="text-lg font-semibold mb-4">Edit Card</h3>

        <label className="block text-xs font-medium text-gray-500 mb-1">Front</label>
        <div
          ref={frontRef}
          contentEditable
          suppressContentEditableWarning
          className={editableClass}
          dangerouslySetInnerHTML={{ __html: card.front }}
        />

        <label className="block text-xs font-medium text-gray-500 mb-1">Back</label>
        <div
          ref={backRef}
          contentEditable
          suppressContentEditableWarning
          className={editableClass}
          dangerouslySetInnerHTML={{ __html: card.back }}
        />

        {error && <p className="text-red-600 text-sm mb-3">{error}</p>}

        <div className="flex justify-end gap-2">
          <button
            onClick={onClose}
            disabled={saving}
            className="px-4 py-2 text-sm text-gray-600 bg-gray-100 rounded-md hover:bg-gray-200 disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 text-sm text-white bg-indigo-600 rounded-md hover:bg-indigo-700 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  );
}
