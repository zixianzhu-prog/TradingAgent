"""Sourced revenue-growth paths for the 5-year scenarios.

The last hand-set scenario input was growth. This replaces it with one rule for every company:

    start = the company's own growth, the lower of the latest quarter year over year (SEC
            press release, from trend-agent/ai-medicine-financials.json) and the latest fiscal
            year (SEC XBRL companyfacts, 10-K)
    bull  = start fades in a straight line to the industry's 5-year historical revenue CAGR
    base  = start fades in a straight line to the industry's fundamental growth
            (return on equity x retention, what the industry can grow without new capital)
    bear  = growth reaches the industry's fundamental growth by year 2 and stays there

Fading growth toward a sector rate follows the mean-reversion finding in Mauboussin &
Callahan, The Base Rate Book (2016): high growth rarely persists for five years. The straight
line is this project's choice; the endpoints come from Damodaran's January tables. Each path
is converted to the 5-year CAGR the scenario model uses.

    python3 scripts/calibrate_growth.py              # refresh Damodaran growth tables and missing XBRL files
    python3 scripts/calibrate_growth.py --offline    # use stored snapshots only (SEC needs SEC_USER_AGENT)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import urllib.request
from datetime import date
from pathlib import Path

from calibrate_multiples import INDUSTRY, FINANCIALS, SNAPSHOT, parse_damodaran

ROOT = Path(__file__).resolve().parents[1]
GROWTH_URLS = {
    "fundamental": "https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/fundgr.html",
    "historical": "https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histgr.html",
}
XBRL_CACHE = ROOT / "state/serenity-source-cache/xbrl"
SEC_VALIDATION = ROOT / "state/sec-xbrl-validation.json"
OUTPUT = ROOT / "state/growth-calibration.json"
REVENUE_TAGS = ("RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet")
HORIZON = 5


def parse_growth_table(page: str, column: str) -> dict[str, float]:
    """Industry -> fraction from one of Damodaran's growth pages (column = exact header text)."""
    import html as htmllib

    def cells_of(tr: str) -> list[str]:
        return [re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", "", td))).strip()
                for td in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S | re.I)]

    rows, col = {}, None
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", page, re.S | re.I):
        cells = cells_of(tr)
        if col is None:
            if "Industry Name" in cells and column in cells:
                col = cells.index(column)
            continue
        if len(cells) <= col or not re.fullmatch(r"\d+", cells[1]):
            continue
        try:
            rows[cells[0]] = round(float(cells[col].rstrip("%")) / 100, 4)
        except ValueError:
            pass                                # 'NA' or '#DIV/0!' cells
    return rows


def refresh_growth_tables(snapshot: dict) -> dict:
    import serenity_evidence_review as ser

    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ser.context()))
    tables = {}
    for key, url in GROWTH_URLS.items():
        with opener.open(urllib.request.Request(url, headers={"User-Agent": "serenity-research-agent"}), timeout=30) as resp:
            page = resp.read().decode("latin-1")
        column = "Fundamental Growth" if key == "fundamental" else "CAGR in Revenues- Last 5 years"
        rows = parse_growth_table(page, column)
        if len(rows) < 50:
            raise ValueError(f"{key} growth table parsed to too few industries")
        tables[key] = {"source": url, "column": column, "industries": rows}
    snapshot["growth"] = tables
    SNAPSHOT.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    return snapshot


def cik_for(row: dict, known: dict[str, str]) -> str | None:
    if row["ticker"] in known:
        return known[row["ticker"]]
    for url in row.get("sources", []):
        m = re.search(r"edgar/data/0*(\d+)/", url)
        if m:
            return f"{int(m.group(1)):010d}"
    return None


def fiscal_year_revenue(facts: dict) -> list[tuple[str, float]]:
    """(fiscal year, revenue $M) from 10-K annual values, latest filing wins."""
    gaap = facts.get("facts", {}).get("us-gaap", {})
    for tag in REVENUE_TAGS:
        best: dict[str, dict] = {}
        for x in gaap.get(tag, {}).get("units", {}).get("USD", []):
            if x.get("form") not in ("10-K", "10-K/A") or not (x.get("start") and x.get("end")):
                continue
            days = (date.fromisoformat(x["end"]) - date.fromisoformat(x["start"])).days
            if not 350 <= days <= 380:
                continue
            fy = x["end"][:4]
            if fy not in best or x["filed"] > best[fy]["filed"]:
                best[fy] = x
        if len(best) >= 2:
            return [(fy, round(best[fy]["val"] / 1e6, 1)) for fy in sorted(best)]
    return []


def load_companyfacts(ticker: str, cik: str, fetch: bool) -> dict | None:
    path = XBRL_CACHE / f"companyfacts-{ticker}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    if not fetch:
        return None
    import serenity_evidence_review as ser

    agent = os.getenv("SEC_USER_AGENT")
    if not agent:
        return None  # SEC requires a contact in the User-Agent; set SEC_USER_AGENT in the environment
    req = urllib.request.Request(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
                                 headers={"User-Agent": agent, "Accept-Encoding": "identity"})
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ser.context()))
    with opener.open(req, timeout=40) as resp:
        data = resp.read()
    XBRL_CACHE.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return json.loads(data)


