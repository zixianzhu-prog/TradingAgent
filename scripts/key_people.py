"""Key people at each covered company: who they are, what they publish, and who has just left.

Peter: "track the company's core people; follow what they publish and the industry meetings". LinkedIn forbids
automated collection, so this builds everything else from public records and hands over a follow list:

1. Roster: officers and directors who filed SEC Forms 3/4/5 in the last four quarters (SEC Insider
   Transactions Data Sets carry each filer's officer title), plus founders quoted from the company's 10-K
   (state/science-founders.json). Key roles: CEO, president, scientific/medical/technology/business/financial
   chiefs, founders, chair.
2. Papers: PubMed, for scientific roles only (chief scientific/medical/technology officer, R&D head, founder):
   articles in the last three years where the author name AND the company as affiliation both match, so a
   namesake elsewhere does not count. Free, no daily quota.
3. Changes: departures from the management radar (8-K Item 5.02).
4. A LinkedIn search link per person, to follow by hand. Nothing is fetched from LinkedIn.

    SEC_USER_AGENT="Name email" python3 scripts/key_people.py
"""
from __future__ import annotations

import csv
import io
import json
import os
import re
import sys
import time
import urllib.parse
import zipfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "state/serenity-source-cache/form345-roster"
OUT = ROOT / "state/key-people.json"
REPORT = ROOT / "outputs/key-people.md"
INDEX = "https://www.sec.gov/data-research/sec-markets-data/insider-transactions-data-sets"
PUBMED = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
KEY = re.compile(r"chief executive|\bceo\b|president|chief scientific|\bcso\b|chief medical|\bcmo\b|chief technology|\bcto\b|"
                 r"chief business|chief financial|\bcfo\b|chief operating|\bcoo\b|research and development|r&d|founder|chair", re.I)
SCIENCE = re.compile(r"chief scientific|\bcso\b|chief medical|\bcmo\b|chief technology|\bcto\b|research and development|r&d|founder", re.I)
NON_RESEARCH = re.compile(r"financial|\bcfo\b|operating|\bcoo\b|business|commercial|counsel|legal|accounting|"
                          r"people|human|administrative|compliance|investor|treasurer|secretary", re.I)
NAME_SUFFIX = re.compile(r"\b(jr|sr|ii|iii|iv|md|phd|m\.d|ph\.d)\.?$", re.I)
csv.field_size_limit(10**8)


def rows(z: zipfile.ZipFile, name: str):
    with z.open(name) as fh:
        yield from csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8", errors="replace"), delimiter="\t")


def roster_from_zip(blob: bytes, ciks: set[str]) -> list[dict]:
    """Officers/directors of covered issuers in one quarterly Forms 3/4/5 data set."""
    z = zipfile.ZipFile(io.BytesIO(blob))
    subs = {}
    for r in rows(z, "SUBMISSION.tsv"):
        cik = str(int(r["ISSUERCIK"])) if r["ISSUERCIK"].strip().isdigit() else None
        if cik in ciks:
            subs[r["ACCESSION_NUMBER"]] = (cik, datetime.strptime(r["FILING_DATE"], "%d-%b-%Y").date().isoformat())
    out = []
    for r in rows(z, "REPORTINGOWNER.tsv"):
        s = subs.get(r["ACCESSION_NUMBER"])
        rel = r["RPTOWNER_RELATIONSHIP"] or ""
        if not s or not re.search(r"Officer|Director", rel):
            continue
        out.append({"cik": s[0], "filed": s[1], "ownerCik": r["RPTOWNERCIK"], "name": r["RPTOWNERNAME"],
                    "relationship": rel, "title": (r["RPTOWNER_TITLE"] or "").strip()})
    return out


def display_name(sec_name: str) -> str:
    """SEC lists 'Last First Middle'; show 'First Middle Last'."""
    parts = [p for p in re.split(r"\s+", sec_name.replace(",", " ").strip()) if p and not NAME_SUFFIX.fullmatch(p)]
    if len(parts) < 2:
        return sec_name.title()
    return " ".join([*parts[1:], parts[0]]).title()


def pubmed_author(name: str) -> str:
    """'First Middle Last' -> 'Last FM' (PubMed author field)."""
    parts = name.split()
    return f"{parts[-1]} {''.join(p[0] for p in parts[:-1])}" if len(parts) >= 2 else name


