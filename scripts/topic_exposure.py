"""Which companies are exposed to each AI-medicine topic, measured from their own filings.

For every topic in ai_medicine_topics.TOPICS this searches SEC full-text filings
(last 15 months) for the topic's phrases and counts, per health operating company,
how many distinct filings use them. Four or more filings (a 10-K and its 10-Qs)
count as full exposure; one passing mention counts a quarter. Policy topics such
as AI device regulation use FDA AI-enabled device clearances instead.

The news engine multiplies this exposure by how hot a topic is in the frontier
news, so an article that names no company can still move the companies that
actually do that work. Run weekly; filings change slowly.
"""
from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import ai_medicine_universe_screen as screen_mod
import beneficiary_mapper as mapper
from ai_medicine_topics import TOPICS

ROOT = Path(__file__).resolve().parents[1]
FULL_EXPOSURE_FILINGS = 4


DRUG_SIC = {2833, 2834, 2836}


def is_drug_developer(row: dict) -> bool:
    return any(str(code).isdigit() and int(code) in DRUG_SIC for code in row.get("sics") or [])


def filing_exposure(phrases: list[str], start: date, end: date, fetch=mapper.http_json, device: bool = False) -> dict[str, dict]:
    found: dict[str, dict] = {}
    for phrase in phrases:
        hits = screen_mod.search_all(phrase, start, end, max_hits=500, fetch=fetch)
        for row in mapper.aggregate(hits).values():
            if not screen_mod.is_operating(row) or (row["sicGroup"] == "Other sector" and not screen_mod.software(row)):
                continue
            if device and is_drug_developer(row):
                continue
            entry = found.setdefault(row["ticker"], {"company": row["name"], "filings": set(), "url": None})
            entry["filings"] |= set(row["filings"])
            latest = max(row["filings"].values(), key=lambda f: f["filed"] or "")
            entry["url"] = entry["url"] or latest["url"]
    return {t: {"company": e["company"], "filings": len(e["filings"]), "url": e["url"],
                "strength": round(min(1.0, len(e["filings"]) / FULL_EXPOSURE_FILINGS), 2)} for t, e in found.items()}


def fda_exposure(root: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    screen = json.loads((root / "state/ai-medicine-universe-screen.json").read_text(encoding="utf-8")) if (root / "state/ai-medicine-universe-screen.json").exists() else {}
    for row in screen.get("companies", []):
        if row.get("fdaAiDevices"):
            out[row["ticker"]] = {"company": row["company"], "filings": 0, "fdaAiDevices": row["fdaAiDevices"], "url": None,
                                  "strength": round(min(1.0, row["fdaAiDevices"] / 5), 2)}
    return out


KEEP = {"own-product": 1.0, "supplier": 0.8, "customer": 0.6, "mention": 0.5, "unread": 0.5}


def read_relations(found: dict[str, dict], topic_key: str) -> dict[str, dict]:
    """Open each candidate's filing and keep only companies whose text supports the link.

    A phrase match alone kept competitors' risk factors, glossary lines and AI shells; the
    filing-level reading (validate_topic_mapping.classify_filing) drops those and records the
    relation. Without SEC_USER_AGENT only cached filings are read; the rest stay as "unread".
    """
    import os

    import prepare_claude_review as claude
    from validate_topic_mapping import classify_filing

    allow_fetch = "@" in os.getenv("SEC_USER_AGENT", "")
    kept = {}
    for ticker, entry in found.items():
        try:
            text = claude.filing_text(entry["url"], allow_fetch=allow_fetch) or ""
        except Exception:
            text = ""
        view = classify_filing(text, topic_key) if text else {"relation": "unread", "aiMentions": 0, "topicMentions": 0, "example": ""}
        relation = view["relation"]
        if relation not in KEEP:
            continue
        kept[ticker] = {**entry, "relation": relation, "topicMentions": view["topicMentions"], "aiMentions": view["aiMentions"],
                        "evidence": view["example"][:400], "strength": round(entry["strength"] * KEEP[relation], 2)}
    return kept


def build(as_of: date, root: Path = ROOT, fetch=mapper.http_json) -> dict:
    start = as_of - timedelta(days=455)
    topics = {}
    for topic in TOPICS:
        try:
            companies = fda_exposure(root) if topic.get("fda_devices") else filing_exposure(topic["filings"], start, as_of, fetch=fetch, device=topic.get("device", False))
            candidates = len(companies)
            if not topic.get("fda_devices"):
                companies = read_relations(companies, topic["key"])
            status = "ok"
        except Exception as exc:
            companies, candidates, status = {}, 0, f"error: {str(exc)[:120]}"
        ranked = dict(sorted(companies.items(), key=lambda kv: (-kv[1]["strength"], -kv[1]["filings"]))[:60])
        topics[topic["key"]] = {"label": topic["label"], "status": status, "phraseCandidates": candidates,
                                "keptAfterReading": len(companies), "companies": ranked}
    return {"asOf": as_of.isoformat(), "window": {"start": start.isoformat(), "end": as_of.isoformat()},
            "fullExposureFilings": FULL_EXPOSURE_FILINGS, "topics": topics}


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure company exposure to AI-medicine topics from SEC filings")
    parser.add_argument("--as-of")
    parser.add_argument("--json-output", default=str(ROOT / "state/topic-exposure.json"))
    args = parser.parse_args()
    as_of = date.fromisoformat(args.as_of) if args.as_of else datetime.now(timezone.utc).date()
    payload = build(as_of)
    payload["generatedAt"] = datetime.now(timezone.utc).isoformat()
    Path(args.json_output).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: [t for t in list(v["companies"])[:6]] for k, v in payload["topics"].items()}, ensure_ascii=False))


if __name__ == "__main__":
    main()
