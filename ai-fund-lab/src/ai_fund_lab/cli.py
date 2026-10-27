from __future__ import annotations

import argparse
import json

from .config import load_settings
from .pipeline import run_pipeline


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Paper-only AI fund research lab")
    result.add_argument("--config", help="Path to a JSON config file")
    result.add_argument("--state", default="state/paper.json")
    result.add_argument("--reports", default="reports")
    result.add_argument(
        "--execute-paper",
        action="store_true",
        help="Persist simulated fills locally. Never sends a broker order.",
    )
    return result


def main() -> None:
    args = parser().parse_args()
    settings = load_settings(args.config)
    report = run_pipeline(settings, args.state, args.reports, args.execute_paper)
    summary = {
        "mode": report["mode"],
        "report_path": report["report_path"],
        "signals": len(report["results"]),
        "orders": sum(1 for x in report["results"] if x["order"]),
        "fills": sum(1 for x in report["results"] if x["fill"]),
        "paper_cash": report["portfolio"]["cash"],
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

