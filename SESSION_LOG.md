# Session log

## 2026-11-13: showcase web interface (web-interface branch)
- SECRET_KEY moved from mysite/settings.py to the DJANGO_SECRET_KEY env var (old key still in git history;
  George decides on purge).
- Added a showcase site (port 8257): How it works, What changed (diff against my-first-blog at d6b519a, from
  web/data/newer_snapshot.json), code explorer, About with a pointer to my-first-blog. The 2016 code (Django 1.9)
  is not run.

## 2026-11-16: old SECRET_KEY purged from git history
- The Django SECRET_KEY once committed in mysite/settings.py was replaced by `REDACTED_OLD_SECRET_KEY` in every
  commit (git-filter-repo --replace-text; George's request). Current files unchanged (same tree), same commit count,
  new commit hashes. The key is now read from the DJANGO_SECRET_KEY environment variable.
- Pre-rewrite mirror kept on the FANTOM backup drive (history_rewrite_2026-11-16). Treat the old key as compromised:
  rotate it on any server that used it. Older clones and GitHub's cached views of old commit SHAs may still hold it.
