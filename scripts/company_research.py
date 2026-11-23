"""Papers a company publishes itself: OpenAlex works whose authors list the company as their institution.

The lab-to-company chain needs a "discovery" link: evidence the company does science that shows up in the
literature. The frontier agent only finds the rare recent paper that names a company. This asks the
other way round: OpenAlex keeps company institutions (type "company"), and every work an employee
authors is tagged with it. The company's research output, its most-cited recent papers and the scientists
on them are then primary, checkable evidence.

Matching is strict: the institution's name, without the country in parentheses and generic words
(Labs, AI, Therapeutics...), must be made of words in the company's name, its first word must match, and
exactly one OpenAlex company must pass. No model calls.

    python3 scripts/company_research.py [--tickers RXRX TEM]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.parse
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "state/company-research.json"
REPORT = ROOT / "outputs/company-research.md"
API = "https://api.openalex.org"
GENERIC = {"inc", "corp", "corporation", "co", "ltd", "limited", "plc", "llc", "nv", "sa", "ag", "holdings", "holding", "group",
           "the", "labs", "lab", "laboratories", "ai", "therapeutics", "pharmaceuticals", "pharmaceutical", "pharma",
           "biosciences", "bioscience", "bio", "biotherapeutics", "health", "healthcare", "medical", "technologies",
           "technology", "genetics", "biologics", "sciences", "science", "diagnostics", "international", "global",
           "and", "of", "deephealth"}
MIN_WORKS = 3


def words(name: str) -> list[str]:
    name = re.sub(r"\([^)]*\)", " ", name or "").lower().replace("&", " and ")
    return [w for w in re.split(r"[^a-z0-9]+", name) if w]


def core(name: str) -> list[str]:
    return [w for w in words(name) if w not in GENERIC]


LOOSE = {"inc", "corp", "corporation", "co", "ltd", "limited", "plc", "llc", "the", "labs", "lab", "laboratories"}


def matches(company: str, institution: str) -> bool:
    """First distinctive word equal, and every institution word (bar legal suffixes and Labs) in the company name."""
    c, i = core(company), core(institution)
    return bool(c and i and c[0] == i[0] and set(words(institution)) - LOOSE <= set(words(company)))


def find_institution(company: str, fetch) -> dict | None:
    query = " ".join(core(company)) or company
    url = f"{API}/institutions?" + urllib.parse.urlencode({"search": query, "filter": "type:company", "per-page": 10})
    found = [r for r in fetch(url).get("results", []) if matches(company, r.get("display_name", ""))]
    return found[0] if len(found) == 1 else None


def recent_works(inst_id: str, since: str, fetch, top: int = 5) -> tuple[int, list[dict]]:
    short = inst_id.rsplit("/", 1)[-1]
    url = f"{API}/works?" + urllib.parse.urlencode({"filter": f"institutions.id:{short},from_publication_date:{since}",
                                                    "sort": "cited_by_count:desc", "per-page": top})
    data = fetch(url)
    out = []
    for w in data.get("results", []):
        staff = [a.get("author", {}).get("display_name") for a in w.get("authorships", [])
                 if any((i.get("id") or "").endswith(short) for i in a.get("institutions", []))]
        out.append({"title": w.get("display_name") or w.get("title"), "doi": w.get("doi"), "id": w.get("id"),
                    "published": w.get("publication_date"), "citedBy": w.get("cited_by_count"),
                    "venue": ((w.get("primary_location") or {}).get("source") or {}).get("display_name"),
                    "companyAuthors": [s for s in staff if s][:4]})
    return int((data.get("meta") or {}).get("count") or 0), out


def universe() -> dict[str, str]:
    theme = json.loads((ROOT / "trend-agent/theme-company-map.json").read_text(encoding="utf-8"))
    path = ROOT / "state/small-cap-stage.json"
    small = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"companies": []}
    names = {r["ticker"]: r.get("company", r["ticker"]) for r in theme["themes"]["ai_medicine"] + small["companies"]}
    names.pop("NVDA", None)
    return names


class BudgetExhausted(Exception):
    """OpenAlex daily budget used up: stop now, keep last results (retrying only burns time)."""


def build(names: dict[str, str], fetch, today: date, previous: dict | None = None) -> dict:
    since = (today - timedelta(days=3 * 365)).isoformat()
    prev = (previous or {}).get("companies", {})
    unmatched = (previous or {}).get("unmatched", {})
    companies, misses, errors = {}, {}, []
    for t, company in sorted(names.items()):
        try:
            if t in prev and prev[t].get("company") == company:
                inst = {"id": prev[t]["openalexId"], "display_name": prev[t]["institution"], "country_code": prev[t].get("country")}
            elif unmatched.get(t, {}).get("company") == company and \
                    (today - date.fromisoformat(unmatched[t]["checked"])).days < 30:
                misses[t] = unmatched[t]  # searched recently with no unique match; search again monthly
                continue
            else:
                inst = find_institution(company, fetch)
            if not inst:
                misses[t] = {"company": company, "checked": today.isoformat()}
                continue
            count, works = recent_works(inst["id"], since, fetch)
            companies[t] = {"company": company, "institution": inst.get("display_name"), "openalexId": inst.get("id"),
                            "country": inst.get("country_code"), "worksSince": since, "recentWorks": count, "topWorks": works,
                            "verified": count >= MIN_WORKS}
        except BudgetExhausted:
            errors.append(f"{t}: OpenAlex daily budget used up")
            for rest in sorted(names):  # keep everything not yet refreshed
                if rest not in companies and rest in prev:
                    companies[rest] = prev[rest]
            misses.update({k: v for k, v in unmatched.items() if k not in misses and k not in companies})
            break
        except Exception as exc:
            errors.append(f"{t}: {type(exc).__name__}")
            if t in prev:
                companies[t] = prev[t]
        time.sleep(0.1)
    return {"generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "method": "OpenAlex company institutions matched strictly by name (unique match only); works since three years ago, most cited first.",
            "summary": {"companies": len(names), "matched": len(companies), "verified": sum(c["verified"] for c in companies.values()),
                        "errors": errors},
            "companies": companies, "unmatched": misses}


def render(p: dict) -> str:
    s = p["summary"]
    lines = ["# 公司自己发表的研究（OpenAlex）", "",
             f"> {s['companies']} 家公司中 {s['matched']} 家在 OpenAlex 有唯一匹配的公司机构；{s['verified']} 家近 3 年有 ≥{MIN_WORKS} 篇员工署名论文。",
             "> 只证明公司在做可发表的研究，不证明某篇论文变成了产品。", "",
             "| 公司 | OpenAlex 机构 | 近 3 年论文 | 引用最多的一篇 | 公司作者 |", "|---|---|---:|---|---|"]
    for t, c in sorted(p["companies"].items(), key=lambda kv: -kv[1]["recentWorks"]):
        w = (c["topWorks"] or [{}])[0]
        title = f"[{(w.get('title') or '')[:70]}]({w.get('doi') or w.get('id')}) ({(w.get('published') or '')[:4]}, 引用 {w.get('citedBy')})" if w else "—"
        lines.append(f"| {t} | {c['institution']} | {c['recentWorks']} | {title} | {', '.join(w.get('companyAuthors') or []) or '—'} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--tickers", nargs="*")
    args = parser.parse_args()
    import beneficiary_mapper as mapper

    names = universe()
    if args.tickers:
        names = {t: n for t, n in names.items() if t in args.tickers}
    key = os.getenv("OPENALEX_API_KEY", "").strip()  # optional, own budget; read from the environment only

    def fetch(url: str, tries: int = 3) -> dict:
        if key:
            url += "&api_key=" + urllib.parse.quote(key)
        for n in range(tries):
            try:
                return mapper.http_json(url, "serenity-research-agent", retries=0)
            except urllib.error.HTTPError as exc:
                if exc.code == 429 and "daily_budget" in exc.read().decode("utf-8", "replace"):
                    raise BudgetExhausted() from None
                if n == tries - 1:
                    raise
                time.sleep(2 ** n * 2)
        return {}

    previous = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {"companies": {}}
    payload = build(names, fetch, date.today(), previous)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT.write_text(render(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
