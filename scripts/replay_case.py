"""Time-machine replay: would the agent have caught a theme early, and who would it have picked?

1. Run the emerging-signal detector day by day over a historical window, seeing
   only articles dated on or before each day.
2. A topic is *confirmed* when it fires on at least two days within a week; the
   second firing day is the detection date. One-day blips are ignored.
3. Map the confirmed topic to companies with the beneficiary mapper, using only
   filings dated on or before the detection date.
4. Score the whole candidate basket afterwards (equal weight, against a sector
   benchmark), so failures count as much as the famous winner.

Example:
    python scripts/replay_case.py --case covid-2020 --database state/replay/covid-2020.db \
        --start 2020-01-10 --end 2020-02-10
"""
from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import beneficiary_mapper as mapper
import pricing_check
import emerging_signal_detector as detector
from emerging_signal_detector import confirm_topics  # noqa: F401  (re-exported for tests)

ROOT = Path(__file__).resolve().parents[1]
HORIZONS = (30, 90, 180, 365)


def daily_signals(databases: list[str], start: date, end: date, recent_days: int = 3, baseline_days: int = 21) -> list[dict]:
    rows = []
    day = start
    while day <= end:
        as_of = datetime(day.year, day.month, day.day, 23, 59, 59, tzinfo=timezone.utc)
        payload = detector.detect(detector.load_docs(databases, as_of, max(90, recent_days + baseline_days)), as_of, recent_days, baseline_days)
        rows.append({"date": day.isoformat(), "signals": [
            {"label": s["label"], "related": s["relatedTerms"], "recent": s["recentArticles"], "baseline": s["baselineArticles"],
             "ids": s.get("articleIds", []),
             "headline": (s["headlines"] or [{}])[0].get("title")}
            for s in payload["signals"][:5]
        ]})
        day += timedelta(days=1)
    return rows


def ground_truth(databases: list[str], term: str, days: list[dict], start: date, end: date) -> dict:
    """Audit a known topic: when did it first appear in the data, and did the detector fire on it?"""
    import sqlite3

    counts: dict[str, int] = {}
    for database in databases:
        connection = sqlite3.connect(database)
        rows = connection.execute(
            "SELECT substr(published_at, 1, 10), COUNT(*) FROM articles WHERE lower(title) LIKE ? GROUP BY 1",
            (f"%{term.lower()}%",),
        ).fetchall()
        connection.close()
        for day, count in rows:
            counts[day] = counts.get(day, 0) + count
    in_window = {d: c for d, c in sorted(counts.items()) if start.isoformat() <= d <= end.isoformat()}
    fired = [row["date"] for row in days if any(term.lower() in " ".join([s["label"], *s.get("related", [])]).lower() for s in row["signals"])]
    return {"term": term, "firstInData": next(iter(in_window), None), "articlesInWindow": sum(in_window.values()),
            "dailyCounts": in_window, "firedOn": fired}


def merge_maps(maps: list[dict], as_of: date) -> dict:
    merged: dict[str, dict] = {}
    for result in maps:
        for bucket in ("candidates", "mentionOnly", "exposed"):
            for row in result.get(bucket, []):
                key = row["cik"] or row["company"]
                current = merged.get(key)
                rank = {"candidates": 0, "mentionOnly": 1, "exposed": 2}[bucket]
                if current is None or rank < current["_rank"] or (rank == current["_rank"] and row["score"] > current["score"]):
                    merged[key] = {**row, "_rank": rank, "matchedTerm": result["topic"]}
    rows = sorted(merged.values(), key=lambda r: (r["_rank"], -r["score"]))
    pick = lambda rank: [{k: v for k, v in r.items() if k != "_rank"} for r in rows if r["_rank"] == rank]
    return {"topics": [m["topic"] for m in maps], "asOf": as_of.isoformat(), "filingHits": sum(m["filingHits"] for m in maps),
            "status": [m["status"] for m in maps], "candidates": pick(0), "mentionOnly": pick(1), "exposed": pick(2)}


def price_outcomes(tickers: list[str], start: date, benchmark: str) -> dict:
    import yfinance as yf

    end = start + timedelta(days=max(HORIZONS) + 10)
    out = {}
    for ticker in [*tickers, benchmark]:
        frame = yf.download(ticker, start=start.isoformat(), end=end.isoformat(), auto_adjust=True, progress=False)
        if frame.empty:
            out[ticker] = None
            continue
        close = frame["Close"]
        if getattr(close, "ndim", 1) > 1:
            close = close.iloc[:, 0]
        series = {index.date(): float(value) for index, value in close.dropna().items()}
        days = sorted(series)
        entry_day = days[0]
        result = {"entryDate": entry_day.isoformat(), "entryPrice": series[entry_day]}
        for horizon in HORIZONS:
            target = next((d for d in days if d >= entry_day + timedelta(days=horizon)), None)
            result[f"r{horizon}"] = series[target] / series[entry_day] - 1 if target else None
        out[ticker] = result
    return out


