from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


MARKET_DIRS = (
    ("core-biotech", "outputs/daily-market"),
    ("robotics-automation", "outputs/theme-market"),
    ("ai-data-center-power", "outputs/power-theme-market"),
    ("ai-medicine", "outputs/ai-medicine-market"),
)

KEY_REPORTS = (
    "outputs/daily-investment-agent.md",
    "outputs/hidden-gems.md",
    "outputs/market-profile-audit.md",
    "outputs/ai-medicine-5-10-year-thesis.md",
    "outputs/serenity-gate-audit.md",
    "outputs/event-revalidation-queue.md",
    "outputs/finrobot-event-analysis.md",
    "outputs/agent-benchmark-validation.md",
    "outputs/ai-medicine-thesis-memory.md",
    "outputs/scientific-frontier.md",
    "outputs/science-commercialization-graph.md",
    "outputs/technology-ownership.md",
    "outputs/uspto-assignment-validation.md",
    "outputs/institutional-ownership.md",
    "outputs/management-radar.md",
    "dashboard/dist/data.json",
)


def rows(connection: sqlite3.Connection, query: str, params=()) -> list[dict]:
    return [dict(row) for row in connection.execute(query, params).fetchall()]


def build(root: Path, news_db: Path, score_db: Path) -> dict:
    news = sqlite3.connect(news_db)
    news.row_factory = sqlite3.Row
    scores = sqlite3.connect(score_db)
    scores.row_factory = sqlite3.Row
    article_dates = rows(news, """SELECT substr(discovered_at,1,10) AS day, COUNT(*) AS articles,
        COUNT(DISTINCT source) AS sources FROM articles GROUP BY day ORDER BY day""")
    theme_dates = rows(news, """SELECT substr(run_at,1,10) AS day, COUNT(*) AS themeRows,
        COUNT(DISTINCT theme_name) AS themes FROM theme_runs GROUP BY day ORDER BY day""")
    prediction_dates = rows(scores, """SELECT as_of AS day, COUNT(*) AS predictions,
        COUNT(DISTINCT ticker) AS tickers FROM predictions GROUP BY as_of ORDER BY as_of""")
    cohorts = rows(scores, """SELECT cohort, COUNT(*) AS predictions,
        COUNT(DISTINCT as_of) AS independentDates, COUNT(DISTINCT ticker) AS tickers
        FROM prediction_cohorts GROUP BY cohort ORDER BY cohort""")
    outcomes = rows(scores, """SELECT horizon, COUNT(*) AS samples,
        COUNT(DISTINCT prediction_as_of) AS independentDates FROM benchmark_outcomes
        GROUP BY horizon ORDER BY horizon""")
    raw_runs = []
    for cohort, relative in MARKET_DIRS:
        files = sorted((root / relative).glob("run-*.json"))
        market_dates: dict[str, int] = {}
        for path in files:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                dates = {item.get("signal", {}).get("as_of") for item in payload.get("results", [])}
                for day in dates - {None}:
                    market_dates[day] = market_dates.get(day, 0) + 1
            except (OSError, json.JSONDecodeError):
                pass
        raw_runs.append({"cohort": cohort, "directory": relative, "files": len(files), "marketDates": market_dates})
    reports = []
    for relative in KEY_REPORTS:
        path = root / relative
        reports.append({
            "path": relative,
            "exists": path.is_file(),
            "updatedAt": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat() if path.is_file() else None,
            "bytes": path.stat().st_size if path.is_file() else 0,
        })
    news.close()
    scores.close()
    latest_prediction = prediction_dates[-1]["day"] if prediction_dates else None
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "storage": {
            "newsDatabase": str(news_db.relative_to(root)),
            "scoreDatabase": str(score_db.relative_to(root)),
            "newsArticles": sum(row["articles"] for row in article_dates),
            "frozenPredictions": sum(row["predictions"] for row in prediction_dates),
            "independentMarketDates": len(prediction_dates),
            "latestPredictionMarketDate": latest_prediction,
        },
        "articleDates": article_dates,
        "themeRunDates": theme_dates,
        "predictionDates": prediction_dates,
        "cohorts": cohorts,
        "benchmarkOutcomes": outcomes,
        "rawRuns": raw_runs,
        "reports": reports,
        "integrityRules": [
            "Raw run files preserve every execution, including retries on the same market date.",
            "Frozen predictions use ticker + market date as the primary key, so retries cannot rewrite the first prediction.",
            "An execution day is not counted as a new independent prediction day unless the market as_of date changes.",
            "Future outcomes are stored separately and never overwrite the original prediction.",
        ],
    }


