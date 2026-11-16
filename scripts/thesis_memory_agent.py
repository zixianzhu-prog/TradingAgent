from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


TRACKED_FIELDS = (
    "rank", "classification", "serenityDecision", "completenessScore",
    "valuationLabel", "fundingRisk", "priceToSales", "forecastReturn",
)


def memory_event(ticker: str, layer: str, kind: str, content: str, importance: int, sources: list[str] | None = None) -> dict:
    raw = f"{ticker}|{layer}|{kind}|{content}"
    return {
        "id": f"mem_{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:12]}",
        "ticker": ticker,
        "layer": layer,
        "kind": kind,
        "content": content,
        "importance": importance,
        "sources": sources or [],
    }


def latest_report(directory: Path) -> dict:
    files = sorted(directory.glob("run-*.json"), key=lambda path: path.stat().st_mtime)
    return json.loads(files[-1].read_text(encoding="utf-8")) if files else {}


def load_reflections(database: Path | None) -> dict[str, list[dict]]:
    """Load the latest point-in-time outcome at each horizon for each company."""
    if database is None or not database.is_file():
        return {}
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if "benchmark_outcomes" not in tables:
        connection.close()
        return {}
    columns = {row[1] for row in connection.execute("PRAGMA table_info(benchmark_outcomes)")}
    xbi_fields = "xbi_return, excess_xbi" if {"xbi_return", "excess_xbi"} <= columns else "NULL AS xbi_return, NULL AS excess_xbi"
    rows = connection.execute(
        f"""SELECT ticker, prediction_as_of, horizon, target_as_of, realized_return,
                   excess_spy, excess_xlv, {xbi_fields}, direction_correct
            FROM benchmark_outcomes ORDER BY ticker, horizon, prediction_as_of DESC"""
    ).fetchall()
    connection.close()
    result: dict[str, list[dict]] = {}
    seen: set[tuple[str, int]] = set()
    for row in rows:
        key = (row["ticker"], int(row["horizon"]))
        if key in seen:
            continue
        seen.add(key)
        result.setdefault(row["ticker"], []).append(dict(row))
    return result


def compare(previous: dict | None, current: dict) -> list[dict]:
    if not previous:
        return []
    changes = []
    for field in TRACKED_FIELDS:
        before, after = previous.get(field), current.get(field)
        if before != after:
            changes.append({"field": field, "before": before, "after": after})
    return changes


