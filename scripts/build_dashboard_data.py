from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from investment_scoring import calculate_scores

ROOT = Path(__file__).resolve().parents[1]

AI_EXPOSURE_LABELS = {
    "RDNT": "影像中心运营商 + AI期权（Digital Health占Q3收入5.2%，外部部分估算3.2%）",
    "SOPH": "直接精准医疗数据平台",
    "TEM": "直接精准医疗数据平台",
    "ISRG": "高质量手术机器人平台，AI为次要增量",
    "GEHC": "大型影像设备平台，AI为功能层",
    "IQV": "临床数据/CRO平台，AI为效率层",
    "NVDA": "算力基准，非AI医疗纯业务",
}


def research_advice(row: dict) -> tuple[str, str]:
    """Turn independent evidence gates into research guidance, never an order."""
    serenity_ready = row["serenity"] == "research-ready"
    if row["serenity"] == "revalidate":
        return "证据重审", "重大事件影响原有判断，查看逐项引用、反证和待核验材料"
    if row["serenity"] == "reject":
        return "暂缓", "存在未通过的研究门槛，市场预测不能抵消该缺口"
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


def ai_medicine_action(peer: dict, serenity_row: dict) -> str:
    gate = serenity_row.get("automated_gate", {})
    if gate.get("decision") == "revalidate":
        return "事件重验证"
    if gate.get("completenessScore", 0) >= 50 and gate.get("evidenceQualityScore", 0) >= 50 and peer.get("screenScore", 0) >= 75:
        return "优先深挖"
    if peer.get("screenScore", 0) >= 90:
        return "高潜力待验证"
    return "观察"


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


def performance_rows(database: Path) -> tuple[list[dict], dict, dict]:
    if not database.is_file():
        return [], {str(h): {"samples": 0} for h in (1, 5, 20, 60)}, {"tasks": [], "latest": []}
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    predictions = [dict(row) for row in connection.execute(
        "SELECT * FROM predictions ORDER BY as_of DESC, ticker"
    ).fetchall()]
    has_benchmarks = connection.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='benchmark_outcomes'"
    ).fetchone()[0]
    benchmark_columns = {
        row[1] for row in connection.execute("PRAGMA table_info(benchmark_outcomes)")
    } if has_benchmarks else set()
    has_cohorts = connection.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='prediction_cohorts'"
    ).fetchone()[0]
    metrics = {}
    for horizon in (1, 5, 20, 60):
        if has_benchmarks:
            xbi_select = "xbi_return, excess_xbi" if {"xbi_return", "excess_xbi"} <= benchmark_columns else "NULL AS xbi_return, NULL AS excess_xbi"
            cohort_join = "JOIN prediction_cohorts c ON c.ticker=b.ticker AND c.as_of=b.prediction_as_of" if has_cohorts else ""
            cohort_where = "AND c.cohort='ai-medicine'" if has_cohorts else ""
            rows = connection.execute(
                f"SELECT b.prediction_as_of, b.realized_return, b.direction_correct, b.spy_return, b.xlv_return, {xbi_select}, b.excess_spy, b.excess_xlv, b.random_return, b.momentum_return FROM benchmark_outcomes b {cohort_join} WHERE b.horizon=? {cohort_where}",
                (horizon,),
            ).fetchall()
        else:
            rows = []
        avg = lambda key: sum(row[key] for row in rows if row[key] is not None) / len([row for row in rows if row[key] is not None]) if any(row[key] is not None for row in rows) else None
        metrics[str(horizon)] = {
            "samples": len(rows),
            "distinctDates": len({row["prediction_as_of"] for row in rows}),
            "averageReturn": avg("realized_return"),
            "hitRate": avg("direction_correct"),
            "spyReturn": avg("spy_return"),
            "xlvReturn": avg("xlv_return"),
            "xbiReturn": avg("xbi_return"),
            "excessSpy": avg("excess_spy"),
            "excessXlv": avg("excess_xlv"),
            "excessXbi": avg("excess_xbi"),
            "randomReturn": avg("random_return"),
            "momentumReturn": avg("momentum_return"),
            "validationStatus": "insufficient-sample" if len(rows) < 30 or len({row["prediction_as_of"] for row in rows}) < 10 else "initial-evidence" if avg("excess_spy") is not None and avg("excess_spy") > 0 and avg("excess_xlv") > 0 and avg("excess_xbi") is not None and avg("excess_xbi") > 0 else "not-validated",
        }
    has_tasks = connection.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='prediction_tasks'"
    ).fetchone()[0]
    task_payload = {"tasks": [], "latest": []}
    if has_tasks:
        task_payload["tasks"] = [dict(row) for row in connection.execute(
            """SELECT task_type AS taskType, COUNT(*) AS samples,
                      COUNT(DISTINCT as_of) AS distinctDates, MAX(as_of) AS latestAsOf
               FROM prediction_tasks GROUP BY task_type ORDER BY task_type"""
        ).fetchall()]
        latest_day = connection.execute("SELECT MAX(as_of) FROM prediction_tasks").fetchone()[0]
        if latest_day:
            task_payload["latest"] = [dict(row) for row in connection.execute(
                """SELECT ticker, as_of AS asOf, task_type AS taskType,
                          horizon_sessions AS horizonSessions, claim, numeric_value AS numericValue,
                          confidence_score AS confidenceScore
                   FROM prediction_tasks WHERE as_of=? ORDER BY ticker, task_type""", (latest_day,)
            ).fetchall()]
    connection.close()
    return predictions, metrics, task_payload


