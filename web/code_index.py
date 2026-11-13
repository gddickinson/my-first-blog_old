"""Code explorer data: the repository's text files, their contents and a summary taken from each file's own
header (module docstring or leading comment; never invented). Secret-looking string assignments are redacted.
"""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "site", "__pycache__", ".pytest_cache", "node_modules", "myvenv"}
SKIP_ROOT_DIRS = {"static"}  # collectstatic output (git-ignored /static)
SKIP_FILES = {"web/data/newer_snapshot.json"}  # the other repo's files; shown on the "What changed" page instead
TEXT_EXT = {".py", ".html", ".css", ".js", ".mjs", ".md", ".txt", ".yml", ".yaml", ".json", ".svg", ".cfg",
            ".toml", ".ini", ""}
MAX_BYTES = 200_000
LANG = {".py": "python", ".html": "html", ".css": "css", ".js": "js", ".mjs": "js", ".md": "markdown",
        ".yml": "yaml", ".yaml": "yaml", ".json": "json", ".svg": "xml"}
SECRET = re.compile(r"""^(\s*\w*(?:SECRET|PASSWORD|TOKEN|API_KEY)\w*\s*=\s*)(['"])(?!\2)[^'"\n]{8,}\2""", re.M)


def redact(text: str) -> str:
    """Replace hard-coded secret-looking string literals (SECRET_KEY = '...') with a placeholder."""
    return SECRET.sub(lambda m: f"{m.group(1)}{m.group(2)}<redacted>{m.group(2)}", text)


def _wanted(p: Path) -> bool:
    rel = p.relative_to(ROOT)
    if any(part in SKIP_DIRS for part in rel.parts[:-1]) or rel.parts[0] in SKIP_ROOT_DIRS and len(rel.parts) > 1:
        return False
    name = p.name
    if rel.as_posix() in SKIP_FILES:
        return False
    if name in (".DS_Store",) or name.endswith((".pyc", ".sqlite3")) or p.suffix not in TEXT_EXT:
        return False
    return p.stat().st_size <= MAX_BYTES


def files() -> list[Path]:
    return sorted((p for p in ROOT.rglob("*") if p.is_file() and _wanted(p)), key=lambda p: p.relative_to(ROOT).as_posix())


def summary(path: Path, text: str) -> str | None:
    """First paragraph of the module docstring or of the file's leading comment block."""
    if path.suffix == ".py":
        try:
            doc = ast.get_docstring(ast.parse(text))
        except SyntaxError:
            doc = None
        if doc:
            return doc.strip().split("\n\n")[0].replace("\n", " ")
        lines = [ln[1:].strip() for ln in text.splitlines()[:6] if ln.startswith("#") and not ln.startswith("#!")]
        lines = [ln for ln in lines if ln and "coding" not in ln]
        return " ".join(lines) or None
    head = text.lstrip()[:600]
    for pat in (r"^/\*(.*?)\*/", r"^<!--(.*?)-->", r"^{#(.*?)#}"):
        m = re.match(pat, head, re.S)
        if m:
            return " ".join(m.group(1).split()) or None
    if path.suffix in (".js", ".mjs", ".yml", ".yaml", ".css"):
        lead = []
        for ln in text.splitlines():
            s = ln.strip()
            if s.startswith(("//", "#")):
                lead.append(s.lstrip("/# ").strip())
            else:
                break
        return " ".join(x for x in lead if x) or None
    if path.suffix == ".md":
        m = re.search(r"^#\s+(.+)$", text, re.M)
        return m.group(1).strip() if m else None
    return None


def slug(rel: str) -> str:
    """Flat, dot-free name for a file's JSON on the static site (GitHub Pages drops .github/ and similar)."""
    return re.sub(r"[^A-Za-z0-9]+", "-", rel).strip("-")


GROUPS = ["Django app (2016)", "Web interface and docs"]


def group(rel: str) -> str:
    """Which part of the repo a file belongs to (by location only)."""
    if rel.startswith(("blog/", "mysite/")) or rel in ("manage.py", ".gitignore", "LICENSE"):
        return "Django app (2016)"
    return "Web interface and docs"


def tree() -> dict:
    out, langs = [], {}
    for p in files():
        rel = p.relative_to(ROOT).as_posix()
        text = p.read_text(errors="replace")
        n = text.count("\n") + (0 if text.endswith("\n") or not text else 1)
        lang = LANG.get(p.suffix, "text")
        langs[lang] = langs.get(lang, 0) + n
        out.append({"path": rel, "slug": slug(rel), "lines": n, "bytes": p.stat().st_size, "lang": lang, "group": group(rel),
                    "summary": summary(p, text)})
    return {"files": out, "groups": GROUPS, "lines_by_lang": langs, "total_lines": sum(f["lines"] for f in out)}


def file(key: str) -> dict | None:
    """A file by its slug (or its repo-relative path)."""
    match = [p for p in files() if slug(p.relative_to(ROOT).as_posix()) == key or p.relative_to(ROOT).as_posix() == key]
    if not match:
        return None
    p = match[0]
    rel = p.relative_to(ROOT).as_posix()
    text = p.read_text(errors="replace")
    return {"path": rel, "slug": slug(rel), "lang": LANG.get(p.suffix, "text"), "text": redact(text),
            "summary": summary(p, text)}


def search(q: str, limit: int = 200) -> list[dict]:
    """Case-insensitive text search over every file (the static site does the same in the browser)."""
    q = q.lower()
    hits = []
    for p in files():
        rel = p.relative_to(ROOT).as_posix()
        for i, line in enumerate(redact(p.read_text(errors="replace")).splitlines(), 1):
            if q in line.lower():
                hits.append({"path": rel, "line": i, "text": line.strip()[:200]})
                if len(hits) >= limit:
                    return hits
    return hits
