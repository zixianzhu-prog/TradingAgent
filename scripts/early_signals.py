"""Earlier signals: who is raising money, and what the people inside companies are doing.

A. Funding radar (SEC Form D). A private company that sells securities under Reg D must
   file Form D within 15 days of the first sale. The filing names the company, its industry
   group, the amount offered and sold, the date of first sale and its executives. This finds
   new health and biotech companies raising money before most news covers them.

B. People signals for covered companies.
   - Insider buying: open-market purchases (Form 4 code P) by officers and directors, from
     the Form 4 monitor. Sales and plan transactions are counted but not treated as signals.
   - Key departures: 8-K Item 5.02 filings whose text says a CEO, CFO, CSO, CMO, president
     or founder resigned, retired or was terminated.
   Both are written to state/company-news.db as official events, so the news engine and the
   re-check rule pick them up like any other news.

Writes state/early-signals.json. Needs SEC_USER_AGENT to download Form D and 8-K documents.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import beneficiary_mapper as mapper
import official_feeds
import serenity_evidence_review as ser

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "state/serenity-source-cache/formd"
INDUSTRIES = ["Biotechnology", "Pharmaceuticals", "Other Health Care"]
AI_NAME = re.compile(r"\b(?:ai|a\.i\.|intelligence|neural|machine|learning|cognit|compute|computational|data|algorithm|quantum|digital|insight|predict|genom|omics)\w*\b", re.I)
KEY_ROLE = re.compile(r"chief executive officer|chief financial officer|chief scientific officer|chief medical officer|chief technology officer|"
                      r"\bpresident\b|\bfounder\b|\bco-founder\b|\bceo\b|\bcfo\b|\bcso\b|\bcmo\b", re.I)
HYPOTHETICAL = re.compile(r"\bif (?:the|his|her|their|such|an?)\b|\bupon (?:\w+ ){0,3}termination\b|\bin the event\b|\bwithout .cause.|\bseverance\b|\bwould\b", re.I)
DEPARTURE = re.compile(r"\b(?:resign\w*|retire\w*|terminat\w*|step(?:ped|s)? down|depart\w*|separat\w*|will not stand for re-election|notified the company of (?:his|her|their) decision)\b", re.I)


def sec_get(url: str) -> bytes:
    agent = os.getenv("SEC_USER_AGENT", "")
    if "@" not in agent:
        raise RuntimeError("SEC_USER_AGENT with a contact email is required")
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ser.context()))
    with opener.open(urllib.request.Request(url, headers={"User-Agent": agent}), timeout=40) as response:
        return response.read()


# ---------------------------------------------------------------- A. Form D
def form_d_hits(start: date, end: date, fetch=mapper.http_json) -> list[dict]:
    hits, seen = [], set()
    for industry in INDUSTRIES:
        offset = 0
        while offset < 1000:
            params = urllib.parse.urlencode({"q": f'"{industry}"', "forms": "D", "dateRange": "custom",
                                             "startdt": start.isoformat(), "enddt": end.isoformat(), "from": offset})
            payload = fetch(f"{mapper.EFTS}?{params}", mapper.DEFAULT_AGENT)
            page = payload.get("hits", {}).get("hits", [])
            for hit in page:
                src = hit.get("_source", {})
                adsh = src.get("adsh") or hit["_id"].split(":")[0]
                if adsh in seen or src.get("form") != "D":  # new offerings only; amendments repeat old ones
                    continue
                seen.add(adsh)
                hits.append({"adsh": adsh, "cik": (src.get("ciks") or [""])[0], "filed": src.get("file_date"),
                             "name": re.sub(r"\s*\(CIK \d+\)\s*$", "", (src.get("display_names") or [""])[0]).strip(),
                             "location": (src.get("biz_locations") or [""])[0], "doc": hit["_id"].split(":")[-1]})
            offset += len(page)
            if not page or offset >= payload.get("hits", {}).get("total", {}).get("value", 0):
                break
            time.sleep(0.15)
    return hits


def parse_form_d(xml: bytes) -> dict:
    root = ET.fromstring(xml)
    text = lambda path: (root.findtext(path) or "").strip()
    number = lambda path: float(text(path)) if re.fullmatch(r"\d+(?:\.\d+)?", text(path)) else None
    people = []
    for person in root.iter("relatedPersonInfo"):
        name = " ".join(filter(None, [(person.findtext("relatedPersonName/firstName") or "").strip(),
                                      (person.findtext("relatedPersonName/lastName") or "").strip()]))
        roles = [r.text for r in person.iter("relationship") if r.text]
        if name:
            people.append({"name": name, "roles": roles})
    return {"industry": text("offeringData/industryGroup/industryGroupType"),
            "offering": number("offeringData/offeringSalesAmounts/totalOfferingAmount"),
            "sold": number("offeringData/offeringSalesAmounts/totalAmountSold"),
            "firstSale": text("offeringData/typeOfFiling/dateOfFirstSale/value"),
            "young": text("primaryIssuer/yearOfInc/withinFiveYears") == "true",
            "yearOfInc": text("primaryIssuer/yearOfInc/value"),
            "equity": text("offeringData/typesOfSecuritiesOffered/isEquityType") == "true",
            "people": people[:6]}


def frontier_titles() -> list[str]:
    """Titles and leads from the frontier-news stores, lower-cased, for name matching."""
    texts = []
    for db in ("trend-agent/state/daily-news.db", "state/radar-news.db", "state/company-news.db"):
        path = ROOT / db
        if not path.exists():
            continue
        with sqlite3.connect(path) as connection:
            texts += [f"{t} {c[:300]}".lower() for t, c in connection.execute("SELECT title, content FROM articles")]
    return texts


LEGAL_SUFFIX = {"inc", "llc", "ltd", "corp", "corporation", "co", "plc", "sa", "ag", "gmbh", "lp", "the"}


def news_mentions(name: str, texts: list[str]) -> int:
    """Frontier-news items that mention the company's full name (legal suffix dropped), e.g. "bighat biosciences".

    Matching a single word ("frontier", "contrast", "bridge") counted ordinary English, so the whole
    name must appear; one-word names need at least seven letters.
    """
    words = [w for w in re.sub(r"[^a-z0-9 ]", " ", name.lower()).split() if w not in LEGAL_SUFFIX]
    if not words or (len(words) == 1 and len(words[0]) < 7):
        return 0
    pattern = re.compile(rf"\b{re.escape(' '.join(words))}\b")
    return sum(1 for t in texts if pattern.search(t))


def funding_radar(days: int, limit: int) -> dict:
    end = date.today()
    start = end - timedelta(days=days)
    CACHE.mkdir(parents=True, exist_ok=True)
    news = frontier_titles()
    rows, errors = [], 0
    for hit in form_d_hits(start, end)[:limit]:
        path = CACHE / f"{hit['adsh']}.xml"
        try:
            if not path.exists():
                cik = str(int(hit["cik"]))
                path.write_bytes(sec_get(f"https://www.sec.gov/Archives/edgar/data/{cik}/{hit['adsh'].replace('-', '')}/{hit['doc']}"))
                time.sleep(0.12)
            detail = parse_form_d(path.read_bytes())
        except Exception:
            errors += 1
            continue
        ticker = re.search(r"\(([A-Z]{1,5})\)\s*$", hit["name"])
        name = re.sub(r"\s*\([A-Z]{1,5}\)\s*$", "", hit["name"]).strip()
        rows.append({**hit, **detail, "name": name, "listedTicker": ticker.group(1) if ticker else None,
                     "aiName": bool(AI_NAME.search(name)), "newsMentions": news_mentions(name, news),
                     "url": f"https://www.sec.gov/Archives/edgar/data/{int(hit['cik'])}/{hit['adsh'].replace('-', '')}/{hit['doc']}"})
    rows.sort(key=lambda r: -(r["sold"] or 0))
    return {"window": {"start": start.isoformat(), "end": end.isoformat()}, "industries": INDUSTRIES,
            "filings": len(rows), "errors": errors, "raisedTotal": sum(r["sold"] or 0 for r in rows), "companies": rows}


# ---------------------------------------------------------------- B. people
ROLE_ZH_TO_EN = {"高管": "Officer", "董事": "Director", "10%股东": "10% owner"}


def insider_buys(snapshot: dict, since: date) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for t in snapshot.get("marketTransactions", []):
        if not t.get("isOpenMarket") or (t.get("date") or "") < since.isoformat():
            continue
        roles = [ROLE_ZH_TO_EN.get(r, r) for r in t.get("roles", [])]
        entry = out.setdefault(t["ticker"], {"buys": [], "sellCount": 0, "sellValue": 0.0})
        if t.get("code") == "P":
            entry["buys"].append({"owner": t.get("owner"), "roles": roles, "date": t.get("date"), "shares": t.get("shares"),
                                  "price": t.get("price"), "value": t.get("value"), "url": t.get("url")})
        elif t.get("code") == "S":
            entry["sellCount"] += 1
            entry["sellValue"] += t.get("value") or 0
    return out


def key_departures(since: date, allow_fetch: bool) -> list[dict]:
    """8-K Item 5.02 filings in the company-news store whose text reports a key officer leaving."""
    import prepare_claude_review as claude

    db = ROOT / "state/company-news.db"
    if not db.exists():
        return []
    with sqlite3.connect(db) as connection:
        # Only the raw SEC records written by official_feeds ("X files 8-K: Item 5.02 ..."), not events this script wrote.
        rows = connection.execute("SELECT title, url, published_at FROM articles WHERE title LIKE '% files 8-K%Item 5.02%' AND published_at >= ?",
                                  (since.isoformat(),)).fetchall()
    out = []
    for title, url, published in rows:
        try:
            text = claude.filing_text(url, allow_fetch=allow_fetch) or ""
        except Exception:
            text = ""
        for sentence in re.split(r"(?<=[.;])\s+", text):
            # A real departure, not a compensation clause describing what happens "upon termination".
            if DEPARTURE.search(sentence) and KEY_ROLE.search(sentence) and not HYPOTHETICAL.search(sentence) and len(sentence) < 600:
                company = title.split(" files ")[0]
                out.append({"company": company, "date": published[:10], "sentence": re.sub(r"\s+", " ", sentence).strip(), "url": url})
                break
    return out


def people_events(buys: dict[str, dict], departures: list[dict], names: dict[str, str]) -> list[dict]:
    """Official events for the news store: insider buys and key departures."""
    rows = []
    for ticker, entry in buys.items():
        for b in entry["buys"]:
            who = ", ".join(r for r in b["roles"] if r not in {"Officer"}) or "insider"
            rows.append({"key": f"form4-buy|{b['url']}", "source": "SEC Form 4 (sec.gov)",
                         "title": f"{names.get(ticker, ticker)} {who} {b['owner']} bought {int(b['shares'] or 0):,} shares in the open market (${(b['value'] or 0):,.0f}) - sec.gov",
                         "url": b["url"], "content": "(SEC Form 4, transaction code P: open-market purchase.)",
                         "published_at": f"{b['date']}T00:00:00+00:00"})
    for d in departures:
        rows.append({"key": f"8k-502|{d['url']}", "source": "SEC EDGAR 8-K (sec.gov)",
                     "title": f"{d['company']} key officer resigns or departs (8-K Item 5.02) - sec.gov",
                     "url": d["url"], "content": f"(SEC 8-K Item 5.02: {d['sentence'][:300]})", "published_at": f"{d['date']}T00:00:00+00:00"})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Form D funding radar and people signals")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--limit", type=int, default=250)
    args = parser.parse_args()
    allow_fetch = "@" in os.getenv("SEC_USER_AGENT", "")
    since = date.today() - timedelta(days=args.days)
    radar = funding_radar(args.days, args.limit) if allow_fetch else {"skipped": "SEC_USER_AGENT not set"}
    snapshot = json.loads((ROOT / "state/form4-snapshot.json").read_text(encoding="utf-8")) if (ROOT / "state/form4-snapshot.json").exists() else {}
    buys = insider_buys(snapshot, since)
    departures = key_departures(since, allow_fetch)
    names = {t: v["name"] for t, v in official_feeds.covered_ciks().items()}
    inserted = official_feeds.store(ROOT / "state/company-news.db", people_events(buys, departures, names))
    payload = {"generatedAt": datetime.now(timezone.utc).isoformat(), "fundingRadar": radar,
               "people": {"since": since.isoformat(), "insiderTrades": buys, "keyDepartures": departures}, "eventsAdded": inserted}
    (ROOT / "state/early-signals.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"formD": radar.get("filings"), "raised": radar.get("raisedTotal"), "insiderBuyers": sum(len(v["buys"]) for v in buys.values()),
                      "departures": len(departures), "eventsAdded": inserted}))


if __name__ == "__main__":
    main()
