from __future__ import annotations

from pathlib import Path
import json
from typing import Any

from .config import load_settings
from .database import connect, enqueue_research, insert_articles, recent_articles, save_theme_run
from .feeds import fetch_feed
from .company_news import _recent
from .reporting import write_reports
from .scoring import score_theme


def run_pipeline(config_path: str, database_path: str, output_dir: str) -> dict[str, object]:
    settings = load_settings(config_path)
    connection = connect(database_path)
    articles = recent_articles(connection, limit=5000)
    from datetime import datetime, timedelta, timezone
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.lookback_days)
    articles = [article for article in articles if _recent(article, cutoff)]
    results = [score_theme(theme, articles) for theme in settings.themes]
    results = [result for result in results if result.article_count]
    queued = 0
    for result in results:
        save_theme_run(connection, result)
        if result.score >= settings.deep_research_score and enqueue_research(connection, result):
            queued += 1
    json_path, markdown_path = write_reports(results, output_dir)
    connection.close()
    return {
        "articles": len(articles),
        "themes": len(results),
        "alerts": sum(result.score >= settings.alert_score for result in results),
        "research_jobs": queued,
        "json_report": str(Path(json_path)),
        "markdown_report": str(Path(markdown_path)),
    }


def run_cycle(
    sources_path: str,
    config_path: str,
    database_path: str,
    output_dir: str,
) -> dict[str, Any]:
    source_data = json.loads(Path(sources_path).read_text(encoding="utf-8"))
    connection = connect(database_path)
    source_results: list[dict[str, Any]] = []
    total_inserted = 0
    total_duplicates = 0
    for source in source_data.get("sources", []):
        if not source.get("enabled", True):
            continue
        name = source["name"]
        try:
            articles = fetch_feed(source["url"], name, int(source.get("timeout", 20)))
            articles = articles[: int(source.get("max_items", 100))]
            inserted, duplicates = insert_articles(connection, articles)
            total_inserted += inserted
            total_duplicates += duplicates
            source_results.append(
                {
                    "name": name,
                    "status": "ok",
                    "fetched": len(articles),
                    "inserted": inserted,
                    "duplicates": duplicates,
                }
            )
        except Exception as exc:  # A failed source must not stop the monitoring cycle.
            source_results.append({"name": name, "status": "error", "error": str(exc)})
    connection.close()
    analysis = run_pipeline(config_path, database_path, output_dir)
    return {
        "sources": source_results,
        "inserted": total_inserted,
        "duplicates": total_duplicates,
        "analysis": analysis,
    }
