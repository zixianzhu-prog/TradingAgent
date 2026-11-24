"""Paper -> author -> inventor -> patent owner -> company, from official records.

People come from three sources already in the project: founders and scientists in the Form 3/4/5 roster
(state/key-people.json), founders named in each 10-K (state/science-founders.json), and the most frequent company
authors of recent papers (state/company-research.json, OpenAlex). Each person is searched as an inventor in the
USPTO Open Data Portal. Every application found is classified by its first applicant:

* company   the company itself (the person invents for the company)
* licensor  a university or institute the company's 10-K says it licenses from (the technology came from that lab)
* other     anyone else; with a common name this may be a different person, so it is reported but never counted

A link counts only for company or licensor applicants, where the filing context confirms the person. Results are
cached per query; the API key is read from USPTO_API_KEY and goes only into the request header.

    USPTO_API_KEY=... python3 scripts/inventor_chain.py
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import serenity_evidence_review as ser
import uspto_assignment_validation as usv

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "state/serenity-source-cache/uspto-inventors"
OUTPUT = ROOT / "state/inventor-chain.json"
REPORT = ROOT / "outputs/inventor-chain.md"
KEY_PEOPLE = ROOT / "state/key-people.json"
FOUNDERS = ROOT / "state/science-founders.json"
RESEARCH = ROOT / "state/company-research.json"
AUTHORS_PER_COMPANY = 3
PAUSE = 1.6  # the portal answers 429 to bursts
STOP = {"university", "of", "the", "and", "for", "research", "foundation", "inc", "institute", "trustees", "regents"}


def load(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def plain(name: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z ]", " ", (name or "").lower())).strip()


def people_by_company(key_people: dict, founders: dict, research: dict) -> dict[str, dict[str, set[str]]]:
    """{ticker: {person name: {roles}}} from the roster, 10-K founders and frequent paper authors."""
    out: dict[str, dict[str, set[str]]] = {}
    companies = key_people.get("companies", {})
    for ticker, c in (companies.items() if isinstance(companies, dict) else []):
        for p in c.get("people", []):
            if p.get("founder") or p.get("scientist"):
                out.setdefault(ticker, {}).setdefault(p["name"], set()).add("founder" if p.get("founder") else "scientist")
    for link in founders.get("links", []):
        if link.get("relation") == "founder" and link.get("person"):
            out.setdefault(link["ticker"], {}).setdefault(link["person"], set()).add("founder (10-K)")
    rows = research.get("companies", {})
    for ticker, c in (rows.items() if isinstance(rows, dict) else []):
        counts = Counter(a for w in c.get("topWorks", []) for a in w.get("companyAuthors", []))
        for name, _ in counts.most_common(AUTHORS_PER_COMPANY):
            out.setdefault(ticker, {}).setdefault(name, set()).add("paper author")
    # One person under two spellings ("Eric P Lefkofsky", "Eric Lefkofsky") is searched and shown once.
    for ticker, persons in out.items():
        merged: dict[str, tuple[str, set[str]]] = {}
        for name, roles in persons.items():
            key = search_name(name).lower()
            keep, have = merged.get(key, (name, set()))
            merged[key] = (keep if len(keep) >= len(name) else name, have | roles)
        out[ticker] = {name: roles for name, roles in merged.values()}
    return out


def search_name(name: str) -> str:
    """First and last name only: the portal stores 'Eric P. Lefkofsky' and 'Eric Lefkofsky' alike under the full text."""
    parts = [p for p in re.sub(r"[.,]", " ", name).split() if len(p) > 1 and p.lower() not in {"jr", "sr", "ii", "iii", "md", "phd"}]
    if len(parts) >= 2:
        return f"{parts[0]} {parts[-1]}"
    return name


def inventor_apps(name: str, key: str, fetch=usv.odp_get, cache_dir: Path = CACHE, limit: int = 50) -> list[dict]:
    q = f'applicationMetaData.inventorBag.inventorNameText:"{search_name(name)}"'
    path = cache_dir / (ser.digest(q) + ".json")
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    found = {}
    for attempt in range(5):
        url = f"{usv.ODP}/search?" + urllib.parse.urlencode({"q": q, "limit": limit})
        try:
            found = fetch(url, key)
            break
        except urllib.error.HTTPError as exc:
            if exc.code == 413 and limit > 10:  # response too large: ask for fewer records
                limit //= 2
                continue
            if exc.code != 429 or attempt == 4:
                raise
            time.sleep(PAUSE * (attempt + 2) * 2)
    apps = []
    for a in found.get("patentFileWrapperDataBag", []):
        m = a.get("applicationMetaData", {})
        apps.append({"number": a.get("applicationNumberText"), "applicant": m.get("firstApplicantName") or "",
                     "title": m.get("inventionTitle") or "", "filed": m.get("filingDate"), "patent": m.get("patentNumber"),
                     "inventors": [i.get("inventorNameText") for i in m.get("inventorBag", [])]})
    cache_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(apps, ensure_ascii=False), encoding="utf-8")
    return apps


def words(name: str) -> set[str]:
    return {w for w in plain(usv.base_name(name)).split() if w not in STOP and len(w) > 2}


def classify(applicant: str, company: str, licensors: list[str]) -> tuple[str, str | None]:
    a = words(applicant)
    if not a:
        return "other", None
    c = words(company)
    if c and (c <= a or (next(iter(sorted(c, key=len, reverse=True))) in a)):
        return "company", None
    for lic in licensors:
        lw = words(lic)
        if lw and (lw <= a or a <= lw):
            return "licensor", lic
    return "other", None


def build(people: dict, names: dict[str, str], licensors: dict[str, list[str]], lookup) -> dict:
    companies = {}
    for ticker, persons in sorted(people.items()):
        rows = []
        for person, roles in sorted(persons.items()):
            apps = lookup(person)
            buckets: dict[str, list[dict]] = {"company": [], "licensor": [], "other": []}
            for app in apps:
                kind, lic = classify(app["applicant"], names.get(ticker, ticker), licensors.get(ticker, []))
                buckets[kind].append({**app, "licensor": lic} if lic else app)
            if not any(buckets.values()):
                continue
            rows.append({"person": person, "roles": sorted(roles), "companyPatents": len(buckets["company"]),
                         "licensorPatents": len(buckets["licensor"]), "otherNameMatches": len(buckets["other"]),
                         "licensors": sorted({a["licensor"] for a in buckets["licensor"]}),
                         "examples": [{k: a.get(k) for k in ("number", "applicant", "title", "filed", "patent")}
                                      for a in (buckets["licensor"] + buckets["company"])[:4]]})
        rows.sort(key=lambda r: (-r["licensorPatents"], -r["companyPatents"]))
        companies[ticker] = {"company": names.get(ticker, ticker), "licensorsIn10K": licensors.get(ticker, []),
                             "people": rows,
                             "inventorsAtCompany": sum(r["companyPatents"] > 0 for r in rows),
                             "labToCompany": [r for r in rows if r["licensorPatents"]]}
    summary = {"companies": len(companies), "peopleSearched": sum(len(p) for p in people.values()),
               "inventorsAtCompany": sum(c["inventorsAtCompany"] for c in companies.values()),
               "labToCompanyLinks": sum(len(c["labToCompany"]) for c in companies.values())}
    return {"generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"), "method": __doc__.split("\n\n")[1].strip(),
            "summary": summary, "companies": companies}


def render(payload: dict) -> str:
    s = payload["summary"]
    lines = ["# 论文作者 → 专利发明人 → 公司（USPTO）", "", f"生成：{payload['generatedAt']}", "",
             f"检索 {s['peopleSearched']} 人；{s['inventorsAtCompany']} 人是本公司专利的发明人；"
             f"{s['labToCompanyLinks']} 人是 10-K 所列授权方（大学/研究所）专利的发明人，即技术来自该实验室的直接证据。", "",
             "> 只有申请人是公司本身或 10-K 披露的授权方时才算同一人；其他同名记录只计数，不作为证据。", ""]
    for ticker, c in payload["companies"].items():
        if not c["people"]:
            continue
        lines += [f"## {ticker} · {c['company']}", ""]
        if c["licensorsIn10K"]:
            lines.append(f"10-K 授权方：{'；'.join(sorted(set(c['licensorsIn10K'])))}")
        lines += ["", "| 人物 | 身份 | 公司专利 | 授权方专利 | 仅同名 | 例子 |", "|---|---|---:|---:|---:|---|"]
        for r in c["people"]:
            ex = "；".join(f"{e['number']} {e['applicant']}：{e['title'][:50]}" for e in r["examples"][:2])
            lines.append(f"| {r['person']} | {'、'.join(r['roles'])} | {r['companyPatents']} | {r['licensorPatents']} | {r['otherNameMatches']} | {ex} |")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    key = os.getenv("USPTO_API_KEY", "").strip()
    if not key:
        prev = load(OUTPUT, None)
        print(json.dumps({"note": "USPTO_API_KEY not set; keeping the last result", "have": bool(prev)}))
        return
    people = people_by_company(load(KEY_PEOPLE, {}), load(FOUNDERS, {}), load(RESEARCH, {}))
    names = {t: c.get("company", t) for t, c in (load(KEY_PEOPLE, {}).get("companies", {}) or {}).items()}
    names.update({t: c.get("company", t) for t, c in (load(RESEARCH, {}).get("companies", {}) or {}).items() if t not in names})
    licensors: dict[str, list[str]] = {}
    for link in load(FOUNDERS, {}).get("links", []):
        if link.get("relation") in ("license", "sponsored_research") and link.get("institution"):
            licensors.setdefault(link["ticker"], []).append(link["institution"])

    failed: list[str] = []

    def lookup(person):
        cached = (CACHE / (ser.digest(f'applicationMetaData.inventorBag.inventorNameText:"{search_name(person)}"') + ".json")).exists()
        try:
            apps = inventor_apps(person, key)
        except urllib.error.HTTPError as exc:  # one person failing must not stop the rest
            failed.append(f"{person} ({exc.code})")
            apps = []
        if not cached:
            time.sleep(PAUSE)
        return apps

    payload = build(people, names, licensors, lookup)
    payload["summary"]["failedLookups"] = failed
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT.write_text(render(payload), encoding="utf-8")
    print(json.dumps(payload["summary"]))


if __name__ == "__main__":
    main()
