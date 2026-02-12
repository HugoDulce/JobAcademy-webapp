import { useRef, useEffect } from 'react';
import { EditorView, keymap } from '@codemirror/view';
import { EditorState } from '@codemirror/state';
import { basicSetup } from 'codemirror';
import { python } from '@codemirror/lang-python';

interface Props {
  value: string;
  onChange: (value: string) => void;
  onRun?: () => void;
  readOnly?: boolean;
}

export default function CodeEditor({ value, onChange, onRun, readOnly = false }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const viewRef = useRef<EditorView | null>(null);

  // Create editor once on mount
  useEffect(() => {
    if (!containerRef.current) return;

    const extensions = [
      basicSetup,
      python(),
      EditorView.updateListener.of((update) => {
        if (update.docChanged) {
          onChange(update.state.doc.toString());
        }
      }),
      EditorView.theme({
        '&': { fontSize: '14px' },
        '.cm-content': { fontFamily: 'monospace' },
        '.cm-gutters': { backgroundColor: '#1e1e2e', color: '#6c7086', border: 'none' },
        '&.cm-editor': { backgroundColor: '#1e1e2e', borderRadius: '0.5rem' },
        '.cm-content, .cm-line': { color: '#cdd6f4' },
        '.cm-activeLine': { backgroundColor: '#313244' },
        '.cm-activeLineGutter': { backgroundColor: '#313244' },
        '.cm-selectionBackground': { backgroundColor: '#45475a !important' },
      }),
    ];

    if (onRun) {
      extensions.push(
        keymap.of([
          {
            key: 'Mod-Enter',
            run: () => { onRun(); return true; },
          },
        ])
      );
    }

    if (readOnly) {
      extensions.push(EditorState.readOnly.of(true));
    }

    const state = EditorState.create({ doc: value, extensions });
    const view = new EditorView({ state, parent: containerRef.current });
    viewRef.current = view;

    return () => { view.destroy(); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Sync external value changes (e.g. card switch) without recreating editor
  useEffect(() => {
    const view = viewRef.current;
    if (!view) return;
    const current = view.state.doc.toString();
    if (current !== value) {
      view.dispatch({
        changes: { from: 0, to: current.length, insert: value },
      });
    }
  }, [value]);

  return (
    <div
      ref={containerRef}
      className="rounded-lg overflow-hidden border border-gray-700"
    />
  );
}
