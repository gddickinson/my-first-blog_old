// About: what it is, the newer version, history, licence.
import { api, app, esc, list, route } from './core.js';

route('about', async () => {
  const i = await api('/info');
  app().innerHTML = `
  <p class="kicker">About</p><h1>my-first-blog_old</h1>
  <p class="lead">George's first Django Girls tutorial blog, from January 2016. It stops at the stage where the
    page's HTML is written by hand; the model exists but no view uses it yet.</p>
  <div class="callout a">The newer version is <a href="https://github.com/gddickinson/my-first-blog">gddickinson/my-first-blog</a>
    (<a href="https://gddickinson.github.io/my-first-blog/">site</a>), which completes the tutorial and runs on current Django.</div>
  <h2>History</h2>
  <ul>${list(i.old_log, e => `<li><code>${esc(e.sha)}</code> ${esc(e.date.slice(0, 10))}: ${esc(e.message)}</li>`)}</ul>
  <h2>Running the 2016 code</h2>
  <p>It was written for Django ${esc(i.django)} (<code>MIDDLEWARE_CLASSES</code>, <code>django.conf.urls.url</code>,
    a <code>ForeignKey</code> without <code>on_delete</code>), which officially supports Python 2.7, 3.4 and 3.5 only, so this site does not run
    it. With such an environment: <code>pip install Django==1.9</code>, <code>python manage.py migrate</code>,
    <code>python manage.py runserver</code>. <code>SECRET_KEY</code> is read from the <code>DJANGO_SECRET_KEY</code>
    environment variable.</p>
  <h2>Run this web interface</h2>
  <pre>pip install -r requirements-web.txt
python run_web.py      # http://127.0.0.1:8257</pre>
  <h2>Licence</h2><p>MIT (see LICENSE). Code by George Dickinson, following the Django Girls tutorial.</p>`;
});
