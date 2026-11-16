"""Prepare Serenity evidence packets for companies found by the market-wide screen.

The daily Serenity review covers the deep-reviewed names. Companies that the
market-wide AI-medicine screen shortlists but nobody has reviewed yet are queued
here with the same packet format, so the scheduled Codex review can grade them
against the same eight gates and the importer can verify every quote.

Evidence per company:
- SEC XBRL company facts (primary): latest and year-ago quarterly revenue, net
  income, operating cash flow, cash, R&D. Supports the earnings gate only.
- FDA AI-enabled device records matched to the company (primary): product
  evidence only, never proof of revenue or customer dependence.
- Matching items from the news database, and the latest 10-K/10-Q links. The
  filing text itself is fetched only when SEC_USER_AGENT carries your own contact.

Queued companies do NOT enter serenity-auto-assessments.json until a review is
imported, so existing reports stay unchanged in the meantime.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import ai_medicine_universe_screen as screen_mod
import beneficiary_mapper as mapper
import serenity_evidence_review as ser

ROOT = Path(__file__).resolve().parents[1]
FACTS = [
    ("Revenue", ("RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "RevenueFromContractWithCustomerIncludingAssessedTax")),
    ("Net income (loss)", ("NetIncomeLoss",)),
    ("Operating cash flow", ("NetCashProvidedByUsedInOperatingActivities",)),
    ("Cash and equivalents", ("CashAndCashEquivalentsAtCarryingValue",)),
    ("R&D expense", ("ResearchAndDevelopmentExpense",)),
]


def cik_from(row: dict) -> str | None:
    for filing in row.get("filings", []):
        match = re.search(r"/edgar/data/(\d+)/", filing.get("url", ""))
        if match:
            return match.group(1)
    return None


def _days(fact: dict) -> int | None:
    if not fact.get("start"):
        return None
    return (datetime.fromisoformat(fact["end"]) - datetime.fromisoformat(fact["start"])).days


def xbrl_passage(ticker: str, cik: str, fetch=mapper.http_json) -> dict | None:
    """One primary passage with every figure for the same period end.

    The latest quarterly revenue sets the period. Other figures must end on that date:
    income for the same quarter, cash as of that date, and operating cash flow as the
    year-to-date total that 10-Qs report (labelled as such). Figures not reported for
    that period are listed as missing instead of borrowing another quarter's number.
    """
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{int(cik):010d}.json"
    payload = fetch(url, mapper.DEFAULT_AGENT)
    taxonomy = {**payload.get("facts", {}).get("ifrs-full", {}), **payload.get("facts", {}).get("us-gaap", {})}

    def facts_for(tags):
        tag = next((t for t in tags if t in taxonomy), None)
        if not tag:
            return None, []
        return tag, [v for unit in taxonomy[tag]["units"].values() for v in unit if v.get("form") in {"10-Q", "10-K", "20-F", "6-K"}]

    rev_tag, revenue = facts_for(FACTS[0][1])
    quarterly = [v for v in revenue if _days(v) and 80 <= _days(v) <= 100]
    if not quarterly:
        return None
    anchor = max(quarterly, key=lambda v: (v["end"], v.get("filed", "")))
    end = anchor["end"]
    sentences = [f"Period: quarter ended {end}. Revenue ({rev_tag}): {anchor['val']:,} for {anchor['start']} to {end}; form {anchor.get('form')} filed {anchor.get('filed')}, accession {anchor.get('accn')}."]
    prior_end = f"{int(end[:4]) - 1}{end[4:]}"
    prior = next((v for v in quarterly if v["end"] == prior_end), None)
    if prior and prior["val"]:
        sentences.append(f"Same quarter a year earlier ({prior['start']} to {prior['end']}): {prior['val']:,}, a change of {anchor['val'] / prior['val'] - 1:+.1%}.")
    missing = []
    for label, tags in FACTS[1:]:
        tag, values = facts_for(tags)
        same_end = [v for v in values if v["end"] == end]
        if not same_end:
            missing.append(label)
            continue
        if label == "Cash and equivalents":
            fact, period = same_end[0], f"as of {end}"
        else:
            in_quarter = [v for v in same_end if _days(v) and 80 <= _days(v) <= 100]
            fact = in_quarter[0] if in_quarter else max(same_end, key=lambda v: _days(v) or 0)
            period = f"{fact['start']} to {end}" + ("" if in_quarter else " (year-to-date total as reported)")
        sentences.append(f"{label} ({tag}): {fact['val']:,} for {period}; form {fact.get('form')} filed {fact.get('filed')}.")
    if missing:
        sentences.append(f"Not reported for the quarter ended {end}: {', '.join(missing)}.")
    text = f"SEC XBRL Companyfacts primary filing evidence for {payload.get('entityName', ticker)}. " + " ".join(sentences)
    return {"title": f"SEC XBRL Companyfacts — {ticker}", "text": text, "url": url, "publishedAt": anchor.get("filed", ""),
            "observedAt": ser.now(), "provenance": "sec-companyfacts", "primary": True, "path": "data.sec.gov"}


def fda_passages(ticker: str, name: str, devices: list[dict]) -> list[dict]:
    matched = screen_mod.fda_counts(devices, {ticker: {"name": name}}).get(ticker, [])
    out = []
    for device in matched[:4]:
        body = (f"FDA AI-enabled medical-device authorization record. Manufacturer: {device['manufacturer']}. Device: {device['device']}. "
                f"Final decision date: {device['decisionDate']}. This record supports regulatory product evidence only; it does not establish "
                "revenue contribution, customer dependence, competitive moat, or investment returns.")
        out.append({"title": f"FDA AI device: {device['device']}", "text": body, "url": device.get("url") or "", "publishedAt": device["decisionDate"],
                    "observedAt": ser.now(), "provenance": "fda-ai-device-list", "primary": True, "path": "state/fda-ai-devices.json"})
    return out


def to_passage(doc: dict) -> dict:
    key = ser.digest([doc["url"], doc["text"]])
    return {**doc, "id": "ev_" + key[:16], "sha256": ser.digest(doc["text"])}


def prepare(screen: dict, devices: list[dict], skills: list[dict], fetch_primary: bool, limit: int, fetch=mapper.http_json) -> dict:
    queue = [r for r in screen.get("companies", []) if r.get("shortlisted") and not r.get("deepReviewed")][:limit]
    inbox = ROOT / "state/serenity-codex-inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    skill_files = [{k: s[k] for k in ("name", "path", "sha256")} for s in skills]
    manifest = {"generatedAt": ser.now(), "provider": "Codex subscription", "requiresApiKey": False, "rubric": ser.GATES,
                "skillFiles": skill_files, "responsePath": "state/serenity-codex-queue-response.json", "source": "ai-medicine-universe-screen",
                "instructions": ("Review each packet against the eight Serenity gates using the three skill files. Quote evidence passages "
                                 "exactly; a gate without supporting primary evidence stays unknown or partial. Market cap band and bucket hint "
                                 "come from the stock-selection skill and are context, not evidence."),
                "companies": []}
    for row in queue:
        ticker, name = row["ticker"], row["company"]
        # Full company name only: short forms such as "Adaptive" or "Generate" are ordinary words
        # and pulled unrelated arXiv titles into the evidence.
        plain = re.sub(r",?\s+(inc|corp|corporation|ltd|plc|n\.v|nv|s\.a|sa|ag|holdings)\.?$", "", name, flags=re.I).strip()
        company = {"ticker": ticker, "name": name, "company_terms": [plain],
                   "official_sources": [f["url"] for f in row.get("filings", [])], "trusted_sources": []}
        primary_docs, errors = [], []
        cik = cik_from(row)
        if cik:
            try:
                doc = xbrl_passage(ticker, cik, fetch=fetch)
                if doc:
                    primary_docs.append(doc)
            except Exception as exc:
                errors.append({"url": f"companyfacts CIK{cik}", "error": type(exc).__name__})
        primary_docs += fda_passages(ticker, name, devices)
        collected, collect_errors = ser.collect(company, fetch_primary)
        passages = [to_passage(d) for d in primary_docs] + collected
        passages = passages[:24]
        identity = ser.digest([ser.VERSION, "codex-subscription", ser.GATES, [s["sha256"] for s in skills],
                               [{k: v for k, v in p.items() if k != "observedAt"} for p in passages]])
        packet_path = inbox / f"{ticker}-{identity[:20]}.json"
        packet = {
            "ticker": ticker, "inputHash": identity, "generatedAt": ser.now(), "company": company, "rubric": ser.GATES,
            "skillFiles": skill_files, "evidence": passages, "sourceErrors": errors + collect_errors,
            "screenContext": {k: row.get(k) for k in ("segment", "phrasePairs", "ownershipPhrases", "fdaAiDevices", "marketCapM", "capBand", "bucketHint", "filings")},
            "responseSchema": {"ticker": ticker, "inputHash": identity, "gates": {g: {"status": "pass|partial|pending|unknown|fail", "reason": "Chinese explanation",
                               "support": [{"id": "ev_...", "quote": "exact substring"}], "counter": [{"id": "ev_...", "quote": "exact substring"}],
                               "missing": [], "falsifiers": []} for g in ser.GATES}},
        }
        packet_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest["companies"].append({"ticker": ticker, "inputHash": identity, "packetPath": str(packet_path.relative_to(ROOT)),
                                      "status": "pending", "evidencePassages": len(passages),
                                      "primaryPassages": sum(1 for p in passages if p.get("primary")), "sourceErrors": len(errors + collect_errors)})
        print(f"[Serenity queue] {ticker}: {len(passages)} passages ({manifest['companies'][-1]['primaryPassages']} primary)", flush=True)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Queue screen-shortlisted companies for Serenity review")
    parser.add_argument("--screen", default=str(ROOT / "state/ai-medicine-universe-screen.json"))
    parser.add_argument("--fda", default=str(ROOT / "state/fda-ai-devices.json"))
    parser.add_argument("--fetch-primary", action="store_true", help="Fetch filing text (needs SEC_USER_AGENT with your own contact)")
    parser.add_argument("--limit", type=int, default=30)
    args = parser.parse_args()
    screen = json.loads(Path(args.screen).read_text(encoding="utf-8"))
    devices = json.loads(Path(args.fda).read_text(encoding="utf-8")).get("devices", []) if Path(args.fda).exists() else []
    manifest = prepare(screen, devices, ser.methodology(), args.fetch_primary, args.limit)
    out = ROOT / "state/serenity-codex-queue.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"queued": len(manifest["companies"]), "manifest": str(out.relative_to(ROOT)),
                      "next": "Run the Codex Serenity review (docs/serenity-queue-review-prompt.md), then: ./scripts/finalize_codex_serenity.sh state/serenity-codex-queue-response.json"}))


if __name__ == "__main__":
    main()
