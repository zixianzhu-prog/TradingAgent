"""Serenity evidence packets built from the companies' own SEC filings.

The screen-era packets held only XBRL numbers and FDA records, so most gates came
back "unknown". For each ticker this script finds the latest annual report (10-K or
20-F) and latest quarterly report (10-Q or 6-K) through the EDGAR index, downloads
them (needs SEC_USER_AGENT with a contact email) and keeps ~1,000-character windows
around the passages each Serenity gate needs:

  supply and suppliers, customers and partners, competition, products and
  regulatory clearances, reimbursement, AI description, results, debt and
  dilution, related parties and governance.

Packets go into the Claude review manifest (state/serenity-claude-queue.json); the
reviewer may only quote these passages, and the importer re-checks every quote.
A compact reading sheet is written next to the manifest for the reviewer.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.parse
from datetime import date, timedelta
from pathlib import Path

import beneficiary_mapper as mapper
import official_feeds
import prepare_claude_review as claude
import serenity_evidence_review as ser

ROOT = Path(__file__).resolve().parents[1]
WINDOW = 500
TOPICS = [
    ("supply", r"sole[- ](?:source|supplier)|single[- ]source|we rely on (?:a limited number of|third[- ]part)|contract manufactur"),
    ("customers", r"(?:customers?|collaborators?) (?:accounted|represented) for|largest customers?|collaboration (?:and license )?agreement with|strategic (?:partnership|collaboration) with"),
    ("competition", r"(?:our )?competitors (?:include|such as)|we compete (?:with|against)|compete directly"),
    ("product", r"510\(k\)|de novo|FDA (?:clearance|approval|approved|cleared)|breakthrough device|CE mark"),
    ("reimbursement", r"Medicare|reimburse|CPT code|coverage (?:decision|policy|policies)|payors?"),
    ("ai", r"artificial intelligence|machine learning|our AI|deep learning|foundation model"),
    ("results", r"total revenue (?:was|increased|grew)|revenue (?:increased|grew) [\d.]+%|net loss (?:was|of)|accumulated deficit"),
    ("debt", r"convertible (?:senior )?notes|term loan|credit (?:agreement|facility)|at-the-market|ATM (?:offering|program)"),
    ("governance", r"related part(?:y|ies)|dual[- ]class|controlled company|material weakness|chief executive officer (?:transition|succession)"),
]
PER_TOPIC = 2


def latest_filings(cik: str, today: date, fetch=mapper.http_json) -> dict[str, str]:
    """URLs of the latest annual and quarterly report (main document, not exhibits)."""
    params = urllib.parse.urlencode({"ciks": f"{int(cik):010d}", "forms": "10-K,20-F,10-Q,6-K", "dateRange": "custom",
                                     "startdt": (today - timedelta(days=540)).isoformat(), "enddt": today.isoformat()})
    hits = fetch(f"{mapper.EFTS}?{params}", mapper.DEFAULT_AGENT).get("hits", {}).get("hits", [])
    best: dict[str, tuple[str, str]] = {}
    for hit in hits:
        src = hit.get("_source", {})
        form = src.get("form", "")
        if str(src.get("file_type", "")).upper() != form:
            continue  # exhibits
        kind = "annual" if form in {"10-K", "20-F"} else "quarterly"
        if form == "6-K":
            continue  # 6-K main documents are usually cover pages; the exhibit holds the report
        if kind not in best or src.get("file_date", "") > best[kind][0]:
            best[kind] = (src.get("file_date", ""), mapper.filing_url(cik, hit.get("_id", "")))
    return {kind: url for kind, (_, url) in best.items()}


def windows(text: str, url: str, label: str) -> list[dict]:
    """Keep passages around the first matches of each topic (skipping the table of contents)."""
    start = max(0, text.find("Item 1.", 5000))
    passages, taken = [], []
    for topic, pattern in TOPICS:
        count = 0
        for match in re.finditer(pattern, text[start:], re.I):
            position = start + match.start()
            if any(abs(position - p) < WINDOW for p in taken):
                continue
            taken.append(position)
            body = text[max(0, position - WINDOW): position + WINDOW]
            pid = "ev_" + ser.digest([url, body])[:16]
            passages.append({"id": pid, "topic": topic, "title": f"{label} · {topic}", "text": body, "url": url, "publishedAt": "",
                             "observedAt": ser.now(), "provenance": "primary-document", "primary": True,
                             "path": "state/serenity-source-cache", "sha256": ser.digest(body)})
            count += 1
            if count >= PER_TOPIC:
                break
    return passages


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Serenity packets from each company's latest SEC filings")
    parser.add_argument("tickers", nargs="+")
    args = parser.parse_args()
    if "@" not in os.getenv("SEC_USER_AGENT", ""):
        sys.exit('Set SEC_USER_AGENT="App Name your.email@example.com" first; SEC requires a contact to download filings.')
    ciks = official_feeds.covered_ciks()
    skills = ser.methodology()
    skill_files = [{k: s[k] for k in ("name", "path", "sha256")} for s in skills]
    manifest_path = ROOT / "state/serenity-claude-queue.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {"companies": []}
    manifest.setdefault("companies", [])
    sheet = []
    for ticker in args.tickers:
        meta = ciks.get(ticker) or {}
        if not meta.get("cik"):
            print(f"{ticker}: no CIK, skipped")
            continue
        evidence, errors = [], []
        for kind, url in latest_filings(meta["cik"], date.today()).items():
            try:
                text = claude.filing_text(url, allow_fetch=True)
                evidence += windows(text, url, f"{ticker} {kind} report")
            except Exception as exc:
                errors.append(f"{url}: {str(exc)[:100]}")
        identity = ser.digest([ser.VERSION, "claude-filings", ser.GATES, [s["sha256"] for s in skills],
                               [{k: v for k, v in p.items() if k != "observedAt"} for p in evidence]])
        packet_path = ROOT / "state/serenity-codex-inbox" / f"{ticker}-claude-{identity[:20]}.json"
        packet_path.write_text(json.dumps({"ticker": ticker, "inputHash": identity, "generatedAt": ser.now(), "reviewer": "Claude",
                                           "rubric": ser.GATES, "skillFiles": skill_files, "evidence": evidence, "sourceErrors": errors},
                                          ensure_ascii=False, indent=2), encoding="utf-8")
        manifest["companies"] = [c for c in manifest["companies"] if c["ticker"] != ticker] + [
            {"ticker": ticker, "inputHash": identity, "packetPath": str(packet_path.relative_to(ROOT)), "status": "pending", "evidencePassages": len(evidence)}]
        sheet.append(f"### {ticker} {meta['name']} · {len(evidence)} passages · inputHash {identity}")
        sheet += [f"[{p['id']}] ({p['topic']}) {p['text']}" for p in evidence]
        print(f"{ticker}: {len(evidence)} passages from {len(set(p['url'] for p in evidence))} filings; errors {len(errors)}")
    manifest.update({"generatedAt": ser.now(), "provider": "Claude", "rubric": ser.GATES, "skillFiles": skill_files,
                     "responsePath": "state/serenity-claude-response.json"})
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "state/serenity-claude-reading-sheet.md").write_text("\n\n".join(sheet), encoding="utf-8")


if __name__ == "__main__":
    main()
