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

Small caps (state/small-cap-stage.json): AI-medicine companies under $1B that the screen's
liquidity cut leaves out of the shortlist are queued too, with their stage (preparation /
growth / slowing), cash runway and their own ClinicalTrials.gov records as primary passages.

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


def signal_passages(small: dict) -> list[dict]:
    """The 8-K press releases that put an IND/deal-sourced company on the list, as primary passages."""
    out = []
    for s in small.get("signals", []):
        cached = ROOT / "state/serenity-source-cache/deals-ind" / (ser.digest(s["url"])[:24] + ".txt")   # pharma_deals_ind.fetch_text cache
        text = cached.read_text(encoding="utf-8")[:6000] if cached.exists() else ""
        if text:
            out.append({"title": f"8-K press release {s['filed']}: {s['text']}", "text": text, "url": s["url"], "publishedAt": s["filed"],
                        "observedAt": ser.now(), "provenance": "sec-8k", "primary": True, "path": "state/pharma-deals-ind.json"})
    return out


def trial_passages(small: dict) -> list[dict]:
    """The company's own trials, as found by small_cap_stage.py (ClinicalTrials.gov, primary)."""
    out = []
    for t in (small.get("clinical") or {}).get("examples", []):
        phase = {0.5: "Early Phase 1", 1: "Phase 1", 2: "Phase 2", 3: "Phase 3", 4: "Phase 4"}.get(t["phase"], t["phase"])
        body = (f"ClinicalTrials.gov registry record {t['nct']}: {t['title']}. Highest listed phase: {phase}. Overall status: {t['status']}. "
                f"Start date: {t['start']}. A registry record shows the trial exists and its stage; it does not show results, approval or revenue.")
        out.append({"title": f"ClinicalTrials.gov {t['nct']}", "text": body, "url": f"https://clinicaltrials.gov/study/{t['nct']}",
                    "publishedAt": t["start"], "observedAt": ser.now(), "provenance": "clinicaltrials-gov", "primary": True,
                    "path": "state/small-cap-stage.json"})
    return out


# Annual-report sections that bear on each gate. A 10-K is too long for the generic first-six-chunks
# rule (which mostly returns forward-looking-statement boilerplate), so passages are picked per gate.
GATE_TERMS = {
    "supply_chain_map": r"supplier|sole source|single source|single-source|contract manufactur|third-party manufactur|raw material|components",
    "customer_dependency": r"customers? (?:accounted|represented)|largest customer|concentration of|% of (?:our )?(?:total )?revenue|collaboration agreement|license agreement|upfront payment|milestone payment",
    "chokepoint_evidence": r"market share|competitor|compete|barrier|patent|exclusive|reimbursement|CPT code|switching cost",
    "pure_play": r"reportable segment|disaggregat|revenue by|product revenue|service revenue",
    "management_governance": r"chief executive officer|board of directors|material weakness|internal control over financial reporting|founder",
}
ANNUAL_FORMS = ("10-K", "20-F", "10-K/A")


def annual_report_passages(ticker: str, cik: str, allow_fetch: bool) -> list[dict]:
    """Up to ten gate-relevant passages from the latest 10-K / 20-F (EDGAR submissions API)."""
    import os
    import prepare_claude_review as pcr

    agent = os.getenv("SEC_USER_AGENT", "")
    if not allow_fetch or "@" not in agent:
        return []
    subs = mapper.http_json(f"https://data.sec.gov/submissions/CIK{int(cik):010d}.json", agent)
    recent = subs.get("filings", {}).get("recent", {})
    rows = list(zip(recent.get("form", []), recent.get("accessionNumber", []), recent.get("primaryDocument", []), recent.get("filingDate", [])))
    # The original annual report holds the business, customers and competition; a 10-K/A often only adds Part III.
    latest = next((r for r in rows if r[0] in ("10-K", "20-F")), None) or next((r for r in rows if r[0] == "10-K/A"), None)
    if not latest:
        return []
    form, accession, document, filed = latest
    url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace('-', '')}/{document}"
    text = pcr.filing_text(url, allow_fetch=True) or ""
    chunks = [text[i:i + 2400] for i in range(0, len(text), 2200)]
    chosen: dict[int, str] = {}
    for gate, terms in GATE_TERMS.items():
        scored = sorted(((len(re.findall(terms, c, re.I)), i) for i, c in enumerate(chunks)), reverse=True)
        for hits, i in [x for x in scored if x[0] >= 2][:2]:
            chosen.setdefault(i, gate)
    out = []
    for i in sorted(chosen)[:10]:
        out.append({"title": f"{form} filed {filed} ({chosen[i]} section)", "text": chunks[i], "url": url, "publishedAt": filed,
                    "observedAt": ser.now(), "provenance": "primary-document", "primary": True, "path": "state/serenity-source-cache"})
    return out


def deal_passages(ticker: str) -> list[dict]:
    """Confirmed IND clearances and big-pharma deals for the company (scripts/pharma_deals_ind.py)."""
    path = ROOT / "state/pharma-deals-ind.json"
    if not path.exists():
        return []
    out = []
    for row in json.loads(path.read_text(encoding="utf-8")).get("filings", []):
        facts = row.get("facts") or {}
        if row.get("ticker") != ticker or not (facts.get("isNewDeal") is True or facts.get("isIndClearance") is True):
            continue
        quotes = [f["quote"] for f in facts.values() if isinstance(f, dict) and f.get("verified") and f.get("quote")]
        if quotes:
            kind = "Big-pharma deal" if row["kind"] == "deal" else "IND clearance"
            out.append({"title": f"8-K {row['filed']}: {kind}", "text": f"SEC 8-K press release filed {row['filed']} ({kind}). " + " ".join(quotes),
                        "url": row["url"], "publishedAt": row["filed"], "observedAt": ser.now(), "provenance": "primary-document",
                        "primary": True, "path": "state/pharma-deals-ind.json"})
    return out