def build_stock_detail(row: dict, serenity_row: dict, theme: dict) -> dict:
    checks = {
        "供应链图": serenity_row.get("supply_chain_map", "unreviewed"),
        "卡位证据": serenity_row.get("chokepoint_evidence", "unreviewed"),
        "客户依赖": serenity_row.get("customer_dependency", "unreviewed"),
        "纯业务暴露": serenity_row.get("pure_play", "unreviewed"),
        "多节点控制": serenity_row.get("multi_node_control", "unreviewed"),
        "财报验证": serenity_row.get("earnings_validation", "unreviewed"),
        "管理层与治理": serenity_row.get("management_governance", "unreviewed"),
        "反方论点": serenity_row.get("counter_thesis", "unreviewed"),
    }
    risks = [label for label, value in checks.items() if value in {"partial", "pending", "unknown", "fail", "unreviewed"}]
    if row["technicalScore"] < 50:
        risks.append("当前技术趋势较弱")
    return {
        "serenityGateReviews": serenity_row.get("gate_reviews", {}),
        "serenityReviewStatus": serenity_row.get("review_status", "not-run"),
        "serenityReviewPath": serenity_row.get("review_path"),
        "serenityEffectiveGates": serenity_row.get("automated_gate", {}).get("gateStates", {}),
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
    serenity_payload = load(ROOT / "state/serenity-auto-assessments.json", {"companies": []})
    serenity = {row["ticker"]: row for row in serenity_payload["companies"]}
    serenity_gate_payload = load(ROOT / "state/serenity-gate-results.json", {"companies": [], "summary": {}})
    for gate_row in serenity_gate_payload.get("companies", []):
        ticker = gate_row["ticker"]
        serenity.setdefault(ticker, {})["serenity_decision"] = gate_row["decision"]
        serenity[ticker]["automated_gate"] = gate_row
    tradingagents_payload = load(ROOT / "state/tradingagents-reviews.json", {"reviews": []})
    tradingagents = {row["ticker"]: row for row in tradingagents_payload["reviews"]}
    ai_medicine_market = latest(ROOT / "outputs/ai-medicine-market")
    nvidia_market = latest(ROOT / "outputs/nvidia-market")
    ai_medicine_theses = load(ROOT / "trend-agent/ai-medicine-theses.json", {"candidates": []})
    ai_medicine_audit_payload = load(ROOT / "state/ai-medicine-thesis-audit.json", {"audits": []})
    ai_medicine_audits = {row["ticker"]: row for row in ai_medicine_audit_payload.get("audits", [])}
    ai_medicine_financial_payload = load(ROOT / "state/ai-medicine-financial-scenarios.json", {"companies": []})
    ai_medicine_financials = {row["ticker"]: row for row in ai_medicine_financial_payload.get("companies", [])}
    independent_evidence_payload = load(ROOT / "trend-agent/ai-medicine-independent-evidence.json", {"companies": []})
    independent_evidence = {row["ticker"]: row for row in independent_evidence_payload.get("companies", [])}
    event_revalidation = load(ROOT / "state/event-revalidation.json", {"scheduledEvents": [], "revalidationTasks": [], "summary": {}})
    disclosure_divergences = load(ROOT / "state/disclosure-divergences.json", {"companies": [], "summary": {}})
    clinical_trials = load(ROOT / "state/clinical-trials-snapshot.json", {"studies": [], "changes": [], "currentRisks": [], "summary": {}})
    evidence_graph = load(ROOT / "state/ai-medicine-evidence-graph.json", {"nodes": [], "edges": [], "companies": [], "summary": {}})
    sec_xbrl = load(ROOT / "state/sec-xbrl-validation.json", {"companies": [], "summary": {}})
    ai_medicine_peer_screen = load(ROOT / "state/ai-medicine-peer-screen.json", {"companies": [], "deepReviewed": [], "challengers": []})
    ai_medicine_peers = {row["ticker"]: row for row in ai_medicine_peer_screen.get("companies", [])}
    action_buckets = {name: [] for name in ("优先深挖", "高潜力待验证", "观察", "事件重验证")}
    for candidate in [*ai_medicine_theses.get("candidates", []), *ai_medicine_theses.get("expanded_deep_dives", [])]:
        ticker = candidate["ticker"]
        action_buckets[ai_medicine_action(ai_medicine_peers.get(ticker, {}), serenity.get(ticker, {}))].append(ticker)
    ai_medicine_thesis_memory = load(ROOT / "state/ai-medicine-thesis-memory.json", {"history": [], "latest": {"companies": {}}, "summary": {}})
    form4_monitor = load(ROOT / "state/form4-snapshot.json", {"filings": [], "newFilings": [], "marketTransactions": [], "summary": {}})
    fda_ai_devices = load(ROOT / "state/fda-ai-devices.json", {"companyCoverage": [], "companyDevices": {}, "summary": {}, "status": "not-run"})
    hidden_gems = load(ROOT / "state/hidden-gems.json", {"candidates": [], "allCompanies": [], "summary": {}})
    finrobot_event_analysis = {"providerMode": "disabled", "events": [], "summary": {}}
    daily_data_inventory = load(ROOT / "state/daily-data-inventory.json", {"storage": {}, "reports": [], "benchmarkOutcomes": []})
    market_profiles = load(ROOT / "state/market-profiles.json", {"profiles": [], "summary": {}})
    scientific_frontier = load(ROOT / "state/scientific-frontier.json", {"works": [], "pubmed": [], "graph": {"nodes": [], "edges": []}, "summary": {}})
    science_commercialization = load(ROOT / "state/science-commercialization-graph.json", {"companies": [], "graph": {"nodes": [], "edges": []}, "summary": {}})
    technology_ownership = load(ROOT / "state/technology-ownership.json", {"companies": [], "summary": {}})
    uspto_assignment_validation = load(ROOT / "state/uspto-assignment-validation.json", {"companies": [], "summary": {}})
    institutional_ownership = load(ROOT / "state/institutional-ownership.json", {"filings": [], "summary": {}})
    opinion_benchmark = load(ROOT / "state/opinion-benchmark.json", {"calls": [], "fundSignals": [], "summary": {}})
    management_radar = load(ROOT / "state/management-radar.json", {"companies": [], "summary": {}})
    event_prediction_validation = load(ROOT / "state/event-prediction-validation.json", {"summary": {}, "episodes": [], "scored": []})
    predictions, performance, prediction_tasks = performance_rows(ROOT / "state/investment-score-history.db")
    stocks = market_rows(ai_medicine_market, theme_links, company_news, serenity, "ai_medicine")
    stocks += market_rows(nvidia_market, theme_links, company_news, serenity, "nvidia")
    stocks.sort(key=lambda row: row["combinedScore"], reverse=True)
    themes_by_name = {row["name"]: row for row in trends.get("themes", [])}
    for row in stocks:
        review = tradingagents.get(row["ticker"])
        row["tradingAgents"] = review or {"status": "pending", "rating": "PENDING", "conclusion": "尚未运行多智能体审查"}
        link = theme_links.get(row["ticker"], {})
        row["detail"] = build_stock_detail(row, serenity.get(row["ticker"], {}), themes_by_name.get(link.get("theme"), {}))
    top = stocks[0] if stocks else None
    balanced = max(stocks, key=lambda row: row["combinedScore"], default=None)
    exposure = max(stocks, key=lambda row: row["evidenceScore"], default=None)
    conflicts = [row for row in stocks if row["technicalScore"] < 20]
    conflict = max(conflicts, key=lambda row: row["forecastReturn"], default=None)
    serenity_ready = [row for row in stocks if row["serenity"] == "research-ready"]
    closest_pass = max(serenity_ready, key=lambda row: row["combinedScore"], default=None)
    momentum_pick = max(stocks, key=lambda row: row["combinedScore"], default=None)
    top_theme = max(trends.get("themes", []), key=lambda row: row.get("score", 0), default=None)
    latest_updates = []
    if top_theme:
        latest_updates.append({"type": "theme", "title": f"{top_theme['label']} 位居主题榜首", "detail": f"主题分 {top_theme['score']}，{top_theme['article_count']} 条证据，来自 {top_theme['source_count']} 个来源。"})
    for ticker in ("TEM", "SDGR", "RXRX", "ABCL"):
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
                "primary": (closest_pass or {}).get("ticker"),
                "tactical": (momentum_pick or {}).get("ticker"),
                "guidance": "优先研究基本面证据完整的候选；把高分动量股作为战术观察，不以单一模型输出代替估值与财报验证。",
            },
            "investmentGate": "No ticker has passed the full Serenity evidence and earnings gate.",
        },
        "predictions": predictions,
        "performance": performance,
        "predictionTasks": prediction_tasks,
        "eventPredictionValidation": event_prediction_validation,
        "tradingAgentsReviews": list(tradingagents.values()),
        "latestUpdates": latest_updates,
        "eventAgent": event_revalidation,
        "disclosureDivergences": disclosure_divergences,
        "clinicalTrials": clinical_trials,
        "evidenceGraph": evidence_graph,
        "secXbrlValidation": sec_xbrl,
        "form4Monitor": form4_monitor,
        "fdaAiDevices": fda_ai_devices,
        "hiddenGems": hidden_gems,
        "finrobotEventAnalysis": finrobot_event_analysis,
        "dailyDataInventory": daily_data_inventory,
        "marketProfiles": market_profiles,
        "scientificFrontier": scientific_frontier,
        "scienceCommercialization": science_commercialization,
        "technologyOwnership": technology_ownership,
        "usptoAssignmentValidation": uspto_assignment_validation,
        "institutionalOwnership": institutional_ownership,
        "opinionBenchmark": opinion_benchmark,
        "managementRadar": management_radar,
        "aiMedicinePeerScreen": ai_medicine_peer_screen,
        "aiMedicineThesisMemory": ai_medicine_thesis_memory,
        "serenityGate": serenity_gate_payload,
        "aiMedicine": {
            "title": ai_medicine_theses.get("title"),
            "note": ai_medicine_theses.get("important_note"),
            "rankingScope": ai_medicine_theses.get("ranking_scope"),
            "auditMethod": ai_medicine_audit_payload.get("method"),
            "actionBuckets": action_buckets,
            "candidates": [
                {
                    **candidate,
                    "audit": ai_medicine_audits.get(candidate["ticker"], {}),
                    "financial": ai_medicine_financials.get(candidate["ticker"], {}),
                    "serenity": serenity.get(candidate["ticker"], {}),
                    "exposureLabel": AI_EXPOSURE_LABELS.get(candidate["ticker"], candidate.get("classification")),
                    "independentEvidence": independent_evidence.get(candidate["ticker"], {}),
                    "actionBucket": ai_medicine_action(ai_medicine_peers.get(candidate["ticker"], {}), serenity.get(candidate["ticker"], {})),
                }
                for candidate in sorted(ai_medicine_theses.get("candidates", []), key=lambda row: row.get("rank", 999))
            ],
            "expandedDeepDives": [
                {
                    **candidate,
                    "audit": ai_medicine_audits.get(candidate["ticker"], {}),
                    "financial": ai_medicine_financials.get(candidate["ticker"], {}),
                    "serenity": serenity.get(candidate["ticker"], {}),
                    "exposureLabel": AI_EXPOSURE_LABELS.get(candidate["ticker"], candidate.get("classification")),
                    "independentEvidence": independent_evidence.get(candidate["ticker"], {}),
                    "actionBucket": ai_medicine_action(ai_medicine_peers.get(candidate["ticker"], {}), serenity.get(candidate["ticker"], {})),
                }
                for candidate in ai_medicine_theses.get("expanded_deep_dives", [])
            ],
        },
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
