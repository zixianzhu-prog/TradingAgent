"""Primary, time-stamped sources: SEC filings per company and Federal Register rules.

Google News mostly returns aggregators and content farms (56% of company news, 2%
primary in the first week). This collector adds the documents Serenity actually
needs, straight from the source:

1. SEC filings for every covered company (8-K, 10-Q, 10-K, 6-K, 20-F) through the
   EDGAR full-text search index, which needs no contact header. 8-K item codes are
   SEC's own event taxonomy (2.02 results, 1.01 material agreement, 5.02 officer
   change, 4.02 restatement...), so filings are classified by item code instead of
   guessing from a headline. Stored in state/company-news.db; the Serenity evidence
   step fetches the filing text when SEC_USER_AGENT is set.
2. Federal Register documents from FDA, CMS and HHS that mention AI: device rules,
   guidance, Medicare payment rules. Stored in state/policy-news.db for the
   regulation and reimbursement themes.

The old www.sec.gov Atom feed in sources.ai-medicine.json returns 403 without a
contact header, so it never delivered anything; this replaces it.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import time
import urllib.parse
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import beneficiary_mapper as mapper  # noqa: E402

FORMS = "8-K,10-Q,10-K,6-K,20-F"
ITEMS = {
    "1.01": "Entry into a Material Definitive Agreement", "1.02": "Termination of a Material Definitive Agreement",
    "1.03": "Bankruptcy or Receivership", "2.01": "Completion of Acquisition or Disposition of Assets",
    "2.02": "Results of Operations and Financial Condition", "2.03": "Creation of a Direct Financial Obligation",
    "2.05": "Costs Associated with Exit or Disposal Activities", "2.06": "Material Impairments",
    "3.01": "Notice of Delisting", "3.02": "Unregistered Sales of Equity Securities",
    "4.01": "Changes in Registrant's Certifying Accountant", "4.02": "Non-Reliance on Previously Issued Financial Statements",
    "5.02": "Departure or Election of Directors or Officers", "5.03": "Amendments to Articles or Bylaws",
    "5.07": "Submission of Matters to a Vote of Security Holders", "7.01": "Regulation FD Disclosure",
    "8.01": "Other Events", "9.01": "Financial Statements and Exhibits",
}
FR_API = "https://www.federalregister.gov/api/v1/documents.json"
FR_TERMS = ['"artificial intelligence"', '"machine learning"', '"software as a service"', '"clinical decision support"']
FR_AGENCIES = {"food-and-drug-administration": "FDA", "centers-for-medicare-medicaid-services": "CMS",
               "health-and-human-services-department": "HHS"}
SCHEMA = """
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY, fingerprint TEXT NOT NULL UNIQUE, source TEXT NOT NULL, title TEXT NOT NULL,
    url TEXT NOT NULL, content TEXT NOT NULL, published_at TEXT NOT NULL, discovered_at TEXT NOT NULL
);
"""


def store(database: Path, rows: list[dict]) -> int:
    import hashlib

    database.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database)
    connection.executescript(SCHEMA)
    now = datetime.now(timezone.utc).isoformat()
    inserted = 0
    for row in rows:
        fingerprint = hashlib.sha256(row["key"].encode()).hexdigest()
        try:
            connection.execute("INSERT INTO articles (fingerprint, source, title, url, content, published_at, discovered_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                               (fingerprint, row["source"], row["title"], row["url"], row["content"], row["published_at"], now))
            inserted += 1
        except sqlite3.IntegrityError:
            pass
    connection.commit()
    connection.close()
    return inserted


def covered_ciks(root: Path = ROOT) -> dict[str, dict]:
    """Ticker -> {cik, name} for every company with a Serenity assessment."""
    sys.path.insert(0, str(root / "scripts"))
    import news_signal_engine as engine  # noqa: E402

    names = {c["ticker"]: c["name"] for c in engine.coverage(root)}
    ciks: dict[str, str] = {}
    screen_path = root / "state/ai-medicine-universe-screen.json"
    if screen_path.exists():
        for row in json.loads(screen_path.read_text(encoding="utf-8")).get("companies", []):
            for filing in row.get("filings", []):
                match = re.search(r"/edgar/data/(\d+)/", filing.get("url", ""))
                if match:
                    ciks.setdefault(row["ticker"], match.group(1))
    watch_path = root / "trend-agent/sec-companyfacts-watchlist.json"
    if watch_path.exists():
        for row in json.loads(watch_path.read_text(encoding="utf-8")).get("companies", []):
            if row.get("cik"):
                ciks.setdefault(row["ticker"], str(int(str(row["cik"]))))
    return {t: {"cik": ciks.get(t), "name": n} for t, n in names.items()}


def filing_rows(ticker: str, name: str, cik: str, start: date, end: date, fetch=mapper.http_json) -> list[dict]:
    params = urllib.parse.urlencode({"ciks": f"{int(cik):010d}", "forms": FORMS, "dateRange": "custom",
                                     "startdt": start.isoformat(), "enddt": end.isoformat()})
    payload = fetch(f"{mapper.EFTS}?{params}", mapper.DEFAULT_AGENT)
    seen: set[str] = set()
    rows = []
    for hit in payload.get("hits", {}).get("hits", []):
        src = hit.get("_source", {})
        adsh = src.get("adsh") or hit.get("_id", "").split(":")[0]
        if adsh in seen or src.get("file_type", "").upper().startswith("EX-"):
            continue
        seen.add(adsh)
        form = src.get("form", "")
        items = [i for i in src.get("items") or [] if i != "9.01"]
        described = "; ".join(f"Item {i} {ITEMS.get(i, '')}".strip() for i in items) or {"10-Q": "Quarterly report", "10-K": "Annual report",
                                                                                         "20-F": "Annual report", "6-K": "Foreign issuer report"}.get(form, form)
        rows.append({
            "key": f"sec|{adsh}",
            "source": f"SEC EDGAR · {ticker}",
            "title": f"{name} files {form}: {described}",
            "url": mapper.filing_url(cik, hit.get("_id", "")),
            "content": f"form={form} items={','.join(items)} accession={adsh} filed={src.get('file_date')} {src.get('file_description') or ''}".strip(),
            "published_at": f"{src.get('file_date')}T12:00:00+00:00",
        })
    return rows


def federal_register_rows(start: date, fetch=mapper.http_json) -> list[dict]:
    rows, seen = [], set()
    for term in FR_TERMS:
        params = [("per_page", "100"), ("order", "newest"), ("conditions[term]", term), ("conditions[publication_date][gte]", start.isoformat())]
        params += [("conditions[agencies][]", slug) for slug in FR_AGENCIES]
        payload = fetch(f"{FR_API}?{urllib.parse.urlencode(params)}", mapper.DEFAULT_AGENT)
        for doc in payload.get("results", []):
            if doc["document_number"] in seen:
                continue
            seen.add(doc["document_number"])
            slugs = [a.get("slug") for a in doc.get("agencies", [])]
            short = next((FR_AGENCIES[s] for s in ("food-and-drug-administration", "centers-for-medicare-medicaid-services") if s in slugs), "HHS")
            rows.append({
                "key": f"fr|{doc['document_number']}",
                "source": f"Federal Register · {short}",
                "title": f"{short} {doc.get('type', 'Document')}: {doc['title']}",
                # The search term is recorded so AI-dependent themes can see why the document was collected.
                # The match note comes first: theme rules read only the start of the content.
                "content": f"(Federal Register search match: {term.strip(chr(34))}) {(doc.get('abstract') or '')[:600]}",
                "url": doc.get("html_url", ""),
                "published_at": f"{doc['publication_date']}T12:00:00+00:00",
            })
        time.sleep(0.3)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect SEC filings and Federal Register rules")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--company-db", default=str(ROOT / "state/company-news.db"))
    parser.add_argument("--policy-db", default=str(ROOT / "state/policy-news.db"))
    args = parser.parse_args()
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=args.days)
    report = {"sec": {}, "missingCik": [], "federalRegister": None}
    sec_rows = []
    for ticker, meta in covered_ciks().items():
        if not meta["cik"]:
            report["missingCik"].append(ticker)
            continue
        try:
            rows = filing_rows(ticker, meta["name"], meta["cik"], start, end)
            sec_rows += rows
            report["sec"][ticker] = len(rows)
        except Exception as exc:  # one company failing must not stop the rest
            report["sec"][ticker] = f"error: {str(exc)[:80]}"
        time.sleep(0.15)
    report["secInserted"] = store(Path(args.company_db), sec_rows)
    try:
        fr_rows = federal_register_rows(start - timedelta(days=60))  # longer window gives the theme baseline
        report["federalRegister"] = {"documents": len(fr_rows), "inserted": store(Path(args.policy_db), fr_rows)}
    except Exception as exc:
        report["federalRegister"] = f"error: {str(exc)[:120]}"
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
