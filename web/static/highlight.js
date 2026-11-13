// Small dependency-free syntax highlighter for the code explorer: Python, HTML with Django template tags, CSS, JS,
// YAML/JSON. highlightLines(text, lang) returns one HTML string per source line (spans never cross a line).
import { esc } from './core.js';

const PY_KW = 'and as assert async await break class continue def del elif else except False finally for from global if import in is lambda None nonlocal not or pass raise return True try while with yield';
const JS_KW = 'async await break case catch class const continue default delete do else export extends false finally for from function if import in instanceof let new null of return static super switch this throw true try typeof undefined var void while yield';
const kw = words => `\\b(?:${words.split(' ').join('|')})\\b`;

// Each rule: [class, regex source]. Earlier rules win at the same position.
const RULES = {
  python: [['c', '#[^\\n]*'], ['s', `[rRbBuUfF]{0,2}(?:"""[\\s\\S]*?"""|'''[\\s\\S]*?'''|"(?:\\\\.|[^"\\\\\\n])*"|'(?:\\\\.|[^'\\\\\\n])*')`],
    ['d', '@[\\w.]+'], ['k', kw(PY_KW)], ['f', '(?<=\\b(?:def|class)\\s+)\\w+'], ['n', '\\b\\d+(?:\\.\\d+)?\\b']],
  html: [['c', '<!--[\\s\\S]*?-->|{#[\\s\\S]*?#}'], ['d', '{%[\\s\\S]*?%}|{{[\\s\\S]*?}}'], ['t', '</?[A-Za-z][\\w-]*|/?>'],
    ['s', '"[^"\\n]*"|\'[^\'\\n]*\''], ['f', '\\b[\\w-]+(?==)']],
  css: [['c', '/\\*[\\s\\S]*?\\*/'], ['s', '"[^"\\n]*"|\'[^\'\\n]*\''], ['f', '[\\w-]+(?=\\s*:[^{]*;)'],
    ['n', '#[0-9a-fA-F]{3,8}\\b|\\b\\d+(?:\\.\\d+)?(?:px|pt|em|rem|%|s|vh|vw)?\\b'], ['t', '[.#]?[A-Za-z][\\w-]*(?=[^{};]*{)']],
  js: [['c', '//[^\\n]*|/\\*[\\s\\S]*?\\*/'], ['s', '`(?:\\\\.|[^`\\\\])*`|"(?:\\\\.|[^"\\\\\\n])*"|\'(?:\\\\.|[^\'\\\\\\n])*\''],
    ['k', kw(JS_KW)], ['n', '\\b\\d+(?:\\.\\d+)?\\b']],
  yaml: [['c', '#[^\\n]*'], ['s', '"[^"\\n]*"|\'[^\'\\n]*\''], ['f', '^\\s*-?\\s*[\\w.-]+(?=:)'], ['d', '\\$\\{\\{[^}]*\\}\\}']],
  json: [['f', '"(?:\\\\.|[^"\\\\])*"(?=\\s*:)'], ['s', '"(?:\\\\.|[^"\\\\])*"'], ['n', '-?\\b\\d+(?:\\.\\d+)?\\b'], ['k', '\\b(?:true|false|null)\\b']],
};
RULES.xml = RULES.html;
const compiled = {};

function tokens(text, lang) {
  const rules = RULES[lang];
  if (!rules) return [[null, text]];
  if (!compiled[lang]) compiled[lang] = new RegExp(rules.map(([, src]) => `(${src})`).join('|'), 'gm');
  const re = compiled[lang];
  re.lastIndex = 0;
  const out = [];
  let pos = 0, m;
  while ((m = re.exec(text))) {
    if (m[0] === '') { re.lastIndex++; continue; }
    const g = m.slice(1).findIndex(x => x !== undefined);
    if (m.index > pos) out.push([null, text.slice(pos, m.index)]);
    out.push([rules[g][0], m[0]]);
    pos = m.index + m[0].length;
  }
  if (pos < text.length) out.push([null, text.slice(pos)]);
  return out;
}

export function highlightLines(text, lang) {
  const lines = [''];
  for (const [cls, t] of tokens(text, lang)) {
    t.split('\n').forEach((piece, i) => {
      if (i > 0) lines.push('');
      if (piece) lines[lines.length - 1] += cls ? `<span class="tk-${cls}">${esc(piece)}</span>` : esc(piece);
    });
  }
  if (text.endsWith('\n')) lines.pop();
  return lines;
}