def basket(outcomes: dict, tickers: list[str], benchmark: str) -> dict:
    summary = {}
    for horizon in HORIZONS:
        values = [outcomes[t][f"r{horizon}"] for t in tickers if outcomes.get(t) and outcomes[t].get(f"r{horizon}") is not None]
        bench = (outcomes.get(benchmark) or {}).get(f"r{horizon}")
        summary[horizon] = {
            "n": len(values),
            "mean": sum(values) / len(values) if values else None,
            "median": sorted(values)[len(values) // 2] if values else None,
            "winners": sum(v > (bench or 0) for v in values),
            "benchmark": bench,
        }
    return summary


def pct(value) -> str:
    return f"{value:+.0%}" if value is not None else "n/a"


def write_markdown(payload: dict, path: Path) -> None:
    case, det, mapped = payload["case"], payload["detection"], payload.get("mapping")
    lines = [f"# 时间机器回放：{case}", "",
             "> 系统被放回历史，每天只能看到当天及之前公开的预印本和 SEC 文件，不使用语言模型。"
             "收益按“确认当天之后的第一个交易日收盘价”买入整篮候选计算，赢家和输家一起算。这是单个历史案例，不代表普遍的预测能力。", ""]
    truth = payload.get("groundTruth")
    if truth:
        lines += ["## 标准答案检查", "",
                  f"- 期望话题：**{truth['term']}**；窗口内数据中第一次出现：{truth['firstInData'] or '没有出现'}；共 {truth['articlesInWindow']} 篇",
                  f"- 系统报警日期：{', '.join(truth['firedOn']) or '从未报警'}",
                  f"- 每日篇数：{', '.join(f'{d[5:]}:{c}' for d, c in truth['dailyCounts'].items()) or '无'}", ""]
    if not det:
        lines += ["## 结论", "",
                  "回放窗口内**没有话题达到确认标准**（两天内重复报警，且第二次带来新文章），系统保持沉默，不生成候选篮子。"
                  "零星的单日噪音被确认规则过滤。若标准答案检查显示期望话题在数据中出现得太晚或太少，说明问题在数据源而不是阈值。"]
    else:
        lines += [f"## 1. 什么时候发现的", "",
                  f"- 话题：**{det['topic']}**",
                  f"- 第一次报警：{det['firstFired']}；确认（第二次报警）：**{det['confirmed']}**；窗口内共报警 {det['daysFired']} 天",
                  f"- 数据：{', '.join(payload['sources'])}", ""]
        lines += [f"- {h['date']}：{h['title']}" for h in det["headlines"]]
        lines += ["", "其他被确认的话题（用于检查误报）：" + ("、".join(f"{c['topic']}（{c['confirmed']}）" for c in payload["otherConfirmed"]) or "无"), ""]
        lines += [f"## 2. 当天能找到哪些公司", "",
                  f"截至 {mapped['asOf']}，用 {', '.join(mapped['topics'])} 检索 SEC 文件，共命中 {mapped['filingHits']} 份。", "",
                  "| 股票 | 公司 | 行业 | 首次在文件中提及 | 事件公告 |", "| --- | --- | --- | --- | ---: |"]
        lines += [f"| {c['ticker'] or '无代码'} | {c['company']} | {c['sicGroup']} | {c['firstFiled']} | {c['announcements']} |" for c in mapped["candidates"]]
        if mapped.get("mentionOnly"):
            lines += ["", "仅在财报中提及的医疗公司：" + ", ".join(r["ticker"] or r["company"] for r in mapped["mentionOnly"])]
        pricing = payload.get("pricing")
        if pricing:
            lines += ["", f"### 当天是否已被定价（只用 {pricing['asOf']} 及之前的行情）", "",
                      "| 股票 | 判断 | 信号以来超额 | 近10日超额 | 波动倍数 | 成交量倍数 |", "| --- | --- | ---: | ---: | ---: | ---: |"]
            for ticker, row in pricing["companies"].items():
                if row["verdict"] == "no data":
                    lines.append(f"| {ticker} | 无数据 | — | — | — | — |")
                    continue
                sigma = f"{row['sigmaMove']:+.1f}σ" if row["sigmaMove"] is not None else "—"
                volume = f"{row['volumeRatio']:.1f}×" if row["volumeRatio"] else "—"
                lines.append(f"| {ticker} | {pricing_check.VERDICT_ZH[row['verdict']]} | {pricing_check.pct(row['excessSinceSignal'])} | "
                             f"{pricing_check.pct(row['excess10d'])} | {sigma} | {volume} |")
        lines += ["", "## 3. 之后的实际表现（整篮等权）", "",
                  "| 股票 | 买入日 | " + " | ".join(f"{h} 天" for h in HORIZONS) + " |", "| --- | --- | " + " | ".join("---:" for _ in HORIZONS) + " |"]
        for ticker, row in payload["outcomes"].items():
            if row is None:
                lines.append(f"| {ticker} | 无行情（可能已退市或被收购） | " + " | ".join("n/a" for _ in HORIZONS) + " |")
                continue
            label = f"**{ticker}（基准）**" if ticker == payload["benchmark"] else ticker
            lines.append(f"| {label} | {row['entryDate']} | " + " | ".join(pct(row.get(f'r{h}')) for h in HORIZONS) + " |")
        lines += ["", "| 周期 | 有行情的候选 | 等权平均 | 中位数 | 跑赢基准的个数 | 基准 |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
        for horizon, row in payload["basket"].items():
            lines.append(f"| {horizon} 天 | {row['n']} | {pct(row['mean'])} | {pct(row['median'])} | {row['winners']}/{row['n']} | {pct(row['benchmark'])} |")
        lines += ["", "## 4. 局限", "",
                  "- 只有两个预印本来源，新闻、WHO 通报和 ProMED 的历史数据尚未接入；接入后预计能更早发现。",
                  "- 只通过 SEC 文件映射公司：只发新闻稿、不提交 8-K 的公司（例如当时的 Inovio）会被漏掉。",
                  "- 已退市或被收购的公司可能没有行情，篮子收益会因此偏向幸存者。",
                  "- 必须用更多案例检验，包括寨卡、埃博拉这类先暴涨后暴跌的“假警报”。"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay detection and beneficiary mapping on a historical window")
    parser.add_argument("--case", required=True)
    parser.add_argument("--database", action="append", required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--topic", help="Force a topic instead of the first confirmed one")
    parser.add_argument("--lookback-days", type=int, default=45)
    parser.add_argument("--benchmark", default="XBI")
    parser.add_argument("--skip-prices", action="store_true")
    parser.add_argument("--expect", help="Ground-truth topic word to audit (when it first appears in the data, whether it fired)")
    args = parser.parse_args()

    days = daily_signals(args.database, date.fromisoformat(args.start), date.fromisoformat(args.end))
    confirmed = confirm_topics(days)
    detection = next((c for c in confirmed if not args.topic or c["topic"] == args.topic), None)
    if args.topic and detection is None:
        detection = {"topic": args.topic, "firstFired": None, "confirmed": args.end, "daysFired": 0, "labels": {}, "headlines": []}
    payload = {"case": args.case, "sources": sorted({db for db in args.database}), "benchmark": args.benchmark,
               "dailySignals": days, "detection": detection,
               "otherConfirmed": [c for c in confirmed if c is not detection], "generatedAt": datetime.now(timezone.utc).isoformat()}
    if detection:
        as_of = date.fromisoformat(detection["confirmed"])
        # Search filings with every leading label of the topic and merge, so the basket
        # does not depend on which single keyword happened to rank first.
        terms = detection.get("searchTerms") or [detection["topic"]]
        maps = [mapper.map_topic(term, as_of, args.lookback_days) for term in terms]
        mapped = merge_maps(maps, as_of)
        payload["mapping"] = mapped
        tickers = [c["ticker"] for c in mapped["candidates"] if c["ticker"]]
        if not args.skip_prices and tickers:
            # What a user would have seen that day: had these stocks already reacted?
            first = date.fromisoformat(detection["firstFired"]) if detection.get("firstFired") else as_of
            payload["pricing"] = pricing_check.check(tickers, first, as_of, args.benchmark)
        if not args.skip_prices:
            # Enter on the first trading day after the detection date: the signal is only known after that day ends.
            outcomes = price_outcomes(tickers, as_of + timedelta(days=1), args.benchmark)
            payload["outcomes"] = outcomes
            payload["basket"] = basket(outcomes, tickers, args.benchmark)
    if args.expect:
        payload["groundTruth"] = ground_truth(args.database, args.expect, days, date.fromisoformat(args.start), date.fromisoformat(args.end))
    out_json = ROOT / f"state/replay/{args.case}.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    write_markdown(payload, ROOT / f"outputs/replay-{args.case}.md")
    print(json.dumps({"detection": detection and {k: detection[k] for k in ("topic", "firstFired", "confirmed")},
                      "candidates": [c["ticker"] for c in payload.get("mapping", {}).get("candidates", [])],
                      "basket": payload.get("basket")}, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