def merge_roster(raw: list[dict]) -> dict[str, list[dict]]:
    """One entry per (company, person): latest title, first and last filing seen."""
    people: dict[tuple, dict] = {}
    for r in sorted(raw, key=lambda x: x["filed"]):
        key = (r["cik"], r["ownerCik"])
        p = people.setdefault(key, {"name": display_name(r["name"]), "ownerCik": r["ownerCik"], "firstSeen": r["filed"],
                                    "title": "", "relationship": r["relationship"]})
        p["lastSeen"] = r["filed"]
        if r["title"]:
            p["title"] = r["title"]
        p["relationship"] = r["relationship"]
    out: dict[str, list[dict]] = {}
    for (cik, _), p in people.items():
        p["key"] = bool(KEY.search(p["title"])) or ("Officer" in p["relationship"] and not p["title"])
        p["scientist"] = bool(SCIENCE.search(p["title"]))
        out.setdefault(cik, []).append(p)
    return out


def company_term(company: str) -> str:
    """Distinctive part of the company name as papers write it ('Recursion', not 'Recursion Pharmaceuticals')."""
    words = [w for w in re.split(r"[^A-Za-z0-9]+", company) if w and w.lower() not in
             {"inc", "corp", "corporation", "co", "ltd", "plc", "llc", "nv", "the", "holdings", "group", "sa", "ag"}]
    if not words:
        return company
    return words[0] if len(words[0]) >= 5 else " ".join(words[:2])


def person_key(name: str) -> str:
    """First and last name, accents and middle names dropped: 'Carl L. G. Hansen' == 'Carl Hansen'."""
    import unicodedata
    plain = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    parts = [w for w in re.split(r"[^a-z]+", plain) if len(w) > 1]
    return f"{parts[0]} {parts[-1]}" if len(parts) >= 2 else plain


