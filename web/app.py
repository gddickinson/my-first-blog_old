"""FastAPI web app for my-first-blog_old: serves the front end in static/ and the JSON API under /api.

Run with `python run_web.py` (http://127.0.0.1:8257, local only). `scripts/build_static.py` exports every path in
STATIC_ENDPOINTS to JSON for the GitHub Pages site, so keep that list in step with the GET routes below.
This is a showcase: the 2016 code targets Django 1.9, which does not run on current Python, so nothing here runs it.
"""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import anatomy, changes, code_index

STATIC = Path(__file__).resolve().parent / "static"

app = FastAPI(title="my-first-blog_old")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/info")
def info():
    """Project summary for the home page (all counts from the files)."""
    t = code_index.tree()
    c = changes.changes()
    app_files = [f for f in t["files"] if f["group"].startswith("Django app")]
    return {"title": "my-first-blog_old", "files": len(t["files"]), "lines": t["total_lines"],
            "app_files": len(app_files), "app_lines": sum(f["lines"] for f in app_files),
            "django": c["structure"]["django_version"]["old"], "newer_django": c["structure"]["django_version"]["new"],
            "commits_2016": sum(e["date"].startswith("2016") for e in c["old_log"]),
            "newer": c["newer"]["repo"], "newer_commit": c["newer"]["commit"], "counts": c["counts"],
            "lines_added": c["lines_added"], "lines_removed": c["lines_removed"], "old_log": c["old_log"]}


@app.get("/api/anatomy")
def get_anatomy():
    return anatomy.anatomy()


@app.get("/api/changes")
def get_changes():
    return changes.changes()


@app.get("/api/code/tree")
def code_tree():
    return code_index.tree()


@app.get("/api/code/file/{key}")
def code_file(key: str):
    f = code_index.file(key)
    if f is None:
        raise HTTPException(404, "No such file")
    return f


@app.get("/api/code/search")
def code_search(q: str):
    return code_index.search(q)


# GET paths (without the /api prefix) written to the static site as api/<path>.json.
STATIC_ENDPOINTS = (["/info", "/anatomy", "/changes", "/code/tree"]
                    + [f"/code/file/{f['slug']}" for f in code_index.tree()["files"]])
