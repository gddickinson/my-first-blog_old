// Code explorer: file list (grouped, filter by name), text search, and a source viewer with line numbers.
// #/code/<slug>?line=N opens a file and highlights a line. Summaries come from each file's own header comment.
import { api, app, esc, go, list, route } from './core.js';
import { highlightLines } from './highlight.js';

function fileList(tree, current, filter) {
  const f = filter.toLowerCase();
  const groups = {};
  for (const x of tree.files) if (!f || x.path.toLowerCase().includes(f)) (groups[x.group] ||= []).push(x);
  return (tree.groups || Object.keys(groups)).filter(g => groups[g]).map(g => [g, groups[g]]).map(([g, xs]) => `<h3>${esc(g)}</h3>${list(xs, x =>
    `<a href="#/code/${x.slug}" class="${x.slug === current ? 'on' : ''}">${esc(x.path)} <span class="mute">${x.lines}</span></a>`)}`).join('')
    || '<p class="mute small">No file matches.</p>';
}

async function viewer(slug, line) {
  const f = await api('/code/file/' + slug);
  const rows = highlightLines(f.text, f.lang);
  const n = rows.length;
  return `<h2 style="margin-top:0;overflow-wrap:anywhere">${esc(f.path)}</h2>
    <p class="small mute">${n} lines · ${esc(f.lang)}${f.summary ? ` · ${esc(f.summary)}` : ' · no header comment'}</p>
    <div class="src"><div class="ln">${rows.map((_, i) => `<a id="L${i + 1}" href="#/code/${slug}?line=${i + 1}&keep=1" class="${line === i + 1 ? 'hl' : ''}">${i + 1}</a>`).join('')}</div>
    <pre>${rows.map((r, i) => line === i + 1 ? `<span class="row-hl">${r || ' '}</span>` : r).join('\n')}</pre></div>`;
}

route('code', async ([slug], query) => {
  const tree = await api('/code/tree');
  const current = slug || (tree.files.find(f => f.path === 'blog/views.py') || tree.files[0]).slug;
  const line = query.line ? +query.line : null;
  app().innerHTML = `
  <p class="kicker">Code explorer</p><h1>Every file</h1>
  <p class="lead">${tree.files.length} files, ${tree.total_lines} lines (${list(Object.entries(tree.lines_by_lang),
    ([k, v]) => `${esc(k)} ${v}`, ', ')}). The 2016 tutorial code is under "Django app (2016)".</p>
  <div class="explorer">
    <div class="panel filelist"><label for="ff">Filter by file name</label><input id="ff" autocomplete="off">
      <form id="sf"><label for="sq">Search the text</label><input id="sq" value="${esc(query.q || '')}" autocomplete="off"></form>
      <div id="fl">${fileList(tree, current, '')}</div></div>
    <div id="view"></div>
  </div>`;
  const view = app().querySelector('#view');
  app().querySelector('#ff').addEventListener('input', e => { app().querySelector('#fl').innerHTML = fileList(tree, current, e.target.value); });
  app().querySelector('#sf').addEventListener('submit', e => {
    e.preventDefault(); go(`#/code/${current}?q=${encodeURIComponent(app().querySelector('#sq').value)}`);
  });
  if (query.q) {
    const hits = await api('/code/search?q=' + encodeURIComponent(query.q));
    const bySlug = Object.fromEntries(tree.files.map(f => [f.path, f.slug]));
    view.innerHTML = `<h2 style="margin-top:0">${hits.length} line(s) containing "${esc(query.q)}"</h2>
      <div class="scroll"><table><tbody>${list(hits, h => `<tr><td class="mono"><a href="#/code/${bySlug[h.path]}?line=${h.line}">${esc(h.path)}:${h.line}</a></td>
      <td class="mono">${esc(h.text)}</td></tr>`)}</tbody></table></div>`;
    return;
  }
  view.innerHTML = await viewer(current, line);
  if (line) view.querySelector('#L' + line)?.scrollIntoView({ block: 'center' });
});