def papers(name: str, company: str, fetch, since_year: int) -> dict:
    term = f'{pubmed_author(name)}[Author] AND "{company_term(company)}"[Affiliation] AND {since_year}:3000[pdat]'
    found = fetch(f"{PUBMED}/esearch.fcgi?" + urllib.parse.urlencode({"db": "pubmed", "retmode": "json", "retmax": 3, "sort": "pub_date", "term": term}))
    ids = found.get("esearchresult", {}).get("idlist", [])
    count = int(found.get("esearchresult", {}).get("count") or 0)
    top = []
    if ids:
        summ = fetch(f"{PUBMED}/esummary.fcgi?" + urllib.parse.urlencode({"db": "pubmed", "retmode": "json", "id": ",".join(ids)}))
        for i in ids:
            s = summ.get("result", {}).get(i, {})
            top.append({"pmid": i, "title": s.get("title"), "journal": s.get("source"), "date": s.get("pubdate"),
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{i}/"})
    return {"count": count, "recent": top, "query": term}


def linkedin_link(name: str, company: str) -> str:
    return "https://www.linkedin.com/search/results/people/?" + urllib.parse.urlencode({"keywords": f"{name} {company_term(company)}"})


def build(universe: dict[str, tuple[str, str]], roster: dict[str, list[dict]], founders: list[dict],
          departures: dict[str, list[dict]], fetch, today: date) -> dict:
    since_year = today.year - 3
    companies = {}
    for t, (cik, company) in sorted(universe.items()):
        people = [dict(p) for p in roster.get(cik, []) if p["key"]]
        known = {person_key(p["name"]): p for p in people}
        for f in founders:
            if f.get("ticker") != t or not f.get("person"):
                continue
            hit = known.get(person_key(f["person"]))
            if hit:
                hit["founder"], hit["founderSource"] = True, f.get("url")
                continue
            new = {"name": f["person"], "title": "Founder (10-K)", "key": True, "scientist": True, "founder": True,
                   "founderSource": f.get("url"), "firstSeen": None, "lastSeen": None}
            people.append(new)
            known[person_key(f["person"])] = new
        for p in people:
            p["linkedin"] = linkedin_link(p["name"], company)
            if not NON_RESEARCH.search(p.get("title") or ""):
                try:
                    p["papers"] = papers(p["name"], company, fetch, since_year)
                except Exception as exc:
                    p["papers"] = {"error": type(exc).__name__}
                time.sleep(0.35)  # PubMed: 3 requests a second without a key
        if people or departures.get(t):
            # Latest filer first, then CEO, then research roles: a successor CEO outranks the one who left.
            people.sort(key=lambda p: p.get("lastSeen") or "", reverse=True)
            people.sort(key=lambda p: (not re.search(r"chief executive|\bceo\b", p["title"], re.I), NON_RESEARCH.search(p["title"] or "") is not None))
            companies[t] = {"company": company, "people": people, "departures": departures.get(t, [])}
    return {"generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "method": "SEC Forms 3/4/5 filer titles (last four quarterly data sets) + founders quoted from 10-Ks; PubMed articles "
                      "matching author name and company affiliation since " + str(since_year) + "; departures from 8-K Item 5.02. "
                      "LinkedIn is linked for manual follow, never fetched.",
            "summary": {"companies": len(companies), "keyPeople": sum(len(c["people"]) for c in companies.values()),
                        "scientists": sum(bool(p.get("scientist")) for c in companies.values() for p in c["people"]),
                        "searched": sum("papers" in p for c in companies.values() for p in c["people"]),
                        "withPapers": sum((p.get("papers") or {}).get("count", 0) > 0 for c in companies.values() for p in c["people"]),
                        "departures": sum(len(c["departures"]) for c in companies.values())},
            "companies": companies}


def render(p: dict) -> str:
    s = p["summary"]
    lines = ["# 核心人物跟踪", "", f"> {s['companies']} 家公司、{s['keyPeople']} 位核心人物（其中科研岗位 {s['scientists']} 位，"
             f"{s['withPapers']} 位近 3 年有以该公司署名的论文）；近期离职 {s['departures']} 起。", "",
             "> 来源：SEC Form 3/4/5 申报人职务（近四个季度）+ 10-K 中的创始人；论文来自 PubMed（作者名与公司署名同时匹配）。"
             "LinkedIn 不允许自动抓取，下表每人附 LinkedIn 搜索链接，供人工关注。", ""]
    for t, c in p["companies"].items():
        lines += [f"## {t} · {c['company']}", "", "| 人物 | 职务 | 最近申报 | 近 3 年论文 | 最近一篇 | LinkedIn |", "|---|---|---|---:|---|---|"]
        for x in c["people"]:
            pp = x.get("papers") or {}
            recent = (pp.get("recent") or [{}])[0]
            last = f"[{(recent.get('title') or '')[:60]}]({recent.get('url')})" if recent.get("url") else "—"
            title = (x["title"] or "高管") + ("（创始人）" if x.get("founder") and "Founder" not in (x["title"] or "") else "")
            lines.append(f"| {x['name']} | {title} | {x.get('lastSeen') or '—'} | {pp.get('count', '—')} | {last} | [搜索]({x['linkedin']}) |")
        for d in c["departures"]:
            lines.append(f"| ⚠ 离职 | {d.get('date')} {d.get('title')} | | | [{(d.get('detail') or '')[:60]}]({d.get('url')}) | |")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    agent = os.getenv("SEC_USER_AGENT", "")
    if "@" not in agent:
        sys.exit("Set SEC_USER_AGENT with your contact email (SEC fair-access policy).")
    import beneficiary_mapper as mapper
    import insider_buy_study as ibs

    theme = json.loads((ROOT / "trend-agent/theme-company-map.json").read_text(encoding="utf-8"))
    small_path = ROOT / "state/small-cap-stage.json"
    small = json.loads(small_path.read_text(encoding="utf-8")) if small_path.exists() else {"companies": []}
    names = {r["ticker"]: r.get("company", r["ticker"]) for r in theme["themes"]["ai_medicine"] + small["companies"]}
    names.pop("NVDA", None)
    ciks = {str(r["ticker"]).upper(): str(r["cik_str"]) for r in mapper.http_json("https://www.sec.gov/files/company_tickers.json", agent).values()}
    universe = {t: (ciks[t], n) for t, n in names.items() if t in ciks}

    page = ibs.get(INDEX, agent).decode("utf-8", "replace")
    links = sorted(((m.group(2), m.group(1)) for m in re.finditer(r'href="([^"]*/(\d{4}q\d)_form345\.zip)"', page)), reverse=True)[:4]
    CACHE.mkdir(parents=True, exist_ok=True)
    wanted = {c for c, _ in universe.values()}
    raw = []
    for q, link in links:
        path = CACHE / f"{q}-roster.json"
        cached = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
        if cached is None or set(cached.get("ciks", [])) != wanted:
            cached = {"ciks": sorted(wanted), "rows": roster_from_zip(ibs.get("https://www.sec.gov" + link, agent), wanted)}
            path.write_text(json.dumps(cached), encoding="utf-8")
        raw += cached["rows"]
        print(f"  {q}: {len(cached['rows'])} officer/director filings")
    founders = json.loads((ROOT / "state/science-founders.json").read_text(encoding="utf-8")).get("links", []) \
        if (ROOT / "state/science-founders.json").exists() else []
    radar = json.loads((ROOT / "state/management-radar.json").read_text(encoding="utf-8")) if (ROOT / "state/management-radar.json").exists() else {}
    departures = {c["ticker"]: [e for e in c.get("timeline", []) if e.get("type") == "key_departure"] for c in radar.get("companies", [])}
    payload = build(universe, merge_roster(raw), founders, departures,
                    lambda url: mapper.http_json(url, "serenity-research-agent"), date.today())
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT.write_text(render(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
