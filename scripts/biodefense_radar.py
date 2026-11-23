"""Biodefense and outbreak radar: where government countermeasure money goes, and which outbreaks are moving.

Peter asked to watch "biological war, any stir": events that suddenly change the outlook for vaccine,
diagnostic and countermeasure makers. Two official sources, no model calls:

* USAspending.gov: contract actions (new obligations) by HHS's Office of the Assistant Secretary for
  Preparedness and Response (ASPR, which runs BARDA and the Strategic National Stockpile), last 90 days;
  recipients are matched to listed companies by name using SEC's ticker file.
* WHO Disease Outbreak News: official outbreak reports, last 60 days.
An outbreak and a contract that name the same pathogen are linked, so a reader sees who is funded to
respond. A contract is revenue for the recipient; an outbreak is context, not evidence of sales.

    python3 scripts/biodefense_radar.py      (set SEC_USER_AGENT for the ticker match)
"""
from __future__ import annotations

import json
import os
import re
import ssl
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "state/biodefense-radar.json"
REPORT = ROOT / "outputs/biodefense-radar.md"
AGENCY = "Office of Assistant Secretary for Preparedness and Response"
USASPENDING = "https://api.usaspending.gov/api/v2/search/spending_by_transaction/"
WHO_DON = "https://www.who.int/api/news/diseaseoutbreaknews?$orderby=PublicationDate%20desc&$top=40"
MIN_USD = 5_000_000
# Subsidiaries whose listed parent the SEC ticker file cannot reveal by name.
PARENTS = {"glaxosmithkline": "GSK", "sanofi": "SNY (Sanofi)", "seqirus": "CSL (ASX: CSL)", "cepheid": "DHR (Danaher)",
           "fresenius kabi": "Fresenius SE (XETRA: FRE)", "hikma": "Hikma (LSE: HIK)", "emergent": "EBS",
           "bavarian nordic": "Bavarian Nordic (CPH: BAVA)", "janssen": "JNJ", "pfizer": "PFE", "merck sharp": "MRK",
           "abbott": "ABT", "becton": "BDX", "roche": "Roche (SIX: ROG)", "genentech": "Roche (SIX: ROG)"}
PATHOGENS = ("ebola", "marburg", "smallpox", "mpox", "monkeypox", "anthrax", "influenza", "h5n1", "avian", "mers",
             "coronavirus", "covid", "chikungunya", "dengue", "yellow fever", "plague", "botulinum", "nerve agent",
             "radiation", "burn", "antifungal", "fungal", "antibiotic", "antimicrobial", "nipah", "lassa", "zika", "measles")
SUFFIX = re.compile(r"\b(inc|incorporated|corp|corporation|co|company|llc|l\.l\.c|ltd|limited|plc|lp|l\.p|holdings?|group|usa|us|the|a/s|ag|n\.v|s\.a)\b\.?", re.I)


def _context():
    # Same trust store the other SEC/FDA fetchers use (handles this machine's certificate chain).
    import serenity_evidence_review as ser
    return ser.context()


def http(url: str, body: dict | None = None, agent: str = "serenity-research-agent") -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers={"User-Agent": agent, "Content-Type": "application/json",
                                                          "Accept-Encoding": "identity"})
    try:
        with urllib.request.urlopen(req, timeout=60, context=_context()) as resp:
            return json.loads(resp.read())
    except urllib.error.URLError as exc:
        if not isinstance(getattr(exc, "reason", None), ssl.SSLError):
            raise
        # Python's CA bundle rejects this host's chain on some machines; curl verifies against the system
        # keychain instead. Verification stays on either way.
        import subprocess
        cmd = ["curl", "-sS", "--fail", "-m", "60", "-A", agent, "-H", "Content-Type: application/json", url]
        if data is not None:
            cmd += ["-X", "POST", "--data-binary", "@-"]
        out = subprocess.run(cmd, input=data, capture_output=True, check=True, timeout=90).stdout
        return json.loads(out)


def name_key(name: str) -> str:
    words = re.sub(r"[^a-z0-9 ]", " ", SUFFIX.sub(" ", (name or "").lower())).split()
    return " ".join(words[:2])


def ticker_index(sec_rows: dict) -> dict[str, tuple[str, str]]:
    """First two significant words of the SEC company title -> (ticker, title); ambiguous keys are dropped."""
    out, clash = {}, set()
    for r in sec_rows.values():
        key = name_key(r["title"])
        if not key:
            continue
        if key in out and out[key][0] != r["ticker"]:
            clash.add(key)
        out.setdefault(key, (r["ticker"], r["title"]))
    return {k: v for k, v in out.items() if k not in clash}


def pathogens_in(text: str) -> list[str]:
    low = (text or "").lower()
    return [p for p in PATHOGENS if p in low]


