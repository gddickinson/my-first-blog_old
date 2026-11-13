// Answers api(path) on the static GitHub Pages site from the JSON exported by scripts/build_static.py.
// Text search over the code runs here in the browser (the server does the same in web/code_index.py).

async function json(p) {
  const r = await fetch('api' + p + '.json');
  if (!r.ok) throw new Error(`${r.status}: ${p} is not part of the static site`);
  return r.json();
}

async function search(q) {
  const tree = await json('/code/tree');
  const files = await Promise.all(tree.files.map(f => json('/code/file/' + f.slug)));
  const needle = q.toLowerCase(), hits = [];
  for (const f of files) {
    f.text.split('\n').forEach((line, i) => {
      if (hits.length < 200 && line.toLowerCase().includes(needle)) hits.push({ path: f.path, line: i + 1, text: line.trim().slice(0, 200) });
    });
  }
  return hits;
}

export async function staticApi(path, body) {
  if (body) throw new Error('This needs the local app (python run_web.py).');
  const [p, qs] = path.split('?');
  if (p === '/code/search') return search(new URLSearchParams(qs).get('q') || '');
  return json(p);
}
