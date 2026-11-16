from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TA_ROOT = ROOT / "work/TradingAgents"
TA_CLI = TA_ROOT / ".venv/bin/tradingagents"
REPORT_ROOT = TA_ROOT / "data/logs/reports"
DEFAULT_PRIORITY = ("RDNT", "SOPH", "TEM", "SDGR", "CERT", "NTRA", "RXRX", "GH", "ABCL", "ISRG", "GEHC", "IQV", "NVDA")
ALL_ANALYSTS = "market,sentiment,news,fundamentals"


def load_universe(path: Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    available = [row["ticker"].upper() for row in payload.get("companies", [])]
    priority = [ticker for ticker in DEFAULT_PRIORITY if ticker in available]
    return priority + [ticker for ticker in available if ticker not in priority]


def newest_review(ticker: str) -> Path | None:
    candidates = [path for path in REPORT_ROOT.glob(f"{ticker}_*") if path.is_dir()]
    candidates = [path for path in candidates if (path / "5_portfolio/decision.md").is_file()]
    return max(candidates, key=lambda path: path.stat().st_mtime) if candidates else None


def review_age(path: Path | None, today: date) -> int | None:
    if path is None:
        return None
    parts = path.name.split("_", 2)
    if len(parts) > 1:
        try:
            return (today - datetime.strptime(parts[1], "%Y%m%d").date()).days
        except ValueError:
            pass
    return (today - datetime.fromtimestamp(path.stat().st_mtime).date()).days


def select_due(tickers: list[str], today: date, cadence_days: int, force: bool) -> list[dict]:
    rows = []
    for ticker in tickers:
        previous = newest_review(ticker)
        age = review_age(previous, today)
        rows.append({
            "ticker": ticker,
            "previousReview": str(previous) if previous else "",
            "ageDays": age,
            "due": force or age is None or age >= cadence_days,
        })
    return rows


def run_one(ticker: str, analysis_date: str, depth: int, models: tuple[str, str]) -> dict:
    quick, deep = models
    env = os.environ.copy()
    env.update({
        "TRADINGAGENTS_RESULTS_DIR": str(TA_ROOT / "data/logs"),
        "TRADINGAGENTS_LLM_PROVIDER": env.get("TRADINGAGENTS_LLM_PROVIDER", "chatgpt"),
        "TRADINGAGENTS_QUICK_THINK_LLM": env.get("TRADINGAGENTS_QUICK_THINK_LLM", quick),
        "TRADINGAGENTS_DEEP_THINK_LLM": env.get("TRADINGAGENTS_DEEP_THINK_LLM", deep),
        "TRADINGAGENTS_OUTPUT_LANGUAGE": env.get("TRADINGAGENTS_OUTPUT_LANGUAGE", "Chinese"),
        "TRADINGAGENTS_MAX_DEBATE_ROUNDS": str(depth),
        "TRADINGAGENTS_MAX_RISK_ROUNDS": str(depth),
        "TRADINGAGENTS_CHECKPOINT_ENABLED": "true",
    })
    command = [
        str(TA_CLI),
        "--ticker", ticker,
        "--date", analysis_date,
        "--analysts", ALL_ANALYSTS,
        "--save",
        "--no-show",
        "--html",
        "--checkpoint",
    ]
    started = datetime.now(timezone.utc)
    completed = subprocess.run(command, cwd=TA_ROOT, env=env, text=True)
    return {
        "ticker": ticker,
        "returnCode": completed.returncode,
        "startedAt": started.isoformat(),
        "finishedAt": datetime.now(timezone.utc).isoformat(),
        "reportDirectory": str(newest_review(ticker) or ""),
    }


def refresh_import() -> None:
    subprocess.run(
        [
            str(ROOT / "trend-agent/.venv/bin/python"),
            str(ROOT / "scripts/import_tradingagents_reports.py"),
            "--input-root", str(ROOT / "outputs"),
            "--tradingagents-root", str(TA_ROOT / "data/logs"),
            "--output", str(ROOT / "state/tradingagents-reviews.json"),
        ],
        cwd=ROOT,
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run full TradingAgents reviews for due AI Medicine candidates.")
    parser.add_argument("--universe", type=Path, default=ROOT / "trend-agent/ai-medicine-universe.json")
    parser.add_argument("--tickers", help="Optional comma-separated override")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--cadence-days", type=int, default=7)
    parser.add_argument("--limit", type=int, default=1, help="Maximum model-consuming reviews in this invocation")
    parser.add_argument("--depth", type=int, choices=(1, 3, 5), default=1)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--plan", action="store_true", help="Print the queue without calling an LLM")
    parser.add_argument("--quick-model", default="gpt-5.6-luna")
    parser.add_argument("--deep-model", default="gpt-5.6-sol")
    parser.add_argument("--state-output", type=Path)
    args = parser.parse_args()

    if not TA_CLI.is_file():
        raise SystemExit(f"TradingAgents CLI not found: {TA_CLI}")
    today = datetime.strptime(args.date, "%Y-%m-%d").date()
    tickers = [value.strip().upper() for value in args.tickers.split(",")] if args.tickers else load_universe(args.universe)
    queue = select_due(tickers, today, args.cadence_days, args.force)
    due = [row for row in queue if row["due"]]
    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "analysisDate": args.date,
        "mode": "plan" if args.plan else "full-review",
        "analysts": ALL_ANALYSTS.split(","),
        "debateRounds": args.depth,
        "riskRounds": args.depth,
        "queue": queue,
        "runs": [],
    }
    if not args.plan:
        for row in due[: max(0, args.limit)]:
            result = run_one(row["ticker"], args.date, args.depth, (args.quick_model, args.deep_model))
            payload["runs"].append(result)
            if result["returnCode"] != 0:
                break
        refresh_import()
    state_output = args.state_output or ROOT / "state" / (
        "tradingagents-full-review-plan.json" if args.plan else "tradingagents-full-review-run.json"
    )
    state_output.parent.mkdir(parents=True, exist_ok=True)
    state_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "due": len(due),
        "selected": [row["ticker"] for row in due[: max(0, args.limit)]],
        "completed": sum(row["returnCode"] == 0 for row in payload["runs"]),
        "errors": sum(row["returnCode"] != 0 for row in payload["runs"]),
        "state": str(state_output),
    }, ensure_ascii=False))
    if any(row["returnCode"] != 0 for row in payload["runs"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
