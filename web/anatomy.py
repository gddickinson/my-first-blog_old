"""How the 2016 version works, read from its code: URL pattern -> view -> template, plus the model it defines.
Every item carries its file and line. No Django import is needed (the code targets Django 1.9)."""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _src(rel):
    return (ROOT / rel).read_text()


def urls():
    out = []
    for rel in ("mysite/urls.py", "blog/urls.py"):
        for n in ast.walk(ast.parse(_src(rel))):
            if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "url" and len(n.args) >= 2:
                out.append({"file": rel, "line": n.lineno, "regex": n.args[0].value,
                            "target": ast.unparse(n.args[1]), "name": next((k.value.value for k in n.keywords if k.arg == "name"), None)})
    return out


def views():
    src = _src("blog/views.py")
    return [{"name": n.name, "line": n.lineno, "source": ast.get_source_segment(src, n),
             "templates": [c.value for c in ast.walk(n) if isinstance(c, ast.Constant) and str(c.value).endswith(".html")],
             "context": next((ast.unparse(c.args[2]) for c in ast.walk(n) if isinstance(c, ast.Call)
                              and getattr(c.func, "id", "") == "render" and len(c.args) > 2), None)}
            for n in ast.parse(src).body if isinstance(n, ast.FunctionDef)]


def templates():
    out = []
    for p in sorted((ROOT / "blog" / "templates").rglob("*.html")):
        text = p.read_text()
        out.append({"file": p.relative_to(ROOT).as_posix(), "html": text,
                    "template_tags": len(re.findall(r"{%|{{", text)),
                    "headings": [(i, m) for i, line in enumerate(text.splitlines(), 1) for m in re.findall(r"<h2><a[^>]*>(.*?)</a>", line)],
                    "dates": re.findall(r"published: ([^<]+)", text)})
    return out


def model():
    rel = "blog/models.py"
    src = _src(rel)
    cls = next(n for n in ast.parse(src).body if isinstance(n, ast.ClassDef))
    fields = [{"name": n.targets[0].id, "line": n.lineno, "decl": ast.get_source_segment(src, n.value)}
              for n in cls.body if isinstance(n, ast.Assign)]
    used_by_views = "Post" in _src("blog/views.py")
    return {"file": rel, "name": cls.name, "line": cls.lineno, "fields": fields,
            "methods": [{"name": n.name, "line": n.lineno} for n in cls.body if isinstance(n, ast.FunctionDef)],
            "used_by_views": used_by_views}


def anatomy():
    return {"urls": urls(), "views": views(), "templates": templates(), "model": model()}
