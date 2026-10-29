# The Diary of a Data Scientist (Flask)

An A–Z glossary of data concepts. Server-rendered with Flask and Jinja, so every term has its own crawlable page.

## Run locally
    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    REPO_URL=https://github.com/you/your-repo flask --app app run --debug

## Deploy
    gunicorn app:app --bind 0.0.0.0:8000

Set `REPO_URL` (contribute links) and optionally `DB_PATH` (where the early-access SQLite database lives; use a persistent volume in production).

## Routes
- `/` home page with the A–Z glossary
- `/term/<slug>` one page per term
- `/api/terms` JSON feed of all terms
- `/subscribe` POST an email for early access
- `/sitemap.xml`, `/robots.txt`

## Contribute a term
Add an object to `data/terms.json` (term, level, definition, example, related) and open a pull request. The app validates the file on startup.

## Export signups
    sqlite3 instance/subscribers.db "select email, created_at from subscribers;"
