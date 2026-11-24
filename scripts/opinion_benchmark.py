"""Freeze and score public biotech opinions without turning them into trading signals.

Only ticker-specific views with an exact quote enter the append-only ledger. To prevent hindsight,
performance starts at the later of publication, discovery and freeze. Specialist-fund filings are
shown separately as capital context; they are not opinions and do not prove financing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path
from statistics import mean
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "trend-agent/opinion-leaders.json"
INBOX = ROOT / "trend-agent/opinion-calls.json"
LEDGER = ROOT / "outputs/opinion-call-ledger.jsonl"
STATE = ROOT / "state/opinion-benchmark.json"
REPORT = ROOT / "outputs/opinion-benchmark.md"
OWNERSHIP = ROOT / "state/institutional-ownership.json"
TICKETS = ROOT / "outputs/order-ticket-ledger.jsonl"
HORIZONS = (20, 60, 120, 250)
STANCES = {"positive", "negative", "neutral"}


def load(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def read_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def iso_day(value: str) -> str:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()


def call_id(row: dict) -> str:
    keys = ("leaderId", "publishedAt", "ticker", "stance", "sourceUrl", "quote")
    stable = {key: row.get(key) for key in keys}
    return hashlib.sha256(json.dumps(stable, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:20]


def validate_call(row: dict, leaders: set[str], frozen_day: str) -> list[str]:
    errors = []
    required = ("leaderId", "publishedAt", "discoveredAt", "ticker", "stance", "confidence",
                "sourceUrl", "quote", "thesis", "falsifiers")
    errors += [f"missing {key}" for key in required if row.get(key) in (None, "")]
    if row.get("leaderId") not in leaders:
        errors.append("unknown leaderId")
    if row.get("stance") not in STANCES:
        errors.append("stance must be positive, negative or neutral")
    try:
        confidence = float(row.get("confidence"))
        if not 0 <= confidence <= 100:
            errors.append("confidence must be 0-100")
    except (TypeError, ValueError):
        errors.append("confidence must be numeric")
    if len(str(row.get("quote") or "").strip()) < 20:
        errors.append("quote must contain at least 20 characters")
    if not str(row.get("ticker") or "").strip().isalnum():
        errors.append("ticker must be alphanumeric")
    if urlparse(str(row.get("sourceUrl") or "")).scheme not in ("http", "https"):
        errors.append("sourceUrl must be http(s)")
    try:
        published, discovered = iso_day(row["publishedAt"]), iso_day(row["discoveredAt"])
        if published > discovered:
            errors.append("publishedAt cannot be after discoveredAt")
        if discovered > frozen_day:
            errors.append("discoveredAt cannot be in the future")
    except (KeyError, TypeError, ValueError):
        errors.append("publishedAt and discoveredAt must be ISO timestamps")
    if not isinstance(row.get("falsifiers"), list) or not row.get("falsifiers"):
        errors.append("falsifiers must be a non-empty list")
    return errors


def freeze_calls(calls: list[dict], config: dict, ledger: list[dict], now: datetime) -> tuple[list[dict], list[dict]]:
    leaders = {row["id"] for row in config.get("publicOpinion", [])}
    existing = {row["callId"] for row in ledger}
    frozen, rejected = [], []
    frozen_day = now.date().isoformat()
    for raw in calls:
        row = dict(raw)
        errors, cid = validate_call(row, leaders, frozen_day), call_id(row)
        if cid in existing:
            continue
        if errors:
            rejected.append({"callId": cid, "ticker": row.get("ticker"), "errors": errors})
            continue
        start = max(iso_day(row["publishedAt"]), iso_day(row["discoveredAt"]), frozen_day)
        frozen.append({"callId": cid, "leaderId": row["leaderId"], "publishedAt": row["publishedAt"],
                       "discoveredAt": row["discoveredAt"], "frozenAt": now.isoformat(timespec="seconds"),
                       "evaluationStart": start, "ticker": str(row["ticker"]).upper(),
                       "stance": row["stance"], "confidence": float(row["confidence"]),
                       "sourceUrl": row["sourceUrl"], "quote": row["quote"].strip(),
                       "thesis": row["thesis"].strip(), "falsifiers": row["falsifiers"],
                       "citationStatus": "pending-verification"})
        existing.add(cid)
    return frozen, rejected


def close_on_or_before(series: dict[str, float], day: str) -> tuple[str, float] | None:
    days = [item for item in series if item <= day]
    return (max(days), series[max(days)]) if days else None


def forward(series: dict[str, float], benchmark: dict[str, float], start: str, sessions: int) -> dict | None:
    base = close_on_or_before(benchmark, start)
    if not base:
        return None
    calendar = sorted(benchmark)
    index = calendar.index(base[0])
    if index + sessions >= len(calendar):
        return None
    end = calendar[index + sessions]
    stock0, stock1 = close_on_or_before(series, base[0]), close_on_or_before(series, end)
    if not stock0 or not stock1 or stock0[0] != base[0]:
        return None
    stock_return = stock1[1] / stock0[1] - 1
    benchmark_return = benchmark[end] / base[1] - 1
    return {"startDate": base[0], "endDate": end, "return": stock_return,
            "benchmarkReturn": benchmark_return, "excess": stock_return - benchmark_return}


def score_calls(ledger: list[dict], closes: dict[str, dict[str, float]]) -> list[dict]:
    benchmark, out = closes.get("XBI", {}), []
    for call in ledger:
        for horizon in HORIZONS:
            result = forward(closes.get(call["ticker"], {}), benchmark, call["evaluationStart"], horizon)
            if not result:
                continue
            sign = -1 if call["stance"] == "negative" else 1
            if call["stance"] == "positive":
                correct = result["excess"] > 0
            elif call["stance"] == "negative":
                correct = result["excess"] < 0
            else:
                correct = abs(result["excess"]) < 0.05
            out.append({"callId": call["callId"], "leaderId": call["leaderId"], "ticker": call["ticker"],
                        "stance": call["stance"], "horizon": horizon, **result,
                        "signedExcess": result["excess"] * sign, "directionCorrect": bool(correct)})
    return out


def summarize_scores(rows: list[dict]) -> dict[str, dict]:
    groups: dict[str, list[dict]] = {}
    for row in rows:
        groups.setdefault(row["leaderId"], []).append(row)
    return {leader: {"observations": len(items),
                     "meanSignedExcess": round(mean(row["signedExcess"] for row in items), 4),
                     "directionAccuracy": round(mean(row["directionCorrect"] for row in items), 3)}
            for leader, items in groups.items()}


def specialist_signals(ownership: dict, config: dict) -> list[dict]:
    funds, out = config.get("capitalBehavior", []), []
    for filing in ownership.get("filings", []):
        name = " ".join(str(filing.get(key) or "") for key in ("reportingPerson", "specialistFund"))
        fund = next((row for row in funds if any(alias.lower() in name.lower() for alias in row.get("aliases", []))), None)
        if fund:
            out.append({"fundId": fund["id"], "fund": fund["name"], "ticker": filing.get("ticker"),
                        "filed": filing.get("filed"), "form": filing.get("form"), "percent": filing.get("percent"),
                        "initial": bool(filing.get("initial")), "intentClass": filing.get("intentClass"),
                        "url": filing.get("url")})
    return sorted(out, key=lambda row: (row.get("filed") or "", row.get("fund") or ""), reverse=True)


def serenity_context(calls: list[dict], tickets: list[dict]) -> dict[str, dict]:
    out = {}
    for call in calls:
        eligible = [row for row in tickets if row.get("ticker") == call["ticker"] and row.get("date", "") <= call["evaluationStart"]]
        if eligible:
            row = max(eligible, key=lambda item: item["date"])
            out[call["callId"]] = {"date": row["date"], "action": row.get("action"),
                                   "serenityDecision": row.get("serenityDecision")}
    return out


def render(payload: dict, config: dict) -> str:
    leaders = {row["id"]: row for row in config.get("publicOpinion", [])}
    summary = payload["summary"]
    lines = ["# 生物科技公开观点与专业资金对标", "",
             f"> 生成：{payload['generatedAt']}。公开观点 {summary['calls']} 条；可计分观察 {summary['scoredObservations']} 条；专业资金申报 {summary['fundSignals']} 条。", "",
             "> 观点只在系统首次发现后向前计分；旧文章不会从原发布日期回填收益。基金持仓是背景信息，不是买入建议，也不等于公司获得融资。", "",
             "## 对标角色", "", "| 对象 | 角色 | 本系统如何使用 |", "|---|---|---|"]
    for row in config.get("publicOpinion", []):
        lines.append(f"| {row['name']} / {row['organization']} | {row['role']} | {row['use']} |")
    lines += ["", "## 观点前瞻记录", ""]
    if not payload["calls"]:
        lines += ["尚无符合条件并被冻结的个股观点。系统从现在开始记录；没有原始链接、发布时间、逐字引用、方向和证伪条件的内容不会进入评分。", ""]
    else:
        lines += ["| 冻结日 | 对象 | 股票 | 方向 | 置信度 | 同日 Serenity | 原文 |", "|---|---|---|---|---:|---|---|"]
        for call in payload["calls"]:
            leader = leaders.get(call["leaderId"], {}).get("name", call["leaderId"])
            context = payload.get("serenityContext", {}).get(call["callId"], {})
            lines.append(f"| {call['evaluationStart']} | {leader} | {call['ticker']} | {call['stance']} | {call['confidence']:.0f} | {context.get('action', '—')} | [来源]({call['sourceUrl']}) |")
    lines += ["", "## 到期表现", "", "| 对象 | 可计分观察 | 平均方向调整后超额 XBI | 方向正确率 |", "|---|---:|---:|---:|"]
    if payload["scoreSummary"]:
        for leader, row in sorted(payload["scoreSummary"].items()):
            lines.append(f"| {leaders.get(leader, {}).get('name', leader)} | {row['observations']} | {row['meanSignedExcess']:+.1%} | {row['directionAccuracy']:.0%} |")
    else:
        lines.append("| 等待 20 个交易日后的第一批结果 | 0 | — | — |")
    lines += ["", "## 专业资金行为（SEC 13D/13G）", "",
              "首次申报表示首次跨过申报门槛，不代表刚刚买入全部股份；修订申报表示持股或申报内容变化。13F 尚未接入。", "",
              "| 日期 | 基金 | 股票 | 申报 | 持股 | 首次/修订 | 来源 |", "|---|---|---|---|---:|---|---|"]
    for row in payload["fundSignals"][:60]:
        pct = "—" if row.get("percent") is None else f"{row['percent']:.2f}%"
        lines.append(f"| {row.get('filed') or '—'} | {row['fund']} | {row.get('ticker') or '—'} | {row.get('form') or '—'} | {pct} | {'首次' if row['initial'] else '修订'} | [SEC]({row.get('url') or ''}) |")
    if not payload["fundSignals"]:
        lines.append("| — | 尚无匹配申报 | — | — | — | — | — |")
    lines += ["", "## 判定纪律", "",
              "- 至少 20 个交易日后才产生第一项收益结果；120/250 日用于中长期验证。",
              "- 同一观点同时保存发布时间、发现时间和冻结时间，收益从三者中最晚者开始。",
              "- 公开评论、Serenity 和专业基金行为分别评分，不把三者拼成事后结论。",
              "- 样本不足时只报告数量和数据质量，不宣称谁更准。"]
    return "\n".join(lines) + "\n"


def build(config: dict, inbox: dict, ledger: list[dict], ownership: dict, tickets: list[dict], now: datetime,
          closes: dict[str, dict[str, float]] | None = None) -> tuple[dict, list[dict]]:
    new, rejected = freeze_calls(inbox.get("calls", []), config, ledger, now)
    calls = ledger + new
    scores = score_calls(calls, closes or {})
    funds = specialist_signals(ownership, config)
    payload = {"schemaVersion": 1, "generatedAt": now.isoformat(timespec="seconds"),
               "method": "append-only public-opinion calls; later-of publication/discovery/freeze; XBI benchmark",
               "summary": {"calls": len(calls), "newCalls": len(new), "rejected": len(rejected),
                           "scoredObservations": len(scores), "fundSignals": len(funds)},
               "calls": calls, "rejected": rejected, "scores": scores,
               "scoreSummary": summarize_scores(scores), "fundSignals": funds,
               "serenityContext": serenity_context(calls, tickets)}
    return payload, new


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--today", help="ISO day for reproducible runs")
    parser.add_argument("--no-market", action="store_true", help="freeze and render without fetching prices")
    args = parser.parse_args()
    now = datetime.fromisoformat(args.today).replace(tzinfo=timezone.utc) if args.today else datetime.now(timezone.utc)
    config, inbox = load(CONFIG, {}), load(INBOX, {"calls": []})
    ledger, ownership, tickets = read_jsonl(LEDGER), load(OWNERSHIP, {}), read_jsonl(TICKETS)
    closes = {}
    if (ledger or inbox.get("calls")) and not args.no_market:
        import ticket_ledger as tl
        rows = ledger + inbox.get("calls", [])
        tickers = sorted({str(row.get("ticker", "")).upper() for row in rows if row.get("ticker")})
        starts = [str(row.get("evaluationStart") or row.get("discoveredAt") or now.date().isoformat())[:10] for row in rows]
        closes = tl.fetch_closes(tickers, min(starts)) if tickers else {}
    payload, new = build(config, inbox, ledger, ownership, tickets, now, closes)
    if new:
        LEDGER.parent.mkdir(parents=True, exist_ok=True)
        with LEDGER.open("a", encoding="utf-8") as handle:
            handle.writelines(json.dumps(row, ensure_ascii=False) + "\n" for row in new)
    STATE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT.write_text(render(payload, config), encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
