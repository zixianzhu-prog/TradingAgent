from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

from investment_scoring import calculate_scores

HORIZONS = (1, 5, 20, 60)


def connect(path: str) -> sqlite3.Connection:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(target)
    connection.row_factory = sqlite3.Row
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS predictions (
          ticker TEXT NOT NULL,
          as_of TEXT NOT NULL,
          price REAL NOT NULL,
          news_score INTEGER NOT NULL,
          relevance_score INTEGER NOT NULL,
          reliability_score INTEGER NOT NULL,
          sentiment REAL NOT NULL,
          technical_score INTEGER NOT NULL,
          kronos_score INTEGER NOT NULL,
          forecast_return REAL NOT NULL,
          combined_score INTEGER NOT NULL,
          confidence TEXT NOT NULL,
          serenity_decision TEXT NOT NULL,
          recorded_at TEXT NOT NULL,
          PRIMARY KEY (ticker, as_of)
        );
        CREATE TABLE IF NOT EXISTS outcomes (
          ticker TEXT NOT NULL,
          prediction_as_of TEXT NOT NULL,
          horizon INTEGER NOT NULL,
          target_as_of TEXT NOT NULL,
          target_price REAL NOT NULL,
          realized_return REAL NOT NULL,
          direction_correct INTEGER NOT NULL,
          evaluated_at TEXT NOT NULL,
          PRIMARY KEY (ticker, prediction_as_of, horizon)
        );
        CREATE TABLE IF NOT EXISTS prediction_cohorts (
          ticker TEXT NOT NULL,
          as_of TEXT NOT NULL,
          cohort TEXT NOT NULL,
          PRIMARY KEY (ticker, as_of, cohort)
        );
        """
    )
    return connection


def latest_report(directory: str) -> Path:
    reports = sorted(Path(directory).glob("run-*.json"), key=lambda path: path.stat().st_mtime)
    if not reports:
        raise SystemExit(f"No market report found in {directory}")
    return reports[-1]


def record_cohort_history(connection: sqlite3.Connection, directory: str, cohort: str) -> int:
    """Recover cohort labels from immutable historical market-run artifacts."""
    inserted = 0
    for path in sorted(Path(directory).glob("run-*.json")):
        market = json.loads(path.read_text(encoding="utf-8"))
        for item in market.get("results", []):
            signal = item.get("signal", {})
            ticker, as_of = signal.get("ticker"), signal.get("as_of")
            if not ticker or not as_of:
                continue
            exists = connection.execute(
                "SELECT 1 FROM predictions WHERE ticker=? AND as_of=?", (ticker, as_of)
            ).fetchone()
            if not exists:
                continue
            before = connection.total_changes
            connection.execute(
                "INSERT OR IGNORE INTO prediction_cohorts (ticker, as_of, cohort) VALUES (?, ?, ?)",
                (ticker, as_of, cohort),
            )
            inserted += connection.total_changes - before
    connection.commit()
    return inserted


def record_predictions(connection: sqlite3.Connection, market: dict[str, Any], news: dict[str, Any], serenity: dict[str, Any], theme_stocks: dict[str, Any] | None = None, cohort: str = "general") -> int:
    news_by_ticker = {item["ticker"]: item for item in news.get("companies", [])}
    for item in (theme_stocks or {}).get("companies", []):
        news_by_ticker.setdefault(item["ticker"], {
            "ticker": item["ticker"],
            "news_score": item.get("transmission_score", 0),
            "relevance_score": round(float(item.get("exposure_strength", 0)) * 100),
            "reliability_score": 100 if item.get("evidence_status") == "confirmed" else 50,
            "sentiment": 0.0,
            "confidence": "high" if item.get("decision") == "deep-research" else "medium",
        })
    serenity_by_ticker = {item["ticker"]: item for item in serenity.get("companies", [])}
    recorded_at = datetime.now(timezone.utc).isoformat()
    count = 0
    for item in market["results"]:
        signal = item["signal"]
        ticker = signal["ticker"]
        company_news = news_by_ticker.get(ticker, {})
        forecast_return = float(market.get("kronos", {}).get(ticker, {}).get("forecast_return", 0.0))
        scores = calculate_scores(signal, forecast_return, company_news)
        before = connection.total_changes
        connection.execute(
            """
            INSERT INTO predictions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(ticker, as_of) DO NOTHING
            """,
            (
                ticker, signal["as_of"], float(signal["price"]), scores["news"],
                int(company_news.get("relevance_score", 0)), int(company_news.get("reliability_score", 0)),
                float(company_news.get("sentiment", 0.0)), scores["technical"], scores["kronos"],
                forecast_return, scores["combined"], company_news.get("confidence", "insufficient"),
                serenity_by_ticker.get(ticker, {}).get("serenity_decision", "unreviewed"), recorded_at,
            ),
        )
        count += connection.total_changes - before
        connection.execute(
            "INSERT OR IGNORE INTO prediction_cohorts (ticker, as_of, cohort) VALUES (?, ?, ?)",
            (ticker, signal["as_of"], cohort),
        )
    connection.commit()
    return count


def backfill_outcomes(connection: sqlite3.Connection) -> int:
    inserted = 0
    tickers = [row[0] for row in connection.execute("SELECT DISTINCT ticker FROM predictions")]
    evaluated_at = datetime.now(timezone.utc).isoformat()
    for ticker in tickers:
        rows = connection.execute(
            "SELECT * FROM predictions WHERE ticker=? ORDER BY as_of", (ticker,)
        ).fetchall()
        for index, prediction in enumerate(rows):
            for horizon in HORIZONS:
                target_index = index + horizon
                if target_index >= len(rows):
                    continue
                target = rows[target_index]
                realized = float(target["price"]) / float(prediction["price"]) - 1.0
                forecast = float(prediction["forecast_return"])
                correct = int((forecast >= 0 and realized >= 0) or (forecast < 0 and realized < 0))
                before = connection.total_changes
                connection.execute(
                    "INSERT OR IGNORE INTO outcomes VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (ticker, prediction["as_of"], horizon, target["as_of"], float(target["price"]),
                     realized, correct, evaluated_at),
                )
                inserted += connection.total_changes - before
    connection.commit()
    return inserted


def build_report(connection: sqlite3.Connection, output: str) -> None:
    predictions = connection.execute("SELECT * FROM predictions ORDER BY as_of DESC, ticker").fetchall()
    lines = [
        "# 投资评分样本外跟踪", "",
        f"生成时间：{datetime.now(timezone.utc).isoformat()}", "",
        "> 每日预测按当时信息冻结保存；未来收益只能由之后的独立交易日观察值回填。", "",
        f"- 已记录预测：{len(predictions)}", f"- 股票数：{len(set(row['ticker'] for row in predictions))}", "",
        "## 最新冻结评分", "",
        "| 日期 | 股票 | 收盘价 | 新闻 | 技术 | Kronos | 综合 | Serenity |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in predictions[:20]:
        lines.append(
            f"| {row['as_of']} | {row['ticker']} | {row['price']:.2f} | {row['news_score']} | "
            f"{row['technical_score']} | {row['kronos_score']} | {row['combined_score']} | {row['serenity_decision']} |"
        )
    lines.extend(["", "## 未来表现回填", "",
                  "| 后续交易观察点 | 已完成样本 | 平均收益 | 方向命中率 | 高分组平均收益 | 低分组平均收益 | Serenity通过组 |",
                  "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |"])
    for horizon in HORIZONS:
        rows = connection.execute(
            """SELECT o.realized_return, o.direction_correct, p.combined_score, p.serenity_decision
               FROM outcomes o JOIN predictions p
               ON p.ticker=o.ticker AND p.as_of=o.prediction_as_of
               WHERE o.horizon=?""", (horizon,)
        ).fetchall()
        returns = [float(row["realized_return"]) for row in rows]
        high = [float(row["realized_return"]) for row in rows if row["combined_score"] >= 70]
        low = [float(row["realized_return"]) for row in rows if row["combined_score"] < 70]
        serenity_ready = [float(row["realized_return"]) for row in rows if row["serenity_decision"] == "research-ready"]
        fmt = lambda values: f"{mean(values):+.2%}" if values else "等待数据"
        hit = f"{mean([row['direction_correct'] for row in rows]):.1%}" if rows else "等待数据"
        lines.append(
            f"| {horizon} | {len(rows)} | {fmt(returns)} | {hit} | {fmt(high)} | {fmt(low)} | {fmt(serenity_ready)} |"
        )
    lines.extend(["", "高分组定义为综合分≥70。样本量不足时不得据此调整权重或宣称有效。", ""])
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze daily scores and backfill future returns")
    parser.add_argument("--market-dir", required=True)
    parser.add_argument("--news-report", required=True)
    parser.add_argument("--serenity-assessment", required=True)
    parser.add_argument("--theme-stock-report")
    parser.add_argument("--database", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--cohort", default="general")
    args = parser.parse_args()
    market = json.loads(latest_report(args.market_dir).read_text(encoding="utf-8"))
    news = json.loads(Path(args.news_report).read_text(encoding="utf-8"))
    serenity = json.loads(Path(args.serenity_assessment).read_text(encoding="utf-8"))
    theme_stocks = json.loads(Path(args.theme_stock_report).read_text(encoding="utf-8")) if args.theme_stock_report else None
    connection = connect(args.database)
    recorded = record_predictions(connection, market, news, serenity, theme_stocks, args.cohort)
    cohort_labels = record_cohort_history(connection, args.market_dir, args.cohort)
    backfilled = backfill_outcomes(connection)
    build_report(connection, args.output)
    connection.close()
    print(json.dumps({"recorded": recorded, "cohortLabels": cohort_labels, "backfilled": backfilled, "report": args.output}))


if __name__ == "__main__":
    main()
