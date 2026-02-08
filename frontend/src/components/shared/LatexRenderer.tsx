import katex from 'katex';

interface Props {
  content: string;
}

export default function LatexRenderer({ content }: Props) {
  const rendered = content
    // Block math: $$...$$
    .replace(/\$\$([\s\S]*?)\$\$/g, (_: string, tex: string) => {
      try {
        return katex.renderToString(tex.trim(), { displayMode: true, throwOnError: false });
      } catch { return `<code>${tex}</code>`; }
    })
    // Inline math: $...$
    .replace(/\$([^$\n]+)\$/g, (_: string, tex: string) => {
      try {
        return katex.renderToString(tex.trim(), { displayMode: false, throwOnError: false });
      } catch { return `<code>${tex}</code>`; }
    })
    // Code blocks
    .replace(/```(\w*)\n([\s\S]*?)```/g, (_: string, lang: string, code: string) =>
      `<pre class="bg-gray-900 text-green-300 p-3 rounded text-sm overflow-x-auto"><code>${code.replace(/</g, '&lt;')}</code></pre>`
    )
    // Newlines to <br>
    .replace(/\n/g, '<br/>');

  return <div dangerouslySetInnerHTML={{ __html: rendered }} className="text-sm leading-relaxed" />;
}
