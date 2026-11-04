from __future__ import annotations

import argparse
import json
from pathlib import Path

from .database import connect, enqueue_company_mapping, insert_articles
from .company_news import build_company_news_report
from .feeds import article_from_change, fetch_feed, load_feed_file
from .pipeline import run_cycle, run_pipeline
from .theme_exposure import build_theme_stock_report
from .research import process_next_job
from .webhook import serve


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Continuous trend intelligence monitor")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init-db", help="Create the SQLite database")
    init.add_argument("--database", default="state/trends.db")

    feed = subparsers.add_parser("ingest-feed", help="Ingest an RSS or Atom feed")
    source = feed.add_mutually_exclusive_group(required=True)
    source.add_argument("--url")
    source.add_argument("--file")
    feed.add_argument("--source-name", required=True)
    feed.add_argument("--database", default="state/trends.db")

    change = subparsers.add_parser("ingest-change", help="Ingest a changedetection.io JSON payload")
    change.add_argument("payload")
    change.add_argument("--database", default="state/trends.db")

    run = subparsers.add_parser("run", help="Score themes and create reports")
    run.add_argument("--config", default="config.example.json")
    run.add_argument("--database", default="state/trends.db")
    run.add_argument("--output", default="reports")

    cycle = subparsers.add_parser("cycle", help="Fetch all configured sources, score themes, and write reports")
    cycle.add_argument("--sources", default="sources.example.json")
    cycle.add_argument("--config", default="config.example.json")
    cycle.add_argument("--database", default="state/trends.db")
    cycle.add_argument("--output", default="reports")

    webhook = subparsers.add_parser("serve-webhook", help="Receive changedetection.io webhook events")
    webhook.add_argument("--database", default="state/trends.db")
    webhook.add_argument("--host", default="127.0.0.1")
    webhook.add_argument("--port", type=int, default=8787)

    research = subparsers.add_parser("research-next", help="Process the next queued deep-research task")
    research.add_argument("--database", default="state/trends.db")
    research.add_argument("--output", default="reports/research")
    research.add_argument("--provider", choices=("brief", "gpt-researcher"), default="brief")

    mapping = subparsers.add_parser(
        "enqueue-company-map",
        help="Queue evidence-first public-company mapping from a completed trend report",
    )
    mapping.add_argument("report")
    mapping.add_argument("--theme", required=True)
    mapping.add_argument("--database", default="state/trends.db")

    company_scores = subparsers.add_parser(
        "company-scores",
        help="Score daily company relevance, source reliability, and news sentiment",
    )
    company_scores.add_argument("--database", default="state/trends.db")
    company_scores.add_argument("--companies", default="companies.example.json")
    company_scores.add_argument("--output", default="reports/company-news")
    company_scores.add_argument("--lookback-days", type=int, default=7)
    theme_stocks = subparsers.add_parser(
        "theme-stocks", help="Map broad trends to stocks through verified business exposure",
    )
    theme_stocks.add_argument("--trends", required=True)
    theme_stocks.add_argument("--mapping", default="theme-company-map.json")
    theme_stocks.add_argument("--output", default="reports/theme-stocks")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "init-db":
        connect(args.database).close()
        print(json.dumps({"database": args.database, "status": "ready"}))
        return
    if args.command == "ingest-feed":
        articles = fetch_feed(args.url, args.source_name) if args.url else load_feed_file(args.file, args.source_name)
        connection = connect(args.database)
        inserted, duplicates = insert_articles(connection, articles)
        connection.close()
        print(json.dumps({"fetched": len(articles), "inserted": inserted, "duplicates": duplicates}))
        return
    if args.command == "ingest-change":
        payload = json.loads(Path(args.payload).read_text(encoding="utf-8"))
        connection = connect(args.database)
        inserted, duplicates = insert_articles(connection, [article_from_change(payload)])
        connection.close()
        print(json.dumps({"inserted": inserted, "duplicates": duplicates}))
        return
    if args.command == "run":
        print(json.dumps(run_pipeline(args.config, args.database, args.output), indent=2))
        return
    if args.command == "cycle":
        print(json.dumps(run_cycle(args.sources, args.config, args.database, args.output), indent=2))
        return
    if args.command == "serve-webhook":
        serve(args.database, args.host, args.port)
        return
    if args.command == "research-next":
        print(json.dumps(process_next_job(args.database, args.output, args.provider), indent=2))
        return
    if args.command == "enqueue-company-map":
        report_path = Path(args.report)
        connection = connect(args.database)
        queue_id = enqueue_company_mapping(
            connection,
            args.theme,
            str(report_path),
            report_path.read_text(encoding="utf-8"),
        )
        connection.close()
        print(json.dumps({"status": "pending", "queue_id": queue_id, "theme": args.theme}))
        return
    if args.command == "company-scores":
        print(json.dumps(build_company_news_report(
            args.database,
            args.companies,
            args.output,
            args.lookback_days,
        ), indent=2))
        return
    if args.command == "theme-stocks":
        print(json.dumps(build_theme_stock_report(args.trends, args.mapping, args.output), indent=2))


if __name__ == "__main__":
    main()
