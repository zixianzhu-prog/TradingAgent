"""Backfill historical bioRxiv/medRxiv preprints into a replay article database.

Used for "time machine" replays of the emerging-signal detector: each preprint is
stored with its posting date as both published and discovered time, because that
is when it became public. The database has the same ``articles`` table as the
live news database, so the detector reads it unchanged.

Example (COVID replay):
    python scripts/backfill_preprints.py --start 2019-11-01 --end 2020-02-15 \
        --database state/replay/covid-2020.db
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.biorxiv.org/details"
DEFAULT_BIORXIV_CATEGORIES = ("microbiology", "immunology", "genomics", "bioinformatics", "evolutionary biology")
SCHEMA = """
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY, fingerprint TEXT NOT NULL UNIQUE, source TEXT NOT NULL, title TEXT NOT NULL,
    url TEXT NOT NULL, content TEXT NOT NULL, published_at TEXT NOT NULL, discovered_at TEXT NOT NULL
);
"""


def fetch_json(url: str, retries: int = 3) -> dict:
    system_ca = Path("/etc/ssl/cert.pem")
    context = ssl.create_default_context(cafile=str(system_ca) if system_ca.exists() else None)
    request = urllib.request.Request(url, headers={"User-Agent": "FocusKPI-Research-Agent/0.1"})
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=40, context=context) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception:
            if attempt == retries:
                raise
            time.sleep(2 * (attempt + 1))
    return {}


def iterate(server: str, start: str, end: str, category: str | None = None, fetch=fetch_json):
    cursor = 0
    while True:
        suffix = f"?{urllib.parse.urlencode({'category': category})}" if category else ""
        payload = fetch(f"{API}/{server}/{start}/{end}/{cursor}{suffix}")
        rows = payload.get("collection", [])
        yield from rows
        total = int((payload.get("messages") or [{}])[0].get("total", 0) or 0)
        cursor += len(rows)
        if not rows or cursor >= total:
            break
        time.sleep(0.3)


def store(connection: sqlite3.Connection, server: str, row: dict) -> bool:
    doi = row.get("doi", "")
    # Revisions share a DOI; keep the first posting only, because that is when the work became public.
    fingerprint = hashlib.sha256(f"{server}|{doi}".encode()).hexdigest()
    posted = f"{row.get('date')}T00:00:00+00:00"
    try:
        connection.execute(
            "INSERT INTO articles (fingerprint, source, title, url, content, published_at, discovered_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (fingerprint, "medRxiv" if server == "medrxiv" else "bioRxiv", row.get("title", ""), f"https://doi.org/{doi}",
             (row.get("abstract") or "")[:600], posted, posted),
        )
        return True
    except sqlite3.IntegrityError:
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill historical preprints for detector replays")
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--database", required=True)
    parser.add_argument("--biorxiv-category", action="append", help="bioRxiv category (repeatable); default: microbiology-related set")
    args = parser.parse_args()
    Path(args.database).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(args.database)
    connection.executescript(SCHEMA)
    counts = {}
    plan = [("medrxiv", None)] + [("biorxiv", c) for c in (args.biorxiv_category or DEFAULT_BIORXIV_CATEGORIES)]
    for server, category in plan:
        inserted = sum(store(connection, server, row) for row in iterate(server, args.start, args.end, category))
        connection.commit()
        counts[f"{server}:{category or 'all'}"] = inserted
    connection.close()
    print(json.dumps({"database": args.database, "inserted": counts}))


if __name__ == "__main__":
    main()