SMALL_CAP_CONTEXT = ("stage", "stageDetail", "marketCapM", "revenueRunRateM", "quarterYoY", "fiscalYoY", "cashM", "cashAsOf",
                     "burnPerMonthM", "runwayMonths", "financingRisk")


def prepare(screen: dict, devices: list[dict], skills: list[dict], fetch_primary: bool, limit: int, fetch=mapper.http_json,
            small_caps: dict | None = None, only: set[str] | None = None, annual: bool = False) -> dict:
    queue = [r for r in screen.get("companies", []) if r.get("shortlisted") and not r.get("deepReviewed")][:limit]
    small = {r["ticker"]: r for r in (small_caps or {}).get("companies", []) if not r.get("deepReviewed")}
    by_ticker = {r["ticker"]: r for r in screen.get("companies", [])}
    # Small caps found through the IND/deal tracker are not in the AI screen; their small-cap row has the same shape.
    queue += [by_ticker.get(t, small[t]) for t in small if by_ticker.get(t) not in queue]
    if only:
        queue = [r for r in queue if r["ticker"] in only]
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
        if ticker in small:
            primary_docs += trial_passages(small[ticker])
        primary_docs += deal_passages(ticker)
        if ticker in small:
            primary_docs += signal_passages(small[ticker])
        if annual and cik:
            try:
                primary_docs = annual_report_passages(ticker, cik, fetch_primary) + primary_docs
            except Exception as exc:
                errors.append({"url": f"annual report CIK{cik}", "error": type(exc).__name__})
        collected, collect_errors = ser.collect(company, fetch_primary)
        passages = [to_passage(d) for d in primary_docs] + collected
        passages = passages[:30 if annual else 24]
        identity = ser.digest([ser.VERSION, "codex-subscription", ser.GATES, [s["sha256"] for s in skills],
                               [{k: v for k, v in p.items() if k != "observedAt"} for p in passages]])
        packet_path = inbox / f"{ticker}-{identity[:20]}.json"
        packet = {
            "ticker": ticker, "inputHash": identity, "generatedAt": ser.now(), "company": company, "rubric": ser.GATES,
            "skillFiles": skill_files, "evidence": passages, "sourceErrors": errors + collect_errors,
            "screenContext": {k: row.get(k) for k in ("segment", "phrasePairs", "ownershipPhrases", "fdaAiDevices", "marketCapM", "capBand", "bucketHint", "filings")},
            # Computed from SEC XBRL and prices by small_cap_stage.py: context for the reviewer, not quotable evidence.
            "smallCapContext": {k: small[ticker].get(k) for k in SMALL_CAP_CONTEXT} if ticker in small else None,
            "responseSchema": {"ticker": ticker, "inputHash": identity, "gates": {g: {"status": "pass|partial|pending|unknown|fail", "reason": "Chinese explanation",
                               "support": [{"id": "ev_...", "quote": "exact substring"}], "counter": [{"id": "ev_...", "quote": "exact substring"}],
                               "missing": [], "falsifiers": []} for g in ser.GATES}},
        }
        packet_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest["companies"].append({"ticker": ticker, "inputHash": identity, "source": "small-cap" if ticker in small else "shortlist", "packetPath": str(packet_path.relative_to(ROOT)),
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
    parser.add_argument("--tickers", nargs="*", help="rebuild only these packets and keep the rest of the manifest")
    parser.add_argument("--annual-report", action="store_true", help="add gate-relevant passages from the latest 10-K/20-F")
    parser.add_argument("--small-caps", default=str(ROOT / "state/small-cap-stage.json"), help="small_cap_stage.py output; skipped if missing")
    args = parser.parse_args()
    small_caps = json.loads(Path(args.small_caps).read_text(encoding="utf-8")) if Path(args.small_caps).exists() else None
    screen = json.loads(Path(args.screen).read_text(encoding="utf-8"))
    devices = json.loads(Path(args.fda).read_text(encoding="utf-8")).get("devices", []) if Path(args.fda).exists() else []
    manifest = prepare(screen, devices, ser.methodology(), args.fetch_primary, args.limit, small_caps=small_caps,
                       only=set(args.tickers) if args.tickers else None, annual=args.annual_report)
    out = ROOT / "state/serenity-codex-queue.json"
    if args.tickers and out.exists():         # merge: replace only the rebuilt entries
        rebuilt = {c["ticker"]: c for c in manifest["companies"]}
        previous = json.loads(out.read_text(encoding="utf-8"))
        previous["companies"] = [rebuilt.pop(c["ticker"], c) for c in previous["companies"]] + list(rebuilt.values())
        previous["generatedAt"] = manifest["generatedAt"]
        manifest = previous
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"queued": len(manifest["companies"]), "manifest": str(out.relative_to(ROOT)),
                      "next": "Run the Codex Serenity review (docs/serenity-queue-review-prompt.md), then: ./scripts/finalize_codex_serenity.sh state/serenity-codex-queue-response.json"}))


if __name__ == "__main__":
    main()
