"""Data freshness: is every source the page relies on as recent as its schedule promises?

Each source has a cadence (daily or weekly) and a limit in calendar days that allows one missed run. A source past its
limit is stale; a missing file or date is missing. Critical sources (prices, order tickets, Serenity gates, news) put a
red alert at the top of the page, because a ticket priced on old data or a gate graded on old filings should not be read
as current.

    python3 scripts/data_freshness.py          # writes state/data-freshness.json
"""
from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "state/data-freshness.json"

# (label, file, how to read its date, cadence, limit in days, critical, what it feeds)
SOURCES = [
    ("Market prices", "state/order-tickets.json", "pricesAsOf", "daily", 4, True, "order tickets, price ranges"),
    ("Order tickets", "state/order-tickets.json", "generatedAt", "daily", 2, True, "buy / wait / avoid calls"),
    ("Serenity gates", "state/serenity-gate-results.json", "generatedAt", "daily", 2, True, "research tiers"),
    ("News intake", "state/daily-data-inventory.json", "articleDates", "daily", 3, True, "events, gate rechecks"),
    ("Frozen predictions", "state/daily-data-inventory.json", "predictionDates", "daily", 4, False, "track record"),
    ("Emerging signals", "state/emerging-signals.json", "generatedAt", "daily", 2, False, "early-theme radar"),
    ("Clinical trials", "state/clinical-trials-snapshot.json", "generatedAt", "daily", 2, False, "trial events"),
    ("Insider filings (Form 4)", "state/form4-snapshot.json", "generatedAt", "daily", 2, False, "management radar"),
    ("Management radar", "state/management-radar.json", "generatedAt", "daily", 2, False, "governance gate"),
    ("Specialist fund stakes", "state/institutional-ownership.json", "generatedAt", "daily", 2, False, "ownership context"),
    ("Patent assignments", "state/uspto-assignment-validation.json", "generatedAt", "daily", 2, False, "patent liens"),
    ("Candidate filter", "state/candidate-filter.json", "generatedAt", "daily", 2, False, "deep-review queue"),
    ("Market-wide screen", "state/ai-medicine-universe-screen.json", "generatedAt", "weekly", 9, False, "new candidates"),
    ("FDA rejection letters", "state/fda-crl-reasons.json", "generatedAt", "weekly", 9, False, "CRL holds on tickets"),
    ("Equity raises", "state/equity-raises.json", "generatedAt", "weekly", 9, False, "dilution notes"),
    ("Company research papers", "state/company-research.json", "generatedAt", "weekly", 9, False, "lab-to-company chain"),
    ("Key people", "state/key-people.json", "generatedAt", "weekly", 9, False, "key-people section"),
    ("Biodefense radar", "state/biodefense-radar.json", "generatedAt", "weekly", 9, False, "biosecurity section"),
    ("Supply chokepoints", "state/ai-medicine-chokepoints.json", "generatedAt", "weekly", 9, False, "chokepoint gate"),
]


def as_date(value) -> date | None:
    if not value:
        return None
    text = str(value)
    try:
        if len(text) == 10:
            return date.fromisoformat(text)
        moment = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return (moment.astimezone(timezone.utc) if moment.tzinfo else moment).date()
    except ValueError:
        return None


def read_date(data, key: str) -> date | None:
    if not isinstance(data, dict):
        return None
    value = data.get(key)
    if isinstance(value, list):  # dated rows such as [{"day": "2026-11-23", ...}]
        days = [as_date(r.get("day") if isinstance(r, dict) else r) for r in value]
        days = [d for d in days if d]
        return max(days) if days else None
    return as_date(value)


def check(today: date, root: Path = ROOT) -> dict:
    rows = []
    for label, rel, key, cadence, limit, critical, feeds in SOURCES:
        path = root / rel
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = None
        as_of = read_date(data, key)
        age = (today - as_of).days if as_of else None
        status = "missing" if as_of is None else ("stale" if age > limit else "fresh")
        rows.append({"label": label, "file": rel, "asOf": as_of.isoformat() if as_of else None, "ageDays": age,
                     "cadence": cadence, "limitDays": limit, "critical": critical, "feeds": feeds, "status": status})
    bad = [r for r in rows if r["status"] != "fresh"]
    return {"generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"), "today": today.isoformat(),
            "sources": rows, "stale": [r["label"] for r in bad],
            "alert": any(r["critical"] for r in bad), "fresh": len(rows) - len(bad)}


def main() -> None:
    result = check(datetime.now(timezone.utc).date())
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"fresh": result["fresh"], "stale": result["stale"], "alert": result["alert"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
