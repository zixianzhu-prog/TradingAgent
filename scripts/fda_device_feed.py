"""Primary-source frontier feed: FDA device decisions from openFDA.

For AI medicine the earliest hard signal is an FDA decision: a 510(k) clearance, a
De Novo grant or a PMA approval. They are official records, dated, and name the
applicant, so they can be mapped to listed companies without guessing from headlines.

Each run pulls decisions from the last --days days (openFDA lags FDA by one to two
weeks), keeps AI/software devices, and maps applicants to listed companies with the
same name rules the market screen uses (first two core words, plus known subsidiary
names such as "GE Medical Systems" for GEHC).

  - mapped decisions go into state/company-news.db with an fda.gov source, so the
    news engine treats them as official regulatory events for that company;
  - every AI decision, mapped or not, goes into state/fda-device-events.json, which
    the page and the Serenity re-check step read.
"""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import official_feeds
from ai_medicine_universe_screen import FDA_ALIASES, core_tokens, same_entity

ROOT = Path(__file__).resolve().parents[1]
API = "https://api.fda.gov/device/{endpoint}.json"
AI_TERMS = re.compile(r"\b(?:ai|artificial intelligence|machine learning|deep learning|neural|algorithm|computer[- ]aided|"
                      r"cad[ex]?|software|analysis software|auto[- ]?seg\w*|automated (?:detection|analysis|segmentation))\b", re.I)
KINDS = {
    "510k": ("510(k) clearance", "https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID={id}"),
    "denovo": ("De Novo grant", "https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/denovo.cfm?ID={id}"),
    "pma": ("PMA approval", "https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpma/pma.cfm?id={id}"),
}


def fetch_json(url: str) -> dict:
    import serenity_evidence_review as ser  # shared certificate context (certifi when available)

    request = urllib.request.Request(url, headers={"User-Agent": "serenity-research-agent"})
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ser.context()))
    with opener.open(request, timeout=40) as response:
        return json.load(response)


def pull(endpoint: str, start: date, end: date, fetch=fetch_json, page: int = 1000) -> list[dict]:
    """All decisions in the window (openFDA caps skip+limit at 26,000)."""
    rows, skip = [], 0
    search = f"decision_date:[{start:%Y%m%d}+TO+{end:%Y%m%d}]"
    while skip < 25_000:
        url = f"{API.format(endpoint=endpoint)}?search={search}&limit={page}&skip={skip}"
        try:
            payload = fetch(url)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:  # openFDA answers 404 when nothing matches
                break
            raise
        batch = payload.get("results", [])
        rows += batch
        skip += len(batch)
        if not batch or skip >= payload.get("meta", {}).get("results", {}).get("total", 0):
            break
        time.sleep(0.3)
    return rows


def normalise(row: dict, endpoint: str) -> dict | None:
    """One decision in a common shape; PMA supplements are dropped (mostly manufacturing changes)."""
    if endpoint == "pma":
        if row.get("supplement_number"):
            return None
        number, name = row.get("pma_number", ""), row.get("trade_name") or row.get("generic_name", "")
        kind = "pma"
    else:
        number, name = row.get("k_number", ""), row.get("device_name", "")
        kind = "denovo" if number.upper().startswith("DEN") or row.get("decision_code") == "DENG" else "510k"
    decided = row.get("decision_date", "")
    if not number or not decided:
        return None
    label, url = KINDS[kind]
    return {"id": number, "kind": kind, "label": label, "device": name.strip(), "applicant": (row.get("applicant") or "").strip(),
            "decisionDate": decided if "-" in decided else f"{decided[:4]}-{decided[4:6]}-{decided[6:]}",
            "productCode": row.get("product_code") or (row.get("openfda") or {}).get("product_code", ""),
            "panel": row.get("advisory_committee_description", ""), "url": url.format(id=number)}


def ai_product_codes(fda_list: dict, minimum: int = 5) -> set[str]:
    """Product codes that recur in FDA's own list of AI-enabled devices."""
    counts = Counter(d.get("productCode") for d in fda_list.get("devices", []) if d.get("productCode"))
    return {code for code, n in counts.items() if n >= minimum}


