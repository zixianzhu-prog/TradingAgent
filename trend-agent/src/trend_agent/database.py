from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Iterable

from .models import Article, ThemeResult, utc_now


SCHEMA = """
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY,
    fingerprint TEXT NOT NULL UNIQUE,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    content TEXT NOT NULL,
    published_at TEXT NOT NULL,
    discovered_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_articles_discovered_at ON articles(discovered_at);
CREATE TABLE IF NOT EXISTS theme_runs (
    id INTEGER PRIMARY KEY,
    theme_name TEXT NOT NULL,
    run_at TEXT NOT NULL,
    score INTEGER NOT NULL,
    status TEXT NOT NULL,
    result_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research_queue (
    id INTEGER PRIMARY KEY,
    theme_name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    request_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research_results (
    id INTEGER PRIMARY KEY,
    queue_id INTEGER NOT NULL,
    theme_name TEXT NOT NULL,
    provider TEXT NOT NULL,
    created_at TEXT NOT NULL,
    report_path TEXT NOT NULL,
    report_text TEXT NOT NULL,
    FOREIGN KEY(queue_id) REFERENCES research_queue(id)
);
"""


def connect(path: str | Path) -> sqlite3.Connection:
    db_path = Path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    return connection


def fingerprint(article: Article) -> str:
    # SEC Atom entries often share generic titles such as "10-Q" across issuers.
    # Scope those fingerprints by issuer/source so one company's filing cannot
    # suppress another company's disclosure as a false duplicate.
    source_scope = article.source if article.source.lower().startswith("sec ") else ""
    normalized = " ".join(f"{source_scope} {article.title} {article.content}".lower().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def insert_articles(connection: sqlite3.Connection, articles: Iterable[Article]) -> tuple[int, int]:
    inserted = 0
    duplicates = 0
    for article in articles:
        try:
            connection.execute(
                """
                INSERT INTO articles (
                    fingerprint, source, title, url, content, published_at, discovered_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    fingerprint(article),
                    article.source,
                    article.title,
                    article.url,
                    article.content,
                    article.published_at,
                    article.discovered_at,
                ),
            )
            inserted += 1
        except sqlite3.IntegrityError:
            duplicates += 1
    connection.commit()
    return inserted, duplicates


def recent_articles(connection: sqlite3.Connection, limit: int = 500) -> list[Article]:
    rows = connection.execute(
        """
        SELECT source, title, url, content, published_at, discovered_at
        FROM articles ORDER BY discovered_at DESC LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [Article(**dict(row)) for row in rows]


def save_theme_run(connection: sqlite3.Connection, result: ThemeResult) -> None:
    connection.execute(
        "INSERT INTO theme_runs (theme_name, run_at, score, status, result_json) VALUES (?, ?, ?, ?, ?)",
        (result.name, utc_now(), result.score, result.status, json.dumps(result.as_dict(), ensure_ascii=False)),
    )
    connection.commit()


def enqueue_research(connection: sqlite3.Connection, result: ThemeResult) -> bool:
    existing = connection.execute(
        "SELECT 1 FROM research_queue WHERE theme_name = ? AND status = 'pending' LIMIT 1",
        (result.name,),
    ).fetchone()
    if existing:
        return False
    request = {
        "theme": result.name,
        "question": (
            f"Investigate the emerging theme '{result.label}'. Identify the causal chain, "
            "first- through third-order effects, supply-chain chokepoints, public companies, "
            "counter-evidence, and the next validation event. Cite every material claim."
        ),
        "evidence": list(result.evidence),
    }
    connection.execute(
        "INSERT INTO research_queue (theme_name, created_at, request_json) VALUES (?, ?, ?)",
        (result.name, utc_now(), json.dumps(request, ensure_ascii=False)),
    )
    connection.commit()
    return True


def enqueue_company_mapping(
    connection: sqlite3.Connection,
    theme_name: str,
    source_report: str,
    report_text: str,
) -> int:
    """Queue an evidence-first company map; this never creates an order."""
    request = {
        "theme": f"{theme_name}_company_map",
        "question": (
            "Convert the research below into an evidence-first public-company watchlist. "
            "Use fresh web research and prefer SEC filings, official investor-relations pages, "
            "government sources, and peer-reviewed literature. Include a company only when a "
            "specific product, revenue stream, manufacturing capability, or disclosed partnership "
            "creates direct exposure to the identified trend. For every candidate provide company "
            "name, US ticker and exchange, direct-exposure evidence with URL, causal mechanism, "
            "strongest counter-evidence, and next validation event. Exclude companies supported "
            "only by vague thematic association. End with a Markdown table whose exact columns are "
            "Ticker | Company | Exposure | Evidence URL | Counter-evidence | Validation event. "
            "This is a research watchlist, not a buy or sell recommendation.\n\n"
            f"Source report: {source_report}\n\n{report_text}"
        ),
        "evidence": [],
    }
    cursor = connection.execute(
        "INSERT INTO research_queue (theme_name, created_at, request_json) VALUES (?, ?, ?)",
        (
            f"{theme_name}_company_map",
            utc_now(),
            json.dumps(request, ensure_ascii=False),
        ),
    )
    connection.commit()
    return int(cursor.lastrowid)


def next_research_job(connection: sqlite3.Connection) -> dict[str, object] | None:
    row = connection.execute(
        "SELECT id, theme_name, request_json FROM research_queue WHERE status = 'pending' ORDER BY id LIMIT 1"
    ).fetchone()
    if row is None:
        return None
    updated = connection.execute(
        "UPDATE research_queue SET status = 'running' WHERE id = ? AND status = 'pending'",
        (row["id"],),
    )
    connection.commit()
    if updated.rowcount != 1:
        return None
    return {
        "id": int(row["id"]),
        "theme_name": str(row["theme_name"]),
        "request": json.loads(row["request_json"]),
    }


def complete_research_job(
    connection: sqlite3.Connection,
    queue_id: int,
    theme_name: str,
    provider: str,
    report_path: str,
    report_text: str,
) -> None:
    connection.execute(
        """
        INSERT INTO research_results (
            queue_id, theme_name, provider, created_at, report_path, report_text
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (queue_id, theme_name, provider, utc_now(), report_path, report_text),
    )
    connection.execute("UPDATE research_queue SET status = 'complete' WHERE id = ?", (queue_id,))
    connection.commit()


def fail_research_job(connection: sqlite3.Connection, queue_id: int) -> None:
    connection.execute("UPDATE research_queue SET status = 'failed' WHERE id = ?", (queue_id,))
    connection.commit()