def build_snapshot(theses: dict, gates: dict, financials: dict, market: dict, events: dict, generated_at: str, reflections: dict[str, list[dict]] | None = None) -> dict:
    gate_rows = {row["ticker"]: row for row in gates.get("companies", [])}
    financial_rows = {row["ticker"]: row for row in financials.get("companies", [])}
    signal_rows = {row["signal"]["ticker"]: row["signal"] for row in market.get("results", [])}
    event_rows: dict[str, list[dict]] = {}
    for task in events.get("revalidationTasks", []):
        event_rows.setdefault(task["ticker"], []).append({
            "title": task.get("title"),
            "status": task.get("status"),
            "affectedGates": task.get("affectedGates", []),
        })
    companies = {}
    reflections = reflections or {}
    research_universe = [*theses.get("candidates", []), *theses.get("expanded_deep_dives", [])]
    for thesis in research_universe:
        ticker = thesis["ticker"]
        gate, financial, signal = gate_rows.get(ticker, {}), financial_rows.get(ticker, {}), signal_rows.get(ticker, {})
        forecast = market.get("kronos", {}).get(ticker, {}).get("forecast_return")
        sources = thesis.get("sources", [])
        memories = [
            memory_event(ticker, "shallow", "market_context", f"Price={signal.get('price')}; five-day forecast={forecast}", 1, ["OpenBB", "Kronos"]),
            memory_event(ticker, "deep", "thesis", thesis.get("thesis", ""), 3, sources),
            memory_event(ticker, "deep", "bear_case", thesis.get("bear_case", ""), 3, sources),
        ]
        for falsifier in thesis.get("falsifiers", []):
            memories.append(memory_event(ticker, "deep", "falsifier", falsifier, 3, sources))
        for event in event_rows.get(ticker, []):
            memories.append(memory_event(ticker, "intermediate", "revalidation_event", f"{event.get('title')} | {event.get('status')} | {','.join(event.get('affectedGates', []))}", 2))
        for outcome in reflections.get(ticker, []):
            xbi = outcome.get("excess_xbi")
            xbi_text = f"; excess XBI={xbi:+.4f}" if xbi is not None else "; excess XBI=unavailable"
            content = (
                f"Prediction {outcome['prediction_as_of']} to {outcome['target_as_of']}; "
                f"horizon={outcome['horizon']}; return={outcome['realized_return']:+.4f}; "
                f"excess SPY={outcome['excess_spy']:+.4f}; excess XLV={outcome['excess_xlv']:+.4f}"
                f"{xbi_text}; direction_correct={outcome['direction_correct']}"
            )
            memories.append(memory_event(ticker, "reflection", "realized_outcome", content, 3, ["Frozen prediction ledger", "Market benchmark prices"]))
        cited_ids = [row["id"] for row in memories if row["kind"] in {"thesis", "bear_case", "revalidation_event", "market_context", "realized_outcome"}]
        companies[ticker] = {
            "ticker": ticker,
            "rank": thesis.get("rank"),
            "classification": thesis.get("classification"),
            "serenityDecision": gate.get("decision", "unreviewed"),
            "completenessScore": gate.get("completenessScore"),
            "valuationLabel": financial.get("valuation_label"),
            "fundingRisk": financial.get("funding_risk"),
            "priceToSales": financial.get("price_to_sales_approx"),
            "price": signal.get("price"),
            "forecastReturn": round(float(forecast), 6) if forecast is not None else None,
            "memoryEvents": memories,
            "citedMemoryIds": cited_ids,
            "layers": {
                "shallow": {"price": signal.get("price"), "fiveDayForecast": forecast},
                "intermediate": {"events": event_rows.get(ticker, []), "staleGates": gate.get("staleGates", [])},
                "deep": {"thesis": thesis.get("thesis"), "bearCase": thesis.get("bear_case"), "falsifiers": thesis.get("falsifiers", [])},
                "reflection": {"latestOutcomes": reflections.get(ticker, [])},
            },
        }
    return {"generatedAt": generated_at, "companies": companies}


def update_memory(previous: dict, snapshot: dict, max_snapshots: int = 365) -> dict:
    history = list(previous.get("history", []))
    prior_snapshot = history[-1] if history else None
    prior_companies = (prior_snapshot or {}).get("companies", {})
    changes = []
    for ticker, current in snapshot["companies"].items():
        ticker_changes = compare(prior_companies.get(ticker), current)
        if ticker_changes:
            changes.append({"ticker": ticker, "changes": ticker_changes, "events": current["layers"]["intermediate"]["events"]})
    fingerprint = json.dumps(snapshot["companies"], sort_keys=True, ensure_ascii=False)
    prior_fingerprint = json.dumps(prior_companies, sort_keys=True, ensure_ascii=False) if prior_snapshot else None
    if fingerprint != prior_fingerprint:
        snapshot["changesFromPrevious"] = changes
        history.append(snapshot)
    history = history[-max_snapshots:]
    return {
        "generatedAt": snapshot["generatedAt"],
        "method": "Deterministic layered thesis memory inspired by FinMem: shallow market context, intermediate events/gates, deep thesis/falsifiers, and realized-outcome reflection.",
        "history": history,
        "latest": history[-1] if history else snapshot,
        "summary": {
            "companies": len(snapshot["companies"]),
            "snapshots": len(history),
            "changedCompanies": len(changes),
            "changedFields": sum(len(row["changes"]) for row in changes),
            "memoryEvents": sum(len(row.get("memoryEvents", [])) for row in snapshot["companies"].values()),
        },
        "claimBoundary": "Memory records what the system believed and why it changed; it does not make a forecast valid or create an order.",
    }


