import React from 'react';

/**
 * Renders markdown text into cleanly styled elements, with full support for:
 * - Markdown tables (| header | header |)
 * - Headings (###, ##, #)
 * - Bold (**text**)
 * - Bullet lists (* or -)
 * - Inline code (`code`)
 * - Paragraphs
 */
export default function FormattedAnswer({ content }) {
  if (!content) return null;

  // Split content into blocks (tables vs paragraphs/lists)
  const lines = content.split('\n');
  const blocks = [];
  let currentTable = [];
  let currentText = [];

  const flushText = () => {
    if (currentText.length > 0) {
      blocks.push({ type: 'text', lines: [...currentText] });
      currentText = [];
    }
  };

  const flushTable = () => {
    if (currentTable.length > 0) {
      blocks.push({ type: 'table', lines: [...currentTable] });
      currentTable = [];
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    // Check if line looks like a markdown table row (starts and ends with |, or has multiple |)
    const isTableRow = line.startsWith('|') && line.endsWith('|') && line.includes('|');

    if (isTableRow) {
      flushText();
      currentTable.push(line);
    } else {
      if (currentTable.length > 0) {
        flushTable();
      }
      currentText.push(lines[i]);
    }
  }

  flushTable();
  flushText();

  const renderInlineFormatted = (text) => {
    // Basic regex for **bold** and `code`
    const parts = [];
    let remaining = text;
    let keyIdx = 0;

    // Split by ** or `
    const tokenRegex = /(\*\*[^*]+\*\*|`[^`]+`)/g;
    let lastIndex = 0;
    let match;

    while ((match = tokenRegex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        parts.push(text.substring(lastIndex, match.index));
      }
      const token = match[0];
      if (token.startsWith('**') && token.endsWith('**')) {
        parts.push(
          <strong key={keyIdx++} className="font-semibold text-white">
            {token.slice(2, -2)}
          </strong>
        );
      } else if (token.startsWith('`') && token.endsWith('`')) {
        parts.push(
          <code key={keyIdx++} className="px-1.5 py-0.5 rounded bg-slate-800 text-indigo-300 font-mono text-xs border border-white/10">
            {token.slice(1, -1)}
          </code>
        );
      }
      lastIndex = tokenRegex.lastIndex;
    }

    if (lastIndex < text.length) {
      parts.push(text.substring(lastIndex));
    }

    return parts.length > 0 ? parts : text;
  };

  return (
    <div className="space-y-3 text-slate-100 text-xs md:text-sm leading-relaxed">
      {blocks.map((block, bIdx) => {
        if (block.type === 'table') {
          // Parse markdown table
          const tableRows = block.lines
            .map(row => 
              row
                .split('|')
                .slice(1, -1)
                .map(cell => cell.trim())
            )
            .filter(row => row.length > 0);

          if (tableRows.length < 2) {
            // Not a valid table, render as raw lines
            return (
              <div key={bIdx} className="font-mono text-xs whitespace-pre-wrap">
                {block.lines.join('\n')}
              </div>
            );
          }

          const headerRow = tableRows[0];
          // Check if row 1 is separator (--- | ---)
          const isSeparator = tableRows[1]?.every(c => /^[-:\s]+$/.test(c));
          const dataRows = isSeparator ? tableRows.slice(2) : tableRows.slice(1);

          return (
            <div key={bIdx} className="my-3 overflow-x-auto rounded-xl border border-white/15 shadow-md bg-slate-950/60">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-slate-800/90 border-b border-white/15 text-slate-200">
                    {headerRow.map((th, thIdx) => (
                      <th
                        key={thIdx}
                        className="py-2.5 px-3.5 font-semibold text-teal-300 uppercase tracking-wider text-[11px]"
                      >
                        {renderInlineFormatted(th)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {dataRows.map((row, rIdx) => (
                    <tr
                      key={rIdx}
                      className="hover:bg-indigo-950/20 transition-colors odd:bg-slate-900/40 even:bg-slate-900/20"
                    >
                      {row.map((cell, cIdx) => (
                        <td key={cIdx} className="py-2 px-3.5 text-slate-200 font-normal">
                          {renderInlineFormatted(cell)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        }

        // Render text lines
        return (
          <div key={bIdx} className="space-y-1.5">
            {block.lines.map((line, lIdx) => {
              const trimmed = line.trim();
              if (!trimmed) {
                return <div key={lIdx} className="h-1" />;
              }

              if (trimmed.startsWith('### ')) {
                return (
                  <h4 key={lIdx} className="text-xs md:text-sm font-bold text-indigo-300 mt-2 mb-1">
                    {renderInlineFormatted(trimmed.replace('### ', ''))}
                  </h4>
                );
              }

              if (trimmed.startsWith('## ')) {
                return (
                  <h3 key={lIdx} className="text-sm md:text-base font-bold text-teal-300 mt-2.5 mb-1">
                    {renderInlineFormatted(trimmed.replace('## ', ''))}
                  </h3>
                );
              }

              if (trimmed.startsWith('# ')) {
                return (
                  <h2 key={lIdx} className="text-base font-extrabold text-white mt-3 mb-1">
                    {renderInlineFormatted(trimmed.replace('# ', ''))}
                  </h2>
                );
              }

              if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
                return (
                  <div key={lIdx} className="flex items-start gap-2 ml-1 text-slate-200">
                    <span className="text-indigo-400 mt-1 flex-shrink-0 text-[10px]">●</span>
                    <span className="flex-1">{renderInlineFormatted(trimmed.slice(2))}</span>
                  </div>
                );
              }

              return (
                <p key={lIdx} className="text-slate-200 leading-relaxed">
                  {renderInlineFormatted(line)}
                </p>
              );
            })}
          </div>
        );
      })}
    </div>
  );
}
