from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MARKET_CAP_MIN_M = 400
MARKET_CAP_MAX_M = 5000


def points(value: str, full: int, partial: int = 0) -> int:
    if value == "pass":
        return full
    if value == "partial":
        return partial
    return 0


def score_company(link: dict[str, Any], serenity: dict[str, Any], financial: dict[str, Any], news: dict[str, Any], market_profile: dict[str, Any] | None = None) -> dict[str, Any]:
    ticker = link["ticker"]
    market_profile = market_profile or {}
    market_cap = financial.get("market_cap_m", market_profile.get("marketCapM"))
    cap_eligible = market_cap is not None and MARKET_CAP_MIN_M <= float(market_cap) <= MARKET_CAP_MAX_M
    article_count = int(news.get("article_count", 0))
    attention_points = 5 if article_count <= 5 else 3 if article_count <= 20 else 0
    breakdown = {
        "marketCap": 15 if cap_eligible else 0,
        "purePlay": 10 if link.get("pure_play") else 0,
        "chokepoint": points(serenity.get("chokepoint_evidence", "unknown"), 15, 8),
        "customerDependency": points(serenity.get("customer_dependency", "unknown"), 15, 7),
        "multiNodeControl": points(serenity.get("multi_node_control", "unknown"), 10, 5),
        "earningsValidation": points(serenity.get("earnings_validation", "unknown"), 10, 0),
        "financialResilience": 10 if financial.get("funding_risk") == "low" else 5 if financial.get("funding_risk") == "medium" else 0,
        "underfollowed": attention_points,
        "liquidity": 10 if market_profile.get("liquidityStatus") == "pass" else 5 if market_profile.get("liquidityStatus") == "partial" else 0,
    }
    total = sum(breakdown.values())
    missing = []
    if market_cap is None:
        missing.append("market cap")
    if serenity.get("customer_dependency") != "pass":
        missing.append("confirmed customer dependency")
    if serenity.get("earnings_validation") != "pass":
        missing.append("earnings validation")
    if market_profile.get("liquidityStatus") != "pass":
        missing.append("point-in-time dollar-volume liquidity")
    if not cap_eligible:
        status = "outside-size-range" if market_cap is not None else "incomplete"
    elif total >= 70 and serenity.get("customer_dependency") == "pass" and serenity.get("earnings_validation") == "pass" and financial.get("funding_risk") in {"low", "medium"} and market_profile.get("liquidityStatus") == "pass":
        status = "deep-research"
    elif total >= 50:
        status = "watch"
    else:
        status = "reject"
    return {
        "ticker": ticker,
        "company": link.get("company", ticker),
        "theme": link.get("theme"),
        "themeLabel": link.get("theme_label", link.get("theme")),
        "serenityRole": link.get("serenity_role"),
        "marketCapM": round(float(market_cap), 1) if market_cap is not None else None,
        "articleCount7d": article_count,
        "fundingRisk": financial.get("funding_risk", "unknown"),
        "runwayYearsProxy": financial.get("runway_years_proxy"),
        "averageDollarVolume60d": market_profile.get("averageDollarVolume60d"),
        "liquidityStatus": market_profile.get("liquidityStatus", "unknown"),
        "annualizedVolatility": market_profile.get("annualizedVolatility"),
        "score": total,
        "status": status,
        "breakdown": breakdown,
        "missingEvidence": missing,
        "sourceUrls": financial.get("sources", []),
        "claimBoundary": "Research priority only; liquidity remains unverified and this is not a buy signal.",
    }


