"""Sourced exit multiples for the 5-year scenarios.

The scenario model needs a price-to-sales multiple at the end of the horizon for each case.
Instead of a hand-set number, every company gets the same rule, so no opinion hides in it:

    bear  = Damodaran industry price/sales (the AI premium is gone; the company trades like
            an average firm in its sector)
    base  = median price/sales of the AI-medicine peers in our universe today
    bull  = top-quartile price/sales of those peers today

Peer multiples are computed from trend-agent/ai-medicine-financials.json (SEC-reported revenue,
shares and the snapshot price), the same inputs the scenario builder uses. Industry multiples come from Aswath Damodaran's public dataset (NYU Stern), updated
each January; the parsed table is kept in trend-agent/damodaran-industry-multiples.json with
its URL and date so the page can cite it and offline runs still work.

    python3 scripts/calibrate_multiples.py              # refresh Damodaran if possible, write state/multiple-calibration.json
    python3 scripts/calibrate_multiples.py --offline    # use the stored Damodaran snapshot
"""
from __future__ import annotations

import argparse
import html as htmllib
import json
import re
import statistics
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DAMODARAN_URL = "https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/psdata.html"
SNAPSHOT = ROOT / "trend-agent/damodaran-industry-multiples.json"
FINANCIALS = ROOT / "trend-agent/ai-medicine-financials.json"
OUTPUT = ROOT / "state/multiple-calibration.json"

# Which Damodaran industry each pick would trade like if its AI premium disappeared.
INDUSTRY = {
    "ISRG": "Healthcare Products",
    "CBLL": "Healthcare Products",
    "HTFL": "Heathcare Information and Technology",   # Damodaran's own spelling
    "TEM": "Heathcare Information and Technology",
    "CAI": "Heathcare Information and Technology",
    "SDGR": "Heathcare Information and Technology",
    "SOPH": "Heathcare Information and Technology",
    "RDNT": "Hospitals/Healthcare Facilities",
    "GEHC": "Healthcare Products",
    "NTRA": "Healthcare Products",    # genetic testing; Damodaran's support-services group (0.37x) is insurers and distributors
    "GH": "Healthcare Products",
    "CERT": "Heathcare Information and Technology",  # biosimulation software
    "CARL": "Healthcare Products",    # personalized spine implants planned by AI
    "GRAL": "Healthcare Products",    # cancer screening test, grouped with NTRA and GH
    "HNGE": "Heathcare Information and Technology",  # digital musculoskeletal care
    "OABI": "Drugs (Biotechnology)",  # antibody-discovery platform paid in milestones and royalties
}
# Mature companies where AI is a small part of revenue: the base case keeps today's own multiple (no AI re-rating),
# the bear case is the lower of the industry and 75% of today's, the bull case at most the lowest of industry, peers and 1.5x today's.
MATURE = {"GEHC": "medical-equipment maker; AI is a small part of revenue"}
# Peers: AI-medicine universe companies with a sales multiple. NVDA is a supplier, not a peer.
PEER_EXCLUDE = {"NVDA"}


def parse_damodaran(page: str) -> dict:
    """Industry rows from the price/sales page: name -> {firms, ps, net_margin, ev_sales, op_margin}."""
    text = htmllib.unescape(re.sub(r"<[^>]+>", "|", page))
    text = re.sub(r"(\| ?)+", "|", re.sub(r"\s+", " ", text))
    cells = [c.strip() for c in text.split("|")]
    start = cells.index("Industry Name") + 6
    rows = {}
    for k in range(start, len(cells) - 5, 6):
        name = cells[k]
        try:
            rows[name] = {"firms": int(cells[k + 1]), "ps": float(cells[k + 2]), "ev_sales": float(cells[k + 4]),
                          "net_margin": cells[k + 3], "operating_margin": cells[k + 5]}
        except ValueError:
            break
    updated = re.search(r"(January|February|March) (20\d\d)", page)
    return {"source": DAMODARAN_URL, "data_date": " ".join(updated.groups()) if updated else "unknown",
            "fetched": date.today().isoformat(), "industries": rows}