def ai_reason(decision: dict, ai_codes: set[str], known_ai: set[str]) -> str | None:
    if decision["id"] in known_ai:
        return "on FDA's AI-enabled device list"
    if AI_TERMS.search(decision["device"]):
        return "device name describes AI or software"
    if decision["productCode"] in ai_codes:
        return "product code common on FDA's AI-enabled list"
    return None


def company_index(root: Path = ROOT) -> list[dict]:
    """Listed companies the agent covers or has screened, with name tokens for matching."""
    names: dict[str, str] = {}
    screen = root / "state/ai-medicine-universe-screen.json"
    if screen.exists():
        names.update({r["ticker"]: r["company"] for r in json.loads(screen.read_text(encoding="utf-8")).get("companies", [])})
    universe = root / "trend-agent/ai-medicine-universe.json"
    if universe.exists():
        names.update({r["ticker"]: r["company"] for r in json.loads(universe.read_text(encoding="utf-8")).get("companies", [])})
    try:
        from news_signal_engine import coverage
        covered = {c["ticker"]: c["name"] for c in coverage(root)}
    except Exception:
        covered = {}
    names.update(covered)
    return [{"ticker": t, "name": n, "tokens": core_tokens(n), "covered": t in covered} for t, n in names.items()]


def sec_listed(root: Path = ROOT, fetch=None) -> list[dict]:
    """All SEC-registered tickers (cached), used to spot listed applicants the agent does not cover yet."""
    cache = root / "state/sec-company-tickers.json"
    if cache.exists() and (datetime.now().timestamp() - cache.stat().st_mtime) < 7 * 86400:
        raw = json.loads(cache.read_text(encoding="utf-8"))
    else:
        import os
        agent = os.getenv("SEC_USER_AGENT", "")
        if "@" not in agent:
            return []  # www.sec.gov requires a contact; skip the fallback rather than fail the feed
        import serenity_evidence_review as ser
        request = urllib.request.Request("https://www.sec.gov/files/company_tickers.json", headers={"User-Agent": agent})
        opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ser.context()))
        with opener.open(request, timeout=40) as response:
            raw = json.load(response)
        cache.write_text(json.dumps(raw), encoding="utf-8")
    seen, out = set(), []
    for row in raw.values():
        if row["ticker"] in seen:
            continue
        seen.add(row["ticker"])
        out.append({"ticker": row["ticker"], "name": row["title"], "tokens": core_tokens(row["title"]), "covered": False})
    return out


def match(applicant: str, companies: list[dict]) -> dict | None:
    lowered = applicant.lower()
    for company in companies:
        if any(lowered.startswith(alias.lower()) for alias in FDA_ALIASES.get(company["ticker"], [])):
            return company
    tokens = core_tokens(applicant)
    return next((c for c in companies if same_entity(c["tokens"], tokens)), None)


def strict_match(applicant: str, companies: list[dict]) -> dict | None:
    """Market-wide fallback: every core word of the listed name must lead the applicant's name.

    The covered-company rule lets a one-word name match its subsidiaries; across ~10,000
    SEC registrants that paired Beta Bionics with BETA Technologies, so a one-word listed
    name only matches a one-word applicant here, and the longest match wins.
    """
    tokens = core_tokens(applicant)
    hits = [c for c in companies if c["tokens"] and tokens[:len(c["tokens"])] == c["tokens"]
            and (len(c["tokens"]) >= 2 or len(tokens) == 1)]
    return max(hits, key=lambda c: len(c["tokens"]), default=None)


def build(decisions: list[dict], companies: list[dict], ai_codes: set[str], known_ai: set[str], listed: list[dict] | None = None) -> list[dict]:
    events = []
    for decision in decisions:
        reason = ai_reason(decision, ai_codes, known_ai)
        if not reason:
            continue
        company = match(decision["applicant"], companies)
        new_candidate = False
        if company is None and listed:
            company = strict_match(decision["applicant"], listed)
            new_candidate = company is not None
        confidence = "possible" if reason.startswith("product code") else "high"
        events.append({**decision, "aiReason": reason, "aiConfidence": confidence, "ticker": company["ticker"] if company else None,
                       "company": company["name"] if company else None, "covered": bool(company and company["covered"]),
                       "newCandidate": new_candidate})
    events.sort(key=lambda e: (e["decisionDate"], e["id"]), reverse=True)
    return events


