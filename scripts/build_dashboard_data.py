from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from investment_scoring import calculate_scores

ROOT = Path(__file__).resolve().parents[1]


def research_advice(row: dict) -> tuple[str, str]:
    """Turn independent evidence gates into research guidance, never an order."""
    serenity_ready = row["serenity"] == "research-ready"
    combined = row["combinedScore"]
    evidence = row["evidenceScore"]
    technical = row["technicalScore"]
    forecast = row["forecastReturn"]
    if serenity_ready and combined >= 70:
        return "核心候选", "基本面证据与市场信号同时通过，进入估值和仓位研究"
    if serenity_ready:
        return "基本面优先", "Serenity 证据通过，但技术趋势尚未确认；优先跟踪而非追价"
    if combined >= 70:
        return "动量候选", "市场与预测信号较强，但供应链、客户或财报证据仍需补齐"
    if combined >= 55:
        return "次级观察", "信号有一定一致性，尚不足以进入高确信度研究"
    if forecast > 0.03 and evidence >= 60:
        return "高弹性观察", "主题关联和模型预测较强，但技术面或基本面存在明显缺口"
    if technical < 20 and forecast > 0.03:
        return "信号冲突", "模型预测向上但当前技术趋势弱，只观察不追涨"
    return "暂缓", "现有证据不足或信号不一致，等待新的新闻、财报或价格确认"