def refresh_snapshot() -> dict:
    import serenity_evidence_review as ser  # shared certificate context

    req = urllib.request.Request(DAMODARAN_URL, headers={"User-Agent": "serenity-research-agent"})
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ser.context()))
    with opener.open(req, timeout=30) as resp:
        page = resp.read().decode("latin-1")
    snap = parse_damodaran(page)
    if len(snap["industries"]) < 50:
        raise ValueError("Damodaran page parsed to too few industries; keeping the stored snapshot")
    SNAPSHOT.write_text(json.dumps(snap, ensure_ascii=False, indent=2), encoding="utf-8")
    return snap


def quartiles(values: list[float]) -> tuple[float, float, float]:
    q = statistics.quantiles(sorted(values), n=4, method="inclusive")
    return round(q[0], 1), round(statistics.median(values), 1), round(q[2], 1)


def price_to_sales(row: dict) -> float | None:
    revenue = row.get("full_year_revenue_guide_m") or (row.get("quarterly_revenue_m") or 0) * 4
    if not revenue or not row.get("price") or not row.get("shares"):
        return None
    return round(row["price"] * row["shares"] / 1e6 / revenue, 1)


def calibrate(companies: list[dict], snapshot: dict) -> dict:
    # Pre-revenue platforms (RXRX, ABCL) are excluded upstream: their sales multiple is not decision-useful.
    peers = {r["ticker"]: ps for r in companies if r["ticker"] not in PEER_EXCLUDE
             if (ps := price_to_sales(r)) and ps < 50}
    q1, median, q3 = quartiles(list(peers.values()))
    industries = snapshot["industries"]
    out = {}
    for row in companies:
        ticker = row["ticker"]
        inputs = row.get("scenario_inputs") or {}
        if inputs.get("metric") != "sales" or ticker not in INDUSTRY:
            continue  # EBITDA-based models (RDNT) keep their own multiples
        industry = INDUSTRY[ticker]
        sector = industries[industry]["ps"]
        bear = min(sector, median)                      # never above the base case
        own = price_to_sales(row)
        if ticker in MATURE and own:
            bull = max(own, min(sector, median, 1.5 * own))
            out[ticker] = {
                "metric": "sales", "bear": round(min(sector, 0.75 * own), 2), "base": round(own, 2), "bull": round(bull, 2),
                "basis": {
                    "bear": f"lower of {industry} price/sales {sector:g}x (Damodaran {snapshot['data_date']}) and 75% of today's {own:.1f}x",
                    "base": f"today's own price/sales {own:.1f}x kept: {MATURE[ticker]}, so no AI re-rating",
                    "bull": f"at most the lowest of the industry ({sector:g}x), the AI-medicine peer median ({median:g}x) and 1.5x today's",
                },
                "sector_industry": industry, "mature": True,
            }
            continue
        out[ticker] = {
            "metric": "sales",
            "bear": bear, "base": median, "bull": max(q3, median),
            "basis": {
                "bear": f"{industry} price/sales {sector:g}x, Damodaran ({snapshot['data_date']}, {industries[industry]['firms']} firms)",
                "base": f"median price/sales of {len(peers)} AI-medicine peers today ({median:g}x)",
                "bull": f"top quartile of the same peers ({q3:g}x)",
            },
            "sector_industry": industry,
        }
    return {"asOf": date.today().isoformat(), "damodaran": {k: snapshot.get(k) for k in ("source", "data_date", "fetched")},
            "peers": peers, "peerQuartiles": {"q1": q1, "median": median, "q3": q3}, "companies": out}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--offline", action="store_true", help="use the stored Damodaran snapshot")
    args = parser.parse_args()
    snapshot = None
    if not args.offline:
        try:
            snapshot = refresh_snapshot()
        except Exception as exc:  # network or parse problem: fall back to the stored copy
            print(f"Damodaran refresh skipped: {exc}")
    if snapshot is None:
        snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    companies = json.loads(FINANCIALS.read_text(encoding="utf-8"))["companies"]
    result = calibrate(companies, snapshot)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    q = result["peerQuartiles"]
    print(f"peers {len(result['peers'])}: q1 {q['q1']}x median {q['median']}x q3 {q['q3']}x; Damodaran {snapshot['data_date']}")
    for ticker, c in result["companies"].items():
        print(f"  {ticker:5} bear {c['bear']:>5}x base {c['base']:>5}x bull {c['bull']:>5}x  ({c['sector_industry']})")


if __name__ == "__main__":
    main()
