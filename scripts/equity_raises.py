"""Money actually raised by listed companies: cash received from selling shares, from SEC XBRL.

Peter's chain ends with "...and it raised money". For private companies that is a Form D; listed companies
mostly raise through registered offerings, ATMs and PIPEs, which Form D never shows. The cash-flow statement
does: ProceedsFromIssuanceOfCommonStock and its siblings are the cash that came in. Employee option
exercises are excluded (different tag), so this is investor money.

Window: the last 24 months. Annual (10-K/20-F) periods ending in the window, plus the year-to-date 10-Q
after the last annual period. Several tags can describe the same cash (common stock, private placement),
so each period takes the largest tag, never the sum.

    SEC_USER_AGENT="Name email" python3 scripts/equity_raises.py [--tickers NAUT ABCL]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "state/serenity-source-cache/xbrl-raises"
OUT = ROOT / "state/equity-raises.json"
REPORT = ROOT / "outputs/equity-raises.md"
TAGS = ("ProceedsFromIssuanceOfCommonStock", "ProceedsFromIssuanceOrSaleOfEquity", "ProceedsFromIssuanceInitialPublicOffering",
        "ProceedsFromIssuanceOfPrivatePlacement", "ProceedsFromIssuanceOfConvertiblePreferredStock",
        "ProceedsFromIssuanceOfPreferredStockAndPreferenceStock", "ProceedsFromIssuanceOfCommonStockAndWarrants")
FORMS = ("10-K", "10-Q", "20-F", "10-K/A", "20-F/A")
TTL_DAYS = 7
MIN_USD = 5_000_000


def days(a: str, b: str) -> int:
    return (date.fromisoformat(b) - date.fromisoformat(a)).days


GENERIC = "ProceedsFromIssuanceOrSaleOfEquity"


def periods(facts: dict) -> dict[tuple[str, str], dict]:
    """(start, end) -> the largest proceeds fact for that period. A specific tag (common stock, IPO, private
    placement, preferred) wins over the generic ProceedsFromIssuanceOrSaleOfEquity, even when it reports zero:
    some filers put a shelf's capacity in the generic tag (TECX: $400M every quarter while the specific tags show
    a $173M private placement)."""
    gaap = facts.get("facts", {}).get("us-gaap", {})
    specific: dict[tuple[str, str], dict] = {}
    generic: dict[tuple[str, str], dict] = {}
    for tag in TAGS:
        bucket = generic if tag == GENERIC else specific
        for x in gaap.get(tag, {}).get("units", {}).get("USD", []):
            if x.get("form") not in FORMS or not x.get("start") or x.get("val") is None:
                continue
            key = (x["start"], x["end"])
            if key not in bucket or x["val"] > bucket[key]["val"]:
                bucket[key] = {**x, "tag": tag}
    return {**generic, **specific}


def raised(facts: dict, today: date, window_days: int = 730) -> dict:
    """Investor cash raised in the window: annual periods ending in it, plus the YTD after the last one."""
    ps = periods(facts)
    since = (today - timedelta(days=window_days)).isoformat()
    annual = sorted((p for (s, e), p in ps.items() if e >= since and 330 <= days(s, e) <= 400), key=lambda p: p["end"])
    # Overlapping annual periods (restated, comparative) count once: keep non-overlapping, latest filed wins.
    picked: list[dict] = []
    for p in annual:
        if picked and p["start"] < picked[-1]["end"]:
            if p.get("filed", "") >= picked[-1].get("filed", ""):
                picked[-1] = p
            continue
        picked.append(p)
    last_end = picked[-1]["end"] if picked else since
    ytd = [p for (s, e), p in ps.items() if s >= last_end and e > last_end and days(s, e) < 330]
    if ytd:
        picked.append(max(ytd, key=lambda p: (p["val"], p["end"])))  # cumulative YTD: the largest is the latest that reported
    cik = facts.get("cik")
    rows = [{"start": p["start"], "end": p["end"], "usdM": round(p["val"] / 1e6, 1), "tag": p["tag"], "form": p["form"],
             "filed": p.get("filed"), "url": f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{p['accn'].replace('-', '')}/"
             if cik and p.get("accn") else None} for p in picked if p["val"] > 0]
    return {"totalUsdM": round(sum(r["usdM"] for r in rows), 1), "periods": rows}


def fetch_facts(ticker: str, cik: str, agent: str) -> dict:
    """Compact companyfacts (proceeds tags only), refreshed weekly."""
    path = CACHE / f"companyfacts-{ticker}.json"
    if path.exists() and time.time() - path.stat().st_mtime < TTL_DAYS * 86400:
        return json.loads(path.read_text(encoding="utf-8"))
    import serenity_evidence_review as ser

    req = urllib.request.Request(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{int(cik):010d}.json",
                                 headers={"User-Agent": agent, "Accept-Encoding": "identity"})
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ser.context()))
    with opener.open(req, timeout=60) as resp:
        full = json.loads(resp.read())
    gaap = full.get("facts", {}).get("us-gaap", {})
    compact = {"cik": full.get("cik"), "entityName": full.get("entityName"),
               "facts": {"us-gaap": {t: gaap[t] for t in TAGS if t in gaap}}}
    CACHE.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(compact), encoding="utf-8")
    time.sleep(0.12)
    return compact


def universe() -> dict[str, str]:
    theme = json.loads((ROOT / "trend-agent/theme-company-map.json").read_text(encoding="utf-8"))
    small = json.loads((ROOT / "state/small-cap-stage.json").read_text(encoding="utf-8")) if (ROOT / "state/small-cap-stage.json").exists() else {"companies": []}
    names = {r["ticker"]: r.get("company", r["ticker"]) for r in theme["themes"]["ai_medicine"] + small["companies"]}
    names.pop("NVDA", None)
    return names


def render(p: dict) -> str:
    rows = sorted(p["companies"].items(), key=lambda kv: -kv[1]["totalUsdM"])
    lines = ["# 上市公司股权融资（SEC XBRL）", "",
             f"> 近 24 个月内结束的财年和今年以来季度中，从投资者处收到的股票发行现金（现金流量表 ProceedsFromIssuance… 标签；不含员工期权行权）。生成：{p['generatedAt'][:10]}。",
             f"> {p['summary']['raised']} 家融资 ≥ 500 万美元。同一期间多个标签取最大值，不相加。", "",
             "| 公司 | 近 24 个月融资 | 期间 | 来源 |", "|---|---:|---|---|"]
    for t, r in rows:
        if not r["periods"]:
            continue
        span = "; ".join(f"{x['start']}→{x['end']} ${x['usdM']:,.1f}M ({x['form']})" for x in r["periods"])
        link = r["periods"][-1].get("url")
        lines.append(f"| {t} · {r['company']} | ${r['totalUsdM']:,.1f}M | {span} | {f'[SEC]({link})' if link else '—'} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--tickers", nargs="*")
    args = parser.parse_args()
    agent = os.getenv("SEC_USER_AGENT", "")
    if "@" not in agent:
        sys.exit("Set SEC_USER_AGENT with your contact email (SEC fair-access policy).")
    import beneficiary_mapper as mapper

    names = universe()
    if args.tickers:
        names = {t: n for t, n in names.items() if t in args.tickers}
    ciks = {str(r["ticker"]).upper(): str(r["cik_str"]) for r in mapper.http_json("https://www.sec.gov/files/company_tickers.json", agent).values()}
    today, companies, errors = date.today(), {}, []
    for t in sorted(names):
        if t not in ciks:
            continue
        try:
            companies[t] = {"company": names[t], **raised(fetch_facts(t, ciks[t], agent), today)}
        except Exception as exc:
            errors.append(f"{t}: {type(exc).__name__}")
    payload = {"generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "method": "SEC XBRL cash-flow proceeds from issuing equity, last 24 months; largest tag per period; option exercises excluded.",
               "summary": {"companies": len(companies), "raised": sum(c["totalUsdM"] * 1e6 >= MIN_USD for c in companies.values()),
                           "errors": errors},
               "companies": companies}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT.write_text(render(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
