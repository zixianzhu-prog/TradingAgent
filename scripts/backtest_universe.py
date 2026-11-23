"""Out-of-sample universe for the order-rule backtest: health-care filers that were NOT in the original sample.

The "growth not slowing" filter was found on the ~100 companies cached in state/serenity-source-cache/xbrl.
To test it honestly it must be run on companies it has never seen. This builds that set:

* EDGAR company lists for health-care SIC codes (pharma, diagnostics, biologics, devices, labs, instruments);
* keep only companies in SEC's current ticker file (listed today, so prices exist) and not already cached;
* fetch each companyfacts file and keep only the fields the backtest reads (revenue tags, cover share count),
  saved compactly under state/serenity-source-cache/xbrl-oos/.

Same survivorship limit as the main test: companies that later delisted have no price history here.

    SEC_USER_AGENT="Name email" python3 scripts/backtest_universe.py [--limit 300]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

import serenity_evidence_review as ser

ROOT = Path(__file__).resolve().parents[1]
IN_SAMPLE = ROOT / "state/serenity-source-cache/xbrl"
OOS = ROOT / "state/serenity-source-cache/xbrl-oos"
SICS = ("2834", "2835", "2836", "3841", "3845", "8071", "3826")
KEEP_GAAP = ("RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet",
             "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueGoodsNet")
KEEP_IFRS = ("Revenue", "RevenueFromContractsWithCustomers")


def get(url: str, agent: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": agent, "Accept-Encoding": "identity"})
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ser.context()))
    with opener.open(req, timeout=60) as resp:
        return resp.read()


def sic_ciks(sic: str, agent: str, pages: int = 15) -> set[str]:
    out = set()
    for page in range(pages):
        url = (f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&SIC={sic}&type=10-K&owner=include"
               f"&count=100&start={page * 100}&output=atom")
        xml = get(url, agent).decode("utf-8", "replace")
        found = set(re.findall(r"<cik>(\d+)</cik>", xml))
        out |= {str(int(c)) for c in found}
        time.sleep(0.15)
        if len(found) < 100:
            break
    return out


def compact(facts: dict) -> dict:
    f = facts.get("facts", {})
    return {"cik": facts.get("cik"), "entityName": facts.get("entityName"), "facts": {
        "us-gaap": {t: f["us-gaap"][t] for t in KEEP_GAAP if t in f.get("us-gaap", {})},
        "ifrs-full": {t: f["ifrs-full"][t] for t in KEEP_IFRS if t in f.get("ifrs-full", {})},
        "dei": {t: f["dei"][t] for t in ("EntityCommonStockSharesOutstanding",) if t in f.get("dei", {})}}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--limit", type=int, default=300)
    args = parser.parse_args()
    agent = os.getenv("SEC_USER_AGENT", "")
    if "@" not in agent:
        sys.exit("Set SEC_USER_AGENT with your contact email (SEC fair-access policy).")
    tickers = json.loads(get("https://www.sec.gov/files/company_tickers.json", agent))
    by_cik = {}
    for r in tickers.values():
        by_cik.setdefault(str(r["cik_str"]), r["ticker"])  # first ticker = primary share class
    ciks = set()
    for sic in SICS:
        ciks |= sic_ciks(sic, agent)
        print(f"  SIC {sic}: {len(ciks)} companies so far")
    seen = {p.stem.removeprefix("companyfacts-") for p in IN_SAMPLE.glob("companyfacts-*.json")}
    todo = sorted((by_cik[c], c) for c in ciks if c in by_cik and by_cik[c] not in seen)
    OOS.mkdir(parents=True, exist_ok=True)
    done = 0
    for ticker, cik in todo:
        if done >= args.limit:
            break
        path = OOS / f"companyfacts-{ticker}.json"
        if path.exists():
            done += 1
            continue
        try:
            facts = json.loads(get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{int(cik):010d}.json", agent))
            path.write_text(json.dumps(compact(facts)), encoding="utf-8")
            done += 1
        except Exception as exc:
            print(f"  {ticker}: {type(exc).__name__}")
        time.sleep(0.12)
    print(json.dumps({"healthcareFilers": len(ciks), "listedNotInSample": len(todo), "saved": done, "dir": str(OOS.relative_to(ROOT))}))


if __name__ == "__main__":
    main()
