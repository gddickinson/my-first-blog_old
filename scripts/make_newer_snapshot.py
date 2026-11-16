"""Write web/data/newer_snapshot.json: the files of the newer version (gddickinson/my-first-blog) at a fixed commit,
for the "What changed" page. Hard-coded secret strings are redacted before they are stored.

Run: python scripts/make_newer_snapshot.py [--repo ../my-first-blog] [--commit 2aaf725]
(the commit is the newer repo's master before any web-interface work: the code as written in 2017).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from web.code_index import redact  # noqa: E402

OUT = ROOT / "web" / "data" / "newer_snapshot.json"


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(ROOT.parent / "my-first-blog"))
    ap.add_argument("--commit", default="2aaf725")
    a = ap.parse_args()
    full = git(a.repo, "rev-parse", a.commit).strip()
    files = {p: redact(git(a.repo, "show", f"{full}:{p}"))
             for p in git(a.repo, "ls-tree", "-r", "--name-only", full).split()}
    log = [line.split("|", 2) for line in git(a.repo, "log", "--reverse", "--format=%h|%aI|%s", full).splitlines()]
    old_log = [line.split("|", 2) for line in git(ROOT, "log", "--reverse", "--format=%h|%aI|%s", "master").splitlines()]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"repo": "gddickinson/my-first-blog", "commit": full, "short": full[:7],
                               "log": [{"sha": s, "date": d, "message": m} for s, d, m in log],
                               "old_log": [{"sha": s, "date": d, "message": m} for s, d, m in old_log],
                               "files": files}, indent=1, ensure_ascii=False) + "\n")
    print(f"wrote {OUT}: {len(files)} files at {full[:7]}")


if __name__ == "__main__":
    main()
