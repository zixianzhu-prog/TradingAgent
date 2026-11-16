"""Market validation layer for the 5-10 year ranking (step 3 of the pipeline).

Serenity decides long-term potential from filings. This script adds what the
market says today, for context only; nothing here changes the ranking:

  - price moves over one and three months, against XBI, and distance from the
    six-month high (OpenBB price history), to see whether a thesis is already
    priced in or has pulled back;
  - price / sales from the financial snapshot;
  - Kronos's five-day forecast from the latest daily market runs.

Writes state/market-validation.json. Run with the ai-fund-lab environment:
    ai-fund-lab/.venv/bin/python scripts/market_validation.py
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ai-fund-lab/src"))

ONE_MONTH, THREE_MONTHS, SIX_MONTHS = 21, 63, 126


def moves(closes: list[float]) -> dict:
    """Returns over 1 and 3 months and distance from the 6-month high, from daily closes (oldest first)."""
    if len(closes) < 2:
        return {}
    last = closes[-1]
    ret = lambda n: last / closes[-1 - n] - 1 if len(closes) > n else None
    window = closes[-SIX_MONTHS:]
    return {"last": last, "oneMonth": ret(ONE_MONTH), "threeMonths": ret(THREE_MONTHS), "fromHigh": last / max(window) - 1}


def reading(row: dict, xbi: dict) -> str:
    """Plain description of where the price stands; descriptive, not a signal."""
    three, high = row.get("threeMonths"), row.get("fromHigh")
    if three is None or high is None:
        return "not enough price history"
    excess = three - (xbi.get("threeMonths") or 0)
    if excess > 0.30:
        return "strong run-up vs XBI; more of the thesis may be priced in"
    if high < -0.25:
        return "well below its 6-month high; sentiment has cooled"
    if excess < -0.15:
        return "lagging XBI over 3 months"
    return "roughly in line with XBI"


def latest_kronos(paths: list[Path]) -> dict[str, dict]:
    """Five-day Kronos forecasts; later runs override earlier ones."""
    forecasts: dict[str, dict] = {}
    for path in sorted(paths, key=lambda p: p.name):
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for ticker, item in (report.get("kronos") or {}).items():
            if isinstance(item, dict) and item.get("forecast_return") is not None:
                forecasts[ticker] = {"forecastReturn": item["forecast_return"], "asOf": report.get("generated_at", "")[:10]}
    return forecasts


def main() -> None:
    parser = argparse.ArgumentParser(description="Market validation for the AI-medicine 5-10 year ranking")
    parser.add_argument("--ranking", default=str(ROOT / "state/ai-medicine-top5.json"))
    parser.add_argument("--financials", default=str(ROOT / "state/ai-medicine-financial-scenarios.json"))
    parser.add_argument("--market-dir", default=str(ROOT / "outputs/ai-medicine-market"))
    parser.add_argument("--extra-kronos", nargs="*", default=[], help="additional ai_fund_lab run reports")
    parser.add_argument("--provider", default="openbb")
    parser.add_argument("--output", default=str(ROOT / "state/market-validation.json"))
    args = parser.parse_args()
    from ai_fund_lab.data import build_provider

    ranking = json.loads(Path(args.ranking).read_text(encoding="utf-8"))
    tickers = [r["ticker"] for r in ranking["ranking"]]
    financials = {r["ticker"]: r for r in json.loads(Path(args.financials).read_text(encoding="utf-8"))["companies"]}
    runs = sorted(Path(args.market_dir).glob("run-*.json"))[-5:] + [Path(p) for p in args.extra_kronos]
    kronos = latest_kronos(runs)
    provider = build_provider(args.provider)
    history = {}
    for ticker in tickers + ["XBI"]:
        try:
            bars = provider.history(ticker, SIX_MONTHS + 5)
            history[ticker] = moves([b.close for b in bars])
            history[ticker]["asOf"] = bars[-1].day.isoformat() if bars else None
        except Exception as exc:  # one ticker's data error must not block the rest
            history[ticker] = {"error": str(exc)[:120]}
    xbi = history.get("XBI", {})
    companies = {}
    for ticker in tickers:
        row = dict(history.get(ticker, {}))
        if xbi.get("threeMonths") is not None and row.get("threeMonths") is not None:
            row["threeMonthsVsXbi"] = row["threeMonths"] - xbi["threeMonths"]
        row["priceToSales"] = financials.get(ticker, {}).get("price_to_sales_approx")
        row["kronos5d"] = kronos.get(ticker)
        row["reading"] = reading(row, xbi)
        companies[ticker] = row
    output = {"generatedAt": datetime.now(timezone.utc).isoformat(), "provider": args.provider, "xbi": xbi,
              "note": "Context only. Market data does not change the Serenity-based 5-10 year ranking.", "companies": companies}
    Path(args.output).write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"companies": len(companies), "kronos": sum(1 for c in companies.values() if c["kronos5d"]), "output": args.output}))


if __name__ == "__main__":
    main()
