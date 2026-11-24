"""Turn public key-person evidence into a small, auditable manual-review queue.

The repository already collects the expensive source data:

* ``key_people.py`` identifies officers/founders from SEC Forms 3/4/5 and 10-Ks,
  finds their PubMed papers, and creates a LinkedIn *search* link.
* ``company_research.py`` maps companies to OpenAlex institutions and papers.
* ``management_radar.py`` supplies quoted 8-K Item 5.02 departures.

This script borrows Academic Tracker's useful pattern -- keep a roster snapshot,
compare it with the previous run, and report only new activity -- without scraping
LinkedIn or adding another network dependency.  It never changes a Serenity gate.
It creates evidence-review tasks for a person to confirm first.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEY_PEOPLE = ROOT / "state/key-people.json"
COMPANY_RESEARCH = ROOT / "state/company-research.json"
MANUAL = ROOT / "trend-agent/people-manual-review.json"
OUT = ROOT / "state/people-signal-tracker.json"
REPORT = ROOT / "outputs/people-signal-tracker.md"
WEEKLY_LIMIT = 30
SCIENCE_ROLE = re.compile(r"scientific|medical|technology|research|r&d|clinical", re.I)
CEO_ROLE = re.compile(r"chief executive|\bceo\b|president", re.I)


def read(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def person_key(name: str) -> str:
    """Stable first/last-name key; middle names and accents do not split a person."""
    plain = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode().lower()
    parts = [x for x in re.split(r"[^a-z]+", plain) if len(x) > 1]
    return f"{parts[0]} {parts[-1]}" if len(parts) > 1 else plain.strip()


def paper_key(row: dict) -> str:
    return str(row.get("pmid") or row.get("doi") or row.get("id") or row.get("url") or row.get("title") or "").lower()


def openalex_by_person(company: dict, people: list[dict]) -> dict[str, list[dict]]:
    """Assign OpenAlex company papers only when an authorship name matches a watched person."""
    watched = {person_key(p.get("name", "")): p.get("name") for p in people}
    out: dict[str, list[dict]] = {key: [] for key in watched}
    for work in company.get("topWorks", []):
        for author in work.get("companyAuthors", []):
            key = person_key(author)
            if key in watched:
                out[key].append({
                    "source": "OpenAlex",
                    "title": work.get("title"),
                    "doi": work.get("doi"),
                    "id": work.get("id"),
                    "date": work.get("published"),
                    "url": work.get("doi") or work.get("id"),
                })
    return out


def current_snapshot(key_people: dict, company_research: dict) -> dict:
    companies = {}
    research = company_research.get("companies", {})
    for ticker, company in sorted(key_people.get("companies", {}).items()):
        people = company.get("people", [])
        oa = openalex_by_person(research.get(ticker, {}), people)
        rows = {}
        for person in people:
            key = person_key(person.get("name", ""))
            publications = []
            for paper in (person.get("papers") or {}).get("recent", []):
                publications.append({
                    "source": "PubMed", "pmid": paper.get("pmid"), "title": paper.get("title"),
                    "date": paper.get("date"), "url": paper.get("url"),
                })
            publications.extend(oa.get(key, []))
            unique = {paper_key(p): p for p in publications if paper_key(p)}
            rows[key] = {
                "name": person.get("name"), "title": person.get("title") or "",
                "lastSeen": person.get("lastSeen"), "linkedin": person.get("linkedin"),
                "founder": bool(person.get("founder")), "publications": list(unique.values()),
            }
        departures = []
        for event in company.get("departures", []):
            departures.append({
                "key": str(event.get("url") or event.get("accession") or event.get("detail") or event),
                "date": event.get("date"), "title": event.get("title"), "detail": event.get("detail"),
                "url": event.get("url"), "source": "SEC 8-K Item 5.02",
            })
        companies[ticker] = {"company": company.get("company", ticker), "people": rows, "departures": departures}
    return companies


def event(event_type: str, ticker: str, person: dict | None, **extra) -> dict:
    affected = {
        "key_departure": ["management_governance", "counter_thesis"],
        "new_key_person": ["management_governance"],
        "role_change": ["management_governance"],
        "new_publication": ["supply_chain_map"],
    }[event_type]
    return {
        "type": event_type, "ticker": ticker, "person": (person or {}).get("name"),
        "linkedin": (person or {}).get("linkedin"), "affectedSerenityGates": affected,
        "status": "needs-human-confirmation", **extra,
    }


def changes(current: dict, previous: dict | None) -> list[dict]:
    """Find deltas.  The first run establishes a baseline and raises no historical alerts."""
    if not previous or not previous.get("companies"):
        return []
    out = []
    prior_companies = previous.get("companies", {})
    for ticker, company in current.items():
        old = prior_companies.get(ticker, {"people": {}, "departures": []})
        old_people = old.get("people", {})
        for key, person in company.get("people", {}).items():
            prior = old_people.get(key)
            if prior is None:
                out.append(event("new_key_person", ticker, person, evidence="New name in the SEC/founder roster"))
                continue
            if (prior.get("title") or "").strip().lower() != (person.get("title") or "").strip().lower():
                out.append(event("role_change", ticker, person, oldTitle=prior.get("title"), newTitle=person.get("title"),
                                 evidence="SEC Forms 3/4/5 roster title changed; confirm with 8-K or company biography"))
            known = {paper_key(p) for p in prior.get("publications", [])}
            for paper in person.get("publications", []):
                if paper_key(paper) not in known:
                    out.append(event("new_publication", ticker, person, publication=paper,
                                     evidence=f"New {paper.get('source')} record with company-affiliated authorship"))
        known_departures = {d.get("key") for d in old.get("departures", [])}
        for departure in company.get("departures", []):
            if departure.get("key") not in known_departures:
                out.append(event("key_departure", ticker, None, departure=departure,
                                 evidence="SEC 8-K Item 5.02 departure; review succession and thesis relevance"))
    return out


def build(key_people: dict, company_research: dict, previous: dict | None, manual: dict, today: date) -> dict:
    companies = current_snapshot(key_people, company_research)
    events = changes(companies, previous)
    reviews = manual.get("reviews", {})
    checklist = []
    for ticker, company in companies.items():
        for key, person in company.get("people", {}).items():
            saved = reviews.get(f"{ticker}:{key}", {})
            title = person.get("title") or ""
            priority = "high" if person.get("founder") or SCIENCE_ROLE.search(title) else "medium" if CEO_ROLE.search(title) else "normal"
            cadence = 7 if priority == "high" else 30 if priority == "medium" else 90
            last_reviewed = saved.get("lastReviewedAt")
            try:
                due = not last_reviewed or (today - date.fromisoformat(last_reviewed)).days >= cadence
            except ValueError:
                due = True
            checklist.append({
                "ticker": ticker, "person": person.get("name"), "title": title,
                "linkedin": person.get("linkedin"), "lastReviewedAt": last_reviewed,
                "notes": saved.get("notes", ""), "priority": priority, "cadenceDays": cadence, "due": due,
            })
    rank = {"high": 0, "medium": 1, "normal": 2}
    checklist.sort(key=lambda row: (not row["due"], rank[row["priority"]], row["ticker"], row["person"] or ""))
    selected = [row for row in checklist if row["due"]][:WEEKLY_LIMIT]
    selected_keys = {(row["ticker"], row["person"]) for row in selected}
    for row in checklist:
        row["selectedThisWeek"] = (row["ticker"], row["person"]) in selected_keys
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "baselineInitialized": bool(previous and previous.get("companies")),
        "method": "Snapshot/delta tracker inspired by Academic Tracker; SEC/PubMed/OpenAlex evidence only. "
                  "LinkedIn is a human checklist and is never fetched. Events reopen research, never auto-grade a gate.",
        "summary": {
            "companies": len(companies), "people": sum(len(c["people"]) for c in companies.values()),
            "newEvents": len(events), "manualReviewsDue": sum(x["due"] for x in checklist),
            "selectedThisWeek": len(selected),
        },
        "events": events, "manualLinkedinReview": checklist, "companies": companies,
    }


def render(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# 核心人物信号与人工复核队列", "",
        f"> 覆盖 {summary['companies']} 家公司、{summary['people']} 位核心人物；新增事件 {summary['newEvents']} 条，"
        f"到期 {summary['manualReviewsDue']} 人，本周按优先级安排 {summary['selectedThisWeek']} 人。", "",
        "> LinkedIn 只提供搜索链接，不自动抓取。新论文、职务变化和离职只会触发复核，不能自动通过 Serenity 门槛或形成交易建议。", "",
    ]
    if not payload["baselineInitialized"]:
        lines += ["首次运行只建立基线，不把已有历史记录误报为新事件。下一次运行开始报告增量。", ""]
    lines += ["## 新增事件", "", "| 公司 | 类型 | 人物 | 证据 | 待复核门槛 |", "|---|---|---|---|---|"]
    if not payload["events"]:
        lines.append("| — | 本轮无新增 | — | — | — |")
    for row in payload["events"]:
        evidence = row.get("evidence", "")
        if row.get("publication"):
            paper = row["publication"]
            evidence = f"[{paper.get('title') or '论文'}]({paper.get('url') or ''})"
        if row.get("departure"):
            dep = row["departure"]
            evidence = f"[{dep.get('detail') or dep.get('title') or '8-K'}]({dep.get('url') or ''})"
        lines.append(f"| {row['ticker']} | {row['type']} | {row.get('person') or '—'} | {evidence} | "
                     f"{', '.join(row['affectedSerenityGates'])} |")
    lines += ["", "## 每周 LinkedIn 人工检查", "", "| 公司 | 人物 | 职务 | 上次检查 | 状态 | 链接 |", "|---|---|---|---|---|---|"]
    for row in payload["manualLinkedinReview"]:
        if not row.get("selectedThisWeek"):
            continue
        lines.append(f"| {row['ticker']} | {row['person']} | {row['title'] or '—'} | {row.get('lastReviewedAt') or '未记录'} | "
                     f"{row['priority']} · 每 {row['cadenceDays']} 天 | [LinkedIn 搜索]({row.get('linkedin') or ''}) |")
    remaining = summary["manualReviewsDue"] - summary["selectedThisWeek"]
    if remaining > 0:
        lines += ["", f"> 另有 {remaining} 人已到期，系统会在后续周次按优先级轮换；完整名单保存在 JSON 状态文件中。"]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--key-people", type=Path, default=KEY_PEOPLE)
    parser.add_argument("--company-research", type=Path, default=COMPANY_RESEARCH)
    parser.add_argument("--manual", type=Path, default=MANUAL)
    parser.add_argument("--state", type=Path, default=OUT)
    parser.add_argument("--report", type=Path, default=REPORT)
    args = parser.parse_args()
    payload = build(
        read(args.key_people, {"companies": {}}), read(args.company_research, {"companies": {}}),
        read(args.state, None), read(args.manual, {"reviews": {}}), date.today(),
    )
    args.state.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.state.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    args.report.write_text(render(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
