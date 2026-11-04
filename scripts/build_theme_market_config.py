from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_config(theme_report: str, base_config: str, output: str, limit: int, theme: str | None) -> list[str]:
    payload = json.loads(Path(theme_report).read_text(encoding="utf-8"))
    rows = payload.get("companies", [])
    if theme:
        rows = [row for row in rows if row.get("theme") == theme]
    rows = [row for row in rows if row.get("decision") in {"deep-research", "watch"}]
    rows.sort(key=lambda row: row.get("transmission_score", 0), reverse=True)
    tickers = list(dict.fromkeys(row["ticker"] for row in rows))[:limit]
    if not tickers:
        raise SystemExit("No eligible theme-linked tickers found")
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
    args = parser.parse_args()
    tickers = build_config(args.theme_report, args.base_config, args.output, args.limit, args.theme)
    print(json.dumps({"watchlist": tickers, "output": args.output}))


if __name__ == "__main__":
    main()
