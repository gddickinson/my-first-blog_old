# Session log

## 2026-11-13: showcase web interface (web-interface branch)
- SECRET_KEY moved from mysite/settings.py to the DJANGO_SECRET_KEY env var (old key still in git history;
  George decides on purge).
- Added a showcase site (port 8257): How it works, What changed (diff against my-first-blog at d6b519a, from
  web/data/newer_snapshot.json), code explorer, About with a pointer to my-first-blog. The 2016 code (Django 1.9)
  is not run.