def contracts(start: date, end: date, fetch=http) -> list[dict]:
    body = {"filters": {"time_period": [{"start_date": start.isoformat(), "end_date": end.isoformat()}],
                        "award_type_codes": ["A", "B", "C", "D"],
                        "agencies": [{"type": "awarding", "tier": "subtier", "name": AGENCY}]},
            "fields": ["Action Date", "Recipient Name", "Transaction Amount", "Transaction Description", "Award ID",
                       "generated_internal_id"],
            "limit": 100, "sort": "Transaction Amount", "order": "desc"}
    rows = fetch(USASPENDING, body).get("results", [])
    out = []
    for r in rows:
        amount = r.get("Transaction Amount") or 0
        if amount < MIN_USD:
            continue
        gid = r.get("generated_internal_id")
        out.append({"date": r.get("Action Date"), "recipient": r.get("Recipient Name"), "amountM": round(amount / 1e6, 1),
                    "description": (r.get("Transaction Description") or "").strip(), "awardId": r.get("Award ID"),
                    "url": f"https://www.usaspending.gov/award/{gid}" if gid else "https://www.usaspending.gov/search",
                    "pathogens": pathogens_in(r.get("Transaction Description") or "")})
    return out


def outbreaks(since: date, fetch=http) -> list[dict]:
    out = []
    for r in fetch(WHO_DON).get("value", []):
        day = (r.get("PublicationDate") or "")[:10]
        if not day or day < since.isoformat():
            continue
        title = r.get("OverrideTitle") or r.get("Title") or ""
        slug = (r.get("ItemDefaultUrl") or r.get("UrlName") or "").strip("/")
        out.append({"date": day, "title": title, "url": f"https://www.who.int/emergencies/disease-outbreak-news/item/{slug}",
                    "pathogens": pathogens_in(title)})
    return out


def build(today: date, sec_rows: dict | None, fetch=http) -> dict:
    index = ticker_index(sec_rows or {})
    errors = []
    try:
        cs = contracts(today - timedelta(days=90), today, fetch)
    except Exception as exc:
        cs, errors = [], errors + [f"USAspending: {type(exc).__name__}"]
    try:
        obs = outbreaks(today - timedelta(days=60), fetch)
    except Exception as exc:
        obs, errors = [], errors + [f"WHO: {type(exc).__name__}"]
    for c in cs:
        hit = index.get(name_key(c["recipient"]))
        parent = next((v for k, v in PARENTS.items() if k in (c["recipient"] or "").lower()), None)
        c["ticker"], c["secTitle"] = (hit if hit else (parent, "listed parent" if parent else None))
    for o in obs:
        o["fundedResponders"] = sorted({c["ticker"] or c["recipient"] for c in cs if set(c["pathogens"]) & set(o["pathogens"])})
    listed = [c for c in cs if c["ticker"]]
    return {"generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"), "asOf": today.isoformat(),
            "sources": {"contracts": f"USAspending.gov, awarding sub-agency: {AGENCY}", "outbreaks": "WHO Disease Outbreak News"},
            "summary": {"contracts": len(cs), "contractUsdM": round(sum(c["amountM"] for c in cs), 1), "listedRecipients": len({c["ticker"] for c in listed}),
                        "outbreaks": len(obs), "tickerMatch": bool(index), "errors": errors},
            "contracts": cs, "outbreaks": obs}


def report(p: dict) -> str:
    s = p["summary"]
    lines = ["# 生物安全与疫情雷达", "", f"截至 {p['asOf']}。来源：{p['sources']['contracts']}；{p['sources']['outbreaks']}。", "",
             f"近 90 天 ASPR/BARDA 合同动作 {s['contracts']} 笔（≥500 万美元），合计 ${s['contractUsdM']:,.0f}M，其中 {s['listedRecipients']} 家上市公司；"
             f"近 60 天 WHO 疫情通报 {s['outbreaks']} 条。合同是收款方的收入；疫情只是背景，不等于销售。",
             "疫情与合同按病原名称匹配，较粗：例如 Regeneron 的 Inmazeb 针对 Zaire 型埃博拉，对 Bundibugyo 型没有获批适应症，需逐一核对毒株。", "",
             "## 政府应对合同", "", "| 日期 | 收款方 | 代码 | 金额 | 病原/用途 | 说明 |", "|---|---|---|---:|---|---|"]
    for c in p["contracts"]:
        lines.append(f"| {c['date']} | {c['recipient']} | {c['ticker'] or '非上市/未匹配'} | ${c['amountM']:,.1f}M | {', '.join(c['pathogens']) or '—'} | [{c['description'][:70]}]({c['url']}) |")
    lines += ["", "## WHO 疫情通报", "", "| 日期 | 通报 | 有合同的应对方 |", "|---|---|---|"]
    for o in p["outbreaks"]:
        lines.append(f"| {o['date']} | [{o['title']}]({o['url']}) | {', '.join(o['fundedResponders']) or '—'} |")
    if s["errors"]:
        lines += ["", "抓取问题：" + "；".join(s["errors"])]
    return "\n".join(lines) + "\n"


def main() -> None:
    agent = os.getenv("SEC_USER_AGENT", "")
    sec_rows = None
    if "@" in agent:
        try:
            sec_rows = http("https://www.sec.gov/files/company_tickers.json", agent=agent)
        except Exception:
            sec_rows = None
    payload = build(date.today(), sec_rows)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT.write_text(report(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
