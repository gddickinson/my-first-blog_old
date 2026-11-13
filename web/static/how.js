// How the 2016 version works, from /api/anatomy (web/anatomy.py reads the code); each claim links to file:line.
import { api, app, esc, list, route } from './core.js';
import { highlightLines } from './highlight.js';

const slug = f => f.replace(/[^A-Za-z0-9]+/g, '-');
const cite = (file, line) => `<a class="cite" href="#/code/${slug(file)}${line ? `?line=${line}` : ''}">${esc(file)}${line ? ':' + line : ''}</a>`;
const code = src => `<pre>${highlightLines(src, 'python').join('\n')}</pre>`;

route('how', async () => {
  const a = await api('/anatomy');
  const v = a.views[0], t = a.templates[0], m = a.model;
  const blogUrl = a.urls.find(u => u.file === 'blog/urls.py');
  app().innerHTML = `
  <p class="kicker">From the real code</p><h1>How it works</h1>
  <p class="lead">This version serves one page. Each step below is read from the code.</p>
  <ol>
    ${list(a.urls.filter(u => u.file === 'mysite/urls.py'), u => `<li><code>mysite/urls.py</code> matches <code>${esc(u.regex || "''")}</code> &rarr; <code>${esc(u.target)}</code> ${cite(u.file, u.line)}</li>`)}
    <li><code>blog/urls.py</code> matches <code>${esc(blogUrl.regex)}</code> (the empty path) &rarr; <code>${esc(blogUrl.target)}</code>,
      named <code>${esc(blogUrl.name)}</code> ${cite(blogUrl.file, blogUrl.line)}</li>
    <li><code>${esc(v.name)}</code> renders <code>${esc(v.templates.join(', '))}</code> with the context <code>${esc(v.context)}</code>,
      so no data goes to the template ${cite('blog/views.py', v.line)}</li>
    <li>The template contains ${t.template_tags} Django template tags: its ${t.headings.length} posts
      (${list(t.headings, ([ln, h]) => `"${esc(h)}" ${cite(t.file, ln)}`, ', ')}) and their dates
      (${list([...new Set(t.dates)], d => esc(d), ', ')}) are typed into the HTML.</li>
  </ol>
  ${code(v.source)}
  <h2>The page it serves</h2>
  <p class="small mute">${esc(t.file)}, shown as the browser would render it (sandboxed, no scripts).</p>
  <iframe class="preview" sandbox="" title="Rendered post_list.html" srcdoc="${esc(t.html)}"></iframe>
  <h2>The model, defined but not used yet</h2>
  <p><code>${esc(m.name)}</code> (${cite(m.file, m.line)}) has a migration and is registered in the admin (${cite('blog/admin.py', 4)}), but
    ${m.used_by_views ? 'is used by the views' : '<code>blog/views.py</code> never queries it'}; the newer version's
    <code>post_list</code> reads posts from it.</p>
  <div class="scroll"><table><thead><tr><th>Field</th><th>Declaration</th><th>Line</th></tr></thead><tbody>
    ${list(m.fields, f => `<tr><td><code>${esc(f.name)}</code></td><td class="mono small">${esc(f.decl.replace(/\s+/g, ' '))}</td><td>${cite(m.file, f.line)}</td></tr>`)}
  </tbody></table></div>
  <p>Methods: ${list(m.methods, x => `<code>${esc(x.name)}()</code> ${cite(m.file, x.line)}`, ', ')}.</p>`;
});
