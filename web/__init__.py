"""Showcase web interface for my-first-blog_old (the 2016 Django Girls attempt; newer version: my-first-blog).

Contents:
    app.py         FastAPI app: JSON API under /api and the front end in static/ (port 8257)
    anatomy.py     how the 2016 version works: URL pattern -> view -> template, and the model, with file:line
    changes.py     "What changed in the newer version": difflib + ast against web/data/newer_snapshot.json
    code_index.py  code explorer: file tree, contents, header summaries (secrets redacted)
    data/          newer_snapshot.json, the newer repo's files (made by scripts/make_newer_snapshot.py)
    static/        the ES-module front end (no build step)
"""
