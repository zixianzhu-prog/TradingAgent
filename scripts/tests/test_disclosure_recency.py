import sqlite3
from datetime import date

from disclosure_conflict_agent import load_articles as load_divergence_articles
from event_revalidation_agent import load_articles as load_event_articles


def test_old_backfilled_article_is_evidence_not_new_event(tmp_path):
    database = tmp_path / "news.db"
    connection = sqlite3.connect(database)
    connection.execute(
        "CREATE TABLE articles (source TEXT,title TEXT,url TEXT,content TEXT,published_at TEXT,discovered_at TEXT)"
    )
    connection.executemany(
        "INSERT INTO articles VALUES (?,?,?,?,?,?)",
        [
            ("SEC TEST Filings", "Old 10-K", "old", "", "2025-02-01T12:00:00Z", "2026-11-09T12:00:00Z"),
            ("SEC TEST Filings", "New 10-Q", "new", "", "2026-11-08T12:00:00Z", "2026-11-09T12:00:00Z"),
        ],
    )
    connection.commit()
    connection.close()
    assert [row["url"] for row in load_event_articles(str(database), 7, date(2026, 11, 9))] == ["new"]
    assert [row["url"] for row in load_divergence_articles(str(database), 7, date(2026, 11, 9))] == ["new"]
