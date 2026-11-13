# INTERFACE.md: navigation map

## Django project (2016, Django 1.9)
| File | Contents |
|---|---|
| `manage.py` | Django command line |
| `mysite/settings.py` | settings (`MIDDLEWARE_CLASSES`, `SECRET_KEY` from `DJANGO_SECRET_KEY`) |
| `mysite/urls.py`, `blog/urls.py` | `admin/`, `include('blog.urls')`, `^$` -> `post_list` |
| `blog/views.py` | `post_list`: renders `post_list.html` with an empty context |
| `blog/models.py`, `blog/migrations/0001_initial.py`, `blog/admin.py` | `Post` model, its migration, admin registration |
| `blog/templates/blog/post_list.html` | hand-written HTML page with two placeholder posts |

## Web interface (`web/`, port 8257)
| File | Contents |
|---|---|
| `run_web.py` | uvicorn on 127.0.0.1:8257 |
| `web/app.py` | FastAPI: `/api/info`, `/api/anatomy`, `/api/changes`, `/api/code/tree`, `/api/code/file/{slug}`, `/api/code/search`; `STATIC_ENDPOINTS` |
| `web/anatomy.py` | `anatomy()`: urls, views, templates, model with file:line (ast, no Django import) |
| `web/changes.py` | `changes()`, `file_changes()`, `structure()`, `normalise()` against `web/data/newer_snapshot.json` |
| `web/code_index.py` | `tree()`, `file(slug)`, `search(q)`, `redact()`, `slug()` |
| `web/static/` | `index.html`, `core.js` + `style.css` (kit), `style_app.css`, `main.js`, `static_api.js`, pages `home.js`, `how.js`, `changes.js`, `code.js`, `about.js`, `highlight.js` |
| `scripts/make_newer_snapshot.py` | stores my-first-blog's files at a commit (secrets redacted) |
| `scripts/build_static.py`, `scripts/screenshots.py` | static export; Playwright smoke test and README images |
| `tests/test_web.py` | API, static build, diff correctness, snapshot currency |