def load(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else default


def latest(directory: Path):
    files = sorted(directory.glob("run-*.json"), key=lambda path: path.stat().st_mtime)
    return load(files[-1], {}) if files else {}


def market_rows(market: dict, links: dict, news: dict, serenity: dict, category: str) -> list[dict]:
    rows = []
    for item in market.get("results", []):
        signal = item["signal"]
        ticker = signal["ticker"]
        link = links.get(ticker, {})
        company_news = news.get(ticker, {})
        thematic_score = link.get("transmission_score")
        score_input = {"news_score": thematic_score if thematic_score is not None else company_news.get("news_score", 0)}
        forecast = float(market.get("kronos", {}).get(ticker, {}).get("forecast_return", 0.0))
        scores = calculate_scores(signal, forecast, score_input)
        row = {
            "ticker": ticker,
            "category": category,
            "theme": link.get("theme_label", "前沿生物科技与公共卫生"),
            "price": round(float(signal["price"]), 2),
            "direction": signal["direction"],
            "themeScore": link.get("theme_score"),
            "evidenceScore": scores["news"],
            "technicalScore": scores["technical"],
            "kronosScore": scores["kronos"],
            "forecastReturn": forecast,
            "combinedScore": scores["combined"],
            "confidence": company_news.get("confidence", "theme-mapped"),
            "serenity": serenity.get(ticker, {}).get("serenity_decision", "unreviewed"),
            "orderIntent": bool(item.get("order")),
        }
        row["advice"], row["adviceReason"] = research_advice(row)
        rows.append(row)
    return rows


def performance_rows(database: Path) -> tuple[list[dict], dict]:
    if not database.is_file():
        return [], {str(h): {"samples": 0} for h in (1, 5, 20, 60)}
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    predictions = [dict(row) for row in connection.execute(
        "SELECT * FROM predictions ORDER BY as_of DESC, ticker"
    ).fetchall()]
    metrics = {}
    for horizon in (1, 5, 20, 60):
        rows = connection.execute(
            "SELECT realized_return, direction_correct FROM outcomes WHERE horizon=?", (horizon,)
        ).fetchall()
        metrics[str(horizon)] = {
            "samples": len(rows),
            "averageReturn": sum(row[0] for row in rows) / len(rows) if rows else None,
            "hitRate": sum(row[1] for row in rows) / len(rows) if rows else None,
        }
    connection.close()
    return predictions, metrics


def build_stock_detail(row: dict, serenity_row: dict, theme: dict) -> dict:
    checks = {
        "供应链图": serenity_row.get("supply_chain_map", "unreviewed"),
        "卡位证据": serenity_row.get("chokepoint_evidence", "unreviewed"),
        "客户依赖": serenity_row.get("customer_dependency", "unreviewed"),
        "纯业务暴露": serenity_row.get("pure_play", "unreviewed"),
        "多节点控制": serenity_row.get("multi_node_control", "unreviewed"),
        "财报验证": serenity_row.get("earnings_validation", "unreviewed"),
    }
    risks = [label for label, value in checks.items() if value in {"partial", "pending", "unknown", "fail", "unreviewed"}]
    if row["technicalScore"] < 50:
        risks.append("当前技术趋势较弱")
    return {
        "serenityReason": serenity_row.get("reason", "尚未完成 Serenity 深度审查。"),
        "serenityChecks": checks,
        "risks": risks or ["仍需持续检查估值、竞争和市场环境"],
        "validation": [
            "下一份财报继续验证收入、订单、利润率和现金流",
            "观察技术趋势是否与 Kronos 预测方向一致",
            "用未来 1/5/20/60 日真实收益回填预测成绩",
        ],
        "evidence": [
            {"title": item.get("title"), "url": item.get("url"), "source": item.get("source"), "publishedAt": item.get("published_at")}
            for item in theme.get("evidence", [])[:6]
        ],
    }


def main() -> None:
    trends = load(ROOT / "trend-agent/reports/daily/trends/latest-trends.json", {"themes": []})
    theme_links_payload = load(ROOT / "trend-agent/reports/daily/theme-stocks/theme-stock-links.json", {"companies": []})
    theme_links = {row["ticker"]: row for row in theme_links_payload["companies"]}
    company_news_payload = load(ROOT / "trend-agent/reports/daily/company-news/company-news-scores.json", {"companies": []})
    company_news = {row["ticker"]: row for row in company_news_payload["companies"]}
    serenity_payload = load(ROOT / "trend-agent/serenity-assessments.json", {"companies": []})
    serenity = {row["ticker"]: row for row in serenity_payload["companies"]}
    tradingagents_payload = load(ROOT / "state/tradingagents-reviews.json", {"reviews": []})
    tradingagents = {row["ticker"]: row for row in tradingagents_payload["reviews"]}
    biotech_market = latest(ROOT / "outputs/daily-market")
    theme_market = latest(ROOT / "outputs/theme-market")
    power_market = latest(ROOT / "outputs/power-theme-market")
    predictions, performance = performance_rows(ROOT / "state/investment-score-history.db")
    stocks = market_rows(theme_market, theme_links, company_news, serenity, "robotics")
    stocks += market_rows(power_market, theme_links, company_news, serenity, "power")
    stocks += market_rows(biotech_market, theme_links, company_news, serenity, "biotech")
    stocks.sort(key=lambda row: row["combinedScore"], reverse=True)
    themes_by_name = {row["name"]: row for row in trends.get("themes", [])}
    for row in stocks:
        review = tradingagents.get(row["ticker"])
        row["tradingAgents"] = review or {"status": "pending", "rating": "PENDING", "conclusion": "尚未运行多智能体审查"}
        link = theme_links.get(row["ticker"], {})
        row["detail"] = build_stock_detail(row, serenity.get(row["ticker"], {}), themes_by_name.get(link.get("theme"), {}))
    robotics = [row for row in stocks if row["category"] == "robotics"]
    top = stocks[0] if stocks else None
    balanced = max(robotics, key=lambda row: row["combinedScore"], default=None)
    exposure = max(robotics, key=lambda row: row["evidenceScore"], default=None)
    conflicts = [row for row in robotics if row["technicalScore"] < 20]
    conflict = max(conflicts, key=lambda row: row["forecastReturn"], default=None)
    serenity_ready = [row for row in stocks if row["serenity"] == "research-ready"]
    closest_pass = max(serenity_ready, key=lambda row: row["combinedScore"], default=None)
    momentum_pick = max(stocks, key=lambda row: row["combinedScore"], default=None)
    top_theme = max(trends.get("themes", []), key=lambda row: row.get("score", 0), default=None)
    latest_updates = []
    if top_theme:
        latest_updates.append({"type": "theme", "title": f"{top_theme['label']} 位居主题榜首", "detail": f"主题分 {top_theme['score']}，{top_theme['article_count']} 条证据，来自 {top_theme['source_count']} 个来源。"})
    for ticker in ("VRT", "MRNA", "NVDA"):
        review = tradingagents.get(ticker)
        if review and review.get("status") == "reviewed":
            latest_updates.append({"type": "rating", "title": f"{ticker} 完成多智能体审查", "detail": f"Portfolio Manager 最终评级：{review['rating']}。"})
    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "mode": "RESEARCH / DRY-RUN",
        "themes": trends.get("themes", []),
        "stocks": stocks,
        "recommendation": {
            "top": top,
            "roboticsBalanced": balanced,
            "roboticsExposure": exposure,
            "signalConflict": conflict,
            "closestPass": closest_pass,
            "fundamentalPick": closest_pass,
            "momentumPick": momentum_pick,
            "portfolioView": {
                "primary": "VRT" if closest_pass and closest_pass["ticker"] == "VRT" else (closest_pass or {}).get("ticker"),
                "tactical": (momentum_pick or {}).get("ticker"),
                "guidance": "优先研究基本面证据完整的候选；把高分动量股作为战术观察，不以单一模型输出代替估值与财报验证。",
            },
            "investmentGate": "No ticker has passed the full Serenity evidence and earnings gate.",
        },
        "predictions": predictions,
        "performance": performance,
        "tradingAgentsReviews": list(tradingagents.values()),
        "latestUpdates": latest_updates,
        "summary": {
            "themes": len(trends.get("themes", [])),
            "stocks": len(stocks),
            "priority": sum(row["combinedScore"] >= 70 for row in stocks),
            "fills": 0,
        },
    }
    output = ROOT / "dashboard/dist/data.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