def build(theme_links: dict, serenity: dict, financials: dict, news: dict, market_profiles: dict | None = None) -> dict:
    serenity_by_ticker = {row["ticker"]: row for row in serenity.get("companies", [])}
    financial_by_ticker = {row["ticker"]: row for row in financials.get("companies", [])}
    news_by_ticker = {row["ticker"]: row for row in news.get("companies", [])}
    market_by_ticker = {row["ticker"]: row for row in (market_profiles or {}).get("companies", [])}
    rows = []
    for link in theme_links.get("companies", []):
        ticker = link["ticker"]
        rows.append(score_company(link, serenity_by_ticker.get(ticker, {}), financial_by_ticker.get(ticker, {}), news_by_ticker.get(ticker, {}), market_by_ticker.get(ticker, {})))
    rows.sort(key=lambda row: (row["status"] != "deep-research", -row["score"], row["ticker"]))
    eligible = [row for row in rows if row["status"] in {"deep-research", "watch"}]
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "method": "Deterministic Serenity small/mid-cap screen: size, pure-play exposure, chokepoint, customer dependency, multi-node control, earnings, funding resilience, and seven-day attention.",
        "criteria": {"marketCapMinM": MARKET_CAP_MIN_M, "marketCapMaxM": MARKET_CAP_MAX_M},
        "summary": {
            "screened": len(rows),
            "withMarketCap": sum(row["marketCapM"] is not None for row in rows),
            "deepResearch": sum(row["status"] == "deep-research" for row in rows),
            "watch": sum(row["status"] == "watch" for row in rows),
        },
        "candidates": eligible,
        "allCompanies": rows,
        "claimBoundary": "A high score means deeper research priority. No candidate is called investable until point-in-time liquidity and all primary evidence are verified.",
    }


def render(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Hidden Gems / Underfollowed Candidates", "",
        "> 使用 Serenity 小中盘筛选方法寻找值得深入研究的冷门公司。分数是研究优先级，不是上涨概率或买入信号。", "",
        f"扫描 {summary['screened']} 家；{summary['withMarketCap']} 家具备可复核市值；{summary['deepResearch']} 家进入深度研究；{summary['watch']} 家观察。", "",
        "| 股票 | 主题 | 市值 | 60日平均成交额 | 7日文章 | Serenity角色 | 融资风险 | 分数 | 状态 |", "|---|---|---:|---:|---:|---|---|---:|---|",
    ]
    for row in payload["candidates"]:
        cap = f"${row['marketCapM'] / 1000:.2f}B" if row["marketCapM"] is not None else "—"
        volume = f"${row['averageDollarVolume60d'] / 1_000_000:.2f}M" if row.get("averageDollarVolume60d") is not None else "—"
        lines.append(f"| {row['ticker']} | {row['themeLabel']} | {cap} | {volume} | {row['articleCount7d']} | {row['serenityRole']} | {row['fundingRisk']} | {row['score']} | {row['status']} |")
    if not payload["candidates"]:
        lines.append("| — | — | — | — | — | 当前没有通过初筛的公司 | — | — | — |")
    lines += ["", "## 必须继续验证", ""]
    for row in payload["candidates"]:
        lines.append(f"- **{row['ticker']}**：{', '.join(row['missingEvidence']) or '无'}")
    lines += ["", "## 解释边界", "", "- 低新闻量只能表示当前配置源中的低关注度，不能证明市场没有定价。", "- 流动性尚未进入冻结台账，因此任何候选都不能据此直接交易。", "- 缺少市值或财务材料的公司保留在 JSON 审计结果中，不会被静默排除。", "- 最终必须经过来源核验、反方论点、财报和未来样本验证。", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Screen underfollowed small/mid-cap research candidates")
    parser.add_argument("--theme-links", required=True)
    parser.add_argument("--serenity", required=True)
    parser.add_argument("--financials", required=True)
    parser.add_argument("--news", required=True)
    parser.add_argument("--market-profiles")
    parser.add_argument("--json-output", required=True)
    parser.add_argument("--markdown-output", required=True)
    args = parser.parse_args()
    payload = build(
        json.loads(Path(args.theme_links).read_text(encoding="utf-8")),
        json.loads(Path(args.serenity).read_text(encoding="utf-8")),
        json.loads(Path(args.financials).read_text(encoding="utf-8")),
        json.loads(Path(args.news).read_text(encoding="utf-8")),
        json.loads(Path(args.market_profiles).read_text(encoding="utf-8")) if args.market_profiles and Path(args.market_profiles).is_file() else {},
    )
    json_path, markdown_path = Path(args.json_output), Path(args.markdown_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    markdown_path.write_text(render(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
