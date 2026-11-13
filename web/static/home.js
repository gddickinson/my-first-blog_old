// Home: hero with the pointer to the newer version, real counts, cards.
import { api, app, esc, list, route } from './core.js';

route('home', async () => {
  const i = await api('/info');
  app().innerHTML = `
  <section class="hero">
    <p class="kicker">Django Girls tutorial · January 2016</p>
    <h1 class="glow">my-first-blog_old</h1>
    <p class="lead">George's first pass at the Django Girls tutorial: a Django ${esc(i.django)} project with a
      <code>Post</code> model and one page whose posts are still written straight into the HTML.</p>
    <div class="callout a"><b>Looking for the working blog?</b> The newer version,
      <a href="https://github.com/gddickinson/my-first-blog">my-first-blog</a> (December 2017, Django ${esc(i.newer_django)}),
      finishes the tutorial: posts from the database, detail pages, and a form to write and edit posts.
      <a href="https://gddickinson.github.io/my-first-blog/">Open its site</a> or
      <a href="#/changes">see what changed</a>.</div>
  </section>
  <div class="tiles">
    <div class="tile"><b>${i.app_files}</b><span>files in the 2016 app</span></div>
    <div class="tile"><b>${i.app_lines}</b><span>lines in the 2016 app</span></div>
    <div class="tile"><b>${i.commits_2016}</b><span>commits in January 2016</span></div>
    <div class="tile"><b>${i.counts.added}</b><span>files added in the newer version</span></div>
    <div class="tile"><b>+${i.lines_added} / -${i.lines_removed}</b><span>lines changed</span></div>
    <div class="tile"><b>${esc(i.django)} &rarr; ${esc(i.newer_django)}</b><span>Django version</span></div>
  </div>
  <div class="grid">
    <a class="card" href="#/how"><b>How it works</b><small>URL &rarr; view &rarr; template</small>
      <span>The one page this version serves, traced through the code, with the page itself.</span></a>
    <a class="card" href="#/changes"><b>What changed in the newer version</b><small>${i.counts.modified} modified · ${i.counts.added} added · ${i.counts.same} unchanged</small>
      <span>A file-by-file diff against my-first-blog at ${esc(i.newer_commit)}, plus the views, URLs, templates and settings that changed.</span></a>
    <a class="card" href="#/code"><b>Code explorer</b><small>${i.files} files · ${i.lines} lines</small>
      <span>Every file with line numbers, highlighting and search.</span></a>
    <a class="card" href="#/about"><b>About</b><small>history and licence</small>
      <span>${list(i.old_log, e => `${esc(e.date.slice(0, 10))}: ${esc(e.message)}`, '; ')}.</span></a>
  </div>`;
});
