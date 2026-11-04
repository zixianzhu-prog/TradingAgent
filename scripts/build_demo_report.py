from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from investment_scoring import calculate_scores


def money(value: float) -> str:
    return f"${value:,.2f}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the unified paper-only agent demo report")
    parser.add_argument("--market-dir", required=True)
    parser.add_argument("--news-report")
    parser.add_argument("--trend-report")
    parser.add_argument("--serenity-assessment")
    parser.add_argument("--theme-stock-report")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    reports = sorted(Path(args.market_dir).glob("run-*.json"), key=lambda path: path.stat().st_mtime)
    if not reports:
        raise SystemExit(f"No market report found in {args.market_dir}")
    market_path = reports[-1]
    market = json.loads(market_path.read_text(encoding="utf-8"))
    news_by_ticker = {}
    if args.news_report and Path(args.news_report).is_file():
        news_payload = json.loads(Path(args.news_report).read_text(encoding="utf-8"))
        news_by_ticker = {item["ticker"]: item for item in news_payload.get("companies", [])}
    trend = None
    if args.trend_report and Path(args.trend_report).is_file():
        trend_payload = json.loads(Path(args.trend_report).read_text(encoding="utf-8"))
        themes = trend_payload.get("themes", [])
        trend = max(themes, key=lambda item: item.get("score", 0)) if themes else None
    serenity_by_ticker = {}
    if args.serenity_assessment and Path(args.serenity_assessment).is_file():
        serenity_payload = json.loads(Path(args.serenity_assessment).read_text(encoding="utf-8"))
        serenity_by_ticker = {item["ticker"]: item for item in serenity_payload.get("companies", [])}
    theme_stocks = []
    if args.theme_stock_report and Path(args.theme_stock_report).is_file():
        theme_stock_payload = json.loads(Path(args.theme_stock_report).read_text(encoding="utf-8"))
        theme_stocks = theme_stock_payload.get("companies", [])
    generated = datetime.fromisoformat(market["generated_at"]).astimezone(ZoneInfo("America/New_York"))
    combined_scores: list[tuple[str, int, str]] = []
    lines = [
        "# 前沿趋势投资研究 Agent：演示结果", "",
        f"生成时间：{generated:%Y-%m-%d %H:%M:%S %Z}", "",
        "> 研究与 dry-run 演示，不构成投资建议；未连接券商，未产生任何成交。", "",
        "## 1. 趋势发现", "",
        "- 主题：前沿生物科技、AI 临床研究与 mRNA 供应链",
        (f"- 当日趋势评分：{trend['score']}/100（{trend['status']}）" if trend else "- 当日趋势评分：无有效主题"),
        (f"- 证据：{trend['article_count']} 条近期匹配内容，来自 {trend['source_count']} 个独立来源" if trend else "- 证据：本次未达到主题匹配条件"),
        "- 正式研究触发门槛：70；评分用于排列研究优先级，不代表新闻真实性或上涨概率", "",
        "## 2. 公司证据门槛", "",
        "自动公司映射在严格筛选后保留两家公司：", "",
        "- MRNA / Moderna：mRNA、LNP 与制造平台直接暴露",
        "- DHR / Danaher：子公司 Aldevron 提供 mRNA cGMP、LNP 封装和无菌灌装能力", "",
        "## 3. OpenBB + Kronos 验证", "",
        "| 股票 | 收盘价 | MA20 | MA50 | ATR14 | 技术方向 | Kronos 5日 | 研究动作 |",
        "| --- | ---: | ---: | ---: | ---: | --- | ---: | --- |",
    ]
    for item in market["results"]:
        signal = item["signal"]
        reasons = {part.split("=", 1)[0]: part.split("=", 1)[1] for part in signal["reasons"] if "=" in part}
        lines.append(
            "| {ticker} | {price} | {ma20} | {ma50} | {atr} | {direction} | {kronos} | {action} |".format(
                ticker=signal["ticker"], price=money(signal["price"]),
                ma20=reasons.get("MA20", "n/a"), ma50=reasons.get("MA50", "n/a"),
                atr=reasons.get("ATR14", "n/a"), direction=signal["direction"],
                kronos=reasons.get("Kronos5D", "n/a"),
                action="paper intent" if item["order"] else "hold",
            )
        )
    if news_by_ticker:
        lines.extend(["", "## 4. 新闻与市场综合研究评分", "",
                      "| 股票 | 新闻关联度 | 来源可靠度 | 新闻情绪 | 新闻评分 | 技术评分 | Kronos评分 | 综合分 | 置信度 |",
                      "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |"])
        for item in market["results"]:
            signal = item["signal"]
            ticker = signal["ticker"]
            news = news_by_ticker.get(ticker, {"relevance_score": 0, "reliability_score": 0,
                                                "sentiment": 0, "news_score": 0,
                                                "confidence": "insufficient"})
            forecast_return = float(market.get("kronos", {}).get(ticker, {}).get("forecast_return", 0.0))
            scores = calculate_scores(signal, forecast_return, news)
            technical_score = scores["technical"]
            kronos_score = scores["kronos"]
            combined = scores["combined"]
            combined_scores.append((ticker, combined, news["confidence"]))
            lines.append(
                f"| {ticker} | {news['relevance_score']} | {news['reliability_score']} | "
                f"{news['sentiment']:+.2f} | {news['news_score']} | {technical_score} | "
                f"{kronos_score} | {combined} | {news['confidence']} |"
            )
        lines.extend(["", "综合分 = 新闻评分45% + 技术评分35% + Kronos方向评分20%。",
                      "这是透明的MVP研究优先级，不是收益概率；新闻证据不足时置信度会保持低。"])

    if serenity_by_ticker:
        lines.extend(["", "## 5. Serenity 供应链投资门槛", "",
                      "| 股票 | 供应链图 | 卡位证据 | 客户依赖 | 纯业务暴露 | 财报验证 | Serenity结论 |",
                      "| --- | --- | --- | --- | --- | --- | --- |"])
        for item in market["results"]:
            ticker = item["signal"]["ticker"]
            assessment = serenity_by_ticker.get(ticker)
            if not assessment:
                continue
            lines.append(
                f"| {ticker} | {assessment['supply_chain_map']} | {assessment['chokepoint_evidence']} | "
                f"{assessment['customer_dependency']} | {assessment['pure_play']} | "
                f"{assessment['earnings_validation']} | {assessment['serenity_decision']} |"
            )
        lines.extend(["", "Serenity 方法把新闻和模型信号当作假设起点，而不是买入依据。",
                      "只有卡位、客户依赖和财报验证均有直接证据，才允许从观察升级为可投资论点。", ""])
        for ticker, assessment in serenity_by_ticker.items():
            lines.append(f"- {ticker}：{assessment['reason']}")

    lines.extend(["", "## 6. 风险控制产生的订单意图", "",
                  "| 股票 | 数量 | 参考价 | 止损参考 | 止盈参考 | 成交 |",
                  "| --- | ---: | ---: | ---: | ---: | --- |"])
    for item in market["results"]:
        order = item["order"]
        if order:
            lines.append(
                f"| {order['ticker']} | {order['quantity']} | {money(order['reference_price'])} | "
                f"{money(order['stop_price'])} | {money(order['take_profit_price'])} | 否（dry-run） |"
            )
    lines.extend([
        "", "仓位由单笔风险 1%、单仓上限 20%、总敞口上限 60% 和现金约束共同决定。",
        "这些是市场模型单独产生的技术面订单意图；新闻综合分尚未授权触发交易。",
        "订单未写入模拟账户，也没有发送到券商。", "",
        "## 7. 结论", "",
    ])
    promoted = [ticker for ticker, score, confidence in combined_scores if score >= 70 and confidence != "low"]
    serenity_ready = [ticker for ticker in promoted if serenity_by_ticker.get(ticker, {}).get("serenity_decision") == "research-ready"]
    serenity_watch = [ticker for ticker in promoted if ticker not in serenity_ready]
    held = [ticker for ticker, _score, _confidence in combined_scores if ticker not in promoted]
    if promoted:
        lines.append(f"- 进入优先深度研究（综合分≥70且新闻置信度不低）：{', '.join(promoted)}")
    if serenity_watch:
        lines.append(f"- Serenity 门槛尚未通过，不升级为投资建议：{', '.join(serenity_watch)}")
    if serenity_ready:
        lines.append(f"- Serenity 证据完整，可进入估值与仓位讨论：{', '.join(serenity_ready)}")
    if held:
        lines.append(f"- 保持观察、等待更多公司相关新闻证据：{', '.join(held)}")
    lines.extend([
        "- 该结论只改变研究优先级，不等于买入建议，也不会自动下单。",
        "- 下一道正式门槛是财报/估值验证和滚动样本外回测。", "",
    ])
    if theme_stocks:
        lines.extend(["## 8. 宽主题关联股票", "",
                      "新闻无需提及股票名称；以下结果来自主题强度与已配置业务/供应链关系的传导。", "",
                      "| 主题 | 股票 | 主题分 | 传导分 | 结论 |",
                      "| --- | --- | ---: | ---: | --- |"])
        for row in theme_stocks[:10]:
            lines.append(
                f"| {row['theme_label']} | {row['ticker']} | {row['theme_score']} | "
                f"{row['transmission_score']} | {row['decision']} |"
            )
        lines.extend(["", "这些股票只进入候选研究池；进入行情、估值或订单流程前仍需单独验证。", ""])
    lines.extend([
        "## 9. 审计文件", "", f"- 市场与模型原始 JSON：`{market_path}`",
        f"- 每日公司新闻评分：`{args.news_report}`" if args.news_report else "- 每日公司新闻评分：本次未提供",
        f"- 每日趋势评分：`{args.trend_report}`" if args.trend_report else "- 每日趋势评分：本次未提供",
        f"- Serenity 门槛：`{args.serenity_assessment}`" if args.serenity_assessment else "- Serenity 门槛：本次未提供",
        f"- 主题股票传导：`{args.theme_stock_report}`" if args.theme_stock_report else "- 主题股票传导：本次未提供",
        "- 趋势深度报告：`trend-agent/reports/research/research-1-frontier_biotech.md`",
        "- 自动公司映射：`trend-agent/reports/company-maps/research-2-frontier_biotech_company_map.md`",
        "- 人工证据桥接：`outputs/frontier-biotech-investment-bridge.md`", "",
    ])
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
