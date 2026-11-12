from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def latest(directory: Path) -> dict:
    files = sorted(directory.glob("run-*.json"), key=lambda path: path.stat().st_mtime)
    return json.loads(files[-1].read_text(encoding="utf-8")) if files else {}


def audit_candidate(candidate: dict, serenity: dict, market: dict) -> dict:
    ticker = candidate["ticker"]
    serenity_row = serenity.get(ticker, {})
    signal_row = next((row for row in market.get("results", []) if row.get("signal", {}).get("ticker") == ticker), {})
    official_sources = [url for url in candidate.get("sources", []) if url.startswith("https://")]
    falsifiers = candidate.get("falsifiers", [])
    checks = {
        "official_sources": min(20, len(official_sources) * 10),
        "explicit_thesis": 15 if candidate.get("thesis") else 0,
        "serenity_review": 20 if serenity_row.get("serenity_decision") in {"research-ready", "watch"} else 0,
        "bear_case": 15 if candidate.get("bear_case") else 0,
        "falsifiers": min(15, len(falsifiers) * 5),
        "market_context": 10 if signal_row else 0,
        "model_context": 5 if ticker in market.get("kronos", {}) else 0,
    }
    score = sum(checks.values())
    missing = []
    if len(official_sources) < 2:
        missing.append("需要至少两个独立的官方或监管来源")
    if len(falsifiers) < 3:
        missing.append("需要至少三个可证伪条件")
    if not signal_row:
        missing.append("缺少当前市场数据")
    if serenity_row.get("earnings_validation") != "pass":
        missing.append("财报验证尚未通过")
    confidence = "high" if score >= 90 and not missing else "medium" if score >= 70 else "low"
    signal = signal_row.get("signal", {})
    forecast = market.get("kronos", {}).get(ticker, {}).get("forecast_return")
    return {
        "ticker": ticker,
        "auditScore": score,
        "evidenceConfidence": confidence,
        "missingEvidence": missing,
        "bearCase": candidate.get("bear_case"),
        "falsifiers": falsifiers,
        "evidenceChain": [
            {"stage": "Forward signal", "claim": candidate.get("why_now"), "provenance": "human-curated from official sources"},
            {"stage": "Business transmission", "claim": candidate.get("thesis"), "provenance": "human research thesis"},
            {"stage": "Serenity gate", "claim": serenity_row.get("reason"), "provenance": "rule-based checklist + human evidence review"},
            {"stage": "Market context", "claim": f"Price {signal.get('price', 'n/a')}; five-day Kronos context {forecast:+.2%}" if forecast is not None else "Market context unavailable", "provenance": "OpenBB market data + Kronos model"},
            {"stage": "Decision", "claim": candidate.get("classification"), "provenance": "research ranking; not an order"},
        ],
        "provenance": {
            "news_and_filings": "external source data",
            "long_horizon_thesis": "human-curated research",
            "serenity_gate": "deterministic checklist with reviewed evidence",
            "market_data": "OpenBB",
            "short_horizon_forecast": "Kronos model",
            "audit_score": "deterministic completeness score",
        },
        "componentScores": checks,
        "sources": official_sources,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit investment theses for evidence, provenance and falsifiability")
    parser.add_argument("--theses", required=True)
    parser.add_argument("--serenity", required=True)
    parser.add_argument("--market-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    theses = json.loads(Path(args.theses).read_text(encoding="utf-8"))
    serenity_payload = json.loads(Path(args.serenity).read_text(encoding="utf-8"))
    serenity = {row["ticker"]: row for row in serenity_payload.get("companies", [])}
    market = latest(Path(args.market_dir))
    audits = [audit_candidate(candidate, serenity, market) for candidate in theses.get("candidates", [])]
    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "method": "Evidence completeness audit; score measures research traceability, not expected return.",
        "audits": audits,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
