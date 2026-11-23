"""Build a deterministic management-change radar from official SEC evidence.

This module does not judge whether a stock will rise or fall. It turns named people,
roles, 8-K departures, governance events and Form 4 transactions into an auditable
timeline. Material changes reopen Serenity gates; ordinary insider sales remain
context-needed because tax, diversification and 10b5-1 plans are common.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EARLY = ROOT / "state/early-signals.json"
FORM4 = ROOT / "state/form4-snapshot.json"
WATCH = ROOT / "trend-agent/event-watchlist.json"
OUTPUT = ROOT / "state/management-radar.json"
REPORT = ROOT / "outputs/management-radar.md"

CORE_ROLE = re.compile(
    r"chief executive|\bceo\b|chief scientific|\bcso\b|chief medical|\bcmo\b|"
    r"founder|co-founder|chief technology|\bcto\b",
    re.I,
)
FINANCE_ROLE = re.compile(r"chief financial|\bcfo\b|president", re.I)
ROLE_PATTERNS = (
    ("Founder", re.compile(r"co-founder|founder", re.I)),
    ("CEO", re.compile(r"chief executive officer|\bceo\b", re.I)),
    ("CSO", re.compile(r"chief scientific officer|\bcso\b", re.I)),
    ("CMO", re.compile(r"chief medical officer|\bcmo\b", re.I)),
    ("CTO", re.compile(r"chief technology officer|\bcto\b", re.I)),
    ("CFO", re.compile(r"chief financial officer|\bcfo\b", re.I)),
    ("President", re.compile(r"\bpresident\b", re.I)),
    ("Director", re.compile(r"director|board", re.I)),
)


def read(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else default


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (text or "").lower())


def roles_from_text(text: str) -> list[str]:
    return [label for label, pattern in ROLE_PATTERNS if pattern.search(text or "")]


def covered_companies(watch: dict, form4: dict) -> dict[str, dict]:
    companies = {}
    issuer_by_ticker = {}
    for filing in form4.get("filings", []):
        issuer_by_ticker.setdefault(filing.get("ticker"), filing.get("issuer"))
    for row in watch.get("companies", []):
        ticker = row["ticker"]
        aliases = set(row.get("aliases", [])) | {ticker, issuer_by_ticker.get(ticker) or ""}
        companies[ticker] = {
            "ticker": ticker,
            "company": issuer_by_ticker.get(ticker) or next((a for a in row.get("aliases", []) if len(a) > 4), ticker),
            "aliases": sorted(a for a in aliases if a),
            "people": {},
            "timeline": [],
        }
    return companies


def ticker_for_company(name: str, companies: dict[str, dict]) -> str | None:
    target = norm(name)
    matches = []
    for ticker, company in companies.items():
        for alias in company["aliases"]:
            candidate = norm(alias)
            if len(candidate) >= 5 and (candidate in target or target in candidate):
                matches.append((len(candidate), ticker))
    return max(matches, default=(0, None))[1]


def add_person(company: dict, name: str | None, roles: list[str], source: str) -> None:
    if not name or name in {"未标注", "待读取"}:
        return
    key = norm(name)
    row = company["people"].setdefault(key, {"name": name, "roles": set(), "sources": set()})
    row["roles"].update(r for r in roles if r)
    row["sources"].add(source)


def departure_event(row: dict, ticker: str) -> dict:
    sentence = row.get("sentence", "")
    roles = roles_from_text(sentence)
    critical = bool(CORE_ROLE.search(sentence))
    severity = "critical" if critical else "high" if FINANCE_ROLE.search(sentence) else "medium"
    gates = ["management_governance", "counter_thesis"]
    if critical:
        gates.append("earnings_validation")
    if any(role in {"CSO", "CMO"} for role in roles):
        gates.append("clinical_validation")
    return {
        "date": row.get("date"), "ticker": ticker, "type": "key_departure", "severity": severity,
        "title": f"Key management departure: {', '.join(roles) or 'senior officer'}",
        "detail": sentence, "roles": roles, "source": "SEC 8-K Item 5.02", "url": row.get("url"),
        "affectedGates": sorted(set(gates)), "interpretation": "revalidate",
    }


def transaction_event(row: dict) -> dict:
    code = row.get("code")
    direction = "supportive" if code == "P" else "context-needed"
    label = "open-market purchase" if code == "P" else "open-market sale"
    return {
        "date": row.get("date"), "ticker": row.get("ticker"), "type": "insider_transaction",
        "severity": "supportive" if code == "P" else "informational", "title": f"{row.get('owner')} {label}",
        "detail": f"{row.get('shares') or 0:,.0f} shares; value ${(row.get('value') or 0):,.0f}; code {code}",
        "roles": row.get("roles", []), "source": "SEC Form 4", "url": row.get("url"),
        "affectedGates": ["management_governance"], "interpretation": direction,
        "policy": "A purchase is supporting evidence only. A sale is not bearish without plan, ownership and concentration context.",
    }


def configured_event(row: dict, ticker: str) -> dict:
    event_type = row.get("type")
    severity = "critical" if event_type == "governance" else "high"
    return {
        "date": row.get("date"), "ticker": ticker, "type": event_type, "severity": severity,
        "title": row.get("label"), "detail": "Configured material event; verify against the cited primary filing.",
        "roles": [], "source": "event watchlist", "url": None,
        "affectedGates": row.get("gates", ["management_governance"]), "interpretation": "revalidate",
    }


def build(early: dict, form4: dict, watch: dict, today: date | None = None, lookback_days: int = 180) -> dict:
    today = today or date.today()
    cutoff = today - timedelta(days=lookback_days)
    companies = covered_companies(watch, form4)
    unmatched = []

    for filing in form4.get("filings", []):
        ticker = filing.get("ticker")
        if ticker in companies:
            add_person(companies[ticker], filing.get("owner"), filing.get("roles", []), "SEC Form 4")
    for row in form4.get("marketTransactions", []):
        if row.get("ticker") in companies and (row.get("date") or "") >= cutoff.isoformat():
            companies[row["ticker"]]["timeline"].append(transaction_event(row))

    for row in (early.get("people") or {}).get("keyDepartures", []):
        ticker = ticker_for_company(row.get("company", ""), companies)
        if not ticker:
            unmatched.append(row)
            continue
        event = departure_event(row, ticker)
        companies[ticker]["timeline"].append(event)
        add_person(companies[ticker], None, event["roles"], "SEC 8-K Item 5.02")

    for company_row in watch.get("companies", []):
        ticker = company_row["ticker"]
        if ticker not in companies:
            continue
        for row in company_row.get("events", []):
            if row.get("type") in {"leadership", "governance"} and row.get("date") and row["date"] >= cutoff.isoformat():
                companies[ticker]["timeline"].append(configured_event(row, ticker))

    output = []
    for ticker, company in companies.items():
        # De-duplicate the same source URL/type while retaining distinct Form 4 transactions.
        seen, timeline = set(), []
        for event in sorted(company["timeline"], key=lambda e: e.get("date") or "", reverse=True):
            key = (event["type"], event.get("url"), event.get("date"), event.get("title"))
            if key in seen:
                continue
            seen.add(key)
            timeline.append(event)
        rechecks = [e for e in timeline if e["interpretation"] == "revalidate"]
        critical = [e for e in rechecks if e["severity"] == "critical"]
        gates = sorted({gate for event in rechecks for gate in event.get("affectedGates", [])})
        attention = "urgent-revalidate" if critical or len(rechecks) >= 2 else "revalidate" if rechecks else "monitor"
        people = [{**p, "roles": sorted(p["roles"]), "sources": sorted(p["sources"])} for p in company["people"].values()]
        people.sort(key=lambda p: (not any(CORE_ROLE.search(role) for role in p["roles"]), p["name"]))
        pending_filings = sum(
            filing.get("ticker") == ticker and filing.get("parseStatus") == "error"
            for filing in form4.get("filings", [])
        )
        output.append({
            "ticker": ticker, "company": company["company"], "attention": attention,
            "affectedGates": gates, "corePeople": people, "timeline": timeline,
            "summary": {"people": len(people), "events": len(timeline), "revalidationEvents": len(rechecks),
                        "purchases": sum(e["interpretation"] == "supportive" for e in timeline),
                        "salesNeedingContext": sum(e["interpretation"] == "context-needed" for e in timeline),
                        "pendingForm4Reads": pending_filings},
        })
    priority = {"urgent-revalidate": 0, "revalidate": 1, "monitor": 2}
    output.sort(key=lambda row: (priority[row["attention"]], -row["summary"]["events"], row["ticker"]))
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"), "asOf": today.isoformat(),
        "lookbackDays": lookback_days,
        "method": "Deterministic SEC 8-K/Form 4 management timeline. Events reopen research gates; they do not predict price.",
        "summary": {"companies": len(output), "urgent": sum(r["attention"] == "urgent-revalidate" for r in output),
                    "revalidate": sum(r["attention"] == "revalidate" for r in output),
                    "people": sum(r["summary"]["people"] for r in output),
                    "events": sum(r["summary"]["events"] for r in output),
                    "pendingForm4Reads": sum(r["summary"]["pendingForm4Reads"] for r in output),
                    "unmatchedDepartures": len(unmatched)},
        "companies": output, "unmatchedDepartures": unmatched,
        "limitations": [
            "Form 4 sales require 10b5-1, tax, ownership percentage and concentration context.",
            "A departure does not prove internal trouble; succession, timing and the person's link to the thesis must be checked.",
            "LinkedIn is not scraped. Papers, patents, conference programs and company filings should provide auditable people evidence.",
        ],
    }


def render(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# 管理层与核心人物雷达", "",
        f"> 截至 {payload['asOf']}；覆盖 {summary['companies']} 家公司、{summary['people']} 名已读取申报人、{summary['events']} 个事件。"
        f"紧急重审 {summary['urgent']} 家，普通重审 {summary['revalidate']} 家；待读取 Form 4 共 {summary['pendingForm4Reads']} 份。", "",
        "> 这是治理研究触发器，不是涨跌预测。Form 4 卖出不会自动视为看空；重大离职和调查只会重新打开对应的 Serenity 门槛。", "",
        "| 状态 | 股票 | 核心人物 | 事件 | 买入 | 待解释卖出 | 重新检查 |", "|---|---|---:|---:|---:|---:|---|",
    ]
    labels = {"urgent-revalidate": "紧急重审", "revalidate": "重审", "monitor": "监控"}
    for company in payload["companies"]:
        s = company["summary"]
        lines.append(f"| {labels[company['attention']]} | {company['ticker']} | {s['people']} | {s['events']} | "
                     f"{s['purchases']} | {s['salesNeedingContext']} | {', '.join(company['affectedGates']) or '—'} |")
    for company in payload["companies"]:
        if not company["timeline"]:
            continue
        lines += ["", f"## {company['ticker']} · {labels[company['attention']]}", ""]
        for event in company["timeline"][:12]:
            source = f"[{event['source']}]({event['url']})" if event.get("url") else event["source"]
            lines.append(f"- {event.get('date') or '—'} · **{event['title']}** · {event['interpretation']} · {source}")
            if event.get("detail"):
                lines.append(f"  - {event['detail'][:400]}")
    lines += ["", "## 判断边界", ""] + [f"- {item}" for item in payload["limitations"]]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--early", default=str(EARLY))
    parser.add_argument("--form4", default=str(FORM4))
    parser.add_argument("--watch", default=str(WATCH))
    parser.add_argument("--output", default=str(OUTPUT))
    parser.add_argument("--report", default=str(REPORT))
    parser.add_argument("--lookback-days", type=int, default=180)
    args = parser.parse_args()
    payload = build(read(Path(args.early), {}), read(Path(args.form4), {}), read(Path(args.watch), {}), lookback_days=args.lookback_days)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    Path(args.report).write_text(render(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
