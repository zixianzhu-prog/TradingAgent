from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_config(theme_report: str, base_config: str, output: str, limit: int, theme: str | None, fallback_tickers: list[str] | None = None, include_tickers: list[str] | None = None) -> list[str]:
    payload = json.loads(Path(theme_report).read_text(encoding="utf-8"))
    rows = payload.get("companies", [])
    if theme:
        rows = [row for row in rows if row.get("theme") == theme]
    rows = [row for row in rows if row.get("decision") in {"deep-research", "watch"}]
    rows.sort(key=lambda row: row.get("transmission_score", 0), reverse=True)
    tickers = list(dict.fromkeys([*(row["ticker"] for row in rows), *(include_tickers or [])]))[:limit]
    if not tickers:
        tickers = list(dict.fromkeys(fallback_tickers or []))[:limit]
    if not tickers:
        raise SystemExit("No eligible theme-linked tickers found and no fallback ticker was configured")
    config = json.loads(Path(base_config).read_text(encoding="utf-8"))
    config["watchlist"] = tickers
    config["max_positions"] = min(len(tickers), int(config.get("max_positions", len(tickers))))
    Path(output).write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    return tickers


def main() -> None:
    parser = argparse.ArgumentParser(description="Build an ai-fund-lab config from theme-linked stocks")
    parser.add_argument("--theme-report", required=True)
    parser.add_argument("--base-config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--limit", type=int, default=4)
    parser.add_argument("--theme")
    parser.add_argument("--fallback-ticker", action="append", default=[])
    parser.add_argument("--include-ticker", action="append", default=[], help="Keep a configured coverage ticker even when today's news link is weak")
    args = parser.parse_args()
    tickers = build_config(args.theme_report, args.base_config, args.output, args.limit, args.theme, args.fallback_ticker, args.include_ticker)
    print(json.dumps({"watchlist": tickers, "output": args.output}))


if __name__ == "__main__":
    main()
