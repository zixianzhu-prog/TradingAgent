from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


RATING_RE = re.compile(
    r"\*\*Rating\*\*\s*:\s*(STRONG BUY|BUY|OVERWEIGHT|HOLD|NEUTRAL|UNDERWEIGHT|SELL|STRONG SELL)",
    re.IGNORECASE,
)
PROPOSAL_RE = re.compile(r"FINAL TRANSACTION PROPOSAL\s*:\s*([^\n]+)", re.IGNORECASE)


def compact(text: str, limit: int = 280) -> str:
    text = re.sub(r"[#>*_`|]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def final_section(text: str) -> str:
    matches = list(re.finditer(r"^#{1,3}\s+(?:投资结论|结论|Research Manager Decision)\s*$", text, re.MULTILINE | re.IGNORECASE))
    if not matches:
        return ""
    return text[matches[-1].end():]


def import_directory(directory: Path) -> dict:
    ticker = directory.name.removeprefix("tradingagents-").upper()
    market_path = directory / "market_report.md"
    plan_path = directory / "investment_plan.md"
    market = market_path.read_text(encoding="utf-8") if market_path.is_file() else ""
    plan = plan_path.read_text(encoding="utf-8") if plan_path.is_file() else ""
    ratings = [value.upper() for value in RATING_RE.findall(plan)]
    proposals = [compact(value, 100) for value in PROPOSAL_RE.findall(plan)]
    conclusion = final_section(plan)
    return {
        "ticker": ticker,
        "status": "reviewed" if plan or market else "missing",
        "rating": ratings[-1] if ratings else "UNRATED",
        "proposal": proposals[-1] if proposals else "",
        "conclusion": compact(conclusion or plan),
        "marketSummary": compact(market),
        "components": {
            "market": bool(market),
            "debate": "Researcher Analysis" in plan,
            "risk": "Risk" in plan or "风险" in plan,
            "portfolioDecision": bool(ratings or proposals),
        },
        "sourceDirectory": str(directory),
    }


def import_report_tree(directory: Path, ticker: str, complete: bool) -> dict:
    if complete:
        market_path = directory / "1_analysts/market.md"
        plan_paths = [directory / "2_research/manager.md", directory / "5_portfolio/decision.md"]
        portfolio_path = directory / "5_portfolio/decision.md"
    else:
        market_path = directory / "market_report.md"
        plan_paths = [directory / "investment_plan.md", directory / "final_trade_decision.md"]
        portfolio_path = directory / "final_trade_decision.md"
    market = market_path.read_text(encoding="utf-8") if market_path.is_file() else ""
    plan = "\n\n".join(path.read_text(encoding="utf-8") for path in plan_paths if path.is_file())
    portfolio = portfolio_path.read_text(encoding="utf-8") if portfolio_path.is_file() else ""
    ratings = [value.upper() for value in RATING_RE.findall(portfolio)]
    proposals = [compact(value, 100) for value in PROPOSAL_RE.findall(portfolio)]
    return {
        "ticker": ticker.upper(),
        "status": "reviewed" if complete and portfolio else "incomplete",
        "rating": ratings[-1] if ratings and complete else "INCOMPLETE",
        "proposal": proposals[-1] if proposals and complete else "",
        "conclusion": compact(portfolio or plan),
        "marketSummary": compact(market),
        "components": {
            "market": bool(market),
            "debate": any(path.is_file() for path in plan_paths),
            "risk": complete and (directory / "4_risk").is_dir(),
            "portfolioDecision": bool(portfolio) and complete,
        },
        "sourceDirectory": str(directory),
    }


def build(input_root: Path, tradingagents_root: Path | None = None) -> dict:
    by_ticker = {
        review["ticker"]: review
        for review in (import_directory(path) for path in sorted(input_root.glob("tradingagents-*")) if path.is_dir())
    }
    if tradingagents_root and tradingagents_root.is_dir():
        completed_root = tradingagents_root / "reports"
        for path in sorted(completed_root.glob("*_*")):
            if not path.is_dir() or not (path / "5_portfolio/decision.md").is_file():
                continue
            ticker = path.name.split("_", 1)[0].upper()
            by_ticker[ticker] = import_report_tree(path, ticker, complete=True)
        for ticker_dir in sorted(tradingagents_root.iterdir()):
            if not ticker_dir.is_dir() or ticker_dir.name == "reports":
                continue
            date_dirs = sorted((path for path in ticker_dir.iterdir() if path.is_dir()), reverse=True)
            if not date_dirs:
                continue
            reports = date_dirs[0] / "reports"
            ticker = ticker_dir.name.upper()
            if reports.is_dir() and ticker not in by_ticker:
                by_ticker[ticker] = import_report_tree(reports, ticker, complete=False)
    return {"generatedAt": datetime.now(timezone.utc).isoformat(), "reviews": sorted(by_ticker.values(), key=lambda row: row["ticker"])}


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize saved TradingAgents Markdown reports into dashboard JSON.")
    parser.add_argument("--input-root", type=Path, default=Path("outputs"))
    parser.add_argument("--tradingagents-root", type=Path)
    parser.add_argument("--output", type=Path, default=Path("state/tradingagents-reviews.json"))
    args = parser.parse_args()
    payload = build(args.input_root, args.tradingagents_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
