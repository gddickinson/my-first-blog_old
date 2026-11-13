"""Web interface tests: every exported endpoint answers, the static build is complete, and the JS engine tests pass.

Run: python -m pytest -q tests/test_web.py
"""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from web.app import STATIC, STATIC_ENDPOINTS, app  # noqa: E402

client = TestClient(app)


def test_index_served():
    r = client.get("/")
    assert r.status_code == 200 and "static/main.js" in r.text


@pytest.mark.parametrize("path", STATIC_ENDPOINTS)
def test_endpoint(path):
    r = client.get("/api" + path)
    assert r.status_code == 200, r.text
    assert r.json() is not None


def test_static_build(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_static
    build_static.build(tmp_path / "site")
    assert (tmp_path / "site" / "index.html").read_text().count("APP_STATIC") == 1
    for path in STATIC_ENDPOINTS:
        assert (tmp_path / "site" / "api" / (path.strip("/") + ".json")).exists()


def test_static_assets_referenced_exist():
    html = (STATIC / "index.html").read_text()
    for name in ("style.css", "main.js"):
        assert f"static/{name}" in html and (STATIC / name).exists()


@pytest.mark.skipif(not shutil.which("node"), reason="node not installed")
def test_js_engine():
    tests = sorted(STATIC.glob("*.test.mjs"))
    for t in tests:
        r = subprocess.run(["node", str(t)], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr


# --- project-specific ---------------------------------------------------------------------------------------
from web import changes  # noqa: E402


def test_diff_reconstructs_both_sides():
    old, new = changes.old_files(), changes.snapshot()["files"]
    for path in set(old) & set(new):
        a, b = changes.normalise(old[path]), changes.normalise(new[path])
        h = changes._hunks(a, b, context=10**6)
        lines = [x for hunk in h for x in hunk["lines"]]
        if a != b:
            assert [t for op, t, *_ in lines if op != "+"] == a.splitlines(), path
            assert [t for op, t, *_ in lines if op != "-"] == b.splitlines(), path


def test_changes_summary():
    c = client.get("/api/changes").json()
    s = c["structure"]
    assert s["views"]["old"] == ["post_list"] and "post_edit" in s["views"]["new"]
    assert s["django_version"] == {"old": "1.9", "new": "1.11.8", "old_migration": "1.9", "new_migration": "1.11.8"}
    assert s["model_same"] is True
    st = {f["path"]: f["status"] for f in c["files"]}
    assert st["blog/forms.py"] == "added" and st["blog/models.py"] == "same" and st["blog/views.py"] == "modified"
    assert not any(x["name"] == "SECRET_KEY" for x in s["settings"])


def test_anatomy_lines():
    a = client.get("/api/anatomy").json()
    for u in a["urls"]:
        assert u["regex"] in (ROOT / u["file"]).read_text().splitlines()[u["line"] - 1]
    assert a["views"][0]["context"] == "{}" and a["templates"][0]["template_tags"] == 0
    assert a["model"]["used_by_views"] is False


def test_no_hardcoded_secret_anywhere_in_export(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_static
    build_static.build(tmp_path / "site")
    pat = re.compile(r"SECRET_KEY\s*=\s*(['\"])(?!<redacted>)[^'\"\n]{8,}\1")
    for f in (tmp_path / "site").rglob("*"):
        if f.is_file() and f.suffix in (".json", ".js", ".html"):
            assert not pat.search(f.read_text()), f
    assert not pat.search(changes.SNAPSHOT.read_text())


NEWER = ROOT.parent / "my-first-blog"


@pytest.mark.skipif(not (NEWER / ".git").exists() or bool(os.environ.get("CI")), reason="needs a local clone of my-first-blog")
def test_snapshot_is_current():
    snap = changes.snapshot()
    r = subprocess.run(["git", "-C", str(NEWER), "ls-tree", "-r", "--name-only", snap["commit"]], capture_output=True, text=True)
    assert r.returncode == 0 and sorted(r.stdout.split()) == sorted(snap["files"])
