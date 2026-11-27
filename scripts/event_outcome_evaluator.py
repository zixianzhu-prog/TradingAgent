"""Evaluate frozen news-event hypotheses without confusing them with Serenity or Kronos.

Only explicit positive/negative calls are eligible. Consecutive repeats for the
same ticker and direction are collapsed into one episode, so a headline that
persists for several daily runs cannot inflate the sample. The first objective
label is 20-session excess return versus XBI; it is a market-response label, not
proof that the company's fundamentals improved.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path
from statistics import mean

MIN_CONFIDENCE = 50.0
EPISODE_GAP_DAYS = 5


def collapse_episodes(rows: list[dict], gap_days: int = EPISODE_GAP_DAYS) -> list[dict]:
    episodes: list[dict] = []
    last_by_ticker: dict[str, dict] = {}
    for row in sorted(rows, key=lambda x: (x["as_of"], x["ticker"])):
        previous = last_by_ticker.get(row["ticker"])
        same_episode = bool(
            previous
            and previous["claim"] == row["claim"]
            and (date.fromisoformat(row["as_of"]) - date.fromisoformat(previous["last_as_of"])).days <= gap_days
        )
        if same_episode:
            previous["last_as_of"] = row["as_of"]
            previous["repeat_count"] += 1
            previous["max_confidence"] = max(previous["max_confidence"], row["confidence_score"] or 0.0)
            continue
        episode = {
            "ticker": row["ticker"],
            "as_of": row["as_of"],
            "last_as_of": row["as_of"],
            "claim": row["claim"],
            "signal": row["numeric_value"],
            "confidence": row["confidence_score"] or 0.0,
            "max_confidence": row["confidence_score"] or 0.0,
            "repeat_count": 1,
        }
        episodes.append(episode)
        last_by_ticker[row["ticker"]] = episode
    return episodes


def evaluate(connection: sqlite3.Connection) -> dict:
    connection.row_factory = sqlite3.Row
    rows = [dict(row) for row in connection.execute(
        """SELECT ticker, as_of, claim, numeric_value, confidence_score
           FROM prediction_tasks
           WHERE task_type='event_impact' AND claim IN ('positive','negative')
           ORDER BY as_of, ticker"""
    )]
    episodes = collapse_episodes(rows)
    # Eligibility uses the confidence frozen on the episode's first day; later repeats are information from after as_of.
    eligible = [row for row in episodes if row["confidence"] >= MIN_CONFIDENCE]
    has_outcomes = connection.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='benchmark_outcomes'"
    ).fetchone()[0]
    scored = []
    if has_outcomes:
        for episode in eligible:
            outcome = connection.execute(
                """SELECT target_as_of, realized_return, excess_xbi
                   FROM benchmark_outcomes
                   WHERE ticker=? AND prediction_as_of=? AND horizon=20""",
                (episode["ticker"], episode["as_of"]),
            ).fetchone()
            if not outcome or outcome["excess_xbi"] is None:  # no XBI price for that window: not scorable
                continue
            excess = float(outcome["excess_xbi"])
            correct = (episode["claim"] == "positive" and excess > 0) or (episode["claim"] == "negative" and excess < 0)
            scored.append({**episode, "target_as_of": outcome["target_as_of"],
                           "realized_return": float(outcome["realized_return"]),
                           "excess_xbi": excess, "direction_correct": bool(correct)})
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "method": {
            "label": "20-session excess return versus XBI",
            "boundary": "market response only; not proof of fundamental improvement",
            "episodeGapDays": EPISODE_GAP_DAYS,
            "minimumConfidence": MIN_CONFIDENCE,
            "neutralCallsScored": False,
        },
        "summary": {
            "rawDirectionalCalls": len(rows),
            "independentEpisodes": len(episodes),
            "eligibleEpisodes": len(eligible),
            "maturedEpisodes": len(scored),
            "hitRate": mean(row["direction_correct"] for row in scored) if scored else None,
            "averageExcessXbi": mean(row["excess_xbi"] for row in scored) if scored else None,
            "status": "insufficient-sample" if len(scored) < 30 else "measurable-not-yet-validated",
        },
        "episodes": episodes,
        "scored": scored,
    }


def write_report(payload: dict, path: Path) -> None:
    s = payload["summary"]
    lines = [
        "# 新闻事件预测验证", "",
        f"生成时间：{payload['generatedAt']}", "",
        "> 新闻事件与 Serenity 长期质量、Kronos 价格方向分开评价。20日相对XBI表现只是市场反应标签，不代表基本面已改善。", "",
        f"- 原始正负方向记录：{s['rawDirectionalCalls']}",
        f"- 去重后的独立事件：{s['independentEpisodes']}",
        f"- 达到可靠度门槛（≥{MIN_CONFIDENCE:.0f}）：{s['eligibleEpisodes']}",
        f"- 已成熟20个交易日：{s['maturedEpisodes']}",
        f"- 当前状态：{s['status']}", "",
        "## 独立事件台账", "",
        "| 股票 | 首次冻结 | 最后出现 | 方向 | 冻结时可靠度 | 合并记录 | 20日结果 |",
        "| --- | --- | --- | --- | ---: | ---: | --- |",
    ]
    scored = {(row["ticker"], row["as_of"]): row for row in payload["scored"]}
    for row in payload["episodes"]:
        outcome = scored.get((row["ticker"], row["as_of"]))
        result = "等待成熟"
        if outcome:
            result = f"{'命中' if outcome['direction_correct'] else '未命中'}；相对XBI {outcome['excess_xbi']:+.2%}"
        elif row["confidence"] < MIN_CONFIDENCE:
            result = "低可靠度，仅记录不计分"
        lines.append(f"| {row['ticker']} | {row['as_of']} | {row['last_as_of']} | {row['claim']} | {row['confidence']:.0f} | {row['repeat_count']} | {result} |")
    lines.extend(["", "至少30个成熟独立事件前，不报告预测有效，也不据此调整真实仓位。", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", default="state/investment-score-history.db")
    parser.add_argument("--json-output", default="state/event-prediction-validation.json")
    parser.add_argument("--markdown-output", default="outputs/event-prediction-validation.md")
    args = parser.parse_args()
    connection = sqlite3.connect(args.database)
    payload = evaluate(connection)
    connection.close()
    Path(args.json_output).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(payload, Path(args.markdown_output))
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
