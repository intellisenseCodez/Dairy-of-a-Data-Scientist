"""The Diary of a Data Scientist: a Flask app serving an A–Z glossary."""
import json
import os
import re
import sqlite3
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, Response, abort, jsonify, render_template, request, url_for

BASE = Path(__file__).parent
LEVELS = ("Beginner", "Intermediate", "Advanced")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

app = Flask(__name__, instance_path=str(BASE / "instance"))
app.config["REPO_URL"] = os.environ.get(
    "REPO_URL", "https://github.com/intellisenseCodez/Dairy-of-a-Data-Scientist"
)
# app.config["DB_PATH"] = os.environ.get("DB_PATH", str(BASE / "instance" / "subscribers.db"))


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def load_terms():
    """Read data/terms.json, validate it, and add slugs and cross-links."""
    raw = json.loads((BASE / "data" / "terms.json").read_text(encoding="utf-8"))
    terms = []
    for row in raw:
        if row["level"] not in LEVELS:
            raise ValueError(f'{row["term"]}: level must be one of {LEVELS}')
        terms.append({**row, "slug": slugify(row["term"])})
    terms.sort(key=lambda t: t["term"].lower())
    by_name = {t["term"]: t for t in terms}
    if len(by_name) != len(terms):
        raise ValueError("Duplicate term names in terms.json")
    for t in terms:
        missing = [r for r in t["related"] if r not in by_name]
        if missing:
            app.logger.warning("%s lists unknown related terms: %s", t["term"], missing)
        t["related_terms"] = [by_name[r] for r in t["related"] if r in by_name]
    return terms


TERMS = load_terms()
BY_SLUG = {t["slug"]: t for t in TERMS}


@app.context_processor
def inject_globals():
    return {"repo_url": app.config["REPO_URL"], "year": datetime.now().year}


@app.route("/")
def index():
    groups = OrderedDict()
    for t in TERMS:
        groups.setdefault(t["term"][0].upper(), []).append(t)
    letters = [(L, L in groups) for L in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
    return render_template(
        "index.html", groups=groups, letters=letters, total=len(TERMS), levels=LEVELS
    )


@app.route("/term/<slug>")
def term(slug):
    t = BY_SLUG.get(slug)
    if t is None:
        abort(404)
    i = TERMS.index(t)
    return render_template(
        "term.html",
        t=t,
        letter=t["term"][0].upper(),
        prev=TERMS[i - 1] if i > 0 else None,
        next=TERMS[i + 1] if i < len(TERMS) - 1 else None,
    )


@app.route("/api/terms")
def api_terms():
    """Read-only JSON feed of the glossary (handy for a future app or quiz tool)."""
    return jsonify(
        [{k: t[k] for k in ("slug", "term", "level", "definition", "example", "related")} for t in TERMS]
    )


# --- early access signups ---------------------------------------------------
def db():
    Path(app.config["DB_PATH"]).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(app.config["DB_PATH"])
    conn.execute(
        "CREATE TABLE IF NOT EXISTS subscribers (email TEXT PRIMARY KEY, created_at TEXT NOT NULL)"
    )
    return conn


@app.post("/subscribe")
def subscribe():
    pass
    # data = request.get_json(silent=True) or request.form
    # email = (data.get("email") or "").strip().lower()
    # if not EMAIL_RE.match(email) or len(email) > 254:
    #     return jsonify(ok=False, message="Please enter a valid email address."), 400
    # with db() as conn:
    #     conn.execute(
    #         "INSERT OR IGNORE INTO subscribers (email, created_at) VALUES (?, ?)",
    #         (email, datetime.now(timezone.utc).isoformat()),
    #     )
    # return jsonify(ok=True, message="Thanks. You are on the list.")


# --- SEO --------------------------------------------------------------------
@app.route("/sitemap.xml")
def sitemap():
    urls = [url_for("index", _external=True)] + [
        url_for("term", slug=t["slug"], _external=True) for t in TERMS
    ]
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    xml += [f"<url><loc>{u}</loc></url>" for u in urls]
    xml.append("</urlset>")
    return Response("\n".join(xml), mimetype="application/xml")


@app.route("/robots.txt")
def robots():
    body = f"User-agent: *\nAllow: /\nSitemap: {url_for('sitemap', _external=True)}\n"
    return Response(body, mimetype="text/plain")


@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