FRESH_DAYS = 21  # openFDA posts decisions one to three weeks late


def public_at(event: dict, first_seen: str) -> str:
    """When the record became public: first sighting for fresh postings, decision date for backfilled history."""
    decided = datetime.fromisoformat(event["decisionDate"]).replace(tzinfo=timezone.utc)
    seen = datetime.fromisoformat(first_seen)
    return first_seen if (seen - decided).days <= FRESH_DAYS else decided.isoformat()


def article_rows(events: list[dict]) -> list[dict]:
    """Mapped, clearly-AI decisions as articles; the headline names the company so the news engine links it.

    A product code that is merely common on FDA's AI list (e.g. general ultrasound) is kept in the JSON
    as a possible AI device but is not pushed to the news engine as an event.
    """
    rows = []
    for e in events:
        if not e["ticker"] or e.get("aiConfidence") != "high" or e.get("newCandidate"):
            continue
        rows.append({"key": f"openfda|{e['id']}", "source": "FDA device database (fda.gov)",
                     "title": f"{e['company']} receives FDA {e['label']} for {e['device']} ({e['id']}) - fda.gov",
                     "url": e["url"],
                     "content": f"(FDA {e['label']}: {e['id']}, decided {e['decisionDate']}, applicant {e['applicant']}, "
                                f"product code {e['productCode']}, {e['aiReason']}.)",
                     "published_at": e.get("publicAt") or f"{e['decisionDate']}T00:00:00+00:00"})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Pull FDA AI/software device decisions from openFDA and map them to companies")
    parser.add_argument("--days", type=int, default=45)
    parser.add_argument("--database", default=str(ROOT / "state/company-news.db"))
    parser.add_argument("--output", default=str(ROOT / "state/fda-device-events.json"))
    args = parser.parse_args()
    end = date.today()
    start = end - timedelta(days=args.days)
    decisions = []
    for endpoint in ("510k", "pma"):
        decisions += [d for d in (normalise(r, endpoint) for r in pull(endpoint, start, end)) if d]
    fda_list = json.loads((ROOT / "state/fda-ai-devices.json").read_text(encoding="utf-8")) if (ROOT / "state/fda-ai-devices.json").exists() else {}
    known_ai = {d.get("submissionNumber") for d in fda_list.get("devices", [])}
    events = build(decisions, company_index(), ai_product_codes(fda_list), known_ai, sec_listed())
    previous = json.loads(Path(args.output).read_text(encoding="utf-8")) if Path(args.output).exists() else {}
    merged = {e["id"]: e for e in previous.get("events", [])} | {e["id"]: e for e in events}
    first_seen = previous.get("firstSeen", {})
    now = datetime.now(timezone.utc).isoformat()
    for key, event in merged.items():
        first_seen.setdefault(key, now)
        event["firstSeen"] = first_seen[key]
        event["publicAt"] = public_at(event, first_seen[key])
    inserted = official_feeds.store(Path(args.database), article_rows(events))
    latest = max((d["decisionDate"] for d in decisions), default=None)
    output = {"generatedAt": now, "window": {"start": start.isoformat(), "end": end.isoformat()},
              "latestDecisionInFeed": latest, "decisionsScanned": len(decisions),
              "note": "openFDA usually trails FDA decisions by one to two weeks.",
              "events": sorted(merged.values(), key=lambda e: (e["decisionDate"], e["id"]), reverse=True), "firstSeen": first_seen}
    Path(args.output).write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    mapped = [e for e in events if e["ticker"] and e["aiConfidence"] == "high"]
    candidates = sorted({e["ticker"] for e in mapped if e.get("newCandidate")})
    print(json.dumps({"decisions": len(decisions), "aiDevices": len(events), "mapped": len(mapped), "inserted": inserted,
                      "latest": latest, "mappedTickers": sorted({e["ticker"] for e in mapped}), "newCandidates": candidates}))


if __name__ == "__main__":
    main()
