"""Quarterly 13F holdings of specialist biotech funds in the companies this project follows.

13D/13G only appear when a holder crosses 5%; 13F shows every quarter-end position of funds managing over $100M, so
it catches adds and trims below the threshold. For each specialist fund (the same list as the 13D/13G radar) the
script finds its 13F filer CIK on EDGAR, reads the information tables of its two latest 13F-HR filings, matches
issuers to covered companies by name, and reports new, added, trimmed and exited positions.

Limits: 13F is filed up to 45 days after quarter end, so it shows what a fund held, not what it holds now; it lists
long US-listed equity and options only; issuer matching is by name (CUSIP-to-ticker maps are not free).

    SEC_USER_AGENT="Name email" python3 scripts/fund_13f.py
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import beneficiary_mapper as mapper

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "state/fund-13f.json"
REPORT = ROOT / "outputs/fund-13f.md"
CACHE = ROOT / "state/serenity-source-cache/13f"
THEME = ROOT / "trend-agent/theme-company-map.json"
SMALL = ROOT / "state/small-cap-stage.json"
FILTER = ROOT / "state/candidate-filter.json"
# Search name -> words the EDGAR entity name must contain.
FUNDS = {
    "RA Capital Management": "ra capital", "Baker Bros. Advisors": "baker bros", "Perceptive Advisors": "perceptive",
    "RTW Investments": "rtw", "Deerfield Management": "deerfield", "OrbiMed Advisors": "orbimed", "EcoR1 Capital": "ecor1",
    "Avoro Capital": "avoro", "Biotechnology Value Fund": "biotechnology value", "Vivo Capital": "vivo capital",
    "Fairmount Funds Management": "fairmount", "Commodore Capital": "commodore", "TCG Crossover Management": "tcg crossover",
    "Cormorant Asset Management": "cormorant", "Logos Global Management": "logos", "Boxer Capital": "boxer",
    "Suvretta Capital": "suvretta", "Adage Capital": "adage", "Samsara BioCapital": "samsara", "Casdin Capital": "casdin",
    "Ally Bridge Group": "ally bridge", "Redmile Group": "redmile", "Rock Springs Capital": "rock springs",
    "Vestal Point Capital": "vestal point", "Darwin Global Management": "darwin", "Siren Capital": "siren",
    "Great Point Partners": "great point", "Octagon Capital": "octagon", "Frazier Life Sciences": "frazier",
    "Foresite Capital": "foresite", "Viking Global Investors": "viking global",
}
SUFFIX = re.compile(r"\b(inc|corp|corporation|co|ltd|plc|holdings?|sa|nv|ag|class [a-z]|com|common|new|ordinary|shs|shares)\b\.?")


def load(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def norm(name: str) -> str:
    text = re.sub(r"[^a-z0-9 ]", " ", (name or "").lower())
    return re.sub(r"\s+", " ", SUFFIX.sub(" ", text)).strip()


def issuer_key(name: str) -> str:
    """First two meaningful words: 13F issuer names are truncated and abbreviated ("TEMPUS AI INC", "CARIS LIFE SCIENCES INC")."""
    return " ".join(norm(name).split()[:2])


def covered() -> dict[str, str]:
    """{issuer key: ticker} for covered companies, the small-cap list and the candidate filter."""
    names: dict[str, str] = {}
    for row in load(THEME, {}).get("themes", {}).get("ai_medicine", []):
        if row.get("ticker") and row.get("company"):
            names[row["ticker"]] = row["company"]
    for row in load(SMALL, {}).get("companies", []):
        names.setdefault(row["ticker"], row.get("company", ""))
    companies = load(FILTER, {}).get("companies", {})
    for t, c in (companies.items() if isinstance(companies, dict) else []):
        names.setdefault(t, c.get("company", ""))
    return {issuer_key(n): t for t, n in names.items() if issuer_key(n)}


def get_json(url: str, agent: str) -> dict:
    time.sleep(0.15)  # SEC fair access: well under 10 requests a second
    return mapper.http_json(url, agent)


def get_text(url: str, agent: str) -> str:
    path = CACHE / (re.sub(r"[^A-Za-z0-9]", "_", url)[-180:])
    if path.exists():
        return path.read_text(encoding="utf-8")
    time.sleep(0.15)
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": agent})
    import ssl
    cafile = "/etc/ssl/cert.pem" if Path("/etc/ssl/cert.pem").exists() else None
    with urllib.request.urlopen(req, timeout=60, context=ssl.create_default_context(cafile=cafile)) as resp:
        text = resp.read().decode("utf-8", "replace")
    CACHE.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return text


def find_filer(search: str, must: str, agent: str) -> tuple[str, str, list] | None:
    """(cik, entity name, 13F-HR rows) for the candidate whose name contains `must` and which files 13F-HR."""
    hits = get_json("https://efts.sec.gov/LATEST/search-index?" + urllib.parse.urlencode({"keysTyped": search}), agent)
    for h in hits.get("hits", {}).get("hits", [])[:6]:
        cik = h.get("_id")
        try:
            subs = get_json(f"https://data.sec.gov/submissions/CIK{int(cik):010d}.json", agent)
        except Exception:
            continue
        name = subs.get("name", "")
        if must not in name.lower():
            continue
        r = subs.get("filings", {}).get("recent", {})
        rows = [(f, a, d, p) for f, a, d, p in zip(r.get("form", []), r.get("accessionNumber", []), r.get("filingDate", []),
                                                    r.get("reportDate", [])) if f == "13F-HR"]
        if rows:
            return cik, name, rows
    return None


def holdings(cik: str, accession: str, agent: str) -> list[dict]:
    base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace('-', '')}/"
    items = get_json(base + "index.json", agent).get("directory", {}).get("item", [])
    xmls = [i["name"] for i in items if i["name"].lower().endswith(".xml") and "primary_doc" not in i["name"].lower()]
    out = []
    for name in xmls:
        try:
            root = ET.fromstring(get_text(base + name, agent))
        except ET.ParseError:
            continue
        for node in root.iter():
            if node.tag.split("}")[-1] != "infoTable":
                continue
            row = {c.tag.split("}")[-1]: c for c in node}
            shares = next((s.text for s in row.get("shrsOrPrnAmt", ET.Element("x")) if s.tag.split("}")[-1] == "sshPrnamt"), None)
            out.append({"issuer": (row.get("nameOfIssuer").text or "").strip() if row.get("nameOfIssuer") is not None else "",
                        "cusip": row.get("cusip").text if row.get("cusip") is not None else "",
                        "value": float(row.get("value").text or 0) if row.get("value") is not None else 0.0,
                        "shares": float(shares or 0), "putCall": row.get("putCall").text if row.get("putCall") is not None else None})
        if out:
            break
    return out


def positions(rows: list[dict], keys: dict[str, str]) -> dict[str, dict]:
    """Covered tickers in one information table, options excluded, summed by ticker."""
    out: dict[str, dict] = {}
    for r in rows:
        if r.get("putCall"):
            continue
        t = keys.get(issuer_key(r["issuer"]))
        if not t:
            continue
        p = out.setdefault(t, {"shares": 0.0, "value": 0.0, "issuer": r["issuer"]})
        p["shares"] += r["shares"]
        p["value"] += r["value"]
    return out


def change(now: dict | None, before: dict | None) -> str:
    if now and not before:
        return "new"
    if before and not now:
        return "exited"
    if not now or not before or not before["shares"]:
        return "held"
    ratio = now["shares"] / before["shares"] - 1
    return "added" if ratio >= 0.10 else "trimmed" if ratio <= -0.10 else "held"


def build(funds: list[dict]) -> dict:
    by_ticker: dict[str, list[dict]] = {}
    for f in funds:
        for t in sorted(set(f["now"]) | set(f["before"])):
            now, before = f["now"].get(t), f["before"].get(t)
            by_ticker.setdefault(t, []).append({
                "fund": f["fund"], "filer": f["filer"], "period": f["period"], "filed": f["filed"], "change": change(now, before),
                "shares": now["shares"] if now else 0, "sharesBefore": before["shares"] if before else 0,
                "valueUsd": now["value"] if now else 0, "url": f["url"]})
    summary = {"funds": len(funds), "companies": len(by_ticker),
               "new": sum(r["change"] == "new" for rows in by_ticker.values() for r in rows),
               "exited": sum(r["change"] == "exited" for rows in by_ticker.values() for r in rows)}
    return {"generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"), "method": __doc__.split("\n\n")[1].strip(),
            "limits": __doc__.split("\n\n")[2].strip(), "summary": summary,
            "funds": [{k: f[k] for k in ("fund", "filer", "cik", "period", "filed", "previousPeriod", "url")} for f in funds],
            "companies": {t: sorted(rows, key=lambda r: r["fund"]) for t, rows in sorted(by_ticker.items())}}


def render(payload: dict) -> str:
    s = payload["summary"]
    word = {"new": "新建仓", "added": "加仓", "trimmed": "减仓", "exited": "清仓", "held": "持有"}
    lines = ["# 专业生物医药基金 13F 持仓", "", f"生成：{payload['generatedAt']}", "",
             f"{s['funds']} 家基金、{s['companies']} 家覆盖公司；最新一季新建仓 {s['new']} 次、清仓 {s['exited']} 次。", "",
             f"> {payload['limits']}", "", "| 股票 | 基金 | 季度末 | 变化 | 股数 | 上季股数 | 市值 |", "|---|---|---|---|---:|---:|---:|"]
    for t, rows in payload["companies"].items():
        for r in rows:
            lines.append(f"| {t} | {r['fund']} | {r['period']} | {word[r['change']]} | {r['shares']:,.0f} | {r['sharesBefore']:,.0f} | ${r['valueUsd'] / 1e6:,.1f}M |")
    return "\n".join(lines) + "\n"


def main() -> None:
    agent = os.getenv("SEC_USER_AGENT", "")
    if "@" not in agent:
        sys.exit("Set SEC_USER_AGENT with your contact email (SEC fair-access policy).")
    keys = covered()
    funds = []
    for search, must in FUNDS.items():
        try:
            hit = find_filer(search, must, agent)
        except Exception as exc:
            print(f"  {search}: lookup failed ({str(exc)[:80]})")
            continue
        if not hit:
            print(f"  {search}: no 13F filer found")
            continue
        cik, name, rows = hit
        latest = rows[0]
        previous = next((r for r in rows[1:] if r[3] != latest[3]), None)
        now = positions(holdings(cik, latest[1], agent), keys)
        before = positions(holdings(cik, previous[1], agent), keys) if previous else {}
        url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{latest[1].replace('-', '')}/"
        funds.append({"fund": search, "filer": name, "cik": cik, "period": latest[3], "filed": latest[2],
                      "previousPeriod": previous[3] if previous else None, "url": url, "now": now, "before": before})
        print(f"  {search}: {name} {latest[3]} -> {len(now)} covered positions")
    # A filer whose latest 13F is far older than everyone else's has stopped filing; its old book is not current.
    newest = max((f["period"] for f in funds), default=None)
    if newest:
        cutoff = (datetime.fromisoformat(newest) - __import__("datetime").timedelta(days=200)).date().isoformat()
        for f in [f for f in funds if f["period"] < cutoff]:
            print(f"  {f['fund']}: latest 13F is for {f['period']}; dropped as stale")
        funds = [f for f in funds if f["period"] >= cutoff]
    payload = build(funds)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT.write_text(render(payload), encoding="utf-8")
    print(json.dumps(payload["summary"]))


if __name__ == "__main__":
    main()