def render(payload: dict) -> str:
    summary, latest = payload["summary"], payload["latest"]
    lines = [
        "# AI Medicine 论点长期记忆", "",
        "> 记录系统在每次运行时知道什么、排名如何变化、哪些事件让 Serenity 门槛失效。它是审计轨迹，不是预测能力证明。", "",
        f"覆盖 {summary['companies']} 家公司；保留 {summary['snapshots']} 个不同状态快照；本次 {summary['changedCompanies']} 家发生变化，共 {summary['changedFields']} 个字段变化。", "",
        "## 本次变化", "",
    ]
    changes = latest.get("changesFromPrevious", [])
    if not changes:
        lines.append("- 首次建立基线，或与上一状态相比没有可记录变化。")
    for row in changes:
        lines.append(f"### {row['ticker']}")
        for change in row["changes"]:
            lines.append(f"- `{change['field']}`：`{change['before']}` → `{change['after']}`")
        for event in row.get("events", []):
            lines.append(f"- 关联事件：{event.get('title')}；影响门槛：{', '.join(event.get('affectedGates', [])) or '未标注'}")
    lines += ["", "## 当前记忆", "", "| 股票 | 排名 | Serenity | 完整度 | 估值 | 融资风险 | 5日环境 |", "|---|---:|---|---:|---|---|---:|"]
    for ticker, row in sorted(latest.get("companies", {}).items(), key=lambda item: item[1].get("rank") or 999):
        forecast = f"{row['forecastReturn']:+.2%}" if row.get("forecastReturn") is not None else "—"
        lines.append(f"| {ticker} | {row.get('rank')} | {row.get('serenityDecision')} | {row.get('completenessScore')} | {row.get('valuationLabel') or '—'} | {row.get('fundingRisk') or '—'} | {forecast} |")
    lines += ["", "## 决策引用记忆", ""]
    for ticker, row in sorted(latest.get("companies", {}).items(), key=lambda item: item[1].get("rank") or 999):
        lines.append(f"- **{ticker}：** " + ", ".join(f"`{memory_id}`" for memory_id in row.get("citedMemoryIds", [])))
    lines += ["", "## 已实现表现反思", "", "| 股票 | 周期 | 实际收益 | 超额 SPY | 超额 XLV | 超额 XBI | 方向正确 |", "|---|---:|---:|---:|---:|---:|---|"]
    reflection_count = 0
    for ticker, row in sorted(latest.get("companies", {}).items(), key=lambda item: item[1].get("rank") or 999):
        for outcome in row.get("layers", {}).get("reflection", {}).get("latestOutcomes", []):
            reflection_count += 1
            fmt = lambda value: f"{value:+.2%}" if value is not None else "—"
            lines.append(
                f"| {ticker} | {outcome['horizon']} | {fmt(outcome.get('realized_return'))} | "
                f"{fmt(outcome.get('excess_spy'))} | {fmt(outcome.get('excess_xlv'))} | "
                f"{fmt(outcome.get('excess_xbi'))} | {'是' if outcome.get('direction_correct') else '否'} |"
            )
    if not reflection_count:
        lines.append("| — | — | 等待未来交易日 | — | — | — | — |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Persist layered AI Medicine thesis memory")
    parser.add_argument("--theses", required=True)
    parser.add_argument("--gates", required=True)
    parser.add_argument("--financials", required=True)
    parser.add_argument("--market-dir", required=True)
    parser.add_argument("--events", required=True)
    parser.add_argument("--performance-db")
    parser.add_argument("--state", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    state_path, report_path = Path(args.state), Path(args.report)
    previous = json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else {}
    now = datetime.now(timezone.utc).isoformat()
    snapshot = build_snapshot(
        json.loads(Path(args.theses).read_text(encoding="utf-8")),
        json.loads(Path(args.gates).read_text(encoding="utf-8")),
        json.loads(Path(args.financials).read_text(encoding="utf-8")),
        latest_report(Path(args.market_dir)),
        json.loads(Path(args.events).read_text(encoding="utf-8")),
        now,
        load_reflections(Path(args.performance_db)) if args.performance_db else {},
    )
    payload = update_memory(previous, snapshot)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    report_path.write_text(render(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