def render(payload: dict) -> str:
    storage = payload["storage"]
    lines = [
        "# 每日运行数据台账", "",
        f"生成时间：{payload['generatedAt']}", "",
        "> 原始运行可以重复保存，但冻结预测按股票和市场日期去重。重复运行不会伪造新的独立预测样本。", "",
        "## 总览", "",
        f"- 新闻原始记录：**{storage['newsArticles']}** 条",
        f"- 冻结预测：**{storage['frozenPredictions']}** 条",
        f"- 独立市场日期：**{storage['independentMarketDates']}** 天",
        f"- 最新预测对应市场日：**{storage['latestPredictionMarketDate'] or '—'}**", "",
        "## 新闻入库日期", "", "| 发现日期 | 新入库文章 | 来源数 |", "|---|---:|---:|",
    ]
    for row in payload["articleDates"]:
        lines.append(f"| {row['day']} | {row['articles']} | {row['sources']} |")
    lines += ["", "## 冻结预测日期", "", "| 市场日期 | 预测数 | 股票数 |", "|---|---:|---:|"]
    for row in payload["predictionDates"]:
        lines.append(f"| {row['day']} | {row['predictions']} | {row['tickers']} |")
    lines += ["", "## 分主题样本", "", "| 队列 | 冻结记录 | 独立日期 | 股票数 |", "|---|---:|---:|---:|"]
    for row in payload["cohorts"]:
        lines.append(f"| {row['cohort']} | {row['predictions']} | {row['independentDates']} | {row['tickers']} |")
    lines += ["", "## 未来表现回填", "", "| 周期 | 已回填样本 | 独立预测日 |", "|---:|---:|---:|"]
    for row in payload["benchmarkOutcomes"]:
        lines.append(f"| {row['horizon']} | {row['samples']} | {row['independentDates']} |")
    lines += ["", "## 原始运行文件", "", "| 队列 | 文件数 | 文件中的市场日期 |", "|---|---:|---|"]
    for row in payload["rawRuns"]:
        dates = ", ".join(f"{day} ({count}次)" for day, count in sorted(row["marketDates"].items())) or "—"
        lines.append(f"| {row['cohort']} | {row['files']} | {dates} |")
    lines += ["", "## 主要报告", ""]
    for row in payload["reports"]:
        lines.append(f"- {'✅' if row['exists'] else '❌'} `{row['path']}` · {row['updatedAt'] or 'missing'}")
    lines += ["", "## 数据完整性规则", ""]
    for rule in payload["integrityRules"]:
        lines.append(f"- {rule}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Inventory persisted daily research and prediction data")
    parser.add_argument("--root", default=".")
    parser.add_argument("--news-db", default="trend-agent/state/daily-news.db")
    parser.add_argument("--score-db", default="state/investment-score-history.db")
    parser.add_argument("--json-output", default="state/daily-data-inventory.json")
    parser.add_argument("--markdown-output", default="outputs/daily-data-inventory.md")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    payload = build(root, root / args.news_db, root / args.score_db)
    json_path, markdown_path = root / args.json_output, root / args.markdown_output
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    markdown_path.write_text(render(payload), encoding="utf-8")
    print(json.dumps(payload["storage"], ensure_ascii=False))


if __name__ == "__main__":
    main()