def cagr_of_path(path: list[float]) -> float:
    total = 1.0
    for g in path:
        total *= 1 + g
    return total ** (1 / len(path)) - 1


def growth_paths(start: float, fundamental: float, historical: float) -> dict:
    """Yearly growth for each case, then the equivalent 5-year CAGR."""
    bull_end, base_end = max(historical, fundamental), fundamental
    # A company growing slower than its industry is not assumed to speed up in the bear or base case: both hold today's rate.
    base_end = min(base_end, start)
    bull = [start + (bull_end - start) * (y / HORIZON) for y in range(1, HORIZON + 1)]
    base = [start + (base_end - start) * (y / HORIZON) for y in range(1, HORIZON + 1)]
    bear = [start + (base_end - start) * min(1.0, y / 2) for y in range(1, HORIZON + 1)]
    paths = {"bear": bear, "base": base, "bull": bull}
    cagr = {k: round(cagr_of_path(v), 4) for k, v in paths.items()}
    cagr["base"] = max(cagr["base"], cagr["bear"])
    cagr["bull"] = max(cagr["bull"], cagr["base"])
    return {"paths": {k: [round(g, 4) for g in v] for k, v in paths.items()}, "cagr": cagr}


def calibrate(companies: list[dict], snapshot: dict, facts_by_ticker: dict[str, dict | None]) -> dict:
    fundamental = snapshot["growth"]["fundamental"]["industries"]
    historical = snapshot["growth"]["historical"]["industries"]
    out = {}
    for row in companies:
        ticker = row["ticker"]
        inputs = row.get("scenario_inputs") or {}
        if inputs.get("metric") != "sales" or ticker not in INDUSTRY:
            continue
        industry = INDUSTRY[ticker]
        history = fiscal_year_revenue(facts_by_ticker.get(ticker) or {})
        fy_growth = history[-1][1] / history[-2][1] - 1 if len(history) >= 2 else None
        quarter = row.get("revenue_growth_pct") / 100 if row.get("revenue_growth_pct") is not None else None
        candidates = [g for g in (quarter, fy_growth) if g is not None]
        if not candidates:
            continue
        start = min(candidates)
        start_basis = ("latest quarter year over year" if start == quarter else f"fiscal {history[-1][0]} over {history[-2][0]}")
        model = growth_paths(start, fundamental[industry], historical[industry])
        three_year = (history[-1][1] / history[-4][1]) ** (1 / 3) - 1 if len(history) >= 4 else None
        out[ticker] = {
            "start": round(start, 4), "start_basis": start_basis,
            "quarter_yoy": quarter, "fiscal_year_yoy": round(fy_growth, 4) if fy_growth is not None else None,
            "three_year_cagr": round(three_year, 4) if three_year is not None else None,
            "revenue_history_m": history,
            "industry": industry,
            "industry_fundamental_growth": fundamental[industry],
            "industry_historical_cagr": historical[industry],
            **model["cagr"],
            "paths": model["paths"],
            "basis": {
                "bear": f"growth falls from {start:.0%} to the industry's fundamental growth {fundamental[industry]:.1%} by year 2 (Damodaran, {industry})",
                "base": f"growth fades from {start:.0%} to {fundamental[industry]:.1%} over 5 years",
                "bull": f"growth fades from {start:.0%} to the industry's 5-year historical revenue CAGR {historical[industry]:.1%}",
            },
        }
    return {"asOf": date.today().isoformat(), "method": __doc__.split("\n\n")[1].strip(),
            "damodaran": {k: snapshot["growth"][k]["source"] for k in snapshot["growth"]}, "companies": out}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    if not args.offline:
        try:
            snapshot = refresh_growth_tables(snapshot)
        except Exception as exc:
            print(f"Damodaran growth refresh skipped: {exc}")
    if "growth" not in snapshot:
        raise SystemExit("No Damodaran growth tables stored; run without --offline once")
    companies = json.loads(FINANCIALS.read_text(encoding="utf-8"))["companies"]
    known = {c["ticker"]: c["cik"] for c in json.loads(SEC_VALIDATION.read_text(encoding="utf-8")).get("companies", []) if c.get("cik")}
    facts = {}
    for row in companies:
        cik = cik_for(row, known)
        if cik and (row.get("scenario_inputs") or {}).get("metric") == "sales":
            try:
                facts[row["ticker"]] = load_companyfacts(row["ticker"], cik, fetch=not args.offline)
            except Exception as exc:
                print(f"{row['ticker']}: companyfacts not fetched ({type(exc).__name__})")
    result = calibrate(companies, snapshot, facts)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    for t, c in result["companies"].items():
        print(f"  {t:5} start {c['start']:>6.1%} ({c['start_basis']})  bear {c['bear']:.1%} base {c['base']:.1%} bull {c['bull']:.1%}  "
              f"industry fund {c['industry_fundamental_growth']:.1%} hist {c['industry_historical_cagr']:.1%}")


if __name__ == "__main__":
    main()
